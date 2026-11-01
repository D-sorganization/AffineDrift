"""Measure live 1440px paragraph line lengths with exact source CSS overrides.

This is a manual evidence tool, not a CI test. It requires Chrome started with a
remote-debugging port and the optional ``websocket-client`` Python package.
It measures the live page DOM, then injects the 61ch baseline, the exact 55ch
rules found in this checkout, and a hypothetical global 56ch token in turn.
"""

from __future__ import annotations

import argparse
import http.client
import json
import re
import time
from pathlib import Path
from typing import Any

import websocket

ROOT = Path(__file__).resolve().parents[3]
BASE_URL = "https://www.affinedrift.com"
PAGES = {
    "Theory Part 1": "/articles/theory-part1.html",
    "ch03": "/articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.html",
    "Core Theses registry": "/articles/core-theses-registry.html",
    "Proximal-distal journey": "/articles/proximal-distal-a-journey-through-the-swing.html",
    "Falsification atlas": "/articles/proximal-distal-falsification-atlas.html",
}
MEASURE_JS = r"""(() => {
  const excluded = 'code,pre,.math,.math-inline,.math-display,.MathJax,sup,[aria-hidden="true"]';
  const paragraphs = [...document.querySelectorAll('#quarto-document-content p')]
    .filter((p) => p.getClientRects().length && p.innerText.trim().length > 200);
  const allFullLines = [];
  const longestFullLineByParagraph = [];
  const perParagraph = [];
  for (const paragraph of paragraphs) {
    const walker = document.createTreeWalker(paragraph, NodeFilter.SHOW_TEXT);
    const lines = new Map();
    let node;
    while ((node = walker.nextNode())) {
      if (node.parentElement?.closest(excluded)) continue;
      const text = node.nodeValue || '';
      for (let offset = 0; offset < text.length;) {
        const size = text.codePointAt(offset) > 0xffff ? 2 : 1;
        const range = document.createRange();
        range.setStart(node, offset);
        range.setEnd(node, offset + size);
        const rect = range.getBoundingClientRect();
        if (rect.height > 0) {
          const top = Math.round(rect.top * 10) / 10;
          lines.set(top, (lines.get(top) || 0) + 1);
        }
        offset += size;
      }
    }
    const counts = [...lines.values()];
    if (counts.length > 1) {
      const fullLines = counts.slice(0, -1);
      allFullLines.push(...fullLines);
      longestFullLineByParagraph.push(Math.max(...fullLines));
      perParagraph.push(counts);
    }
  }
  const median = (values) => {
    const sorted = [...values].sort((a, b) => a - b);
    return sorted.length
      ? (sorted[(sorted.length - 1) >> 1] + sorted[sorted.length >> 1]) / 2
      : null;
  };
  return {
    url: location.href,
    title: document.title,
    viewport: [innerWidth, innerHeight],
    proseWidth: getComputedStyle(
      document.querySelector('#quarto-document-content p') || document.documentElement,
    ).getPropertyValue('--prose-width').trim(),
    paragraphCount: perParagraph.length,
    fullLineCount: allFullLines.length,
    fullLineMedian: median(allFullLines),
    longestLineMedian: median(longestFullLineByParagraph),
    fullLineCounts: allFullLines,
    perParagraph,
  };
})()"""


class DevTools:
    """Minimal synchronous Chrome DevTools Protocol client."""

    def __init__(self, websocket_url: str) -> None:
        """Connect to a Chrome DevTools WebSocket endpoint."""
        self.connection = websocket.create_connection(
            websocket_url,
            timeout=90,
            suppress_origin=True,
        )
        self.next_id = 0

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send one CDP command and return its result or raise its error."""
        self.next_id += 1
        request_id = self.next_id
        self.connection.send(
            json.dumps({"id": request_id, "method": method, "params": params or {}})
        )
        while True:
            message = json.loads(self.connection.recv())
            if message.get("id") == request_id:
                if "error" in message:
                    raise RuntimeError(message["error"])
                return message.get("result", {})

    def evaluate(self, expression: str, *, await_promise: bool = False) -> Any:
        """Evaluate JavaScript in the current page and return its value."""
        result = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": await_promise,
                "userGesture": True,
            },
        )
        if "exceptionDetails" in result:
            raise RuntimeError(result["exceptionDetails"])
        return result.get("result", {}).get("value")


def width_rules() -> str:
    """Return the two 55ch selector rules from this checked out source tree."""
    sources = [
        ROOT / "css/tokens/typography.css",
        ROOT / "articles/The_Physics_of_Golf/quarto/typography.css",
    ]
    rules = []
    for path in sources:
        text = path.read_text(encoding="utf-8")
        rules.extend(
            match.group(0)
            for match in re.finditer(r"([^{}]+\{[^{}]*--prose-width:\s*55ch;[^{}]*\})", text)
        )
    if len(rules) != 2:
        raise ValueError(f"expected the two scoped 55ch rules, found {len(rules)}")
    return "\n".join(rules)


def add_style(devtools: DevTools, css: str) -> None:
    """Replace the measurement stylesheet in the current page."""
    script = (
        "(() => {let style=document.getElementById('ad5166-width-measure');"
        "if(!style){style=document.createElement('style');"
        "style.id='ad5166-width-measure';document.head.append(style);}"
        f"style.textContent={json.dumps(css)};return true;}})()"
    )
    devtools.evaluate(script)


def collect(port: int) -> dict[str, Any]:
    """Measure all configured pages using a local Chrome debugging port."""
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    connection.request("PUT", "/json/new?about:blank")
    response = connection.getresponse()
    if response.status != 200:
        raise RuntimeError(f"Chrome target creation failed: HTTP {response.status}")
    target = json.loads(response.read())
    connection.close()
    devtools = DevTools(target["webSocketDebuggerUrl"])
    devtools.call("Page.enable")
    devtools.call("Runtime.enable")
    devtools.call(
        "Emulation.setDeviceMetricsOverride",
        {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False},
    )
    rules = width_rules()
    output = []
    for name, path in PAGES.items():
        devtools.call("Page.navigate", {"url": BASE_URL + path})
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            if devtools.evaluate("document.readyState") == "complete":
                break
            time.sleep(0.25)
        else:
            raise TimeoutError(f"page did not finish loading: {BASE_URL + path}")
        devtools.evaluate("document.fonts.ready.then(() => true)", await_promise=True)
        time.sleep(1)

        add_style(devtools, ":root { --prose-width: 61ch; }")
        baseline = devtools.evaluate(MEASURE_JS)
        add_style(devtools, ":root { --prose-width: 61ch; }\n" + rules)
        current_branch = devtools.evaluate(MEASURE_JS)
        add_style(devtools, ":root { --prose-width: 56ch; }")
        hypothetical_global = devtools.evaluate(MEASURE_JS)
        output.append(
            {
                "page": name,
                "base_61ch": baseline,
                "current_branch_rules": current_branch,
                "hypothetical_global_56ch": hypothetical_global,
            }
        )
    devtools.connection.close()
    return {
        "method": "paragraph Range rects grouped by top; final short line excluded",
        "pages": output,
    }


def main() -> None:
    """Parse CLI options and print the rendered page measurements as JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chrome-port", type=int, default=9227)
    args = parser.parse_args()
    print(json.dumps(collect(args.chrome_port), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

/**
 * AffineDrift - PDF Module
 * Handles PDF download and print functionality
 */

import { MATHJAX_RENDER_DELAY_MS } from "./utils.js";

/**
 * Initialize PDF download button
 */
export function initPDFDownload() {
    if (
        document.querySelector(".home-layout") ||
        document.querySelector(".pdf-download-btn")
    ) {
        return;
    }

    const pdfBtn = document.createElement("button");
    pdfBtn.className = "pdf-download-btn";
    pdfBtn.setAttribute("aria-label", "Download page as PDF");
    pdfBtn.setAttribute("title", "Download as PDF");
    pdfBtn.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M12,19L8,15H10.5V12H13.5V15H16L12,19Z"/>
    </svg>
    <span>PDF</span>
  `;

    pdfBtn.addEventListener("click", function () {
        preparePDFPrint();
    });

    document.body.appendChild(pdfBtn);
}

/**
 * Prepare the page for PDF printing
 */
export function preparePDFPrint() {
    const pageTitle = document.title
        .replace(" – AffineDrift", "")
        .replace("AffineDrift – ", "");

    let printTitleBlock = document.querySelector(".print-title-block");
    if (!printTitleBlock) {
        printTitleBlock = document.createElement("div");
        printTitleBlock.className = "print-title-block";
        printTitleBlock.style.display = "none";
        printTitleBlock.innerHTML = `
      <h1>${pageTitle}</h1>
      <div class="print-author">AffineDrift</div>
      <div class="print-date">${new Date().toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
        })}</div>
    `;

        const mainContent =
            document.querySelector(".main-content-area") ||
            document.querySelector("main.content") ||
            document.querySelector("#quarto-content");
        if (mainContent) {
            mainContent.insertBefore(printTitleBlock, mainContent.firstChild);
        }
    }

    if (window.MathJax && window.MathJax.typesetPromise) {
        MathJax.typesetPromise()
            .then(() => {
                setTimeout(() => {
                    window.print();
                }, MATHJAX_RENDER_DELAY_MS);
            })
            .catch((err) => {
                console.error("MathJax typeset error, printing anyway:", err);
                window.print();
            });
    } else {
        window.print();
    }
}

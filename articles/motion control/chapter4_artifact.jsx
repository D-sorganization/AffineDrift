import { useState, useMemo } from "react";

const colors = {
  chapblue: "#004682",
  accentred: "#B42828",
  trajgreen: "#1E823C",
  darkgold: "#A07814",
  purple: "#64288C",
  softgray: "#F5F5F5",
  lightblue: "#E8F0F8",
  lightred: "#FDF0F0",
  lightgold: "#FDF8E8",
  lightpurple: "#F5F0F8",
};

function MathInline({ children }) {
  return <span className="font-mono text-sm" style={{ color: colors.chapblue }}>{children}</span>;
}

function MathBlock({ children, label }) {
  return (
    <div className="my-4 bg-gray-50 border-l-4 border-gray-300 p-4 overflow-x-auto">
      <div className="font-mono text-sm leading-relaxed text-gray-800">{children}</div>
      {label && <div className="text-xs text-gray-500 mt-1 text-right">{label}</div>}
    </div>
  );
}

function ThemedBox({ title, number, borderColor, bgColor, children, icon }) {
  return (
    <div className="my-6 rounded-lg overflow-hidden shadow-sm" style={{ border: `2px solid ${borderColor}` }}>
      <div className="px-4 py-2 flex items-center gap-2" style={{ backgroundColor: borderColor }}>
        {icon && <span>{icon}</span>}
        <span className="font-bold text-white text-sm">{title} {number}</span>
      </div>
      <div className="p-4 text-sm leading-relaxed" style={{ backgroundColor: bgColor }}>{children}</div>
    </div>
  );
}

function Section({ id, number, title, children }) {
  return (
    <section id={id} className="mb-10">
      <h2 className="text-2xl font-bold mb-4 pb-2 border-b-2" style={{ color: colors.chapblue, borderColor: colors.chapblue }}>
        4.{number} &nbsp;{title}
      </h2>
      {children}
    </section>
  );
}

function SubSection({ title, children }) {
  return (
    <div className="mb-6">
      <h3 className="text-lg font-bold mb-3" style={{ color: colors.chapblue }}>{title}</h3>
      {children}
    </div>
  );
}

function LyapunovVsOrbitalDiagram() {
  return (
    <div className="grid grid-cols-2 gap-4 my-6">
      <div className="p-4 rounded-lg border-2" style={{ borderColor: colors.accentred, backgroundColor: colors.lightred }}>
        <h4 className="font-bold text-sm mb-3" style={{ color: colors.accentred }}>Lyapunov View</h4>
        <svg viewBox="0 0 200 180" className="w-full">
          <defs>
            <marker id="arG4" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill={colors.trajgreen} />
            </marker>
          </defs>
          <path d="M 20 140 C 60 40, 120 30, 180 80" fill="none" stroke={colors.trajgreen} strokeWidth="2.5"
            markerMid="url(#arG4)" />
          <circle cx="100" cy="48" r="4" fill={colors.trajgreen} />
          <text x="105" y="42" fontSize="10" fill={colors.trajgreen} fontWeight="bold">γ*(t)</text>
          <circle cx="75" cy="72" r="4" fill={colors.accentred} />
          <text x="80" y="68" fontSize="9" fill={colors.accentred}>γ*(t−ε)</text>
          <line x1="100" y1="48" x2="77" y2="70" stroke={colors.accentred} strokeWidth="1.5" strokeDasharray="4" />
          <text x="92" y="66" fontSize="9" fill={colors.accentred}>e≠0</text>
          <text x="50" y="170" fontSize="12" fontWeight="bold" fill={colors.accentred}>"Unstable" ✗</text>
        </svg>
        <p className="text-xs text-gray-500 mt-1">Timing shift creates persistent nonzero error e(t). Lyapunov says unstable — <strong>wrong answer</strong>.</p>
      </div>
      <div className="p-4 rounded-lg border-2" style={{ borderColor: colors.trajgreen, backgroundColor: "#F0F8F2" }}>
        <h4 className="font-bold text-sm mb-3" style={{ color: colors.trajgreen }}>Orbital View</h4>
        <svg viewBox="0 0 200 180" className="w-full">
          <defs>
            <marker id="arG4b" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill={colors.trajgreen} />
            </marker>
          </defs>
          <path d="M 20 140 C 60 40, 120 30, 180 80" fill="none" stroke={colors.trajgreen} strokeWidth="2.5"
            markerMid="url(#arG4b)" />
          <circle cx="75" cy="72" r="4" fill={colors.chapblue} />
          <text x="80" y="68" fontSize="9" fill={colors.chapblue} fontWeight="bold">on O</text>
          <text x="120" y="60" fontSize="9" fill={colors.chapblue}>d⊥ = 0</text>
          <text x="55" y="170" fontSize="12" fontWeight="bold" fill={colors.trajgreen}>"Stable" ✓</text>
        </svg>
        <p className="text-xs text-gray-500 mt-1">System is on the orbit. Timing differs but transverse distance is zero — <strong>correct answer</strong>.</p>
      </div>
    </div>
  );
}

function TransverseDecompositionDiagram() {
  return (
    <svg viewBox="0 0 500 280" className="w-full max-w-xl mx-auto my-6">
      <defs>
        <marker id="arB4" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill={colors.chapblue} />
        </marker>
        <marker id="arR4" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill={colors.accentred} />
        </marker>
        <marker id="arG4c" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill={colors.trajgreen} />
        </marker>
      </defs>
      {/* Orbit curve */}
      <path d="M 40 200 C 100 200, 150 60, 250 100 C 350 140, 400 50, 460 70"
        fill="none" stroke={colors.trajgreen} strokeWidth="3" />
      <text x="465" y="65" fill={colors.trajgreen} fontSize="13" fontWeight="bold">O</text>
      {/* Point on orbit */}
      <circle cx="250" cy="100" r="5" fill={colors.trajgreen} />
      <text x="258" y="92" fill={colors.trajgreen} fontSize="11" fontWeight="bold">γ*(s*)</text>
      {/* Tangent vector */}
      <line x1="250" y1="100" x2="340" y2="110" stroke={colors.chapblue} strokeWidth="2.5" markerEnd="url(#arB4)" />
      <text x="345" y="108" fill={colors.chapblue} fontSize="12" fontWeight="bold">t(s*)</text>
      {/* Transverse hyperplane */}
      <line x1="240" y1="30" x2="260" y2="240" stroke={colors.darkgold} strokeWidth="2" strokeDasharray="6,3" />
      <text x="215" y="25" fill={colors.darkgold} fontSize="12" fontWeight="bold">Σ(s*)</text>
      {/* Actual state */}
      <circle cx="256" cy="185" r="5" fill={colors.accentred} />
      <text x="265" y="190" fill={colors.accentred} fontSize="11" fontWeight="bold">x(t)</text>
      {/* Transverse deviation ξ */}
      <line x1="250" y1="100" x2="255" y2="180" stroke={colors.accentred} strokeWidth="2" markerEnd="url(#arR4)" />
      <text x="225" y="150" fill={colors.accentred} fontSize="12" fontWeight="bold">ξ</text>
      {/* Phase axis */}
      <line x1="40" y1="260" x2="460" y2="260" stroke="#bbb" strokeWidth="1" />
      <text x="465" y="264" fill="#999" fontSize="11">s</text>
      <line x1="250" y1="255" x2="250" y2="265" stroke="#bbb" />
      <text x="243" y="277" fill="#999" fontSize="10">s*</text>
    </svg>
  );
}

function FloquetDemo() {
  const [mu1, setMu1] = useState(0.7);
  const [mu2, setMu2] = useState(0.4);
  const [mu3, setMu3] = useState(-0.3);

  const allStable = Math.abs(mu1) < 1 && Math.abs(mu2) < 1 && Math.abs(mu3) < 1;
  const worstMult = Math.max(Math.abs(mu1), Math.abs(mu2), Math.abs(mu3));
  const stridesTo1Pct = worstMult >= 1 ? Infinity : Math.ceil(Math.log(0.01) / Math.log(worstMult));

  const points = useMemo(() => {
    const pts = [];
    for (let i = 0; i <= 360; i += 2) {
      const rad = i * Math.PI / 180;
      pts.push({ x: Math.cos(rad), y: Math.sin(rad) });
    }
    return pts;
  }, []);

  const cx = 150, cy = 120, r = 90;

  return (
    <div className="my-6 p-5 rounded-xl bg-white shadow-md border border-gray-200">
      <h4 className="font-bold text-base mb-3" style={{ color: colors.purple }}>
        Interactive: Floquet Multipliers & Orbital Stability
      </h4>
      <p className="text-sm text-gray-600 mb-4">
        Drag to adjust the three Floquet multipliers. All must lie inside the unit circle (|μ| {'<'} 1) for asymptotic orbital stability.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <svg viewBox="0 0 300 240" className="w-full max-w-xs mx-auto">
            {/* Unit circle */}
            <circle cx={cx} cy={cy} r={r} fill="none" stroke="#ddd" strokeWidth="2" />
            <line x1={cx - r - 20} y1={cy} x2={cx + r + 20} y2={cy} stroke="#eee" strokeWidth="1" />
            <line x1={cx} y1={cy - r - 20} x2={cx} y2={cy + r + 20} stroke="#eee" strokeWidth="1" />
            <text x={cx + r + 5} y={cy - 5} fontSize="9" fill="#999">1</text>
            <text x={cx - r - 12} y={cy - 5} fontSize="9" fill="#999">-1</text>
            {/* Stable region fill */}
            <circle cx={cx} cy={cy} r={r} fill={allStable ? "#E8F5E9" : "#FFEBEE"} opacity="0.3" />
            {/* Multipliers (on real axis for this demo) */}
            <circle cx={cx + mu1 * r} cy={cy} r="8" fill={Math.abs(mu1) < 1 ? colors.chapblue : colors.accentred} />
            <text x={cx + mu1 * r - 3} y={cy + 4} fontSize="10" fill="white" fontWeight="bold">1</text>
            <circle cx={cx + mu2 * r} cy={cy - 25} r="8" fill={Math.abs(mu2) < 1 ? colors.trajgreen : colors.accentred} />
            <text x={cx + mu2 * r - 3} y={cy - 21} fontSize="10" fill="white" fontWeight="bold">2</text>
            <circle cx={cx + mu3 * r} cy={cy + 25} r="8" fill={Math.abs(mu3) < 1 ? colors.darkgold : colors.accentred} />
            <text x={cx + mu3 * r - 3} y={cy + 29} fontSize="10" fill="white" fontWeight="bold">3</text>
            <text x={cx - 30} y={230} fontSize="11" fill="#666">Unit circle in ℂ</text>
          </svg>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium" style={{ color: colors.chapblue }}>μ₁ = {mu1.toFixed(2)}</label>
            <input type="range" min="-120" max="120" value={mu1 * 100} onChange={e => setMu1(Number(e.target.value) / 100)} className="w-full" />
          </div>
          <div>
            <label className="text-sm font-medium" style={{ color: colors.trajgreen }}>μ₂ = {mu2.toFixed(2)}</label>
            <input type="range" min="-120" max="120" value={mu2 * 100} onChange={e => setMu2(Number(e.target.value) / 100)} className="w-full" />
          </div>
          <div>
            <label className="text-sm font-medium" style={{ color: colors.darkgold }}>μ₃ = {mu3.toFixed(2)}</label>
            <input type="range" min="-120" max="120" value={mu3 * 100} onChange={e => setMu3(Number(e.target.value) / 100)} className="w-full" />
          </div>

          <div className={`p-3 rounded-lg border ${allStable ? "bg-green-50 border-green-300" : "bg-red-50 border-red-300"}`}>
            <div className="text-lg font-bold" style={{ color: allStable ? colors.trajgreen : colors.accentred }}>
              {allStable ? "✓ Asymptotically Orbitally Stable" : "✗ Orbitally Unstable"}
            </div>
            <div className="text-xs text-gray-600 mt-1">
              Worst |μ| = {worstMult.toFixed(3)}
              {allStable && <span> · Convergence per period: {((1 - worstMult) * 100).toFixed(1)}%</span>}
            </div>
            {allStable && stridesTo1Pct < 500 && (
              <div className="text-xs text-gray-600">
                Periods to reduce 10% deviation to 1%: <strong>{stridesTo1Pct}</strong>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function AmplificationProfile() {
  const phases = [
    { s: 0, rho: 1.0, label: "Address" },
    { s: 0.1, rho: 1.0 },
    { s: 0.2, rho: 1.05 },
    { s: 0.3, rho: 1.1, label: "Top" },
    { s: 0.35, rho: 1.3 },
    { s: 0.4, rho: 1.5 },
    { s: 0.45, rho: 1.4, label: "Transition" },
    { s: 0.5, rho: 1.2 },
    { s: 0.55, rho: 0.95 },
    { s: 0.6, rho: 0.75 },
    { s: 0.65, rho: 0.55, label: "Release" },
    { s: 0.7, rho: 0.4 },
    { s: 0.75, rho: 0.3, label: "Impact" },
    { s: 0.85, rho: 0.35 },
    { s: 1.0, rho: 0.5, label: "Finish" },
  ];

  const w = 440, h = 200, pad = { l: 50, r: 20, t: 20, b: 35 };
  const pw = w - pad.l - pad.r, ph = h - pad.t - pad.b;
  const maxRho = 1.6;

  const toX = s => pad.l + s * pw;
  const toY = rho => pad.t + ph - (rho / maxRho) * ph;

  const pathD = phases.map((p, i) => `${i === 0 ? "M" : "L"} ${toX(p.s).toFixed(1)} ${toY(p.rho).toFixed(1)}`).join(" ");

  return (
    <div className="my-6 p-4 bg-white rounded-lg shadow-sm border">
      <h4 className="font-bold text-sm mb-2" style={{ color: colors.chapblue }}>Transverse Amplification Ratio ρ(0, s) Along the Golf Swing</h4>
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full">
        {/* Grid */}
        <line x1={pad.l} y1={toY(1)} x2={w - pad.r} y2={toY(1)} stroke="#ccc" strokeWidth="1" strokeDasharray="4" />
        <text x={pad.l - 5} y={toY(1) + 4} fontSize="9" fill="#999" textAnchor="end">1.0</text>
        <text x={pad.l - 5} y={toY(0) + 4} fontSize="9" fill="#999" textAnchor="end">0</text>
        <text x={pad.l - 5} y={toY(1.5) + 4} fontSize="9" fill="#999" textAnchor="end">1.5</text>
        {/* ρ = 1 reference */}
        <rect x={pad.l} y={toY(maxRho)} width={pw} height={toY(1) - toY(maxRho)} fill={colors.accentred} opacity="0.05" />
        <rect x={pad.l} y={toY(1)} width={pw} height={toY(0) - toY(1)} fill={colors.trajgreen} opacity="0.05" />
        <text x={w - pad.r - 5} y={toY(1.3)} fontSize="8" fill={colors.accentred} textAnchor="end">ρ {'>'} 1: errors grow</text>
        <text x={w - pad.r - 5} y={toY(0.5)} fontSize="8" fill={colors.trajgreen} textAnchor="end">ρ {'<'} 1: errors shrink</text>
        {/* Axes */}
        <line x1={pad.l} y1={h - pad.b} x2={w - pad.r} y2={h - pad.b} stroke="#888" strokeWidth="1" />
        <line x1={pad.l} y1={pad.t} x2={pad.l} y2={h - pad.b} stroke="#888" strokeWidth="1" />
        <text x={w / 2} y={h - 5} fontSize="10" fill="#666" textAnchor="middle">Phase s (normalized)</text>
        <text x={12} y={h / 2} fontSize="10" fill="#666" textAnchor="middle" transform={`rotate(-90, 12, ${h / 2})`}>ρ(0, s)</text>
        {/* Curve */}
        <path d={pathD} fill="none" stroke={colors.chapblue} strokeWidth="2.5" />
        {/* Filled area below curve */}
        <path d={`${pathD} L ${toX(1)} ${toY(0)} L ${toX(0)} ${toY(0)} Z`} fill={colors.chapblue} opacity="0.08" />
        {/* Phase labels */}
        {phases.filter(p => p.label).map((p, i) => (
          <g key={i}>
            <line x1={toX(p.s)} y1={toY(p.rho) + 3} x2={toX(p.s)} y2={h - pad.b} stroke="#ddd" strokeWidth="1" strokeDasharray="2" />
            <circle cx={toX(p.s)} cy={toY(p.rho)} r="3" fill={p.rho > 1 ? colors.accentred : colors.trajgreen} />
            <text x={toX(p.s)} y={h - pad.b + 12} fontSize="8" fill="#666" textAnchor="middle">{p.label}</text>
          </g>
        ))}
      </svg>
      <div className="mt-2 grid grid-cols-4 gap-2 text-xs">
        <div className="p-2 rounded bg-blue-50 text-center">
          <div className="font-bold" style={{ color: colors.chapblue }}>Backswing</div>
          <div className="text-gray-500">ρ ≈ 1, neutral</div>
        </div>
        <div className="p-2 rounded bg-red-50 text-center">
          <div className="font-bold" style={{ color: colors.accentred }}>Transition</div>
          <div className="text-gray-500">ρ {'>'} 1, unstable</div>
        </div>
        <div className="p-2 rounded bg-green-50 text-center">
          <div className="font-bold" style={{ color: colors.trajgreen }}>Release</div>
          <div className="text-gray-500">ρ drops fast</div>
        </div>
        <div className="p-2 rounded bg-green-100 text-center">
          <div className="font-bold" style={{ color: colors.trajgreen }}>Impact</div>
          <div className="text-gray-500">ρ = 0.3, funnel!</div>
        </div>
      </div>
    </div>
  );
}

function ControllerArchitecture() {
  return (
    <div className="my-6 p-4 bg-white rounded-lg shadow-sm border">
      <h4 className="font-bold text-sm mb-3" style={{ color: colors.chapblue }}>Complete Tracking Controller Architecture</h4>
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm" style={{ backgroundColor: colors.trajgreen }}>1</div>
          <div className="flex-1 p-3 rounded-lg border-2" style={{ borderColor: colors.trajgreen, backgroundColor: "#F0F8F2" }}>
            <div className="font-bold text-sm" style={{ color: colors.trajgreen }}>Feedforward u*(t)</div>
            <div className="text-xs text-gray-600">From inverse dynamics, ~90% of total control effort. Executes the motion.</div>
          </div>
          <div className="text-2xl font-light text-gray-300">→</div>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm" style={{ backgroundColor: colors.chapblue }}>2</div>
          <div className="flex-1 p-3 rounded-lg border-2" style={{ borderColor: colors.chapblue, backgroundColor: colors.lightblue }}>
            <div className="font-bold text-sm" style={{ color: colors.chapblue }}>Projection: s* = π(x), ξ = P(x − γ*(s*))</div>
            <div className="text-xs text-gray-600">Find nearest point on orbit, extract transverse deviation only.</div>
          </div>
          <div className="text-2xl font-light text-gray-300">→</div>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm" style={{ backgroundColor: colors.darkgold }}>3</div>
          <div className="flex-1 p-3 rounded-lg border-2" style={{ borderColor: colors.darkgold, backgroundColor: colors.lightgold }}>
            <div className="font-bold text-sm" style={{ color: colors.darkgold }}>Transverse Feedback: δu = K⊥(s*)·ξ</div>
            <div className="text-xs text-gray-600">Phase-varying gains from Riccati equation. Tightens near impact. The optimal funnel.</div>
          </div>
          <div className="text-2xl font-light text-gray-300">→</div>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm bg-gray-500">Σ</div>
          <div className="flex-1 p-3 rounded-lg border-2 border-gray-400 bg-gray-50">
            <div className="font-bold text-sm text-gray-700">Plant: u = u*(t) + δu</div>
            <div className="text-xs text-gray-600">Total control = feedforward + transverse correction. Measure x(t), loop back to projection.</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function WhyNotStandardLQR() {
  const rows = [
    { issue: "Tangential correction", transverse: "Ignores timing errors (benign)", standard: "Wastes effort correcting timing" },
    { issue: "Marginal stability", transverse: "Removed by reduction", standard: "Fights λ=1 eigenvalue → high gains" },
    { issue: "Funnel shape", transverse: "Natural phase-varying width", standard: "Penalizes all errors equally" },
    { issue: "Dimension", transverse: "n−1 (smaller Riccati)", standard: "n (larger computation)" },
    { issue: "Physical meaning", transverse: "ξ = cross-orbit deviation", standard: "e = x−γ*(t) mixes tangential+transverse" },
  ];
  return (
    <div className="my-6 overflow-x-auto">
      <table className="w-full text-xs border-collapse">
        <thead>
          <tr style={{ backgroundColor: colors.chapblue }}>
            <th className="text-left text-white p-2">Issue</th>
            <th className="text-left text-white p-2">Transverse LQR ✓</th>
            <th className="text-left text-white p-2">Standard LQR ✗</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
              <td className="p-2 font-medium">{r.issue}</td>
              <td className="p-2 text-green-700">{r.transverse}</td>
              <td className="p-2 text-red-700">{r.standard}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SummaryTable() {
  const rows = [
    { concept: "Orbital stability", sig: "Correct stability notion for moving systems: only cross-orbit deviations matter" },
    { concept: "Transverse linearization", sig: "Reduces to (n−1)-dim LTV stability; removes tangential nuisance direction" },
    { concept: "Floquet multipliers", sig: "Eigenvalues of monodromy matrix; determine periodic orbit stability" },
    { concept: "Moving Poincaré sections", sig: "Extend analysis to non-periodic trajectories via state transition matrix" },
    { concept: "Amplification ratio ρ", sig: "Max singular value of Φ⊥; quantifies transverse error growth/contraction" },
    { concept: "Transverse LQR", sig: "Phase-varying feedback from Riccati equation; the optimal funnel controller" },
    { concept: "Riccati funnel", sig: "LQR cost-to-go defines funnel boundary; connects geometric and algebraic views" },
  ];
  return (
    <div className="my-6 overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr style={{ backgroundColor: colors.chapblue }}>
            <th className="text-left text-white p-3">Concept</th>
            <th className="text-left text-white p-3">Significance</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
              <td className="p-3 font-mono text-xs" style={{ color: colors.chapblue }}>{r.concept}</td>
              <td className="p-3 text-gray-700">{r.sig}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function NavSidebar({ sections, activeSection, onNav }) {
  return (
    <nav className="hidden lg:block fixed right-4 top-1/2 -translate-y-1/2 w-48 text-xs z-50">
      <div className="bg-white/90 backdrop-blur rounded-lg shadow-lg p-3 border">
        <div className="font-bold text-gray-500 mb-2 uppercase tracking-wider" style={{ fontSize: 10 }}>Sections</div>
        {sections.map((s) => (
          <button key={s.id} onClick={() => onNav(s.id)}
            className={`block w-full text-left px-2 py-1.5 rounded transition-colors ${activeSection === s.id ? "font-bold" : "text-gray-500 hover:text-gray-800"}`}
            style={activeSection === s.id ? { color: colors.chapblue, backgroundColor: colors.lightblue } : {}}>
            {s.short}
          </button>
        ))}
      </div>
    </nav>
  );
}

const sections = [
  { id: "problem", num: "1", title: "The Problem with Lyapunov", short: "4.1 Problem w/ Lyapunov" },
  { id: "orbital", num: "2", title: "Orbital Stability: Definitions", short: "4.2 Orbital Stability" },
  { id: "decomposition", num: "3", title: "Transverse–Tangential Decomposition", short: "4.3 Decomposition" },
  { id: "transverse-lin", num: "4", title: "Transverse Linearization", short: "4.4 Transverse Lin." },
  { id: "floquet", num: "5", title: "Floquet Theory", short: "4.5 Floquet Theory" },
  { id: "poincare", num: "6", title: "Moving Poincaré Sections", short: "4.6 Poincaré Sections" },
  { id: "controller", num: "7", title: "Controller Design", short: "4.7 Controller Design" },
  { id: "robustness", num: "8", title: "Robustness", short: "4.8 Robustness" },
  { id: "summary", num: "9", title: "Summary", short: "4.9 Summary" },
];

export default function Chapter4() {
  const [activeSection, setActiveSection] = useState("problem");
  const handleNav = (id) => {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavSidebar sections={sections} activeSection={activeSection} onNav={handleNav} />
      <div className="max-w-3xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-10">
          <div className="h-1 w-full rounded mb-6" style={{ backgroundColor: colors.chapblue }} />
          <p className="text-sm font-bold uppercase tracking-widest mb-2" style={{ color: colors.chapblue }}>Chapter 4</p>
          <h1 className="text-4xl font-bold mb-4" style={{ color: colors.chapblue }}>Orbital Stability and Transverse Linearization</h1>
          <p className="text-lg italic text-gray-500 border-l-4 pl-4" style={{ borderColor: colors.darkgold }}>
            "Stability is not the absence of motion. It is the faithfulness of motion."
          </p>
          <div className="h-1 w-full rounded mt-6" style={{ backgroundColor: colors.chapblue }} />
        </div>

        {/* 4.1 */}
        <Section id="problem" number="1" title="The Problem with Lyapunov">
          <p className="text-gray-700 leading-relaxed mb-4">
            A system perfectly tracking a trajectory but shifted by ε seconds has error <MathInline>e(t) = γ*(t−ε) − γ*(t) ≈ −ε·γ̇*(t)</MathInline>. This error never decays. Lyapunov declares the trajectory <em>unstable</em>. But the system is executing the correct motion perfectly — the only "error" is timing.
          </p>

          <LyapunovVsOrbitalDiagram />

          <ThemedBox title="Key Idea 4.1." number="The Fundamental Inadequacy of Point Stability" borderColor={colors.accentred} bgColor={colors.lightred}>
            <p className="mb-2">Lyapunov stability conflates two independent phenomena:</p>
            <p className="mb-1"><strong>(i) Transverse deviations:</strong> drifting <em>away from</em> the path. Genuine control failure.</p>
            <p className="mb-2"><strong>(ii) Tangential deviations:</strong> ahead of or behind schedule <em>along</em> the path. Just a timing difference.</p>
            <p>Lyapunov rejects both. <strong>Orbital stability</strong> accepts tangential deviations and rejects only transverse ones.</p>
          </ThemedBox>
        </Section>

        {/* 4.2 */}
        <Section id="orbital" number="2" title="Orbital Stability: Formal Definitions">
          <ThemedBox title="Definition 4.1." number="Orbit" borderColor={colors.darkgold} bgColor={colors.lightgold}>
            <p>The <strong>orbit</strong> O = {'{'}γ*(t) : t ∈ [0,T]{'}'} ⊂ X is the image of the trajectory as a set — a curve without parameterization.</p>
          </ThemedBox>

          <ThemedBox title="Definition 4.2." number="Orbital Stability" borderColor={colors.darkgold} bgColor={colors.lightgold}>
            <p className="mb-2"><strong>Orbitally stable:</strong> d(x(0), O) {'<'} δ ⟹ d(x(t), O) {'<'} ε for all t ≥ 0.</p>
            <p className="mb-2"><strong>Asymptotically orbitally stable:</strong> additionally d(x(t), O) → 0 as t → ∞.</p>
            <p><strong>With asymptotic phase:</strong> additionally ‖x(t) − γ*(t + θ*)‖ → 0 for some phase shift θ*. The strongest practical form.</p>
          </ThemedBox>
        </Section>

        {/* 4.3 */}
        <Section id="decomposition" number="3" title="The Transverse–Tangential Decomposition">
          <TransverseDecompositionDiagram />

          <ThemedBox title="Definition 4.4." number="Transverse Hyperplane" borderColor={colors.darkgold} bgColor={colors.lightgold}>
            <p className="mb-2">At each orbit point γ*(s), state space decomposes as:</p>
            <MathBlock>x = γ*(s*) + ξ,  where  ξ ∈ Σ(s*) = {'{'}v : vᵀ t(s*) = 0{'}'}</MathBlock>
            <p>s* is the projected phase (along-orbit), ξ is the <strong>transverse deviation</strong> (cross-orbit). Orbital stability ⟺ stability of ξ = 0.</p>
          </ThemedBox>
        </Section>

        {/* 4.4 */}
        <Section id="transverse-lin" number="4" title="Transverse Linearization">
          <ThemedBox title="Theorem 4.1." number="Transverse Linearization" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <p className="mb-2">The linearized transverse dynamics about the orbit are:</p>
            <MathBlock label="(4.5)">ξ̇ = A⊥(s)·ξ + B⊥(s)·δu</MathBlock>
            <p>where A⊥ is the Jacobian <em>projected</em> onto the transverse space (dimension n−1), with the tangential component removed. The removed eigenvalue corresponds to motion along the orbit.</p>
          </ThemedBox>

          <ThemedBox title="Principle 4.1." number="The Transverse Reduction Principle" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <p>γ*(t) is asymptotically orbitally stable <strong>if and only if</strong> the origin of the transverse linearization is asymptotically stable. This reduces the nonlinear orbital stability question to a <em>linear</em> problem on an (n−1)-dimensional space. All LTV control tools apply.</p>
          </ThemedBox>

          <ThemedBox title="Remark 4.1." number="Understanding A⊥" borderColor={colors.purple} bgColor={colors.lightpurple}>
            <p className="mb-1">A⊥ = P·J·P minus the tangential projection of J, where P = I − t·tᵀ projects onto Σ.</p>
            <p>The Frenet–Serret frame from Chapter 2 provides the natural basis for Σ. When computed in this basis, A⊥ reveals the curvature-induced coupling v²K(s) from Chapter 2 as a concrete matrix term.</p>
          </ThemedBox>
        </Section>

        {/* 4.5 */}
        <Section id="floquet" number="5" title="Floquet Theory: Stability of Periodic Orbits">
          <ThemedBox title="Definition 4.6." number="Monodromy Matrix" borderColor={colors.darkgold} bgColor={colors.lightgold}>
            <p>For a periodic orbit with period T, the <strong>monodromy matrix</strong> M = Φ(T, 0) maps transverse deviations through one complete period. Its eigenvalues μ₁, ..., μₙ₋₁ are the <strong>Floquet multipliers</strong>.</p>
          </ThemedBox>

          <ThemedBox title="Theorem 4.2." number="Floquet Stability Criterion" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <p className="mb-1">• <strong>Stable:</strong> all |μₖ| ≤ 1 (inside or on unit circle)</p>
            <p className="mb-1">• <strong>Asymptotically stable:</strong> all |μₖ| {'<'} 1 (strictly inside)</p>
            <p>• <strong>Unstable:</strong> any |μₖ| {'>'} 1 (outside unit circle)</p>
          </ThemedBox>

          <FloquetDemo />

          <ThemedBox title="Remark 4.2." number="The Missing Multiplier" borderColor={colors.purple} bgColor={colors.lightpurple}>
            <p>The <em>full</em> n-dimensional system always has a multiplier at exactly +1 (the tangential direction). Without transverse reduction, the monodromy matrix appears only marginally stable even for asymptotically orbitally stable systems. The reduction removes this trivial +1 eigenvalue.</p>
          </ThemedBox>
        </Section>

        {/* 4.6 */}
        <Section id="poincare" number="6" title="Moving Poincaré Sections">
          <p className="text-gray-700 leading-relaxed mb-4">
            The golf swing is not periodic — it's a finite-time trajectory. Classical Poincaré sections need periodicity. The generalization: <strong>moving Poincaré sections</strong>, a continuous family of transverse hyperplanes along the orbit.
          </p>

          <ThemedBox title="Principle 4.2." number="Finite-Time Orbital Stability" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <p className="mb-2">The <strong>transverse amplification ratio</strong> from phase s₁ to s₂:</p>
            <MathBlock label="(4.15)">ρ(s₁, s₂) = σ_max(Φ⊥(s₂, s₁))</MathBlock>
            <p>If ρ {'<'} 1, deviations shrink. If ρ {'>'} 1, they grow. For trajectory design, we require ρ(0, s_impact) ≪ 1 — deviations contract toward impact. This is the <strong>funnel from Chapter 1</strong>, now made precise.</p>
          </ThemedBox>

          <AmplificationProfile />

          <ThemedBox title="Example 4.4." number="Golf Swing Amplification Profile" borderColor="gray" bgColor={colors.softgray}>
            <p className="mb-1"><strong>Backswing:</strong> ρ ≈ 1, slow and nearly linear.</p>
            <p className="mb-1"><strong>Transition:</strong> ρ {'>'} 1, high curvature amplifies errors — the unstable phase.</p>
            <p className="mb-1"><strong>Late downswing:</strong> ρ drops sharply. The passive double-pendulum release is self-stabilizing transversely.</p>
            <p><strong>Impact:</strong> ρ(0, impact) {'<'} 1. Net contraction — the natural funnel. Skilled golfers are accurate because the trajectory's passive transverse dynamics create contraction without active feedback.</p>
          </ThemedBox>
        </Section>

        {/* 4.7 */}
        <Section id="controller" number="7" title="Controller Design via Transverse Stabilization">
          <ThemedBox title="Principle 4.3." number="Transverse LQR" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <p className="mb-2">Solve the differential Riccati equation for the transverse dynamics:</p>
            <MathBlock label="(4.17)">−Ṡ = A⊥ᵀS + SA⊥ − SB⊥R⁻¹B⊥ᵀS + Q(t)</MathBlock>
            <p className="mb-2">Optimal feedback: <MathInline>K⊥(t) = R⁻¹ B⊥ᵀ S(t)</MathInline></p>
            <p>Q(t) penalizes transverse deviation (large near impact = tight funnel). R penalizes effort. The phase-dependent Q creates exactly the time-varying tube from Chapter 1.</p>
          </ThemedBox>

          <ControllerArchitecture />

          <ThemedBox title="Theorem 4.3." number="Riccati Funnel" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <p>The ellipsoidal set {'{'}ξ : ξᵀS(t)ξ ≤ c{'}'} defines a time-varying tube whose width ~ 1/√λₖ(t). As the terminal penalty S_T tightens, the tube narrows toward impact. <strong>The funnel is the level set of the Riccati cost-to-go.</strong></p>
          </ThemedBox>

          <SubSection title="Why Not Standard LQR?">
            <WhyNotStandardLQR />
          </SubSection>
        </Section>

        {/* 4.8 */}
        <Section id="robustness" number="8" title="Robustness of Orbital Stability">
          <ThemedBox title="Proposition 4.1." number="Transverse LQR Robustness" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <p>With R = rI, the transverse LQR inherits classical LQR robustness: gain margin [½, ∞) and phase margin ±60° in each transverse channel. For the golf swing, robustness = <strong>repeatability</strong>: consistent results despite noisy motor commands.</p>
          </ThemedBox>
        </Section>

        {/* 4.9 */}
        <Section id="summary" number="9" title="Summary">
          <SummaryTable />

          <p className="text-gray-700 leading-relaxed mb-4">
            This chapter provided the mathematical backbone for everything that follows. The transverse linearization converts nonlinear trajectory tracking into a linear, lower-dimensional problem. The Floquet/Poincaré framework gives both analytical insight and numerical algorithms.
          </p>
          <p className="text-gray-700 leading-relaxed mb-4">
            The key insight for the golf swing: orbital stability — not Lyapunov stability — is the correct framework. The swing's passive transverse dynamics create a natural funnel, and transverse LQR tightens it with phase-varying gains.
          </p>
          <p className="text-gray-700 leading-relaxed">
            In Chapter 5, we'll see how <strong>underactuation</strong> constrains the transverse dynamics, creating geometric structure to exploit rather than tolerate.
          </p>

          <div className="mt-10 text-center border-t pt-6">
            <div className="w-32 h-px bg-gray-300 mx-auto mb-4" />
            <p className="text-sm italic text-gray-500 leading-relaxed">
              The pendulum does not care if you are watching at noon or midnight.<br />
              Its orbit knows no clock.<br /><br />
              Stability is not arrival. It is the promise<br />
              that the motion, once begun, will keep its shape—<br />
              even when the world pushes back.
            </p>
          </div>
        </Section>
      </div>
    </div>
  );
}

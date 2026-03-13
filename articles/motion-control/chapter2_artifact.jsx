import { useState } from "react";

const colors = {
  chapblue: "#004682",
  accentred: "#B42828",
  trajgreen: "#1E823C",
  darkgold: "#A07814",
  purple: "#64288C",
  softgray: "#F5F5F5",
  lightblue: "#E8F0F8",
  lightred: "#FDF0F0",
  lightgreen: "#F0F8F2",
  lightgold: "#FDF8E8",
  lightpurple: "#F5F0F8",
};

function MathBlock({ children, label }) {
  return (
    <div className="my-4 bg-gray-50 border-l-4 border-gray-300 p-4 overflow-x-auto">
      <div className="font-mono text-sm leading-relaxed text-gray-800">{children}</div>
      {label && <div className="text-xs text-gray-500 mt-1 text-right">{label}</div>}
    </div>
  );
}

function MathInline({ children }) {
  return <span className="font-mono text-sm" style={{ color: colors.chapblue }}>{children}</span>;
}

function ThemedBox({ title, number, color, bgColor, borderColor, children }) {
  return (
    <div className="my-6 rounded-lg overflow-hidden shadow-sm" style={{ border: `2px solid ${borderColor}` }}>
      <div className="px-4 py-2" style={{ backgroundColor: borderColor }}>
        <span className="font-bold text-white text-sm">{title} {number}</span>
      </div>
      <div className="p-4 text-sm leading-relaxed" style={{ backgroundColor: bgColor }}>
        {children}
      </div>
    </div>
  );
}

function Section({ id, number, title, children }) {
  return (
    <section id={id} className="mb-10">
      <h2 className="text-2xl font-bold mb-4 pb-2 border-b-2" style={{ color: colors.chapblue, borderColor: colors.chapblue }}>
        2.{number} &nbsp;{title}
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

function CurvatureDemo() {
  const [speed, setSpeed] = useState(25);
  const [curvature, setCurvature] = useState(2.0);
  const aPerp = curvature * speed * speed;
  const gForce = aPerp / 9.81;

  return (
    <div className="my-6 p-5 rounded-xl bg-white shadow-md border border-gray-200">
      <h4 className="font-bold text-base mb-4" style={{ color: colors.accentred }}>
        Interactive: Curvature–Authority Relationship
      </h4>
      <p className="text-sm text-gray-600 mb-4">
        Explore how speed and curvature combine to determine centripetal acceleration demand: <MathInline>a⊥ = κ · v²</MathInline>
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Speed <MathInline>v</MathInline> = {speed} m/s
          </label>
          <input
            type="range" min="1" max="60" value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
            className="w-full accent-blue-700"
          />
          <div className="flex justify-between text-xs text-gray-400">
            <span>1 m/s (practice)</span>
            <span>60 m/s (elite)</span>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">
            Curvature <MathInline>κ</MathInline> = {curvature.toFixed(1)} rad/m
          </label>
          <input
            type="range" min="1" max="50" value={curvature * 10}
            onChange={(e) => setCurvature(Number(e.target.value) / 10)}
            className="w-full accent-red-700"
          />
          <div className="flex justify-between text-xs text-gray-400">
            <span>0.1 (gentle)</span>
            <span>5.0 (tight bend)</span>
          </div>
        </div>
      </div>
      <div className="flex items-center gap-4 p-4 rounded-lg" style={{ backgroundColor: gForce > 100 ? "#FEE2E2" : gForce > 50 ? "#FEF3C7" : "#ECFDF5" }}>
        <div className="text-center flex-1">
          <div className="text-3xl font-bold" style={{ color: gForce > 100 ? colors.accentred : gForce > 50 ? colors.darkgold : colors.trajgreen }}>
            {aPerp.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">m/s² centripetal</div>
        </div>
        <div className="text-center flex-1">
          <div className="text-3xl font-bold" style={{ color: gForce > 100 ? colors.accentred : gForce > 50 ? colors.darkgold : colors.trajgreen }}>
            {gForce.toFixed(1)}g
          </div>
          <div className="text-xs text-gray-500">g-forces</div>
        </div>
        <div className="text-center flex-1">
          <div className="text-sm font-medium" style={{ color: gForce > 100 ? colors.accentred : gForce > 50 ? colors.darkgold : colors.trajgreen }}>
            {gForce > 100 ? "🔴 Extreme demand" : gForce > 50 ? "🟡 High demand" : gForce > 10 ? "🟢 Moderate" : "⚪ Low"}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {gForce > 100 ? "Requires passive dynamics" : gForce > 50 ? "Near actuator limits" : "Within active control"}
          </div>
        </div>
      </div>
      <p className="text-xs text-gray-500 mt-3 italic">
        Note: v² scaling means doubling speed quadruples the centripetal demand. This is why the "pause at the top" exists—the timing law respects the curvature speed limit.
      </p>
    </div>
  );
}

function FrenetDiagram() {
  return (
    <svg viewBox="0 0 500 300" className="w-full max-w-lg mx-auto my-6">
      <defs>
        <marker id="arrowGreen" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill={colors.trajgreen} />
        </marker>
        <marker id="arrowBlue" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill={colors.chapblue} />
        </marker>
        <marker id="arrowRed" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill={colors.accentred} />
        </marker>
        <marker id="arrowPurple" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill={colors.purple} />
        </marker>
      </defs>
      {/* Curve */}
      <path d="M 50 220 C 120 220, 150 80, 250 120 C 350 160, 380 60, 450 80"
        fill="none" stroke={colors.trajgreen} strokeWidth="3" />
      <text x="455" y="75" fill={colors.trajgreen} fontSize="14" fontWeight="bold">γ*(s)</text>
      {/* Point on curve */}
      <circle cx="250" cy="120" r="5" fill={colors.trajgreen} />
      {/* Tangent vector e1 */}
      <line x1="250" y1="120" x2="330" y2="135" stroke={colors.chapblue} strokeWidth="2.5" markerEnd="url(#arrowBlue)" />
      <text x="335" y="132" fill={colors.chapblue} fontSize="13" fontWeight="bold">e₁ (tangent)</text>
      {/* Normal vector e2 */}
      <line x1="250" y1="120" x2="265" y2="40" stroke={colors.accentred} strokeWidth="2.5" markerEnd="url(#arrowRed)" />
      <text x="270" y="38" fill={colors.accentred} fontSize="13" fontWeight="bold">e₂ (normal)</text>
      {/* Binormal e3 - coming "out of page" shown as shorter */}
      <line x1="250" y1="120" x2="200" y2="70" stroke={colors.purple} strokeWidth="2" strokeDasharray="5,3" markerEnd="url(#arrowPurple)" />
      <text x="155" y="65" fill={colors.purple} fontSize="12" fontWeight="bold">e₃ (binormal)</text>
      {/* Osculating circle */}
      <circle cx="265" cy="20" r="100" fill="none" stroke="#ccc" strokeWidth="1" strokeDasharray="4,4" />
      <text x="320" y="15" fill="#999" fontSize="11">osculating circle</text>
      <text x="340" y="30" fill="#999" fontSize="11">R = 1/κ</text>
      {/* Phase axis */}
      <line x1="50" y1="270" x2="450" y2="270" stroke="#aaa" strokeWidth="1" />
      <text x="455" y="274" fill="#999" fontSize="11">s</text>
      <line x1="250" y1="265" x2="250" y2="275" stroke="#aaa" strokeWidth="1" />
      <text x="243" y="288" fill="#999" fontSize="11">s₀</text>
      <text x="45" y="288" fill="#999" fontSize="11">0</text>
      <text x="440" y="288" fill="#999" fontSize="11">L</text>
    </svg>
  );
}

function FunnelTimingDiagram() {
  const phases = [
    { label: "Backswing", start: 0, end: 30, color: colors.chapblue, annotation: "κ moderate, v low → low demand" },
    { label: "Transition", start: 30, end: 45, color: colors.darkgold, annotation: "κ HIGH, v rising → PEAK demand" },
    { label: "Downswing", start: 45, end: 70, color: colors.accentred, annotation: "κ decreasing, v HIGH → high demand" },
    { label: "Impact", start: 70, end: 80, color: colors.trajgreen, annotation: "κ moderate, v maximum → precision zone" },
    { label: "Follow-through", start: 80, end: 100, color: "#999", annotation: "κ low, v decreasing → relaxed" },
  ];
  return (
    <div className="my-6 p-4 bg-white rounded-lg shadow-sm border">
      <h4 className="font-bold text-sm mb-3" style={{ color: colors.chapblue }}>Curvature × Speed² Along the Golf Swing</h4>
      <div className="flex h-8 rounded-full overflow-hidden mb-2">
        {phases.map((p, i) => (
          <div key={i} className="flex items-center justify-center text-white text-xs font-bold"
            style={{ width: `${p.end - p.start}%`, backgroundColor: p.color }}>
            {p.label}
          </div>
        ))}
      </div>
      <div className="space-y-1">
        {phases.map((p, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: p.color }} />
            <span className="text-gray-600">{p.annotation}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function TableOfConcepts() {
  const rows = [
    { concept: "Arc length s", significance: "Natural \"distance along path\"—separates shape from timing" },
    { concept: "Curvature κ(s)", significance: "Determines centripetal control demand a⊥ = κv²" },
    { concept: "Torsion τ(s)", significance: "Measures out-of-plane complexity; multi-joint coordination" },
    { concept: "Frenet–Serret frame", significance: "Moving coordinate system for tangential/transverse decomposition" },
    { concept: "Curvature signature", significance: "Uniquely specifies trajectory shape, independent of timing" },
    { concept: "Path–timing separation", significance: "Decomposes control into path design + speed planning" },
  ];
  return (
    <div className="my-6 overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr style={{ backgroundColor: colors.chapblue }}>
            <th className="text-left text-white p-3 font-bold">Concept</th>
            <th className="text-left text-white p-3 font-bold">Control Significance</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
              <td className="p-3 font-mono text-sm" style={{ color: colors.chapblue }}>{r.concept}</td>
              <td className="p-3 text-gray-700">{r.significance}</td>
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
  { id: "geometry", num: "1", title: "Why Geometry Comes First", short: "2.1 Geometry First" },
  { id: "param", num: "2", title: "Parameterized Curves", short: "2.2 Parameterization" },
  { id: "arclength", num: "3", title: "Arc Length", short: "2.3 Arc Length" },
  { id: "curvature", num: "4", title: "Curvature", short: "2.4 Curvature" },
  { id: "frenet", num: "5", title: "The Frenet–Serret Frame", short: "2.5 Frenet–Serret" },
  { id: "control-lang", num: "6", title: "Curvature in Control Language", short: "2.6 Control Language" },
  { id: "reparam", num: "7", title: "Reparameterization & Timing", short: "2.7 Timing Laws" },
  { id: "osculating", num: "8", title: "Osculating Objects", short: "2.8 Osculating" },
  { id: "deviations", num: "9", title: "Geometry of Deviations", short: "2.9 Deviations" },
  { id: "fundamental", num: "10", title: "Fundamental Theorem", short: "2.10 Fundamental Thm" },
  { id: "summary", num: "11", title: "Summary", short: "2.11 Summary" },
];

export default function Chapter2() {
  const [activeSection, setActiveSection] = useState("geometry");

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
          <p className="text-sm font-bold uppercase tracking-widest mb-2" style={{ color: colors.chapblue }}>
            Chapter 2
          </p>
          <h1 className="text-4xl font-bold mb-4" style={{ color: colors.chapblue }}>
            Curves in State Space
          </h1>
          <p className="text-lg italic text-gray-500 border-l-4 pl-4" style={{ borderColor: colors.darkgold }}>
            "The shortest distance between two points is a straight line, but no interesting motion has ever been straight."
          </p>
          <div className="h-1 w-full rounded mt-6" style={{ backgroundColor: colors.chapblue }} />
        </div>

        {/* 2.1 */}
        <Section id="geometry" number="1" title="Why Geometry Comes First">
          <p className="text-gray-700 leading-relaxed mb-4">
            In Chapter 1 we argued that control is fundamentally about <em>motion</em>—the faithful execution of a trajectory through state space. Before we can stabilize a trajectory, optimize it, or confine the system to a tube around it, we need to understand what a trajectory <em>is</em> as a mathematical object.
          </p>
          <p className="text-gray-700 leading-relaxed mb-4">
            This chapter develops the differential geometry of curves in ℝⁿ, adapted to the needs of control theory. The central insight is that a trajectory has intrinsic geometric properties—curvature, torsion, and a natural moving frame—that exist independently of how fast the system moves along the curve.
          </p>
          <ThemedBox title="Key Idea 2.1." number="Intrinsic vs. Extrinsic" color={colors.accentred} bgColor={colors.lightred} borderColor={colors.accentred}>
            <p className="mb-2">A trajectory has two kinds of properties:</p>
            <p className="mb-1"><strong>Intrinsic:</strong> Properties of the curve itself—its shape, curvature, how it bends and twists. Independent of parameterization.</p>
            <p className="mb-2"><strong>Extrinsic:</strong> Properties that depend on how the curve is traversed—speed, acceleration, timing. Depend on parameterization.</p>
            <p>Good control design separates these cleanly. The <em>trajectory planner</em> designs the intrinsic shape. The <em>timing law</em> specifies speed. The <em>tracking controller</em> maintains both.</p>
          </ThemedBox>
        </Section>

        {/* 2.2 */}
        <Section id="param" number="2" title="Parameterized Curves">
          <ThemedBox title="Definition 2.1." number="Parameterized Curve" color={colors.darkgold} bgColor={colors.lightgold} borderColor={colors.darkgold}>
            <p>A <strong>parameterized curve</strong> in ℝⁿ is a smooth map <MathInline>γ: I → ℝⁿ</MathInline>, where <MathInline>I ⊆ ℝ</MathInline> is an interval. The parameter may be time <MathInline>t</MathInline>, arc length <MathInline>s</MathInline>, or any monotone scalar. The curve is <strong>regular</strong> if <MathInline>γ'(λ) ≠ 0</MathInline> for all <MathInline>λ ∈ I</MathInline>.</p>
          </ThemedBox>
          <p className="text-gray-700 leading-relaxed mb-4">
            The critical point is that many different parameterizations describe the same geometric curve. The <strong>unit tangent vector</strong> strips away speed information:
          </p>
          <MathBlock label="(2.3)">e₁(λ) = γ'(λ) / ‖γ'(λ)‖</MathBlock>
          <p className="text-gray-700 leading-relaxed">
            The tangent vector <MathInline>e₁</MathInline> tells us the <em>direction</em> of the curve—a purely geometric quantity. The speed tells us how <em>fast</em> we traverse it—a parameterization-dependent quantity.
          </p>
        </Section>

        {/* 2.3 */}
        <Section id="arclength" number="3" title="Arc Length: The Natural Parameter">
          <ThemedBox title="Definition 2.2." number="Arc Length" color={colors.darkgold} bgColor={colors.lightgold} borderColor={colors.darkgold}>
            <p>The <strong>arc length</strong> of a curve from <MathInline>λ = a</MathInline> to <MathInline>λ = b</MathInline> is</p>
            <MathBlock>L = ∫ₐᵇ ‖γ'(λ)‖ dλ</MathBlock>
            <p>When parameterized by arc length, speed is identically 1: <MathInline>‖γ'(s)‖ = 1</MathInline> for all <MathInline>s</MathInline>.</p>
          </ThemedBox>
          <ThemedBox title="Principle 2.1." number="Arc Length as Canonical Clock" color={colors.chapblue} bgColor={colors.lightblue} borderColor={colors.chapblue}>
            <p>Arc-length parameterization strips away all timing information and reveals the pure geometry. For a golf swing, <MathInline>γ(s)</MathInline> describes the spatial path. The timing law <MathInline>s(t)</MathInline> is a separate design choice. A slow practice swing and a full-speed competition swing follow the same <MathInline>γ(s)</MathInline> with different <MathInline>s(t)</MathInline>.</p>
          </ThemedBox>
          <ThemedBox title="Remark 2.1." number="Arc Length in High Dimensions" color={colors.purple} bgColor={colors.lightpurple} borderColor={colors.purple}>
            <p>When the state space carries a Riemannian metric (the mass-inertia matrix for mechanical systems), arc length generalizes to:</p>
            <MathBlock>L = ∫ₐᵇ √(γ'ᵀ G(γ) γ') dλ</MathBlock>
            <p>This means "distance in configuration space" naturally weights by segment mass—a heavy limb contributes more to arc length than a light one.</p>
          </ThemedBox>
        </Section>

        {/* 2.4 */}
        <Section id="curvature" number="4" title="Curvature: How Curves Bend">
          <ThemedBox title="Definition 2.3." number="Curvature" color={colors.darkgold} bgColor={colors.lightgold} borderColor={colors.darkgold}>
            <p>For a curve parameterized by arc length, the <strong>curvature</strong> is</p>
            <MathBlock label="(2.5)">κ(s) = ‖γ''(s)‖ = ‖de₁/ds‖</MathBlock>
            <p>Curvature measures the rate of turning per unit distance. The reciprocal <MathInline>R = 1/κ</MathInline> is the <strong>radius of curvature</strong>.</p>
          </ThemedBox>

          <p className="text-gray-700 leading-relaxed mb-4">
            For arbitrary parameterization, curvature can be computed as:
          </p>
          <MathBlock label="Theorem 2.1">κ(t) = √(‖γ'‖²‖γ''‖² − (γ'·γ'')²) / ‖γ'‖³</MathBlock>

          <ThemedBox title="Example 2.2." number="Elliptical Trajectory" color="gray" bgColor={colors.softgray} borderColor="#999">
            <p>For the ellipse <MathInline>γ(t) = (a cos t, b sin t)</MathInline>:</p>
            <MathBlock>κ(t) = ab / (a²sin²t + b²cos²t)^(3/2)</MathBlock>
            <p>Curvature is <em>highest at the ends of the minor axis</em> and <em>lowest at the ends of the major axis</em>. The tighter the bend, the more control authority needed to track it.</p>
          </ThemedBox>
        </Section>

        {/* 2.5 */}
        <Section id="frenet" number="5" title="The Frenet–Serret Frame">
          <p className="text-gray-700 leading-relaxed mb-4">
            The tangent vector is only the first element of a natural coordinate frame that moves with the curve. This <strong>Frenet–Serret frame</strong> provides a complete local coordinate system at every point.
          </p>

          <FrenetDiagram />

          <ThemedBox title="Definition 2.4." number="Frenet–Serret Frame" color={colors.darkgold} bgColor={colors.lightgold} borderColor={colors.darkgold}>
            <p className="mb-2">The frame <MathInline>{'{'}e₁, e₂, ..., eₚ{'}'}</MathInline> is constructed by Gram–Schmidt orthonormalization of successive arc-length derivatives of the curve.</p>
            <div className="my-3 overflow-x-auto">
              <table className="text-sm">
                <tbody>
                  <tr><td className="pr-4 font-mono" style={{color: colors.chapblue}}>e₁ = T</td><td className="pr-4">Unit tangent</td><td>Direction of motion</td></tr>
                  <tr><td className="pr-4 font-mono" style={{color: colors.accentred}}>e₂ = N</td><td className="pr-4">Principal normal</td><td>Direction the curve bends toward</td></tr>
                  <tr><td className="pr-4 font-mono" style={{color: colors.purple}}>e₃ = B</td><td className="pr-4">Binormal</td><td>T × N; normal to osculating plane</td></tr>
                </tbody>
              </table>
            </div>
          </ThemedBox>

          <ThemedBox title="Theorem 2.2." number="Frenet–Serret Equations" color={colors.chapblue} bgColor={colors.lightblue} borderColor={colors.chapblue}>
            <p className="mb-2">The frame evolves along the curve via the skew-symmetric system:</p>
            <MathBlock>d/ds [e₁, e₂, ..., eₚ]ᵀ = Ω · [e₁, e₂, ..., eₚ]ᵀ</MathBlock>
            <p>where <MathInline>Ω</MathInline> is skew-symmetric with entries <MathInline>κ₁, κ₂, ..., κₚ₋₁</MathInline> (the generalized curvatures) on the super/sub-diagonals. Skew-symmetry guarantees the frame remains orthonormal—it rotates without stretching.</p>
          </ThemedBox>

          <ThemedBox title="Principle 2.3." number="Dynamic Rank of a Trajectory" color={colors.chapblue} bgColor={colors.lightblue} borderColor={colors.chapblue}>
            <p>For a system with <MathInline>N</MathInline> DOF and <MathInline>m</MathInline> actuators, a generic trajectory has at most <MathInline>p = 2m</MathInline> linearly independent arc-length derivatives. Underactuated systems (<MathInline>m {'<'} N</MathInline>) have trajectories geometrically confined to a submanifold—curvatures in "forbidden" directions are set by passive dynamics.</p>
          </ThemedBox>
        </Section>

        {/* 2.6 */}
        <Section id="control-lang" number="6" title="Curvature and Torsion in the Language of Control">
          <ThemedBox title="Principle 2.2." number="The Curvature–Authority Principle" color={colors.chapblue} bgColor={colors.lightblue} borderColor={colors.chapblue}>
            <p className="mb-2">The centripetal acceleration required to follow a curve at speed <MathInline>v</MathInline> is:</p>
            <MathBlock label="(2.12)">a⊥ = κ · v²</MathBlock>
            <p>(i) High curvature demands high lateral authority. (ii) Required authority grows as the <em>square</em> of speed. (iii) A trajectory easy to track slowly may be impossible at high speed.</p>
          </ThemedBox>

          <CurvatureDemo />

          <ThemedBox title="Example 2.4." number="Curvature Cost in the Golf Downswing" color="gray" bgColor={colors.softgray} borderColor="#999">
            <p>Mid-downswing: <MathInline>v ≈ 25</MathInline> m/s, <MathInline>κ ≈ 2</MathInline> rad/m. Centripetal demand:</p>
            <MathBlock>a⊥ ≈ 2 × 25² = 1250 m/s² ≈ 127g</MathBlock>
            <p>This demand is met by <em>passive coupling</em> in the kinematic chain—the very underactuation that setpoint control treats as a constraint. The geometry creates the forces needed to execute the motion.</p>
          </ThemedBox>

          <FunnelTimingDiagram />
        </Section>

        {/* 2.7 */}
        <Section id="reparam" number="7" title="Reparameterization and Timing Laws">
          <ThemedBox title="Definition 2.6." number="Timing Law" color={colors.darkgold} bgColor={colors.lightgold} borderColor={colors.darkgold}>
            <p>Given <MathInline>γ*(s)</MathInline> parameterized by arc length, a <strong>timing law</strong> is a smooth, monotonically increasing function <MathInline>s: [0, T] → [0, L]</MathInline>. Different timing laws produce different motions through the same geometric path.</p>
          </ThemedBox>

          <ThemedBox title="Principle 2.4." number="Path–Timing Separation" color={colors.chapblue} bgColor={colors.lightblue} borderColor={colors.chapblue}>
            <p className="mb-2">The trajectory control problem decomposes into two subproblems:</p>
            <p className="mb-1"><strong>(A) Path design:</strong> Choose the geometric curve that achieves the task. Key quantity: curvature <MathInline>κ(s)</MathInline>.</p>
            <p className="mb-2"><strong>(B) Timing design:</strong> Choose <MathInline>s(t)</MathInline> balancing speed against tracking difficulty. Key quantity: speed profile <MathInline>v(s)</MathInline>.</p>
            <p>The interaction is captured by the curvature cost <MathInline>κ(s)·v(s)²</MathInline>, which must stay within controller authority everywhere.</p>
          </ThemedBox>

          <ThemedBox title="Example 2.5." number="Timing the Downswing" color="gray" bgColor={colors.softgray} borderColor="#999">
            <p>At maximum path curvature <MathInline>κ_max</MathInline>, the geometric speed limit is:</p>
            <MathBlock>v_transition ≤ √(a_max / κ_max)</MathBlock>
            <p>The golfer's "pause at the top" is not aesthetic—it is the timing law respecting the curvature speed limit at maximum path curvature.</p>
          </ThemedBox>
        </Section>

        {/* 2.8 */}
        <Section id="osculating" number="8" title="The Osculating Objects">
          <ThemedBox title="Definition 2.7." number="Osculating Objects" color={colors.darkgold} bgColor={colors.lightgold} borderColor={colors.darkgold}>
            <p className="mb-1"><strong>(i) Osculating line:</strong> Tangent line—best linear approximation.</p>
            <p className="mb-1"><strong>(ii) Osculating circle:</strong> In the (T, N) plane, radius <MathInline>R = 1/κ</MathInline>—best circular approximation.</p>
            <p className="mb-1"><strong>(iii) Osculating plane:</strong> Spanned by T and N. Torsion measures departure rate.</p>
            <p><strong>(iv) Osculating sphere:</strong> Best third-order approximation, accounts for curvature and torsion.</p>
          </ThemedBox>
        </Section>

        {/* 2.9 */}
        <Section id="deviations" number="9" title="The Geometry of Trajectory Deviations">
          <ThemedBox title="Definition 2.8." number="Frenet–Serret Coordinates" color={colors.darkgold} bgColor={colors.lightgold} borderColor={colors.darkgold}>
            <p>Any state near the reference decomposes as:</p>
            <MathBlock>x = γ*(s*) + Σ ξₖ eₖ(s*)</MathBlock>
            <p>where <MathInline>s*</MathInline> is the tangential coordinate and <MathInline>ξ = (ξ₂, ..., ξₙ)</MathInline> are transverse coordinates. Tracking becomes: <em>regulate ξ to zero while s* advances.</em></p>
          </ThemedBox>

          <SubSection title="Curvature-Induced Coupling">
            <p className="text-gray-700 leading-relaxed mb-4">
              Because the Frenet–Serret frame rotates along the curve, the linearized transverse dynamics have a <strong>curvature-induced coupling</strong>:
            </p>
            <MathBlock label="Proposition 2.1">ξ̇ = [A(s) − v² K(s)] ξ + B(s) u_fb</MathBlock>
            <p className="text-gray-700 leading-relaxed">
              The term <MathInline>v²K(s)</MathInline> depends on the generalized curvatures—the <em>stability of trajectory tracking depends on the geometry of the trajectory.</em> Low-curvature trajectories are inherently easier to stabilize.
            </p>
          </SubSection>
        </Section>

        {/* 2.10 */}
        <Section id="fundamental" number="10" title="Fundamental Theorem and Uniqueness">
          <ThemedBox title="Theorem 2.3." number="Fundamental Theorem of Curves" color={colors.chapblue} bgColor={colors.lightblue} borderColor={colors.chapblue}>
            <p className="mb-2">Given smooth curvature functions <MathInline>κ₁(s), ..., κₚ₋₁(s)</MathInline> on <MathInline>[0, L]</MathInline>, there exists a curve whose generalized curvatures match exactly. This curve is <strong>unique up to rigid motions.</strong></p>
            <p className="font-bold" style={{ color: colors.chapblue }}>The curvature signature IS the trajectory.</p>
          </ThemedBox>

          <ThemedBox title="Remark 2.2." number="The Curvature Signature" color={colors.purple} bgColor={colors.lightpurple} borderColor={colors.purple}>
            <p>If a golfer can reproduce the curvature signature of their swing, the spatial path is automatically reproduced, regardless of timing. A coach's instruction to "flatten your swing plane" is a request to reduce <MathInline>κ₂(s)</MathInline> during a specific phase—a precise modification to the curvature signature.</p>
          </ThemedBox>
        </Section>

        {/* 2.11 */}
        <Section id="summary" number="11" title="Summary">
          <TableOfConcepts />

          <p className="text-gray-700 leading-relaxed mb-4">
            The key takeaway: a trajectory is not just "a function of time." It is a geometric object with intrinsic structure that directly determines the difficulty of controlling it. In Chapter 3, we will see that state spaces of mechanical systems are curved manifolds, and the interplay between curve geometry and space geometry produces the richest results of this book.
          </p>

          <div className="mt-10 text-center border-t pt-6">
            <div className="w-32 h-px bg-gray-300 mx-auto mb-4" />
            <p className="text-sm italic text-gray-500 leading-relaxed">
              The shape of a river is written in its curvature.<br />
              The story of a motion is written the same way.<br /><br />
              Learn to read the curvature, and you read the motion.
            </p>
          </div>
        </Section>
      </div>
    </div>
  );
}

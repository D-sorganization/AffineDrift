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
        3.{number} &nbsp;{title}
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

function JointTable() {
  const joints = [
    { type: "Revolute (hinge)", dof: 1, manifold: "S¹", topology: "Circle" },
    { type: "Prismatic (slider)", dof: 1, manifold: "ℝ", topology: "Line" },
    { type: "Universal", dof: 2, manifold: "S²", topology: "2-sphere" },
    { type: "Ball-and-socket", dof: 3, manifold: "SO(3)", topology: "Rotation group" },
    { type: "Planar", dof: 3, manifold: "ℝ² × S¹", topology: "Plane + rotation" },
    { type: "Free body", dof: 6, manifold: "SE(3)", topology: "Rigid motions" },
  ];
  return (
    <div className="my-6 overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr style={{ backgroundColor: colors.chapblue }}>
            <th className="text-left text-white p-3">Joint Type</th>
            <th className="text-center text-white p-3">DOF</th>
            <th className="text-center text-white p-3">Manifold</th>
            <th className="text-left text-white p-3">Topology</th>
          </tr>
        </thead>
        <tbody>
          {joints.map((j, i) => (
            <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
              <td className="p-3">{j.type}</td>
              <td className="p-3 text-center font-bold">{j.dof}</td>
              <td className="p-3 text-center font-mono" style={{ color: colors.accentred }}>{j.manifold}</td>
              <td className="p-3 text-gray-600">{j.topology}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function GimbalLockDemo() {
  const [theta, setTheta] = useState(45);
  const singularity = Math.abs(theta - 90) < 5 || Math.abs(theta + 90) < 5;
  const jacobianDet = Math.cos(theta * Math.PI / 180);
  const conditionNumber = Math.abs(jacobianDet) < 0.001 ? Infinity : 1 / Math.abs(jacobianDet);

  return (
    <div className="my-6 p-5 rounded-xl bg-white shadow-md border border-gray-200">
      <h4 className="font-bold text-base mb-3" style={{ color: colors.accentred }}>
        Interactive: Gimbal Lock in Euler Angles
      </h4>
      <p className="text-sm text-gray-600 mb-4">
        Drag θ (pitch angle) toward ±90° and watch the Jacobian determinant approach zero—the representation degenerates.
      </p>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">
          Pitch angle θ = {theta}°
        </label>
        <input type="range" min="-89" max="89" value={theta}
          onChange={(e) => setTheta(Number(e.target.value))}
          className="w-full" />
        <div className="flex justify-between text-xs text-gray-400">
          <span>-89° (near singularity)</span>
          <span>0° (safe)</span>
          <span>+89° (near singularity)</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className={`p-3 rounded-lg text-center ${singularity ? "bg-red-50 border-red-200 border" : "bg-green-50 border-green-200 border"}`}>
          <div className="text-2xl font-bold" style={{ color: singularity ? colors.accentred : colors.trajgreen }}>
            {jacobianDet.toFixed(3)}
          </div>
          <div className="text-xs text-gray-500">det(J) = cos(θ)</div>
        </div>
        <div className={`p-3 rounded-lg text-center ${singularity ? "bg-red-50 border-red-200 border" : "bg-green-50 border-green-200 border"}`}>
          <div className="text-2xl font-bold" style={{ color: singularity ? colors.accentred : colors.trajgreen }}>
            {conditionNumber === Infinity ? "∞" : conditionNumber.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">Condition number</div>
        </div>
        <div className={`p-3 rounded-lg text-center ${singularity ? "bg-red-50 border-red-200 border" : "bg-green-50 border-green-200 border"}`}>
          <div className="text-lg font-bold" style={{ color: singularity ? colors.accentred : colors.trajgreen }}>
            {singularity ? "⚠️ SINGULAR" : "✓ OK"}
          </div>
          <div className="text-xs text-gray-500">Status</div>
        </div>
      </div>

      {singularity && (
        <div className="mt-3 p-3 bg-red-50 rounded-lg border border-red-200">
          <p className="text-xs text-red-800">
            <strong>Gimbal lock!</strong> Small physical rotations produce infinite Euler angle rates.
            A controller computing torques from angle errors will command infinite torques here.
            This is a <em>coordinate singularity</em>, not a physical one—the fix is to work on SO(3) directly.
          </p>
        </div>
      )}
    </div>
  );
}

function InertiaWeightDemo() {
  const [angle, setAngle] = useState(10);
  const torsoInertia = 12.0;
  const wristInertia = 0.03;
  const angleRad = angle * Math.PI / 180;
  const torsoEnergy = 0.5 * torsoInertia * angleRad * angleRad;
  const wristEnergy = 0.5 * wristInertia * angleRad * angleRad;
  const ratio = Math.sqrt(torsoInertia / wristInertia);

  return (
    <div className="my-6 p-5 rounded-xl bg-white shadow-md border border-gray-200">
      <h4 className="font-bold text-base mb-3" style={{ color: colors.darkgold }}>
        Interactive: Inertia-Weighted Distance
      </h4>
      <p className="text-sm text-gray-600 mb-4">
        Same angular change, vastly different physical "distances" when measured by kinetic energy.
      </p>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">
          Angular change: {angle}°
        </label>
        <input type="range" min="1" max="45" value={angle}
          onChange={(e) => setAngle(Number(e.target.value))}
          className="w-full" />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-3">
        <div className="p-4 rounded-lg bg-blue-50 border border-blue-200">
          <div className="text-xs text-gray-500 mb-1">Torso rotation ({angle}°)</div>
          <div className="text-xs text-gray-400">I = 12 kg·m²</div>
          <div className="text-2xl font-bold mt-2" style={{ color: colors.chapblue }}>
            {torsoEnergy.toFixed(2)} J
          </div>
          <div className="w-full bg-blue-200 rounded-full h-3 mt-2">
            <div className="h-3 rounded-full" style={{
              width: `${Math.min(100, torsoEnergy / 2 * 100)}%`,
              backgroundColor: colors.chapblue
            }} />
          </div>
        </div>
        <div className="p-4 rounded-lg bg-yellow-50 border border-yellow-200">
          <div className="text-xs text-gray-500 mb-1">Wrist rotation ({angle}°)</div>
          <div className="text-xs text-gray-400">I = 0.03 kg·m²</div>
          <div className="text-2xl font-bold mt-2" style={{ color: colors.darkgold }}>
            {wristEnergy.toFixed(4)} J
          </div>
          <div className="w-full bg-yellow-200 rounded-full h-3 mt-2">
            <div className="h-3 rounded-full" style={{
              width: `${Math.min(100, wristEnergy / 2 * 100)}%`,
              backgroundColor: colors.darkgold
            }} />
          </div>
        </div>
      </div>

      <div className="p-3 bg-gray-50 rounded-lg text-center">
        <span className="text-sm text-gray-600">Torso is </span>
        <span className="text-lg font-bold" style={{ color: colors.accentred }}>{ratio.toFixed(0)}×</span>
        <span className="text-sm text-gray-600"> farther in the kinetic energy metric</span>
        <br />
        <span className="text-xs text-gray-400">({(torsoEnergy / wristEnergy).toFixed(0)}× more energy for the same angle)</span>
      </div>
    </div>
  );
}

function StickFigureDiagram() {
  return (
    <svg viewBox="0 0 520 320" className="w-full max-w-xl mx-auto my-6">
      {/* Ground */}
      <line x1="40" y1="280" x2="260" y2="280" stroke="#aaa" strokeWidth="2" />
      {/* Torso */}
      <line x1="150" y1="275" x2="150" y2="140" stroke={colors.chapblue} strokeWidth="4" />
      <text x="165" y="210" fill={colors.chapblue} fontSize="11">torso</text>
      {/* Spine joint */}
      <circle cx="150" cy="275" r="8" fill={colors.accentred} />
      <text x="165" y="295" fill={colors.accentred} fontSize="11" fontWeight="bold">SO(3)</text>
      {/* Shoulder joint */}
      <circle cx="150" cy="140" r="8" fill={colors.accentred} />
      <text x="165" y="135" fill={colors.accentred} fontSize="11" fontWeight="bold">SO(3)</text>
      {/* Upper arm */}
      <line x1="150" y1="140" x2="90" y2="200" stroke={colors.trajgreen} strokeWidth="4" />
      <text x="100" y="160" fill={colors.trajgreen} fontSize="11">arm</text>
      {/* Elbow */}
      <circle cx="90" cy="200" r="6" fill={colors.darkgold} />
      <text x="55" y="195" fill={colors.darkgold} fontSize="11" fontWeight="bold">S¹</text>
      {/* Forearm */}
      <line x1="90" y1="200" x2="55" y2="260" stroke={colors.purple} strokeWidth="4" />
      <text x="57" y="230" fill={colors.purple} fontSize="11">forearm</text>
      {/* Wrist */}
      <circle cx="55" cy="260" r="6" fill={colors.darkgold} />
      <text x="15" y="255" fill={colors.darkgold} fontSize="10" fontWeight="bold">S¹×S¹</text>
      {/* Club */}
      <line x1="55" y1="260" x2="20" y2="310" stroke="#555" strokeWidth="3" />
      <circle cx="20" cy="310" r="4" fill="#333" />
      <text x="5" y="305" fill="#555" fontSize="10">club</text>

      {/* Config space box */}
      <rect x="290" y="30" width="210" height="260" rx="8" fill="white" stroke="#ddd" strokeWidth="2" />
      <text x="310" y="60" fill={colors.chapblue} fontSize="14" fontWeight="bold">Configuration Space</text>
      <line x1="300" y1="70" x2="490" y2="70" stroke="#eee" strokeWidth="1" />
      <text x="310" y="95" fill="#333" fontSize="13" fontFamily="monospace">Q = SO(3) × SO(3)</text>
      <text x="310" y="120" fill="#333" fontSize="13" fontFamily="monospace">    × S¹ × S¹ × S¹</text>
      <line x1="300" y1="140" x2="490" y2="140" stroke="#eee" strokeWidth="1" />
      <text x="310" y="165" fill="#555" fontSize="12">dim = 3 + 3 + 1 + 1 + 1</text>
      <text x="310" y="185" fill="#555" fontSize="12" fontWeight="bold">    = 9</text>
      <line x1="300" y1="200" x2="490" y2="200" stroke="#eee" strokeWidth="1" />
      <text x="310" y="225" fill="#555" fontSize="12">State space: TQ</text>
      <text x="310" y="245" fill="#555" fontSize="12" fontWeight="bold">dim(TQ) = 18</text>
      <text x="310" y="275" fill={colors.accentred} fontSize="13" fontWeight="bold">Not ℝ⁹ !</text>
    </svg>
  );
}

function EuclideanVsManifoldTable() {
  const rows = [
    { euclidean: "Q = ℝⁿ", manifold: "Q = SO(3)ᵏ × Tᵐ × ..." },
    { euclidean: "Error: e = q − q*", manifold: "Error: e = log((q*)⁻¹ q)" },
    { euclidean: "Derivative: q̈", manifold: "Covariant derivative: ∇q̇ q̇" },
    { euclidean: "Shortest path: straight line", manifold: "Shortest path: geodesic" },
    { euclidean: "Distance: ‖q₂ − q₁‖", manifold: "Geodesic distance: dG(q₁, q₂)" },
    { euclidean: "Curvature: κ (Ch. 2)", manifold: "Geodesic curvature: κg" },
    { euclidean: "Coriolis: \"extra forces\"", manifold: "Christoffel symbols: geometry" },
    { euclidean: "PD: −kp·e − kd·ė", manifold: "−kp·log(·)ᵛ − kd·(parallel transport)" },
  ];
  return (
    <div className="my-6 overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr style={{ backgroundColor: colors.chapblue }}>
            <th className="text-left text-white p-3">Euclidean Assumption</th>
            <th className="text-left text-white p-3">Manifold Replacement</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
              <td className="p-3 font-mono text-xs text-gray-500 line-through decoration-gray-300">{r.euclidean}</td>
              <td className="p-3 font-mono text-xs" style={{ color: colors.chapblue }}>{r.manifold}</td>
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
  { id: "lie", num: "1", title: "The Lie That Coordinates Tell", short: "3.1 Coordinate Lies" },
  { id: "manifolds", num: "2", title: "Smooth Manifolds", short: "3.2 Manifolds" },
  { id: "joints", num: "3", title: "Configuration Manifolds of Joints", short: "3.3 Joint Manifolds" },
  { id: "so3", num: "4", title: "The Rotation Group SO(3)", short: "3.4 SO(3)" },
  { id: "golf-config", num: "5", title: "The Golf Swing Config Space", short: "3.5 Golf Config" },
  { id: "riemannian", num: "6", title: "Riemannian Metrics & Mass Matrix", short: "3.6 Riemannian" },
  { id: "curves-revisited", num: "7", title: "Curves on Manifolds Revisited", short: "3.7 Curves Revisited" },
  { id: "error-metrics", num: "8", title: "Error Metrics on Manifolds", short: "3.8 Error Metrics" },
  { id: "eom", num: "9", title: "Equations of Motion", short: "3.9 EoM on Manifolds" },
  { id: "practical", num: "10", title: "Practical Implementation", short: "3.10 Implementation" },
  { id: "summary", num: "11", title: "Summary", short: "3.11 Summary" },
];

export default function Chapter3() {
  const [activeSection, setActiveSection] = useState("lie");
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
          <p className="text-sm font-bold uppercase tracking-widest mb-2" style={{ color: colors.chapblue }}>Chapter 3</p>
          <h1 className="text-4xl font-bold mb-4" style={{ color: colors.chapblue }}>Configuration Manifolds</h1>
          <p className="text-lg italic text-gray-500 border-l-4 pl-4" style={{ borderColor: colors.darkgold }}>
            "The map is not the territory. The coordinate chart is not the manifold. Every time you write θ for an angle, you are lying—just a little."
          </p>
          <div className="h-1 w-full rounded mt-6" style={{ backgroundColor: colors.chapblue }} />
        </div>

        {/* 3.1 */}
        <Section id="lie" number="1" title="The Lie That Coordinates Tell">
          <p className="text-gray-700 leading-relaxed mb-4">
            In Chapter 2 we developed curves in ℝⁿ. But the state spaces of real mechanical systems are <em>not</em> ℝⁿ. Consider the simplest rotating joint: a hinge. Its configuration is an angle θ, but θ = 0 and θ = 2π are the <em>same physical state</em>. The true configuration space is the circle S¹—locally like ℝ but globally completely different.
          </p>

          <ThemedBox title="Warning 3.1." number="The Gimbal Lock Catastrophe" borderColor={colors.accentred} bgColor={colors.lightred} icon="⚠️">
            <p className="mb-2">Representing orientation with three Euler angles encounters <strong>gimbal lock</strong>: at θ = ±π/2, two rotation axes align, losing a degree of freedom.</p>
            <p className="mb-2">This is a <em>coordinate singularity</em>—forcing SO(3) into ℝ³ coordinates. Apollo 13's IMU experienced this operationally.</p>
            <p className="font-bold" style={{ color: colors.accentred }}>If you use the wrong coordinates, your controller will have singularities that the physical system does not.</p>
          </ThemedBox>

          <GimbalLockDemo />

          <ThemedBox title="Key Idea 3.1." number="The Manifold Imperative" borderColor={colors.accentred} bgColor={colors.lightred}>
            <p>The configuration space of a mechanical system is a <strong>smooth manifold</strong> Q. Control theory built on ℝⁿ must be replaced by control on Q whenever: (i) joints allow full rotation, (ii) the trajectory traverses significant portions of configuration space, or (iii) singularity-free representation is required. For the golf swing, all three conditions are met.</p>
          </ThemedBox>
        </Section>

        {/* 3.2 */}
        <Section id="manifolds" number="2" title="Smooth Manifolds: The Minimum You Need">
          <ThemedBox title="Definition 3.1." number="Smooth Manifold" borderColor={colors.darkgold} bgColor={colors.lightgold}>
            <p>A <strong>smooth manifold</strong> M of dimension n is a space with a collection of <strong>coordinate charts</strong> {'{'}(Uα, φα){'}'} such that: (i) the charts cover M, (ii) each φα maps to ℝⁿ, and (iii) where charts overlap, transitions are smooth.</p>
            <p className="mt-2 italic text-gray-600">Key intuition: locally you can use coordinates, but no single coordinate system works globally. Like a road atlas needing multiple pages.</p>
          </ThemedBox>

          <SubSection title="Tangent Spaces and the Tangent Bundle">
            <ThemedBox title="Definition 3.3." number="Tangent Bundle" borderColor={colors.darkgold} bgColor={colors.lightgold}>
              <p>The <strong>tangent bundle</strong> TM is the collection of all tangent spaces. A point in TM is a pair (p, v)—a position and a velocity. For a mechanical system, the <strong>state space is the tangent bundle</strong>: X = TQ. A state is (q, q̇).</p>
            </ThemedBox>
          </SubSection>
        </Section>

        {/* 3.3 */}
        <Section id="joints" number="3" title="The Configuration Manifolds of Joints">
          <p className="text-gray-700 leading-relaxed mb-4">
            Every mechanical joint constrains relative motion. The allowed configurations form a manifold whose topology depends on the joint type:
          </p>
          <JointTable />
          <ThemedBox title="Definition 3.4." number="Product Configuration Space" borderColor={colors.darkgold} bgColor={colors.lightgold}>
            <p>For a serial chain of k joints with manifolds M₁, ..., Mₖ:</p>
            <MathBlock>Q = M₁ × M₂ × ··· × Mₖ</MathBlock>
            <p>Example: a 3-revolute robot arm has Q = S¹ × S¹ × S¹ = T³ (the 3-torus).</p>
          </ThemedBox>
        </Section>

        {/* 3.4 */}
        <Section id="so3" number="4" title="The Rotation Group SO(3)">
          <ThemedBox title="Definition 3.5." number="SO(3)" borderColor={colors.darkgold} bgColor={colors.lightgold}>
            <MathBlock>SO(3) = {'{'}R ∈ ℝ³ˣ³ : RᵀR = I, det(R) = 1{'}'}</MathBlock>
            <p>A 3-dimensional compact Lie group. Every 3-parameter representation has at least one singularity—this is a topological necessity.</p>
          </ThemedBox>

          <ThemedBox title="Principle 3.1." number="Representation Principle for Rotations" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <p className="mb-2">For trajectory control on SO(3), use:</p>
            <p className="mb-1"><strong>(a) Rotation matrices</strong> R ∈ ℝ³ˣ³: 9 params, 6 constraints. Singularity-free but redundant.</p>
            <p className="mb-1"><strong>(b) Unit quaternions</strong> q ∈ S³: 4 params, 1 constraint. Singularity-free, minimal redundancy.</p>
            <p className="mb-2"><strong>(c) Exponential coordinates:</strong> 3 params, singularity at ‖ω‖ = π. Natural for linearization.</p>
            <p className="font-bold" style={{ color: colors.accentred }}>Never use Euler angles for control of large-rotation trajectories.</p>
          </ThemedBox>

          <SubSection title="The Lie Algebra so(3) and the Exponential Map">
            <ThemedBox title="Definition 3.7." number="Exponential Map" borderColor={colors.darkgold} bgColor={colors.lightgold}>
              <p className="mb-2">The exponential map connects the Lie algebra (linear, where we can add and scale) to the Lie group (nonlinear, where dynamics live):</p>
              <MathBlock label="Rodrigues formula">R = exp([ω]×) = I + (sinθ/θ)[ω]× + ((1−cosθ)/θ²)[ω]×²</MathBlock>
              <p>where θ = ‖ω‖. Geometrically: rotation by angle θ about axis ω/θ.</p>
            </ThemedBox>
          </SubSection>
        </Section>

        {/* 3.5 */}
        <Section id="golf-config" number="5" title="The Golf Swing Configuration Space">
          <StickFigureDiagram />

          <ThemedBox title="Consequences for Control" number="" borderColor={colors.accentred} bgColor={colors.lightred}>
            <p className="mb-2"><strong>C1. No global linearization.</strong> You cannot write x = x* + δx with δx ∈ ℝ¹⁸. Linearization must use the tangent space via the exponential map.</p>
            <p className="mb-2"><strong>C2. Error is not a vector.</strong> The "error" between two configurations is log(q₁⁻¹ q₂) ∈ Lie algebra, not q₂ − q₁ (subtraction is undefined).</p>
            <p className="mb-2"><strong>C3. Geodesics replace straight lines.</strong> Shortest paths are geodesics on the Riemannian manifold.</p>
            <p><strong>C4. Parallel transport replaces vector addition.</strong> Comparing velocities at different trajectory points requires transport along the manifold.</p>
          </ThemedBox>

          <ThemedBox title="Warning 3.2." number="Euler Angle Catastrophe in Golf" borderColor={colors.accentred} bgColor={colors.lightred} icon="⚠️">
            <p>During the backswing, the shoulder passes near gimbal lock (θ ≈ ±π/2). In these regions, the Jacobian becomes singular, small rotations produce huge angle jumps, and angle-error controllers command <em>infinite torques</em>. The fix: work on SO(3) directly with rotation matrices or quaternions.</p>
          </ThemedBox>
        </Section>

        {/* 3.6 */}
        <Section id="riemannian" number="6" title="Riemannian Metrics and the Mass Matrix">
          <ThemedBox title="Principle 3.2." number="The Mass Matrix as Riemannian Metric" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <p className="mb-2">The kinetic energy T = ½ q̇ᵀ M(q) q̇ defines a Riemannian metric G = M(q) on Q:</p>
            <p className="mb-1"><strong>(i) Distance</strong> is measured in "kinetic energy units"—high-inertia motions are "far."</p>
            <p className="mb-1"><strong>(ii) Geodesics</strong> under this metric are free motions—no applied torques.</p>
            <p><strong>(iii) Arc length</strong> naturally weights each DOF by effective inertia.</p>
          </ThemedBox>

          <InertiaWeightDemo />

          <ThemedBox title="Principle 3.3." number="Geodesics and Passive Dynamics" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <p>Geodesics are the "easiest" paths—motions the system naturally follows with no forces. A well-designed trajectory stays close to geodesics where possible. The golf follow-through is nearly geodesic; the downswing deviates because impact conditions require active torques to redirect motion.</p>
          </ThemedBox>
        </Section>

        {/* 3.7 */}
        <Section id="curves-revisited" number="7" title="Curves on Manifolds Revisited">
          <ThemedBox title="Definition 3.9." number="Covariant Derivative" borderColor={colors.darkgold} bgColor={colors.lightgold}>
            <p>On a manifold, we cannot simply subtract vectors at different points. The <strong>covariant derivative</strong> ∇ is the unique differentiation compatible with the metric and torsion-free. It replaces d/ds in all Chapter 2 formulas.</p>
          </ThemedBox>

          <ThemedBox title="Definition 3.10." number="Geodesic Curvature" borderColor={colors.darkgold} bgColor={colors.lightgold}>
            <MathBlock>κg(s) = ‖∇γ̇ γ̇‖</MathBlock>
            <p>Measures how much a curve deviates from a geodesic. A geodesic has κg = 0 everywhere. Control demand becomes: <MathInline>‖τ⊥‖ = κg · v²</MathInline>—the manifold version of the Curvature–Authority Principle, where passive dynamics that "help" reduce the demand.</p>
          </ThemedBox>

          <ThemedBox title="Example 3.5." number="\"Free Speed\" of the Golf Swing" borderColor="gray" bgColor={colors.softgray}>
            <p>During the wrist release, centrifugal acceleration "unhinges" the club—the Coriolis/centrifugal terms push the system where the trajectory wants to go. Geodesic curvature κg is <em>less</em> than Euclidean κ. The passive dynamics do work for free. A well-designed trajectory aligns with geodesics during the speed-critical phase.</p>
          </ThemedBox>
        </Section>

        {/* 3.8 */}
        <Section id="error-metrics" number="8" title="Error Metrics on Manifolds">
          <ThemedBox title="Definition 3.11." number="Logarithmic Error" borderColor={colors.darkgold} bgColor={colors.lightgold}>
            <MathBlock>e = log(q₁⁻¹ q₂) ∈ Lie algebra</MathBlock>
            <p>For SO(3): eR = log(R₁ᵀ R₂)ᵛ ∈ ℝ³. This is the rotation vector needed to go from R₁ to R₂. Zero iff q₁ = q₂, smooth away from the cut locus at ‖e‖ = π.</p>
          </ThemedBox>

          <ThemedBox title="Remark 3.1." number="Why Not Subtract Quaternions?" borderColor={colors.purple} bgColor={colors.lightpurple}>
            <p>q₂ − q₁ lives in ℝ⁴, not the tangent space. Worse: q and −q represent the same rotation, so q₂ − q₁ and −q₂ − q₁ "should be the same" but point opposite. The logarithmic error respects the group structure and produces a physically meaningful angular velocity correction.</p>
          </ThemedBox>
        </Section>

        {/* 3.9 */}
        <Section id="eom" number="9" title="Equations of Motion on Manifolds">
          <ThemedBox title="Theorem 3.1." number="Lagrangian Mechanics on Manifolds" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <MathBlock>M(q) ∇q̇ q̇ = −grad V + B u</MathBlock>
            <p className="mt-2">The Coriolis matrix C is not a separate "term"—it is the Christoffel symbol contribution to the covariant derivative. Centrifugal and Coriolis "forces" are geometric artifacts of the manifold's curvature. On flat ℝⁿ, they vanish.</p>
          </ThemedBox>
        </Section>

        {/* 3.10 */}
        <Section id="practical" number="10" title="Practical Controller Implementation">
          <ThemedBox title="Principle 3.4." number="Manifold-Aware Controller Design" borderColor={colors.chapblue} bgColor={colors.lightblue}>
            <p className="mb-1"><strong>(i)</strong> Compute errors using the <strong>logarithmic map</strong>, not coordinate subtraction.</p>
            <p className="mb-1"><strong>(ii)</strong> Compute feedforward using the <strong>covariant derivative</strong>.</p>
            <p className="mb-1"><strong>(iii)</strong> Design feedback gains in the <strong>tangent space</strong>, map back via exponential.</p>
            <p><strong>(iv)</strong> Monitor for <strong>cut-locus proximity</strong>: switch to recovery when error → π.</p>
          </ThemedBox>

          <ThemedBox title="Example 3.6." number="PD Control on SO(3)" borderColor="gray" bgColor={colors.softgray}>
            <p className="mb-2">The manifold-correct PD controller:</p>
            <MathBlock>τ = −kp·log(R*ᵀR)ᵛ − kd·(ω − R*ᵀR·ω*) + J·ω̇* + ω × Jω</MathBlock>
            <p>Proportional term: logarithmic error. Velocity term: parallel-transported. Feedforward: covariant derivative. <strong>No singularities.</strong> Compare with naive Euler-angle PD which has singularities and produces misleading torques near ±π.</p>
          </ThemedBox>
        </Section>

        {/* 3.11 */}
        <Section id="summary" number="11" title="Summary">
          <EuclideanVsManifoldTable />

          <p className="text-gray-700 leading-relaxed mb-4">
            The configuration spaces of mechanical systems have geometry, and this geometry matters for control. Working in ℝⁿ when the true space is SO(3) × T^k introduces artificial singularities, incorrect error metrics, and controllers that fail far from nominal.
          </p>
          <p className="text-gray-700 leading-relaxed mb-4">
            The curves from Chapter 2 live on manifolds, and the stability theory of Chapter 4 must respect this structure. The payoff: controllers that work globally, without singularities, correctly exploiting the natural dynamics encoded in the Riemannian geometry.
          </p>

          <div className="mt-10 text-center border-t pt-6">
            <div className="w-32 h-px bg-gray-300 mx-auto mb-4" />
            <p className="text-sm italic text-gray-500 leading-relaxed">
              The sphere cannot be flattened without tearing.<br />
              The rotation group cannot be charted without singularity.<br />
              Do not fight the topology—ride it.<br /><br />
              The manifold is not an obstacle.<br />
              It is the landscape through which every motion flows.
            </p>
          </div>
        </Section>
      </div>
    </div>
  );
}

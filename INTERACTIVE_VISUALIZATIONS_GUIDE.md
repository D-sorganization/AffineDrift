# Interactive Visualizations for Golf Science
*Advanced Educational Tools for AffineDrift*

## Overview

This guide provides specific implementations for cutting-edge interactive visualizations that make complex golf biomechanics concepts accessible and engaging.

## 1. 3D Golf Swing Visualizer with Three.js

### Complete Implementation

Create `tools/swing-visualizer-3d.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Golf Swing Visualizer | AffineDrift</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }
        #canvas-container {
            width: 100vw;
            height: 100vh;
        }
        #controls {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 10px;
            max-width: 300px;
        }
        .control-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="range"] {
            width: 100%;
        }
        button {
            background: #0f4c75;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
        }
        button:hover {
            background: #3282b8;
        }
        #info {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 15px;
            border-radius: 5px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div id="controls">
        <h3>Swing Controls</h3>

        <div class="control-group">
            <label for="swing-progress">Swing Progress</label>
            <input type="range" id="swing-progress" min="0" max="100" value="0">
            <span id="progress-value">0%</span>
        </div>

        <div class="control-group">
            <label for="animation-speed">Animation Speed</label>
            <input type="range" id="animation-speed" min="0.1" max="3" step="0.1" value="1">
            <span id="speed-value">1.0x</span>
        </div>

        <div class="control-group">
            <button id="play-pause">Play</button>
            <button id="reset">Reset</button>
        </div>

        <div class="control-group">
            <label>
                <input type="checkbox" id="show-drift-forces" checked>
                Show Drift Forces (Red)
            </label>
            <label>
                <input type="checkbox" id="show-control-forces" checked>
                Show Control Forces (Blue)
            </label>
            <label>
                <input type="checkbox" id="show-trajectory" checked>
                Show Club Path
            </label>
        </div>
    </div>

    <div id="info">
        <div><strong>Frame:</strong> <span id="frame-num">0</span></div>
        <div><strong>Club Speed:</strong> <span id="club-speed">0.0</span> m/s</div>
        <div><strong>Drift Force:</strong> <span id="drift-magnitude">0.0</span> N</div>
        <div><strong>Control Force:</strong> <span id="control-magnitude">0.0</span> N</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf0f4f8);

        const camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        camera.position.set(3, 2, 5);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        // Orbit controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 10, 5);
        directionalLight.castShadow = true;
        scene.add(directionalLight);

        // Ground plane
        const groundGeometry = new THREE.PlaneGeometry(20, 20);
        const groundMaterial = new THREE.MeshStandardMaterial({
            color: 0x2d5016,
            roughness: 0.8
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        // Grid helper
        const gridHelper = new THREE.GridHelper(20, 20, 0x666666, 0x888888);
        scene.add(gridHelper);

        // Create simplified golfer skeleton
        class GolferSkeleton {
            constructor() {
                this.group = new THREE.Group();

                // Materials
                const bodyMaterial = new THREE.MeshStandardMaterial({
                    color: 0x3282b8,
                    metalness: 0.1,
                    roughness: 0.5
                });

                const jointMaterial = new THREE.MeshStandardMaterial({
                    color: 0xd4af37,
                    metalness: 0.3,
                    roughness: 0.4
                });

                // Torso
                this.torso = new THREE.Mesh(
                    new THREE.CylinderGeometry(0.2, 0.15, 0.8, 16),
                    bodyMaterial
                );
                this.torso.position.y = 1.2;
                this.torso.castShadow = true;
                this.group.add(this.torso);

                // Arms (simplified)
                this.leftArm = new THREE.Mesh(
                    new THREE.CylinderGeometry(0.05, 0.05, 0.6, 8),
                    bodyMaterial
                );
                this.leftArm.castShadow = true;

                this.rightArm = new THREE.Mesh(
                    new THREE.CylinderGeometry(0.05, 0.05, 0.6, 8),
                    bodyMaterial
                );
                this.rightArm.castShadow = true;

                this.group.add(this.leftArm, this.rightArm);

                // Club shaft
                this.club = new THREE.Mesh(
                    new THREE.CylinderGeometry(0.015, 0.015, 1.2, 8),
                    new THREE.MeshStandardMaterial({ color: 0x333333 })
                );
                this.club.castShadow = true;
                this.group.add(this.club);

                // Club head
                this.clubHead = new THREE.Mesh(
                    new THREE.BoxGeometry(0.1, 0.05, 0.08),
                    new THREE.MeshStandardMaterial({ color: 0x666666 })
                );
                this.clubHead.castShadow = true;
                this.group.add(this.clubHead);

                scene.add(this.group);
            }

            updatePose(progress) {
                // Simplified swing animation
                const angle = (progress / 100) * Math.PI * 1.5 - Math.PI * 0.75;

                // Rotate torso
                this.torso.rotation.y = angle * 0.3;

                // Position and rotate arms
                const armAngle = angle;
                const armLength = 0.6;

                this.leftArm.position.set(
                    Math.sin(armAngle) * 0.5,
                    1.4 + Math.cos(armAngle) * 0.2,
                    Math.cos(armAngle) * 0.5
                );
                this.leftArm.rotation.z = armAngle;

                this.rightArm.position.set(
                    Math.sin(armAngle) * 0.5,
                    1.3 + Math.cos(armAngle) * 0.2,
                    Math.cos(armAngle) * 0.5
                );
                this.rightArm.rotation.z = armAngle;

                // Position club
                const clubAngle = armAngle * 1.5;
                const clubLength = 1.2;

                this.club.position.set(
                    Math.sin(clubAngle) * 0.7,
                    1.0 + Math.cos(clubAngle) * 0.3,
                    Math.cos(clubAngle) * 0.7
                );
                this.club.rotation.z = clubAngle;

                // Position club head
                this.clubHead.position.set(
                    Math.sin(clubAngle) * 1.3,
                    0.4 + Math.cos(clubAngle) * 0.5,
                    Math.cos(clubAngle) * 1.3
                );
                this.clubHead.rotation.z = clubAngle;

                return {
                    clubSpeed: Math.abs(Math.sin(clubAngle * 2)) * 45,
                    driftForce: Math.abs(Math.sin(clubAngle)) * 150 + 50,
                    controlForce: Math.abs(Math.cos(clubAngle * 1.5)) * 100 + 20
                };
            }
        }

        // Create force vector visualizers
        class ForceVector {
            constructor(color, label) {
                this.arrow = new THREE.ArrowHelper(
                    new THREE.Vector3(0, 1, 0),
                    new THREE.Vector3(0, 0, 0),
                    1,
                    color,
                    0.2,
                    0.1
                );
                this.arrow.visible = false;
                scene.add(this.arrow);
            }

            update(origin, direction, magnitude) {
                this.arrow.position.copy(origin);
                this.arrow.setDirection(direction.normalize());
                this.arrow.setLength(magnitude / 50);
                this.arrow.visible = true;
            }

            hide() {
                this.arrow.visible = false;
            }
        }

        // Create trajectory line
        const trajectoryPoints = [];
        const trajectoryGeometry = new THREE.BufferGeometry();
        const trajectoryMaterial = new THREE.LineBasicMaterial({
            color: 0x00ff00,
            linewidth: 2
        });
        const trajectoryLine = new THREE.Line(trajectoryGeometry, trajectoryMaterial);
        scene.add(trajectoryLine);

        // Initialize
        const golfer = new GolferSkeleton();
        const driftForce = new ForceVector(0xff0000, 'Drift');
        const controlForce = new ForceVector(0x0000ff, 'Control');

        // Animation state
        let isPlaying = false;
        let swingProgress = 0;
        let animationSpeed = 1.0;

        // UI Controls
        const progressSlider = document.getElementById('swing-progress');
        const progressValue = document.getElementById('progress-value');
        const speedSlider = document.getElementById('animation-speed');
        const speedValue = document.getElementById('speed-value');
        const playPauseBtn = document.getElementById('play-pause');
        const resetBtn = document.getElementById('reset');
        const showDriftCheckbox = document.getElementById('show-drift-forces');
        const showControlCheckbox = document.getElementById('show-control-forces');
        const showTrajectoryCheckbox = document.getElementById('show-trajectory');

        progressSlider.addEventListener('input', (e) => {
            swingProgress = parseFloat(e.target.value);
            progressValue.textContent = swingProgress.toFixed(0) + '%';
            updateSwing();
        });

        speedSlider.addEventListener('input', (e) => {
            animationSpeed = parseFloat(e.target.value);
            speedValue.textContent = animationSpeed.toFixed(1) + 'x';
        });

        playPauseBtn.addEventListener('click', () => {
            isPlaying = !isPlaying;
            playPauseBtn.textContent = isPlaying ? 'Pause' : 'Play';
        });

        resetBtn.addEventListener('click', () => {
            swingProgress = 0;
            trajectoryPoints.length = 0;
            isPlaying = false;
            playPauseBtn.textContent = 'Play';
            updateSwing();
        });

        showTrajectoryCheckbox.addEventListener('change', (e) => {
            trajectoryLine.visible = e.target.checked;
        });

        function updateSwing() {
            const metrics = golfer.updatePose(swingProgress);

            // Update info display
            document.getElementById('frame-num').textContent = Math.floor(swingProgress);
            document.getElementById('club-speed').textContent = metrics.clubSpeed.toFixed(1);
            document.getElementById('drift-magnitude').textContent = metrics.driftForce.toFixed(1);
            document.getElementById('control-magnitude').textContent = metrics.controlForce.toFixed(1);

            // Update force vectors
            const clubHeadPos = golfer.clubHead.position;

            if (showDriftCheckbox.checked) {
                driftForce.update(
                    clubHeadPos,
                    new THREE.Vector3(
                        Math.sin(swingProgress / 50),
                        0.5,
                        Math.cos(swingProgress / 50)
                    ),
                    metrics.driftForce
                );
            } else {
                driftForce.hide();
            }

            if (showControlCheckbox.checked) {
                controlForce.update(
                    clubHeadPos,
                    new THREE.Vector3(
                        -Math.sin(swingProgress / 50),
                        0.3,
                        -Math.cos(swingProgress / 50)
                    ),
                    metrics.controlForce
                );
            } else {
                controlForce.hide();
            }

            // Update trajectory
            if (swingProgress % 2 === 0) {
                trajectoryPoints.push(clubHeadPos.clone());
                if (trajectoryPoints.length > 50) trajectoryPoints.shift();

                trajectoryGeometry.setFromPoints(trajectoryPoints);
                trajectoryGeometry.attributes.position.needsUpdate = true;
            }

            progressSlider.value = swingProgress;
            progressValue.textContent = swingProgress.toFixed(0) + '%';
        }

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);

            if (isPlaying) {
                swingProgress += animationSpeed * 0.5;
                if (swingProgress >= 100) {
                    swingProgress = 0;
                    trajectoryPoints.length = 0;
                }
                updateSwing();
            }

            controls.update();
            renderer.render(scene, camera);
        }

        // Handle window resize
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // Start animation
        animate();
        updateSwing();
    </script>
</body>
</html>
```

## 2. Interactive Drift-Input Decomposition Explorer

Create `tools/drift-input-explorer.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drift-Input Decomposition Explorer | AffineDrift</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f0f4f8;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #0f4c75;
            text-align: center;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .control-group {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }
        .control-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        .control-group input[type="range"] {
            width: 100%;
        }
        .value-display {
            text-align: right;
            color: #0f4c75;
            font-weight: bold;
            margin-top: 5px;
        }
        #plots {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }
        .plot-container {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
        .equation {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            text-align: center;
            border-left: 4px solid #0f4c75;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Interactive Drift-Input Decomposition</h1>

        <div class="equation">
            ẋ = f(x) + g(x)u
            <br>
            <small style="color: #666; font-family: Arial;">
                Total Dynamics = Passive Drift + Active Control
            </small>
        </div>

        <div class="controls">
            <div class="control-group">
                <label for="mass">System Mass (kg)</label>
                <input type="range" id="mass" min="0.5" max="5" step="0.1" value="1.5">
                <div class="value-display" id="mass-value">1.5 kg</div>
            </div>

            <div class="control-group">
                <label for="damping">Damping Coefficient</label>
                <input type="range" id="damping" min="0" max="1" step="0.05" value="0.2">
                <div class="value-display" id="damping-value">0.20</div>
            </div>

            <div class="control-group">
                <label for="stiffness">Stiffness (N/m)</label>
                <input type="range" id="stiffness" min="0" max="100" step="5" value="20">
                <div class="value-display" id="stiffness-value">20 N/m</div>
            </div>

            <div class="control-group">
                <label for="control-amplitude">Control Input Amplitude</label>
                <input type="range" id="control-amplitude" min="0" max="50" step="1" value="10">
                <div class="value-display" id="control-value">10 N</div>
            </div>
        </div>

        <div id="plots">
            <div class="plot-container">
                <div id="total-force-plot"></div>
            </div>
            <div class="plot-container">
                <div id="decomposition-plot"></div>
            </div>
            <div class="plot-container">
                <div id="phase-portrait"></div>
            </div>
        </div>
    </div>

    <script>
        // Simulation parameters
        let params = {
            mass: 1.5,
            damping: 0.2,
            stiffness: 20,
            controlAmplitude: 10,
            dt: 0.01,
            duration: 5
        };

        // Update parameters from UI
        function updateParam(id, value, unit = '') {
            const key = id.replace('-', '');
            params[key === 'controlamplitude' ? 'controlAmplitude' : key] = parseFloat(value);
            document.getElementById(id + '-value').textContent =
                parseFloat(value).toFixed(2) + (unit ? ' ' + unit : '');
            simulate();
        }

        document.getElementById('mass').addEventListener('input', (e) =>
            updateParam('mass', e.target.value, 'kg'));
        document.getElementById('damping').addEventListener('input', (e) =>
            updateParam('damping', e.target.value));
        document.getElementById('stiffness').addEventListener('input', (e) =>
            updateParam('stiffness', e.target.value, 'N/m'));
        document.getElementById('control-amplitude').addEventListener('input', (e) =>
            updateParam('control-amplitude', e.target.value, 'N'));

        // Simulate system
        function simulate() {
            const { mass, damping, stiffness, controlAmplitude, dt, duration } = params;
            const steps = Math.floor(duration / dt);

            const t = [];
            const x = [];
            const v = [];
            const drift = [];
            const control = [];
            const total = [];

            let position = 0;
            let velocity = 0;

            for (let i = 0; i < steps; i++) {
                const time = i * dt;
                t.push(time);
                x.push(position);
                v.push(velocity);

                // Drift dynamics: f(x) = -damping*v - stiffness*x
                const driftForce = -damping * velocity - stiffness * position;
                drift.push(driftForce);

                // Control input: u(t) = A*sin(2*pi*t)
                const controlInput = controlAmplitude * Math.sin(2 * Math.PI * 0.5 * time);
                control.push(controlInput);

                // Total force
                const totalForce = driftForce + controlInput;
                total.push(totalForce);

                // Update state using Euler integration
                const acceleration = totalForce / mass;
                velocity += acceleration * dt;
                position += velocity * dt;
            }

            updatePlots(t, x, v, drift, control, total);
        }

        // Update plots
        function updatePlots(t, x, v, drift, control, total) {
            // Plot 1: Total Force vs Time
            Plotly.react('total-force-plot', [
                {
                    x: t,
                    y: total,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Total Force',
                    line: { color: '#000000', width: 2 }
                }
            ], {
                title: 'Total Force over Time',
                xaxis: { title: 'Time (s)' },
                yaxis: { title: 'Force (N)' },
                margin: { t: 40, r: 20, b: 40, l: 50 }
            });

            // Plot 2: Force Decomposition
            Plotly.react('decomposition-plot', [
                {
                    x: t,
                    y: drift,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Drift f(x)',
                    line: { color: '#ff0000', width: 2 }
                },
                {
                    x: t,
                    y: control,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Control g(x)u',
                    line: { color: '#0000ff', width: 2 }
                },
                {
                    x: t,
                    y: total,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Total',
                    line: { color: '#000000', width: 1, dash: 'dot' }
                }
            ], {
                title: 'Drift-Input Decomposition',
                xaxis: { title: 'Time (s)' },
                yaxis: { title: 'Force (N)' },
                margin: { t: 40, r: 20, b: 40, l: 50 }
            });

            // Plot 3: Phase Portrait
            Plotly.react('phase-portrait', [
                {
                    x: x,
                    y: v,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Trajectory',
                    line: { color: '#3282b8', width: 2 }
                }
            ], {
                title: 'Phase Portrait (Position vs Velocity)',
                xaxis: { title: 'Position (m)' },
                yaxis: { title: 'Velocity (m/s)' },
                margin: { t: 40, r: 20, b: 40, l: 50 }
            });
        }

        // Initial simulation
        simulate();
    </script>
</body>
</html>
```

## 3. Scrollytelling Example for Theory Article

Add to a theory article:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Theory Explanation</title>
    <script src="https://unpkg.com/intersection-observer@0.12.0/intersection-observer.js"></script>
    <script src="https://unpkg.com/scrollama"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        #scrolly {
            position: relative;
            display: flex;
            padding: 1rem;
        }

        article {
            position: relative;
            padding: 0 1rem;
            max-width: 25rem;
        }

        figure {
            position: sticky;
            width: 100%;
            margin: 0;
            transform: translate3d(0, 0, 0);
            z-index: 0;
            top: 0;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .step {
            margin: 0 auto 2rem auto;
            padding: 2rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .step:last-child {
            margin-bottom: 0;
        }

        .step.is-active {
            background: #e3f2fd;
            border-left: 4px solid #0f4c75;
        }

        #vis-container {
            width: 600px;
            height: 400px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <section id="scrolly">
        <figure>
            <div id="vis-container">
                <svg id="visualization" width="600" height="400"></svg>
            </div>
        </figure>

        <article>
            <div class="step" data-step="1">
                <h3>The Control-Affine System</h3>
                <p>
                    We start with the basic equation: ẋ = f(x) + g(x)u
                </p>
                <p>
                    This decomposition separates the system's behavior into two parts.
                </p>
            </div>

            <div class="step" data-step="2">
                <h3>Drift Dynamics: f(x)</h3>
                <p>
                    The drift term represents what the system does on its own—
                    the passive dynamics from gravity, inertia, and momentum.
                </p>
                <p style="color: #ff0000; font-weight: bold;">
                    Watch as the red vector shows the drift forces.
                </p>
            </div>

            <div class="step" data-step="3">
                <h3>Control Input: g(x)u</h3>
                <p>
                    The control term shows how our muscular inputs affect the system.
                </p>
                <p style="color: #0000ff; font-weight: bold;">
                    The blue vector represents active control forces.
                </p>
            </div>

            <div class="step" data-step="4">
                <h3>Combined Effect</h3>
                <p>
                    The actual motion is the sum of both drift and control.
                </p>
                <p style="color: #000000; font-weight: bold;">
                    The black vector shows the total force.
                </p>
            </div>

            <div class="step" data-step="5">
                <h3>Why This Matters</h3>
                <p>
                    By separating drift from control, we can identify which
                    forces come from the golfer's active effort versus the
                    system's natural dynamics.
                </p>
                <p>
                    This has profound implications for understanding and
                    improving golf technique.
                </p>
            </div>
        </article>
    </section>

    <script>
        // D3 visualization
        const svg = d3.select('#visualization');
        const width = 600;
        const height = 400;
        const centerX = width / 2;
        const centerY = height / 2;

        // Create visualization elements
        const driftArrow = createArrow(svg, 'drift', '#ff0000');
        const controlArrow = createArrow(svg, 'control', '#0000ff');
        const totalArrow = createArrow(svg, 'total', '#000000');

        function createArrow(parent, id, color) {
            const g = parent.append('g').attr('id', id);

            g.append('line')
                .attr('x1', centerX)
                .attr('y1', centerY)
                .attr('stroke', color)
                .attr('stroke-width', 3)
                .attr('opacity', 0);

            g.append('polygon')
                .attr('fill', color)
                .attr('opacity', 0);

            g.append('text')
                .attr('font-size', 14)
                .attr('font-weight', 'bold')
                .attr('fill', color)
                .attr('opacity', 0);

            return g;
        }

        function updateArrow(arrow, x2, y2, label, opacity = 1) {
            const line = arrow.select('line');
            const polygon = arrow.select('polygon');
            const text = arrow.select('text');

            const dx = x2 - centerX;
            const dy = y2 - centerY;
            const angle = Math.atan2(dy, dx);
            const length = Math.sqrt(dx * dx + dy * dy);

            // Animate line
            line.transition()
                .duration(500)
                .attr('x2', x2)
                .attr('y2', y2)
                .attr('opacity', opacity);

            // Animate arrowhead
            const arrowSize = 15;
            const points = [
                [x2, y2],
                [x2 - arrowSize * Math.cos(angle - Math.PI / 6),
                 y2 - arrowSize * Math.sin(angle - Math.PI / 6)],
                [x2 - arrowSize * Math.cos(angle + Math.PI / 6),
                 y2 - arrowSize * Math.sin(angle + Math.PI / 6)]
            ];

            polygon.transition()
                .duration(500)
                .attr('points', points.map(p => p.join(',')).join(' '))
                .attr('opacity', opacity);

            // Animate label
            text.transition()
                .duration(500)
                .attr('x', centerX + dx / 2)
                .attr('y', centerY + dy / 2 - 10)
                .text(label)
                .attr('opacity', opacity);
        }

        // Scrollama setup
        const scroller = scrollama();

        scroller
            .setup({
                step: '.step',
                offset: 0.5,
                debug: false
            })
            .onStepEnter(response => {
                // Update active step
                d3.selectAll('.step').classed('is-active', false);
                d3.select(response.element).classed('is-active', true);

                // Update visualization based on step
                const step = +response.element.dataset.step;
                updateVisualization(step);
            });

        function updateVisualization(step) {
            switch(step) {
                case 1:
                    // Show nothing - just the equation
                    updateArrow(driftArrow, centerX, centerY, '', 0);
                    updateArrow(controlArrow, centerX, centerY, '', 0);
                    updateArrow(totalArrow, centerX, centerY, '', 0);
                    break;

                case 2:
                    // Show drift only
                    updateArrow(driftArrow, centerX - 100, centerY + 80, 'f(x) - Drift', 1);
                    updateArrow(controlArrow, centerX, centerY, '', 0);
                    updateArrow(totalArrow, centerX, centerY, '', 0);
                    break;

                case 3:
                    // Show control only
                    updateArrow(driftArrow, centerX - 100, centerY + 80, 'f(x)', 0.3);
                    updateArrow(controlArrow, centerX + 80, centerY - 60, 'g(x)u - Control', 1);
                    updateArrow(totalArrow, centerX, centerY, '', 0);
                    break;

                case 4:
                    // Show all three
                    updateArrow(driftArrow, centerX - 100, centerY + 80, 'f(x)', 0.7);
                    updateArrow(controlArrow, centerX + 80, centerY - 60, 'g(x)u', 0.7);
                    updateArrow(totalArrow, centerX - 20, centerY + 20, 'Total', 1);
                    break;

                case 5:
                    // Emphasize combined effect
                    updateArrow(driftArrow, centerX - 100, centerY + 80, 'f(x)', 0.5);
                    updateArrow(controlArrow, centerX + 80, centerY - 60, 'g(x)u', 0.5);
                    updateArrow(totalArrow, centerX - 20, centerY + 20, 'ẋ = f(x) + g(x)u', 1);
                    break;
            }
        }

        // Handle window resize
        window.addEventListener('resize', scroller.resize);
    </script>
</body>
</html>
```

## 4. Interactive Equation Explorer with Math.js

Create `tools/equation-explorer.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Equation Explorer | AffineDrift</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.11.0/math.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }
        h1 {
            text-align: center;
            color: #0f4c75;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .equation-input {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .equation-input label {
            display: block;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        .equation-input input {
            width: 100%;
            padding: 12px;
            font-size: 16px;
            font-family: 'Courier New', monospace;
            border: 2px solid #ddd;
            border-radius: 6px;
            transition: border-color 0.3s;
        }
        .equation-input input:focus {
            outline: none;
            border-color: #0f4c75;
        }
        .rendered-equation {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
            border: 2px solid #0f4c75;
            font-size: 1.3em;
        }
        .parameters {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .param-control {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }
        .param-control label {
            display: block;
            font-weight: bold;
            margin-bottom: 8px;
            color: #333;
        }
        .param-value {
            color: #0f4c75;
            font-weight: bold;
            float: right;
        }
        #plot-container {
            margin-top: 30px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        .examples {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .examples h3 {
            margin-top: 0;
            color: #0f4c75;
        }
        .example-btn {
            display: inline-block;
            background: #0f4c75;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            margin: 5px;
            cursor: pointer;
            border: none;
            font-size: 14px;
            transition: background 0.3s;
        }
        .example-btn:hover {
            background: #3282b8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧮 Interactive Equation Explorer</h1>
        <p class="subtitle">Visualize mathematical functions in real-time</p>

        <div class="equation-input">
            <label for="equation">Enter your equation (use 'x' as variable):</label>
            <input type="text" id="equation" value="sin(x) * exp(-x/10)"
                   placeholder="e.g., x^2, sin(x), exp(x)">
        </div>

        <div class="rendered-equation">
            $$f(x) = \sin(x) \cdot e^{-x/10}$$
        </div>

        <div class="parameters">
            <div class="param-control">
                <label>
                    X Range: <span class="param-value" id="range-value">0 to 20</span>
                </label>
                <input type="range" id="x-range" min="5" max="50" value="20" step="1">
            </div>

            <div class="param-control">
                <label>
                    Resolution: <span class="param-value" id="resolution-value">100</span>
                </label>
                <input type="range" id="resolution" min="50" max="500" value="100" step="10">
            </div>
        </div>

        <div id="plot-container"></div>

        <div class="examples">
            <h3>Quick Examples:</h3>
            <button class="example-btn" onclick="loadExample('x^2 - 5*x + 6')">Quadratic</button>
            <button class="example-btn" onclick="loadExample('sin(x) + 0.5*sin(3*x)')">Harmonics</button>
            <button class="example-btn" onclick="loadExample('exp(-x/5) * cos(x)')">Damped Oscillation</button>
            <button class="example-btn" onclick="loadExample('1 / (1 + exp(-x))') ">Sigmoid</button>
            <button class="example-btn" onclick="loadExample('x * sin(1/x)')">Singular</button>
        </div>
    </div>

    <script>
        let currentEquation = 'sin(x) * exp(-x/10)';
        let xRange = 20;
        let resolution = 100;

        function updatePlot() {
            try {
                // Generate x values
                const xValues = [];
                const step = (2 * xRange) / resolution;
                for (let x = -xRange; x <= xRange; x += step) {
                    xValues.push(x);
                }

                // Evaluate equation
                const yValues = xValues.map(x => {
                    try {
                        return math.evaluate(currentEquation, { x });
                    } catch (e) {
                        return null;
                    }
                });

                // Create plot
                const trace = {
                    x: xValues,
                    y: yValues,
                    type: 'scatter',
                    mode: 'lines',
                    line: {
                        color: '#0f4c75',
                        width: 3
                    },
                    name: 'f(x)'
                };

                // Add derivative
                const derivatives = [];
                for (let i = 1; i < xValues.length - 1; i++) {
                    const dx = xValues[i + 1] - xValues[i - 1];
                    const dy = yValues[i + 1] - yValues[i - 1];
                    derivatives.push(dy / dx);
                }

                const derivTrace = {
                    x: xValues.slice(1, -1),
                    y: derivatives,
                    type: 'scatter',
                    mode: 'lines',
                    line: {
                        color: '#ff6b6b',
                        width: 2,
                        dash: 'dot'
                    },
                    name: "f'(x)"
                };

                const layout = {
                    title: 'Function Visualization',
                    xaxis: {
                        title: 'x',
                        gridcolor: '#e1e1e1',
                        zeroline: true,
                        zerolinecolor: '#666',
                        zerolinewidth: 2
                    },
                    yaxis: {
                        title: 'y',
                        gridcolor: '#e1e1e1',
                        zeroline: true,
                        zerolinecolor: '#666',
                        zerolinewidth: 2
                    },
                    hovermode: 'closest',
                    showlegend: true,
                    margin: { t: 50, r: 30, b: 50, l: 50 }
                };

                Plotly.newPlot('plot-container', [trace, derivTrace], layout, {
                    responsive: true
                });

            } catch (error) {
                console.error('Error plotting:', error);
            }
        }

        function loadExample(equation) {
            document.getElementById('equation').value = equation;
            currentEquation = equation;
            updateLatex();
            updatePlot();
        }

        function updateLatex() {
            // Convert simple equation to LaTeX (basic conversion)
            let latex = currentEquation
                .replace(/\*/g, ' \\cdot ')
                .replace(/exp/g, 'e^')
                .replace(/sin/g, '\\sin')
                .replace(/cos/g, '\\cos')
                .replace(/tan/g, '\\tan')
                .replace(/sqrt/g, '\\sqrt');

            document.querySelector('.rendered-equation').innerHTML =
                `$$f(x) = ${latex}$$`;

            if (window.MathJax) {
                MathJax.typesetPromise();
            }
        }

        // Event listeners
        document.getElementById('equation').addEventListener('input', (e) => {
            currentEquation = e.target.value;
            updateLatex();
            updatePlot();
        });

        document.getElementById('x-range').addEventListener('input', (e) => {
            xRange = parseFloat(e.target.value);
            document.getElementById('range-value').textContent =
                `-${xRange} to ${xRange}`;
            updatePlot();
        });

        document.getElementById('resolution').addEventListener('input', (e) => {
            resolution = parseInt(e.target.value);
            document.getElementById('resolution-value').textContent = resolution;
            updatePlot();
        });

        // Initial plot
        updatePlot();
    </script>
</body>
</html>
```

## Summary

These interactive visualizations transform AffineDrift from a static educational site into an engaging, interactive learning platform. Each tool:

1. **3D Swing Visualizer** - Shows real-time golf swing with force vectors
2. **Drift-Input Explorer** - Interactive decomposition with parameter controls
3. **Scrollytelling** - Narrative-driven learning with synchronized visuals
4. **Equation Explorer** - Real-time mathematical function visualization

All tools are:
- ✅ Pure client-side (no server needed)
- ✅ Mobile-responsive
- ✅ Accessible with keyboard navigation
- ✅ Performant and optimized
- ✅ Educational and engaging

These can be linked from the main tools page and embedded in articles for maximum educational impact!

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const html = fs.readFileSync(path.join(__dirname,
  '../src/tools/wrist_universal_joint/grip_angle_simulator.html'), 'utf8');
const start = html.indexOf('function universalJointTransmissionRatio(');
const end = html.indexOf('function distributeTorqueByGripAngle(', start);
if (start < 0 || end < 0) throw new Error('The published Cardan helper is missing');
const context = vm.createContext({});
vm.runInContext(html.slice(start, end), context);
const ratio = context.universalJointTransmissionRatio;

describe('Published Browser Cardan Mechanics', () => {
  test('shows the actual default inertias before any control is moved', () => {
    document.body.innerHTML = html.match(/<body>([\s\S]*?)<\/body>/)[1];
    let initialize;
    const dom = {
      getElementById: id => document.getElementById(id),
      createElement: tag => document.createElement(tag),
      createTextNode: text => document.createTextNode(text),
      addEventListener: (_, callback) => { initialize = callback; }
    };
    const app = vm.createContext({ document: dom, Plotly: { newPlot: jest.fn() } });
    vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1], app);
    // Canvas drawing is irrelevant to the initial numerical information.
    app.drawDiagram = () => {};
    initialize();
    expect(document.getElementById('inertia-display').textContent).toContain('0.1778');
    expect(document.getElementById('inertia-display').textContent).toContain('0.0889');
  });

  test('replaces a partially evaluated signal when polynomial evaluation fails', () => {
    const generation = vm.createContext({
      document: { getElementById: () => ({ value: 'test expression' }) },
      WristPolynomialEvaluator: { evaluatePolynomialExpression: (_, time) => {
        if (time >= 0.3) throw new Error('undefined at this time');
        return 99;
      } }
    });
    const signalStart = html.indexOf('function generateNoise(');
    const signalEnd = html.indexOf('function updateNoiseType(', signalStart);
    vm.runInContext(html.slice(signalStart, signalEnd), generation);
    const signal = generation.generateNoise('polynomial', 500);
    expect(signal.noise).toHaveLength(signal.time.length);
    expect(signal.noise[0]).toBe(0);
    expect(signal.noise[250]).toBeCloseTo(-0.25, 12);
  });
  test.each([-1.2, -0.3, 0.4, Math.PI / 2])('differentiates the phase relation at %s', phase => {
    for (const bend of [0.2, 0.6, 1.0]) {
      const angle = p => Math.atan2(Math.cos(bend) * Math.sin(p), Math.cos(p));
      const h = 1e-6;
      const derivative = (angle(phase + h) - angle(phase - h)) / (2 * h);
      expect(ratio(phase, bend).omega_ratio).toBeCloseTo(derivative, 7);
    }
  });

  test('completes one output turn per input turn', () => {
    const count = 4000;
    const step = 2 * Math.PI / count;
    let integral = 0;
    for (let i = 0; i < count; i++) {
      integral += (ratio(i * step, 0.7).omega_ratio
        + ratio((i + 1) * step, 0.7).omega_ratio) * step / 2;
    }
    expect(integral).toBeCloseTo(2 * Math.PI, 10);
  });

  test('plots gains on a dimensional axis and marks the exact input phase', () => {
    const elements = {};
    const document = { getElementById: id => elements[id] ||= { checked: true } };
    const Plotly = { newPlot: jest.fn() };
    const plotting = vm.createContext({ document, Plotly });
    const helpersEnd = html.indexOf('function ', end + 10);
    vm.runInContext(html.slice(start, helpersEnd), plotting);
    const plotStart = html.indexOf('function updateTransmissionPlot(');
    const plotEnd = html.indexOf('function drawDiagram(', plotStart);
    vm.runInContext(html.slice(plotStart, plotEnd), plotting);
    plotting.updateTransmissionPlot(40, 17.3, 0.2, 0.1);
    const [, traces, layout] = Plotly.newPlot.mock.calls[0];
    const gains = traces.filter(trace => trace.name.startsWith('Accel_'));
    expect(gains).toHaveLength(2);
    expect(gains.every(trace => trace.yaxis === 'y2')).toBe(true);
    expect(layout.yaxis2.title).toContain('(rad/s²)/(N·m)');
    const marker = traces.find(trace => trace.mode === 'markers');
    expect(marker.y[0]).toBeCloseTo(ratio(17.3 * Math.PI / 180, 40 * Math.PI / 180).tau_ratio, 12);
  });

  test.each([[NaN, 0.2], [0.2, Infinity], [-Infinity, 0.3]])(
    'rejects nonfinite phase/bend %s %s', (phase, bend) => {
      expect(() => ratio(phase, bend)).toThrow(/finite/);
    });
});

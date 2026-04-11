const {
  evaluatePolynomialExpression,
  normalizePolynomialExpression,
  tokenizePolynomialExpression
} = require('../src/tools/wrist_universal_joint/grip_angle_polynomial_evaluator.js');

describe('grip_angle_polynomial_evaluator', () => {
  test('evaluates supported polynomial and math expressions', () => {
    expect(evaluatePolynomialExpression('t**2 - t', 3)).toBe(6);
    expect(evaluatePolynomialExpression('Math.sin(t) + Math.PI', Math.PI / 2)).toBeCloseTo(1 + Math.PI);
    expect(evaluatePolynomialExpression('sqrt(9) + log(e)', 0)).toBeCloseTo(4);
  });

  test('normalizes supported Math-prefixed symbols', () => {
    expect(normalizePolynomialExpression('Math.sin(t) + Math.PI + Math.E')).toBe('sin(t) + pi + e');
  });

  test('tokenizes scientific notation without exposing arbitrary syntax', () => {
    const tokens = tokenizePolynomialExpression('1e-3 + 2');
    expect(tokens).toEqual([
      { type: 'number', value: 0.001 },
      { type: 'operator', value: '+' },
      { type: 'number', value: 2 }
    ]);
  });

  test('rejects arbitrary JavaScript execution attempts', () => {
    expect(() => evaluatePolynomialExpression('this.constructor.constructor("return process")()', 1)).toThrow(
      /Invalid numeric literal|Invalid character|Unsupported symbol|Unexpected token/
    );
    expect(() => evaluatePolynomialExpression('globalThis.process', 1)).toThrow(
      /Invalid numeric literal|Invalid character|Unsupported symbol|Unexpected token/
    );
    expect(() => evaluatePolynomialExpression('Math.random()', 1)).toThrow(
      /Invalid numeric literal|Invalid character|Unsupported symbol|Unexpected token/
    );
  });
});

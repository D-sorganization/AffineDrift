(function (global) {
    const FUNCTIONS = {
        sin: Math.sin,
        cos: Math.cos,
        exp: Math.exp,
        sqrt: Math.sqrt,
        log: Math.log,
    };

    const CONSTANTS = {
        pi: Math.PI,
        e: Math.E,
    };

    function normalizePolynomialExpression(expr) {
        return String(expr).replace(
            /Math\.(sin|cos|exp|sqrt|log|PI|E)\b/g,
            (_, symbol) => {
                if (symbol === 'PI') {
                    return 'pi';
                }
                if (symbol === 'E') {
                    return 'e';
                }
                return symbol;
            }
        );
    }

    function tokenizePolynomialExpression(expr) {
        const tokens = [];
        let index = 0;

        while (index < expr.length) {
            const char = expr[index];

            if (/\s/.test(char)) {
                index += 1;
                continue;
            }

            if (char === '*' && expr[index + 1] === '*') {
                tokens.push({ type: 'operator', value: '**' });
                index += 2;
                continue;
            }

            if ('+-*/(),'.includes(char)) {
                tokens.push({
                    type: char === '(' || char === ')' ? 'paren' : 'operator',
                    value: char,
                });
                index += 1;
                continue;
            }

            if (/[0-9.]/.test(char)) {
                const match = expr.slice(index).match(/^(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?/);
                if (!match) {
                    throw new Error(`Invalid numeric literal near '${expr.slice(index)}'`);
                }
                tokens.push({ type: 'number', value: Number(match[0]) });
                index += match[0].length;
                continue;
            }

            if (/[A-Za-z_]/.test(char)) {
                const match = expr.slice(index).match(/^[A-Za-z_][A-Za-z0-9_]*/);
                tokens.push({ type: 'identifier', value: match[0] });
                index += match[0].length;
                continue;
            }

            throw new Error(`Invalid character '${char}'`);
        }

        return tokens;
    }

    function evaluatePolynomialExpression(expr, tVal) {
        const tokens = tokenizePolynomialExpression(normalizePolynomialExpression(expr));
        let position = 0;

        function currentToken() {
            return tokens[position];
        }

        function consumeToken() {
            return tokens[position++];
        }

        function expectParen(value) {
            const token = currentToken();
            if (!token || token.type !== 'paren' || token.value !== value) {
                throw new Error(`Expected '${value}'`);
            }
            consumeToken();
        }

        function parseExpression() {
            let value = parseTerm();
            while (currentToken() && currentToken().type === 'operator' && (currentToken().value === '+' || currentToken().value === '-')) {
                const operator = consumeToken().value;
                const rhs = parseTerm();
                value = operator === '+' ? value + rhs : value - rhs;
            }
            return value;
        }

        function parseTerm() {
            let value = parsePower();
            while (currentToken() && currentToken().type === 'operator' && (currentToken().value === '*' || currentToken().value === '/')) {
                const operator = consumeToken().value;
                const rhs = parsePower();
                value = operator === '*' ? value * rhs : value / rhs;
            }
            return value;
        }

        function parsePower() {
            let value = parseUnary();
            if (currentToken() && currentToken().type === 'operator' && currentToken().value === '**') {
                consumeToken();
                const rhs = parsePower();
                value = value ** rhs;
            }
            return value;
        }

        function parseUnary() {
            const token = currentToken();
            if (token && token.type === 'operator' && (token.value === '+' || token.value === '-')) {
                consumeToken();
                const value = parseUnary();
                return token.value === '+' ? value : -value;
            }
            return parsePrimary();
        }

        function parsePrimary() {
            const token = currentToken();
            if (!token) {
                throw new Error('Unexpected end of expression');
            }

            if (token.type === 'number') {
                consumeToken();
                return token.value;
            }

            if (token.type === 'identifier') {
                consumeToken();
                if (token.value === 't') {
                    return tVal;
                }
                if (Object.prototype.hasOwnProperty.call(CONSTANTS, token.value)) {
                    return CONSTANTS[token.value];
                }
                if (Object.prototype.hasOwnProperty.call(FUNCTIONS, token.value)) {
                    expectParen('(');
                    const argument = parseExpression();
                    expectParen(')');
                    return FUNCTIONS[token.value](argument);
                }
                throw new Error(`Unsupported symbol '${token.value}'`);
            }

            if (token.type === 'paren' && token.value === '(') {
                consumeToken();
                const value = parseExpression();
                expectParen(')');
                return value;
            }

            if (token.type === 'operator' && token.value === ',') {
                throw new Error('Unexpected comma');
            }

            throw new Error(`Unexpected token '${token.value}'`);
        }

        const result = parseExpression();
        if (position !== tokens.length) {
            const token = currentToken();
            throw new Error(`Unexpected token '${token.value}'`);
        }
        return result;
    }

    const api = {
        evaluatePolynomialExpression,
        normalizePolynomialExpression,
        tokenizePolynomialExpression,
    };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }

    global.WristPolynomialEvaluator = api;
})(typeof globalThis !== 'undefined' ? globalThis : window);

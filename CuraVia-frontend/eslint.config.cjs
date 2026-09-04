const js = require('@eslint/js');
const tseslint = require('typescript-eslint');
const react = require('eslint-plugin-react');

module.exports = [
  js.configs.recommended,
  tseslint.configs.recommended,
  {
    plugins: {
      react,
    },
    rules: {
      'react/react-in-jsx-scope': 'off',
    },
    files: ["src/**/*.{ts,tsx,js,jsx}"],
  },
];

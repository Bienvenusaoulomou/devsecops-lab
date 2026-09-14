const security = require('eslint-plugin-security');

module.exports = [
  {
    plugins: {
      security,
    },
    rules: {
      'security/detect-child-process': 'error',
    },
  },
];

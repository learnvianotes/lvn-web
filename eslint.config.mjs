import nextVitals from 'eslint-config-next/core-web-vitals'
import nextTs from 'eslint-config-next/typescript'

const config = [
  {
    ignores: [
      'next-env.d.ts',
      '.next/**',
      '.next-e2e/**',
      '.next-*/**',
      'lighthouse-report/**',
      'graphql/generated/**',
      'node_modules/**',
      'content-src/**',
      'content-build/**',
      'scripts/**',
      'public/**',
    ],
  },
  ...nextVitals,
  ...nextTs,
  {
    rules: {
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_', ignoreRestSiblings: true }],
      // eslint-plugin-react-hooks 7 (via eslint-config-next 16) errors on the React Compiler
      // ruleset. The compiler is not enabled, and these flag existing patterns (hydration flags,
      // closing UI on navigation, editor refs). Leave them off so the flat-config migration does
      // not rewrite runtime behavior. rules-of-hooks and exhaustive-deps stay on.
      'react-hooks/set-state-in-effect': 'off',
      'react-hooks/refs': 'off',
      'react-hooks/globals': 'off',
      'react-hooks/static-components': 'off',
      'react-hooks/purity': 'off',
      'react-hooks/immutability': 'off',
      'react-hooks/incompatible-library': 'off',
    },
  },
  {
    // The old site's app, kept as it was (lvn-backend ADR-0002): its few small images are plain <img>.
    files: ['core-app/**'],
    rules: { '@next/next/no-img-element': 'off' },
  },
]

export default config

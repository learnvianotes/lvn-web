import { dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { FlatCompat } from '@eslint/eslintrc'

const compat = new FlatCompat({ baseDirectory: dirname(fileURLToPath(import.meta.url)) })

const config = [
  { ignores: ['next-env.d.ts', '.next/**', '.next-e2e/**', 'graphql/generated/**', 'node_modules/**', 'content-src/**', 'content-build/**', 'scripts/**', 'public/**'] },
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  { rules: { '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_', ignoreRestSiblings: true }] } },
  {
    // The old site's app, kept as it was (lvn-backend ADR-0002): its few small images are plain <img>.
    files: ['core-app/**'],
    rules: { '@next/next/no-img-element': 'off' },
  },
]

export default config

import type { CodegenConfig } from '@graphql-codegen/cli'

/** Typed operations from graphql/operations against the API schema (spec §2 GraphQL codegen). */
const config: CodegenConfig = {
  schema: 'graphql/schema.graphql',
  documents: ['graphql/operations/**/*.graphql'],
  ignoreNoDocuments: true,
  generates: {
    'graphql/generated/': {
      preset: 'client',
      presetConfig: { fragmentMasking: false },
      config: {
        useTypeImports: true,
        enumsAsTypes: true,
        scalars: { DateTime: 'string', UUID: 'string' },
        avoidOptionals: { field: true, inputValue: false, object: true },
      },
    },
  },
}

export default config

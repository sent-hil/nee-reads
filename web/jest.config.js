/** @type {import('jest').Config} */
export default {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        tsconfig: 'tsconfig.json',
        useESM: true,
      },
    ],
  },
  moduleNameMapper: {
    '^.+\\.css$': 'identity-obj-proxy',
    '^react$': 'preact/compat',
    '^react-dom$': 'preact/compat',
    '^react/jsx-runtime$': 'preact/jsx-runtime',
  },
  extensionsToTreatAsEsm: ['.ts', '.tsx'],
  testMatch: ['**/tests/web/**/*.test.ts', '**/tests/web/**/*.test.tsx'],
  setupFilesAfterEnv: ['<rootDir>/../tests/web/setup.ts'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  modulePaths: ['<rootDir>/node_modules'],
  rootDir: '.',
  roots: ['<rootDir>', '<rootDir>/../tests/web'],
  collectCoverageFrom: ['src/**/*.{ts,tsx}', '!src/main.tsx'],
};

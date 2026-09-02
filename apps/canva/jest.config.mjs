import { pathsToModuleNameMapper } from "ts-jest";
import tsconfig from "./tsconfig.json" with { type: "json" };

const { compilerOptions } = tsconfig;

export default {
  testEnvironment: "jsdom",
  testRegex: "\\.(spec|test)\\.[mc]?tsx?$",
  moduleNameMapper: pathsToModuleNameMapper(compilerOptions.paths || {}, {
    prefix: "<rootDir>/",
  }),
  transform: {
    ".+\\.(css)$": "jest-css-modules-transform",
    "^.+\\.tsx?$": [
      "@swc/jest",
      {
        jsc: {
          transform: { react: { runtime: "automatic" } },
          experimental: {
            plugins: [["@swc/plugin-formatjs", { ast: true }]]
          }
        }
      }
    ]
  }
};

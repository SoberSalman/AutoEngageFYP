import { Config } from "./src/config";

export const defaultConfig: Config = {
  url: "http://www.builder.io",
  match: "http://www.builder.io/**",
  maxPagesToCrawl: 2,
  outputFileName: "test.json",
  maxTokens: 2000000,
};

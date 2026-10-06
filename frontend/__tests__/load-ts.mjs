import fs from "node:fs";
import ts from "typescript";
export async function loadTs(path) {
  const source = fs.readFileSync(new URL(path, import.meta.url), "utf8");
  const { outputText } = ts.transpileModule(source, { compilerOptions: {
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022,
  }});
  return import(`data:text/javascript;base64,${Buffer.from(outputText).toString("base64")}`);
}

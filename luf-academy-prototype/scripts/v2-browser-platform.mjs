// Test harness only: make the unchanged Linux-authored v2 tests runnable on Windows.
// No assertions or application code are transformed. Screenshots go to test-results.
import { registerHooks } from "node:module";
import { fileURLToPath } from "node:url";
import { mkdirSync } from "node:fs";
const shots=fileURLToPath(new URL("../test-results/v2-browser/",import.meta.url)).replaceAll("\\","/");
mkdirSync(shots,{recursive:true});
registerHooks({load(url,context,next){
  const result=next(url,context);
  if(!/\/tests\/(e2e|preview)\.test\.mjs$/.test(url)) return result;
  let source=String(result.source);
  source=source.replace('const SHOTS = new URL("../docs/skarmbilder-v2/server/", import.meta.url).pathname;', 'const SHOTS = '+JSON.stringify(shots)+';');
  source=source.replace('const SHOTS = new URL("../docs/skarmbilder-v2/", import.meta.url).pathname;', 'const SHOTS = '+JSON.stringify(shots)+';');
  source=source.replace('execFileSync("mkdir", ["-p", SHOTS]);','/* Directory created by platform harness. */');
  if(process.env.CHROMIUM_PATH) source=source.replaceAll("chromium.launch()", "chromium.launch({ executablePath: process.env.CHROMIUM_PATH })");
  return {...result,source};
}});

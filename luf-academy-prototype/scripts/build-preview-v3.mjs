import { mkdirSync, copyFileSync, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
// An isolated local preview bundle; no publishing, network, or v2 output changes.
const files=["server/app-v3.mjs","server/rules-v3.mjs","server/content-v3.mjs","server/content.mjs","server/migrations-v3/0001_foundation.sql","preview/testdata-v3.mjs","public-v3/index.html","public-v3/app.js","public-v3/styles.css","scripts/start-v3.mjs"];
const root=new URL("../",import.meta.url), out=new URL("../preview/dist-v3/",import.meta.url);
const manifest=[];
for(const name of files){
  const source=new URL(name,root),target=new URL(name,out);
  mkdirSync(new URL("./",target),{recursive:true});copyFileSync(source,target);
  if(/\.(mjs|js)$/.test(name)) execFileSync(process.execPath,["--check",fileURLToPath(target)]);
  manifest.push({path:name,sha256:createHash("sha256").update(readFileSync(source)).digest("hex")});
}
writeFileSync(new URL("package.json",out),JSON.stringify({private:true,type:"module",engines:{node:">=22.13.0"}},null,2));
writeFileSync(new URL("manifest.json",out),JSON.stringify(manifest,null,2));
console.log("V3 local preview built: "+fileURLToPath(out));
console.log("Run: node scripts/start-v3.mjs --human-test (from the bundle directory).");

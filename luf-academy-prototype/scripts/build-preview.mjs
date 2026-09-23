// Bygger förhandsvisningen för Human Test som en enda HTML-fil.
// Samma arbetsyta, samma innehållsregister, samma stil som prototypen.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { publicProgram } from "../server/content.mjs";

const read = (p) => readFileSync(new URL(`../${p}`, import.meta.url), "utf8");
const css = read("public/styles.css");
const app = read("public/app.js");
const transport = read("preview/transport.js");
// Samma regelmodul som servern. Exporterna blir window.LR_RULES.
const rulesSrc = read("server/rules.mjs");
const ruleNames = [...rulesSrc.matchAll(/^export (?:function|const) (\w+)/gm)].map((m) => m[1]);
const rules = `window.LR_RULES = (function () {\n${rulesSrc.replace(/^export /gm, "")}\nreturn { ${ruleNames.join(", ")} };\n})();`;
const program = JSON.stringify(publicProgram({ internal: true })).replace(/</g, "\\u003c");

const overrides = `
/* Förhandsvisning */
.topbar { top: env(safe-area-inset-top, 0px); }
.prototype-band { background: transparent; color: var(--muted); border-bottom: 1px solid var(--line); font-size: 11px; padding: 4px 12px; }
`;

const html = `<title>Min ledarskapsresa</title>
<meta name="robots" content="noindex, nofollow">
<style>
${css}
${overrides}
</style>
<div id="prototype-band" class="prototype-band" hidden>Testversion. Ej produktion.</div>
<header class="topbar">
  <a class="brand" href="#/"><span class="brand-name">LUF Academy</span><span class="brand-line">Ledarskap utan filter</span></a>
  <nav id="account" class="account" aria-label="Konto"></nav>
</header>
<main id="app" tabindex="-1"><p class="loading">Hämtar din resa.</p></main>
<div id="save-status" class="save-status" role="status" aria-live="polite"></div>
<dialog id="share-dialog" class="dialog"></dialog>
<script>window.LR_PROGRAM = ${program};</script>
<script>
${rules}
</script>
<script>
${transport}
</script>
<script>
${app}
</script>
`;

mkdirSync(new URL("../preview/dist/", import.meta.url), { recursive: true });
const out = new URL("../preview/dist/min-ledarskapsresa.html", import.meta.url);
writeFileSync(out, html);
console.log(`${out.pathname} ${(html.length / 1024).toFixed(0)} KB`);

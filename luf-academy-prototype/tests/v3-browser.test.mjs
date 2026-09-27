import { test } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { openV3Db,createV3App } from "../server/app-v3.mjs";
const require=createRequire(import.meta.url);
const {chromium}=require("playwright");
const shots=fileURLToPath(new URL("../test-results/v3/",import.meta.url));
mkdirSync(shots,{recursive:true});
async function setup(t,width=1280){
  const db=openV3Db(),app=createV3App(db,{humanTest:true}),server=createServer(app.handle);
  await new Promise(r=>server.listen(0,"127.0.0.1",r));
  const base="http://127.0.0.1:"+server.address().port;
  const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || undefined});
  const context=await browser.newContext({viewport:{width,height:900}});
  const page=await context.newPage(),external=[],errors=[];
  page.on("request",r=>{if(!r.url().startsWith(base))external.push(r.url());});
  page.on("pageerror",e=>errors.push(e.message));
  t.after(async()=>{await browser.close();await new Promise(r=>server.close(r));db.close();assert.deepEqual(external,[]);assert.deepEqual(errors,[]);});
  await page.goto(base+"/#test="+app.bootstrap);await page.locator("h1",{hasText:"Min riktning"}).waitFor();
  return {db,app,base,browser,context,page};
}
const nav=async(page,id)=>{await page.locator('#nav [data-nav="'+id+'"]').click();await page.locator('#nav [data-nav="'+id+'"][aria-current="page"]').waitFor();};
async function submit(page,id,type){
  const response=page.waitForResponse(r=>r.url().includes("/event") && r.request().postDataJSON()?.event?.type===type && r.status()===200);
  await page.locator('form[data-id="'+id+'"] button[type=submit]').click();await response;
  await page.waitForFunction(()=>document.querySelector("#status").textContent.startsWith("Sparat"));
}
async function fill(page,id,name,value){await page.locator('form[data-id="'+id+'"] [name="'+name+'"]').fill(value);}
async function clock(page,day){
  const done=page.waitForResponse(r=>r.url().includes("/event") && r.request().postDataJSON()?.event?.type==="clock" && r.status()===200);
  await page.locator("#clock").selectOption(String(day));await done;
}
for(const width of [1280,390]) test("Human journey, sharing, roles and layout "+width,async t=>{
  const {page,db}=await setup(t,width);
  // Start is usable without Spegel.
  await nav(page,"talk");await fill(page,"talk-start","preparation","Jag vill förstå varför jag avbryter.");
  await submit(page,"talk-start","note");
  await nav(page,"direction");
  await page.getByText("Spegeln 1",{exact:true}).first().click();
  await page.locator('[data-mirror="1"]').click();
  await page.getByText("egen chef · syntetiskt perspektiv",{exact:true}).waitFor();
  await page.getByText("egen chef · syntetiskt perspektiv",{exact:true}).click();
  await page.locator('[data-share="mirror:mirror1-0"]').click();
  await page.locator('[data-share="mirror:mirror1-0"][data-enabled="false"]').waitFor({state:"attached"});
  await clock(page,0);
  await fill(page,"focus","title","Lyssna färdigt");await fill(page,"focus","why","Ge andra utrymme");await fill(page,"focus","notice","Fler talar till punkt");
  await submit(page,"focus","focus");await page.locator(".card p").filter({hasText:"Lyssna färdigt"}).first().waitFor();
  await nav(page,"action");await fill(page,"action","what","Fråga före råd");await fill(page,"action","situation","Ett fiktivt möte");await fill(page,"action","when","Imorgon");await submit(page,"action","action");
  await nav(page,"outcome");
  let form=page.locator('form[data-kind="outcome"]').first(),id=await form.getAttribute("data-id");
  await form.locator("select").selectOption("Nej");
  assert.equal(await form.locator('[data-field="happened"]').isVisible(),false);
  assert.equal(await form.locator('[data-field="blocked"]').isVisible(),true);
  await form.locator('[name="blocked"]').fill("Mötet ställdes in");await form.locator('[name="next"]').fill("Prova nästa möte");await submit(page,id,"outcome");
  await page.screenshot({path:shots+"/outcome-"+width+".png",fullPage:true});
  await nav(page,"reflection");await fill(page,"reflection","text","PRIVATE-REFLECTION");await submit(page,"reflection","note");
  await page.getByText("När du vill undersöka lite djupare",{exact:true}).click();
  const boxes=await page.locator(".corners span").evaluateAll(xs=>xs.map(x=>({text:x.textContent,left:x.getBoundingClientRect().left})));
  assert.deepEqual(boxes.map(x=>x.text),["SE","HÖRA","KÄNNA"]);assert.ok(boxes[0].left<boxes[1].left && boxes[1].left<boxes[2].left);
  await nav(page,"round");await fill(page,"cotrainer-round-1","text","PRIVATE-COTRAINER");await submit(page,"cotrainer-round-1","note");
  await clock(page,21);await nav(page,"talk");await page.getByText("Mitt 1:1",{exact:true}).click();await fill(page,"talk-middle","takeaway","Ge mer tid");await submit(page,"talk-middle","note");
  await nav(page,"direction");await page.getByText("Ompröva: behåll eller byt fokus",{exact:true}).click();await fill(page,"focus","title","Ge tid efter frågan");await fill(page,"focus","reason","Jag förstod problemet bättre");await submit(page,"focus","focus");
  await nav(page,"action");await fill(page,"action","what","Vänta på svaret");await fill(page,"action","situation","Nästa fiktiva möte");await fill(page,"action","when","På fredag");await submit(page,"action","action");
  await nav(page,"outcome");form=page.locator('form[data-kind="outcome"]').first();id=await form.getAttribute("data-id");await form.locator("select").selectOption("Ja");await form.locator('[name="happened"]').fill("Den andre fick tänka klart");await form.locator('[name="evidence"]').fill("Jag hörde ett nytt förslag");await form.locator('[name="next"]').fill("Fortsätta ge tid");await submit(page,id,"outcome");
  await nav(page,"talk");await page.getByText("Avslutande 1:1",{exact:true}).click();await fill(page,"talk-end","next","Fortsätta ge tid");await submit(page,"talk-end","note");
  await clock(page,42);await clock(page,72);await nav(page,"journey");await fill(page,"d30","still","Jag väntar längre");await submit(page,"d30","note");
  await nav(page,"round");await page.getByText("Alla träffar",{exact:true}).click();assert.equal(await page.getByText("Runda bordet Återträff",{exact:true}).count()>=1,true);
  await clock(page,134);await nav(page,"journey");await page.getByText("Spegeln 2",{exact:true}).click();await page.locator('[data-mirror="2"]').click();await page.getByText("Spegeln 2",{exact:true}).click();await page.locator('[data-mirror="2"]').waitFor({state:"detached"});
  await fill(page,"three","noticed","Mer utrymme i samtalet");await submit(page,"three","note");
  await page.screenshot({path:shots+"/journey-"+width+".png",fullPage:true});
  await nav(page,"talk");await page.getByText("3-månaders 1:1",{exact:true}).click();await fill(page,"talk-three","takeaway","Fortsätta undersöka");await submit(page,"talk-three","note");
  const stored=JSON.parse(db.prepare("SELECT value FROM lr_v3_state WHERE user_id='v3_alex'").get().value);
  assert.equal(stored.focus.length,2);assert.equal(stored.actions.length,2);assert.equal(stored.mirrors.length,8);assert.equal(stored.coreEnd.next,"Fortsätta ge tid");
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator("#person").selectOption("v3_jan");await page.locator("#login").click();await page.getByRole("heading",{name:"Delat med Jan",exact:true}).waitFor();
  await page.getByText("Delat Spegel-perspektiv · egen chef",{exact:true}).waitFor();
  assert.ok(!(await page.locator("main").innerText()).includes("PRIVATE"));
  await page.screenshot({path:shots+"/jan-"+width+".png",fullPage:true});
  await page.locator("#person").selectOption("v3_admin");await page.locator("#login").click();await page.getByRole("heading",{name:"Programstatus",exact:true}).waitFor();
  await page.getByText("Startad · 4 syntetiska svar · klar",{exact:true}).first().waitFor();
  assert.ok(!(await page.locator("main").innerText()).includes("PRIVATE"));
  await page.screenshot({path:shots+"/admin-"+width+".png",fullPage:true});
});
test("Two tabs and failed saves keep local text; no silent overwrite",async t=>{
  const {page,context,base,app,db}=await setup(t);
  await nav(page,"reflection");
  const other=await context.newPage();await other.goto(base+"/#test="+app.bootstrap);await other.locator("h1",{hasText:"Min riktning"}).waitFor();await nav(other,"reflection");
  await fill(page,"reflection","text","FIRST-SAVED");await submit(page,"reflection","note");
  await fill(other,"reflection","text","SECOND-LOCAL");
  await other.waitForFunction(()=>document.querySelector("#status").textContent.includes("annan flik"));
  assert.equal(await other.locator('textarea[name="text"]').inputValue(),"SECOND-LOCAL");
  assert.equal(JSON.parse(db.prepare("SELECT value FROM lr_v3_state WHERE user_id='v3_alex'").get().value).notes.reflection.data.text,"FIRST-SAVED");
  await page.route("**/api/v3/event",r=>r.abort());
  await fill(page,"reflection","text","NETWORK-LOCAL");
  await page.getByRole("button",{name:"Försök spara igen",exact:true}).waitFor();
  assert.equal(await page.locator('textarea[name="text"]').inputValue(),"NETWORK-LOCAL");
  await page.unroute("**/api/v3/event");
  await page.getByRole("button",{name:"Försök spara igen",exact:true}).click();
  await page.waitForFunction(()=>document.querySelector("#status").textContent.startsWith("Sparat"));
  assert.equal(JSON.parse(db.prepare("SELECT value FROM lr_v3_state WHERE user_id='v3_alex'").get().value).notes.reflection.data.text,"NETWORK-LOCAL");
});
test("Validation can be corrected in place without freezing autosave",async t=>{
  const {page}=await setup(t);
  await fill(page,"focus","title","Undersöka");await submit(page,"focus","focus");
  await nav(page,"action");await fill(page,"action","what","Lyssna");await fill(page,"action","situation","Fiktivt samtal");await fill(page,"action","when","Idag");await submit(page,"action","action");
  await nav(page,"outcome");
  const form=page.locator('form[data-kind="outcome"]').first(),id=await form.getAttribute("data-id");
  await form.locator("select").selectOption("Nej");
  const invalid=page.waitForResponse(r=>r.url().includes("/event") && r.status()===400);
  await form.locator("button[type=submit]").click();await invalid;
  await form.locator('[name="blocked"]').fill("Tiden ändrades");await submit(page,id,"outcome");
  await nav(page,"reflection");await fill(page,"reflection","text","Jag kan fortsätta skriva");await submit(page,"reflection","note");
});

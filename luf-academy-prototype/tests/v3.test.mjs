import { test } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { DatabaseSync } from "node:sqlite";
import { openV3Db, createV3App } from "../server/app-v3.mjs";
import { initialState, reduceState, projectState } from "../server/rules-v3.mjs";
import { SURFACES,TALKS,CORNERS,FEELING,BOOK,FIELDS } from "../server/content-v3.mjs";
import { ROUNDS, MIRROR_FIXTURES } from "../preview/testdata-v3.mjs";
import { verifyBook } from "../scripts/verify-book-v3.mjs";
const focus=(id="f1",title="Lyssna färdigt",reason="")=>({type:"focus",id,data:{title,why:"Ge utrymme",notice:"Fler talar till punkt",reason}});
const action=id=>({type:"action",id,data:{what:"Ställa en fråga",situation:"Planeringsmötet",when:"Imorgon"}});
const step=(s,e)=>reduceState(s,e);
async function fixture(t){
  const db=openV3Db(),app=createV3App(db,{humanTest:true}),server=createServer(app.handle);
  await new Promise(r=>server.listen(0,"127.0.0.1",r));
  const base="http://127.0.0.1:"+server.address().port;
  t.after(async()=>{await new Promise(r=>server.close(r));db.close();});
  async function login(id){
    const r=await fetch(base+"/api/v3/login",{method:"POST",headers:{"Content-Type":"application/json",Origin:base},body:JSON.stringify({bootstrap:app.bootstrap,person:id})});
    assert.equal(r.status,200);return r.headers.get("set-cookie").split(";")[0];
  }
  const request=async(cookie,path,body,origin=base)=>{
    const r=await fetch(base+"/api/v3/"+path,{method:body?"POST":"GET",headers:{Cookie:cookie,Origin:origin,"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined});
    return {status:r.status,body:await r.json()};
  };
  return {db,request,login,base,app};
}
test("A: isolated schema, migration rollback and production gate",()=>{
  const db=openV3Db();
  assert.throws(()=>createV3App(db),/endast/);
  assert.ok(db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all().every(x=>x.name.startsWith("lr_v3_")));
  db.exec("DROP TABLE lr_v3_history; DROP TABLE lr_v3_state; DROP TABLE lr_v3_meta;");
  assert.equal(db.prepare("SELECT COUNT(*) n FROM sqlite_master WHERE type='table'").get().n,0);db.close();
  const p=join(mkdtempSync(join(tmpdir(),"v3-isolation-")),"v2.sqlite");
  const v2=new DatabaseSync(p);v2.exec("CREATE TABLE lr_entry(value TEXT); INSERT INTO lr_entry VALUES ('PRESERVE');");v2.close();
  assert.throws(()=>openV3Db(p),/egen databas/);
  const unchanged=new DatabaseSync(p);assert.equal(unchanged.prepare("SELECT value FROM lr_entry").get().value,"PRESERVE");unchanged.close();
});
test("B: one focus, preserved reason/history, observation never creates focus",()=>{
  let s=step(initialState(),focus());
  s=step(s,{type:"note",kind:"reflection",id:"reflection",data:{text:"Annat jag ser"}});
  assert.equal(s.focus.length,1);
  assert.throws(()=>step(s,focus("f2","Nytt fokus")),/byter/);
  s=step(s,focus("f2","Fråga före råd","Jag såg ett annat problem"));
  assert.equal(s.focus.filter(x=>x.active).length,1);assert.equal(s.focus[0].title,"Lyssna färdigt");
  assert.equal(s.focus[1].reason,"Jag såg ett annat problem");
  s=step(s,{type:"keep",data:{reason:"Vill prova igen"}});assert.equal(s.reviews.length,1);
});
test("C: several actions, Ja/Delvis/Nej and conditional backbone, no seven fields",()=>{
  let s=step(initialState(),focus());
  for(const [i,result] of ["Ja","Delvis","Nej"].entries()){
    s=step(s,action("a"+i));
    if(result==="Nej") assert.throws(()=>step(s,{type:"outcome",id:"a"+i,data:{result}}),/stoppade/);
    s=step(s,{type:"outcome",id:"a"+i,data:{result,blocked:result==="Nej"?"Mötet ställdes in":"",next:"Prova igen"}});
  }
  assert.equal(s.actions.length,3);
  assert.deepEqual(s.actions.map(x=>x.outcome.result),["Ja","Delvis","Nej"]);
  assert.equal(s.actions[2].outcome.happened,"");
  assert.equal(FIELDS.outcome.length,5);
  assert.throws(()=>step(s,action("a0")),/finns redan/);
  assert.throws(()=>step(s,{type:"outcome",id:"a0",data:{result:"Ja",se:"extra"}}),/Okänt/);
});
test("D: HTTP authentication, ownership, active share/revoke, status-only admin, no employer",async t=>{
  const f=await fixture(t),alex=await f.login("v3_alex"),sam=await f.login("v3_sam"),jan=await f.login("v3_jan"),admin=await f.login("v3_admin"),employer=await f.login("v3_employer");
  assert.equal((await f.request("","state")).status,401);
  let revision=0;
  const save=async event=>{const r=await f.request(alex,"event",{baseRevision:revision,event});assert.equal(r.status,200);revision=r.body.revision;return r;};
  await save(focus());await save({type:"mirror",round:1});
  await save({type:"note",kind:"reflection",id:"reflection",data:{text:"PRIVATE-OBSERVATION"}});
  await save({type:"note",kind:"cotrainer",id:"cotrainer-round-1",data:{text:"PRIVATE-COTRAINER"}});
  assert.equal((await f.request(sam,"state?participant=v3_alex")).status,404);
  assert.deepEqual((await f.request(jan,"state?participant=v3_alex")).body.state.shared,[]);
  const status=await f.request(admin,"state?participant=v3_alex");
  assert.equal(status.body.state.mirrors[0].count,4);
  assert.ok(!JSON.stringify(status).includes("PRIVATE"));
  assert.ok(!JSON.stringify(status).includes(MIRROR_FIXTURES[0].answers[0]));
  assert.equal((await f.request(employer,"state?participant=v3_alex")).status,403);
  assert.equal((await f.request(jan,"history?participant=v3_alex")).status,403);
  assert.equal((await f.request(admin,"event",{baseRevision:revision,event:focus()})).status,403);
  assert.equal((await f.request(alex,"event",{baseRevision:revision,event:{type:"share",target:"note:cotrainer-round-1",enabled:true}})).status,400);
  await save({type:"share",target:"mirror:mirror1-0",enabled:true});
  let shared=(await f.request(jan,"state?participant=v3_alex")).body.state.shared;
  assert.equal(shared.length,1);assert.deepEqual(shared[0].value.answers,MIRROR_FIXTURES[0].answers);
  await save({type:"share",target:"mirror:mirror1-0",enabled:false});
  assert.deepEqual((await f.request(jan,"state?participant=v3_alex")).body.state.shared,[]);
  await save({type:"note",kind:"summary",id:"summary-1",data:{text:"SELECTED-SUMMARY"}});
  await save({type:"share",target:"note:summary-1",enabled:true});
  shared=(await f.request(jan,"state?participant=v3_alex")).body.state.shared;
  assert.equal(shared[0].value.data.text,"SELECTED-SUMMARY");
  assert.ok(!JSON.stringify(shared).includes("PRIVATE"));
  assert.equal((await f.request(alex,"event",{baseRevision:revision,event:focus("x")},"http://evil.invalid")).status,403);
});
test("D: concurrency, no missing revisions, rejected writes leave history untouched",async t=>{
  const f=await fixture(t),cookie=await f.login("v3_alex");
  const results=await Promise.all([f.request(cookie,"event",{baseRevision:0,event:focus("a")}),f.request(cookie,"event",{baseRevision:0,event:focus("b")})]);
  assert.deepEqual(results.map(x=>x.status).sort(),[200,409]);
  assert.equal((await f.request(cookie,"event",{event:focus("c")})).status,409);
  assert.equal(f.db.prepare("SELECT COUNT(*) n FROM lr_v3_history").get().n,1);
  assert.equal((await f.request(cookie,"history")).body.length,1);
  assert.equal((await f.request(cookie,"state")).body.revision,1);
});
test("D: persistence across reopen; history is private source snapshots",()=>{
  const p=join(mkdtempSync(join(tmpdir(),"v3-persist-")),"synthetic.sqlite");
  let db=openV3Db(p);const state=step(initialState(),focus());
  db.prepare("UPDATE lr_v3_state SET value=?,revision=1 WHERE user_id='v3_alex'").run(JSON.stringify(state));db.close();
  db=openV3Db(p);assert.equal(JSON.parse(db.prepare("SELECT value FROM lr_v3_state WHERE user_id='v3_alex'").get().value).focus[0].title,"Lyssna färdigt");db.close();
});
test("E: six meetings and reunion, no themes/completion, private optional cotrainer",()=>{
  assert.equal(ROUNDS.length,7);assert.equal(ROUNDS[6].day,42+30);
  assert.ok(ROUNDS.every(x=>!("theme" in x) && !("completion" in x)));
  const s=step(initialState(),{type:"note",kind:"cotrainer",id:"cotrainer-round-1",data:{text:"Jag lyssnade"}});
  assert.ok(!JSON.stringify(projectState(s,"program_admin")).includes("lyssnade"));
  assert.ok(!JSON.stringify(projectState(s,"facilitator")).includes("lyssnade"));
});
test("F: four conversations, minutes are advisory; Start does not require Spegel",()=>{
  assert.deepEqual(TALKS.map(x=>x.minutes),[60,45,45,30]);
  const s=step(initialState(),{type:"note",kind:"talk",id:"talk-start",data:{preparation:"Jag vet inte ännu"}});
  assert.equal(s.notes["talk-start"].data.preparation,"Jag vet inte ännu");
  assert.equal(s.mirrors.length,0);
});
test("G: three book layers without week rules; real PDF checks reject wrong title/page",()=>{
  assert.deepEqual(Object.keys(BOOK),["foundation","cases","optional"]);
  assert.ok(!JSON.stringify(BOOK).includes("vecka"));
  assert.ok(process.env.LHM_BOOK_TXT,"Boktext krävs, testet får inte hoppas över.");
  const raw=readFileSync(process.env.LHM_BOOK_TXT,"utf8");
  assert.deepEqual(verifyBook(BOOK,raw),[]);
  const bad=structuredClone(BOOK);bad.foundation[0].title="Påhittad rubrik";
  assert.ok(verifyBook(bad,raw).length>0);
  const wrong=structuredClone(BOOK);wrong.foundation[0].pages="1–2";
  assert.ok(verifyBook(wrong,raw).length>0);
});
test("H: permanent SE/HÖRA/KÄNNA positions and own-signal wording",()=>{
  assert.deepEqual(CORNERS,["SE","HÖRA","KÄNNA"]);assert.match(FEELING,/egen signal/);assert.match(FEELING,/aldrig kunskap/);
  assert.equal(SURFACES.length,7);
});
test("I: fixed synthetic mirrors, no injected answers, no contact/email routes",async t=>{
  const f=await fixture(t),cookie=await f.login("v3_alex");
  let r=await f.request(cookie,"event",{baseRevision:0,event:{type:"mirror",round:1,data:{answers:["real"]}}});
  assert.equal(r.status,400);
  r=await f.request(cookie,"event",{baseRevision:0,event:{type:"mirror",round:2}});assert.equal(r.status,400);
  assert.ok(MIRROR_FIXTURES.every(x=>x.synthetic));
  for(const path of ["invite","email","external-mirror","analytics"]) assert.equal((await f.request(cookie,path,{text:"PRIVATE"})).status,404);
});
test("Journey: end snapshot survives later focus/action, 30 days and 3 months",()=>{
  let s=step(initialState(),focus());s=step(s,action("a1"));
  s=step(s,{type:"outcome",id:"a1",data:{result:"Ja",next:"Fortsätta lyssna"}});
  s=step(s,{type:"clock",day:42});
  s=step(s,focus("f2","Senare fokus","Ny insikt"));
  s=step(s,action("a2"));s=step(s,{type:"clock",day:72});
  assert.equal(s.coreEnd.focus.id,"f1");assert.equal(s.coreEnd.action.id,"a1");assert.equal(s.coreEnd.next,"Fortsätta lyssna");
  s=step(s,{type:"note",kind:"d30",id:"d30",data:{still:"Lyssnar"}});
  assert.throws(()=>step(s,{type:"mirror",round:2}),/tremånaders/);
  s=step(s,{type:"clock",day:134});s=step(s,{type:"mirror",round:2});
  s=step(s,{type:"note",kind:"talk",id:"talk-three",data:{takeaway:"Undersöka vidare"}});
  assert.equal(s.mirrors.filter(x=>x.round===2).length,4);
  assert.equal(s.notes.d30.data.still,"Lyssnar");
});

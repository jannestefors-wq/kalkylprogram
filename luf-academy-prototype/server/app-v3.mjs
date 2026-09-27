import { DatabaseSync } from "node:sqlite";
import { createHash, randomBytes, timingSafeEqual } from "node:crypto";
import { readFileSync } from "node:fs";
import { initialState, reduceState, projectState, recommend, V3Error } from "./rules-v3.mjs";
import * as content from "./content-v3.mjs";
import { PEOPLE, ROUNDS, FIXTURE_ID } from "../preview/testdata-v3.mjs";
const hash = token => createHash("sha256").update(token).digest("hex");
const equal = (a,b) => typeof a === "string" && typeof b === "string" && a.length === b.length && timingSafeEqual(Buffer.from(a),Buffer.from(b));
export function openV3Db(path = ":memory:") {
  const db = new DatabaseSync(path);
  const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all().map(x => x.name);
  if (tables.some(x => !x.startsWith("lr_v3_"))) { db.close(); throw new Error("V3 Human Test kräver en egen databas."); }
  db.exec(readFileSync(new URL("./migrations-v3/0001_foundation.sql", import.meta.url), "utf8"));
  db.prepare("INSERT OR IGNORE INTO lr_v3_meta VALUES (?)").run(FIXTURE_ID);
  for (const p of PEOPLE.filter(x => x.role === "participant")) db.prepare("INSERT OR IGNORE INTO lr_v3_state VALUES (?, 0, ?, ?)").run(p.id, JSON.stringify(initialState()), new Date().toISOString());
  return db;
}
export function createV3App(db, { humanTest = false, bootstrap = randomBytes(32).toString("hex") } = {}) {
  // Ingen produktionsväg. Måste väljas uttryckligen, och endast loopback.
  if (!humanTest) throw new Error("V3 024 är endast syntetisk Human Test.");
  const sessions = new Map();
  const asset = (path, type) => ({ data: readFileSync(new URL(path, import.meta.url)), type });
  const assets = {
    "/": asset("../public-v3/index.html", "text/html; charset=utf-8"),
    "/app.js": asset("../public-v3/app.js", "text/javascript; charset=utf-8"),
    "/styles.css": asset("../public-v3/styles.css", "text/css; charset=utf-8")
  };
  const row = id => {
    const r = db.prepare("SELECT * FROM lr_v3_state WHERE user_id=?").get(id);
    if (!r) throw new V3Error(404,"Resan finns inte.");
    return { revision: r.revision, state: JSON.parse(r.value) };
  };
  function write(id, baseRevision, change) {
    db.exec("BEGIN IMMEDIATE");
    try {
      const old = row(id);
      if (!Number.isInteger(baseRevision) || baseRevision !== old.revision) throw new V3Error(409, "Texten har ändrats i en annan flik. Din text finns kvar här. Hämta senaste versionen innan du försöker igen.");
      const next = change(old.state);
      const now = new Date().toISOString();
      db.prepare("INSERT INTO lr_v3_history VALUES (?,?,?,?)").run(id, old.revision, JSON.stringify(old.state), now);
      db.prepare("UPDATE lr_v3_state SET revision=?,value=?,updated_at=? WHERE user_id=?").run(old.revision+1,JSON.stringify(next),now,id);
      db.exec("COMMIT");
      return {revision:old.revision+1,state:next};
    } catch(e) { db.exec("ROLLBACK"); throw e; }
  }
  async function body(req) {
    let size=0; const chunks=[];
    for await(const chunk of req) { size+=chunk.length; if(size>65536) throw new V3Error(413,"För mycket text."); chunks.push(chunk); }
    try { return JSON.parse(Buffer.concat(chunks).toString("utf8")); } catch { throw new V3Error(400,"Ogiltig förfrågan."); }
  }
  function send(res, code, value) { res.writeHead(code,{"Content-Type":"application/json; charset=utf-8"}); res.end(JSON.stringify(value)); }
  async function handle(req,res) {
    res.setHeader("Cache-Control","no-store");
    res.setHeader("Content-Security-Policy","default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'");
    res.setHeader("X-Content-Type-Options","nosniff");
    res.setHeader("Referrer-Policy","no-referrer");
    try {
      if (!["127.0.0.1","::1","::ffff:127.0.0.1"].includes(req.socket.remoteAddress)) throw new V3Error(403,"Endast lokal Human Test.");
      const host = req.headers.host || "";
      if (!/^(127\.0\.0\.1|localhost|\[::1\]):\d+$/.test(host)) throw new V3Error(403,"Ogiltig värd.");
      if(req.method !== "GET" && req.headers.origin !== "http://"+host) throw new V3Error(403,"Ogiltigt ursprung.");
      const url=new URL(req.url,"http://"+host);
      if(req.method==="GET" && assets[url.pathname]) { res.writeHead(200,{"Content-Type":assets[url.pathname].type}); return res.end(assets[url.pathname].data); }
      if(url.pathname==="/api/v3/login" && req.method==="POST") {
        const b=await body(req);
        if(!equal(b.bootstrap,bootstrap)) throw new V3Error(403,"Öppna testlänken från den lokala starten.");
        const person=PEOPLE.find(x=>x.id===b.person);
        if(!person) throw new V3Error(403,"Okänd testperson.");
        const token=randomBytes(32).toString("hex");
        sessions.set(hash(token), {person,expires:Date.now()+8*3600000});
        res.setHeader("Set-Cookie","lr_v3_session="+token+"; HttpOnly; SameSite=Strict; Path=/");
        return send(res,200,{person});
      }
      const token=(req.headers.cookie || "").match(/(?:^|; )lr_v3_session=([^;]+)/)?.[1] || "";
      const session=sessions.get(hash(token));
      if(!session || session.expires<Date.now()) throw new V3Error(401,"Välj en testvy.");
      const person=session.person;
      if(url.pathname==="/api/v3/config" && req.method==="GET") return send(res,200,{person,people:PEOPLE,surfaces:content.SURFACES,talks:content.TALKS,compass:content.COMPASS,compassNote:content.COMPASS_NOTE,corners:content.CORNERS,feeling:content.FEELING,fields:content.FIELDS,mirror:content.MIRROR,book:content.BOOK,bookNote:content.BOOK_NOTE,resultNote:content.RESULT_NOTE,rounds:ROUNDS});
      const target=url.searchParams.get("participant") || person.id;
      if(person.role==="participant" && target!==person.id) throw new V3Error(404,"Resan finns inte.");
      if(person.role==="employer") throw new V3Error(403,"Arbetsgivare har ingen individuell läsväg.");
      if(url.pathname==="/api/v3/state" && req.method==="GET") {
        const r=row(target); return send(res,200,{revision:r.revision,state:projectState(r.state,person.role)});
      }
      if(url.pathname==="/api/v3/history" && req.method==="GET") {
        if(person.role!=="participant") throw new V3Error(403,"Historiken är privat.");
        return send(res,200,db.prepare("SELECT revision,value,created_at FROM lr_v3_history WHERE user_id=? ORDER BY revision DESC LIMIT 50").all(person.id).map(r=>({...r,value:JSON.parse(r.value)})));
      }
      if(url.pathname==="/api/v3/event" && req.method==="POST") {
        if(person.role!=="participant") throw new V3Error(403,"Endast deltagaren skriver sin resa.");
        const b=await body(req);
        return send(res,200,write(person.id,b.baseRevision,s=>reduceState(s,b.event)));
      }
      if(url.pathname==="/api/v3/recommend" && req.method==="POST") {
        if(person.role!=="facilitator") throw new V3Error(403,"Endast Jan kan rekommendera ett avsnitt.");
        const b=await body(req);
        const r=write(target,b.baseRevision,s=>recommend(s,b.title));
        return send(res,200,{revision:r.revision,state:projectState(r.state,person.role)});
      }
      throw new V3Error(404,"Sidan finns inte.");
    } catch(e) { send(res,e instanceof V3Error?e.status:500,{error:e instanceof V3Error?e.message:"Det gick inte att spara. Försök igen; behåll din text."}); }
  }
  return {handle,bootstrap};
}

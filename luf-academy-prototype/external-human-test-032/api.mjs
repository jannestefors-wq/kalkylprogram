
import {initialState,reduceState,projectState,recommend,V3Error} from './server/rules-v3.mjs';
import * as content from './server/content-v3.mjs';
import {ROUNDS} from './preview/testdata-v3.mjs';
const enc=new TextEncoder();
export const hash=async value=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',enc.encode(value))),b=>b.toString(16).padStart(2,'0')).join('');
const random=()=>Array.from(crypto.getRandomValues(new Uint8Array(32)),b=>b.toString(16).padStart(2,'0')).join('');
const one=(db,q,...p)=>db.prepare(q).bind(...p).first();
const run=(db,q,...p)=>db.prepare(q).bind(...p).run();
const stmt=(db,q,...p)=>db.prepare(q).bind(...p);
const deny=(status,message)=>{throw new V3Error(status,message)};
const catalog=env=>{
 const entries=JSON.parse(env.LMHM032_ACCESS || '[]');
 if(entries.length!==12)deny(503,'Testmiljön är inte tillgänglig.');
 return entries;
};
const safePerson=p=>({id:p.id,role:p.role,name:p.name});
export const headers={'Cache-Control':'no-store','X-Robots-Tag':'noindex, nofollow, noarchive','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"};
const json=(data,status=200,extra={})=>Response.json(data,{status,headers:{...headers,...extra}});
const sessionToken=req=>req.headers.get('cookie')?.match(/(?:^|;\s*)lmhm032=([a-f0-9]{64})(?:;|$)/)?.[1];
export async function identity(env,req){
 const token=sessionToken(req);if(!token)return null;
 const s=await one(env.DB,'SELECT s.user_id,s.epoch FROM ht032_session s JOIN ht032_control c ON c.user_id=s.user_id WHERE s.hash=? AND s.expires>? AND c.revoked=0 AND c.epoch=s.epoch',await hash(token),Date.now());
 if(!s)return null;
 const p=catalog(env).find(x=>x.id===s.user_id);return p?{...safePerson(p),epoch:s.epoch}:null;
}
async function row(db,id){
 const r=await one(db,'SELECT revision,value FROM ht032_state WHERE user_id=?',id);
 return r?{revision:r.revision,state:JSON.parse(r.value)}:{revision:0,state:initialState()};
}
async function write(env,p,id,base,change){
 const old=await row(env.DB,id);
 if(!Number.isInteger(base)||base!==old.revision)deny(409,'Texten har ändrats i en annan flik. Din text finns kvar här. Hämta senaste versionen innan du försöker igen.');
 const next=change(old.state),writeId=random(),at=new Date().toISOString();
 // Ensure empty state exists, then compare-and-swap and history in one D1 batch.
 await run(env.DB,'INSERT OR IGNORE INTO ht032_state(user_id,revision,value) VALUES(?,0,?)',id,JSON.stringify(initialState()));
 const results=await env.DB.batch([
 stmt(env.DB,'UPDATE ht032_state SET revision=revision+1,value=?,write_id=? WHERE user_id=? AND revision=? AND EXISTS(SELECT 1 FROM ht032_control WHERE user_id=? AND epoch=? AND revoked=0)',JSON.stringify(next),writeId,id,base,p.id,p.epoch),
 stmt(env.DB,'INSERT INTO ht032_history(user_id,revision,value,created_at) SELECT ?,?,?,? WHERE EXISTS(SELECT 1 FROM ht032_state WHERE user_id=? AND write_id=?)',id,base,JSON.stringify(old.state),at,id,writeId)
 ]);
 if(results[0].meta.changes!==1)deny(409,'Testresan har ändrats eller återställts. Öppna testlänken igen.');
 return {revision:base+1,state:projectState(next,p.role)};
}
export async function handle(env,req){
 try{
  const u=new URL(req.url),path=u.pathname,db=env.DB;
  let b={};
  if(req.method!=='GET'){
   if(req.headers.get('origin')!==u.origin)deny(403,'Ogiltigt ursprung.');
   if(!req.headers.get('content-type')?.startsWith('application/json'))deny(415,'JSON krävs.');
   const raw=await req.text();if(raw.length>65536)deny(413,'För mycket text.');
   try{b=JSON.parse(raw)}catch{deny(400,'Ogiltig förfrågan.')}
   if(!b||typeof b!=='object'||Array.isArray(b))deny(400,'Ogiltig förfrågan.');
  }
  if(path==='/api/v3/login'&&req.method==='POST'){
   if(typeof b.token!=='string'||!/^[a-f0-9]{64}$/.test(b.token))deny(403,'Testlänken är ogiltig eller återkallad.');
   const digest=await hash(b.token),entry=catalog(env).find(x=>x.hash===digest);
   if(!entry)deny(403,'Testlänken är ogiltig eller återkallad.');
   await run(db,'INSERT OR IGNORE INTO ht032_control(user_id,epoch,revoked) VALUES(?,0,0)',entry.id);
   const c=await one(db,'SELECT epoch,revoked FROM ht032_control WHERE user_id=?',entry.id);
   if(c.revoked)deny(403,'Testlänken är ogiltig eller återkallad.');
   const token=random();
   await run(db,'INSERT INTO ht032_session(hash,user_id,epoch,expires) VALUES(?,?,?,?)',await hash(token),entry.id,c.epoch,Date.now()+8*3600000);
   return json({ok:true},200,{'Set-Cookie':'lmhm032='+token+'; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=28800'});
  }
  const p=await identity(env,req);if(!p)deny(401,'Öppna din individuella testlänk.');
  if(path==='/api/v3/logout'&&req.method==='POST'){
   await run(db,'DELETE FROM ht032_session WHERE hash=?',await hash(sessionToken(req)));
   return json({ok:true},200,{'Set-Cookie':'lmhm032=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0'});
  }
  const participants=catalog(env).filter(x=>x.role==='participant');
  const target=u.searchParams.get('participant')||p.id;
  if(p.role==='participant'&&target!==p.id)deny(404,'Resan finns inte.');
  if(path==='/api/v3/config'&&req.method==='GET')return json({person:safePerson(p),people:p.role==='participant'?[safePerson(p)]:participants.map(safePerson),surfaces:content.SURFACES,talks:content.TALKS,compass:content.COMPASS,compassNote:content.COMPASS_NOTE,corners:content.CORNERS,feeling:content.FEELING,fields:content.FIELDS,mirror:content.MIRROR,book:content.BOOK,bookNote:content.BOOK_NOTE,resultNote:content.RESULT_NOTE,rounds:ROUNDS});
  if(path==='/api/v3/manage'){
   if(p.role!=='facilitator')deny(403,'Endast Jan hanterar testplatser.');
   if(req.method==='GET'){
    const slots=[];
    for(const person of participants){
     const c=await one(db,'SELECT epoch,revoked FROM ht032_control WHERE user_id=?',person.id);
     const f=await one(db,'SELECT value,updated_at FROM ht032_feedback WHERE user_id=?',person.id);
     slots.push({...safePerson(person),revoked:!!c?.revoked,feedback:f?JSON.parse(f.value):null,updatedAt:f?.updated_at||null});
    }
    return json(slots);
   }
   if(req.method==='POST'){
    if(!participants.some(x=>x.id===b.id)||!['reset','delete','revoke'].includes(b.action))deny(400,'Ogiltig testplats eller åtgärd.');
    await run(db,'INSERT OR IGNORE INTO ht032_control(user_id,epoch,revoked) VALUES(?,0,0)',b.id);
    const statements=[stmt(db,'UPDATE ht032_control SET epoch=epoch+1,revoked=CASE WHEN ?=1 THEN 1 ELSE revoked END WHERE user_id=?',b.action==='reset'?0:1,b.id),stmt(db,'DELETE FROM ht032_session WHERE user_id=?',b.id)];
    if(b.action!=='revoke')for(const table of ['ht032_history','ht032_state','ht032_feedback'])statements.push(stmt(db,'DELETE FROM '+table+' WHERE user_id=?',b.id));
    await db.batch(statements);return json({ok:true});
   }
  }
  if(path==='/api/v3/feedback'){
   if(p.role!=='participant')deny(403,'Endast testaren lämnar feedback.');
   if(req.method==='GET'){const r=await one(db,'SELECT value FROM ht032_feedback WHERE user_id=?',p.id);return json(r?JSON.parse(r.value):['','','','','']);}
   if(req.method==='POST'){
    if(!Array.isArray(b.answers)||b.answers.length!==5||b.answers.some(x=>typeof x!=='string'||x.length>5000))deny(400,'Skriv högst 5000 tecken per svar.');
    const saved=await run(db,'INSERT INTO ht032_feedback(user_id,value,updated_at) SELECT ?,?,? WHERE EXISTS(SELECT 1 FROM ht032_control WHERE user_id=? AND epoch=? AND revoked=0) ON CONFLICT(user_id) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at',p.id,JSON.stringify(b.answers),new Date().toISOString(),p.id,p.epoch);
    if(saved.meta.changes!==1)deny(409,'Testplatsen har återställts eller återkallats. Öppna testlänken igen.');
    return json({ok:true});
   }
  }
  if(!participants.some(x=>x.id===target))deny(404,'Resan finns inte.');
  if(path==='/api/v3/state'&&req.method==='GET'){const r=await row(db,target);return json({revision:r.revision,state:projectState(r.state,p.role)});}
  if(path==='/api/v3/history'&&req.method==='GET'){
   if(p.role!=='participant')deny(403,'Historiken är privat.');
   const r=await db.prepare('SELECT revision,value,created_at FROM ht032_history WHERE user_id=? ORDER BY revision DESC LIMIT 50').bind(p.id).all();
   return json(r.results.map(x=>({...x,value:JSON.parse(x.value)})));
  }
  if(path==='/api/v3/event'&&req.method==='POST'){
   if(p.role!=='participant')deny(403,'Endast deltagaren skriver sin resa.');
   return json(await write(env,p,p.id,b.baseRevision,s=>reduceState(s,b.event)));
  }
  if(path==='/api/v3/recommend'&&req.method==='POST'){
   if(p.role!=='facilitator')deny(403,'Endast Jan kan ge läshänvisning.');
   return json(await write(env,p,target,b.baseRevision,s=>recommend(s,b.title)));
  }
  deny(404,'Sidan finns inte.');
 }catch(e){return json({error:e instanceof V3Error?e.message:'Testmiljön kunde inte svara. Behåll texten och försök igen.'},e instanceof V3Error?e.status:500);}
}


import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
const dir=new URL('./',import.meta.url);
const read=p=>readFileSync(new URL(p,dir),'utf8');
let app=read('../public-v3/app.js');
app=app.replace(/let bootstrap =[^\n]+\nif\(bootstrap\)[^\n]+/,'');
app=app.replace('await api("login",{bootstrap,person:$("#person").value});','');
app=app.replace('cfg=await api("config");blocked=false;dirty=false;','cfg=await api("config");blocked=false;dirty=false; $("#feedback-link").hidden=cfg.person.role!=="participant"; $("#manage-link").hidden=cfg.person.role!=="facilitator";');
app=app.replace('}catch(e){if(!blocked)status(e.message);}\n};','}catch(e){if(e.status===401)location.replace("/human-test");else if(!blocked)status(e.message);}\n};');
app=app.replace('if(bootstrap) $("#login").click();','$("#login").click();\n$("#logout").onclick=async()=>{await flush();await api("logout",{});location.replace("/human-test");};');
let index=read('../public-v3/index.html');
index=index.replace(/    <label>Testvy.*\n/,'').replace('<button id="login">Öppna testvy</button>','<button id="login" hidden>Öppna testvy</button><a id="feedback-link" href="/feedback" hidden>Testfeedback</a><a id="manage-link" href="/manage" hidden>Hantera testplatser</a><button id="logout">Logga ut</button>').replace('Simulerad tid','Testläge · simulerad tid').replace('Öppna den lokala testlänken och välj en testvy. Använd bara påhittade uppgifter.','Din privata testresa laddas. Använd bara påhittade uppgifter.');
const shell=(title,body,script)=>'<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+title+'</title><link rel="stylesheet" href="/styles.css"></head><body><header><a class="brand" href="/academy">LUF Academy<span>Human Test · fiktiva uppgifter</span></a></header><div class="layout"><main>'+body+'</main></div><script type="module" src="/'+script+'"></script></body></html>';
const entry=shell('LMHM Human Test','<h1>Välkommen till Human Test</h1><p>Detta är en testversion av Ledarskap med hjärta och mod.</p><p>Testa hur resan, frågorna och verktygen känns att använda.</p><p>Använd fiktiva situationer och namn. Skriv inte in känsliga personuppgifter eller verkliga uppgifter om kollegor, medarbetare eller andra personer.</p><p>Spegelns svar i denna testversion är syntetiska och inga andra människor kontaktas.</p><button id="begin">Jag förstår – börja testa</button><p id="message" role="status"></p>','entry.js');
const entryJs=`let token=location.hash.startsWith('#invite=')?location.hash.slice(8):null;
history.replaceState(null,'',location.pathname);
window.addEventListener('hashchange',()=>{if(location.hash.startsWith('#invite=')){token=location.hash.slice(8);history.replaceState(null,'',location.pathname);}});
document.querySelector('#begin').onclick=async()=>{
 const message=document.querySelector('#message'),button=document.querySelector('#begin');button.disabled=true;
 try{
  const r=token?await fetch('/api/v3/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token})}):await fetch('/api/v3/config');
  const b=await r.json();if(!r.ok)throw new Error(b.error);token=null;location.replace('/academy');
 }catch(e){message.textContent=e.message||'Kunde inte öppna testet. Öppna din individuella länk igen.';button.disabled=false;}
};`;
const questions=['Var det tydligt vad du skulle göra?','Var det någonstans du fastnade eller blev osäker?','Vilken del gav mest värde?','Var det något som kändes onödigt eller krångligt?','Vad skulle få detta att kännas ännu mer användbart för dig?'];
const feedback=shell('Testfeedback','<h1>Testfeedback</h1><p>Frivilligt. Använd fiktiva uppgifter. Jan läser svaren under ditt testnummer, separat från resan.</p><form id="feedback">'+questions.map((q,i)=>'<label for="q'+i+'">'+q+'</label><textarea disabled maxlength="5000" id="q'+i+'"></textarea>').join('')+'<button disabled>Spara feedback</button></form><p id="message" role="status"></p><a href="/academy">Tillbaka till resan</a>','feedback.js');
const feedbackJs=`const message=document.querySelector('#message'),fields=[...document.querySelectorAll('textarea')];
try{const r=await fetch('/api/v3/feedback');const b=await r.json();if(!r.ok)throw new Error(b.error);fields.forEach((x,i)=>{x.value=b[i]||'';x.disabled=false;});document.querySelector('form button').disabled=false;}catch(e){message.textContent=e.message;}
document.querySelector('form').onsubmit=async e=>{e.preventDefault();try{const r=await fetch('/api/v3/feedback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answers:fields.map(x=>x.value)})});const b=await r.json();if(!r.ok)throw new Error(b.error);message.textContent='Feedbacken är sparad.';}catch(e){message.textContent=e.message;}};`;
const manage=shell('Hantera testplatser','<h1>Hantera testplatser</h1><p>Återställ tar bort resa, historik och feedback men behåller länken om den inte återkallats. Radera tar bort samma data och återkallar länken. Återkalla stoppar åtkomsten men bevarar data. Alla tre åtgärder avslutar platsens aktiva sessioner.</p><div id="slots"></div><p id="message" role="status"></p><a href="/academy">Till Jans vy</a>','manage.js');
const manageJs=`const questions=${JSON.stringify(questions)};
const box=document.querySelector('#slots'),message=document.querySelector('#message');
async function load(){const r=await fetch('/api/v3/manage');const rows=await r.json();if(!r.ok)throw new Error(rows.error);box.replaceChildren();
 for(const slot of rows){const card=document.createElement('section');card.className='card';const title=document.createElement('h2');title.textContent=slot.name+' · '+(slot.revoked?'Återkallad':'Aktiv');card.append(title);
 for(const [i,q] of questions.entries()){const h=document.createElement('h3'),p=document.createElement('p');h.textContent=q;p.textContent=slot.feedback?.[i]||'Ingen feedback ännu';card.append(h,p);}
 for(const [action,label] of [['reset','Återställ testdata'],['delete','Radera data och återkalla'],['revoke','Återkalla länk']]){const button=document.createElement('button');button.textContent=label;button.onclick=async()=>{if(!confirm(label+' för '+slot.name+'?'))return;try{const r=await fetch('/api/v3/manage',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:slot.id,action})});const b=await r.json();if(!r.ok)throw new Error(b.error);await load();message.textContent='Klart.';}catch(e){message.textContent=e.message;}};card.append(button);}box.append(card);
}}
load().catch(e=>message.textContent=e.message);`;
const files={index,app,styles:read('../public-v3/styles.css'),entry,entryJs,feedback,feedbackJs,manage,manageJs};
writeFileSync(new URL('./assets.mjs',dir),'export const files = '+JSON.stringify(files)+';\n');

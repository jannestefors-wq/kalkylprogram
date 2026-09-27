const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let bootstrap = location.hash.startsWith("#test=") ? location.hash.slice(6) : sessionStorage.getItem("lmhm-v3-test");
if(bootstrap) sessionStorage.setItem("lmhm-v3-test",bootstrap);
let cfg, state, revision, section="direction", pending, queue=Promise.resolve(), blocked=false, dirty=false;
let focusMode=null, renderedSection=null, renderedDay=null;
const status = text => { $("#status").textContent=text; };
const uid = () => crypto.randomUUID();
async function api(path,body) {
  const response=await fetch("/api/v3/"+path,{method:body?"POST":"GET",headers:body?{"Content-Type":"application/json"}:{},body:body?JSON.stringify(body):undefined});
  const result=await response.json();
  if(!response.ok) { const error=new Error(result.error);error.status=response.status;throw error; }
  return result;
}
function target() { return cfg.person.role==="participant"?"":"?participant="+($("#participant")?.value || "v3_alex"); }
async function refresh() { const r=await api("state"+target());state=r.state;revision=r.revision; }
function send(event) {
  const operation=queue.then(async()=>{
    if(blocked) throw new Error("Sparandet är pausat. Kopiera din text innan du hämtar senaste versionen.");
    const r=await api("event",{baseRevision:revision,event});
    state=r.state; revision=r.revision; dirty=false; status("Sparat · privat om du inte valt att dela");
  });
  queue=operation.catch(e=>{
    blocked=e.status===409 || !e.status || e.status>=500;
    dirty=true;
    status(e.status?e.message:"Det gick inte att spara. Texten är kvar. Kontrollera anslutningen och försök igen.");
    if(blocked && e.status!==409) {
      const retry=document.createElement("button");
      retry.textContent="Försök spara igen";
      retry.onclick=async()=>{
        blocked=false;
        try {
          if(pending) await flush();
          else await send(event);
        } catch(error) { status(error.message); }
      };
      $("#status").append(" ",retry);
    }
  });
  return operation;
}
async function flush() {
  if(pending) { const fn=pending;pending=null;clearTimeout(timer); await fn(); }
  await queue;
  if(blocked) throw new Error("Din osparade text finns kvar. Kopiera den och öppna testvyn igen för att hämta senaste versionen.");
}
let timer;
window.addEventListener("beforeunload",e=>{if(dirty || pending){e.preventDefault();e.returnValue="";}});
$("#login").onclick=async()=>{
  try {
    if(dirty && !confirm("Det finns osparad text. Har du kopierat den innan du öppnar testvyn igen?")) return;
    clearTimeout(timer);pending=null; await queue;
    await api("login",{bootstrap,person:$("#person").value});
    cfg=await api("config");blocked=false;dirty=false;
    $("#identity").textContent=cfg.person.name;
    $("#clock-wrap").hidden=cfg.person.role!=="participant";
    if(cfg.person.role==="participant") {
      await refresh();$("#clock").value=state.day;
      section="direction"; focusMode=null; renderedSection=null; render();
    } else { await renderRole(); }
    status("");
  }catch(e){if(!blocked)status(e.message);}
};
$("#clock").onchange=async()=>{
  try { await flush();await send({type:"clock",day:Number($("#clock").value)});render(); }
  catch(e){if(!blocked)status(e.message);}
};
function share(target) {
  const shared=state.shares.includes(target);
  return '<button type="button" data-share="'+esc(target)+'" data-enabled="'+!shared+'">'+(shared?"Återkalla delning":"Dela med Jan")+'</button><small> '+(shared?"Jan ser detta moment och fortsatta ändringar tills du återkallar.":"Bara detta moment delas om du väljer det.")+'</small>';
}
function record(value) {
  if(!value) return '<p class="muted">Inget sparat ännu.</p>';
  const data=value.data || value;
  const labels=Object.fromEntries(Object.values(cfg.fields).flat());
  return Object.entries(data).filter(([k,v])=>labels[k] && typeof v==="string" && v).map(([k,v])=>'<p><strong>'+esc(labels[k])+'</strong><br>'+esc(v)+'</p>').join("");
}
function form(kind,id,value={},submit="Spara",type="note") {
  const draft=state.drafts[id]?.data;
  const data=draft || value;
  const fields=cfg.fields[kind].filter(([key])=>kind!=="focus" || (type==="keep" ? key==="reason" : key!=="reason" || state.focus.length>0));
  return '<form data-kind="'+kind+'" data-id="'+id+'" data-type="'+type+'">'+fields.map(([k,label])=>{
    let hidden=kind==="outcome" && ((k==="blocked" && data.result!=="Nej") || (["happened","evidence"].includes(k) && data.result==="Nej"));
    const control=k==="result"?'<select name="result" id="'+id+'-'+k+'"><option value="">Välj</option>'+["Ja","Delvis","Nej"].map(v=>'<option'+(data[k]===v?" selected":"")+'>'+v+'</option>').join("")+'</select>':'<textarea id="'+id+'-'+k+'" name="'+k+'" maxlength="8000" rows="2">'+esc(data[k])+'</textarea>';
    return '<div data-field="'+k+'"'+(hidden?" hidden":"")+'><label for="'+id+'-'+k+'">'+esc(k==="reason" ? (type==="keep" ? "Vill du skriva något om varför? (frivilligt)" : "Varför byter jag fokus?") : label)+'</label>'+control+'</div>';
  }).join("")+'<button class="primary" type="submit">'+submit+'</button><p class="muted"><small>Texten sparas medan du skriver. '+(type==="note"?"Privat som standard.":"Knappen bekräftar ditt val.")+'</small></p></form>';
}
function note(kind,id) { return form(kind,id,state.notes[id]?.data || {}) + (state.notes[id] && kind!=="cotrainer"?share("note:"+id):""); }
function books() {
  const list=items=>items.map(x=>'<div class="book"><strong>'+esc(x.title)+'</strong> · s. '+esc(x.pages)+(x.note?'<br><small>'+esc(x.note)+'</small>':'')+'</div>').join("");
  return '<details><summary>Boken som stöd</summary><p>'+esc(cfg.bookNote)+'</p><h3>Gemensam grund</h3><p>Läs i små delar för ett gemensamt språk. Stanna där det hjälper. Du behöver inte läsa allt före nästa samtal eller Runda bordet.</p>'+list(cfg.book.foundation)+'<h3>När du vill förstå din situation bättre</h3><p>Välj ett avsnitt som hjälper dig med situationen du står i. Jan kan också ge en läshänvisning.</p>'+list(cfg.book.cases)+(state.recommendations?.length?'<h3>Jan har pekat på</h3>'+list(cfg.book.optional.filter(x=>state.recommendations.includes(x.title))):"")+'<details><summary>Frivillig fördjupning</summary><p>I egen takt, utan kalenderkrav.</p>'+list(cfg.book.optional)+'</details></details>';
}
function thinking() {
  return '<details><summary>När du vill undersöka lite djupare</summary><div class="corners">'+cfg.corners.map(x=>'<span>'+x+'</span>').join("")+'</div><p>'+esc(cfg.feeling)+'</p><p>Vad vet du? Vad tolkar du? Varför tror du att det händer? Är detta rätt problem?</p><p>Mät · Korrigera · Mät igen: se vad som händer, ompröva och välj nästa försök. Inget här behöver fyllas i.</p></details>';
}
function mirror(round) {
  const answers=state.mirrors.filter(x=>x.round===round);
  return '<details><summary>Spegeln '+round+'</summary><p>Perspektiv och observationer hjälper dig att förstå. Det är inte betyg eller diagnos. Alla svar här är påhittade. Ingen kontaktas.</p><p>Du läser svaren. Jan ser inget automatiskt. Du kan dela valda svar eller en egen sammanfattning och återkalla delningen. Admin ser bara status. Relationsrollen kan göra en verklig svarande identifierbar; anonymitet utlovas inte.</p><p class="muted">Riktiga svar och lagringstider kräver separat integritetsgranskning före användning.</p>'+
    (!answers.length?'<button data-mirror="'+round+'">Visa syntetiska svar · Spegeln '+round+'</button>':answers.map(a=>'<details><summary>'+esc(a.relation)+' · syntetiskt perspektiv</summary>'+a.answers.map((x,i)=>'<p><strong>'+esc(cfg.mirror[round][i])+(round===1 && i===5?" (frivillig)":"")+'</strong><br>'+esc(x || "Inget svar")+'</p>').join("")+share("mirror:"+a.id)+'</details>').join(""))+
    '<h3>Min egen sammanfattning</h3>'+note("summary","summary-"+round)+'</details>';
}
function render() {
  if(!cfg || cfg.person.role!=="participant") return;
  const sameView=renderedSection===section && renderedDay===state.day;
  const openDetails=new Set(sameView ? [...document.querySelectorAll("#app details[open]")].map(x=>x.querySelector(":scope > summary")?.textContent) : []);
  if(!sameView) focusMode=null;
  renderedSection=section; renderedDay=state.day;
  $("#nav").innerHTML=cfg.surfaces.map(([id,title])=>'<a href="#'+id+'" data-nav="'+id+'"'+(section===id?' aria-current="page"':'')+'>'+esc(title)+'</a>').join("");
  const [id,title,intro]=cfg.surfaces.find(x=>x[0]===section);
  const focus=state.focus.find(x=>x.active);
  let html='<p class="eyebrow">Mitt privata arbetsrum</p><h1>'+esc(title)+'</h1><p class="intro">'+esc(id==="direction" && state.day<0 ? "Börja med det du vill förstå. Spegeln och samtalet med Jan kan hjälpa dig att se tydligare innan du väljer fokus." : intro)+'</p>';
  if(id==="direction") {
    if(state.day<0) html+='<div class="card"><h2>Före start</h2><p>Se vad du vill förstå bättre. Spegeln kan ge perspektiv, men du kan alltid gå vidare till Start 1:1 med det underlag du har.</p>'+mirror(1)+'<a href="#talk" data-nav="talk">Förbered Start 1:1</a></div>';
    if(focus) html+='<div class="card"><h2>Mitt primära fokus</h2>'+record(focus)+share("focus:"+focus.id)+'</div>';
    if(!focus && state.day<0) html+='<p>Förstå först → samtal → välj fokus. Efter Start 1:1 blir fokusvalet nästa steg. Spegel-svar är inget krav för samtalet.</p>';
    else if(!focus) html+=form("focus","focus",{},"Välj detta fokus","focus");
    else {
      html+='<h2>Ompröva mitt fokus</h2><p>Att byta fokus kan vara ett tecken på att du förstått problemet bättre.</p><div class="row"><button data-focus-mode="keep">Behåll mitt fokus</button><button data-focus-mode="change">Jag behöver byta fokus</button></div>';
      if(focusMode==="keep") html+=form("focus","keep-focus",{},"Bekräfta: behåll mitt fokus","keep");
      if(focusMode==="change") html+=form("focus","focus",{},"Välj detta fokus","focus");
    }
    html+='<details><summary>Tidigare fokus och omprövningar</summary>'+state.focus.map(x=>'<div class="record">'+record(x)+'<small>'+(x.active?"Nuvarande fokus":"Tidigare fokus")+'</small></div>').join("")+state.reviews.map(x=>'<p>Behöll fokus: '+esc(x.reason || "Ingen anteckning")+'</p>').join("")+'</details>'+books();
  }
  if(id==="action") html+='<div class="card"><h2>Det jag arbetar med nu</h2><p>'+esc(focus?.title || (state.day<0?"Börja med det du vill förstå och samtalet med Jan. Därefter väljer du fokus och vad du vill prova.":"Välj ett primärt fokus i Min riktning först."))+'</p></div>'+(focus?form("action","action",{},"Lägg till handling","action"):(state.day<0?'<a data-nav="talk" href="#talk">Förbered Start 1:1</a>':'<a data-nav="direction" href="#direction">Till Min riktning</a>'))+'<details><summary>Mina tidigare handlingar</summary>'+state.actions.map(x=>'<div class="record">'+record(x)+share("action:"+x.id)+'</div>').join("")+'</details>';
  if(id==="outcome") html+=!state.actions.length?'<p>När du valt en handling kan du komma tillbaka hit och se vad som hände.</p><a data-nav="action" href="#action">Välj vad jag provar</a>':state.actions.slice().reverse().map((x,i)=>'<details'+(i===0?" open":"")+'><summary>'+esc(x.what)+'</summary><p>'+esc(x.situation)+' · '+esc(x.when)+'</p>'+form("outcome","outcome-"+x.id,x.outcome || {},"Spara vad som hände","outcome")+share("action:"+x.id)+'</details>').join("")+thinking()+'<p><a href="#direction" data-nav="direction">Ompröva: behåll eller byt fokus</a></p>';
  if(id==="reflection") html+='<p>Förstå först. Skriv sedan. Något du upptäcker blir inte automatiskt ett nytt fokus. Du kan också skriva en fråga att ta med till Jan eller Runda bordet.</p>'+note("reflection","reflection")+thinking();
  if(id==="round") {
    const completed=cfg.rounds.filter(x=>x.day<state.day);
    const latest=completed.at(-1);
    const selected=completed.find(x=>sameView && x.id===$("#round-select")?.value) || latest;
    const next=cfg.rounds.find(x=>x.day>=state.day);
    html+='<div class="card"><h2>Nästa träff</h2>'+(next?roundInfo(next):'<p>De planerade träffarna har passerat i testtiden.</p>')+'</div><details><summary>Alla träffar</summary>'+cfg.rounds.map(roundInfo).join("")+'</details>';
    html+='<h2>Efter Runda bordet</h2>';
    if(!latest) html+='<p>Efter din första träff finns här plats för en frivillig privat tanke. Just nu kan du fundera på vad du vill ta med till samtalet.</p>';
    else html+='<p>Frivilligt och bara för dig. En tanke räcker.</p><label for="round-select">Träff</label><select id="round-select">'+completed.map(x=>'<option value="'+x.id+'"'+(x.id===selected.id?' selected':'')+'>'+x.title+'</option>').join("")+'</select><div id="cotrainer-form">'+note("cotrainer","cotrainer-"+selected.id)+'</div>';
  }
  if(id==="talk") {
    const relevant=state.day>=134?"three":state.day>=42?"end":state.day>=21?"middle":"start";
    html+=cfg.talks.map(t=>'<details data-talk="'+t.id+'"'+(t.id===relevant?" open":"")+'><summary>'+t.title+'</summary><p>Cirka '+t.minutes+' minuter är ett riktvärde. Samtalet får följa människan.</p>'+(t.id==="start"?'<p>Vad skaver? Vad tror du är problemet? Vad har du sett i Spegeln? Vad vill du förstå? Skriv bara det som hjälper.</p>':"")+(t.id==="three" && state.day<134?'<p>Här kan du läsa frågorna inför tre månader. Anteckningsytan öppnas vid tremånadersuppföljningen.</p>'+cfg.fields.talk.map(([,label])=>'<p>'+esc(label)+'</p>').join(""):note("talk","talk-"+t.id))+(t.id==="start" && state.day>=0?'<p><a data-nav="direction" href="#direction">Vad är mitt primära fokus nu?</a></p><p><a data-nav="action" href="#action">Vad ska jag prova först?</a></p>':"")+'</details>').join("");
  }
  if(id==="journey") {
    html+='<p>'+esc(cfg.resultNote)+'</p>'+mirror(1)+'<details><summary>Fokus och handlingar över tid</summary>'+state.focus.map(f=>'<div class="record">'+record(f)+state.actions.filter(x=>x.focusId===f.id).map(x=>'<div class="card">'+record(x)+record(x.outcome)+'</div>').join("")+'</div>').join("")+'</details>';
    if(state.day>=72) html+='<h2>30 dagar · Vad blev faktiskt kvar?</h2><div class="card"><h3>Vid kärnresans slut</h3>'+record(state.coreEnd?.focus)+'<h3>Sista handlingen</h3>'+record(state.coreEnd?.action)+'<p>Det jag tänkte fortsätta göra: '+esc(state.coreEnd?.next || "Ingen anteckning")+'</p></div>'+note("d30","d30")+'<p><a data-nav="round" href="#round">Runda bordet Återträff</a></p>';
    else html+='<p class="muted">Här möter du uppföljningen 30 dagar efter kärnresans slut.</p>';
    if(state.day>=134) html+='<h2>Tre månader · då och nu</h2><p>Jämför ditt ursprungliga fokus, fokusbyten, handlingar, 30 dagar och Spegeln 1 med det du ser nu.</p>'+mirror(2)+note("three","three")+'<a data-nav="talk" href="#talk">Till 3-månaders 1:1</a>';
    html+='<details><summary>Privat sparhistorik</summary><p>Tidigare sparade versioner av din resa. Bara du kan läsa dem.</p><button id="history">Visa tidigare versioner</button><div id="history-list"></div></details>';
  }
  $("#app").innerHTML=html;
  for(const detail of document.querySelectorAll("#app details")) if(openDetails.has(detail.querySelector(":scope > summary")?.textContent)) detail.open=true;
  bind();
}
function roundInfo(x) { return '<div class="record"><h3>'+esc(x.title)+'</h3><p>'+new Intl.DateTimeFormat("sv-SE",{dateStyle:"long",timeStyle:"short",timeZone:"Europe/Stockholm"}).format(new Date(x.startsAt))+' · '+esc(x.duration)+'</p><p>'+esc(x.preparation)+'</p><small>Testträff. Ingen riktig möteslänk eller extern anslutning.</small></div>'; }
function bindForms() {
  document.querySelectorAll("form").forEach(f=>{
    const data=()=>Object.fromEntries(new FormData(f));
    const event=()=>({type:f.dataset.type,kind:f.dataset.kind,id:f.dataset.type==="outcome"?f.dataset.id.slice(8):f.dataset.type==="note"?f.dataset.id:uid(),data:data()});
    const saveDraft=()=>{
      const e=f.dataset.type==="note"?event():{type:"draft",kind:f.dataset.kind,id:f.dataset.id,data:data()};
      return send(e).catch(e=>{if(!blocked)status(e.message);});
    };
    f.oninput=()=>{
      dirty=true;status("Sparar…");
      if(f.dataset.kind==="outcome") {
        const no=f.elements.result.value==="Nej";
        f.querySelector('[data-field="blocked"]').hidden=!no;
        for(const k of ["happened","evidence"]) f.querySelector('[data-field="'+k+'"]').hidden=no;
      }
      // Flush the previous form before replacing its pending save.
      if(pending && pending.form!==f) { pending(); }
      clearTimeout(timer);pending=saveDraft;pending.form=f;
      timer=setTimeout(()=>{const fn=pending;pending=null;if(fn) fn();},650);
    };
    f.onsubmit=async e=>{
      e.preventDefault();
      try { await flush();await send(event());if(["focus","keep"].includes(f.dataset.type)) focusMode=null;render(); }
      catch(e){if(!blocked)status(e.message);}
    };
  });
}
function bind() {
  bindForms();
  document.querySelectorAll("[data-nav]").forEach(a=>a.onclick=async e=>{e.preventDefault();try{await flush();section=a.dataset.nav;render();$("#app").focus();}catch(e){if(!blocked)status(e.message);}});
  document.querySelectorAll("[data-share]").forEach(b=>b.onclick=async()=>{try{await flush();await send({type:"share",target:b.dataset.share,enabled:b.dataset.enabled==="true"});render();}catch(e){if(!blocked)status(e.message);}});
  document.querySelectorAll("[data-mirror]").forEach(b=>b.onclick=async()=>{try{await flush();await send({type:"mirror",round:Number(b.dataset.mirror)});render();}catch(e){if(!blocked)status(e.message);}});
  document.querySelectorAll("[data-focus-mode]").forEach(button=>button.onclick=async()=>{try{await flush();focusMode=button.dataset.focusMode;render();}catch(e){if(!blocked)status(e.message);}});
  if($("#round-select")) $("#round-select").onchange=async()=>{try{await flush();$("#cotrainer-form").innerHTML=note("cotrainer","cotrainer-"+$("#round-select").value);bindForms();}catch(e){if(!blocked)status(e.message);}};
  if($("#history")) $("#history").onclick=async()=>{try{await flush();const h=await api("history");$("#history-list").innerHTML=h.map(x=>'<details><summary>'+esc(new Date(x.created_at).toLocaleString("sv-SE"))+' · sparning '+x.revision+'</summary>'+x.value.focus.map(record).join("")+x.value.actions.map(a=>record(a)+record(a.outcome)).join("")+Object.values(x.value.notes).map(record).join("")+'</details>').join("") || "<p>Ingen tidigare sparning.</p>";}catch(e){if(!blocked)status(e.message);}};
}
async function renderRole() {
  $("#nav").innerHTML="";
  if(cfg.person.role==="employer") {$("#app").innerHTML="<h1>Ingen individuell läsväg</h1><p>Arbetsgivare kan inte läsa deltagarens resa.</p>";return;}
  $("#app").innerHTML='<h1>'+(cfg.person.role==="facilitator"?"Delat med Jan":"Programstatus")+'</h1><label for="participant">Syntetisk deltagare</label><select id="participant">'+cfg.people.filter(x=>x.role==="participant").map(x=>'<option value="'+x.id+'">'+esc(x.name)+'</option>').join("")+'</select><div id="role-content"></div>';
  const show=async()=>{
    await refresh();
    if(cfg.person.role==="program_admin") $("#role-content").innerHTML=state.mirrors.map(x=>'<div class="card"><h2>Spegeln '+x.round+'</h2><p>'+(x.started?"Startad":"Inte startad")+' · '+x.count+' syntetiska svar · '+(x.ready?"klar":"inte klar")+'</p></div>').join("");
    else {
      $("#role-content").innerHTML='<p>Här finns bara moment som deltagaren aktivt delat. Privat material, utkast och historik är inte åtkomliga.</p>'+state.shared.map(x=>'<div class="card">'+(x.value.answers?'<h2>Delat Spegel-perspektiv · '+esc(x.value.relation)+'</h2>'+x.value.answers.map((a,i)=>'<p><strong>'+esc(cfg.mirror[x.value.round][i])+'</strong><br>'+esc(a)+'</p>').join(""):record(x.value)+(x.value.outcome?record(x.value.outcome):""))+'</div>').join("")+'<details><summary>Kompass, inte manus.</summary><p>'+esc(cfg.compassNote)+'</p>'+cfg.compass.map(x=>'<p>'+esc(x)+'</p>').join("")+'<p>Stoppa snabba lösningar, antaganden som fakta och etiketter på människor. Systemstödet drar aldrig slutsatsen åt Jan.</p></details><details><summary>Rekommendera ett verifierat bokavsnitt</summary><select id="book-choice">'+cfg.book.optional.map(x=>'<option>'+esc(x.title)+'</option>').join("")+'</select><button id="recommend">Ge läshänvisning</button></details>';
      $("#recommend").onclick=async()=>{try{const r=await api("recommend"+target(),{baseRevision:revision,title:$("#book-choice").value});revision=r.revision;status("Läshänvisningen är sparad.");}catch(e){if(!blocked)status(e.message);}};
    }
  };
  $("#participant").onchange=()=>show().catch(e=>{if(!blocked)status(e.message);});
  await show();
}
if(bootstrap) $("#login").click();

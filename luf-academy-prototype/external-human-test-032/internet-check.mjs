import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
if(process.stdin.isTTY)process.stdin.setRawMode(true);
process.stdout.write('Ready for private test input (hidden).\n');
const input=await new Promise(resolve=>{let text='';process.stdin.on('data',chunk=>{text+=chunk.toString();if(/[\r\n]/.test(text)){process.stdin.pause();resolve(JSON.parse(text.trim()));}});process.stdin.resume();});
const {base,tokens,finalCheck=false}=input;
let stage='start';
const request=async(cookie,path,body)=>fetch(base+'/api/v3/'+path,{method:body?'POST':'GET',headers:{cookie:cookie||'',Origin:base,'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});
const loginApi=async i=>{const r=await request('','login',{token:tokens[i]});assert.equal(r.status,200);return r.headers.get('set-cookie').split(';')[0];};
let browser,debugPage;
try{
 stage='public access and headers';
 const entry=await fetch(base+'/human-test');assert.equal(entry.status,200);assert.match(entry.headers.get('x-robots-tag'),/noindex/);
 assert.match(await(await fetch(base+'/robots.txt')).text(),/Disallow: \//);
 for(const path of ['human-test','app.js','entry.js','feedback.js','manage.js']){const html=await(await fetch(base+'/'+path)).text();for(const token of tokens)assert.ok(!html.includes(token));}
 assert.equal((await request('','state')).status,401);
 const jan=await loginApi(10),admin=await loginApi(11);
 if(finalCheck){
   stage='all ten final links';
   for(let i=0;i<10;i++){const cookie=await loginApi(i);const cfg=await(await request(cookie,'config')).json();assert.equal(cfg.person.id,'test'+String(i+1).padStart(2,'0'));assert.equal(cfg.people.length,1);const s=await(await request(cookie,'state')).json();assert.equal(s.state.focus.length,0);await request(cookie,'logout',{});}
   const slots=await(await request(jan,'manage')).json();assert.equal(slots.length,10);assert.ok(slots.every(x=>!x.revoked&&!x.feedback));
   console.log('PASS: final ten isolated links, empty journeys, Jan access, noindex and source checks');
 }else{
   for(const id of ['test01','test02'])assert.equal((await request(jan,'manage',{id,action:'reset'})).status,200);
   browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
   for(const width of [1280,390]){
    stage='browser '+width;
    const a=await browser.newContext({viewport:{width,height:900}}),b=await browser.newContext({viewport:{width,height:900}});
    const pa=await a.newPage(),pb=await b.newPage(),errors=[];debugPage=pa;
    for(const page of [pa,pb])page.on('pageerror',e=>errors.push(e.message));
    const login=async(page,i)=>{stage='login '+i+' at '+width;await page.goto(base+'/human-test#invite='+tokens[i]);await page.getByRole('button',{name:'Jag förstår – börja testa'}).click();await page.getByRole('heading',{name:'Min riktning',exact:true}).waitFor();assert.ok(!page.url().includes(tokens[i]));};
    const nav=async id=>{await pa.locator('#nav [data-nav="'+id+'"]').click();await pa.locator('#nav [data-nav="'+id+'"][aria-current=page]').waitFor();};
    const fill=async(id,key,value)=>pa.locator('form[data-id="'+id+'"] [name="'+key+'"]').fill(value);
    const submit=async(id,type)=>{const done=pa.waitForResponse(r=>r.url().includes('/event')&&r.request().postDataJSON()?.event?.type===type&&r.status()===200);await pa.locator('form[data-id="'+id+'"] button[type=submit]').click();await done;};
    await login(pa,0);stage='clock '+width;
    const clock=pa.waitForResponse(r=>r.url().includes('/event')&&r.request().postDataJSON()?.event?.type==='clock'&&r.status()===200);await pa.locator('#clock').selectOption('0');await clock;
    stage='focus '+width;await fill('focus','title','032 FIKTIVT fokus A');await submit('focus','focus');
    await nav('action');await fill('action','what','Fråga före råd');await fill('action','situation','Fiktivt möte');await fill('action','when','Nu');await submit('action','action');
    await nav('outcome');const form=pa.locator('form[data-kind=outcome]').first(),id=await form.getAttribute('data-id');await form.locator('select').selectOption('Ja');await fill(id,'happened','Fiktivt svar');await submit(id,'outcome');
    await login(pb,1);
    const other=await pb.evaluate(async()=>({state:(await fetch('/api/v3/state?participant=test01')).status,manage:(await fetch('/api/v3/manage')).status,people:(await(await fetch('/api/v3/config')).json()).people.length}));
    assert.deepEqual(other,{state:404,manage:403,people:1});assert.ok(!(await pb.locator('main').innerText()).includes('032 FIKTIVT'));
    await pa.reload();await pa.locator('#app > .card p').filter({hasText:'032 FIKTIVT fokus A'}).first().waitFor();
    await pa.locator('#logout').click();await pa.getByRole('heading',{name:'Välkommen till Human Test'}).waitFor();await login(pa,0);
    await pa.locator('#app > .card p').filter({hasText:'032 FIKTIVT fokus A'}).first().waitFor();
    const state=await pa.evaluate(async()=>await(await fetch('/api/v3/state')).json());assert.equal(state.state.actions[0].outcome.result,'Ja');
    await pa.locator('#feedback-link').click();await pa.locator('#q0').fill('032 syntetisk feedback');await pa.getByRole('button',{name:'Spara feedback'}).click();await pa.getByText('Feedbacken är sparad.',{exact:true}).waitFor();
    await pb.locator('#feedback-link').click();assert.equal(await pb.locator('#q0').inputValue(),'');
    const slots=await(await request(jan,'manage')).json();assert.equal(slots[0].feedback[0],'032 syntetisk feedback');
    assert.equal((await request(admin,'manage')).status,403);
    assert.ok(!JSON.stringify(await(await request(jan,'state?participant=test01')).json()).includes('032 FIKTIVT'));
    assert.ok(!JSON.stringify(await(await request(admin,'state?participant=test01')).json()).includes('032 FIKTIVT'));
    assert.deepEqual(errors,[]);
    for(const id of ['test01','test02'])assert.equal((await request(jan,'manage',{id,action:'reset'})).status,200);
    await a.close();await b.close();console.log('PASS: internet '+width+'px, A focus/action/outcome, B isolation, reload/relogin, feedback, roles and reset');
   }
   stage='revoked temporary verifier';
   const verifier=await loginApi(9);assert.equal((await request(jan,'manage',{id:'verify032',action:'delete'})).status,200);
   assert.equal((await request(verifier,'state')).status,401);assert.equal((await request('','login',{token:tokens[9]})).status,403);
   console.log('PASS: revoked link and existing session denied, verifier data deleted');
 }
 await request(jan,'logout',{});await request(admin,'logout',{});
}catch(e){if(debugPage)console.log(await debugPage.locator('body').innerText());console.error('FAIL at '+stage+': '+tokens.reduce((m,t)=>m.split(t).join('[redacted]'),e.message));process.exitCode=1;}finally{await browser?.close();}

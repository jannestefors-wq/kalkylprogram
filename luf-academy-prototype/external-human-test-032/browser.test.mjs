
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fixture,serve} from './test-helper.mjs';
const {chromium}=createRequire(import.meta.url)('playwright');
for(const width of [1280,390])test('032 browser: isolated invites, reload, logout, feedback and roles '+width,async()=>{
 const f=await fixture(),server=await serve(f.env),browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const a=await browser.newContext({viewport:{width,height:900}}),b=await browser.newContext({viewport:{width,height:900}});
  const pa=await a.newPage(),pb=await b.newPage(),errors=[];
  pa.on('pageerror',e=>errors.push(e.message));pb.on('pageerror',e=>errors.push(e.message));
  async function login(page,i){await page.goto(server.base+'/human-test#invite='+f.tokens[i]);await page.getByRole('button',{name:'Jag förstår – börja testa'}).click();await page.getByRole('heading',{name:'Min riktning',exact:true}).waitFor();}
  await login(pa,0);
  assert.equal(await pa.locator('#person').count(),0);
  assert.ok(!pa.url().includes(f.tokens[0]));
  const nav=async(page,id)=>{await page.locator('#nav [data-nav="'+id+'"]').click();await page.locator('#nav [data-nav="'+id+'"][aria-current=page]').waitFor();};
  async function submit(page,id,type){const done=page.waitForResponse(r=>r.url().includes('/event')&&r.request().postDataJSON()?.event?.type===type&&r.status()===200);await page.locator('form[data-id="'+id+'"] button[type=submit]').click();await done;}
  const fill=async(id,name,value)=>pa.locator('form[data-id="'+id+'"] [name="'+name+'"]').fill(value);
  const clockDone=pa.waitForResponse(r=>r.url().includes('/event')&&r.request().postDataJSON()?.event?.type==='clock'&&r.status()===200);
  await pa.locator('#clock').selectOption('0');await clockDone;
  await fill('focus','title','TEST A privat fokus');await submit(pa,'focus','focus');
  await nav(pa,'action');await fill('action','what','Fråga före råd');await fill('action','situation','Fiktivt möte');await fill('action','when','Nu');await submit(pa,'action','action');
  await nav(pa,'outcome');const form=pa.locator('form[data-kind=outcome]').first(),id=await form.getAttribute('data-id');await form.locator('select').selectOption('Ja');await fill(id,'happened','Jag väntade på svaret');await submit(pa,id,'outcome');
  await login(pb,1);assert.ok(!(await pb.locator('main').innerText()).includes('TEST A'));
  assert.equal(await pb.locator('form[data-kind=focus]').count(),0);
  const check=await pb.evaluate(async()=>({other:(await fetch('/api/v3/state?participant=test01')).status,manage:(await fetch('/api/v3/manage')).status,people:(await (await fetch('/api/v3/config')).json()).people.length}));
  assert.deepEqual(check,{other:404,manage:403,people:1});
  await pa.reload();await pa.locator('#app > .card p').filter({hasText:'TEST A privat fokus'}).first().waitFor();
  await pa.locator('#logout').click();await pa.getByRole('heading',{name:'Välkommen till Human Test'}).waitFor();await login(pa,0);await pa.locator('#app > .card p').filter({hasText:'TEST A privat fokus'}).first().waitFor();
  await pa.route('**/api/v3/feedback',async route=>{if(route.request().method()==='GET')await new Promise(r=>setTimeout(r,1000));await route.continue();});await pa.locator('#feedback-link').click();await pa.locator('#q0').fill('Fiktiv feedback A');await pa.getByRole('button',{name:'Spara feedback'}).click();await pa.getByText('Feedbacken är sparad.',{exact:true}).waitFor();
  await pb.locator('#feedback-link').click();assert.equal(await pb.locator('#q0').inputValue(),'');
  assert.deepEqual(errors,[]);
  await a.close();await b.close();
 }finally{await browser.close();await server.close();f.sqlite.close();}
});

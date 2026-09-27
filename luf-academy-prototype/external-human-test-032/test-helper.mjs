
import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import {createServer} from 'node:http';
import {randomBytes} from 'node:crypto';
import {handle,identity,headers,hash} from './api.mjs';
import {files} from './assets.mjs';
export function adapter(sqlite){
 const prepare=sql=>({bind(...args){
  return {
   first:async()=>sqlite.prepare(sql).get(...args)||null,
   all:async()=>({results:sqlite.prepare(sql).all(...args)}),
   run:async()=>({meta:{changes:Number(sqlite.prepare(sql).run(...args).changes)}})
  };
 }});
 return {prepare,async batch(items){sqlite.exec('BEGIN IMMEDIATE');try{const r=[];for(const x of items)r.push(await x.run());sqlite.exec('COMMIT');return r;}catch(e){sqlite.exec('ROLLBACK');throw e;}}};
}
export async function fixture(){
 const sqlite=new DatabaseSync(':memory:');sqlite.exec(readFileSync(new URL('./schema.sql',import.meta.url),'utf8'));
 const tokens=Array.from({length:12},()=>randomBytes(32).toString('hex'));
 const catalog=await Promise.all(tokens.map(async(token,i)=>({id:i<10?'test'+String(i+1).padStart(2,'0'):i===10?'jan':'admin',name:i<10?'Testare '+String(i+1).padStart(2,'0'):i===10?'Jan':'Fredde',role:i<10?'participant':i===10?'facilitator':'program_admin',hash:await hash(token)})));
 const env={DB:adapter(sqlite),LMHM032_ACCESS:JSON.stringify(catalog)};
 return {env,sqlite,tokens,catalog};
}
export async function serve(env){
 const server=createServer(async(req,res)=>{
  try{
   const origin='http://'+req.headers.host,url=new URL(req.url,origin);
   let raw='';for await(const chunk of req)raw+=chunk;
   const request=new Request(url,{method:req.method,headers:req.headers,body:['GET','HEAD'].includes(req.method)?undefined:raw});
   let response;
   if(url.pathname.startsWith('/api/'))response=await handle(env,request);
   else{
    const map={'/human-test':['entry','text/html'],'/academy':['index','text/html'],'/app.js':['app','text/javascript'],'/styles.css':['styles','text/css'],'/entry.js':['entryJs','text/javascript'],'/feedback':['feedback','text/html'],'/feedback.js':['feedbackJs','text/javascript'],'/manage':['manage','text/html'],'/manage.js':['manageJs','text/javascript']};
    const item=map[url.pathname];
    response=item?new Response(files[item[0]],{headers:{...headers,'Content-Type':item[1]}}):new Response('Not found',{status:404});
   }
   res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));
  }catch{res.writeHead(500);res.end('Error');}
 });
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 return {base:'http://127.0.0.1:'+server.address().port,close:()=>new Promise(r=>server.close(r))};
}

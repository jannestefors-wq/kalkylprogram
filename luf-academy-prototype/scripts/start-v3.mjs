import { createServer } from "node:http";
import { mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { createV3App, openV3Db } from "../server/app-v3.mjs";
if (!process.argv.includes("--human-test")) throw new Error("Ange --human-test. Ingen produktionsstart finns.");
const dir = new URL("../data/v3-human-test/", import.meta.url);
mkdirSync(dir,{recursive:true});
const db=openV3Db(fileURLToPath(new URL("synthetic.sqlite",dir)));
const app=createV3App(db,{humanTest:true});
const server=createServer(app.handle);
server.listen(Number(process.env.V3_PORT || 3024),"127.0.0.1",()=>{
  console.log("Endast syntetisk Human Test. Ingen deployment.");
  console.log("http://127.0.0.1:"+server.address().port+"/#test="+app.bootstrap);
});
for(const signal of ["SIGINT","SIGTERM"]) process.on(signal,()=>server.close(()=>{db.close();process.exit(0);}));

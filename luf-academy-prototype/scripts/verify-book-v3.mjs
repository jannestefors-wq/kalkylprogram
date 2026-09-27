import { readFileSync } from "node:fs";
import { BOOK } from "../server/content-v3.mjs";
export function verifyBook(book,raw){
  const parts=raw.replaceAll("\r\n","\n").split(/\n=====PDFPAGE (\d+)=====\n/).slice(1),pdf={};
  for(let i=0;i<parts.length;i+=2) pdf[Number(parts[i])]=parts[i+1];
  const norm=s=>String(s).replace(/[”“"]/g,'"').replace(/\s+/g," ").trim();
  const toc=[];
  for(const line of (pdf[5] || "").split("\n")) {const m=line.match(/^(.+?)\s*\.{3,}\s*(\d+)\s*$/);if(m)toc.push({title:norm(m[1]),page:Number(m[2])});}
  const failures=[];
  for(const ref of Object.values(book).flat()){
    const chapter=toc.findIndex(x=>x.title===norm(ref.inChapter || ref.title));
    const [from,to=from]=ref.pages.split("–").map(Number);
    const [pf,pt=pf]=ref.pdfPages.split("–").map(Number);
    const text=norm(Array.from({length:Math.max(0,to-from+1)},(_,i)=>pdf[from+i+7] || "").join(" "));
    if(chapter<0 || from<toc[chapter]?.page || to>=(toc[chapter+1]?.page || 206) || pf!==from+7 || pt!==to+7 || !text) failures.push(ref.title+": sida eller kapitel");
    const headingText=ref.inChapter?text:norm(pdf[(toc[chapter]?.page || 0)+7] || "");
    for(const heading of ref.headings || [ref.title]) if(!headingText.includes(norm(heading))) failures.push(ref.title+": rubrik");
  }
  return failures;
}
if(process.argv[1]?.endsWith("verify-book-v3.mjs")){
  if(!process.env.LHM_BOOK_TXT) throw new Error("LHM_BOOK_TXT krävs.");
  const failures=verifyBook(BOOK,readFileSync(process.env.LHM_BOOK_TXT,"utf8"));
  console.log("V3 bokkontroll: "+Object.values(BOOK).flat().length+" hänvisningar, "+failures.length+" fel.");
  if(failures.length){console.error(failures.join("\n"));process.exitCode=1;}
}

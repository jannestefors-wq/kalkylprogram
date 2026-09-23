import { createServer } from "node:http";
import { mkdirSync } from "node:fs";
import { dirname } from "node:path";
import { openDb } from "./db.mjs";
import { createApp } from "./app.mjs";

const dbPath = process.env.LR_DB || "data/prototype.db";
mkdirSync(dirname(dbPath), { recursive: true });
const db = openDb(dbPath);
const app = createApp(db, {
  identityMode: process.env.LR_IDENTITY_MODE || "prototype-link",
  prototype: process.env.LR_PROTOTYPE !== "0",
  secureCookies: process.env.LR_SECURE_COOKIES === "1",
});

const port = Number(process.env.PORT || 4310);
const host = process.env.HOST || "127.0.0.1";
createServer((req, res) => app.handle(req, res)).listen(port, host, () => {
  console.log(`LUF Academy prototyp: http://${host}:${port}  (databas: ${dbPath})`);
});

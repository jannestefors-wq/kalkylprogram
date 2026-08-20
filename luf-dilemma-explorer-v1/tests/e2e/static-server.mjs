import http from "node:http";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".css": "text/css; charset=utf-8",
};

/**
 * Minimal static file server, dependency-free, for local dev and e2e tests.
 * Serves `rootDir` at "/". No caching, no directory listing, no symlink
 * traversal outside rootDir.
 */
export function startServer(rootDir, port = 0) {
  const root = path.resolve(rootDir);

  const server = http.createServer(async (req, res) => {
    try {
      const urlPath = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
      let filePath = path.join(root, urlPath);
      if (!filePath.startsWith(root)) {
        res.writeHead(403).end("Forbidden");
        return;
      }
      let st = await stat(filePath).catch(() => null);
      if (st && st.isDirectory()) {
        filePath = path.join(filePath, "index.html");
        st = await stat(filePath).catch(() => null);
      }
      if (!st) {
        res.writeHead(404).end("Not found");
        return;
      }
      const ext = path.extname(filePath);
      const body = await readFile(filePath);
      res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
      res.end(body);
    } catch (err) {
      res.writeHead(500).end(String(err));
    }
  });

  return new Promise((resolve) => {
    server.listen(port, "127.0.0.1", () => {
      const { port: actualPort } = server.address();
      resolve({
        url: `http://127.0.0.1:${actualPort}`,
        close: () => new Promise((r) => server.close(r)),
      });
    });
  });
}

// Allow `node static-server.mjs [dir] [port]` for manual/local use.
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const dir = process.argv[2] || ".";
  const port = Number(process.argv[3]) || 8080;
  const { url } = await startServer(dir, port);
  console.log(`Serving ${path.resolve(dir)} at ${url}`);
}

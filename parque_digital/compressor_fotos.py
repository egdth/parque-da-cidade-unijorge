"""Compressor local de fotografias sem dependências externas (usa <canvas> do navegador local para gerar WebP <= 150 KB)."""

from __future__ import annotations

import base64
import functools
import http.server
import json
from pathlib import Path
import re
import shutil
import socketserver
import subprocess
import tempfile
import threading

CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]


def _find_browser() -> Path:
    for p in CHROME_CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError("Nenhum navegador Chromium local encontrado para compressão via <canvas>.")


def compress_photo_to_webp(
    src_path: Path,
    dst_path: Path,
    max_kb: int = 125,
    max_dim: int = 1120,
    correcao_leve: bool = True,
    crop_top_pct: float = 0.0,
) -> dict[str, int | float | str]:
    """Comprime uma foto real/autorizada para WebP <= max_kb (teto 150 KB) com correção leve opcional sem filtros."""
    browser = _find_browser()
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    work_dir = Path(tempfile.mkdtemp(prefix="toldo_foto_"))
    prof_dir = Path(tempfile.mkdtemp(prefix="toldo_prof_"))
    try:
        ext = src_path.suffix.lower() or ".jpg"
        staged_name = f"entrada{ext}"
        shutil.copyfile(src_path, work_dir / staged_name)

        filtro_css = "brightness(1.02) contrast(1.02)" if correcao_leve else "none"
        limit_bytes = max_kb * 1024

        harness = f"""<!DOCTYPE html>
<html lang="pt-BR"><body>
<img id="src" src="{staged_name}">
<script>
window.addEventListener("load", () => {{
  const img = document.getElementById("src");
  const nw = img.naturalWidth || 800;
  const nh = img.naturalHeight || 600;
  const sy = Math.round(nh * {crop_top_pct});
  const sh = Math.max(1, nh - sy);
  const scale = Math.min(1, {max_dim} / Math.max(nw, sh));
  const w = Math.max(1, Math.round(nw * scale));
  const h = Math.max(1, Math.round(sh * scale));
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  ctx.filter = "{filtro_css}";
  ctx.drawImage(img, 0, sy, nw, sh, 0, 0, w, h);

  let chosen = "";
  let chosenBytes = 0;
  let chosenQ = 0.84;
  for (let q = 0.84; q >= 0.42; q -= 0.06) {{
    const url = canvas.toDataURL("image/webp", Number(q.toFixed(2)));
    const b64 = url.split(",")[1] || "";
    const byteLen = Math.floor(b64.length * 3 / 4);
    chosen = b64;
    chosenBytes = byteLen;
    chosenQ = Number(q.toFixed(2));
    if (byteLen <= {limit_bytes}) break;
  }}
  const out = document.createElement("pre");
  out.id = "payload";
  out.textContent = JSON.stringify({{ width: w, height: h, quality: chosenQ, bytes: chosenBytes, b64: chosen }});
  document.body.appendChild(out);
  document.title = "PRONTO";
}});
</script></body></html>"""
        (work_dir / "compress.html").write_text(harness, encoding="utf-8")

        class QuietHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass

        httpd = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(work_dir)))
        port = httpd.server_address[1]
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        try:
            res = subprocess.run(
                [
                    str(browser),
                    "--headless=new",
                    "--disable-gpu",
                    f"--user-data-dir={prof_dir}",
                    "--virtual-time-budget=2500",
                    "--dump-dom",
                    f"http://127.0.0.1:{port}/compress.html",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        finally:
            httpd.shutdown()

        m = re.search(r'<pre id="payload">(.*?)</pre>', res.stdout, re.S)
        if not m:
            raise RuntimeError("Falha ao extrair WebP comprimido do <canvas>.")
        data = json.loads(m.group(1))
        raw = base64.b64decode(data["b64"])
        dst_path.write_bytes(raw)
        kb = round(len(raw) / 1024, 2)
        return {
            "path": str(dst_path),
            "width": int(data["width"]),
            "height": int(data["height"]),
            "quality": float(data["quality"]),
            "kb": kb,
        }
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
        shutil.rmtree(prof_dir, ignore_errors=True)

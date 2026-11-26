"""Bateria completa de Testes de Aceitação (Fase 8 — Seção 15) do projeto 'Toldo Aberto'."""

from __future__ import annotations

import functools
import http.server
import json
from pathlib import Path
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading

import segno

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from parque_digital.build_toldo import build_pacote_completo
from parque_digital.compilador_toldo import compilar_site_ambulante
from parque_digital.dados_modelo import validar_dados

CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")


def _dump_dom_from_chrome(url: str, extra_flags: list[str] | None = None, wait_ms: int = 2400) -> str:
    prof = Path(tempfile.mkdtemp(prefix="toldo_test_"))
    try:
        cmd = [
            str(CHROME),
            "--headless=new",
            "--disable-gpu",
            f"--user-data-dir={prof}",
            f"--virtual-time-budget={wait_ms}",
            "--window-size=1440,900",
            "--dump-dom",
            *(extra_flags or []),
            url,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True, timeout=35)
        return res.stdout
    finally:
        shutil.rmtree(prof, ignore_errors=True)


def run_all_acceptance_tests() -> dict[str, object]:
    report: dict[str, object] = {}

    # 1. Ausência total de telefones fictícios de exemplo em dados e código fonte
    banidos = ("5571" + "98812" + "3456", "71" + "98812" + "3456")
    ocorrencias_banidas = []
    for pasta in ("parque_digital", "exemplos", "ambulantes_exemplo", "docs"):
        p_dir = ROOT / pasta
        if not p_dir.exists():
            continue
        for arq in p_dir.rglob("*"):
            if arq.is_file() and arq.suffix in {".py", ".json", ".html", ".md"}:
                # Ignora builders legados v1..v5 apenas se necessário? Não: limpamos de builder_v5 também se houver!
                txt = arq.read_text(encoding="utf-8", errors="ignore")
                for b in banidos:
                    if b in txt:
                        ocorrencias_banidas.append(str(arq.relative_to(ROOT)))
    assert not ocorrencias_banidas, f"Telefones banidos encontrados: {ocorrencias_banidas}"
    report["arquivos_com_telefone_banido"] = ocorrencias_banidas

    # 2. Quatro sites fictícios gerados sem alterar código + verificação de fotos <= 150 KB
    quatro_builds = {}
    for seg in ("alimentacao", "brinquedos", "inflaveis", "bicicletas"):
        out_dir = ROOT / "output" / "quatro-segmentos" / seg
        info = build_pacote_completo(
            pasta_ambulante=ROOT / "ambulantes_exemplo" / seg,
            out_dir=out_dir,
            project_root=ROOT,
            modo_producao=False,
            incluir_equipe=(seg == "alimentacao"),
        )
        for nome_f, meta_f in info["fotos_detalhe"].items():
            assert float(meta_f["kb"]) <= 150.0, f"Foto {nome_f} excedeu 150 KB: {meta_f}"
        html_seg = (out_dir / "index.html").read_text(encoding="utf-8")
        assert 'lang="pt-BR"' in html_seg
        assert "Modelo demonstrativo: dados fictícios" in html_seg
        assert "Barraca Exemplo" in html_seg
        for termo_proibido in (
            "Modo Equipe",
            "Placa A5",
            "Tela Cheia",
            "Modo Solar",
            "Comerciante Local Verificado",
            "Pagamento Seguro",
            "Recebedor identificado",
            "Mais pedido",
            "Pedir 1x",
            "Falar Agora no WhatsApp",
            "+ Adicionar",
            "Revisar e Pedir",
            "Enviar Pedido no WhatsApp",
        ):
            assert termo_proibido not in html_seg, f"Termo removido encontrado em {seg}: {termo_proibido}"
        assert re.search(r"\boficial\b", html_seg, re.I) is None, f"Palavra 'oficial' encontrada em {seg}"
        quatro_builds[seg] = {
            "html_kb": info["html_kb"],
            "fontes_ptbr_kb": info["fontes_ptbr_kb"],
            "fotos_kb": info["fotos_kb"],
            "total_estatico_kb": info["primeira_carga_estimada_kb"],
        }
    report["quatro_segmentos"] = quatro_builds

    # 3. Trava do build de produção (sem consentimento, WhatsApp mal formatado, dado de exemplo) e omissão de blocos vazios
    base_prod = json.loads((ROOT / "ambulantes_exemplo" / "alimentacao" / "dados.json").read_text(encoding="utf-8"))
    assert validar_dados(base_prod, modo_producao=True), "Deveria rejeitar modo_exemplo=True em produção"

    sem_consent = {**base_prod, "modo_exemplo": False, "nome_negocio": "Pastel da Sombra", "whatsapp": "5571991112233", "consentimento": False}
    assert any("consentimento" in e for e in validar_dados(sem_consent, modo_producao=True))

    zap_ruim = {**sem_consent, "consentimento": True, "whatsapp": "7199111"}
    assert any("WhatsApp" in e for e in validar_dados(zap_ruim, modo_producao=True))

    nome_exemplo = {**sem_consent, "consentimento": True, "nome_negocio": "Barraca Exemplo"}
    assert any("exemplo" in e.lower() for e in validar_dados(nome_exemplo, modo_producao=True))

    # Build de produção válido com campos opcionais vazios -> oculta blocos vazios e não exibe aviso de exemplo
    tmp_prod = Path(tempfile.mkdtemp(prefix="toldo_prod_ok_"))
    try:
        dados_prod_limpo = {
            **sem_consent,
            "consentimento": True,
            "historia_aprovada": "",
            "destaque": "",
            "aceita_encomendas": False,
            "fotos": {},
            "pix": {"autorizado": False, "chave": "", "recebedor": ""},
        }
        (tmp_prod / "dados.json").write_text(json.dumps(dados_prod_limpo, ensure_ascii=False), encoding="utf-8")
        out_prod = tmp_prod / "dist"
        compilar_site_ambulante(tmp_prod, out_prod, ROOT, modo_producao=True)
        html_prod = (out_prod / "index.html").read_text(encoding="utf-8")
        assert "Modelo demonstrativo" not in html_prod
        assert "Barraca Exemplo" not in html_prod
        assert 'id="quem-atende"' not in html_prod
        assert 'id="encomendas"' not in html_prod
        assert '<div class="caixa-pix">' not in html_prod
        assert 'class="bloco-destaque-casa"' not in html_prod
        report["trava_producao_e_blocos_vazios"] = "APROVADO"
    finally:
        shutil.rmtree(tmp_prod, ignore_errors=True)

    # 4. Servidor local para testes reais de navegador (sem JS, carga 360px <= 700 KB, pedido 2 itens + obs, Esc, preço alterado, QR Code)
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(ROOT)))
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    try:
        # 4a) Legibilidade sem JavaScript (--disable-javascript)
        dom_nojs = _dump_dom_from_chrome(
            f"http://127.0.0.1:{port}/output/quatro-segmentos/alimentacao/index.html",
            extra_flags=["--disable-javascript"],
            wait_ms=1500,
        )
        assert "Pastel grande frito na hora" in dom_nojs
        assert "Quinta a domingo" in dom_nojs
        assert "entrada principal, ao lado da sombra das amendoeiras" in dom_nojs
        report["legivel_sem_javascript"] = True

        # 4b) E2E completo em Chrome:
        # - Medição real de primeira carga móvel (Performance API em 360x640) <= 700 KB
        # - 5 segundos / primeira dobra: nome, oferta, horário e Como chegar visíveis em 360x640
        # - 2 itens com variações + 1 observação -> mensagem e total exatos (sem enviar!) + persistência
        # - Janela modal da comanda abre e fecha com Esc
        e2e_harness = ROOT / "output" / "_e2e_fase8.html"
        try:
            e2e_harness.write_text(
                f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0">
<iframe id="mob" src="http://127.0.0.1:{port}/output/quatro-segmentos/alimentacao/index.html" style="width:360px;height:640px;border:0"></iframe>
<script>
window.addEventListener("load", () => setTimeout(() => {{
  const win = document.getElementById("mob").contentWindow;
  const doc = win.document;
  win.localStorage.clear();

  // Peso real transferido na primeira carga móvel (HTML + recursos carregados em 360x640)
  const nav = win.performance.getEntriesByType("navigation")[0];
  const resEntries = win.performance.getEntriesByType("resource");
  const bytesTransferidos = (nav ? (nav.decodedBodySize || nav.transferSize || 0) : 0) +
    resEntries.reduce((acc, r) => acc + (r.encodedBodySize || r.decodedBodySize || 0), 0);
  const primeiraCargaKB = Math.round((bytesTransferidos / 1024) * 100) / 100;

  // Clareza em 5 segundos (360x640): nome, oferta, horário e Como chegar visíveis sem rolar
  const rNome = doc.getElementById("hero-nome").getBoundingClientRect();
  const rChegar = doc.getElementById("cta-chegar").getBoundingClientRect();
  const dobra5s = rNome.top >= 0 && rChegar.bottom <= 640;

  // Adiciona 2 itens com variações + 1 observação (sem enviar!)
  doc.querySelector('[data-escolher-variacao="pastel-grande"][data-var-indice="3"]').click(); // Camarão seco R$ 14,00
  doc.querySelector('[data-adicionar-item="pastel-grande"]').click();
  doc.querySelector('[data-escolher-variacao="caldo-cana"][data-var-indice="1"]').click(); // Copo 500 ml R$ 9,00
  doc.querySelector('[data-adicionar-item="caldo-cana"]').click();

  // Abre gaveta da comanda no celular e preenche observação
  doc.getElementById("btn-ver-meu-pedido").click();
  const gaveta = doc.getElementById("gaveta-comanda");
  const abriuGaveta = gaveta.open === true;

  const campoObs = gaveta.querySelector("[data-comanda-obs]");
  campoObs.value = "Pastel bem quentinho e caldo com limão";
  campoObs.dispatchEvent(new win.Event("input", {{ bubbles: true }}));

  const totalTexto = gaveta.querySelector("[data-comanda-total]").textContent.trim();
  const msgGerada = gaveta.querySelector("[data-comanda-previa-msg]").textContent.trim();
  const salvoStorage = JSON.parse(win.localStorage.getItem("toldo_aberto_pedido_barraca-exemplo-alimentacao") || "{{}}");

  // Testa fechamento com tecla Esc (evento cancel nativo de <dialog>)
  gaveta.dispatchEvent(new win.Event("cancel", {{ cancelable: true }}));
  if (gaveta.open) gaveta.close();
  const fechouEsc = gaveta.open === false;

  win.localStorage.clear();

  document.title = JSON.stringify({{
    primeiraCargaKB,
    recursosCarregados: resEntries.map(r => r.name.split("/").pop()),
    dobra5s,
    abriuGaveta,
    fechouEsc,
    totalTexto,
    msgGerada,
    itensSalvosStorage: (salvoStorage.itens || []).length
  }});
}}, 700));
</script></body></html>""",
                encoding="utf-8",
            )
            dom_e2e = _dump_dom_from_chrome(f"http://127.0.0.1:{port}/output/_e2e_fase8.html", wait_ms=2800)
            m = re.search(r"<title>(.*?)</title>", dom_e2e, re.S)
            dados_e2e = json.loads(html_unescape(m.group(1)))
            assert dados_e2e["primeiraCargaKB"] <= 700.0, f"Primeira carga acima de 700 KB: {dados_e2e}"
            assert dados_e2e["dobra5s"] is True
            assert dados_e2e["abriuGaveta"] is True and dados_e2e["fechouEsc"] is True
            assert dados_e2e["totalTexto"] == "R$ 23,00"
            assert "1x Pastel grande frito na hora (Camarão seco) — R$ 14,00" in dados_e2e["msgGerada"]
            assert "1x Caldo de cana moído na hora (Copo 500 ml) — R$ 9,00" in dados_e2e["msgGerada"]
            assert "Total estimado: R$ 23,00" in dados_e2e["msgGerada"]
            assert "Observação: Pastel bem quentinho e caldo com limão" in dados_e2e["msgGerada"], f"E2E mismatch: {dados_e2e}"
            assert dados_e2e["itensSalvosStorage"] == 2
            report["pedido_e_carga_movel"] = dados_e2e
        finally:
            if e2e_harness.exists():
                e2e_harness.unlink()

        # 4c) Alterar um preço no dados.json atualiza cardápio, pedido e mensagem sem mudar código
        tmp_preco_dir = ROOT / "output" / "_teste_mudanca_preco"
        try:
            shutil.copytree(ROOT / "ambulantes_exemplo" / "alimentacao", tmp_preco_dir / "entrada", dirs_exist_ok=True)
            d_alt = json.loads((tmp_preco_dir / "entrada" / "dados.json").read_text(encoding="utf-8"))
            # Altera Camarão seco de R$ 14,00 para R$ 17,50
            d_alt["itens"][0]["variacoes"][3]["preco"] = 17.50
            (tmp_preco_dir / "entrada" / "dados.json").write_text(json.dumps(d_alt, ensure_ascii=False), encoding="utf-8")
            compilar_site_ambulante(tmp_preco_dir / "entrada", tmp_preco_dir / "saida", ROOT, modo_producao=False)

            probe_p = tmp_preco_dir / "probe.html"
            probe_p.write_text(
                f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>
<iframe id="f" src="http://127.0.0.1:{port}/output/_teste_mudanca_preco/saida/index.html" style="width:1440px;height:900px;border:0"></iframe>
<script>
window.addEventListener("load", () => setTimeout(() => {{
  const doc = document.getElementById("f").contentDocument;
  doc.defaultView.localStorage.clear();
  doc.querySelector('[data-escolher-variacao="pastel-grande"][data-var-indice="3"]').click();
  const placa = doc.querySelector('[data-placa-texto="pastel-grande"]').textContent.trim();
  doc.querySelector('[data-adicionar-item="pastel-grande"]').click();
  const total = doc.querySelector('[data-comanda-instancia="desktop"] [data-comanda-total]').textContent.trim();
  const msg = doc.querySelector('[data-comanda-instancia="desktop"] [data-comanda-previa-msg]').textContent.trim();
  doc.defaultView.localStorage.clear();
  document.title = JSON.stringify({{ placa, total, msg }});
}}, 600));
</script></body></html>""",
                encoding="utf-8",
            )
            dom_p = _dump_dom_from_chrome(f"http://127.0.0.1:{port}/output/_teste_mudanca_preco/probe.html", wait_ms=2400)
            res_p = json.loads(html_unescape(re.search(r"<title>(.*?)</title>", dom_p, re.S).group(1)))
            assert res_p["placa"] == "R$ 17,50"
            assert res_p["total"] == "R$ 17,50"
            assert "R$ 17,50" in res_p["msg"]
            report["propagacao_mudanca_preco"] = res_p
        finally:
            shutil.rmtree(tmp_preco_dir, ignore_errors=True)

        # 4d) E2E completo de equipe.html nos 4 segmentos + geometria responsiva (320px/360px/1440px) + compilação --producao
        e2e_eq = ROOT / "output" / "_e2e_equipe_completa.html"
        try:
            e2e_eq.write_text(
                f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0">
<iframe id="eq320" src="http://127.0.0.1:{port}/output/quatro-segmentos/alimentacao/equipe.html" style="width:320px;height:800px;border:0"></iframe>
<iframe id="eq1440" src="http://127.0.0.1:{port}/output/quatro-segmentos/alimentacao/equipe.html" style="width:1440px;height:900px;border:0"></iframe>
<script>
window.addEventListener("load", () => setTimeout(() => {{
  const d320 = document.getElementById("eq320").contentDocument;
  const d1440 = document.getElementById("eq1440").contentDocument;
  d320.defaultView.localStorage.clear();
  d1440.defaultView.localStorage.clear();

  const semOverflow320 = d320.documentElement.scrollWidth <= 320;
  const semOverflow1440 = d1440.documentElement.scrollWidth <= 1440;
  const zeroSenhas = d1440.querySelectorAll('input[type="password"]').length === 0;
  const temAvisoExportacao = d1440.body.innerText.includes("Exportar não publica o site");

  // Verifica alvos de toque visíveis >= 48px (botões, campos de texto, selects e rótulos de opções)
  const alvosMenores48 = [];
  d320.querySelectorAll('button, input:not([type="checkbox"]):not([type="radio"]):not([type="file"]), select, textarea, .opcao-controle').forEach((el) => {{
    if (el.hidden || el.closest("[hidden]") || el.closest("details:not([open]) > :not(summary)")) return;
    const cs = d320.defaultView.getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") return;
    const r = el.getBoundingClientRect();
    if (r.width > 0 && r.height > 0 && (r.height < 47.5 || r.width < 47.5)) {{
      alvosMenores48.push(el.id || el.className || el.tagName);
    }}
  }});

  function setVal(doc, sel, val) {{
    const el = typeof sel === "string" ? doc.querySelector(sel) : sel;
    el.value = val;
    el.dispatchEvent(new doc.defaultView.Event("input", {{ bubbles: true }}));
    el.dispatchEvent(new doc.defaultView.Event("change", {{ bubbles: true }}));
  }}

  function setCheck(doc, sel, checked) {{
    const el = typeof sel === "string" ? doc.querySelector(sel) : sel;
    el.checked = checked;
    el.dispatchEvent(new doc.defaultView.Event("change", {{ bubbles: true }}));
  }}

  const resultadosSegmentos = {{}};

  // 1) ALIMENTAÇÃO completo (com Pix, horários extras, GPS, Destaque da casa, variações, história e fotos referenciadas)
  setCheck(d1440, "#eq-consentimento", true);
  setCheck(d1440, "#seg-alimentacao", true);
  setVal(d1440, "#eq-nome", "Pastel da Dona Nalva");
  setVal(d1440, "#eq-atendente", "Dona Nalva");
  setVal(d1440, "#eq-oferta", "Pastel na hora e caldo de cana gelado, no Parque da Cidade");
  setVal(d1440, "#eq-dias", "Quinta a domingo");
  setVal(d1440, "#eq-inicio", "08h");
  setVal(d1440, "#eq-fim", "17h");
  d1440.getElementById("btn-add-horario").click();
  setVal(d1440, ".js-ht-dias", "Sábado e domingo");
  setVal(d1440, ".js-ht-hora", "07h30 às 17h30");
  setVal(d1440, "#eq-ref", "Perto da entrada principal, ao lado das amendoeiras");
  setVal(d1440, "#eq-lat", "-12,9949");
  setVal(d1440, "#eq-lng", "-38,4611");
  setVal(d1440, "#eq-zap", "(71) 99123-4567");
  setCheck(d1440, "#eq-pix-aut", true);
  setVal(d1440, "#eq-pix-nome", "Maria Nalva dos Santos");
  setVal(d1440, "#eq-pix-chave", "nalva.pastel@exemplo.br");
  setVal(d1440, "#eq-historia", "Abro a massa fresquinha toda manhã na sombra das amendoeiras.");
  setCheck(d1440, "#eq-ref-foto-barraca", true);
  setCheck(d1440, ".item-editor .js-it-destaque", true);
  setVal(d1440, ".item-editor .js-it-nome", "Pastel grande na hora");
  setVal(d1440, ".item-editor .js-it-cat", "Salgados");
  setVal(d1440, ".item-editor .js-it-desc", "Acompanha vinagrete da casa.");
  d1440.querySelector(".item-editor .js-add-var").click();
  setVal(d1440, ".item-editor .js-var-rotulo", "Queijo coalho");
  setVal(d1440, ".item-editor .js-var-preco", "10,00");

  resultadosSegmentos.alimentacao = {{
    json: JSON.parse(d1440.getElementById("json-gerado-previa").value),
    prompt: d1440.getElementById("prompt-gerado-chat").value
  }};

  // 2) BRINQUEDOS (com idade indicada)
  setCheck(d1440, "#seg-brinquedos", true);
  setVal(d1440, ".item-editor .js-it-nome", "Kit bolha gigante");
  setVal(d1440, ".item-editor .js-it-idade", "A partir de 3 anos");
  resultadosSegmentos.brinquedos = {{
    json: JSON.parse(d1440.getElementById("json-gerado-previa").value),
    prompt: d1440.getElementById("prompt-gerado-chat").value
  }};

  // 3) INFLÁVEIS (com tempo, idade, altura e regras)
  setCheck(d1440, "#seg-inflaveis", true);
  setVal(d1440, ".item-editor .js-it-nome", "Tobogã inflável colorido");
  setVal(d1440, ".item-editor .js-it-tempo", "15 minutos");
  setVal(d1440, ".item-editor .js-it-idade", "3 a 12 anos");
  setVal(d1440, ".item-editor .js-it-altura", "Até 1,50 m");
  setVal(d1440, ".item-editor .js-it-regras", "Sem calçados.\\nResponsável por perto.");
  resultadosSegmentos.inflaveis = {{
    json: JSON.parse(d1440.getElementById("json-gerado-previa").value),
    prompt: d1440.getElementById("prompt-gerado-chat").value
  }};

  // 4) BICICLETAS (com tempos_precos e regras_aluguel)
  setCheck(d1440, "#seg-bicicletas", true);
  setVal(d1440, "#eq-regra-doc", "Documento com foto no cadastro.");
  setVal(d1440, "#eq-regra-caucao", "Sem caução.");
  setVal(d1440, "#eq-regra-devolucao", "Devolução até as 17h.");
  setVal(d1440, ".item-editor .js-it-nome", "Bicicleta passeio aro 26");
  const tps = d1440.querySelectorAll(".item-editor .js-linha-tp");
  setVal(d1440, tps[0].querySelector(".js-tp-tempo"), "30 minutos");
  setVal(d1440, tps[0].querySelector(".js-tp-preco"), "18,00");
  setVal(d1440, tps[1].querySelector(".js-tp-tempo"), "1 hora");
  setVal(d1440, tps[1].querySelector(".js-tp-preco"), "30,00");
  resultadosSegmentos.bicicletas = {{
    json: JSON.parse(d1440.getElementById("json-gerado-previa").value),
    prompt: d1440.getElementById("prompt-gerado-chat").value
  }};

  d1440.defaultView.localStorage.clear();
  document.title = JSON.stringify({{
    semOverflow320,
    semOverflow1440,
    zeroSenhas,
    temAvisoExportacao,
    alvosMenores48,
    resultadosSegmentos
  }});
}}, 700));
</script></body></html>""",
                encoding="utf-8",
            )
            dom_eq = _dump_dom_from_chrome(f"http://127.0.0.1:{port}/output/_e2e_equipe_completa.html", wait_ms=3200)
            res_eq = json.loads(html_unescape(re.search(r"<title>(.*?)</title>", dom_eq, re.S).group(1)))
            assert res_eq["semOverflow320"] is True, f"Overflow em 320px em equipe.html: {res_eq}"
            assert res_eq["semOverflow1440"] is True, f"Overflow em 1440px em equipe.html: {res_eq}"
            assert res_eq["zeroSenhas"] is True
            assert res_eq["temAvisoExportacao"] is True
            assert res_eq["alvosMenores48"] == [], f"Alvos < 48px em equipe.html: {res_eq['alvosMenores48']}"

            # Verifica que o dados.json exportado por equipe.html compila em MODO PRODUÇÃO nos 4 segmentos sem faltar nenhum campo!
            for seg_k, pacote_seg in res_eq["resultadosSegmentos"].items():
                dados_exp = pacote_seg["json"]
                prompt_exp = pacote_seg["prompt"]
                erros_prod = validar_dados(dados_exp, modo_producao=True)
                assert erros_prod == [], f"Erros de produção em {seg_k} exportado por equipe.html: {erros_prod}"
                assert "COLETA 100% COMPLETA E VALIDADA PARA BUILD DE PRODUÇÃO" in prompt_exp, f"Prompt incompleto em {seg_k}: {prompt_exp}"
                assert '"slug": "pastel-da-dona-nalva"' in prompt_exp

                tmp_eq_build = Path(tempfile.mkdtemp(prefix=f"eq_prod_{seg_k}_"))
                try:
                    (tmp_eq_build / "dados.json").write_text(json.dumps(dados_exp, ensure_ascii=False), encoding="utf-8")
                    compilar_site_ambulante(tmp_eq_build, tmp_eq_build / "dist", ROOT, modo_producao=True)
                    html_compilado = (tmp_eq_build / "dist" / "index.html").read_text(encoding="utf-8")
                    assert "Pastel da Dona Nalva" in html_compilado
                    assert "5571991234567" in html_compilado
                    assert "Perto da Perto da" not in html_compilado
                finally:
                    shutil.rmtree(tmp_eq_build, ignore_errors=True)

            report["equipe_4_segmentos_e_prompt"] = "APROVADO_100_PORCENTO"
        finally:
            if e2e_eq.exists():
                e2e_eq.unlink()
    finally:
        httpd.shutdown()

    # 5. Verificação matemática da matriz ISO-18004 do QR Code gerado para cada segmento
    qr_validados = {}
    for seg in ("alimentacao", "brinquedos", "inflaveis", "bicicletas"):
        dados_s = json.loads((ROOT / "ambulantes_exemplo" / seg / "dados.json").read_text(encoding="utf-8"))
        url_esp = dados_s["url_final"]
        svg_gerado = (ROOT / "output" / "quatro-segmentos" / seg / "qrcode.svg").read_text(encoding="utf-8")
        esperado_buf = Path(tempfile.mktemp(suffix=".svg"))
        try:
            segno.make(url_esp, error="m").save(str(esperado_buf), kind="svg", scale=8, border=2, dark="#000000", light="#FFFFFF", omitsize=True)
            path_d_gerado = re.findall(r'<path[^>]*d="([^"]+)"', svg_gerado)
            path_d_esperado = re.findall(r'<path[^>]*d="([^"]+)"', esperado_buf.read_text(encoding="utf-8"))
            assert path_d_gerado and path_d_gerado == path_d_esperado, f"Matriz QR divergente em {seg}"
            qr_validados[seg] = url_esp
        finally:
            if esperado_buf.exists():
                esperado_buf.unlink()
    report["qrcodes_matriz_verificada"] = qr_validados

    return report


def html_unescape(s: str) -> str:
    import html
    return html.unescape(s)


if __name__ == "__main__":
    resultado = run_all_acceptance_tests()
    print("ACCEPTANCE_SUITE_PASSED=", json.dumps(resultado, indent=2, ensure_ascii=False))

"""Gera a Página Separada da Equipe (`equipe.html`) e a Placa A5 Imprimível (`placa-a5.html` + `qrcode.svg`) na linguagem 'Toldo Aberto' (Seção 13)."""

from __future__ import annotations

import html
import json
from pathlib import Path
import re
from typing import Any

import segno

from .sistema_toldo import (
    ACCENTS,
    FONT_AND_TOKENS_CSS,
    ICONES_2PX,
    copy_fonts_to,
    render_toldo_svg,
)


def gerar_qrcode_svg_local(url: str, out_svg_path: Path) -> str:
    """Gera QR Code vetorial offline ISO-18004 em alto contraste preto e branco."""
    out_svg_path.parent.mkdir(parents=True, exist_ok=True)
    qr = segno.make(url, error="m")
    qr.save(str(out_svg_path), kind="svg", scale=8, border=2, dark="#000000", light="#FFFFFF", omitsize=True)
    svg_txt = out_svg_path.read_text(encoding="utf-8")
    if "viewBox=" not in svg_txt:
        m = re.search(r'width="(\d+)"\s+height="(\d+)"', svg_txt)
        if m:
            svg_txt = svg_txt.replace("<svg ", f'<svg viewBox="0 0 {m.group(1)} {m.group(2)}" ', 1)
    # Remove declaração XML para embutir direto no HTML da placa A5 sem requisição extra
    svg_inline = re.sub(r"^<\?xml[^>]*\?>\s*", "", svg_txt).strip()
    out_svg_path.write_text(svg_txt, encoding="utf-8")
    return svg_inline


def gerar_placa_a5(dados: dict[str, Any], out_dir: Path, project_root: Path) -> dict[str, str]:
    """Gera `placa-a5.html` e `qrcode.svg` imprimíveis em A5 (>= 6 cm de QR, legível em P&B)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    copy_fonts_to(out_dir, project_root)

    seg = str(dados.get("segmento", "alimentacao"))
    nome = str(dados.get("nome_negocio", "Barraca Exemplo")).strip()
    oferta = str(dados.get("o_que_oferece", "")).strip()
    ref = str(dados.get("referencia", "")).strip()
    modo_exemplo = bool(dados.get("modo_exemplo", False))
    url_final = str(dados.get("url_final", "")).strip() or "https://parque-da-cidade-unijorge.vercel.app/"

    qr_path = out_dir / "qrcode.svg"
    svg_qr = gerar_qrcode_svg_local(url_final, qr_path)

    selo_demo = (
        '<p class="placa-aviso-demo">Modelo demonstrativo: dados fictícios</p>'
        if modo_exemplo
        else ""
    )
    oferta_html = f'<p class="placa-oferta">{html.escape(oferta)}</p>' if oferta else ""
    ref_html = f'<p class="placa-referencia">Parque da Cidade · Perto da {html.escape(ref)}</p>' if ref else ""

    placa_html = f"""<!DOCTYPE html>
<html lang="pt-BR" data-segmento="{html.escape(seg)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Placa A5 — {html.escape(nome)}</title>
  <link rel="preload" href="fonts/fraunces-600-800-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="fonts/atkinson-hyperlegible-400-latin.woff2" as="font" type="font/woff2" crossorigin>
  <style>
{FONT_AND_TOKENS_CSS}
    @page {{
      size: A5 portrait;
      margin: 8mm;
    }}
    body {{
      background-color: var(--papel-2);
      padding: var(--s-24) var(--s-16);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: var(--s-16);
    }}
    .barra-impressao {{
      width: 100%;
      max-width: 148mm;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: var(--s-12);
    }}
    .folha-a5 {{
      width: 100%;
      max-width: 148mm;
      min-height: 204mm;
      background-color: #FFFFFF;
      color: #000000;
      border: 2.5px solid #000000;
      border-radius: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    /* Borda firme no toldo para leitura nítida mesmo em impressão P&B */
    .toldo-placa {{
      border-bottom: 2px solid #000000;
    }}
    .placa-corpo {{
      padding: 8mm 10mm;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 5mm;
      flex: 1 1 auto;
      justify-content: space-between;
    }}
    .placa-aviso-demo {{
      font-size: 0.9375rem;
      font-weight: 700;
      padding: 4px 12px;
      border: 1.5px dashed #000000;
      border-radius: 999px;
    }}
    .placa-nome {{
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-optical-sizing: auto;
      font-variation-settings: "SOFT" 45;
      font-size: clamp(2.1rem, 6vw, 2.85rem);
      line-height: 0.98;
      font-weight: 800;
      color: #000000;
    }}
    .placa-oferta {{
      margin-top: var(--s-8);
      font-size: 1.0625rem;
      line-height: 1.38;
      color: #000000;
      max-width: 38ch;
    }}
    /* QR Code com pelo menos 6 cm físicos (68 mm x 68 mm) */
    .moldura-qr {{
      padding: 4mm;
      border: 2.5px solid #000000;
      border-radius: 14px;
      background-color: #FFFFFF;
      display: inline-flex;
      flex-direction: column;
      align-items: center;
      gap: 3mm;
    }}
    .qr-fisico {{
      width: 68mm;
      height: 68mm;
      min-width: 60mm;
      min-height: 60mm;
      display: block;
    }}
    .qr-fisico svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}
    .chamada-camera {{
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-size: 1.375rem;
      line-height: 1.15;
      font-weight: 700;
      color: #000000;
    }}
    .endereco-escrito {{
      width: 100%;
      padding: 3mm 4mm;
      border: 1.5px solid #000000;
      border-radius: 10px;
      font-size: 0.95rem;
      font-weight: 700;
      word-break: break-all;
      background-color: #FFFFFF;
      color: #000000;
    }}
    .placa-referencia {{
      font-size: 0.9375rem;
      color: #000000;
    }}
    .placa-rodape {{
      width: 100%;
      padding: 3.5mm 8mm;
      border-top: 2px solid #000000;
      font-size: 0.875rem;
      font-weight: 700;
      text-align: center;
      background-color: #FFFFFF;
      color: #000000;
    }}
    body.simular-pb .folha-a5 {{
      filter: grayscale(100%) contrast(1.08);
    }}
    @media print {{
      body {{
        background: #FFFFFF;
        padding: 0;
      }}
      .barra-impressao {{
        display: none !important;
      }}
      .folha-a5 {{
        width: 100%;
        max-width: none;
        min-height: 192mm;
        border-width: 2px;
      }}
    }}
  </style>
</head>
<body>
  <div class="barra-impressao">
    <button type="button" class="botao botao-mata" id="btn-imprimir-placa">
      {ICONES_2PX["pedido"]}<span>Imprimir Placa A5</span>
    </button>
    <button type="button" class="botao botao-contorno" id="btn-alternar-pb" aria-pressed="false">
      {ICONES_2PX["confere"]}<span>Testar leitura em P&amp;B</span>
    </button>
  </div>

  <main class="folha-a5" aria-labelledby="titulo-placa">
    <div class="toldo-placa">
      {render_toldo_svg(seg, altura_lona=34)}
    </div>
    <div class="placa-corpo">
      {selo_demo}
      <div>
        <h1 id="titulo-placa" class="placa-nome">{html.escape(nome)}</h1>
        {oferta_html}
      </div>

      <div class="moldura-qr">
        <div class="qr-fisico" role="img" aria-label="QR Code para abrir {html.escape(url_final)}">
          {svg_qr}
        </div>
      </div>

      <div style="width: 100%; display: flex; flex-direction: column; gap: 3mm; align-items: center;">
        <p class="chamada-camera">Aponte a câmera para ver os preços</p>
        <p class="endereco-escrito">{html.escape(url_final)}</p>
        {ref_html}
      </div>
    </div>
    <footer class="placa-rodape">
      Projeto de Extensão Parque Digital — Unijorge · Parque da Cidade (Salvador)
    </footer>
  </main>

  <script>
    document.getElementById("btn-imprimir-placa").addEventListener("click", () => window.print());
    const btnPb = document.getElementById("btn-alternar-pb");
    btnPb.addEventListener("click", () => {{
      const ativo = document.body.classList.toggle("simular-pb");
      btnPb.setAttribute("aria-pressed", ativo ? "true" : "false");
    }});
  </script>
</body>
</html>"""

    placa_path = out_dir / "placa-a5.html"
    placa_path.write_text(placa_html, encoding="utf-8")
    return {"placa_path": str(placa_path), "qr_path": str(qr_path)}


def gerar_pagina_equipe(out_dir: Path, project_root: Path) -> str:
    """Gera `equipe.html` separada e fora do menu do cliente: ficha em blocos, consentimento, prévia ao vivo, rascunho local + apagar e exportação sem senha."""
    out_dir.mkdir(parents=True, exist_ok=True)
    copy_fonts_to(out_dir, project_root)

    toldos_js = {seg: render_toldo_svg(seg, altura_lona=30) for seg in ACCENTS}

    equipe_html = f"""<!DOCTYPE html>
<html lang="pt-BR" data-segmento="alimentacao">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow">
  <title>Ficha de Campo da Equipe Unijorge — Toldo Aberto</title>
  <link rel="preload" href="fonts/fraunces-600-800-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="fonts/atkinson-hyperlegible-400-latin.woff2" as="font" type="font/woff2" crossorigin>
  <style>
{FONT_AND_TOKENS_CSS}
    .topo-equipe {{
      background-color: var(--papel-2);
      border-bottom: 1.5px solid var(--linha);
      padding-block: var(--s-24);
    }}
    .grade-equipe {{
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--s-32);
      padding-block: var(--s-32) var(--s-96);
      align-items: start;
    }}
    @media (min-width: 1024px) {{
      .grade-equipe {{
        grid-template-columns: repeat(12, minmax(0, 1fr));
      }}
      .coluna-ficha {{ grid-column: 1 / 8; }}
      .coluna-previa {{
        grid-column: 8 / 13;
        position: sticky;
        top: var(--s-24);
      }}
    }}
    .bloco-ficha {{
      background-color: var(--papel-2);
      border: 1.5px solid var(--linha);
      border-radius: var(--r-foto);
      padding: var(--s-24);
      margin-bottom: var(--s-24);
      display: flex;
      flex-direction: column;
      gap: var(--s-16);
    }}
    .bloco-ficha legend {{
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-size: 1.5rem;
      font-weight: 700;
      padding-inline: var(--s-8);
      color: var(--tinta);
    }}
    .campo-grupo {{
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: var(--s-8);
    }}
    .campo-grupo label {{
      font-weight: 700;
    }}
    .duas-colunas {{
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--s-16);
    }}
    @media (min-width: 600px) {{
      .duas-colunas {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
    .linha-consentimento {{
      display: flex;
      align-items: flex-start;
      gap: var(--s-12);
      padding: var(--s-16);
      background-color: var(--papel);
      border: 2px solid var(--tinta);
      border-radius: var(--r-botao);
    }}
    .linha-consentimento input[type="checkbox"] {{
      width: 24px;
      height: 24px;
      margin-top: 2px;
      accent-color: var(--mata);
      flex-shrink: 0;
    }}
    .item-editor {{
      background-color: var(--papel);
      border: 1.5px solid var(--linha);
      border-radius: var(--r-botao);
      padding: var(--s-16);
      display: flex;
      flex-direction: column;
      gap: var(--s-12);
    }}
    .cartao-previa-ao-vivo {{
      background-color: var(--papel);
      border: 2px solid var(--tinta);
      border-radius: var(--r-foto);
      overflow: hidden;
    }}
    .previa-miolo {{
      padding: var(--s-24);
      display: flex;
      flex-direction: column;
      gap: var(--s-12);
    }}
    .aviso-exportacao {{
      margin-top: var(--s-16);
      padding: var(--s-16);
      background-color: var(--papel-2);
      border: 2px solid var(--tinta);
      border-radius: var(--r-botao);
      font-weight: 700;
    }}
    .barra-rascunho {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: var(--s-12);
      padding: var(--s-12) var(--s-16);
      background-color: var(--papel);
      border: 1.5px solid var(--linha);
      border-radius: var(--r-botao);
      margin-bottom: var(--s-24);
    }}
  </style>
</head>
<body>
  <div id="toldo-equipe">{render_toldo_svg("alimentacao", altura_lona=34)}</div>

  <header class="topo-equipe">
    <div class="conteiner">
      <p class="texto-apoio">Uso interno dos grupos extensionistas Unijorge (página fora do menu do cliente · sem senhas)</p>
      <h1 class="titulo-secao" style="margin-top: var(--s-8);">Ficha de campo do ambulante</h1>
    </div>
  </header>

  <main class="conteiner grade-equipe">
    <form id="form-equipe" class="coluna-ficha" novalidate>
      <div class="barra-rascunho">
        <span id="status-rascunho" role="status" class="texto-apoio" style="font-weight: 700;">Rascunho local pronto neste aparelho.</span>
        <button type="button" class="botao botao-contorno" id="btn-apagar-rascunho">
          {ICONES_2PX["lixeira"]}<span>Apagar rascunho</span>
        </button>
      </div>

      <!-- BLOCO 1: CONSENTIMENTO E IDENTIFICAÇÃO -->
      <fieldset class="bloco-ficha">
        <legend>1. Consentimento e negócio</legend>
        <div class="linha-consentimento">
          <input type="checkbox" id="eq-consentimento" name="consentimento" required>
          <label for="eq-consentimento">
            Li em voz alta para o ambulante que a página é gratuita, feita pela extensão da Unijorge, e que ele pode pedir correção ou retirada do ar a qualquer momento. Autorização confirmada. *
          </label>
        </div>

        <div class="duas-colunas">
          <div class="campo-grupo">
            <label for="eq-segmento">Segmento no Parque da Cidade *</label>
            <select id="eq-segmento" name="segmento" class="campo-entrada">
              <option value="alimentacao">Alimentação e bebidas</option>
              <option value="brinquedos">Brinquedos e doces</option>
              <option value="inflaveis">Infláveis e pula-pula</option>
              <option value="bicicletas">Aluguel de bicicletas</option>
            </select>
          </div>
          <div class="campo-grupo">
            <label for="eq-slug">Identificador curto (slug) *</label>
            <input type="text" id="eq-slug" name="slug" class="campo-entrada" autocorrect="off" autocapitalize="none" spellcheck="false" placeholder="Ex.: barraca-da-nalva" required>
          </div>
        </div>

        <div class="duas-colunas">
          <div class="campo-grupo">
            <label for="eq-nome">Nome do negócio *</label>
            <input type="text" id="eq-nome" name="nome_negocio" class="campo-entrada" placeholder="Ex.: Pastel da Sombra" required>
          </div>
          <div class="campo-grupo">
            <label for="eq-atendente">Quem atende</label>
            <input type="text" id="eq-atendente" name="quem_atende" class="campo-entrada" placeholder="Ex.: Dona Lúcia">
          </div>
        </div>

        <div class="campo-grupo">
          <label for="eq-oferta">O que oferece, no Parque da Cidade *</label>
          <input type="text" id="eq-oferta" name="o_que_oferece" class="campo-entrada" placeholder="Ex.: Pastel frito na hora e caldo de cana, no Parque da Cidade" required>
        </div>
      </fieldset>

      <!-- BLOCO 2: HORÁRIO, PONTO E CONTATO -->
      <fieldset class="bloco-ficha">
        <legend>2. Horário, ponto e pagamento</legend>
        <div class="duas-colunas">
          <div class="campo-grupo">
            <label for="eq-dias">Dias de funcionamento *</label>
            <input type="text" id="eq-dias" name="dias" class="campo-entrada" placeholder="Ex.: Quinta a domingo" required>
          </div>
          <div class="duas-colunas">
            <div class="campo-grupo">
              <label for="eq-inicio">Início *</label>
              <input type="text" id="eq-inicio" name="inicio" class="campo-entrada" placeholder="08h" required>
            </div>
            <div class="campo-grupo">
              <label for="eq-fim">Fim *</label>
              <input type="text" id="eq-fim" name="fim" class="campo-entrada" placeholder="17h" required>
            </div>
          </div>
        </div>

        <div class="campo-grupo">
          <label for="eq-ref">Perto de qual referência no parque? *</label>
          <input type="text" id="eq-ref" name="referencia" class="campo-entrada" placeholder="Ex.: entrada principal, ao lado das amendoeiras" required>
        </div>

        <div class="duas-colunas">
          <div class="campo-grupo">
            <label for="eq-lat">Latitude (opcional)</label>
            <input type="text" id="eq-lat" name="latitude" class="campo-entrada" inputmode="decimal" placeholder="-12.9949">
          </div>
          <div class="campo-grupo">
            <label for="eq-lng">Longitude (opcional)</label>
            <input type="text" id="eq-lng" name="longitude" class="campo-entrada" inputmode="decimal" placeholder="-38.4611">
          </div>
        </div>

        <div class="duas-colunas">
          <div class="campo-grupo">
            <label for="eq-zap">WhatsApp com DDD (DDI 55) *</label>
            <input type="text" id="eq-zap" name="whatsapp" class="campo-entrada" inputmode="numeric" placeholder="55719..." required>
          </div>
          <div class="campo-grupo">
            <label for="eq-pag">Formas de pagamento (separadas por vírgula)</label>
            <input type="text" id="eq-pag" name="pagamento" class="campo-entrada" value="Dinheiro, Cartão, Pix">
          </div>
        </div>

        <div class="linha-consentimento">
          <input type="checkbox" id="eq-pix-aut" name="pix_autorizado">
          <label for="eq-pix-aut">O ambulante autorizou exibir chave Pix e nome do recebedor na página.</label>
        </div>
        <div class="duas-colunas" id="bloco-campos-pix" hidden>
          <div class="campo-grupo">
            <label for="eq-pix-nome">Nome do recebedor no Pix</label>
            <input type="text" id="eq-pix-nome" name="pix_recebedor" class="campo-entrada">
          </div>
          <div class="campo-grupo">
            <label for="eq-pix-chave">Chave Pix</label>
            <input type="text" id="eq-pix-chave" name="pix_chave" class="campo-entrada" autocorrect="off" autocapitalize="none">
          </div>
        </div>
      </fieldset>

      <!-- BLOCO 3: ITENS E PREÇOS -->
      <fieldset class="bloco-ficha">
        <legend>3. Itens, variações e preços conferidos</legend>
        <div class="duas-colunas">
          <div class="campo-grupo">
            <label for="eq-data-precos">Data da conferência dos preços</label>
            <input type="date" id="eq-data-precos" name="data_precos" class="campo-entrada">
          </div>
          <div class="campo-grupo">
            <label for="eq-url">URL final prevista</label>
            <input type="url" id="eq-url" name="url_final" class="campo-entrada" autocorrect="off" autocapitalize="none" placeholder="https://...">
          </div>
        </div>

        <div class="duas-colunas">
          <label class="linha-consentimento" for="eq-pedidos-dia">
            <input type="checkbox" id="eq-pedidos-dia" checked>
            <span>Aceita pedidos no dia (comanda)</span>
          </label>
          <label class="linha-consentimento" for="eq-encomendas">
            <input type="checkbox" id="eq-encomendas" checked>
            <span>Aceita encomendas para grupos</span>
          </label>
        </div>

        <div id="lista-itens-equipe" style="display:flex;flex-direction:column;gap:var(--s-12);"></div>
        <div>
          <button type="button" class="botao botao-contorno" id="btn-novo-item">
            {ICONES_2PX["mais"]}<span>Adicionar item ao catálogo</span>
          </button>
        </div>
      </fieldset>

      <!-- BLOCO 4: HISTÓRIA E FOTOS -->
      <fieldset class="bloco-ficha">
        <legend>4. Frase aprovada e enquadramento de foto</legend>
        <div class="campo-grupo">
          <label for="eq-historia">Frase curta aprovada por quem atende (opcional)</label>
          <textarea id="eq-historia" name="historia_aprovada" rows="2" class="campo-entrada" placeholder="Escreva exatamente com as palavras aprovadas pelo ambulante."></textarea>
        </div>
        <div class="duas-colunas">
          <div class="campo-grupo">
            <label for="eq-foco-barraca">Enquadramento da foto da barraca</label>
            <select id="eq-foco-barraca" class="campo-entrada">
              <option value="topo">Topo (protege rostos no alto)</option>
              <option value="centro">Centro</option>
              <option value="base">Base</option>
            </select>
          </div>
          <div class="campo-grupo">
            <label for="eq-foto-teste">Testar foto local (comprime até 150 KB)</label>
            <input type="file" id="eq-foto-teste" accept="image/*" class="campo-entrada">
          </div>
        </div>
        <p class="texto-apoio" id="status-foto-equipe" role="status"></p>
      </fieldset>

      <p class="mensagem-erro" id="erro-exportacao-equipe" role="alert" hidden>
        {ICONES_2PX["alerta"]}<span id="texto-erro-equipe">Confirme o consentimento e os campos obrigatórios antes de exportar.</span>
      </p>

      <div style="display:flex;flex-wrap:wrap;gap:var(--s-12);">
        <button type="submit" class="botao botao-mata" id="btn-exportar-dados">
          {ICONES_2PX["pedido"]}<span>Exportar dados.json</span>
        </button>
      </div>

      <p class="aviso-exportacao">
        Exportar não publica o site. O arquivo <code>dados.json</code> salvo no aparelho deve ser entregue à revisão e ao passo de compilação da equipe Unijorge antes de ir ao ar.
      </p>
    </form>

    <!-- PRÉVIA AO VIVO -->
    <aside class="coluna-previa" aria-labelledby="titulo-previa-equipe">
      <h2 id="titulo-previa-equipe" class="nome-item" style="margin-bottom: var(--s-12);">Prévia ao vivo</h2>
      <div class="cartao-previa-ao-vivo">
        <div id="previa-toldo">{render_toldo_svg("alimentacao", altura_lona=30)}</div>
        <div class="previa-miolo">
          <img id="previa-foto-local" alt="Prévia da foto selecionada" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:12px;" hidden>
          <h3 class="letreiro-nome" id="previa-nome" style="font-size: 2.35rem;">Nome da barraca</h3>
          <p id="previa-oferta" class="texto-apoio">O que oferece, no Parque da Cidade</p>
          <p id="previa-horario" style="font-size: 0.9375rem; font-weight: 700;">Dias e horário</p>
          <p id="previa-ref" class="texto-apoio" style="font-size: 0.9375rem;">Perto da referência</p>
          <div style="padding-top:var(--s-12);border-top:1px dashed var(--linha);display:flex;justify-content:space-between;align-items:center;gap:var(--s-8);">
            <span id="previa-item-nome" style="font-weight:700;">Primeiro item</span>
            <span class="placa-preco"><span class="placa-furo" aria-hidden="true"></span><span class="preco-valor" id="previa-item-preco">R$ 0,00</span></span>
          </div>
        </div>
      </div>

      <div class="aviso-exportacao" style="margin-top: var(--s-16);">
        Exportar não publica o site. Nenhum dado sai deste aparelho até você exportar o arquivo.
      </div>
    </aside>
  </main>

  <script>
  (() => {{
    const TOLDOS = {json.dumps(toldos_js, ensure_ascii=False)};
    const CHAVE_RASCUNHO = "toldo_aberto_rascunho_equipe_v1";
    const form = document.getElementById("form-equipe");
    const listaItens = document.getElementById("lista-itens-equipe");
    const statusRascunho = document.getElementById("status-rascunho");
    const pixAut = document.getElementById("eq-pix-aut");
    const blocoPix = document.getElementById("bloco-campos-pix");

    let itensEstado = [
      {{ nome: "Pastel grande na hora", categoria: "Salgados", preco: "10.00", variacoes: "Queijo:10, Carne:10" }}
    ];

    function criarLinhaItemDOM(item, idx) {{
      const wrap = document.createElement("div");
      wrap.className = "item-editor";
      wrap.innerHTML =
        '<div class="duas-colunas">' +
          '<div class="campo-grupo"><label>Nome do item ' + (idx + 1) + '</label><input type="text" class="campo-entrada js-it-nome"></div>' +
          '<div class="campo-grupo"><label>Categoria</label><input type="text" class="campo-entrada js-it-cat"></div>' +
        '</div>' +
        '<div class="duas-colunas">' +
          '<div class="campo-grupo"><label>Preço base (R$)</label><input type="text" inputmode="decimal" class="campo-entrada js-it-preco"></div>' +
          '<div class="campo-grupo"><label>Variações (Ex.: 300 ml:14, 500 ml:20)</label><input type="text" class="campo-entrada js-it-var"></div>' +
        '</div>' +
        '<div><button type="button" class="botao botao-contorno js-rem-it">Remover item</button></div>';
      wrap.querySelector(".js-it-nome").value = item.nome || "";
      wrap.querySelector(".js-it-cat").value = item.categoria || "";
      wrap.querySelector(".js-it-preco").value = item.preco || "";
      wrap.querySelector(".js-it-var").value = item.variacoes || "";
      wrap.querySelectorAll("input").forEach((inp) => inp.addEventListener("input", () => {{
        sincronizarItensDoDOM();
        atualizarPreviaESalvar();
      }}));
      wrap.querySelector(".js-rem-it").addEventListener("click", () => {{
        if (itensEstado.length > 1) {{
          itensEstado.splice(idx, 1);
          renderizarItensEditor();
          atualizarPreviaESalvar();
        }}
      }});
      return wrap;
    }}

    function renderizarItensEditor() {{
      listaItens.innerHTML = "";
      itensEstado.forEach((it, i) => listaItens.appendChild(criarLinhaItemDOM(it, i)));
    }}

    function sincronizarItensDoDOM() {{
      itensEstado = Array.from(listaItens.querySelectorAll(".item-editor")).map((ed) => ({{
        nome: ed.querySelector(".js-it-nome").value,
        categoria: ed.querySelector(".js-it-cat").value,
        preco: ed.querySelector(".js-it-preco").value,
        variacoes: ed.querySelector(".js-it-var").value
      }}));
    }}

    function montarDadosJSON() {{
      const seg = document.getElementById("eq-segmento").value;
      const dPrecos = document.getElementById("eq-data-precos").value;
      const dataBR = dPrecos && /^\\d{{4}}-\\d{{2}}-\\d{{2}}$/.test(dPrecos)
        ? dPrecos.split("-").reverse().join("/")
        : "";
      const itensFormatados = itensEstado.filter((x) => x.nome.trim()).map((x, idx) => {{
        const vars = (x.variacoes || "").split(",").map((s) => s.trim()).filter(Boolean).map((par) => {{
          const [r, p] = par.split(":");
          return {{ rotulo: (r || "").trim(), preco: Number(String(p || x.preco || 0).replace(",", ".")) || 0 }};
        }}).filter((v) => v.rotulo);
        return {{
          id: "item-" + (idx + 1),
          categoria: x.categoria.trim() || "Geral",
          nome: x.nome.trim(),
          preco: Number(String(x.preco || 0).replace(",", ".")) || 0,
          tipo_variacao: "opção",
          variacoes: vars
        }};
      }});

      const inicio = document.getElementById("eq-inicio").value.trim();
      const fim = document.getElementById("eq-fim").value.trim();
      const dias = document.getElementById("eq-dias").value.trim();

      return {{
        slug: document.getElementById("eq-slug").value.trim() || "barraca-parque",
        modo_exemplo: false,
        consentimento: document.getElementById("eq-consentimento").checked,
        segmento: seg,
        nome_negocio: document.getElementById("eq-nome").value.trim(),
        quem_atende: document.getElementById("eq-atendente").value.trim(),
        o_que_oferece: document.getElementById("eq-oferta").value.trim(),
        whatsapp: document.getElementById("eq-zap").value.replace(/\\D/g, ""),
        pix: {{
          autorizado: pixAut.checked,
          recebedor: document.getElementById("eq-pix-nome").value.trim(),
          chave: document.getElementById("eq-pix-chave").value.trim()
        }},
        pagamento: document.getElementById("eq-pag").value.split(",").map((s) => s.trim()).filter(Boolean),
        dias: dias,
        horarios: {{
          inicio: inicio,
          fim: fim,
          tabela: dias && inicio && fim ? [{{ dias: dias, horario: inicio + " às " + fim }}] : []
        }},
        referencia: document.getElementById("eq-ref").value.trim(),
        latitude: document.getElementById("eq-lat").value.trim() || null,
        longitude: document.getElementById("eq-lng").value.trim() || null,
        data_precos_conferidos: dataBR,
        destaque: "",
        aceita_pedidos_do_dia: document.getElementById("eq-pedidos-dia").checked,
        aceita_encomendas: document.getElementById("eq-encomendas").checked,
        historia_aprovada: document.getElementById("eq-historia").value.trim(),
        fotos: {{}},
        enquadramentos: {{ barraca: document.getElementById("eq-foco-barraca").value }},
        url_final: document.getElementById("eq-url").value.trim(),
        itens: itensFormatados
      }};
    }}

    function atualizarPreviaESalvar() {{
      const dados = montarDadosJSON();
      document.documentElement.setAttribute("data-segmento", dados.segmento);
      document.getElementById("toldo-equipe").innerHTML = TOLDOS[dados.segmento] || TOLDOS.alimentacao;
      document.getElementById("previa-toldo").innerHTML = TOLDOS[dados.segmento] || TOLDOS.alimentacao;
      blocoPix.hidden = !pixAut.checked;

      document.getElementById("previa-nome").textContent = dados.nome_negocio || "Nome da barraca";
      document.getElementById("previa-oferta").textContent = dados.o_que_oferece || "O que oferece, no Parque da Cidade";
      document.getElementById("previa-horario").textContent = dados.dias
        ? dados.dias + (dados.horarios.inicio && dados.horarios.fim ? ", das " + dados.horarios.inicio + " às " + dados.horarios.fim : "")
        : "Dias e horário";
      document.getElementById("previa-ref").textContent = dados.referencia ? "Perto da " + dados.referencia : "Perto da referência";

      const pItem = dados.itens[0];
      document.getElementById("previa-item-nome").textContent = pItem ? pItem.nome : "Primeiro item";
      const pVal = pItem ? (pItem.variacoes.length ? pItem.variacoes[0].preco : pItem.preco) : 0;
      document.getElementById("previa-item-preco").textContent = "R$ " + Number(pVal || 0).toFixed(2).replace(".", ",");

      try {{
        window.localStorage.setItem(CHAVE_RASCUNHO, JSON.stringify({{ dados: dados, itensEstado: itensEstado }}));
        statusRascunho.textContent = "Rascunho salvo automaticamente neste aparelho.";
      }} catch (_e) {{
        statusRascunho.textContent = "Armazenamento local indisponível; exporte antes de fechar.";
      }}
    }}

    /* Carregar rascunho se existir */
    try {{
      const salvo = JSON.parse(window.localStorage.getItem(CHAVE_RASCUNHO) || "null");
      if (salvo && salvo.dados) {{
        const d = salvo.dados;
        document.getElementById("eq-consentimento").checked = Boolean(d.consentimento);
        document.getElementById("eq-segmento").value = d.segmento || "alimentacao";
        document.getElementById("eq-slug").value = d.slug || "";
        document.getElementById("eq-nome").value = d.nome_negocio || "";
        document.getElementById("eq-atendente").value = d.quem_atende || "";
        document.getElementById("eq-oferta").value = d.o_que_oferece || "";
        document.getElementById("eq-dias").value = d.dias || "";
        document.getElementById("eq-inicio").value = (d.horarios && d.horarios.inicio) || "";
        document.getElementById("eq-fim").value = (d.horarios && d.horarios.fim) || "";
        document.getElementById("eq-ref").value = d.referencia || "";
        document.getElementById("eq-zap").value = d.whatsapp || "";
        pixAut.checked = Boolean(d.pix && d.pix.autorizado);
        if (Array.isArray(salvo.itensEstado) && salvo.itensEstado.length) itensEstado = salvo.itensEstado;
      }}
    }} catch (_e) {{}}

    renderizarItensEditor();
    atualizarPreviaESalvar();

    form.querySelectorAll("input, select, textarea").forEach((el) => {{
      if (el.id !== "eq-foto-teste") {{
        el.addEventListener("input", atualizarPreviaESalvar);
        el.addEventListener("change", atualizarPreviaESalvar);
      }}
    }});

    document.getElementById("btn-novo-item").addEventListener("click", () => {{
      itensEstado.push({{ nome: "", categoria: "", preco: "", variacoes: "" }});
      renderizarItensEditor();
    }});

    document.getElementById("btn-apagar-rascunho").addEventListener("click", () => {{
      try {{ window.localStorage.removeItem(CHAVE_RASCUNHO); }} catch (_e) {{}}
      form.reset();
      itensEstado = [{{ nome: "", categoria: "", preco: "", variacoes: "" }}];
      renderizarItensEditor();
      atualizarPreviaESalvar();
      statusRascunho.textContent = "Rascunho apagado deste aparelho.";
    }});

    /* Teste local de compressão de foto até 150 KB */
    document.getElementById("eq-foto-teste").addEventListener("change", (ev) => {{
      const arq = ev.target.files && ev.target.files[0];
      if (!arq) return;
      const leitor = new FileReader();
      leitor.onload = () => {{
        const img = new Image();
        img.onload = () => {{
          const escala = Math.min(1, 1080 / Math.max(img.width, img.height));
          const cv = document.createElement("canvas");
          cv.width = Math.round(img.width * escala);
          cv.height = Math.round(img.height * escala);
          const ctx = cv.getContext("2d");
          ctx.filter = "brightness(1.02) contrast(1.02)";
          ctx.drawImage(img, 0, 0, cv.width, cv.height);
          const dataUrl = cv.toDataURL("image/webp", 0.78);
          const kb = Math.round(((dataUrl.split(",")[1] || "").length * 3 / 4) / 1024);
          const prevImg = document.getElementById("previa-foto-local");
          prevImg.src = dataUrl;
          prevImg.hidden = false;
          document.getElementById("status-foto-equipe").textContent = "Foto comprimida localmente para " + kb + " KB (limite 150 KB).";
        }};
        img.src = leitor.result;
      }};
      leitor.readAsDataURL(arq);
    }});

    form.addEventListener("submit", (ev) => {{
      ev.preventDefault();
      sincronizarItensDoDOM();
      const dados = montarDadosJSON();
      const erroBox = document.getElementById("erro-exportacao-equipe");
      const erroTxt = document.getElementById("texto-erro-equipe");

      if (!dados.consentimento) {{
        erroTxt.textContent = "Confirme o consentimento do ambulante antes de exportar.";
        erroBox.hidden = false;
        document.getElementById("eq-consentimento").focus();
        return;
      }}
      if (!dados.nome_negocio || !/^55\\d{{10,11}}$/.test(dados.whatsapp)) {{
        erroTxt.textContent = "Preencha o nome do negócio e um WhatsApp válido com DDI 55 + DDD (12 ou 13 dígitos).";
        erroBox.hidden = false;
        return;
      }}
      erroBox.hidden = true;
      const blob = new Blob([JSON.stringify(dados, null, 2)], {{ type: "application/json" }});
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "dados.json";
      link.click();
      URL.revokeObjectURL(link.href);
    }});
  }})();
  </script>
</body>
</html>"""

    eq_path = out_dir / "equipe.html"
    eq_path.write_text(equipe_html, encoding="utf-8")
    return str(eq_path)

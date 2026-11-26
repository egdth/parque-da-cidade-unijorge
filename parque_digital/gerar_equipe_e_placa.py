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


TEMPLATE_EQUIPE_HTML = r"""<!DOCTYPE html>
<html lang="pt-BR" data-segmento="alimentacao">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow">
  <title>Entrevista e Ficha de Campo — Equipe Unijorge · Toldo Aberto</title>
  <link rel="preload" href="fonts/fraunces-600-800-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="fonts/atkinson-hyperlegible-400-latin.woff2" as="font" type="font/woff2" crossorigin>
  <style>
__FONT_AND_TOKENS_CSS__
    .topo-equipe {
      background-color: var(--papel-2);
      border-bottom: 1.5px solid var(--linha);
      padding-block: var(--s-24);
    }
    .grade-equipe {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: var(--s-32);
      padding-block: var(--s-24) var(--s-96);
      align-items: start;
    }
    @media (min-width: 1040px) {
      .grade-equipe {
        grid-template-columns: repeat(12, minmax(0, 1fr));
      }
      .coluna-ficha { grid-column: 1 / 8; min-width: 0; }
      .coluna-previa {
        grid-column: 8 / 13;
        min-width: 0;
        position: sticky;
        top: var(--s-16);
        display: flex;
        flex-direction: column;
        gap: var(--s-16);
      }
    }
    .coluna-ficha,
    .coluna-previa {
      min-width: 0;
    }
    .barra-rascunho {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: var(--s-12);
      padding: var(--s-12) var(--s-16);
      background-color: var(--papel-2);
      border: 1.5px solid var(--linha);
      border-radius: var(--r-botao);
      margin-bottom: var(--s-24);
    }
    .barra-rascunho-acoes {
      display: flex;
      flex-wrap: wrap;
      gap: var(--s-8);
    }
    .bloco-ficha {
      background-color: var(--papel-2);
      border: 1.5px solid var(--linha);
      border-radius: var(--r-foto);
      padding: var(--s-16);
      margin-bottom: var(--s-24);
      display: flex;
      flex-direction: column;
      gap: var(--s-16);
      min-width: 0;
    }
    @media (min-width: 600px) {
      .bloco-ficha {
        padding: var(--s-24);
      }
    }
    .bloco-ficha > legend {
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-optical-sizing: auto;
      font-variation-settings: "SOFT" 45;
      font-size: clamp(1.25rem, 4vw, 1.55rem);
      line-height: 1.15;
      font-weight: 700;
      padding-inline: var(--s-8);
      color: var(--tinta);
    }
    .sub-fieldset {
      border: 0;
      padding: 0;
      margin: 0;
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: var(--s-8);
    }
    .sub-fieldset > legend {
      font-weight: 700;
      color: var(--tinta);
      margin-bottom: var(--s-4);
    }
    .pergunta-falada {
      background-color: var(--papel);
      border: 1px solid var(--linha);
      border-inline-start: 4px solid var(--acento);
      border-radius: 12px;
      padding: var(--s-12) var(--s-16);
      color: var(--tinta);
      font-size: 0.96875rem;
      line-height: 1.45;
    }
    .pergunta-falada strong {
      display: block;
      color: var(--apoio);
      font-size: 0.875rem;
      margin-bottom: 2px;
    }
    .campo-grupo {
      display: flex;
      flex-direction: column;
      align-items: stretch;
      gap: var(--s-4);
      min-width: 0;
    }
    .campo-grupo > label {
      font-weight: 700;
      color: var(--tinta);
    }
    .ajuda-campo {
      font-size: 0.9375rem;
      line-height: 1.45;
      color: var(--apoio);
    }
    .duas-colunas,
    .grade-escolhas {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: var(--s-12);
    }
    @media (min-width: 640px) {
      .duas-colunas,
      .grade-escolhas {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: var(--s-16);
      }
    }
    .opcao-controle {
      display: flex;
      align-items: flex-start;
      gap: var(--s-12);
      min-height: 48px;
      padding: var(--s-12) var(--s-16);
      background-color: var(--papel);
      border: 1.5px solid var(--linha);
      border-radius: var(--r-botao);
      transition: border-color 150ms ease-out, background-color 150ms ease-out;
    }
    .opcao-controle--destaque {
      border: 2px solid var(--tinta);
    }
    .opcao-controle:has(input:checked) {
      border-color: var(--acento);
      border-width: 2px;
    }
    .opcao-controle input[type="checkbox"],
    .opcao-controle input[type="radio"] {
      width: 22px;
      height: 22px;
      min-width: 22px;
      min-height: 22px;
      margin-top: 2px;
      accent-color: var(--mata);
      flex-shrink: 0;
      cursor: pointer;
    }
    .opcao-controle label {
      flex: 1 1 auto;
      font-weight: 700;
      line-height: 1.35;
      cursor: pointer;
      padding-block: 10px;
      margin-block: -10px;
    }
    .opcao-controle label span.subtexto-opcao {
      display: block;
      font-weight: 400;
      font-size: 0.9375rem;
      color: var(--apoio);
      margin-top: 2px;
    }
    .item-editor,
    .slot-foto-card,
    .subbloco-branco {
      background-color: var(--papel);
      border: 1.5px solid var(--linha);
      border-radius: var(--r-botao);
      padding: var(--s-12);
      display: flex;
      flex-direction: column;
      gap: var(--s-12);
      min-width: 0;
    }
    @media (min-width: 600px) {
      .item-editor,
      .slot-foto-card,
      .subbloco-branco {
        padding: var(--s-16);
      }
    }
    .item-editor-topo {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: var(--s-8);
      padding-bottom: var(--s-8);
      border-bottom: 1px solid var(--linha);
    }
    .linha-subitem {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: var(--s-8);
      padding: var(--s-12);
      background-color: var(--papel-2);
      border: 1px solid var(--linha);
      border-radius: 12px;
      align-items: end;
    }
    @media (min-width: 640px) {
      .linha-subitem {
        grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) auto;
      }
    }
    .miniatura-upload {
      width: 96px;
      height: 72px;
      object-fit: cover;
      border-radius: 10px;
      border: 1.5px solid var(--linha);
      background-color: var(--papel-2);
    }
    .painel-lateral-bloco {
      background-color: var(--papel);
      border: 2px solid var(--tinta);
      border-radius: var(--r-foto);
      padding: var(--s-16);
      display: flex;
      flex-direction: column;
      gap: var(--s-12);
      min-width: 0;
    }
    @media (min-width: 600px) {
      .painel-lateral-bloco {
        padding: var(--s-24);
      }
    }
    .selo-prontidao {
      display: inline-flex;
      align-items: center;
      align-self: flex-start;
      gap: var(--s-8);
      padding: var(--s-8) var(--s-12);
      border-radius: var(--r-pilula);
      font-size: 0.9375rem;
      font-weight: 700;
      border: 1.5px solid var(--tinta);
      background-color: var(--sol);
      color: var(--tinta);
    }
    .selo-prontidao.pronto {
      background-color: var(--mata);
      border-color: var(--mata);
      color: #FFFFFF;
    }
    .lista-pendencias {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: var(--s-4);
      font-size: 0.9375rem;
    }
    .lista-pendencias li {
      display: flex;
      align-items: flex-start;
      gap: var(--s-8);
    }
    .cartao-previa-ao-vivo {
      background-color: var(--papel);
      border: 2px solid var(--tinta);
      border-radius: var(--r-foto);
      overflow: hidden;
    }
    .previa-miolo {
      padding: var(--s-16);
      display: flex;
      flex-direction: column;
      gap: var(--s-12);
    }
    @media (min-width: 600px) {
      .previa-miolo {
        padding: var(--s-24);
      }
    }
    .caixa-codigo-saida {
      font-family: ui-monospace, "Cascadia Mono", Consolas, monospace;
      font-size: 1rem;
      line-height: 1.45;
      background-color: var(--papel-2);
      color: var(--tinta);
      border: 1.5px solid var(--linha);
      border-radius: 12px;
      padding: var(--s-12);
      width: 100%;
      max-width: 100%;
      min-height: 150px;
      resize: vertical;
      overflow-wrap: anywhere;
    }
    .par-copia {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: var(--s-8);
    }
    /* Bolha mantida na árvore de acessibilidade com opacity (nunca display:none) para anúncio imediato */
    .bolha-status-copia {
      display: inline-flex;
      align-items: center;
      min-height: 36px;
      padding: var(--s-4) var(--s-12);
      border-radius: var(--r-pilula);
      background-color: var(--mata-escura);
      color: var(--papel);
      font-size: 0.9375rem;
      font-weight: 700;
      opacity: 0;
      pointer-events: none;
      transition: opacity 160ms ease-out;
    }
    .bolha-status-copia.visivel {
      opacity: 1;
    }
    .bolha-status-copia.falha {
      background-color: var(--erro);
      color: #FFFFFF;
    }
    .aviso-exportacao {
      padding: var(--s-16);
      background-color: var(--papel-2);
      border: 2px solid var(--tinta);
      border-radius: var(--r-botao);
      font-weight: 700;
    }
    details.detalhes-json summary {
      min-height: 48px;
      display: flex;
      align-items: center;
      font-weight: 700;
      cursor: pointer;
      padding-block: var(--s-8);
    }
    .campo-entrada[type="file"] {
      padding-block: 9px;
    }
    .botao-compacto {
      padding-inline: var(--s-16);
      font-size: 0.96875rem;
    }
  </style>
</head>
<body>
  <div id="toldo-equipe">__TOLDO_INICIAL_34__</div>

  <header class="topo-equipe">
    <div class="conteiner">
      <p class="texto-apoio">Uso interno dos grupos extensionistas Unijorge · Página separada fora do menu do cliente · Zero senhas</p>
      <h1 id="titulo-form-equipe" class="titulo-secao" style="margin-top: var(--s-8);">Roteiro de entrevista e ficha do ambulante</h1>
      <p class="texto-apoio" style="margin-top: var(--s-8);">
        Faça as perguntas abaixo diretamente na barraca. Ao preencher, a página monta sozinha o <strong>prompt completo para colar no chat</strong> e o arquivo <strong><code>dados.json</code></strong> com 100% dos campos do site e da Placa A5.
      </p>
    </div>
  </header>

  <main class="conteiner grade-equipe">
    <form id="form-equipe" class="coluna-ficha" aria-labelledby="titulo-form-equipe" novalidate>
      <div class="barra-rascunho">
        <span id="status-rascunho" role="status" class="texto-apoio" style="font-weight: 700;">Rascunho salvo automaticamente neste aparelho.</span>
        <div class="barra-rascunho-acoes">
          <input type="file" id="eq-importar-json" accept="application/json,.json" hidden>
          <button type="button" class="botao botao-contorno botao-compacto" id="btn-importar-json">
            __IC_PEDIDO__<span>Carregar dados.json</span>
          </button>
          <button type="button" class="botao botao-contorno botao-compacto" id="btn-exemplo-treino">
            __IC_CONFERE__<span>Preencher treino</span>
          </button>
          <button type="button" class="botao botao-contorno botao-compacto" id="btn-apagar-rascunho">
            __IC_LIXEIRA__<span>Apagar rascunho</span>
          </button>
        </div>
      </div>

      <!-- BLOCO 1: CONSENTIMENTO, SEGMENTO E IDENTIFICAÇÃO -->
      <fieldset class="bloco-ficha">
        <legend>1. Consentimento, segmento e nome na placa</legend>

        <div class="pergunta-falada" id="ajuda-consentimento">
          <strong>Pergunta 1 — Leia em voz alta antes de anotar qualquer dado:</strong>
          “Este site e a placa com QR Code são gratuitos, feitos pelo projeto de extensão da Unijorge para divulgar seu trabalho aqui no Parque da Cidade. Não tem taxa, não pede senha e o(a) senhor(a) pode pedir correção de preço, troca de foto ou retirada do ar quando quiser. Podemos criar sua página?”
        </div>

        <div class="opcao-controle opcao-controle--destaque">
          <input type="checkbox" id="eq-consentimento" name="consentimento" aria-describedby="ajuda-consentimento erro-campo-consentimento" required>
          <label for="eq-consentimento">
            Autorização verbal confirmada pelo(a) ambulante titular. *
            <span class="subtexto-opcao">Obrigatório para gerar o site real em modo de produção.</span>
          </label>
        </div>
        <p class="mensagem-erro" id="erro-campo-consentimento" role="alert" hidden>
          __IC_ALERTA__<span>Confirme a autorização verbal do(a) ambulante antes de exportar.</span>
        </p>

        <div class="opcao-controle">
          <input type="checkbox" id="eq-modo-exemplo" name="modo_exemplo">
          <label for="eq-modo-exemplo">
            Simulação em sala de aula (<code>modo_exemplo = true</code>)
            <span class="subtexto-opcao">Deixe desmarcado para ambulante real. Quando marcado, desativa o envio real ao WhatsApp e exibe o selo demonstrativo.</span>
          </label>
        </div>

        <fieldset class="sub-fieldset">
          <legend>Qual é o segmento principal da barraca ou serviço no parque? *</legend>
          <div class="grade-escolhas">
            <div class="opcao-controle">
              <input type="radio" id="seg-alimentacao" name="segmento" value="alimentacao" checked>
              <label for="seg-alimentacao">
                Alimentação e bebidas
                <span class="subtexto-opcao">Cardápio por categorias, variações e comanda no WhatsApp</span>
              </label>
            </div>
            <div class="opcao-controle">
              <input type="radio" id="seg-brinquedos" name="segmento" value="brinquedos">
              <label for="seg-brinquedos">
                Brinquedos e doces
                <span class="subtexto-opcao">Grade de produtos com faixa de idade indicada</span>
              </label>
            </div>
            <div class="opcao-controle">
              <input type="radio" id="seg-inflaveis" name="segmento" value="inflaveis">
              <label for="seg-inflaveis">
                Infláveis e pula-pula
                <span class="subtexto-opcao">Tempo da sessão, idade, altura permitida e regras</span>
              </label>
            </div>
            <div class="opcao-controle">
              <input type="radio" id="seg-bicicletas" name="segmento" value="bicicletas">
              <label for="seg-bicicletas">
                Aluguel de bicicletas
                <span class="subtexto-opcao">Tabela por modelo e tempo + documento, caução e devolução</span>
              </label>
            </div>
          </div>
        </fieldset>

        <div class="pergunta-falada" id="ajuda-nome-atendente">
          <strong>Perguntas 2 e 3 — Pergunte ao ambulante:</strong>
          “Como o(a) senhor(a) quer que o nome da barraca apareça bem grande no topo do site e na placa impressa? E como gosta de ser chamado(a) pelos clientes aqui no parque?”
        </div>

        <div class="duas-colunas">
          <div class="campo-grupo">
            <label for="eq-nome">Nome do negócio no letreiro *</label>
            <input type="text" id="eq-nome" name="nome_negocio" class="campo-entrada" autocomplete="organization" aria-describedby="ajuda-nome-atendente erro-campo-nome" placeholder="Ex.: Pastel da Dona Nalva" required>
            <p class="mensagem-erro" id="erro-campo-nome" role="alert" hidden>
              __IC_ALERTA__<span>Informe o nome real do negócio (não use “Barraca Exemplo” em produção).</span>
            </p>
          </div>
          <div class="campo-grupo">
            <label for="eq-atendente">Como quem atende é chamado(a)</label>
            <input type="text" id="eq-atendente" name="quem_atende" class="campo-entrada" autocomplete="name" placeholder="Ex.: Dona Nalva e família">
          </div>
        </div>

        <div class="pergunta-falada" id="ajuda-oferta">
          <strong>Pergunta 4 — Pergunte ao ambulante:</strong>
          “Em uma frase curta, quais são as 2 ou 3 coisas principais que você vende ou aluga aqui no Parque da Cidade?”
        </div>

        <div class="campo-grupo">
          <label for="eq-oferta">Frase principal do que oferece no parque *</label>
          <input type="text" id="eq-oferta" name="o_que_oferece" class="campo-entrada" aria-describedby="ajuda-oferta erro-campo-oferta" placeholder="Ex.: Pastel frito na hora, caldo de cana e açaí na tigela, no Parque da Cidade" required>
          <p class="mensagem-erro" id="erro-campo-oferta" role="alert" hidden>
            __IC_ALERTA__<span>Resuma em uma frase curta o que a barraca oferece.</span>
          </p>
        </div>

        <div class="duas-colunas">
          <div class="campo-grupo">
            <label for="eq-slug">Identificador curto do endereço (slug) *</label>
            <input type="text" id="eq-slug" name="slug" class="campo-entrada" autocorrect="off" autocapitalize="none" spellcheck="false" aria-describedby="ajuda-slug" placeholder="Ex.: pastel-da-dona-nalva" required>
            <span id="ajuda-slug" class="ajuda-campo">Gerado automaticamente a partir do nome; ajuste se desejar.</span>
          </div>
          <div class="campo-grupo">
            <label for="eq-url">Endereço final do site (para o QR Code da Placa A5) *</label>
            <input type="url" id="eq-url" name="url_final" class="campo-entrada" autocorrect="off" autocapitalize="none" spellcheck="false" aria-describedby="ajuda-url" placeholder="https://pastel-da-dona-nalva.vercel.app/" required>
            <span id="ajuda-url" class="ajuda-campo">Usado no QR Code impresso e no botão Compartilhar.</span>
          </div>
        </div>
      </fieldset>

      <!-- BLOCO 2: DIAS, HORÁRIOS E LOCALIZAÇÃO -->
      <fieldset class="bloco-ficha">
        <legend>2. Dias, horários e como achar no parque</legend>

        <div class="pergunta-falada" id="ajuda-horarios">
          <strong>Pergunta 5 — Pergunte ao ambulante:</strong>
          “Quais dias da semana você costuma trabalhar aqui, e de que horas até que horas? O horário muda entre dia de semana e sábado, domingo ou feriado?”
        </div>

        <div class="duas-colunas">
          <div class="campo-grupo">
            <label for="eq-dias">Resumo dos dias na abertura do site *</label>
            <input type="text" id="eq-dias" name="dias" class="campo-entrada" aria-describedby="ajuda-horarios erro-campo-dias" placeholder="Ex.: Quinta a domingo e feriados" required>
            <p class="mensagem-erro" id="erro-campo-dias" role="alert" hidden>
              __IC_ALERTA__<span>Informe os dias habituais de funcionamento.</span>
            </p>
          </div>
          <div class="duas-colunas">
            <div class="campo-grupo">
              <label for="eq-inicio">Abre às *</label>
              <input type="text" id="eq-inicio" name="inicio" class="campo-entrada" placeholder="Ex.: 08h" required>
            </div>
            <div class="campo-grupo">
              <label for="eq-fim">Fecha às *</label>
              <input type="text" id="eq-fim" name="fim" class="campo-entrada" placeholder="Ex.: 17h" required>
            </div>
          </div>
        </div>

        <div class="subbloco-branco">
          <div>
            <p style="font-weight: 700;">Linhas da tabela “Como chegar” (se o horário variar por dia)</p>
            <p class="ajuda-campo">Se todos os dias tiverem o mesmo horário acima, não precisa adicionar linhas extras: a página preenche sozinha. Se sábado/domingo tiver horário diferente, adicione abaixo.</p>
          </div>
          <div id="lista-horarios-tabela" style="display:flex;flex-direction:column;gap:var(--s-8);"></div>
          <div>
            <button type="button" class="botao botao-contorno botao-compacto" id="btn-add-horario">
              __IC_MAIS__<span>Adicionar faixa de horário na tabela</span>
            </button>
          </div>
        </div>

        <div class="pergunta-falada" id="ajuda-ref">
          <strong>Pergunta 6 — Pergunte ao ambulante:</strong>
          “Se alguém entrar no Parque da Cidade procurando você, qual é o ponto de referência mais fácil de achar?”
        </div>

        <div class="campo-grupo">
          <label for="eq-ref">Ponto de referência dentro do Parque da Cidade *</label>
          <input type="text" id="eq-ref" name="referencia" class="campo-entrada" aria-describedby="ajuda-ref dica-ref erro-campo-ref" placeholder="Ex.: entrada principal, ao lado da sombra das amendoeiras" required>
          <span id="dica-ref" class="ajuda-campo">Escreva sem “Perto da” no começo (o site já escreve “Perto da ...” automaticamente).</span>
          <p class="mensagem-erro" id="erro-campo-ref" role="alert" hidden>
            __IC_ALERTA__<span>Descreva o ponto de referência no Parque da Cidade.</span>
          </p>
        </div>

        <div class="subbloco-branco">
          <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:var(--s-12);">
            <div>
              <p style="font-weight: 700;">Pergunta 7 — Coordenadas GPS exatas da barraca (opcional)</p>
              <p class="ajuda-campo">Ativa o botão “Como chegar” direto no mapa. Se estiver na barraca agora, capture pelo GPS do celular.</p>
            </div>
            <button type="button" class="botao botao-contorno botao-compacto" id="btn-capturar-gps">
              __IC_CHEGAR__<span>Capturar GPS aqui na barraca</span>
            </button>
          </div>
          <p id="status-gps" role="status" class="ajuda-campo"></p>
          <div class="duas-colunas">
            <div class="campo-grupo">
              <label for="eq-lat">Latitude (decimal)</label>
              <input type="text" id="eq-lat" name="latitude" class="campo-entrada" inputmode="decimal" autocorrect="off" spellcheck="false" placeholder="Ex.: -12.9949">
            </div>
            <div class="campo-grupo">
              <label for="eq-lng">Longitude (decimal)</label>
              <input type="text" id="eq-lng" name="longitude" class="campo-entrada" inputmode="decimal" autocorrect="off" spellcheck="false" placeholder="Ex.: -38.4611">
            </div>
          </div>
        </div>
      </fieldset>

      <!-- BLOCO 3: WHATSAPP, PAGAMENTO E PIX -->
      <fieldset class="bloco-ficha">
        <legend>3. WhatsApp, formas de pagamento e Pix</legend>

        <div class="pergunta-falada" id="ajuda-zap">
          <strong>Pergunta 8 — Pergunte ao ambulante:</strong>
          “Qual é o número de WhatsApp com DDD que vai receber os pedidos ou dúvidas dos clientes? Podemos mandar um ‘oi’ para conferir se está certinho?”
        </div>

        <div class="campo-grupo">
          <label for="eq-zap">WhatsApp de atendimento com DDD *</label>
          <input type="text" id="eq-zap" name="whatsapp" class="campo-entrada" inputmode="numeric" autocomplete="tel" autocorrect="off" spellcheck="false" aria-describedby="ajuda-zap dica-zap erro-campo-zap" placeholder="Ex.: 71 99123-4567 ou 5571991234567" required>
          <span id="dica-zap" class="ajuda-campo">Pode digitar só DDD + número: a ficha acrescenta o código 55 do Brasil automaticamente.</span>
          <p class="mensagem-erro" id="erro-campo-zap" role="alert" hidden>
            __IC_ALERTA__<span>Digite um WhatsApp válido com DDD (10 ou 11 dígitos, ou 12/13 começando com 55).</span>
          </p>
        </div>

        <div class="pergunta-falada">
          <strong>Pergunta 9 — Pergunte ao ambulante:</strong>
          “Quais formas de pagamento você aceita aqui na barraca?”
        </div>

        <fieldset class="sub-fieldset">
          <legend>Formas de pagamento aceitas *</legend>
          <div class="grade-escolhas">
            <div class="opcao-controle">
              <input type="checkbox" id="pag-dinheiro" name="pagamento_opcao" value="Dinheiro" checked>
              <label for="pag-dinheiro">Dinheiro</label>
            </div>
            <div class="opcao-controle">
              <input type="checkbox" id="pag-debito" name="pagamento_opcao" value="Cartão de débito">
              <label for="pag-debito">Cartão de débito</label>
            </div>
            <div class="opcao-controle">
              <input type="checkbox" id="pag-credito" name="pagamento_opcao" value="Cartão de crédito">
              <label for="pag-credito">Cartão de crédito</label>
            </div>
            <div class="opcao-controle">
              <input type="checkbox" id="pag-aprox" name="pagamento_opcao" value="Cartão por aproximação" checked>
              <label for="pag-aprox">Cartão por aproximação</label>
            </div>
            <div class="opcao-controle">
              <input type="checkbox" id="pag-pix-presencial" name="pagamento_opcao" value="Pix na barraca" checked>
              <label for="pag-pix-presencial">Pix na barraca</label>
            </div>
          </div>
          <div class="campo-grupo" style="margin-top: var(--s-8);">
            <label for="eq-pag-outros">Outras formas ou observação de pagamento (opcional, separe por vírgula)</label>
            <input type="text" id="eq-pag-outros" name="pagamento_outros" class="campo-entrada" placeholder="Ex.: Vale-refeição, Pix no QR da maquininha">
          </div>
        </fieldset>

        <div class="pergunta-falada">
          <strong>Pergunta 10 — Pergunte ao ambulante:</strong>
          “Você quer deixar sua chave Pix escrita no site com botão de copiar, ou prefere passar o Pix só na hora/conversa?”
        </div>

        <div class="opcao-controle opcao-controle--destaque">
          <input type="checkbox" id="eq-pix-aut" name="pix_autorizado" aria-controls="bloco-campos-pix" aria-expanded="false">
          <label for="eq-pix-aut">
            O(a) ambulante autorizou exibir a chave Pix e o nome do recebedor na página pública.
            <span class="subtexto-opcao">Se não autorizar, o site informa que aceita Pix na barraca sem expor chave nem CPF/telefone.</span>
          </label>
        </div>

        <div class="subbloco-branco" id="bloco-campos-pix" hidden>
          <div class="duas-colunas">
            <div class="campo-grupo">
              <label for="eq-pix-nome">Nome do recebedor como aparece no banco *</label>
              <input type="text" id="eq-pix-nome" name="pix_recebedor" class="campo-entrada" aria-describedby="erro-campo-pix" placeholder="Ex.: Maria Nalva dos Santos">
            </div>
            <div class="campo-grupo">
              <label for="eq-pix-chave">Chave Pix exata *</label>
              <input type="text" id="eq-pix-chave" name="pix_chave" class="campo-entrada" autocorrect="off" autocapitalize="none" spellcheck="false" aria-describedby="erro-campo-pix" placeholder="Celular, e-mail, CPF/CNPJ ou chave aleatória">
            </div>
          </div>
          <p class="ajuda-campo">O site exibe “Confira o nome antes de pagar” junto ao recebedor para segurança do cliente e do ambulante.</p>
          <p class="mensagem-erro" id="erro-campo-pix" role="alert" hidden>
            __IC_ALERTA__<span>Para exibir o Pix no site, preencha tanto o nome do recebedor quanto a chave Pix.</span>
          </p>
        </div>
      </fieldset>

      <!-- BLOCO 4: PEDIDOS, ENCOMENDAS E REGRAS DO SEGMENTO -->
      <fieldset class="bloco-ficha">
        <legend>4. Pedidos no WhatsApp, encomendas e regras</legend>

        <div class="campo-grupo" style="max-width: 320px;">
          <label for="eq-data-precos">Data em que os preços foram conferidos *</label>
          <input type="date" id="eq-data-precos" name="data_precos" class="campo-entrada" required>
          <span class="ajuda-campo">Aparece no selo “Preços conferidos em DD/MM/AAAA”.</span>
        </div>

        <div class="pergunta-falada">
          <strong>Pergunta 11 — Pergunte ao ambulante:</strong>
          “No dia de movimento, o cliente pode montar o pedido pelo site para abrir pronto no seu WhatsApp? E você aceita encomendas antecipadas para aniversários, piqueniques ou grupos?”
        </div>

        <div class="duas-colunas">
          <div class="opcao-controle" id="wrap-pedidos-dia">
            <input type="checkbox" id="eq-pedidos-dia" name="aceita_pedidos_do_dia" checked>
            <label for="eq-pedidos-dia">
              Ativar comanda de pedidos do dia (Alimentação)
              <span class="subtexto-opcao">Permite somar itens, escolher sabor/tamanho e abrir pedido pronto no WhatsApp.</span>
            </label>
          </div>
          <div class="opcao-controle">
            <input type="checkbox" id="eq-encomendas" name="aceita_encomendas" checked>
            <label for="eq-encomendas">
              Aceita encomendas ou reservas para grupos
              <span class="subtexto-opcao">Exibe o formulário de orçamento para piqueniques, aniversários e excursões.</span>
            </label>
          </div>
        </div>

        <div class="subbloco-branco" id="bloco-regras-aluguel" hidden>
          <div class="pergunta-falada">
            <strong>Pergunta 12 (exclusiva para Aluguel de bicicletas):</strong>
            “Qual documento o cliente precisa apresentar no cadastro? Vocês cobram caução? E qual é a regra e horário limite para devolver a bicicleta?”
          </div>
          <div class="campo-grupo">
            <label for="eq-regra-doc">Documento exigido no cadastro *</label>
            <input type="text" id="eq-regra-doc" name="regra_documento" class="campo-entrada" placeholder="Ex.: Apresentação de documento oficial com foto do responsável.">
          </div>
          <div class="duas-colunas">
            <div class="campo-grupo">
              <label for="eq-regra-caucao">Regra de caução *</label>
              <input type="text" id="eq-regra-caucao" name="regra_caucao" class="campo-entrada" placeholder="Ex.: Não cobramos caução em dinheiro.">
            </div>
            <div class="campo-grupo">
              <label for="eq-regra-devolucao">Local e horário limite de devolução *</label>
              <input type="text" id="eq-regra-devolucao" name="regra_devolucao" class="campo-entrada" placeholder="Ex.: Devolução no mesmo ponto até as 17h.">
            </div>
          </div>
          <p class="mensagem-erro" id="erro-campo-regras-bike" role="alert" hidden>
            __IC_ALERTA__<span>Preencha pelo menos uma regra de documento, caução ou devolução para o aluguel de bicicletas.</span>
          </p>
        </div>
      </fieldset>

      <!-- BLOCO 5: CATÁLOGO DE ITENS, PREÇOS E VARIAÇÕES -->
      <fieldset class="bloco-ficha">
        <legend>5. Catálogo completo de itens, variações e preços</legend>

        <div class="pergunta-falada" id="dica-catalogo-segmento">
          <strong>Pergunta 13 — Pergunte ao ambulante:</strong>
          “Quais produtos nunca faltam na sua barraca? Para cada um, diga o nome, uma descrição curtinha de como é servido, o preço (ou sabores/tamanhos) e qual deles é o Destaque da casa.”
        </div>

        <div id="lista-itens-equipe" style="display:flex;flex-direction:column;gap:var(--s-16);"></div>

        <p class="mensagem-erro" id="erro-campo-itens" role="alert" hidden>
          __IC_ALERTA__<span id="texto-erro-itens">Cadastre pelo menos 1 item com nome e preço válido.</span>
        </p>

        <div>
          <button type="button" class="botao botao-contorno" id="btn-novo-item">
            __IC_MAIS__<span id="rotulo-btn-novo-item">Adicionar item ao catálogo</span>
          </button>
        </div>
      </fieldset>

      <!-- BLOCO 6: HISTÓRIA APROVADA E FOTOS -->
      <fieldset class="bloco-ficha">
        <legend>6. Frase de quem atende e fotos com enquadramento</legend>

        <div class="pergunta-falada" id="ajuda-historia">
          <strong>Pergunta 14 — Pergunte e leia de volta para aprovar:</strong>
          “Tem uma frase curtinha contando seu carinho pelo trabalho ou sua história aqui no Parque da Cidade que você queira mostrar no site?” (Anote com as palavras da pessoa e leia em voz alta para ela aprovar; se preferir não ter, deixe em branco.)
        </div>

        <div class="campo-grupo">
          <label for="eq-historia">Frase curta aprovada por quem atende (opcional)</label>
          <textarea id="eq-historia" name="historia_aprovada" rows="3" class="campo-entrada" aria-describedby="ajuda-historia" placeholder="Ex.: Chego cedo para abrir a massa na sombra das amendoeiras e atender quem passeia no parque com comida feita na hora."></textarea>
        </div>

        <div class="pergunta-falada">
          <strong>Passo 15 — Fotos opcionais da barraca (comprimidas automaticamente no aparelho até 120 KB):</strong>
          Nenhuma foto é obrigatória (o site adapta o layout sem imagem vazia). Se tirar fotos agora neste aparelho, anexe abaixo para comprimir em <code>.webp</code> e já preencher os nomes exatos no <code>dados.json</code>. Se outro colega tirou a foto em outra câmera, marque a caixa de referência correspondente.
        </div>

        <!-- Foto 1: Barraca (Primeira tela) -->
        <div class="slot-foto-card">
          <p style="font-weight: 700;">Foto 1 — Abertura / Barraca (<code>barraca.webp</code> · horizontal)</p>
          <div class="duas-colunas">
            <div class="campo-grupo">
              <label for="eq-file-barraca">Selecionar foto da barraca</label>
              <input type="file" id="eq-file-barraca" name="arquivo_barraca" accept="image/*" class="campo-entrada">
            </div>
            <div class="campo-grupo">
              <label for="eq-foco-barraca">Enquadramento de corte</label>
              <select id="eq-foco-barraca" name="foco_barraca" class="campo-entrada">
                <option value="topo" selected>Topo (protege rostos e letreiro)</option>
                <option value="centro">Centro</option>
                <option value="base">Base (foco no balcão/produto)</option>
              </select>
            </div>
          </div>
          <div class="opcao-controle">
            <input type="checkbox" id="eq-ref-foto-barraca" name="incluir_foto_barraca">
            <label for="eq-ref-foto-barraca">Referenciar <code>barraca.webp</code> no <code>dados.json</code></label>
          </div>
          <div id="info-foto-barraca" style="display:flex;flex-wrap:wrap;align-items:center;gap:var(--s-12);" hidden>
            <img id="thumb-foto-barraca" class="miniatura-upload" alt="Miniatura da foto da barraca">
            <span id="txt-foto-barraca" class="ajuda-campo" style="font-weight:700;"></span>
            <button type="button" class="botao botao-contorno botao-compacto" data-baixar-foto="barraca">__IC_PEDIDO__<span>Baixar barraca.webp</span></button>
            <button type="button" class="botao botao-contorno botao-compacto" data-limpar-foto="barraca">__IC_LIXEIRA__<span>Remover</span></button>
          </div>
        </div>

        <!-- Foto 2: Fachada / Entorno (Como chegar) -->
        <div class="slot-foto-card">
          <p style="font-weight: 700;">Foto 2 — Vista aberta do ponto em “Como chegar” (<code>fachada.webp</code> · opcional)</p>
          <div class="duas-colunas">
            <div class="campo-grupo">
              <label for="eq-file-fachada">Selecionar foto do ponto/entorno</label>
              <input type="file" id="eq-file-fachada" name="arquivo_fachada" accept="image/*" class="campo-entrada">
            </div>
            <div class="campo-grupo">
              <label for="eq-foco-fachada">Enquadramento de corte</label>
              <select id="eq-foco-fachada" name="foco_fachada" class="campo-entrada">
                <option value="centro" selected>Centro</option>
                <option value="topo">Topo</option>
                <option value="base">Base</option>
              </select>
            </div>
          </div>
          <div class="opcao-controle">
            <input type="checkbox" id="eq-ref-foto-fachada" name="incluir_foto_fachada">
            <label for="eq-ref-foto-fachada">Referenciar <code>fachada.webp</code> no <code>dados.json</code></label>
          </div>
          <div id="info-foto-fachada" style="display:flex;flex-wrap:wrap;align-items:center;gap:var(--s-12);" hidden>
            <img id="thumb-foto-fachada" class="miniatura-upload" alt="Miniatura da foto da fachada">
            <span id="txt-foto-fachada" class="ajuda-campo" style="font-weight:700;"></span>
            <button type="button" class="botao botao-contorno botao-compacto" data-baixar-foto="fachada">__IC_PEDIDO__<span>Baixar fachada.webp</span></button>
            <button type="button" class="botao botao-contorno botao-compacto" data-limpar-foto="fachada">__IC_LIXEIRA__<span>Remover</span></button>
          </div>
        </div>

        <!-- Foto 3: Retrato (Quem atende) -->
        <div class="slot-foto-card">
          <p style="font-weight: 700;">Foto 3 — Retrato em “Quem atende” (<code>retrato.webp</code> · vertical 4:5 · opcional)</p>
          <div class="duas-colunas">
            <div class="campo-grupo">
              <label for="eq-file-retrato">Selecionar retrato autorizado</label>
              <input type="file" id="eq-file-retrato" name="arquivo_retrato" accept="image/*" class="campo-entrada">
            </div>
            <div class="campo-grupo">
              <label for="eq-foco-retrato">Enquadramento de corte</label>
              <select id="eq-foco-retrato" name="foco_retrato" class="campo-entrada">
                <option value="topo" selected>Topo (protege cabeça e olhar)</option>
                <option value="centro">Centro</option>
                <option value="base">Base</option>
              </select>
            </div>
          </div>
          <div class="opcao-controle">
            <input type="checkbox" id="eq-ref-foto-retrato" name="incluir_foto_retrato">
            <label for="eq-ref-foto-retrato">Referenciar <code>retrato.webp</code> no <code>dados.json</code></label>
          </div>
          <div id="info-foto-retrato" style="display:flex;flex-wrap:wrap;align-items:center;gap:var(--s-12);" hidden>
            <img id="thumb-foto-retrato" class="miniatura-upload" alt="Miniatura do retrato">
            <span id="txt-foto-retrato" class="ajuda-campo" style="font-weight:700;"></span>
            <button type="button" class="botao botao-contorno botao-compacto" data-baixar-foto="retrato">__IC_PEDIDO__<span>Baixar retrato.webp</span></button>
            <button type="button" class="botao botao-contorno botao-compacto" data-limpar-foto="retrato">__IC_LIXEIRA__<span>Remover</span></button>
          </div>
        </div>

        <p class="ajuda-campo" id="status-foto-equipe" role="status"></p>
      </fieldset>

      <div class="mensagem-erro" id="erro-exportacao-equipe" role="alert" tabindex="-1" hidden>
        __IC_ALERTA__<span id="texto-erro-equipe">Revise os campos obrigatórios destacados acima antes de exportar.</span>
      </div>

      <div style="display:flex;flex-wrap:wrap;gap:var(--s-12);">
        <button type="submit" class="botao botao-mata" id="btn-exportar-dados">
          __IC_PEDIDO__<span>Exportar dados.json completo</span>
        </button>
        <button type="button" class="botao botao-contorno" id="btn-baixar-prompt-txt">
          __IC_COMPARTILHAR__<span>Baixar prompt (.txt)</span>
        </button>
        <button type="button" class="botao botao-contorno" id="btn-baixar-todas-fotos" hidden>
          __IC_CONFERE__<span>Baixar fotos .webp otimizadas</span>
        </button>
      </div>

      <p class="aviso-exportacao" style="margin-top: var(--s-16);">
        Exportar não publica o site. O arquivo <code>dados.json</code> (e as fotos <code>.webp</code>, se houver) ou o prompt copiado devem passar pela compilação e revisão da equipe Unijorge antes de ir ao ar.
      </p>
    </form>

    <!-- COLUNA LATERAL: PRONTIDÃO + PRÉVIA + PROMPT PRONTO + JSON -->
    <aside class="coluna-previa" aria-labelledby="titulo-previa-equipe">
      <div class="painel-lateral-bloco">
        <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:var(--s-8);">
          <h2 id="titulo-previa-equipe" class="nome-item">Conferência da coleta</h2>
          <span id="selo-prontidao" class="selo-prontidao" role="status">Pendente</span>
        </div>
        <ul id="lista-pendencias" class="lista-pendencias"></ul>
      </div>

      <div class="painel-lateral-bloco">
        <h2 class="nome-item">Prompt pronto para colar no chat</h2>
        <p class="ajuda-campo">
          Contém todas as respostas organizadas + instruções do sistema Toldo Aberto + o <code>dados.json</code> completo embutido. Basta copiar e colar na conversa sem precisar responder mais nada depois.
        </p>
        <label for="prompt-gerado-chat" class="ajuda-campo" style="font-weight:700;color:var(--tinta);">Texto completo do prompt</label>
        <textarea id="prompt-gerado-chat" class="caixa-codigo-saida" rows="9" readonly></textarea>
        <div class="par-copia">
          <button type="button" class="botao botao-mata botao-compacto" command="--copy" commandfor="prompt-gerado-chat" id="btn-copiar-prompt">
            __IC_COPIAR__<span>Copiar prompt completo</span>
          </button>
          <span class="bolha-status-copia" role="status" id="status-copia-prompt"></span>
        </div>

        <details class="detalhes-json">
          <summary>Ver e copiar somente o arquivo dados.json</summary>
          <div style="display:flex;flex-direction:column;gap:var(--s-8);margin-top:var(--s-8);">
            <label for="json-gerado-previa" class="ajuda-campo" style="font-weight:700;color:var(--tinta);">Conteúdo exato do dados.json</label>
            <textarea id="json-gerado-previa" class="caixa-codigo-saida" rows="8" readonly></textarea>
            <div class="par-copia">
              <button type="button" class="botao botao-contorno botao-compacto" command="--copy" commandfor="json-gerado-previa" id="btn-copiar-json">
                __IC_COPIAR__<span>Copiar só o dados.json</span>
              </button>
              <span class="bolha-status-copia" role="status" id="status-copia-json"></span>
            </div>
          </div>
        </details>
      </div>

      <div class="cartao-previa-ao-vivo">
        <div id="previa-toldo">__TOLDO_INICIAL_30__</div>
        <div class="previa-miolo">
          <img id="previa-foto-local" alt="Prévia da foto da barraca" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:12px;border:1.5px solid var(--linha);" hidden>
          <h3 class="letreiro-nome" id="previa-nome" style="font-size: clamp(1.9rem, 5vw, 2.35rem);">Nome da barraca</h3>
          <p id="previa-oferta" class="texto-apoio">O que oferece, no Parque da Cidade</p>
          <p id="previa-horario" style="font-size: 0.9375rem; font-weight: 700;">Dias e horário</p>
          <p id="previa-ref" class="texto-apoio" style="font-size: 0.9375rem;">Perto da referência</p>
          <div style="padding-top:var(--s-12);border-top:1px dashed var(--linha);display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:var(--s-8);">
            <span id="previa-item-nome" style="font-weight:700;">Primeiro item do catálogo</span>
            <span class="placa-preco"><span class="placa-furo" aria-hidden="true"></span><span class="preco-valor" id="previa-item-preco">R$ 0,00</span></span>
          </div>
        </div>
      </div>

      <div class="aviso-exportacao">
        Exportar não publica o site. Nenhum dado sai deste aparelho até você copiar o prompt ou baixar o arquivo.
      </div>
    </aside>
  </main>

  <script>
  (() => {
    const TOLDOS_34 = __TOLDOS_34_JSON__;
    const TOLDOS_30 = __TOLDOS_30_JSON__;
    const ICONES = __ICONES_JSON__;
    const CHAVE_RASCUNHO = "toldo_aberto_rascunho_equipe_v2";
    const TELEFONES_BANIDOS = ["5571" + "98812" + "3456", "71" + "98812" + "3456"];
    const MAPA_FOCO_CSS = { topo: "center 22%", centro: "center 50%", base: "center 78%" };

    const DICAS_SEGMENTO = {
      alimentacao: {
        pergunta: "“Quais comidas e bebidas nunca faltam na sua barraca? Diga o nome, a categoria, como é servido, o preço (ou sabores/tamanhos) e qual item é o Destaque da casa.”",
        botao: "Adicionar item ao cardápio",
        catPadrao: "Cardápio",
        placeholderNome: "Ex.: Pastel grande frito na hora",
        placeholderCat: "Ex.: Salgados na hora"
      },
      brinquedos: {
        pergunta: "“Quais brinquedos e doces você vende aqui no parque? Diga o nome, a categoria, uma descrição curta, a idade indicada e o preço ou opções.”",
        botao: "Adicionar brinquedo ou doce",
        catPadrao: "Produtos",
        placeholderNome: "Ex.: Kit bolha de sabão gigante",
        placeholderCat: "Ex.: Para o gramado"
      },
      inflaveis: {
        pergunta: "“Quais brinquedos infláveis ou pula-pula funcionam? Diga o nome, tempo da sessão, valor, faixa de idade, altura permitida e regras de segurança na entrada.”",
        botao: "Adicionar brinquedo inflável",
        catPadrao: "Brinquedos infláveis",
        placeholderNome: "Ex.: Tobogã inflável colorido",
        placeholderCat: "Ex.: Brinquedos infláveis"
      },
      bicicletas: {
        pergunta: "“Quais modelos de bicicleta ou triciclo você aluga, o que acompanha cada modelo e quanto custa por 30 minutos, 1 hora ou outro tempo?”",
        botao: "Adicionar modelo de bicicleta",
        catPadrao: "Aluguel na ciclovia",
        placeholderNome: "Ex.: Bicicleta passeio aro 26",
        placeholderCat: "Ex.: Aluguel na ciclovia"
      }
    };

    const form = document.getElementById("form-equipe");
    const listaItensEl = document.getElementById("lista-itens-equipe");
    const listaHorariosEl = document.getElementById("lista-horarios-tabela");
    const statusRascunho = document.getElementById("status-rascunho");
    const pixAut = document.getElementById("eq-pix-aut");
    const blocoPix = document.getElementById("bloco-campos-pix");

    let slugEditadoManual = false;
    let urlEditadaManual = false;
    let horariosExtrasEstado = [];
    let fotosMemoria = { barraca: null, fachada: null, retrato: null };
    let fotosItensMemoria = Object.create(null);

    function criarItemVazio() {
      return {
        uid: "u" + Math.random().toString(36).slice(2, 9),
        nome: "",
        categoria: "",
        descricao: "",
        destaque: false,
        preco: "",
        tipo_variacao: "sabor",
        variacoes: [],
        idade_indicada: "",
        tempo: "",
        altura_permitida: "",
        regras_texto: "",
        tempos_precos: [
          { tempo: "30 minutos", preco: "" },
          { tempo: "1 hora", preco: "" }
        ],
        incluir_foto: false,
        foco_foto: "centro"
      };
    }

    let itensEstado = [criarItemVazio()];

    function dataHojeISO() {
      const d = new Date();
      const m = String(d.getMonth() + 1).padStart(2, "0");
      const dia = String(d.getDate()).padStart(2, "0");
      return d.getFullYear() + "-" + m + "-" + dia;
    }

    const campoDataPrecos = document.getElementById("eq-data-precos");
    if (!campoDataPrecos.value) {
      campoDataPrecos.value = dataHojeISO();
    }

    function gerarSlug(texto) {
      return String(texto || "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "")
        .slice(0, 48);
    }

    function parseMoeda(valor) {
      if (valor === null || valor === undefined) return 0;
      const limpo = String(valor).trim().replace(/[R$\s]/g, "").replace(",", ".");
      const n = Number(limpo);
      return Number.isFinite(n) && n >= 0 ? Math.round(n * 100) / 100 : 0;
    }

    function parseDecimalOpcional(valor) {
      const s = String(valor || "").trim().replace(",", ".");
      if (!s) return null;
      const n = Number(s);
      return Number.isFinite(n) ? n : null;
    }

    function normalizarWhatsapp(bruto) {
      const dig = String(bruto || "").replace(/\D/g, "");
      if (!dig) return "";
      if (dig.length === 10 || dig.length === 11) {
        return "55" + dig;
      }
      return dig;
    }

    function segmentoAtual() {
      const marcado = form.querySelector('input[name="segmento"]:checked');
      return marcado ? marcado.value : "alimentacao";
    }

    function limparPrefixoPerto(ref) {
      return String(ref || "").trim().replace(/^perto\s+d[aoe]s?\s+/i, "").trim();
    }

    /* --- TABELA DINÂMICA DE HORÁRIOS EXTRAS --- */
    function renderizarHorariosExtras() {
      listaHorariosEl.innerHTML = "";
      horariosExtrasEstado.forEach((linha, idx) => {
        const row = document.createElement("div");
        row.className = "linha-subitem";
        const idDias = "eq-ht-dias-" + idx;
        const idHora = "eq-ht-hora-" + idx;
        row.innerHTML =
          '<div class="campo-grupo">' +
            '<label for="' + idDias + '">Dias / período ' + (idx + 1) + '</label>' +
            '<input type="text" id="' + idDias + '" class="campo-entrada js-ht-dias" placeholder="Ex.: Sábado, domingo e feriados">' +
          '</div>' +
          '<div class="campo-grupo">' +
            '<label for="' + idHora + '">Horário correspondente</label>' +
            '<input type="text" id="' + idHora + '" class="campo-entrada js-ht-hora" placeholder="Ex.: 07h30 às 17h30">' +
          '</div>' +
          '<div>' +
            '<button type="button" class="botao botao-contorno botao-compacto js-rem-ht">' + ICONES.lixeira + '<span>Remover</span></button>' +
          '</div>';
        row.querySelector(".js-ht-dias").value = linha.dias || "";
        row.querySelector(".js-ht-hora").value = linha.horario || "";
        row.querySelectorAll("input").forEach((inp) => inp.addEventListener("input", () => {
          sincronizarHorariosDoDOM();
          atualizarTudo();
        }));
        row.querySelector(".js-rem-ht").addEventListener("click", () => {
          horariosExtrasEstado.splice(idx, 1);
          renderizarHorariosExtras();
          atualizarTudo();
        });
        listaHorariosEl.appendChild(row);
      });
    }

    function sincronizarHorariosDoDOM() {
      horariosExtrasEstado = Array.from(listaHorariosEl.querySelectorAll(".linha-subitem")).map((row) => ({
        dias: row.querySelector(".js-ht-dias").value,
        horario: row.querySelector(".js-ht-hora").value
      }));
    }

    document.getElementById("btn-add-horario").addEventListener("click", () => {
      sincronizarHorariosDoDOM();
      horariosExtrasEstado.push({ dias: "", horario: "" });
      renderizarHorariosExtras();
      atualizarTudo();
    });

    /* --- COMPRESSÃO LOCAL DE FOTOS PARA WEBP <= 120 KB --- */
    function comprimirArquivoWebp(arquivo, aoConcluir) {
      const leitor = new FileReader();
      leitor.onload = () => {
        const img = new Image();
        img.onload = () => {
          let maxDim = 1080;
          let qualidade = 0.80;
          let dataUrl = "";
          let kb = 999;
          const cv = document.createElement("canvas");
          const ctx = cv.getContext("2d");
          for (let i = 0; i < 6; i++) {
            const escala = Math.min(1, maxDim / Math.max(img.width, img.height));
            cv.width = Math.max(1, Math.round(img.width * escala));
            cv.height = Math.max(1, Math.round(img.height * escala));
            ctx.clearRect(0, 0, cv.width, cv.height);
            ctx.filter = "brightness(1.02) contrast(1.02)";
            ctx.drawImage(img, 0, 0, cv.width, cv.height);
            dataUrl = cv.toDataURL("image/webp", qualidade);
            kb = Math.round((((dataUrl.split(",")[1] || "").length * 3) / 4 / 1024) * 10) / 10;
            if (kb <= 120) break;
            qualidade -= 0.08;
            if (qualidade < 0.48) {
              qualidade = 0.62;
              maxDim = Math.round(maxDim * 0.82);
            }
          }
          aoConcluir({ dataUrl: dataUrl, kb: kb, width: cv.width, height: cv.height });
        };
        img.src = leitor.result;
      };
      leitor.readAsDataURL(arquivo);
    }

    function dispararDownloadDataUrl(dataUrl, nomeArquivo) {
      const a = document.createElement("a");
      a.href = dataUrl;
      a.download = nomeArquivo;
      document.body.appendChild(a);
      a.click();
      a.remove();
    }

    function atualizarBotaoBaixarTodasFotos() {
      const temFotoPrincipal = Object.values(fotosMemoria).some(Boolean);
      const temFotoItem = Object.values(fotosItensMemoria).some(Boolean);
      document.getElementById("btn-baixar-todas-fotos").hidden = !(temFotoPrincipal || temFotoItem);
    }

    ["barraca", "fachada", "retrato"].forEach((slot) => {
      const inputArq = document.getElementById("eq-file-" + slot);
      const chkRef = document.getElementById("eq-ref-foto-" + slot);
      const boxInfo = document.getElementById("info-foto-" + slot);
      const thumb = document.getElementById("thumb-foto-" + slot);
      const txt = document.getElementById("txt-foto-" + slot);

      inputArq.addEventListener("change", (ev) => {
        const arq = ev.target.files && ev.target.files[0];
        if (!arq) return;
        comprimirArquivoWebp(arq, (res) => {
          fotosMemoria[slot] = res;
          chkRef.checked = true;
          thumb.src = res.dataUrl;
          txt.textContent = slot + ".webp pronta (" + res.kb + " KB · " + res.width + "×" + res.height + " px)";
          boxInfo.hidden = false;
          document.getElementById("status-foto-equipe").textContent =
            "Foto " + slot + ".webp comprimida para " + res.kb + " KB (limite de 150 KB respeitado).";
          atualizarBotaoBaixarTodasFotos();
          atualizarTudo();
        });
      });
    });

    document.querySelectorAll("[data-baixar-foto]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const slot = btn.getAttribute("data-baixar-foto");
        if (fotosMemoria[slot]) {
          dispararDownloadDataUrl(fotosMemoria[slot].dataUrl, slot + ".webp");
        }
      });
    });

    document.querySelectorAll("[data-limpar-foto]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const slot = btn.getAttribute("data-limpar-foto");
        fotosMemoria[slot] = null;
        document.getElementById("eq-file-" + slot).value = "";
        document.getElementById("eq-ref-foto-" + slot).checked = false;
        document.getElementById("info-foto-" + slot).hidden = true;
        atualizarBotaoBaixarTodasFotos();
        atualizarTudo();
      });
    });

    document.getElementById("btn-baixar-todas-fotos").addEventListener("click", () => {
      sincronizarItensDoDOM();
      const dados = montarDadosJSON();
      ["barraca", "fachada", "retrato"].forEach((slot) => {
        if (fotosMemoria[slot]) {
          dispararDownloadDataUrl(fotosMemoria[slot].dataUrl, slot + ".webp");
        }
      });
      itensEstado.forEach((it, idx) => {
        const mem = fotosItensMemoria[it.uid];
        if (mem && dados.itens[idx]) {
          dispararDownloadDataUrl(mem.dataUrl, dados.itens[idx].id + ".webp");
        }
      });
    });

    /* --- EDITOR COMPLETO DE ITENS POR SEGMENTO --- */
    function criarCardItemDOM(item, idx, seg) {
      const cfgSeg = DICAS_SEGMENTO[seg] || DICAS_SEGMENTO.alimentacao;
      const uid = item.uid || ("u" + idx);
      item.uid = uid;

      const card = document.createElement("div");
      card.className = "item-editor";
      card.setAttribute("data-uid", uid);

      const mostrarDestaque = seg === "alimentacao";
      const mostrarVariacoes = seg !== "bicicletas";
      const mostrarIdade = seg === "brinquedos" || seg === "inflaveis";
      const mostrarInflavel = seg === "inflaveis";
      const mostrarBike = seg === "bicicletas";

      const varsHTML = (item.variacoes || []).map((v, vIdx) => (
        '<div class="linha-subitem js-linha-var">' +
          '<div class="campo-grupo">' +
            '<label for="var-rot-' + uid + '-' + vIdx + '">Rótulo da opção ' + (vIdx + 1) + '</label>' +
            '<input type="text" id="var-rot-' + uid + '-' + vIdx + '" class="campo-entrada js-var-rotulo" placeholder="Ex.: Queijo coalho, 500 ml">' +
          '</div>' +
          '<div class="campo-grupo">' +
            '<label for="var-pr-' + uid + '-' + vIdx + '">Preço (R$)</label>' +
            '<input type="text" id="var-pr-' + uid + '-' + vIdx + '" inputmode="decimal" class="campo-entrada js-var-preco" placeholder="Ex.: 10,00">' +
          '</div>' +
          '<div>' +
            '<button type="button" class="botao botao-contorno botao-compacto js-rem-var" data-vidx="' + vIdx + '">' + ICONES.lixeira + '<span>Remover</span></button>' +
          '</div>' +
        '</div>'
      )).join("");

      const temposHTML = (item.tempos_precos || []).map((tp, tIdx) => (
        '<div class="linha-subitem js-linha-tp">' +
          '<div class="campo-grupo">' +
            '<label for="tp-tempo-' + uid + '-' + tIdx + '">Tempo ' + (tIdx + 1) + ' *</label>' +
            '<input type="text" id="tp-tempo-' + uid + '-' + tIdx + '" class="campo-entrada js-tp-tempo" placeholder="Ex.: 30 minutos, 1 hora">' +
          '</div>' +
          '<div class="campo-grupo">' +
            '<label for="tp-pr-' + uid + '-' + tIdx + '">Valor (R$) *</label>' +
            '<input type="text" id="tp-pr-' + uid + '-' + tIdx + '" inputmode="decimal" class="campo-entrada js-tp-preco" placeholder="Ex.: 18,00">' +
          '</div>' +
          '<div>' +
            '<button type="button" class="botao botao-contorno botao-compacto js-rem-tp" data-tidx="' + tIdx + '">' + ICONES.lixeira + '<span>Remover</span></button>' +
          '</div>' +
        '</div>'
      )).join("");

      card.innerHTML =
        '<div class="item-editor-topo">' +
          '<strong class="nome-item" style="font-size:1.15rem;">Item ' + (idx + 1) + '</strong>' +
          '<button type="button" class="botao botao-contorno botao-compacto js-rem-item"' + (itensEstado.length <= 1 ? ' hidden' : '') + '>' +
            ICONES.lixeira + '<span>Remover item</span>' +
          '</button>' +
        '</div>' +

        (mostrarDestaque
          ? '<div class="opcao-controle">' +
              '<input type="checkbox" id="it-dest-' + uid + '" class="js-it-destaque">' +
              '<label for="it-dest-' + uid + '">Marcar como “Destaque da casa” no topo do cardápio</label>' +
            '</div>'
          : '') +

        '<div class="duas-colunas">' +
          '<div class="campo-grupo">' +
            '<label for="it-nome-' + uid + '">Nome do item / modelo *</label>' +
            '<input type="text" id="it-nome-' + uid + '" class="campo-entrada js-it-nome" placeholder="' + cfgSeg.placeholderNome + '">' +
          '</div>' +
          '<div class="campo-grupo">' +
            '<label for="it-cat-' + uid + '">Categoria no catálogo</label>' +
            '<input type="text" id="it-cat-' + uid + '" class="campo-entrada js-it-cat" placeholder="' + cfgSeg.placeholderCat + '">' +
          '</div>' +
        '</div>' +

        '<div class="campo-grupo">' +
          '<label for="it-desc-' + uid + '">Descrição curta (preparo, acompanhamento ou detalhes)</label>' +
          '<input type="text" id="it-desc-' + uid + '" class="campo-entrada js-it-desc" placeholder="Ex.: Massa sequinha aberta na hora, acompanha vinagrete.">' +
        '</div>' +

        (mostrarVariacoes
          ? '<div class="duas-colunas">' +
              '<div class="campo-grupo">' +
                '<label for="it-preco-' + uid + '">Preço único em R$ (quando não há variações)</label>' +
                '<input type="text" id="it-preco-' + uid + '" inputmode="decimal" class="campo-entrada js-it-preco" placeholder="Ex.: 10,00">' +
              '</div>' +
              '<div class="campo-grupo">' +
                '<label for="it-tvar-' + uid + '">Tipo de escolha (se tiver variações)</label>' +
                '<select id="it-tvar-' + uid + '" class="campo-entrada js-it-tvar">' +
                  '<option value="sabor">Sabor (ex.: Queijo, Carne)</option>' +
                  '<option value="tamanho">Tamanho (ex.: 300 ml, 500 ml)</option>' +
                  '<option value="opção">Opção (ex.: Com carne do sol)</option>' +
                  '<option value="tempo">Tempo (ex.: 15 min, 40 min)</option>' +
                '</select>' +
              '</div>' +
            '</div>' +
            '<div class="campo-grupo">' +
              '<span style="font-weight:700;">Variações de sabor, tamanho ou opção (opcional)</span>' +
              '<span class="ajuda-campo">Se o preço depender do sabor/tamanho ou se o cliente precisar escolher uma opção, adicione abaixo.</span>' +
              '<div class="js-lista-vars" style="display:flex;flex-direction:column;gap:var(--s-8);margin-top:var(--s-4);">' + varsHTML + '</div>' +
              '<div style="margin-top:var(--s-8);">' +
                '<button type="button" class="botao botao-contorno botao-compacto js-add-var">' + ICONES.mais + '<span>Adicionar variação</span></button>' +
              '</div>' +
            '</div>'
          : '') +

        (mostrarIdade
          ? '<div class="duas-colunas">' +
              '<div class="campo-grupo">' +
                '<label for="it-idade-' + uid + '">Faixa de idade indicada</label>' +
                '<input type="text" id="it-idade-' + uid + '" class="campo-entrada js-it-idade" placeholder="Ex.: A partir de 3 anos / 3 a 12 anos">' +
              '</div>' +
              (mostrarInflavel
                ? '<div class="campo-grupo">' +
                    '<label for="it-tempo-' + uid + '">Tempo da sessão</label>' +
                    '<input type="text" id="it-tempo-' + uid + '" class="campo-entrada js-it-tempo" placeholder="Ex.: 15 minutos">' +
                  '</div>'
                : '<div></div>') +
            '</div>'
          : '') +

        (mostrarInflavel
          ? '<div class="campo-grupo">' +
              '<label for="it-altura-' + uid + '">Altura permitida</label>' +
              '<input type="text" id="it-altura-' + uid + '" class="campo-entrada js-it-altura" placeholder="Ex.: De 0,90 m até 1,50 m">' +
            '</div>' +
            '<div class="campo-grupo">' +
              '<label for="it-regras-' + uid + '">Regras de uso e segurança na entrada (1 regra por linha)</label>' +
              '<textarea id="it-regras-' + uid + '" rows="3" class="campo-entrada js-it-regras" placeholder="Entrada somente sem calçados.\nResponsável próximo ao brinquedo."></textarea>' +
            '</div>'
          : '') +

        (mostrarBike
          ? '<div class="campo-grupo">' +
              '<span style="font-weight:700;">Tempos e valores deste modelo *</span>' +
              '<div class="js-lista-tps" style="display:flex;flex-direction:column;gap:var(--s-8);margin-top:var(--s-4);">' + temposHTML + '</div>' +
              '<div style="margin-top:var(--s-8);">' +
                '<button type="button" class="botao botao-contorno botao-compacto js-add-tp">' + ICONES.mais + '<span>Adicionar tempo e valor</span></button>' +
              '</div>' +
            '</div>'
          : '') +

        '<details class="detalhes-json">' +
          '<summary>Foto opcional deste item e enquadramento</summary>' +
          '<div style="display:flex;flex-direction:column;gap:var(--s-12);padding-top:var(--s-8);">' +
            '<div class="duas-colunas">' +
              '<div class="campo-grupo">' +
                '<label for="it-file-' + uid + '">Foto do item (gera .webp até 120 KB)</label>' +
                '<input type="file" id="it-file-' + uid + '" accept="image/*" class="campo-entrada js-it-file">' +
              '</div>' +
              '<div class="campo-grupo">' +
                '<label for="it-foco-' + uid + '">Enquadramento da foto</label>' +
                '<select id="it-foco-' + uid + '" class="campo-entrada js-it-foco">' +
                  '<option value="centro">Centro</option>' +
                  '<option value="topo">Topo</option>' +
                  '<option value="base">Base</option>' +
                '</select>' +
              '</div>' +
            '</div>' +
            '<div class="opcao-controle">' +
              '<input type="checkbox" id="it-incfoto-' + uid + '" class="js-it-incfoto">' +
              '<label for="it-incfoto-' + uid + '">Referenciar foto deste item no <code>dados.json</code></label>' +
            '</div>' +
            '<div class="js-info-foto-it" style="display:flex;flex-wrap:wrap;align-items:center;gap:var(--s-8);"' + (fotosItensMemoria[uid] ? '' : ' hidden') + '>' +
              '<span class="ajuda-campo js-txt-foto-it" style="font-weight:700;">' +
                (fotosItensMemoria[uid] ? ('Foto pronta (' + fotosItensMemoria[uid].kb + ' KB)') : '') +
              '</span>' +
              '<button type="button" class="botao botao-contorno botao-compacto js-baixar-foto-it">' + ICONES.pedido + '<span>Baixar .webp deste item</span></button>' +
            '</div>' +
          '</div>' +
        '</details>';

      /* Preencher valores atuais */
      card.querySelector(".js-it-nome").value = item.nome || "";
      card.querySelector(".js-it-cat").value = item.categoria || "";
      card.querySelector(".js-it-desc").value = item.descricao || "";
      card.querySelector(".js-it-foco").value = item.foco_foto || "centro";
      card.querySelector(".js-it-incfoto").checked = Boolean(item.incluir_foto);

      if (mostrarDestaque) {
        const chkDest = card.querySelector(".js-it-destaque");
        chkDest.checked = Boolean(item.destaque);
        chkDest.addEventListener("change", () => {
          sincronizarItensDoDOM();
          if (chkDest.checked) {
            itensEstado.forEach((outro, oIdx) => { outro.destaque = oIdx === idx; });
            renderizarItensEditor();
          }
          atualizarTudo();
        });
      }

      if (mostrarVariacoes) {
        card.querySelector(".js-it-preco").value = item.preco || "";
        card.querySelector(".js-it-tvar").value = item.tipo_variacao || "sabor";
        const linhasVar = card.querySelectorAll(".js-linha-var");
        (item.variacoes || []).forEach((v, vIdx) => {
          if (linhasVar[vIdx]) {
            linhasVar[vIdx].querySelector(".js-var-rotulo").value = v.rotulo || "";
            linhasVar[vIdx].querySelector(".js-var-preco").value = v.preco !== undefined ? String(v.preco) : "";
          }
        });
        card.querySelector(".js-add-var").addEventListener("click", () => {
          sincronizarItensDoDOM();
          itensEstado[idx].variacoes.push({ rotulo: "", preco: "" });
          renderizarItensEditor();
          atualizarTudo();
        });
        card.querySelectorAll(".js-rem-var").forEach((bRem) => {
          bRem.addEventListener("click", () => {
            sincronizarItensDoDOM();
            const vi = Number(bRem.getAttribute("data-vidx"));
            itensEstado[idx].variacoes.splice(vi, 1);
            renderizarItensEditor();
            atualizarTudo();
          });
        });
      }

      if (mostrarIdade) {
        card.querySelector(".js-it-idade").value = item.idade_indicada || "";
      }
      if (mostrarInflavel) {
        card.querySelector(".js-it-tempo").value = item.tempo || "";
        card.querySelector(".js-it-altura").value = item.altura_permitida || "";
        card.querySelector(".js-it-regras").value = item.regras_texto || "";
      }
      if (mostrarBike) {
        const linhasTp = card.querySelectorAll(".js-linha-tp");
        (item.tempos_precos || []).forEach((tp, tIdx) => {
          if (linhasTp[tIdx]) {
            linhasTp[tIdx].querySelector(".js-tp-tempo").value = tp.tempo || "";
            linhasTp[tIdx].querySelector(".js-tp-preco").value = tp.preco !== undefined ? String(tp.preco) : "";
          }
        });
        card.querySelector(".js-add-tp").addEventListener("click", () => {
          sincronizarItensDoDOM();
          itensEstado[idx].tempos_precos.push({ tempo: "", preco: "" });
          renderizarItensEditor();
          atualizarTudo();
        });
        card.querySelectorAll(".js-rem-tp").forEach((bRem) => {
          bRem.addEventListener("click", () => {
            sincronizarItensDoDOM();
            const ti = Number(bRem.getAttribute("data-tidx"));
            if (itensEstado[idx].tempos_precos.length > 1) {
              itensEstado[idx].tempos_precos.splice(ti, 1);
              renderizarItensEditor();
              atualizarTudo();
            }
          });
        });
      }

      const fileIt = card.querySelector(".js-it-file");
      fileIt.addEventListener("change", (ev) => {
        const arq = ev.target.files && ev.target.files[0];
        if (!arq) return;
        comprimirArquivoWebp(arq, (res) => {
          fotosItensMemoria[uid] = res;
          card.querySelector(".js-it-incfoto").checked = true;
          card.querySelector(".js-txt-foto-it").textContent = "Foto pronta (" + res.kb + " KB)";
          card.querySelector(".js-info-foto-it").hidden = false;
          sincronizarItensDoDOM();
          atualizarBotaoBaixarTodasFotos();
          atualizarTudo();
        });
      });

      card.querySelector(".js-baixar-foto-it").addEventListener("click", () => {
        sincronizarItensDoDOM();
        const mem = fotosItensMemoria[uid];
        if (!mem) return;
        const slugIt = gerarSlug(itensEstado[idx].nome) || ("item-" + (idx + 1));
        dispararDownloadDataUrl(mem.dataUrl, slugIt + ".webp");
      });

      card.querySelectorAll("input:not([type='file']), select, textarea").forEach((inp) => {
        if (!inp.classList.contains("js-it-destaque")) {
          inp.addEventListener("input", () => {
            sincronizarItensDoDOM();
            document.getElementById("erro-campo-itens").hidden = true;
            atualizarTudo();
          });
          inp.addEventListener("change", () => {
            sincronizarItensDoDOM();
            atualizarTudo();
          });
        }
      });

      const btnRemItem = card.querySelector(".js-rem-item");
      if (btnRemItem) {
        btnRemItem.addEventListener("click", () => {
          sincronizarItensDoDOM();
          if (itensEstado.length > 1) {
            delete fotosItensMemoria[uid];
            itensEstado.splice(idx, 1);
            renderizarItensEditor();
            atualizarBotaoBaixarTodasFotos();
            atualizarTudo();
          }
        });
      }

      return card;
    }

    function renderizarItensEditor() {
      const seg = segmentoAtual();
      listaItensEl.innerHTML = "";
      itensEstado.forEach((it, i) => listaItensEl.appendChild(criarCardItemDOM(it, i, seg)));
    }

    function sincronizarItensDoDOM() {
      const seg = segmentoAtual();
      const cards = Array.from(listaItensEl.querySelectorAll(".item-editor"));
      if (!cards.length) return;
      itensEstado = cards.map((card, idx) => {
        const ant = itensEstado[idx] || criarItemVazio();
        const novo = Object.assign({}, ant, {
          uid: card.getAttribute("data-uid") || ant.uid,
          nome: card.querySelector(".js-it-nome").value,
          categoria: card.querySelector(".js-it-cat").value,
          descricao: card.querySelector(".js-it-desc").value,
          foco_foto: card.querySelector(".js-it-foco").value,
          incluir_foto: card.querySelector(".js-it-incfoto").checked
        });
        if (seg === "alimentacao" && card.querySelector(".js-it-destaque")) {
          novo.destaque = card.querySelector(".js-it-destaque").checked;
        }
        if (seg !== "bicicletas") {
          novo.preco = card.querySelector(".js-it-preco").value;
          novo.tipo_variacao = card.querySelector(".js-it-tvar").value;
          novo.variacoes = Array.from(card.querySelectorAll(".js-linha-var")).map((lv) => ({
            rotulo: lv.querySelector(".js-var-rotulo").value,
            preco: lv.querySelector(".js-var-preco").value
          }));
        }
        if (seg === "brinquedos" || seg === "inflaveis") {
          novo.idade_indicada = card.querySelector(".js-it-idade").value;
        }
        if (seg === "inflaveis") {
          novo.tempo = card.querySelector(".js-it-tempo").value;
          novo.altura_permitida = card.querySelector(".js-it-altura").value;
          novo.regras_texto = card.querySelector(".js-it-regras").value;
        }
        if (seg === "bicicletas") {
          novo.tempos_precos = Array.from(card.querySelectorAll(".js-linha-tp")).map((lt) => ({
            tempo: lt.querySelector(".js-tp-tempo").value,
            preco: lt.querySelector(".js-tp-preco").value
          }));
        }
        return novo;
      });
    }

    document.getElementById("btn-novo-item").addEventListener("click", () => {
      sincronizarItensDoDOM();
      itensEstado.push(criarItemVazio());
      renderizarItensEditor();
      atualizarTudo();
    });

    /* --- MONTAGEM COMPLETA DO DADOS.JSON (100% DO ESQUEMA DO COMPILADOR) --- */
    function montarDadosJSON() {
      const seg = segmentoAtual();
      const cfgSeg = DICAS_SEGMENTO[seg] || DICAS_SEGMENTO.alimentacao;
      const modoExemplo = document.getElementById("eq-modo-exemplo").checked;
      const nomeNegocio = document.getElementById("eq-nome").value.trim();
      const slugBase = document.getElementById("eq-slug").value.trim() || gerarSlug(nomeNegocio) || "barraca-parque";
      const urlFinal = document.getElementById("eq-url").value.trim() || ("https://" + slugBase + ".vercel.app/");

      const dPrecos = document.getElementById("eq-data-precos").value;
      const dataBR = dPrecos && /^\d{4}-\d{2}-\d{2}$/.test(dPrecos)
        ? dPrecos.split("-").reverse().join("/")
        : "";

      const dias = document.getElementById("eq-dias").value.trim();
      const inicio = document.getElementById("eq-inicio").value.trim();
      const fim = document.getElementById("eq-fim").value.trim();

      const linhasTabelaExplicitas = horariosExtrasEstado
        .map((l) => ({ dias: String(l.dias || "").trim(), horario: String(l.horario || "").trim() }))
        .filter((l) => l.dias && l.horario);

      const tabelaHorarios = linhasTabelaExplicitas.length
        ? linhasTabelaExplicitas
        : (dias && inicio && fim ? [{ dias: dias, horario: inicio + " às " + fim }] : []);

      const pagamentosMarcados = Array.from(form.querySelectorAll('input[name="pagamento_opcao"]:checked')).map((c) => c.value);
      const pagamentosExtras = document.getElementById("eq-pag-outros").value
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const listaPagamentos = Array.from(new Set(pagamentosMarcados.concat(pagamentosExtras)));

      const fotosObj = {};
      const enquadramentosObj = {};
      ["barraca", "fachada", "retrato"].forEach((slot) => {
        const focoVal = document.getElementById("eq-foco-" + slot).value;
        enquadramentosObj[slot] = focoVal;
        if (document.getElementById("eq-ref-foto-" + slot).checked) {
          fotosObj[slot] = slot + ".webp";
        }
      });

      const idsUsados = new Set();
      let idDestaqueEscolhido = "";

      const itensFormatados = itensEstado
        .filter((x) => String(x.nome || "").trim())
        .map((x, idx) => {
          const baseId = gerarSlug(x.nome) || ("item-" + (idx + 1));
          let itemId = baseId;
          let sufixo = 2;
          while (idsUsados.has(itemId)) {
            itemId = baseId + "-" + sufixo;
            sufixo += 1;
          }
          idsUsados.add(itemId);

          if (seg === "alimentacao" && x.destaque && !idDestaqueEscolhido) {
            idDestaqueEscolhido = itemId;
          }

          const nomeFotoItem = x.incluir_foto ? (itemId + ".webp") : "";
          if (x.incluir_foto) {
            enquadramentosObj[itemId] = x.foco_foto || "centro";
          }

          const baseItem = {
            id: itemId,
            categoria: String(x.categoria || "").trim() || cfgSeg.catPadrao,
            nome: String(x.nome || "").trim(),
            descricao: String(x.descricao || "").trim(),
            foto: nomeFotoItem
          };

          if (seg === "bicicletas") {
            const tps = (x.tempos_precos || [])
              .map((tp) => ({ tempo: String(tp.tempo || "").trim(), preco: parseMoeda(tp.preco) }))
              .filter((tp) => tp.tempo && tp.preco > 0);
            return Object.assign(baseItem, {
              tempos_precos: tps,
              variacoes: []
            });
          }

          const varsLimpas = (x.variacoes || [])
            .map((v) => ({ rotulo: String(v.rotulo || "").trim(), preco: parseMoeda(v.preco) }))
            .filter((v) => v.rotulo && v.preco > 0);

          const itemMontado = Object.assign(baseItem, varsLimpas.length
            ? {
                tipo_variacao: x.tipo_variacao || "sabor",
                variacoes: varsLimpas
              }
            : {
                preco: parseMoeda(x.preco),
                variacoes: []
              }
          );

          if (seg === "brinquedos") {
            itemMontado.idade_indicada = String(x.idade_indicada || "").trim();
          } else if (seg === "inflaveis") {
            itemMontado.tempo = String(x.tempo || "").trim();
            itemMontado.idade_indicada = String(x.idade_indicada || "").trim();
            itemMontado.altura_permitida = String(x.altura_permitida || "").trim();
            itemMontado.regras = String(x.regras_texto || "")
              .split(/\r?\n/)
              .map((r) => r.trim())
              .filter(Boolean);
          }

          return itemMontado;
        });

      const payload = {
        slug: slugBase,
        modo_exemplo: modoExemplo,
        consentimento: document.getElementById("eq-consentimento").checked,
        segmento: seg,
        nome_negocio: nomeNegocio,
        quem_atende: document.getElementById("eq-atendente").value.trim(),
        o_que_oferece: document.getElementById("eq-oferta").value.trim(),
        whatsapp: normalizarWhatsapp(document.getElementById("eq-zap").value),
        pix: {
          autorizado: pixAut.checked,
          chave: pixAut.checked ? document.getElementById("eq-pix-chave").value.trim() : "",
          recebedor: pixAut.checked ? document.getElementById("eq-pix-nome").value.trim() : ""
        },
        pagamento: listaPagamentos,
        dias: dias,
        horarios: {
          inicio: inicio,
          fim: fim,
          tabela: tabelaHorarios
        },
        referencia: limparPrefixoPerto(document.getElementById("eq-ref").value),
        latitude: parseDecimalOpcional(document.getElementById("eq-lat").value),
        longitude: parseDecimalOpcional(document.getElementById("eq-lng").value),
        data_precos_conferidos: dataBR,
        destaque: seg === "alimentacao" ? idDestaqueEscolhido : "",
        aceita_pedidos_do_dia: seg === "alimentacao" ? document.getElementById("eq-pedidos-dia").checked : false,
        aceita_encomendas: document.getElementById("eq-encomendas").checked,
        historia_aprovada: document.getElementById("eq-historia").value.trim(),
        fotos: fotosObj,
        enquadramentos: enquadramentosObj,
        url_final: urlFinal,
        itens: itensFormatados
      };

      if (seg === "bicicletas") {
        payload.regras_aluguel = {
          documento: document.getElementById("eq-regra-doc").value.trim(),
          caucao: document.getElementById("eq-regra-caucao").value.trim(),
          devolucao: document.getElementById("eq-regra-devolucao").value.trim()
        };
      }

      return payload;
    }

    /* --- AVALIAÇÃO DE PRONTIDÃO PARA PRODUÇÃO (--producao) --- */
    function diagnosticarDados(dados) {
      const pendencias = [];
      const serializado = JSON.stringify(dados).toLowerCase();

      if (!dados.modo_exemplo && !dados.consentimento) {
        pendencias.push({ id: "eq-consentimento", msg: "Confirmar autorização verbal do(a) ambulante" });
      }
      if (!dados.nome_negocio) {
        pendencias.push({ id: "eq-nome", msg: "Preencher nome do negócio no letreiro" });
      } else if (!dados.modo_exemplo && (dados.nome_negocio.toLowerCase().includes("barraca exemplo") || serializado.includes("dados fictícios"))) {
        pendencias.push({ id: "eq-nome", msg: "Substituir 'Barraca Exemplo' pelo nome real do negócio" });
      }
      if (!dados.o_que_oferece) {
        pendencias.push({ id: "eq-oferta", msg: "Preencher frase curta do que oferece no parque" });
      }
      if (!dados.dias || !dados.horarios.inicio || !dados.horarios.fim) {
        pendencias.push({ id: "eq-dias", msg: "Preencher dias, horário de abertura e fechamento" });
      }
      if (!dados.referencia) {
        pendencias.push({ id: "eq-ref", msg: "Preencher ponto de referência no Parque da Cidade" });
      }
      for (const banido of TELEFONES_BANIDOS) {
        if (serializado.includes(banido)) {
          pendencias.push({ id: "eq-zap", msg: "Remover número telefônico fictício proibido" });
        }
      }
      if (!dados.modo_exemplo && !/^55\d{10,11}$/.test(dados.whatsapp)) {
        pendencias.push({ id: "eq-zap", msg: "Informar WhatsApp válido com DDD (10 ou 11 dígitos)" });
      }
      if (dados.pix.autorizado && (!dados.pix.recebedor || !dados.pix.chave)) {
        pendencias.push({ id: "eq-pix-nome", msg: "Completar nome do recebedor e chave Pix (ou desmarcar Pix na página)" });
      }
      if (dados.segmento === "bicicletas") {
        const ra = dados.regras_aluguel || {};
        if (!ra.documento && !ra.caucao && !ra.devolucao) {
          pendencias.push({ id: "eq-regra-doc", msg: "Informar regras de documento, caução e devolução das bicicletas" });
        }
      }
      if (!dados.itens.length) {
        pendencias.push({ id: "btn-novo-item", msg: "Cadastrar pelo menos 1 item no catálogo" });
      } else {
        const itemSemPreco = dados.itens.find((it) => {
          if (dados.segmento === "bicicletas") return !(it.tempos_precos && it.tempos_precos.length > 0);
          if (it.variacoes && it.variacoes.length > 0) return false;
          return !(Number(it.preco) > 0);
        });
        if (itemSemPreco) {
          pendencias.push({ id: "btn-novo-item", msg: "Definir preço válido (maior que R$ 0,00) em '" + itemSemPreco.nome + "'" });
        }
      }

      return pendencias;
    }

    /* --- GERAÇÃO DO PROMPT COMPLETO PARA COLAR NO CHAT --- */
    function montarPromptChat(dados, pendencias) {
      const nomesSeg = {
        alimentacao: "Alimentação e bebidas",
        brinquedos: "Brinquedos e doces",
        inflaveis: "Infláveis e pula-pula",
        bicicletas: "Aluguel de bicicletas"
      };
      const statusCabecalho = pendencias.length === 0
        ? "COLETA 100% COMPLETA E VALIDADA PARA BUILD DE PRODUÇÃO (--producao)"
        : "RASCUNHO EM PREENCHIMENTO (" + pendencias.length + " pendência(s) restante(s))";

      const resumoItens = dados.itens.length
        ? dados.itens.map((it, i) => {
            let precoTxt = "";
            if (dados.segmento === "bicicletas") {
              precoTxt = (it.tempos_precos || []).map((tp) => tp.tempo + ": R$ " + tp.preco.toFixed(2).replace(".", ",")).join(" | ");
            } else if (it.variacoes && it.variacoes.length) {
              precoTxt = "(" + (it.tipo_variacao || "opção") + ") " +
                it.variacoes.map((v) => v.rotulo + ": R$ " + v.preco.toFixed(2).replace(".", ",")).join(" | ");
            } else {
              precoTxt = "R$ " + Number(it.preco || 0).toFixed(2).replace(".", ",");
            }
            const seloDest = dados.destaque === it.id ? " [DESTAQUE DA CASA]" : "";
            return "  " + (i + 1) + ". [" + it.categoria + "] " + it.nome + seloDest + " — " + precoTxt +
              (it.descricao ? " (" + it.descricao + ")" : "");
          }).join("\n")
        : "  (Nenhum item preenchido ainda)";

      const fotosListadas = Object.entries(dados.fotos || {}).map(([k, v]) => k + ": " + v + " (foco " + (dados.enquadramentos[k] || "centro") + ")");

      const linhas = [
        "Atue como o compilador e equipe Parque Digital Unijorge (sistema visual 'Toldo Aberto') para gerar e revisar o pacote completo do site gratuito deste(a) ambulante do Parque da Cidade Joventino Silva (Salvador-BA).",
        "",
        "STATUS DA FICHA DE CAMPO: " + statusCabecalho,
        "- Consentimento verbal confirmado: " + (dados.consentimento ? "SIM" : "NÃO") + (dados.modo_exemplo ? " (Modo treino/exemplo ativo)" : " (Modo produção real)"),
        "- Segmento: " + (nomesSeg[dados.segmento] || dados.segmento) + " (" + dados.segmento + ")",
        "- Nome no letreiro e na Placa A5: " + (dados.nome_negocio || "(em branco)"),
        "- Quem atende: " + (dados.quem_atende || "(não informado — ocultar assinatura individual)"),
        "- Frase da oferta na abertura: " + (dados.o_que_oferece || "(em branco)"),
        "- Slug / URL final do QR Code: " + dados.slug + " -> " + dados.url_final,
        "- Funcionamento: " + (dados.dias || "(em branco)") + ", das " + (dados.horarios.inicio || "?") + " às " + (dados.horarios.fim || "?"),
        "- Ponto de referência no parque: " + (dados.referencia ? "Perto da " + dados.referencia : "(em branco)"),
        "- Coordenadas GPS: " + (dados.latitude !== null && dados.longitude !== null ? dados.latitude + ", " + dados.longitude : "não informadas (omitir botão de mapa externo)"),
        "- WhatsApp (DDI 55 + DDD): " + (dados.whatsapp || "(vazio)"),
        "- Formas de pagamento: " + (dados.pagamento.length ? dados.pagamento.join(", ") : "(nenhuma selecionada)"),
        "- Pix exibido na página: " + (dados.pix.autorizado ? "SIM — Recebedor: " + dados.pix.recebedor + " | Chave: " + dados.pix.chave : "NÃO (combinar somente presencialmente ou no WhatsApp)"),
        "- Preços conferidos em: " + (dados.data_precos_conferidos || "(sem data)"),
        "- Comanda de pedidos do dia ativa: " + (dados.aceita_pedidos_do_dia ? "SIM" : "NÃO"),
        "- Formulário de encomendas para grupos ativo: " + (dados.aceita_encomendas ? "SIM" : "NÃO"),
        "- Frase aprovada ('Quem atende'): " + (dados.historia_aprovada ? "“" + dados.historia_aprovada + "”" : "(em branco — ocultar seção Quem atende)"),
        "- Fotos referenciadas: " + (fotosListadas.length ? fotosListadas.join(", ") : "nenhuma foto anexada (usar abertura tipográfica Toldo Aberto sem quadro vazio)"),
        "",
        "CATÁLOGO COLETADO NA BARRACA:",
        resumoItens,
        "",
        "TAREFAS SOLICITADAS NO PROJETO:",
        "1. Salve o JSON abaixo em `dados.json` (e coloque eventuais fotos `.webp` na subpasta `fotos/`).",
        "2. Revise se há apenas eventuais erros de digitação em português mantendo 100% de fidelidade aos preços, regras e palavras aprovadas pelo(a) ambulante (sem inventar selos, promoções ou informações).",
        "3. Compile o pacote estático completo (`index.html`, `placa-a5.html` com QR Code >= 6 cm e `qrcode.svg`) rodando:",
        "   `python -m parque_digital.build_toldo --entrada <pasta_do_ambulante> --saida docs" + (dados.modo_exemplo ? "" : " --producao") + "`",
        "",
        "ARQUIVO `dados.json` COMPLETO PRONTO PARA COMPILAÇÃO:",
        "```json",
        JSON.stringify(dados, null, 2),
        "```"
      ];

      return linhas.join("\n");
    }

    /* --- ATUALIZAÇÃO DE INTERFACE, PRÉVIA, PROMPT E RASCUNHO --- */
    let ultimoSegmentoRenderizado = segmentoAtual();

    function atualizarVisibilidadeSegmento(seg) {
      const cfgSeg = DICAS_SEGMENTO[seg] || DICAS_SEGMENTO.alimentacao;
      document.documentElement.setAttribute("data-segmento", seg);
      document.getElementById("toldo-equipe").innerHTML = TOLDOS_34[seg] || TOLDOS_34.alimentacao;
      document.getElementById("previa-toldo").innerHTML = TOLDOS_30[seg] || TOLDOS_30.alimentacao;

      document.getElementById("wrap-pedidos-dia").hidden = seg !== "alimentacao";
      document.getElementById("bloco-regras-aluguel").hidden = seg !== "bicicletas";
      document.getElementById("dica-catalogo-segmento").innerHTML =
        "<strong>Pergunta 13 — Pergunte ao ambulante:</strong> " + cfgSeg.pergunta;
      document.getElementById("rotulo-btn-novo-item").textContent = cfgSeg.botao;

      blocoPix.hidden = !pixAut.checked;
      pixAut.setAttribute("aria-expanded", pixAut.checked ? "true" : "false");

      if (seg !== ultimoSegmentoRenderizado) {
        ultimoSegmentoRenderizado = seg;
        renderizarItensEditor();
      }
    }

    function atualizarTudo() {
      const seg = segmentoAtual();
      atualizarVisibilidadeSegmento(seg);

      const dados = montarDadosJSON();
      const pendencias = diagnosticarDados(dados);

      /* Checklist lateral de prontidão */
      const selo = document.getElementById("selo-prontidao");
      const ulPend = document.getElementById("lista-pendencias");
      if (pendencias.length === 0) {
        selo.className = "selo-prontidao pronto";
        selo.innerHTML = ICONES.confere + '<span>100% pronto para exportar</span>';
        ulPend.innerHTML =
          '<li>' + ICONES.confere + '<span>Todos os dados obrigatórios do site, da comanda/catálogo e da Placa A5 estão preenchidos.</span></li>';
      } else {
        selo.className = "selo-prontidao";
        selo.innerHTML = ICONES.alerta + '<span>Faltam ' + pendencias.length + ' dado(s)</span>';
        ulPend.innerHTML = pendencias.slice(0, 6).map((p) => (
          '<li>' + ICONES.alerta + '<span>' + p.msg + '</span></li>'
        )).join("");
      }

      /* Prévia visual ao vivo */
      const prevImg = document.getElementById("previa-foto-local");
      if (fotosMemoria.barraca) {
        prevImg.src = fotosMemoria.barraca.dataUrl;
        prevImg.style.objectPosition = MAPA_FOCO_CSS[dados.enquadramentos.barraca] || "center 22%";
        prevImg.hidden = false;
      } else {
        prevImg.hidden = true;
      }

      document.getElementById("previa-nome").textContent = dados.nome_negocio || "Nome da barraca";
      document.getElementById("previa-oferta").textContent = dados.o_que_oferece || "O que oferece, no Parque da Cidade";
      document.getElementById("previa-horario").textContent = dados.dias
        ? dados.dias + (dados.horarios.inicio && dados.horarios.fim ? ", das " + dados.horarios.inicio + " às " + dados.horarios.fim : "")
        : "Dias e horário";
      document.getElementById("previa-ref").textContent = dados.referencia
        ? "Perto da " + dados.referencia
        : "Perto da referência";

      const pItem = dados.itens[0];
      document.getElementById("previa-item-nome").textContent = pItem ? pItem.nome : "Primeiro item do catálogo";
      let pVal = 0;
      if (pItem) {
        if (dados.segmento === "bicicletas" && pItem.tempos_precos && pItem.tempos_precos.length) {
          pVal = pItem.tempos_precos[0].preco;
        } else if (pItem.variacoes && pItem.variacoes.length) {
          pVal = pItem.variacoes[0].preco;
        } else {
          pVal = pItem.preco || 0;
        }
      }
      document.getElementById("previa-item-preco").textContent = "R$ " + Number(pVal || 0).toFixed(2).replace(".", ",");

      /* Saídas sincronizadas: JSON puro + Prompt completo para o chat */
      document.getElementById("json-gerado-previa").value = JSON.stringify(dados, null, 2);
      document.getElementById("prompt-gerado-chat").value = montarPromptChat(dados, pendencias);

      /* Persistência local resiliente (sem blobs pesados) */
      try {
        window.localStorage.setItem(CHAVE_RASCUNHO, JSON.stringify({
          dados: dados,
          itensEstado: itensEstado,
          horariosExtrasEstado: horariosExtrasEstado,
          pagamentoOutros: document.getElementById("eq-pag-outros").value,
          slugEditadoManual: slugEditadoManual,
          urlEditadaManual: urlEditadaManual
        }));
        statusRascunho.textContent = "Rascunho salvo automaticamente neste aparelho.";
      } catch (_e) {
        statusRascunho.textContent = "Armazenamento local indisponível; exporte antes de fechar.";
      }
    }

    /* Auto-sugestão de slug e URL final enquanto edita o nome */
    document.getElementById("eq-nome").addEventListener("input", (ev) => {
      const s = gerarSlug(ev.target.value);
      if (!slugEditadoManual) {
        document.getElementById("eq-slug").value = s;
      }
      if (!urlEditadaManual) {
        const slugAtual = document.getElementById("eq-slug").value.trim() || s;
        document.getElementById("eq-url").value = slugAtual ? ("https://" + slugAtual + ".vercel.app/") : "";
      }
    });
    document.getElementById("eq-slug").addEventListener("input", (ev) => {
      slugEditadoManual = Boolean(ev.target.value.trim());
      if (!urlEditadaManual) {
        const s = gerarSlug(ev.target.value);
        document.getElementById("eq-url").value = s ? ("https://" + s + ".vercel.app/") : "";
      }
    });
    document.getElementById("eq-url").addEventListener("input", (ev) => {
      urlEditadaManual = Boolean(ev.target.value.trim());
    });

    /* Captura de GPS no local */
    document.getElementById("btn-capturar-gps").addEventListener("click", () => {
      const statusGps = document.getElementById("status-gps");
      if (!navigator.geolocation) {
        statusGps.textContent = "Este navegador não oferece leitura direta de GPS; digite se desejar.";
        return;
      }
      statusGps.textContent = "Obtendo localização atual do aparelho...";
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          document.getElementById("eq-lat").value = pos.coords.latitude.toFixed(6);
          document.getElementById("eq-lng").value = pos.coords.longitude.toFixed(6);
          statusGps.textContent = "Coordenadas registradas com sucesso.";
          atualizarTudo();
        },
        () => {
          statusGps.textContent = "Permissão de localização recusada ou sem sinal; o campo continua opcional.";
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    });

    /* Validação contextual não-intrusiva (valida no blur se tocado, limpa imediatamente no input) */
    function validarCampoIndividual(idCampo) {
      const el = document.getElementById(idCampo);
      if (!el) return;
      const modoEx = document.getElementById("eq-modo-exemplo").checked;
      let invalido = false;
      let idErro = "";

      if (idCampo === "eq-nome") {
        idErro = "erro-campo-nome";
        const v = el.value.trim();
        invalido = !v || (!modoEx && v.toLowerCase().includes("barraca exemplo"));
      } else if (idCampo === "eq-oferta") {
        idErro = "erro-campo-oferta";
        invalido = !el.value.trim();
      } else if (idCampo === "eq-dias") {
        idErro = "erro-campo-dias";
        invalido = !el.value.trim();
      } else if (idCampo === "eq-ref") {
        idErro = "erro-campo-ref";
        invalido = !el.value.trim();
      } else if (idCampo === "eq-zap") {
        idErro = "erro-campo-zap";
        const z = normalizarWhatsapp(el.value);
        invalido = !modoEx && (!/^55\d{10,11}$/.test(z) || TELEFONES_BANIDOS.includes(z));
      }

      if (invalido) {
        el.setAttribute("aria-invalid", "true");
        if (idErro) document.getElementById(idErro).hidden = false;
      } else {
        el.removeAttribute("aria-invalid");
        if (idErro) document.getElementById(idErro).hidden = true;
      }
    }

    ["eq-nome", "eq-oferta", "eq-dias", "eq-ref", "eq-zap"].forEach((idC) => {
      const el = document.getElementById(idC);
      el.addEventListener("input", () => {
        el.dataset.tocado = "1";
        el.removeAttribute("aria-invalid");
        const err = document.getElementById("erro-campo-" + idC.replace("eq-", ""));
        if (err) err.hidden = true;
        document.getElementById("erro-exportacao-equipe").hidden = true;
      });
      el.addEventListener("blur", () => {
        if (el.dataset.tocado === "1") validarCampoIndividual(idC);
      });
    });

    document.getElementById("eq-consentimento").addEventListener("change", (ev) => {
      if (ev.target.checked) {
        ev.target.removeAttribute("aria-invalid");
        document.getElementById("erro-campo-consentimento").hidden = true;
      }
    });

    /* Carregar dados em formulário (de rascunho ou de dados.json importado) */
    function aplicarObjetoDadosNoFormulario(d, itensBrutos, horariosBrutos) {
      if (!d) return;
      document.getElementById("eq-consentimento").checked = Boolean(d.consentimento);
      document.getElementById("eq-modo-exemplo").checked = Boolean(d.modo_exemplo);
      const radioSeg = form.querySelector('input[name="segmento"][value="' + (d.segmento || "alimentacao") + '"]');
      if (radioSeg) radioSeg.checked = true;
      ultimoSegmentoRenderizado = d.segmento || "alimentacao";

      document.getElementById("eq-nome").value = d.nome_negocio || "";
      document.getElementById("eq-atendente").value = d.quem_atende || "";
      document.getElementById("eq-oferta").value = d.o_que_oferece || "";
      document.getElementById("eq-slug").value = d.slug || "";
      document.getElementById("eq-url").value = d.url_final || "";
      document.getElementById("eq-dias").value = d.dias || "";
      document.getElementById("eq-inicio").value = (d.horarios && d.horarios.inicio) || "";
      document.getElementById("eq-fim").value = (d.horarios && d.horarios.fim) || "";
      document.getElementById("eq-ref").value = d.referencia || "";
      document.getElementById("eq-lat").value = d.latitude !== null && d.latitude !== undefined ? String(d.latitude) : "";
      document.getElementById("eq-lng").value = d.longitude !== null && d.longitude !== undefined ? String(d.longitude) : "";
      document.getElementById("eq-zap").value = d.whatsapp || "";

      if (d.data_precos_conferidos && /^\d{2}\/\d{2}\/\d{4}$/.test(d.data_precos_conferidos)) {
        document.getElementById("eq-data-precos").value = d.data_precos_conferidos.split("/").reverse().join("-");
      }

      const listaPag = Array.isArray(d.pagamento) ? d.pagamento : [];
      const valoresPadrao = new Set();
      form.querySelectorAll('input[name="pagamento_opcao"]').forEach((chk) => {
        valoresPadrao.add(chk.value);
        chk.checked = listaPag.includes(chk.value);
      });
      const sobrasPag = listaPag.filter((p) => !valoresPadrao.has(p));
      document.getElementById("eq-pag-outros").value = sobrasPag.join(", ");

      pixAut.checked = Boolean(d.pix && d.pix.autorizado);
      document.getElementById("eq-pix-nome").value = (d.pix && d.pix.recebedor) || "";
      document.getElementById("eq-pix-chave").value = (d.pix && d.pix.chave) || "";

      document.getElementById("eq-pedidos-dia").checked = d.aceita_pedidos_do_dia !== false;
      document.getElementById("eq-encomendas").checked = Boolean(d.aceita_encomendas);
      document.getElementById("eq-historia").value = d.historia_aprovada || "";

      const ra = d.regras_aluguel || {};
      document.getElementById("eq-regra-doc").value = ra.documento || "";
      document.getElementById("eq-regra-caucao").value = ra.caucao || "";
      document.getElementById("eq-regra-devolucao").value = ra.devolucao || "";

      ["barraca", "fachada", "retrato"].forEach((slot) => {
        const enq = d.enquadramentos && d.enquadramentos[slot];
        if (enq) document.getElementById("eq-foco-" + slot).value = enq;
        document.getElementById("eq-ref-foto-" + slot).checked = Boolean(d.fotos && d.fotos[slot]);
      });

      if (Array.isArray(horariosBrutos)) {
        horariosExtrasEstado = horariosBrutos;
      } else if (d.horarios && Array.isArray(d.horarios.tabela) && d.horarios.tabela.length > 1) {
        horariosExtrasEstado = d.horarios.tabela.map((l) => ({ dias: l.dias || "", horario: l.horario || "" }));
      } else {
        horariosExtrasEstado = [];
      }

      if (Array.isArray(itensBrutos) && itensBrutos.length) {
        itensEstado = itensBrutos.map((x) => Object.assign(criarItemVazio(), x));
      } else if (Array.isArray(d.itens) && d.itens.length) {
        itensEstado = d.itens.map((it) => Object.assign(criarItemVazio(), {
          nome: it.nome || "",
          categoria: it.categoria || "",
          descricao: it.descricao || "",
          destaque: Boolean(d.destaque && d.destaque === it.id),
          preco: it.preco !== undefined ? String(it.preco) : "",
          tipo_variacao: it.tipo_variacao || "sabor",
          variacoes: Array.isArray(it.variacoes) ? it.variacoes.map((v) => ({ rotulo: v.rotulo || "", preco: String(v.preco ?? "") })) : [],
          idade_indicada: it.idade_indicada || "",
          tempo: it.tempo || "",
          altura_permitida: it.altura_permitida || "",
          regras_texto: Array.isArray(it.regras) ? it.regras.join("\n") : "",
          tempos_precos: Array.isArray(it.tempos_precos) && it.tempos_precos.length
            ? it.tempos_precos.map((tp) => ({ tempo: tp.tempo || "", preco: String(tp.preco ?? "") }))
            : [{ tempo: "30 minutos", preco: "" }, { tempo: "1 hora", preco: "" }],
          incluir_foto: Boolean(it.foto),
          foco_foto: (d.enquadramentos && d.enquadramentos[it.id]) || "centro"
        }));
      }
    }

    /* Restaurar rascunho local ao abrir */
    try {
      const salvo = JSON.parse(window.localStorage.getItem(CHAVE_RASCUNHO) || "null");
      if (salvo && salvo.dados) {
        slugEditadoManual = Boolean(salvo.slugEditadoManual);
        urlEditadaManual = Boolean(salvo.urlEditadaManual);
        aplicarObjetoDadosNoFormulario(salvo.dados, salvo.itensEstado, salvo.horariosExtrasEstado);
        if (typeof salvo.pagamentoOutros === "string") {
          document.getElementById("eq-pag-outros").value = salvo.pagamentoOutros;
        }
      }
    } catch (_e) {}

    renderizarHorariosExtras();
    renderizarItensEditor();
    atualizarTudo();

    form.addEventListener("input", (ev) => {
      if (!ev.target.closest("#lista-itens-equipe") && !ev.target.closest("#lista-horarios-tabela") && ev.target.type !== "file") {
        atualizarTudo();
      }
    });
    form.addEventListener("change", (ev) => {
      if (!ev.target.closest("#lista-itens-equipe") && !ev.target.closest("#lista-horarios-tabela") && ev.target.type !== "file") {
        atualizarTudo();
      }
    });

    /* Importar arquivo dados.json existente */
    const inputImportar = document.getElementById("eq-importar-json");
    document.getElementById("btn-importar-json").addEventListener("click", () => inputImportar.click());
    inputImportar.addEventListener("change", (ev) => {
      const arq = ev.target.files && ev.target.files[0];
      if (!arq) return;
      const leitor = new FileReader();
      leitor.onload = () => {
        try {
          const obj = JSON.parse(String(leitor.result || "{}"));
          slugEditadoManual = true;
          urlEditadaManual = Boolean(obj.url_final);
          aplicarObjetoDadosNoFormulario(obj, null, null);
          renderizarHorariosExtras();
          renderizarItensEditor();
          atualizarTudo();
          statusRascunho.textContent = "Arquivo dados.json carregado para edição.";
        } catch (_e) {
          statusRascunho.textContent = "Não foi possível ler o JSON selecionado.";
        }
      };
      leitor.readAsText(arq, "utf-8");
    });

    /* Botão Preencher treino (modo_exemplo = true) */
    document.getElementById("btn-exemplo-treino").addEventListener("click", () => {
      const seg = segmentoAtual();
      const exemplosPorSeg = {
        alimentacao: {
          slug: "barraca-treino-alimentacao",
          modo_exemplo: true,
          consentimento: true,
          segmento: "alimentacao",
          nome_negocio: "Barraca Exemplo",
          quem_atende: "Dona Lúcia (simulação)",
          o_que_oferece: "Pastel frito na hora e caldo de cana gelado, no Parque da Cidade",
          whatsapp: "",
          pix: { autorizado: false, chave: "", recebedor: "" },
          pagamento: ["Dinheiro", "Cartão por aproximação", "Pix na barraca"],
          dias: "Quinta a domingo",
          horarios: { inicio: "08h", fim: "17h", tabela: [{ dias: "Quinta e sexta", horario: "08h às 16h30" }, { dias: "Sábado e domingo", horario: "07h30 às 17h30" }] },
          referencia: "entrada principal, ao lado da sombra das amendoeiras",
          latitude: -12.9949,
          longitude: -38.4611,
          destaque: "pastel-grande-frito-na-hora",
          aceita_pedidos_do_dia: true,
          aceita_encomendas: true,
          historia_aprovada: "Abro a massa cedo na sombra das amendoeiras para servir sempre quentinho.",
          url_final: "https://parque-da-cidade-unijorge.vercel.app/",
          itens: [
            { id: "pastel-grande-frito-na-hora", categoria: "Salgados na hora", nome: "Pastel grande frito na hora", descricao: "Acompanha vinagrete da casa.", tipo_variacao: "sabor", variacoes: [{ rotulo: "Queijo coalho", preco: 10 }, { rotulo: "Camarão seco", preco: 14 }] },
            { id: "cocada-cremosa", categoria: "Doces", nome: "Cocada baiana cremosa", descricao: "Coco fresco ralado no tacho.", preco: 6, variacoes: [] }
          ]
        },
        brinquedos: {
          slug: "barraca-treino-brinquedos",
          modo_exemplo: true,
          consentimento: true,
          segmento: "brinquedos",
          nome_negocio: "Barraca Exemplo",
          quem_atende: "Seu Jorge (simulação)",
          o_que_oferece: "Bolhas de sabão gigantes, pipas sem cerol e bolas leves, no Parque da Cidade",
          whatsapp: "",
          pix: { autorizado: false, chave: "", recebedor: "" },
          pagamento: ["Dinheiro", "Cartão por aproximação", "Pix na barraca"],
          dias: "Sábado, domingo e feriados",
          horarios: { inicio: "08h", fim: "17h", tabela: [{ dias: "Sábado, domingo e feriados", horario: "08h às 17h" }] },
          referencia: "gramado central, ao lado da Praça das Crianças",
          aceita_encomendas: true,
          url_final: "https://parque-da-cidade-unijorge.vercel.app/brinquedos/",
          itens: [
            { id: "kit-bolha-gigante", categoria: "Para o gramado", nome: "Kit bolha de sabão gigante", descricao: "Varinha de algodão com líquido concentrado.", idade_indicada: "A partir de 3 anos", tipo_variacao: "tamanho", variacoes: [{ rotulo: "Refil 250 ml", preco: 15 }, { rotulo: "Refil 500 ml", preco: 18 }] }
          ]
        },
        inflaveis: {
          slug: "barraca-treino-inflaveis",
          modo_exemplo: true,
          consentimento: true,
          segmento: "inflaveis",
          nome_negocio: "Barraca Exemplo",
          quem_atende: "Tia Cris (simulação)",
          o_que_oferece: "Tobogã inflável e cama elástica com monitor na sombra, no Parque da Cidade",
          whatsapp: "",
          pix: { autorizado: false, chave: "", recebedor: "" },
          pagamento: ["Dinheiro", "Cartão de débito", "Pix na barraca"],
          dias: "Sábado, domingo e feriados",
          horarios: { inicio: "08h30", fim: "17h30", tabela: [{ dias: "Sábado, domingo e feriados", horario: "08h30 às 17h30" }] },
          referencia: "área infantil sombreada, próximo ao Parque Infantil",
          aceita_encomendas: true,
          url_final: "https://parque-da-cidade-unijorge.vercel.app/inflaveis/",
          itens: [
            { id: "toboga-inflavel", categoria: "Brinquedos infláveis", nome: "Tobogã inflável colorido", descricao: "Com monitor na escada.", tempo: "15 minutos", preco: 15, idade_indicada: "3 a 12 anos", altura_permitida: "De 0,90 m até 1,50 m", regras: ["Entrada somente sem calçados.", "Responsável próximo ao brinquedo."] }
          ]
        },
        bicicletas: {
          slug: "barraca-treino-bicicletas",
          modo_exemplo: true,
          consentimento: true,
          segmento: "bicicletas",
          nome_negocio: "Barraca Exemplo",
          quem_atende: "Marcos (simulação)",
          o_que_oferece: "Aluguel de bicicletas infantis, aro 26/29 e triciclos na ciclovia, no Parque da Cidade",
          whatsapp: "",
          pix: { autorizado: false, chave: "", recebedor: "" },
          pagamento: ["Dinheiro", "Cartão de débito", "Pix na barraca"],
          dias: "Terça a domingo",
          horarios: { inicio: "07h", fim: "17h", tabela: [{ dias: "Terça a domingo", horario: "07h às 17h" }] },
          referencia: "início da pista de ciclismo, ao lado do estacionamento principal",
          aceita_encomendas: true,
          regras_aluguel: {
            documento: "Documento oficial com foto no cadastro.",
            caucao: "Não cobramos caução em dinheiro.",
            devolucao: "Devolução no mesmo ponto até as 17h."
          },
          url_final: "https://parque-da-cidade-unijorge.vercel.app/bicicletas/",
          itens: [
            { id: "bicicleta-passeio", categoria: "Aluguel na ciclovia", nome: "Bicicleta passeio aro 26 ou 29", descricao: "Marcha leve e cestinha opcional.", tempos_precos: [{ tempo: "30 minutos", preco: 18 }, { tempo: "1 hora", preco: 30 }] }
          ]
        }
      };
      aplicarObjetoDadosNoFormulario(exemplosPorSeg[seg] || exemplosPorSeg.alimentacao, null, null);
      renderizarHorariosExtras();
      renderizarItensEditor();
      atualizarTudo();
      statusRascunho.textContent = "Dados de treino carregados (desmarque o modo simulação para entrevista real).";
    });

    /* Apagar rascunho */
    document.getElementById("btn-apagar-rascunho").addEventListener("click", () => {
      try { window.localStorage.removeItem(CHAVE_RASCUNHO); } catch (_e) {}
      form.reset();
      slugEditadoManual = false;
      urlEditadaManual = false;
      campoDataPrecos.value = dataHojeISO();
      horariosExtrasEstado = [];
      itensEstado = [criarItemVazio()];
      fotosMemoria = { barraca: null, fachada: null, retrato: null };
      fotosItensMemoria = Object.create(null);
      ["barraca", "fachada", "retrato"].forEach((s) => {
        document.getElementById("info-foto-" + s).hidden = true;
      });
      form.querySelectorAll("[aria-invalid]").forEach((el) => el.removeAttribute("aria-invalid"));
      form.querySelectorAll(".mensagem-erro").forEach((el) => { el.hidden = true; });
      atualizarBotaoBaixarTodasFotos();
      renderizarHorariosExtras();
      renderizarItensEditor();
      atualizarTudo();
      statusRascunho.textContent = "Rascunho apagado deste aparelho.";
    });

    /* --- BOTÕES DE COPIAR (INVOKER COMMANDS + FALLBACK SEGURO + LIVE REGION EXTERNA) --- */
    const timersCopia = new WeakMap();
    let ultimaMensagemCopia = "";

    function copiarLegado(texto) {
      const focoAnterior = document.activeElement;
      const area = Object.assign(document.createElement("textarea"), { value: texto });
      area.setAttribute("readonly", "");
      area.style.cssText = "position:fixed;inset-block-start:0;opacity:0";
      document.body.appendChild(area);
      area.select();
      try {
        return document.execCommand("copy");
      } finally {
        area.remove();
        if (focoAnterior && focoAnterior.focus) focoAnterior.focus({ preventScroll: true });
      }
    }

    function anunciarResultadoCopia(botao, ok) {
      const bolha = botao.nextElementSibling;
      if (!bolha) return;
      clearTimeout(timersCopia.get(botao));
      botao.removeAttribute("data-copied");
      botao.removeAttribute("data-failed");
      bolha.classList.remove("visivel", "falha");

      const rotuloSpan = botao.querySelector("span");
      const textoRotulo = rotuloSpan ? rotuloSpan.textContent : "Copiar";
      botao.innerHTML = (ok ? ICONES.confere : ICONES.alerta) + "<span>" + textoRotulo + "</span>";

      let msg = ok ? "Copiado para a área de transferência" : "Não foi possível copiar automaticamente";
      if (msg === ultimaMensagemCopia) msg += "\u00A0";
      ultimaMensagemCopia = msg;

      bolha.textContent = "";
      botao.setAttribute(ok ? "data-copied" : "data-failed", "");
      bolha.classList.add("visivel");
      if (!ok) bolha.classList.add("falha");
      requestAnimationFrame(() => { bolha.textContent = msg; });

      timersCopia.set(botao, setTimeout(() => {
        botao.removeAttribute("data-copied");
        botao.removeAttribute("data-failed");
        botao.innerHTML = ICONES.copiar + "<span>" + textoRotulo + "</span>";
        bolha.classList.remove("visivel", "falha");
        bolha.textContent = "";
      }, 2400));
    }

    async function executarCopia(botao, alvo) {
      sincronizarHorariosDoDOM();
      sincronizarItensDoDOM();
      atualizarTudo();
      const texto = alvo.matches("input, textarea") ? alvo.value : alvo.innerText.trim();
      if (!texto) return;
      try {
        await navigator.clipboard.writeText(texto);
        anunciarResultadoCopia(botao, true);
      } catch (_e) {
        const okLegado = copiarLegado(texto);
        anunciarResultadoCopia(botao, Boolean(okLegado));
      }
    }

    document.addEventListener("command", (event) => {
      if (event.command && event.command.startsWith("--copy")) {
        executarCopia(event.source, event.target);
      }
    }, true);

    if (!("CommandEvent" in window)) {
      document.addEventListener("click", (event) => {
        if (event.defaultPrevented) return;
        const botao = event.target.closest('button[command^="--copy"]');
        if (!botao) return;
        const alvo = document.getElementById(botao.getAttribute("commandfor"));
        if (alvo) executarCopia(botao, alvo);
      });
    }

    /* Baixar prompt em .txt */
    document.getElementById("btn-baixar-prompt-txt").addEventListener("click", () => {
      sincronizarHorariosDoDOM();
      sincronizarItensDoDOM();
      atualizarTudo();
      const dados = montarDadosJSON();
      const promptTxt = document.getElementById("prompt-gerado-chat").value;
      const blob = new Blob([promptTxt], { type: "text/plain;charset=utf-8" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "prompt-" + (dados.slug || "ambulante") + ".txt";
      link.click();
      URL.revokeObjectURL(link.href);
    });

    /* Submissão / Exportação final validada do dados.json */
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      sincronizarHorariosDoDOM();
      sincronizarItensDoDOM();
      atualizarTudo();

      const dados = montarDadosJSON();
      const pendencias = diagnosticarDados(dados);
      const erroBox = document.getElementById("erro-exportacao-equipe");
      const erroTxt = document.getElementById("texto-erro-equipe");

      ["eq-nome", "eq-oferta", "eq-dias", "eq-ref", "eq-zap"].forEach((idC) => {
        document.getElementById(idC).dataset.tocado = "1";
        validarCampoIndividual(idC);
      });

      if (!dados.modo_exemplo && !dados.consentimento) {
        document.getElementById("eq-consentimento").setAttribute("aria-invalid", "true");
        document.getElementById("erro-campo-consentimento").hidden = false;
      }
      if (dados.pix.autorizado && (!dados.pix.recebedor || !dados.pix.chave)) {
        document.getElementById("erro-campo-pix").hidden = false;
      } else {
        document.getElementById("erro-campo-pix").hidden = true;
      }

      if (pendencias.length > 0) {
        erroTxt.textContent = "Complete antes de exportar: " + pendencias[0].msg + ".";
        erroBox.hidden = false;
        const primeiroAlvo = document.getElementById(pendencias[0].id) || erroBox;
        primeiroAlvo.focus();
        return;
      }

      erroBox.hidden = true;
      const blob = new Blob([JSON.stringify(dados, null, 2)], { type: "application/json;charset=utf-8" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "dados.json";
      link.click();
      URL.revokeObjectURL(link.href);
    });
  })();
  </script>
</body>
</html>"""


def gerar_pagina_equipe(out_dir: Path, project_root: Path) -> str:
    """Gera `equipe.html` separada e fora do menu do cliente: roteiro completo de entrevista, prompt pronto para chat, prévia ao vivo, rascunho local + apagar e exportação `dados.json` sem senha."""
    out_dir.mkdir(parents=True, exist_ok=True)
    copy_fonts_to(out_dir, project_root)

    toldos_34 = {seg: render_toldo_svg(seg, altura_lona=34) for seg in ACCENTS}
    toldos_30 = {seg: render_toldo_svg(seg, altura_lona=30) for seg in ACCENTS}

    equipe_html = (
        TEMPLATE_EQUIPE_HTML
        .replace("__FONT_AND_TOKENS_CSS__", FONT_AND_TOKENS_CSS)
        .replace("__TOLDO_INICIAL_34__", toldos_34["alimentacao"])
        .replace("__TOLDO_INICIAL_30__", toldos_30["alimentacao"])
        .replace("__TOLDOS_34_JSON__", json.dumps(toldos_34, ensure_ascii=False))
        .replace("__TOLDOS_30_JSON__", json.dumps(toldos_30, ensure_ascii=False))
        .replace("__ICONES_JSON__", json.dumps(ICONES_2PX, ensure_ascii=False))
        .replace("__IC_LIXEIRA__", ICONES_2PX["lixeira"])
        .replace("__IC_MAIS__", ICONES_2PX["mais"])
        .replace("__IC_PEDIDO__", ICONES_2PX["pedido"])
        .replace("__IC_COPIAR__", ICONES_2PX["copiar"])
        .replace("__IC_CONFERE__", ICONES_2PX["confere"])
        .replace("__IC_ALERTA__", ICONES_2PX["alerta"])
        .replace("__IC_CHEGAR__", ICONES_2PX["chegar"])
        .replace("__IC_COMPARTILHAR__", ICONES_2PX["compartilhar"])
    )

    eq_path = out_dir / "equipe.html"
    eq_path.write_text(equipe_html, encoding="utf-8")
    return str(eq_path)

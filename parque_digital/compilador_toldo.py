"""Compilador estático principal do site do cliente no conceito 'Toldo Aberto'."""

from __future__ import annotations

import html
import json
from pathlib import Path
import re
from typing import Any

from .compressor_fotos import compress_photo_to_webp
from .dados_modelo import carregar_dados_ambulante, formatar_brl
from .estilos_site_toldo import SITE_TOLDO_CSS
from .sistema_toldo import (
    FONT_AND_TOKENS_CSS,
    ICONES_2PX,
    copy_fonts_to,
    render_serrilhado_svg,
    render_toldo_svg,
)

ICONE_FECHAR_2PX = (
    '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>'
)

ENQUADRAMENTOS_MAP = {
    "topo": "center 22%",
    "centro": "center 50%",
    "base": "center 78%",
}

CTA_POR_SEGMENTO = {
    "alimentacao": ("Ver cardápio", "Cardápio"),
    "brinquedos": ("Ver produtos", "Produtos e doces"),
    "inflaveis": ("Ver preços", "Brinquedos e preços"),
    "bicicletas": ("Ver aluguel", "Tabela de aluguel"),
}


def _mensagem_erro_variacao(tipo_variacao: str) -> str:
    t = (tipo_variacao or "sabor").strip().lower()
    artigo = "a" if t in {"opção", "opcao", "porção", "porcao", "cor"} else "o"
    return f"Escolha {artigo} {t} para adicionar."


def _preparar_fotos(
    dados: dict[str, Any],
    pasta_fotos_origem: Path,
    out_dir: Path,
) -> dict[str, dict[str, Any]]:
    """Comprime todas as fotos referenciadas em `dados.json` para WebP <= 150 KB em `out_dir/fotos/`."""
    mapa: dict[str, dict[str, Any]] = {}
    if not pasta_fotos_origem.exists():
        return mapa

    nomes_usados: set[str] = set()
    fotos_obj = dados.get("fotos") or {}
    for chave in ("barraca", "fachada", "retrato"):
        val = str(fotos_obj.get(chave, "")).strip()
        if val:
            nomes_usados.add(val)
    for item in dados.get("itens") or []:
        val = str(item.get("foto", "")).strip()
        if val:
            nomes_usados.add(val)

    dst_fotos = out_dir / "fotos"
    for nome_arq in sorted(nomes_usados):
        src = pasta_fotos_origem / nome_arq
        if not src.exists():
            continue
        stem = Path(nome_arq).stem
        dst = dst_fotos / f"{stem}.webp"
        # Se já é um WebP <= 145 KB, apenas copia e lê dimensões via compressor rápido
        meta = compress_photo_to_webp(src, dst, max_kb=120, max_dim=1080, correcao_leve=True)
        mapa[nome_arq] = {
            "rel": f"fotos/{dst.name}",
            "width": int(meta["width"]),
            "height": int(meta["height"]),
            "kb": float(meta["kb"]),
        }
    return mapa


def _render_primeira_tela_hibrida(dados: dict[str, Any], fotos_meta: dict[str, dict[str, Any]]) -> str:
    seg = dados["segmento"]
    nome = html.escape(dados["nome_negocio"])
    oferta = html.escape(str(dados.get("o_que_oferece", "")).strip())
    dias = str(dados.get("dias", "")).strip()
    horarios = dados.get("horarios") or {}
    h_ini = str(horarios.get("inicio", "")).strip()
    h_fim = str(horarios.get("fim", "")).strip()
    ref = str(dados.get("referencia", "")).strip()
    cta_texto, _ = CTA_POR_SEGMENTO.get(seg, ("Ver cardápio", "Cardápio"))

    linhas_meta: list[str] = []
    if dias and h_ini and h_fim:
        linhas_meta.append(
            f'<li>{ICONES_2PX["relogio"]}<span><strong>{html.escape(dias)}</strong>, das {html.escape(h_ini)} às {html.escape(h_fim)}</span></li>'
        )
    elif dias:
        linhas_meta.append(f'<li>{ICONES_2PX["relogio"]}<span><strong>{html.escape(dias)}</strong></span></li>')
    if ref:
        linhas_meta.append(f'<li>{ICONES_2PX["chegar"]}<span>Perto da <strong>{html.escape(ref)}</strong></span></li>')
    meta_html = f'<ul class="metadados-barraca">{"".join(linhas_meta)}</ul>' if linhas_meta else ""

    link_encomendas = (
        f'<a href="#encomendas" class="link-encomendas" id="cta-encomendas">'
        f'{ICONES_2PX["grupo"]}<span>Pedir orçamento para grupo</span></a>'
        if dados.get("aceita_encomendas")
        else ""
    )

    acoes_html = f"""<div class="hero-acoes-empilhadas">
          <div class="acoes-primeira-tela">
            <a href="#cardapio" class="botao botao-mata" id="cta-cardapio">{ICONES_2PX['cardapio']}<span>{html.escape(cta_texto)}</span></a>
            <a href="#como-chegar" class="botao botao-contorno" id="cta-chegar">{ICONES_2PX['chegar']}<span>Como chegar</span></a>
          </div>
          {link_encomendas}
        </div>"""

    arq_barraca = str((dados.get("fotos") or {}).get("barraca", "")).strip()
    info_foto = fotos_meta.get(arq_barraca)

    if info_foto:
        enquad = ENQUADRAMENTOS_MAP.get(str((dados.get("enquadramentos") or {}).get("barraca", "topo")), "center 22%")
        quem = str(dados.get("quem_atende", "")).strip()
        alt = f"{quem} atendendo na {dados['nome_negocio']}" if quem else f"Atendimento na {dados['nome_negocio']} no Parque da Cidade"
        oferta_html = f'<p class="oferta-parque">{oferta}</p>' if oferta else ""
        return f"""
  <div class="toldo-abertura toldo-desktop-alto">{render_toldo_svg(seg, altura_lona=26)}</div>
  <header class="primeira-tela" style="--foco-foto: {enquad};">
    <div class="conteiner hero-hibrido-palco">
      <div class="hero-hibrido-midia foto-revelada">
        <div class="hero-hibrido-midia-miolo">
          <img src="{info_foto['rel']}" alt="{html.escape(alt)}" width="{info_foto['width']}" height="{info_foto['height']}" fetchpriority="high" class="foto-enquadrada" id="hero-foto">
        </div>
      </div>
      <div class="hero-hibrido-cartao">
        <div class="hero-hibrido-cabeca">
          <h1 class="letreiro-nome" id="hero-nome">{nome}</h1>
          {oferta_html}
        </div>
        <div class="hero-hibrido-rodape">
          {meta_html}
          {acoes_html}
        </div>
      </div>
    </div>
  </header>"""

    # Sem foto: Tabuleta B no celular + Painel amplo C com cartão na base no computador
    oferta_mob = f'<p class="oferta-parque oferta-mobile-only">{oferta}</p>' if oferta else ""
    oferta_desk = f'<p class="oferta-parque oferta-desktop-only">{oferta}</p>' if oferta else ""
    return f"""
  <div class="toldo-abertura">{render_toldo_svg(seg, altura_lona=54)}</div>
  <header class="primeira-tela semfoto-envoltorio">
    <div class="semfoto-painel-acento">
      <div class="semfoto-painel-miolo">
        <h1 class="letreiro-nome" id="hero-nome">{nome}</h1>
        {oferta_mob}
      </div>
    </div>
    <div class="semfoto-cartao-base">
      <div class="semfoto-info-esq">
        {oferta_desk}
        {meta_html}
      </div>
      {acoes_html}
    </div>
  </header>"""


def _render_botao_perguntar(item_nome: str, modo_exemplo: bool, whatsapp_limpo: str, nome_negocio: str) -> str:
    if modo_exemplo or not whatsapp_limpo:
        return (
            '<button type="button" class="botao botao-mata" disabled aria-disabled="true">'
            f'{ICONES_2PX["whatsapp"]}<span>Perguntar no WhatsApp</span></button>'
        )
    msg = f"Olá! Vi {item_nome} no site da {nome_negocio} no Parque da Cidade e gostaria de tirar uma dúvida."
    from urllib.parse import quote
    href = f"https://wa.me/{whatsapp_limpo}?text={quote(msg)}"
    return (
        f'<a href="{href}" target="_blank" rel="noopener noreferrer" class="botao botao-mata">'
        f'{ICONES_2PX["whatsapp"]}<span>Perguntar no WhatsApp</span></a>'
    )


def _render_variacoes_e_placa(item: dict[str, Any], destaque: bool = False) -> tuple[str, str, str]:
    """Retorna (placa_html, variacoes_html, erro_html) para um item."""
    item_id = html.escape(str(item["id"]))
    variacoes = item.get("variacoes") or []
    classe_placa = "placa-preco placa-preco--destaque" if destaque else "placa-preco"
    classe_valor = "preco-destaque" if destaque else "preco-valor"

    if variacoes:
        precos = [float(v["preco"]) for v in variacoes]
        menor = min(precos)
        maior = max(precos)
        rotulo_inicial = formatar_brl(menor) if menor == maior else f"A partir de {formatar_brl(menor)}"
        placa_html = (
            f'<span class="{classe_placa}" data-placa-item="{item_id}">'
            f'<span class="placa-furo" aria-hidden="true"></span>'
            f'<span class="{classe_valor}" data-placa-texto="{item_id}">{html.escape(rotulo_inicial)}</span>'
            f'</span>'
        )
        tipo_var = str(item.get("tipo_variacao", "sabor")).strip() or "sabor"
        pilulas: list[str] = []
        for idx, v in enumerate(variacoes):
            rot = str(v["rotulo"])
            pr = float(v["preco"])
            sufixo_preco = f" · {formatar_brl(pr)}" if menor != maior else ""
            pilulas.append(
                f'<button type="button" class="pilula-variacao" role="radio" aria-checked="false" '
                f'data-escolher-variacao="{item_id}" data-var-indice="{idx}" '
                f'data-var-rotulo="{html.escape(rot)}" data-var-preco="{pr:.2f}" '
                f'data-var-preco-fmt="{html.escape(formatar_brl(pr))}">'
                f'<span>{html.escape(rot + sufixo_preco)}</span></button>'
            )
        var_html = (
            f'<div class="grupo-variacoes" role="radiogroup" aria-label="Opções de {html.escape(tipo_var)} para {html.escape(item["nome"])}">'
            f'{"".join(pilulas)}</div>'
        )
        msg_erro = _mensagem_erro_variacao(tipo_var)
        erro_html = (
            f'<p class="mensagem-erro" id="erro-item-{item_id}" role="alert" hidden>'
            f'{ICONES_2PX["alerta"]}<span>{html.escape(msg_erro)}</span></p>'
        )
        return placa_html, var_html, erro_html

    preco_unico = float(item.get("preco", 0.0))
    placa_html = (
        f'<span class="{classe_placa}" data-placa-item="{item_id}">'
        f'<span class="placa-furo" aria-hidden="true"></span>'
        f'<span class="{classe_valor}">{html.escape(formatar_brl(preco_unico))}</span>'
        f'</span>'
    )
    return placa_html, "", ""


def _render_comanda_miolo(sufixo_id: str, modo_exemplo: bool) -> str:
    btn_zap_attrs = 'disabled aria-disabled="true"' if modo_exemplo else ""
    aviso_demo = " (WhatsApp desativado no exemplo)" if modo_exemplo else ""
    return f"""
      <div class="comanda-envoltorio" data-comanda-instancia="{sufixo_id}">
        {render_serrilhado_svg("topo")}
        <div class="comanda-corpo">
          <div class="comanda-acoes-topo">
            <div>
              <h3 class="nome-item">Seu pedido</h3>
              <p class="texto-apoio" data-comanda-resumo-qtd>0 itens</p>
            </div>
            <button type="button" class="botao-limpar" data-limpar-pedido hidden>
              {ICONES_2PX["lixeira"]}<span>Limpar</span>
            </button>
          </div>

          <div class="comanda-vazia" data-comanda-vazia>
            Seu pedido está vazio. Escolha um item no cardápio.
          </div>

          <ul class="comanda-lista" data-comanda-lista hidden></ul>

          <div data-comanda-rodape hidden>
            <div class="grupo-campo" style="margin-bottom: var(--s-16);">
              <label for="obs-pedido-{sufixo_id}">Observação</label>
              <textarea id="obs-pedido-{sufixo_id}" name="observacao_pedido" class="campo-entrada" rows="2" data-comanda-obs placeholder="Ex.: pastel bem passado, sem cebola no vinagrete"></textarea>
            </div>

            <div class="comanda-total-bloco">
              <span style="font-weight: 700;">Total estimado</span>
              <span class="preco-destaque" data-comanda-total>R$ 0,00</span>
            </div>

            <button type="button" class="botao botao-mata" style="width: 100%;" data-abrir-pedido-zap {btn_zap_attrs}>
              {ICONES_2PX["whatsapp"]}<span>Abrir pedido no WhatsApp</span>
            </button>
            <p class="texto-apoio" style="margin-top: var(--s-12);">
              O pedido só vale depois da confirmação na conversa.{aviso_demo}
            </p>
            <details class="previa-texto-pedido">
              <summary>Conferir mensagem montada do pedido</summary>
              <pre data-comanda-previa-msg></pre>
            </details>
          </div>
        </div>
        {render_serrilhado_svg("base")}
      </div>"""


def _render_secao_catalogo(
    dados: dict[str, Any],
    fotos_meta: dict[str, dict[str, Any]],
    whatsapp_limpo: str,
) -> str:
    seg = dados["segmento"]
    modo_exemplo = bool(dados.get("modo_exemplo", False))
    itens = dados.get("itens") or []
    if not itens:
        return ""

    _, titulo_secao = CTA_POR_SEGMENTO.get(seg, ("Ver cardápio", "Cardápio"))
    data_conf = str(dados.get("data_precos_conferidos", "")).strip()
    selo_html = (
        f'<span class="selo-conferencia">{ICONES_2PX["data"]}<span>Preços conferidos em {html.escape(data_conf)}</span></span>'
        if data_conf
        else ""
    )

    enquadramentos = dados.get("enquadramentos") or {}

    # 1. SEGMENTO ALIMENTAÇÃO
    if seg == "alimentacao":
        usa_comanda = bool(dados.get("aceita_pedidos_do_dia", False))
        categorias: list[str] = []
        for it in itens:
            cat = str(it.get("categoria", "Cardápio")).strip() or "Cardápio"
            if cat not in categorias:
                categorias.append(cat)

        filtros_html = ""
        if len(categorias) > 1:
            botoes_filtro = [
                f'<button type="button" class="pilula-variacao" aria-pressed="true" data-filtrar-categoria="__todas__">'
                f'{ICONES_2PX["confere"]}<span>Todos</span></button>'
            ]
            for cat in categorias:
                botoes_filtro.append(
                    f'<button type="button" class="pilula-variacao" aria-pressed="false" data-filtrar-categoria="{html.escape(cat)}">'
                    f'<span>{html.escape(cat)}</span></button>'
                )
            filtros_html = f"""
      <div class="barra-filtros-envoltorio" id="barra-filtros">
        <div class="barra-filtros-interna">
          <div class="conteiner">
            <nav aria-label="Filtrar categorias do cardápio">
              <div class="trilho-filtros" id="trilho-filtros">
                {"".join(botoes_filtro)}
              </div>
            </nav>
          </div>
        </div>
      </div>"""

        # Destaque da casa opcional
        id_destaque = str(dados.get("destaque", "")).strip()
        destaque_html = ""
        for it in itens:
            if str(it.get("id")) == id_destaque and id_destaque:
                placa_d, var_d, erro_d = _render_variacoes_e_placa(it, destaque=True)
                arq_f = str(it.get("foto", "")).strip()
                meta_f = fotos_meta.get(arq_f)
                foco_d = ENQUADRAMENTOS_MAP.get(str(enquadramentos.get(id_destaque, "centro")), "center 50%")
                foto_d_html = (
                    f'<div class="destaque-foto-envoltorio" style="--foco-foto: {foco_d};">'
                    f'<img src="{meta_f["rel"]}" alt="{html.escape(it["nome"])}" width="{meta_f["width"]}" height="{meta_f["height"]}" loading="lazy" class="foto-enquadrada">'
                    f'</div>'
                    if meta_f
                    else ""
                )
                acao_d = (
                    f'<button type="button" class="botao botao-adicionar" data-adicionar-item="{html.escape(id_destaque)}">'
                    f'{ICONES_2PX["pedido"]}<span>Adicionar</span></button>'
                    if usa_comanda
                    else _render_botao_perguntar(it["nome"], modo_exemplo, whatsapp_limpo, dados["nome_negocio"])
                )
                desc_d = f'<p>{html.escape(str(it.get("descricao", "")))}</p>' if it.get("descricao") else ""
                destaque_html = f"""
          <article class="bloco-destaque-casa" data-bloco-destaque data-item-card="{html.escape(id_destaque)}">
            {foto_d_html}
            <div class="destaque-miolo">
              <span class="selo-destaque-casa">{ICONES_2PX['confere']}<span>Destaque da casa</span></span>
              <div class="destaque-cabeca">
                <h3 class="destaque-titulo">{html.escape(it['nome'])}</h3>
                {placa_d}
              </div>
              {desc_d}
              {var_d}
              {erro_d}
              <div>{acao_d}</div>
            </div>
          </article>"""
                break

        blocos_cat: list[str] = []
        for cat in categorias:
            linhas: list[str] = []
            for it in itens:
                if (str(it.get("categoria", "Cardápio")).strip() or "Cardápio") != cat:
                    continue
                if str(it.get("id")) == id_destaque and destaque_html:
                    # Evita duplicar o ID dos controles interativos quando já exibido no Destaque da casa
                    continue
                iid = str(it["id"])
                placa_i, var_i, erro_i = _render_variacoes_e_placa(it, destaque=False)
                arq_f = str(it.get("foto", "")).strip()
                meta_f = fotos_meta.get(arq_f)
                desc_i = f'<p class="texto-apoio">{html.escape(str(it.get("descricao", "")))}</p>' if it.get("descricao") else ""
                acao_i = (
                    f'<button type="button" class="botao botao-adicionar" data-adicionar-item="{html.escape(iid)}">'
                    f'{ICONES_2PX["pedido"]}<span>Adicionar</span></button>'
                    if usa_comanda
                    else _render_botao_perguntar(it["nome"], modo_exemplo, whatsapp_limpo, dados["nome_negocio"])
                )

                if meta_f:
                    foco_i = ENQUADRAMENTOS_MAP.get(str(enquadramentos.get(iid, "centro")), "center 50%")
                    linhas.append(f"""
                <article class="linha-item" data-item-card="{html.escape(iid)}">
                  <div class="linha-item-topo">
                    <div class="miniatura-1x1" style="--foco-foto: {foco_i};">
                      <img src="{meta_f['rel']}" alt="{html.escape(it['nome'])}" width="{meta_f['width']}" height="{meta_f['height']}" loading="lazy" class="foto-enquadrada">
                    </div>
                    <div class="linha-item-textos">
                      <div class="linha-item-cabeca-foto">
                        <h4 class="nome-item">{html.escape(it['nome'])}</h4>
                        {placa_i}
                      </div>
                      {desc_i}
                    </div>
                  </div>
                  {var_i}
                  {erro_i}
                  <div class="rodape-acao-item">{acao_i}</div>
                </article>""")
                else:
                    linhas.append(f"""
                <article class="linha-item linha-item--tipografica" data-item-card="{html.escape(iid)}">
                  <div class="linha-item-textos">
                    <div class="cabeca-tipografica">
                      <h4 class="nome-item">{html.escape(it['nome'])}</h4>
                      {placa_i}
                    </div>
                    {desc_i}
                  </div>
                  {var_i}
                  {erro_i}
                  <div class="rodape-acao-item">{acao_i}</div>
                </article>""")

            if linhas:
                blocos_cat.append(f"""
            <div class="grupo-categoria-bloco" data-secao-categoria="{html.escape(cat)}">
              <h3 class="titulo-categoria">{html.escape(cat)}</h3>
              <div class="grade-linhas-cardapio">
                {"".join(linhas)}
              </div>
            </div>""")

        classe_palco = "palco-cardapio-comanda palco-cardapio-comanda--com-comanda" if usa_comanda else "palco-cardapio-comanda"
        aside_comanda = (
            f'<aside class="coluna-comanda-fixa" aria-label="Comanda do pedido">{_render_comanda_miolo("desktop", modo_exemplo)}</aside>'
            if usa_comanda
            else ""
        )

        return f"""
    <section id="cardapio" class="secao-catalogo" aria-labelledby="titulo-cardapio">
      <div class="conteiner">
        <div class="cabecalho-secao">
          <h2 id="titulo-cardapio" class="titulo-secao">{html.escape(titulo_secao)}</h2>
          {selo_html}
        </div>
      </div>
      {filtros_html}
      <div class="conteiner {classe_palco}">
        <div class="coluna-itens-cardapio">
          {destaque_html}
          {"".join(blocos_cat)}
        </div>
        {aside_comanda}
      </div>
    </section>"""

    # 2. SEGMENTO BRINQUEDOS E DOCES (grade de 2 colunas com foto/tipografia, preço e idade indicada)
    if seg == "brinquedos":
        cartoes: list[str] = []
        for it in itens:
            iid = str(it["id"])
            placa_i, var_i, _ = _render_variacoes_e_placa(it, destaque=False)
            arq_f = str(it.get("foto", "")).strip()
            meta_f = fotos_meta.get(arq_f)
            idade = str(it.get("idade_indicada", "")).strip()
            idade_html = f'<span class="etiqueta-idade">Idade indicada: {html.escape(idade)}</span>' if idade else ""
            cat_rotulo = str(it.get("categoria", "")).strip()
            topo_visual = (
                f'<div class="miniatura-1x1" style="width:100%;height:auto;aspect-ratio:1/1;">'
                f'<img src="{meta_f["rel"]}" alt="{html.escape(it["nome"])}" width="{meta_f["width"]}" height="{meta_f["height"]}" loading="lazy" class="foto-enquadrada"></div>'
                if meta_f
                else (f'<p class="selo-tipografico-brinquedo">{html.escape(cat_rotulo)}</p>' if cat_rotulo else "")
            )
            desc_i = f'<p class="texto-apoio">{html.escape(str(it.get("descricao", "")))}</p>' if it.get("descricao") else ""
            cartoes.append(f"""
          <article class="item-brinquedo" data-item-card="{html.escape(iid)}">
            <div style="display:flex;flex-direction:column;gap:var(--s-12);">
              {topo_visual}
              <h3 class="nome-item">{html.escape(it['nome'])}</h3>
              {idade_html}
              {desc_i}
              <div>{placa_i}</div>
              {var_i}
            </div>
            <div>{_render_botao_perguntar(it['nome'], modo_exemplo, whatsapp_limpo, dados['nome_negocio'])}</div>
          </article>""")
        return f"""
    <section id="cardapio" class="secao-catalogo" aria-labelledby="titulo-cardapio">
      <div class="conteiner">
        <div class="cabecalho-secao">
          <h2 id="titulo-cardapio" class="titulo-secao">{html.escape(titulo_secao)}</h2>
          {selo_html}
        </div>
        <div class="grade-brinquedos">
          {"".join(cartoes)}
        </div>
      </div>
    </section>"""

    # 3. SEGMENTO INFLÁVEIS (um bloco grande por brinquedo com tempo, preço, idade, altura e regras)
    if seg == "inflaveis":
        blocos: list[str] = []
        for it in itens:
            iid = str(it["id"])
            placa_i, var_i, _ = _render_variacoes_e_placa(it, destaque=True)
            ficha_pares: list[str] = []
            for rot_f, ch_f in (("Tempo", "tempo"), ("Idade indicada", "idade_indicada"), ("Altura permitida", "altura_permitida")):
                val_f = str(it.get(ch_f, "")).strip()
                if val_f:
                    ficha_pares.append(f'<div class="ficha-dado"><dt>{rot_f}</dt><dd>{html.escape(val_f)}</dd></div>')
            ficha_html = f'<dl class="ficha-tecnica-inflavel">{"".join(ficha_pares)}</dl>' if ficha_pares else ""
            regras = [str(r).strip() for r in (it.get("regras") or []) if str(r).strip()]
            regras_html = (
                '<div><h4 style="font-weight:700;margin-bottom:var(--s-8);">Regras de uso</h4>'
                '<ul class="regras-inflavel">'
                + "".join(f"<li>{html.escape(r)}</li>" for r in regras)
                + "</ul></div>"
                if regras
                else ""
            )
            desc_i = f'<p>{html.escape(str(it.get("descricao", "")))}</p>' if it.get("descricao") else ""
            blocos.append(f"""
          <article class="bloco-inflavel" data-item-card="{html.escape(iid)}">
            <div class="destaque-cabeca">
              <h3 class="destaque-titulo">{html.escape(it['nome'])}</h3>
              {placa_i}
            </div>
            {desc_i}
            {ficha_html}
            {var_i}
            {regras_html}
            <div>{_render_botao_perguntar(it['nome'], modo_exemplo, whatsapp_limpo, dados['nome_negocio'])}</div>
          </article>""")
        return f"""
    <section id="cardapio" class="secao-catalogo" aria-labelledby="titulo-cardapio">
      <div class="conteiner">
        <div class="cabecalho-secao">
          <h2 id="titulo-cardapio" class="titulo-secao">{html.escape(titulo_secao)}</h2>
          {selo_html}
        </div>
        <div class="lista-inflaveis">
          {"".join(blocos)}
        </div>
      </div>
    </section>"""

    # 4. SEGMENTO BICICLETAS (tabela responsiva de tipo por tempo + documento, caução e devolução)
    colunas_tempo: list[str] = []
    for it in itens:
        for tp in it.get("tempos_precos") or []:
            t_nome = str(tp.get("tempo", "")).strip()
            if t_nome and t_nome not in colunas_tempo:
                colunas_tempo.append(t_nome)

    ths_tempo = "".join(f'<th scope="col">{html.escape(t)}</th>' for t in colunas_tempo)
    linhas_tr: list[str] = []
    for it in itens:
        mapa_tp = {str(tp["tempo"]).strip(): float(tp["preco"]) for tp in (it.get("tempos_precos") or []) if "tempo" in tp and "preco" in tp}
        desc_b = f'<div class="texto-apoio" style="font-weight:400;margin-top:4px;">{html.escape(str(it.get("descricao", "")))}</div>' if it.get("descricao") else ""
        tds = "".join(
            f'<td data-tempo-rotulo="{html.escape(t)}"><span class="placa-preco"><span class="placa-furo" aria-hidden="true"></span>'
            f'<span class="preco-valor">{html.escape(formatar_brl(mapa_tp[t]))}</span></span></td>'
            if t in mapa_tp
            else f'<td data-tempo-rotulo="{html.escape(t)}">—</td>'
            for t in colunas_tempo
        )
        linhas_tr.append(f'<tr><th scope="row"><span class="nome-item">{html.escape(it["nome"])}</span>{desc_b}</th>{tds}</tr>')

    regras_aluguel = dados.get("regras_aluguel") or {}
    cartoes_regras: list[str] = []
    for rot_r, ch_r in (("Documento", "documento"), ("Caução", "caucao"), ("Devolução", "devolucao")):
        val_r = str(regras_aluguel.get(ch_r, "")).strip()
        if val_r:
            cartoes_regras.append(f'<div class="bloco-regra-bike"><h3>{rot_r}</h3><p>{html.escape(val_r)}</p></div>')
    bloco_regras_html = f'<div class="grade-regras-bikes">{"".join(cartoes_regras)}</div>' if cartoes_regras else ""

    return f"""
    <section id="cardapio" class="secao-catalogo" aria-labelledby="titulo-cardapio">
      <div class="conteiner">
        <div class="cabecalho-secao">
          <h2 id="titulo-cardapio" class="titulo-secao">{html.escape(titulo_secao)}</h2>
          {selo_html}
        </div>
        <div tabindex="0" role="region" aria-labelledby="legenda-tabela-bikes" class="tabela-envoltorio">
          <table class="tabela-bikes">
            <caption id="legenda-tabela-bikes">Valores de aluguel por modelo e tempo</caption>
            <thead>
              <tr>
                <th scope="col">Modelo</th>
                {ths_tempo}
              </tr>
            </thead>
            <tbody>
              {"".join(linhas_tr)}
            </tbody>
          </table>
        </div>
        {bloco_regras_html}
        <div>{_render_botao_perguntar("Aluguel de bicicletas", modo_exemplo, whatsapp_limpo, dados["nome_negocio"])}</div>
      </div>
    </section>"""


def _render_secao_como_chegar(dados: dict[str, Any], fotos_meta: dict[str, dict[str, Any]]) -> str:
    ref = str(dados.get("referencia", "")).strip()
    horarios = dados.get("horarios") or {}
    tabela_h = horarios.get("tabela") or []
    lat = dados.get("latitude")
    lng = dados.get("longitude")
    pagamentos = [str(p).strip() for p in (dados.get("pagamento") or []) if str(p).strip()]
    pix = dados.get("pix") or {}
    modo_exemplo = bool(dados.get("modo_exemplo", False))

    if not (ref or tabela_h or pagamentos):
        return ""

    ref_html = f'<p class="referencia-destaque">Perto da {html.escape(ref)}.</p>' if ref else ""

    linhas_h = "".join(
        f'<tr><th scope="row">{html.escape(str(l.get("dias", "")))}</th><td>{html.escape(str(l.get("horario", "")))}</td></tr>'
        for l in tabela_h
        if l.get("dias") and l.get("horario")
    )
    tabela_html = (
        f'<table class="tabela-horarios" aria-label="Dias e horários de atendimento"><tbody>{linhas_h}</tbody></table>'
        if linhas_h
        else ""
    )

    btn_mapa = ""
    if lat not in (None, "") and lng not in (None, ""):
        url_mapa = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        btn_mapa = (
            f'<a href="{html.escape(url_mapa)}" target="_blank" rel="noopener noreferrer" class="botao botao-claro-escuro">'
            f'{ICONES_2PX["chegar"]}<span>Como chegar</span></a>'
        )

    arq_fachada = str((dados.get("fotos") or {}).get("fachada", "")).strip()
    meta_fachada = fotos_meta.get(arq_fachada)
    foco_fachada = ENQUADRAMENTOS_MAP.get(str((dados.get("enquadramentos") or {}).get("fachada", "centro")), "center 50%")
    col_dir_html = (
        f'<div class="chegar-col-dir"><div class="foto-fachada" style="--foco-foto: {foco_fachada};">'
        f'<img src="{meta_fachada["rel"]}" alt="Vista da {html.escape(dados["nome_negocio"])} no Parque da Cidade" '
        f'width="{meta_fachada["width"]}" height="{meta_fachada["height"]}" loading="lazy" class="foto-enquadrada">'
        f'</div></div>'
        if meta_fachada
        else ""
    )

    # Pix só se autorizado e não for exemplo
    pix_autorizado = bool(pix.get("autorizado")) and not modo_exemplo
    chave_pix = str(pix.get("chave", "")).strip()
    recebedor_pix = str(pix.get("recebedor", "")).strip()
    pix_html = ""
    if pix_autorizado and chave_pix and recebedor_pix:
        pix_html = f"""
        <div class="caixa-pix">
          <p><strong>Recebedor:</strong> {html.escape(recebedor_pix)}</p>
          <p>Chave Pix: <code id="pix-chave-valor">{html.escape(chave_pix)}</code></p>
          <div style="display:flex;flex-wrap:wrap;align-items:center;gap:var(--s-12);">
            <button type="button" class="botao botao-claro-escuro" command="--copy" commandfor="pix-chave-valor" id="btn-copiar-pix">
              {ICONES_2PX["copiar"]}<span>Copiar chave Pix</span>
            </button>
            <span class="bolha-status-copia" role="status" id="status-copia-pix"></span>
          </div>
          <p class="mensagem-erro" id="erro-copia-pix" role="alert" hidden>
            {ICONES_2PX["alerta"]}<span>Não foi possível copiar. Toque e segure a chave.</span>
          </p>
          <p class="texto-apoio">Confira o nome antes de pagar.</p>
        </div>"""

    como_pagar_html = ""
    if pagamentos or pix_html:
        itens_pag = "".join(f'<li class="item-pagamento">{html.escape(p)}</li>' for p in pagamentos)
        lista_pag = f'<ul class="lista-pagamentos">{itens_pag}</ul>' if itens_pag else ""
        como_pagar_html = f"""
      <div class="bloco-como-pagar">
        <h3 class="titulo-secao" style="font-size: clamp(1.5rem, 3vw, 2.25rem);">Como pagar</h3>
        {lista_pag}
        {pix_html}
      </div>"""

    return f"""
    <section id="como-chegar" class="secao-como-chegar fundo-escuro" aria-labelledby="titulo-como-chegar">
      <div class="conteiner">
        <h2 id="titulo-como-chegar" class="titulo-secao">Como chegar</h2>
        {ref_html}
        <div class="grade-chegar">
          <div class="chegar-col-esq">
            {tabela_html}
            {btn_mapa}
          </div>
          {col_dir_html}
        </div>
        {como_pagar_html}
      </div>
    </section>"""


def _render_secao_encomendas(dados: dict[str, Any]) -> str:
    if not dados.get("aceita_encomendas"):
        return ""
    modo_exemplo = bool(dados.get("modo_exemplo", False))
    nota_demo = (
        '<p class="texto-apoio" id="aviso-encomenda-demo" role="status"></p>'
        if modo_exemplo
        else ""
    )
    return f"""
    <section id="encomendas" class="secao-encomendas" aria-labelledby="titulo-encomendas">
      <div class="conteiner">
        <h2 id="titulo-encomendas" class="titulo-secao">Encomendas para grupos</h2>
        <p class="texto-apoio" style="margin-top: var(--s-8);">
          Preencha os dados para montar a mensagem de orçamento para piqueniques, aniversários ou turmas no parque.
        </p>
        <div class="grade-encomendas">
          <form class="form-encomendas" id="form-encomendas" aria-labelledby="titulo-encomendas" novalidate>
            <div class="linha-dupla-campos">
              <div class="grupo-campo">
                <label for="enc-data">Data desejada *</label>
                <input type="date" id="enc-data" name="data" class="campo-entrada" required aria-describedby="erro-enc-data">
                <p class="mensagem-erro" id="erro-enc-data" role="alert" hidden>
                  {ICONES_2PX["alerta"]}<span>Escolha uma data a partir de hoje.</span>
                </p>
              </div>
              <div class="grupo-campo">
                <label for="enc-hora">Horário aproximado *</label>
                <input type="time" id="enc-hora" name="hora" class="campo-entrada" required>
              </div>
            </div>

            <div class="linha-dupla-campos">
              <div class="grupo-campo">
                <label for="enc-pessoas">Quantidade de pessoas *</label>
                <input type="text" inputmode="numeric" pattern="[0-9]+" id="enc-pessoas" name="pessoas" class="campo-entrada" placeholder="Ex.: 15" required>
              </div>
              <div class="grupo-campo">
                <label for="enc-nome">Seu nome *</label>
                <input type="text" id="enc-nome" name="nome" autocomplete="name" class="campo-entrada" required>
              </div>
            </div>

            <div class="grupo-campo">
              <label for="enc-pedido">O que deseja encomendar *</label>
              <textarea id="enc-pedido" name="pedido" rows="3" class="campo-entrada" placeholder="Ex.: 30 pastéis sortidos e 2 jarras de caldo de cana" required></textarea>
            </div>

            <fieldset class="grupo-campo">
              <legend>Retirada ou entrega *</legend>
              <div class="opcoes-recebimento">
                <label class="opcao-radio" for="enc-retirada">
                  <input type="radio" id="enc-retirada" name="recebimento" value="Retirada na barraca" checked>
                  <span>Retirada na barraca</span>
                </label>
                <label class="opcao-radio" for="enc-entrega">
                  <input type="radio" id="enc-entrega" name="recebimento" value="Entrega a confirmar na conversa">
                  <span>Entrega a confirmar na conversa</span>
                </label>
              </div>
            </fieldset>

            <div>
              <button type="submit" class="botao botao-mata" id="btn-enviar-encomenda">
                {ICONES_2PX["grupo"]}<span>Pedir orçamento para grupo</span>
              </button>
              <p class="texto-apoio" style="margin-top: var(--s-12);">
                O valor e a disponibilidade são confirmados na conversa.
              </p>
              {nota_demo}
            </div>
          </form>

          <div class="painel-previa-conversa">
            <p class="texto-apoio" style="font-weight: 700; margin-bottom: var(--s-8);">Prévia ao vivo da mensagem</p>
            <div class="balao-conversa" id="balao-previa-encomenda" aria-live="polite"></div>
          </div>
        </div>
      </div>
    </section>"""


def _render_secao_quem_atende(dados: dict[str, Any], fotos_meta: dict[str, dict[str, Any]]) -> str:
    historia = str(dados.get("historia_aprovada", "")).strip()
    quem = str(dados.get("quem_atende", "")).strip()
    if not historia:
        return ""

    arq_retrato = str((dados.get("fotos") or {}).get("retrato", "")).strip()
    meta_retrato = fotos_meta.get(arq_retrato)
    foco_retrato = ENQUADRAMENTOS_MAP.get(str((dados.get("enquadramentos") or {}).get("retrato", "topo")), "center 22%")

    if meta_retrato:
        bloco_esq = (
            f'<div class="moldura-retrato-4x5" style="--foco-foto: {foco_retrato};">'
            f'<img src="{meta_retrato["rel"]}" alt="Retrato de {html.escape(quem or dados["nome_negocio"])}" '
            f'width="{meta_retrato["width"]}" height="{meta_retrato["height"]}" loading="lazy" class="foto-enquadrada">'
            f'</div>'
        )
    else:
        bloco_esq = (
            f'<div class="placa-nome-atendente">'
            f'<p class="texto-apoio">Atendimento direto na barraca</p>'
            f'<p class="titulo-secao" style="margin-top: var(--s-8);">{html.escape(quem or dados["nome_negocio"])}</p>'
            f'</div>'
        )

    assinatura = f'<p class="texto-apoio" style="margin-top: var(--s-16); font-weight: 700;">— {html.escape(quem)}</p>' if quem else ""

    return f"""
    <section id="quem-atende" class="secao-quem-atende" aria-labelledby="titulo-quem-atende">
      <div class="conteiner">
        <h2 id="titulo-quem-atende" class="titulo-secao" style="margin-bottom: var(--s-32);">Quem atende</h2>
        <div class="grade-quem-atende">
          <div class="quem-retrato-col">
            {bloco_esq}
          </div>
          <div class="quem-frase-col">
            <blockquote class="citacao-quem-atende">“{html.escape(historia)}”</blockquote>
            {assinatura}
          </div>
        </div>
      </div>
    </section>"""


def _render_rodape(dados: dict[str, Any], whatsapp_limpo: str) -> str:
    modo_exemplo = bool(dados.get("modo_exemplo", False))
    if modo_exemplo or not whatsapp_limpo:
        btn_zap = (
            '<button type="button" class="botao botao-claro-escuro" disabled aria-disabled="true">'
            f'{ICONES_2PX["whatsapp"]}<span>Chamar no WhatsApp</span></button>'
        )
    else:
        btn_zap = (
            f'<a href="https://wa.me/{whatsapp_limpo}" target="_blank" rel="noopener noreferrer" class="botao botao-claro-escuro">'
            f'{ICONES_2PX["whatsapp"]}<span>Chamar no WhatsApp</span></a>'
        )

    return f"""
  <footer class="rodape-site fundo-escuro">
    <div class="conteiner">
      <div class="rodape-acoes">
        {btn_zap}
        <button type="button" class="botao botao-claro-escuro" id="btn-compartilhar">
          {ICONES_2PX["compartilhar"]}<span>Compartilhar</span>
        </button>
        <span class="bolha-status-copia" role="status" id="status-compartilhar"></span>
      </div>
      <div class="rodape-creditos">
        <div>
          <h2>Projeto de Extensão Parque Digital — Unijorge</h2>
          <p>
            Página gratuita criada por estudantes do Centro Universitário Jorge Amado (Unijorge) em parceria com trabalhadores ambulantes do Parque da Cidade Joventino Silva, em Salvador.
          </p>
        </div>
        <div>
          <h2>Como pedir correção ou retirada do ar</h2>
          <p>
            O ambulante titular pode pedir alteração de preço, troca de foto ou retirada imediata desta página a qualquer momento falando com a equipe extensionista da Unijorge no Parque da Cidade ou na coordenação de Extensão da Unijorge.
          </p>
        </div>
      </div>
    </div>
  </footer>"""


def _gerar_script_cliente(dados: dict[str, Any], whatsapp_limpo: str) -> str:
    catalogo_js = {}
    for it in dados.get("itens") or []:
        iid = str(it["id"])
        variacoes = it.get("variacoes") or []
        catalogo_js[iid] = {
            "id": iid,
            "nome": str(it["nome"]),
            "tipoVariacao": str(it.get("tipo_variacao", "sabor")).strip() or "sabor",
            "precoUnico": float(it.get("preco", 0.0)) if not variacoes else None,
            "variacoes": [{"rotulo": str(v["rotulo"]), "preco": float(v["preco"])} for v in variacoes],
        }

    cfg = {
        "slug": str(dados.get("slug", "barraca")),
        "nomeNegocio": str(dados["nome_negocio"]),
        "modoExemplo": bool(dados.get("modo_exemplo", False)),
        "whatsapp": whatsapp_limpo,
        "urlFinal": str(dados.get("url_final", "")),
        "usaComanda": bool(dados.get("segmento") == "alimentacao" and dados.get("aceita_pedidos_do_dia")),
        "catalogo": catalogo_js,
        "iconeConfere": ICONES_2PX["confere"],
        "iconePedido": ICONES_2PX["pedido"],
        "iconeLixeira": ICONES_2PX["lixeira"],
        "msgDemoEncomenda": (
            "Modelo demonstrativo: mensagem conferida na prévia ao lado (envio desativado no exemplo)."
            if dados.get("modo_exemplo")
            else ""
        ),
    }

    return f"""
  <script>
  (() => {{
    const CFG = {json.dumps(cfg, ensure_ascii=False)};
    const CHAVE_STORAGE = "toldo_aberto_pedido_" + CFG.slug;

    function formatarBRL(valor) {{
      return "R$ " + Number(valor || 0).toFixed(2).replace(".", ",");
    }}

    /* 1. Barra de filtros fixa + fallback IntersectionObserver para dicas de rolagem */
    const barraFiltros = document.getElementById("barra-filtros");
    if (barraFiltros && !CSS.supports("container-type", "scroll-state")) {{
      const obsSticky = new IntersectionObserver(
        ([e]) => barraFiltros.classList.toggle("is-stuck", e.intersectionRatio < 1),
        {{ threshold: [1], rootMargin: "-1px 0px 0px 0px" }}
      );
      obsSticky.observe(barraFiltros);
    }}

    const trilhoFiltros = document.getElementById("trilho-filtros");
    if (trilhoFiltros && !CSS.supports("animation-timeline", "scroll()")) {{
      const primeiro = trilhoFiltros.firstElementChild;
      const ultimo = trilhoFiltros.lastElementChild;
      if (primeiro && ultimo) {{
        const obsFade = new IntersectionObserver((entries) => {{
          for (const ent of entries) {{
            trilhoFiltros.classList.toggle(ent.target === primeiro ? "more-start" : "more-end", ent.intersectionRatio < 1);
          }}
        }}, {{ root: trilhoFiltros, threshold: 1, rootMargin: "1px" }});
        obsFade.observe(primeiro);
        obsFade.observe(ultimo);
      }}
    }}

    document.querySelectorAll("[data-filtrar-categoria]").forEach((btn) => {{
      btn.addEventListener("click", () => {{
        const alvo = btn.getAttribute("data-filtrar-categoria");
        document.querySelectorAll("[data-filtrar-categoria]").forEach((b) => {{
          const ativo = b === btn;
          b.setAttribute("aria-pressed", ativo ? "true" : "false");
          const rotulo = b.querySelector("span") ? b.querySelector("span").textContent : b.textContent.trim();
          b.innerHTML = (ativo ? CFG.iconeConfere : "") + "<span>" + rotulo + "</span>";
        }});
        document.querySelectorAll("[data-secao-categoria]").forEach((sec) => {{
          const mostrar = alvo === "__todas__" || sec.getAttribute("data-secao-categoria") === alvo;
          sec.hidden = !mostrar;
        }});
        const blocoDest = document.querySelector("[data-bloco-destaque]");
        if (blocoDest) blocoDest.hidden = alvo !== "__todas__";
      }});
    }});

    /* 2. Seleção obrigatória de variação + reação da placa de preço (150-250ms) */
    const escolhasAtuais = Object.create(null);

    document.querySelectorAll("[data-escolher-variacao]").forEach((pilula) => {{
      pilula.addEventListener("click", () => {{
        const itemId = pilula.getAttribute("data-escolher-variacao");
        const indice = Number(pilula.getAttribute("data-var-indice"));
        const precoFmt = pilula.getAttribute("data-var-preco-fmt");
        escolhasAtuais[itemId] = indice;

        const grupo = pilula.closest('[role="radiogroup"]');
        if (grupo) {{
          grupo.querySelectorAll("[data-escolher-variacao]").forEach((p) => {{
            const marcado = p === pilula;
            p.setAttribute("aria-checked", marcado ? "true" : "false");
            const txt = p.querySelector("span") ? p.querySelector("span").textContent : p.textContent.trim();
            p.innerHTML = (marcado ? CFG.iconeConfere : "") + "<span>" + txt + "</span>";
          }});
        }}

        const placa = document.querySelector('[data-placa-item="' + itemId + '"]');
        const placaTxt = document.querySelector('[data-placa-texto="' + itemId + '"]');
        if (placaTxt && precoFmt) {{
          placaTxt.textContent = precoFmt;
          if (placa) {{
            placa.classList.add("trocando");
            setTimeout(() => placa.classList.remove("trocando"), 180);
          }}
        }}

        const erroEl = document.getElementById("erro-item-" + itemId);
        if (erroEl) erroEl.hidden = true;
      }});
    }});

    /* 3. Estado da Comanda com persistência resiliente a falhas do armazenamento */
    function lerEstadoInicial() {{
      try {{
        const bruto = window.localStorage.getItem(CHAVE_STORAGE);
        if (!bruto) return {{ itens: [], obs: "" }};
        const obj = JSON.parse(bruto);
        if (!obj || !Array.isArray(obj.itens)) return {{ itens: [], obs: "" }};
        return {{
          itens: obj.itens.filter((x) => x && typeof x.chave === "string" && Number(x.qtd) > 0),
          obs: typeof obj.obs === "string" ? obj.obs : ""
        }};
      }} catch (_e) {{
        return {{ itens: [], obs: "" }};
      }}
    }}

    const estadoPedido = lerEstadoInicial();

    function salvarEstado() {{
      try {{
        window.localStorage.setItem(CHAVE_STORAGE, JSON.stringify(estadoPedido));
      }} catch (_e) {{
        /* Falha silenciosa se armazenamento privado/cheio */
      }}
    }}

    function montarMensagemPedido() {{
      if (!estadoPedido.itens.length) return "";
      const linhas = ["Olá! Gostaria de fazer um pedido na " + CFG.nomeNegocio + ":"];
      let total = 0;
      for (const linha of estadoPedido.itens) {{
        const sub = linha.preco * linha.qtd;
        total += sub;
        const comp = linha.variacao ? " (" + linha.variacao + ")" : "";
        linhas.push("• " + linha.qtd + "x " + linha.nome + comp + " — " + formatarBRL(sub));
      }}
      linhas.push("Total estimado: " + formatarBRL(total));
      if (estadoPedido.obs && estadoPedido.obs.trim()) {{
        linhas.push("Observação: " + estadoPedido.obs.trim());
      }}
      return linhas.join("\\n");
    }}

    function renderizarComandas() {{
      if (!CFG.usaComanda) return;
      const totalQtd = estadoPedido.itens.reduce((acc, x) => acc + x.qtd, 0);
      const totalValor = estadoPedido.itens.reduce((acc, x) => acc + x.preco * x.qtd, 0);
      const msgPronta = montarMensagemPedido();

      document.querySelectorAll("[data-comanda-instancia]").forEach((inst) => {{
        const resumoQtd = inst.querySelector("[data-comanda-resumo-qtd]");
        const btnLimpar = inst.querySelector("[data-limpar-pedido]");
        const blocoVazio = inst.querySelector("[data-comanda-vazia]");
        const listaUl = inst.querySelector("[data-comanda-lista]");
        const rodape = inst.querySelector("[data-comanda-rodape]");
        const campoObs = inst.querySelector("[data-comanda-obs]");
        const spanTotal = inst.querySelector("[data-comanda-total]");
        const preMsg = inst.querySelector("[data-comanda-previa-msg]");

        if (resumoQtd) resumoQtd.textContent = totalQtd === 1 ? "1 item" : totalQtd + " itens";
        if (btnLimpar) btnLimpar.hidden = totalQtd === 0;
        if (blocoVazio) blocoVazio.hidden = totalQtd > 0;
        if (listaUl) listaUl.hidden = totalQtd === 0;
        if (rodape) rodape.hidden = totalQtd === 0;
        if (spanTotal) spanTotal.textContent = formatarBRL(totalValor);
        if (preMsg) preMsg.textContent = msgPronta;
        if (campoObs && document.activeElement !== campoObs && campoObs.value !== estadoPedido.obs) {{
          campoObs.value = estadoPedido.obs;
        }}

        if (listaUl) {{
          listaUl.innerHTML = estadoPedido.itens.map((it) => {{
            const rotVar = it.variacao ? " (" + it.variacao + ")" : "";
            const sub = formatarBRL(it.preco * it.qtd);
            return (
              '<li data-linha-chave="' + it.chave + '">' +
                '<div class="comanda-item-topo">' +
                  '<span class="comanda-item-nome"></span>' +
                  '<span class="comanda-pontilhado" aria-hidden="true"></span>' +
                  '<span class="preco-valor">' + sub + '</span>' +
                '</div>' +
                '<div class="comanda-controles">' +
                  '<div class="passo-qtd">' +
                    '<button type="button" class="botao-qtd" data-alterar-qtd="' + it.chave + '" data-delta="-1" aria-label="Diminuir quantidade">−</button>' +
                    '<span style="font-weight:700;min-width:20px;text-align:center;">' + it.qtd + '</span>' +
                    '<button type="button" class="botao-qtd" data-alterar-qtd="' + it.chave + '" data-delta="1" aria-label="Aumentar quantidade">+</button>' +
                  '</div>' +
                  '<button type="button" class="botao-qtd" data-remover-chave="' + it.chave + '">' + CFG.iconeLixeira + '<span>Remover</span></button>' +
                '</div>' +
              '</li>'
            );
          }}).join("");
          estadoPedido.itens.forEach((it) => {{
            const li = listaUl.querySelector('[data-linha-chave="' + it.chave + '"] .comanda-item-nome');
            if (li) li.textContent = it.qtd + "x " + it.nome + (it.variacao ? " (" + it.variacao + ")" : "");
          }});
        }}
      }});

      const barraMovel = document.getElementById("barra-pedido-movel");
      if (barraMovel) {{
        barraMovel.hidden = totalQtd === 0;
        const txtMovel = document.getElementById("barra-pedido-resumo");
        if (txtMovel) txtMovel.textContent = (totalQtd === 1 ? "1 item · " : totalQtd + " itens · ") + formatarBRL(totalValor);
      }}
    }}

    const timersConfirmacao = new WeakMap();

    document.querySelectorAll("[data-adicionar-item]").forEach((btn) => {{
      btn.addEventListener("click", () => {{
        const itemId = btn.getAttribute("data-adicionar-item");
        const meta = CFG.catalogo[itemId];
        if (!meta) return;

        let variacaoRotulo = "";
        let precoUnit = Number(meta.precoUnico || 0);

        if (meta.variacoes && meta.variacoes.length > 0) {{
          const idxEscolhido = escolhasAtuais[itemId];
          if (typeof idxEscolhido !== "number" || !meta.variacoes[idxEscolhido]) {{
            const erroEl = document.getElementById("erro-item-" + itemId);
            if (erroEl) erroEl.hidden = false;
            const primeiraPilula = document.querySelector('[data-escolher-variacao="' + itemId + '"]');
            if (primeiraPilula) primeiraPilula.focus();
            return;
          }}
          variacaoRotulo = meta.variacoes[idxEscolhido].rotulo;
          precoUnit = Number(meta.variacoes[idxEscolhido].preco);
        }}

        const chave = itemId + "::" + variacaoRotulo;
        const existente = estadoPedido.itens.find((x) => x.chave === chave);
        if (existente) {{
          existente.qtd += 1;
          existente.preco = precoUnit;
        }} else {{
          estadoPedido.itens.push({{
            chave: chave,
            itemId: itemId,
            nome: meta.nome,
            variacao: variacaoRotulo,
            preco: precoUnit,
            qtd: 1
          }});
        }}
        salvarEstado();
        renderizarComandas();

        /* Confirmação tátil em 180ms sem travar o botão */
        clearTimeout(timersConfirmacao.get(btn));
        btn.classList.remove("botao-adicionar");
        btn.classList.add("botao-adicionado");
        btn.innerHTML = CFG.iconeConfere + "<span>Adicionado ao pedido</span>";
        timersConfirmacao.set(btn, setTimeout(() => {{
          btn.classList.remove("botao-adicionado");
          btn.classList.add("botao-adicionar");
          btn.innerHTML = CFG.iconePedido + "<span>Adicionar</span>";
        }}, 1400));

        const barraMovel = document.getElementById("barra-pedido-movel");
        if (barraMovel && !barraMovel.hidden) {{
          barraMovel.classList.add("reagindo");
          setTimeout(() => barraMovel.classList.remove("reagindo"), 200);
        }}
      }});
    }});

    document.addEventListener("click", (ev) => {{
      const btnDelta = ev.target.closest("[data-alterar-qtd]");
      if (btnDelta) {{
        const chave = btnDelta.getAttribute("data-alterar-qtd");
        const delta = Number(btnDelta.getAttribute("data-delta"));
        const alvo = estadoPedido.itens.find((x) => x.chave === chave);
        if (alvo) {{
          alvo.qtd += delta;
          if (alvo.qtd <= 0) {{
            estadoPedido.itens = estadoPedido.itens.filter((x) => x.chave !== chave);
          }}
          salvarEstado();
          renderizarComandas();
        }}
        return;
      }}
      const btnRem = ev.target.closest("[data-remover-chave]");
      if (btnRem) {{
        const chave = btnRem.getAttribute("data-remover-chave");
        estadoPedido.itens = estadoPedido.itens.filter((x) => x.chave !== chave);
        salvarEstado();
        renderizarComandas();
        return;
      }}
      const btnLimpar = ev.target.closest("[data-limpar-pedido]");
      if (btnLimpar) {{
        estadoPedido.itens = [];
        estadoPedido.obs = "";
        document.querySelectorAll("[data-comanda-obs]").forEach((c) => {{ c.value = ""; }});
        salvarEstado();
        renderizarComandas();
        return;
      }}
      const btnAbrirZap = ev.target.closest("[data-abrir-pedido-zap]");
      if (btnAbrirZap && !CFG.modoExemplo && CFG.whatsapp) {{
        const msg = montarMensagemPedido();
        if (msg) {{
          window.open("https://wa.me/" + CFG.whatsapp + "?text=" + encodeURIComponent(msg), "_blank", "noopener,noreferrer");
        }}
      }}
    }});

    document.querySelectorAll("[data-comanda-obs]").forEach((campo) => {{
      campo.addEventListener("input", () => {{
        estadoPedido.obs = campo.value;
        document.querySelectorAll("[data-comanda-obs]").forEach((outro) => {{
          if (outro !== campo) outro.value = campo.value;
        }});
        salvarEstado();
        const msg = montarMensagemPedido();
        document.querySelectorAll("[data-comanda-previa-msg]").forEach((pre) => {{ pre.textContent = msg; }});
      }});
    }});

    /* Gaveta modal da comanda no celular (<dialog closedby="any"> + fallback Safari) */
    const gaveta = document.getElementById("gaveta-comanda");
    const btnVerPedido = document.getElementById("btn-ver-meu-pedido");
    const btnFecharGaveta = document.getElementById("btn-fechar-gaveta");
    if (gaveta && btnVerPedido) {{
      btnVerPedido.addEventListener("click", () => gaveta.showModal());
      if (btnFecharGaveta) btnFecharGaveta.addEventListener("click", () => gaveta.close());
      if (!("closedBy" in HTMLDialogElement.prototype)) {{
        gaveta.addEventListener("click", (event) => {{
          if (event.target !== gaveta) return;
          const r = gaveta.getBoundingClientRect();
          const dentro = r.top <= event.clientY && event.clientY <= r.top + r.height && r.left <= event.clientX && event.clientX <= r.left + r.width;
          if (!dentro) gaveta.close();
        }});
      }}
    }}

    renderizarComandas();

    /* 4. Copiar chave Pix com Invoker Commands + fallback + tratamento de erro */
    let ultimaMsgStatus = "";
    const timersCopia = new WeakMap();
    async function executarCopiaPix(botao, alvo) {{
      if (!botao || !alvo) return;
      const texto = alvo.innerText.trim();
      const bolha = document.getElementById("status-copia-pix");
      const erroPix = document.getElementById("erro-copia-pix");
      clearTimeout(timersCopia.get(botao));
      try {{
        await navigator.clipboard.writeText(texto);
        if (erroPix) erroPix.hidden = true;
        if (bolha) {{
          let msg = "Chave Pix copiada";
          if (msg === ultimaMsgStatus) msg += "\\u00A0";
          ultimaMsgStatus = msg;
          bolha.textContent = msg;
          bolha.classList.add("visivel");
        }}
        timersCopia.set(botao, setTimeout(() => {{
          if (bolha) {{
            bolha.classList.remove("visivel");
            bolha.textContent = "";
          }}
        }}, 2500));
      }} catch (_err) {{
        if (bolha) {{
          bolha.classList.remove("visivel");
          bolha.textContent = "";
        }}
        if (erroPix) erroPix.hidden = false;
      }}
    }}

    document.addEventListener("command", (ev) => {{
      if (ev.command && ev.command.startsWith("--copy")) {{
        executarCopiaPix(ev.source, ev.target);
      }}
    }}, true);

    if (!("CommandEvent" in window)) {{
      document.addEventListener("click", (ev) => {{
        if (ev.defaultPrevented) return;
        const btn = ev.target.closest('button[command^="--copy"]');
        if (!btn) return;
        const alvo = document.getElementById(btn.getAttribute("commandfor"));
        if (alvo) executarCopiaPix(btn, alvo);
      }});
    }}

    /* 5. Formulário de Encomendas com prévia ao vivo em balão e validação de data >= hoje */
    const formEnc = document.getElementById("form-encomendas");
    const balaoEnc = document.getElementById("balao-previa-encomenda");
    if (formEnc && balaoEnc) {{
      const cData = document.getElementById("enc-data");
      const cHora = document.getElementById("enc-hora");
      const cPessoas = document.getElementById("enc-pessoas");
      const cNome = document.getElementById("enc-nome");
      const cPedido = document.getElementById("enc-pedido");
      const erroData = document.getElementById("erro-enc-data");

      function hojeISO() {{
        const agora = new Date();
        const ano = agora.getFullYear();
        const mes = String(agora.getMonth() + 1).padStart(2, "0");
        const dia = String(agora.getDate()).padStart(2, "0");
        return ano + "-" + mes + "-" + dia;
      }}

      if (cData) cData.min = hojeISO();

      function formatarDataBR(iso) {{
        if (!iso || !/^\\d{{4}}-\\d{{2}}-\\d{{2}}$/.test(iso)) return "a combinar";
        const p = iso.split("-");
        return p[2] + "/" + p[1] + "/" + p[0];
      }}

      function montarTextoEncomenda() {{
        const receb = (formEnc.querySelector('input[name="recebimento"]:checked') || {{}}).value || "Retirada na barraca";
        return [
          "Olá! Gostaria de pedir orçamento para grupo na " + CFG.nomeNegocio + ":",
          "• Data: " + formatarDataBR(cData ? cData.value : "") + (cHora && cHora.value ? " às " + cHora.value : ""),
          "• Pessoas: " + (cPessoas && cPessoas.value.trim() ? cPessoas.value.trim() : "a informar"),
          "• Pedido: " + (cPedido && cPedido.value.trim() ? cPedido.value.trim() : "itens a combinar"),
          "• Recebimento: " + receb,
          "• Nome: " + (cNome && cNome.value.trim() ? cNome.value.trim() : "a informar")
        ].join("\\n");
      }}

      function atualizarBalao() {{
        balaoEnc.textContent = montarTextoEncomenda();
      }}

      function validarDataCampo() {{
        if (!cData) return true;
        const val = cData.value;
        const invalida = !val || val < hojeISO();
        cData.setAttribute("aria-invalid", invalida ? "true" : "false");
        if (erroData) erroData.hidden = !invalida;
        return !invalida;
      }}

      let dataEditada = false;
      if (cData) {{
        cData.addEventListener("blur", () => {{
          if (dataEditada && cData.value) validarDataCampo();
        }});
        cData.addEventListener("input", () => {{
          dataEditada = true;
          if (cData.value && cData.value >= hojeISO()) {{
            cData.setAttribute("aria-invalid", "false");
            if (erroData) erroData.hidden = true;
          }}
          atualizarBalao();
        }});
      }}

      formEnc.querySelectorAll("input, textarea").forEach((el) => {{
        if (el !== cData) el.addEventListener("input", atualizarBalao);
        if (el.type === "radio") el.addEventListener("change", atualizarBalao);
      }});

      formEnc.addEventListener("submit", (ev) => {{
        ev.preventDefault();
        if (!validarDataCampo()) {{
          cData.focus();
          return;
        }}
        const primeiroVazio = [cHora, cPessoas, cNome, cPedido].find((c) => c && !c.value.trim());
        if (primeiroVazio) {{
          primeiroVazio.setAttribute("aria-invalid", "true");
          primeiroVazio.focus();
          primeiroVazio.addEventListener("input", () => primeiroVazio.setAttribute("aria-invalid", "false"), {{ once: true }});
          return;
        }}
        const textoFinal = montarTextoEncomenda();
        atualizarBalao();
        if (CFG.modoExemplo || !CFG.whatsapp) {{
          const avisoDemo = document.getElementById("aviso-encomenda-demo");
          if (avisoDemo && CFG.msgDemoEncomenda) avisoDemo.textContent = CFG.msgDemoEncomenda;
          return;
        }}
        window.open("https://wa.me/" + CFG.whatsapp + "?text=" + encodeURIComponent(textoFinal), "_blank", "noopener,noreferrer");
      }});

      atualizarBalao();
    }}

    /* 6. Compartilhar página no rodapé */
    const btnComp = document.getElementById("btn-compartilhar");
    const statusComp = document.getElementById("status-compartilhar");
    if (btnComp) {{
      btnComp.addEventListener("click", async () => {{
        const urlAlvo = CFG.urlFinal || window.location.href;
        try {{
          if (navigator.share) {{
            await navigator.share({{ title: CFG.nomeNegocio, url: urlAlvo }});
            return;
          }}
          await navigator.clipboard.writeText(urlAlvo);
          if (statusComp) {{
            statusComp.textContent = "Link copiado";
            statusComp.classList.add("visivel");
            setTimeout(() => {{ statusComp.classList.remove("visivel"); statusComp.textContent = ""; }}, 2200);
          }}
        }} catch (_e) {{}}
      }});
    }}
  }})();
  </script>"""


def compilar_site_ambulante(
    pasta_ambulante: Path,
    out_dir: Path,
    project_root: Path,
    modo_producao: bool = False,
    fase_ate: int = 8,
) -> dict[str, Any]:
    """Compila `dados.json` + `fotos/` em um site estático completo, comprimindo fotos e validando regras."""
    dados, pasta_fotos = carregar_dados_ambulante(pasta_ambulante, modo_producao=modo_producao)
    out_dir.mkdir(parents=True, exist_ok=True)
    fonts_copied = copy_fonts_to(out_dir, project_root)
    fotos_meta = _preparar_fotos(dados, pasta_fotos, out_dir)

    modo_exemplo = bool(dados.get("modo_exemplo", False))
    whatsapp_limpo = "" if modo_exemplo else re.sub(r"\D", "", str(dados.get("whatsapp", "")))
    usa_comanda = bool(dados["segmento"] == "alimentacao" and dados.get("aceita_pedidos_do_dia"))

    arq_barraca = str((dados.get("fotos") or {}).get("barraca", "")).strip()
    preload_hero = (
        f'<link rel="preload" href="{fotos_meta[arq_barraca]["rel"]}" as="image" type="image/webp" fetchpriority="high">'
        if arq_barraca in fotos_meta
        else ""
    )

    faixa_demo_html = (
        '<div class="faixa-demo" role="status"><div class="conteiner">'
        '<span>Modelo demonstrativo: dados fictícios</span></div></div>'
        if modo_exemplo
        else ""
    )

    hero_html = _render_primeira_tela_hibrida(dados, fotos_meta)
    catalogo_html = _render_secao_catalogo(dados, fotos_meta, whatsapp_limpo)

    secoes_finais_html = ""
    rodape_html = ""
    if fase_ate >= 5:
        secoes_finais_html = (
            _render_secao_como_chegar(dados, fotos_meta)
            + _render_secao_encomendas(dados)
            + _render_secao_quem_atende(dados, fotos_meta)
        )
        rodape_html = _render_rodape(dados, whatsapp_limpo)

    barra_e_gaveta_html = ""
    if usa_comanda:
        barra_e_gaveta_html = f"""
  <div class="barra-pedido-movel" id="barra-pedido-movel" hidden>
    <div>
      <p style="font-size: 0.9375rem; font-weight: 700;" id="barra-pedido-resumo">0 itens · R$ 0,00</p>
    </div>
    <button type="button" class="botao botao-mata" id="btn-ver-meu-pedido">
      {ICONES_2PX["pedido"]}<span>Ver meu pedido</span>
    </button>
  </div>

  <dialog class="gaveta-comanda" id="gaveta-comanda" closedby="any" aria-labelledby="titulo-gaveta-pedido">
    <div class="gaveta-topo">
      <h2 id="titulo-gaveta-pedido" class="nome-item">Revisar comanda</h2>
      <button type="button" class="botao-limpar" id="btn-fechar-gaveta">
        {ICONE_FECHAR_2PX}<span>Fechar</span>
      </button>
    </div>
    <div class="gaveta-miolo">
      {_render_comanda_miolo("mobile", modo_exemplo)}
    </div>
  </dialog>"""

    html_final = f"""<!DOCTYPE html>
<html lang="pt-BR" data-segmento="{html.escape(dados['segmento'])}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(dados['nome_negocio'])} — Parque da Cidade</title>
  <meta name="description" content="{html.escape(str(dados.get('o_que_oferece', dados['nome_negocio'])))}">
  <link rel="preload" href="fonts/fraunces-600-800-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="fonts/atkinson-hyperlegible-400-latin.woff2" as="font" type="font/woff2" crossorigin>
  {preload_hero}
  <style>
{FONT_AND_TOKENS_CSS}
{SITE_TOLDO_CSS}
  </style>
</head>
<body>
  <a href="#cardapio" class="link-pular">Pular para o conteúdo principal</a>
  {faixa_demo_html}
  {hero_html}
  <main>
    {catalogo_html}
    {secoes_finais_html}
  </main>
  {rodape_html}
  {barra_e_gaveta_html}
  {_gerar_script_cliente(dados, whatsapp_limpo)}
</body>
</html>"""

    index_path = out_dir / "index.html"
    index_path.write_text(html_final, encoding="utf-8")
    html_kb = round(index_path.stat().st_size / 1024, 2)
    fotos_kb = round(sum(f["kb"] for f in fotos_meta.values()), 2)
    fontes_ptbr_kb = round(
        sum(kb for nome, kb in fonts_copied if nome.endswith("-latin.woff2")),
        2,
    )

    return {
        "index_path": str(index_path),
        "segmento": dados["segmento"],
        "html_kb": html_kb,
        "fontes_ptbr_kb": fontes_ptbr_kb,
        "fotos_kb": fotos_kb,
        "fotos_detalhe": fotos_meta,
        "primeira_carga_estimada_kb": round(html_kb + fontes_ptbr_kb + fotos_kb, 2),
    }

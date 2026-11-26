"""Folha de estilo completa do site do cliente no conceito 'Toldo Aberto' (Fases 4 a 8)."""

from __future__ import annotations

SITE_TOLDO_CSS = r"""
    html {
      scroll-behavior: smooth;
      scroll-padding-top: 84px;
    }
    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
    }

    /* Abertura única de até 600ms: o toldo se desenrola e revela a foto */
    @keyframes desenrolar-toldo {
      from { transform: scaleY(0.18); opacity: 0.45; }
      to   { transform: scaleY(1); opacity: 1; }
    }
    @keyframes revelar-abertura {
      from { opacity: 0; transform: translateY(-6px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @media (prefers-reduced-motion: no-preference) {
      .toldo-abertura {
        transform-origin: top center;
        animation: desenrolar-toldo 460ms cubic-bezier(0.22, 1, 0.36, 1) both;
      }
      .foto-revelada {
        animation: revelar-abertura 540ms cubic-bezier(0.22, 1, 0.36, 1) 80ms both;
      }
    }

    .link-pular {
      position: absolute;
      left: -9999px;
      top: var(--s-8);
      z-index: 100;
      background-color: var(--mata);
      color: #FFFFFF;
      padding: var(--s-12) var(--s-16);
      border-radius: var(--r-botao);
      font-weight: 700;
      text-decoration: none;
    }
    .link-pular:focus {
      left: var(--s-16);
    }

    /* Faixa enxuta obrigatória do modelo demonstrativo */
    .faixa-demo {
      background-color: var(--papel-2);
      border-bottom: 1px solid var(--linha);
      padding-block: var(--s-4);
      font-size: 0.9375rem;
      line-height: 1.3;
      font-weight: 700;
      color: var(--tinta);
    }

    .toldo-abertura {
      position: relative;
      z-index: 3;
      pointer-events: none;
    }

    /* Escala fluida combinando rem + vw para respeitar zoom de 200% */
    .letreiro-nome {
      font-size: clamp(2.75rem, 1.2rem + 6.8vw, 6rem);
      line-height: 0.95;
      font-weight: 760;
      letter-spacing: -0.02em;
    }
    .titulo-secao {
      font-size: clamp(1.875rem, 1.1rem + 3.2vw, 3.25rem);
      line-height: 1.05;
      font-weight: 700;
      letter-spacing: -0.015em;
    }

    .oferta-parque {
      font-size: 1.0625rem;
      line-height: 1.42;
      color: var(--tinta);
    }

    .metadados-barraca {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: var(--s-4);
      font-size: 0.9375rem;
      line-height: 1.38;
      color: var(--apoio);
    }
    .metadados-barraca li {
      display: flex;
      align-items: flex-start;
      gap: var(--s-8);
    }
    .metadados-barraca .icone {
      width: 18px;
      height: 18px;
      margin-top: 2px;
      color: var(--tinta);
    }
    .metadados-barraca strong {
      color: var(--tinta);
      font-weight: 700;
    }

    .acoes-primeira-tela {
      display: flex;
      flex-wrap: wrap;
      gap: var(--s-8);
      width: 100%;
    }
    .acoes-primeira-tela .botao {
      flex: 1 1 138px;
      padding: var(--s-12) var(--s-8);
      gap: 6px;
      white-space: nowrap;
    }
    @media (max-width: 349px) {
      .acoes-primeira-tela .botao {
        flex: 1 1 100%;
      }
    }
    @media (min-width: 640px) {
      .acoes-primeira-tela {
        width: auto;
        gap: var(--s-12);
      }
      .acoes-primeira-tela .botao {
        flex: 0 0 auto;
        padding: var(--s-12) var(--s-24);
        gap: var(--s-8);
      }
    }

    .link-encomendas {
      display: inline-flex;
      align-items: center;
      gap: var(--s-8);
      min-height: 48px;
      padding-block: var(--s-8);
      color: var(--tinta);
      font-size: 0.9375rem;
      font-weight: 700;
      text-decoration: underline;
      text-underline-offset: 4px;
      text-decoration-thickness: 1.5px;
    }
    .link-encomendas:hover {
      color: var(--acento);
    }

    .foto-enquadrada {
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: var(--foco-foto, center 24%);
    }

    /* =========================================================================
       PRIMEIRA TELA HÍBRIDA APROVADA (FASE 3):
       - Celular (< 960px): Opção B (letreiro grande + foto em janela / tabuleta)
       - Computador (>= 960px): Opção C (foto ampla + cartão sólido na base)
       ========================================================================= */
    .primeira-tela {
      background-color: var(--papel);
    }

    /* --- COM FOTO: Celular (< 960px) = Opção B --- */
    @media (max-width: 959px) {
      .hero-hibrido-palco {
        display: flex;
        flex-direction: column;
        gap: var(--s-8);
        padding-block: var(--s-8) var(--s-24);
      }
      .hero-hibrido-cartao {
        display: contents;
      }
      .hero-hibrido-cabeca {
        order: 1;
        padding-bottom: var(--s-8);
        border-bottom: 1px solid var(--linha);
      }
      .hero-hibrido-cabeca .oferta-parque {
        margin-top: var(--s-4);
      }
      .hero-hibrido-midia {
        order: 2;
        padding: var(--s-8);
        background-color: var(--papel-2);
        border: 2px solid var(--tinta);
        border-radius: var(--r-foto);
      }
      .hero-hibrido-midia-miolo {
        width: 100%;
        aspect-ratio: 4 / 3;
        max-height: clamp(112px, calc(100svh - 428px), 32svh);
        border-radius: 12px;
        overflow: hidden;
      }
      .hero-hibrido-rodape {
        order: 3;
        display: flex;
        flex-direction: column;
        gap: var(--s-8);
      }
      .hero-acoes-empilhadas {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: var(--s-4);
      }
    }

    /* --- COM FOTO: Computador (>= 960px) = Opção C --- */
    @media (min-width: 960px) {
      .toldo-desktop-alto svg {
        height: 64px;
      }
      .hero-hibrido-palco {
        display: grid;
        grid-template-columns: repeat(12, minmax(0, 1fr));
        align-items: center;
        padding-block: var(--s-32) var(--s-64);
      }
      .hero-hibrido-midia {
        grid-column: 6 / 13;
        grid-row: 1;
        border-radius: var(--r-foto);
        border: 1.5px solid var(--linha);
        overflow: hidden;
        background-color: var(--papel-2);
      }
      .hero-hibrido-midia-miolo {
        width: 100%;
        aspect-ratio: 5 / 4;
        max-height: 520px;
      }
      .hero-hibrido-cartao {
        grid-column: 1 / 7;
        grid-row: 1;
        position: relative;
        z-index: 2;
        margin-top: var(--s-32);
        background-color: var(--papel);
        border: 1.5px solid var(--linha);
        border-radius: var(--r-foto);
        padding: var(--s-32);
        display: flex;
        flex-direction: column;
        gap: var(--s-16);
      }
      .hero-hibrido-cabeca .oferta-parque {
        margin-top: var(--s-12);
      }
      .hero-hibrido-rodape {
        display: flex;
        flex-direction: column;
        gap: var(--s-16);
      }
      .hero-acoes-empilhadas {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: var(--s-8);
      }
      .metadados-barraca {
        gap: var(--s-8);
        font-size: 1.0625rem;
      }
    }

    /* --- SEM FOTO: Celular (< 960px) = Tabuleta B | Computador (>= 960px) = Painel C --- */
    @media (max-width: 959px) {
      .semfoto-envoltorio {
        padding-block: var(--s-8) var(--s-24);
      }
      .semfoto-painel-acento {
        background-color: var(--acento);
        color: #FFFFFF;
        border-radius: var(--r-foto);
        padding: var(--s-8);
        margin-inline: var(--s-16);
      }
      .semfoto-painel-miolo {
        border: 1.5px solid rgba(255, 249, 240, 0.75);
        border-radius: 14px;
        padding: var(--s-16);
      }
      .semfoto-painel-miolo .oferta-parque {
        color: var(--papel);
        margin-top: var(--s-8);
      }
      .semfoto-cartao-base {
        padding: var(--s-16) var(--s-16) 0;
        display: flex;
        flex-direction: column;
        gap: var(--s-12);
      }
      .semfoto-cartao-base .oferta-desktop-only {
        display: none;
      }
    }

    @media (min-width: 960px) {
      .semfoto-envoltorio {
        padding-bottom: var(--s-64);
      }
      .semfoto-painel-acento {
        background-color: var(--acento);
        color: #FFFFFF;
        border-top: 2px solid var(--tinta);
        padding-block: var(--s-48) var(--s-64);
      }
      .semfoto-painel-miolo {
        max-width: 1200px;
        margin-inline: auto;
        padding-inline: var(--s-32);
      }
      .semfoto-painel-miolo .oferta-mobile-only {
        display: none;
      }
      .semfoto-cartao-base {
        max-width: calc(1200px - 64px);
        margin-inline: auto;
        margin-top: -32px;
        position: relative;
        z-index: 2;
        background-color: var(--papel);
        border: 1.5px solid var(--linha);
        border-radius: var(--r-foto);
        padding: var(--s-32);
        display: grid;
        grid-template-columns: repeat(12, minmax(0, 1fr));
        gap: var(--s-24);
        align-items: center;
      }
      .semfoto-info-esq {
        grid-column: 1 / 7;
        display: flex;
        flex-direction: column;
        gap: var(--s-12);
      }
      .semfoto-cartao-base .hero-acoes-empilhadas {
        grid-column: 7 / 13;
        justify-self: end;
      }
    }

    /* =========================================================================
       SEÇÃO A — CARDÁPIO / CATÁLOGO, FILTROS FIXOS, PLACA DE PREÇO E COMANDA
       ========================================================================= */
    .secao-catalogo {
      background-color: var(--papel-2);
      border-top: 1.5px solid var(--linha);
      padding-block: var(--s-32) var(--s-48);
      /* Impede oscilação de scroll anchoring ao colar a barra de filtros */
      overflow-anchor: none;
    }
    @media (min-width: 960px) {
      .secao-catalogo {
        padding-block: var(--s-96);
      }
    }

    .cabecalho-secao {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
      justify-content: space-between;
      gap: var(--s-16);
      margin-bottom: var(--s-24);
    }

    /* Barra de filtros fixa no topo ao rolar com máscara de continuidade horizontal */
    @property --fade-start {
      syntax: "<length>";
      inherits: false;
      initial-value: 0px;
    }
    @property --fade-end {
      syntax: "<length>";
      inherits: false;
      initial-value: 0px;
    }

    .barra-filtros-envoltorio {
      position: sticky;
      top: 0;
      z-index: 20;
      background-color: var(--papel-2);
      border-block: 1.5px solid var(--linha);
      margin-bottom: var(--s-32);
      container-type: scroll-state;
      container-name: filtros-topo;
    }
    @container filtros-topo scroll-state(stuck: top) {
      .barra-filtros-interna {
        background-color: var(--papel);
      }
    }
    .barra-filtros-envoltorio.is-stuck .barra-filtros-interna {
      background-color: var(--papel);
    }

    .barra-filtros-interna {
      padding-block: var(--s-8);
      transition: background-color 180ms ease-out;
    }

    .trilho-filtros {
      display: flex;
      align-items: center;
      gap: var(--s-8);
      overflow-x: auto;
      scrollbar-width: thin;
      scroll-padding-inline: 2.5rem;
      --fade-size: 2.5rem;
      mask:
        linear-gradient(black, black) no-clip subtract,
        linear-gradient(to right, black, transparent) 0 0 / var(--fade-start) 100% no-repeat no-clip,
        linear-gradient(to right, transparent, black) 100% 0 / var(--fade-end) 100% no-repeat no-clip;
      animation: revelar-fade-esq linear both, esconder-fade-dir linear both;
      animation-timeline: scroll(self inline);
      animation-range: 0 var(--fade-size), calc(100% - var(--fade-size)) 100%;
    }
    .trilho-filtros.more-start { --fade-start: var(--fade-size); }
    .trilho-filtros.more-end   { --fade-end: var(--fade-size); }
    @keyframes revelar-fade-esq { to { --fade-start: var(--fade-size); } }
    @keyframes esconder-fade-dir { from { --fade-end: var(--fade-size); } }

    .trilho-filtros .pilula-variacao {
      flex-shrink: 0;
    }

    /* Layout de computador do Cardápio: 2 colunas de itens + Comanda fixa ao lado */
    .palco-cardapio-comanda {
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--s-32);
      align-items: start;
    }
    @media (min-width: 1024px) {
      .palco-cardapio-comanda--com-comanda {
        grid-template-columns: repeat(12, minmax(0, 1fr));
        gap: var(--s-32);
      }
      .palco-cardapio-comanda--com-comanda .coluna-itens-cardapio {
        grid-column: 1 / 9;
      }
      .palco-cardapio-comanda--com-comanda .coluna-comanda-fixa {
        grid-column: 9 / 13;
        position: sticky;
        top: 88px;
      }
    }

    @media (max-width: 1023px) {
      .coluna-comanda-fixa {
        display: none;
      }
    }

    /* Destaque da casa (opcional, apenas se escolhido no dados.json) */
    .bloco-destaque-casa {
      background-color: var(--papel);
      border: 2px solid var(--tinta);
      border-radius: var(--r-foto);
      overflow: hidden;
      margin-bottom: var(--s-32);
    }
    .destaque-foto-envoltorio {
      width: 100%;
      aspect-ratio: 16 / 10;
      max-height: 320px;
      border-radius: 0 0 var(--r-foto) var(--r-foto);
      overflow: hidden;
      border-bottom: 1.5px solid var(--linha);
      background-color: var(--papel-2);
    }
    .destaque-miolo {
      padding: var(--s-24);
      display: flex;
      flex-direction: column;
      gap: var(--s-16);
    }
    .selo-destaque-casa {
      display: inline-flex;
      align-items: center;
      align-self: flex-start;
      gap: var(--s-8);
      padding: var(--s-4) var(--s-12);
      border-radius: var(--r-pilula);
      background-color: var(--papel-2);
      border: 1.5px solid var(--tinta);
      font-size: 0.9375rem;
      font-weight: 700;
      color: var(--tinta);
    }
    .destaque-cabeca {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      justify-content: space-between;
      gap: var(--s-12);
    }
    .destaque-titulo {
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-optical-sizing: auto;
      font-variation-settings: "SOFT" 45;
      font-size: clamp(1.5rem, 3vw, 2rem);
      line-height: 1.1;
      font-weight: 700;
    }

    /* Grade de linhas de itens em alimentação: 1 coluna no celular, 2 colunas no computador */
    .grupo-categoria-bloco {
      margin-bottom: var(--s-32);
    }
    .grupo-categoria-bloco:last-child {
      margin-bottom: 0;
    }
    .titulo-categoria {
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-optical-sizing: auto;
      font-variation-settings: "SOFT" 45;
      font-size: 1.5rem;
      line-height: 1.15;
      font-weight: 700;
      padding-bottom: var(--s-8);
      border-bottom: 2px solid var(--tinta);
      margin-bottom: var(--s-16);
    }

    .grade-linhas-cardapio {
      display: grid;
      grid-template-columns: 1fr;
      gap: 0;
    }
    @media (min-width: 960px) {
      .grade-linhas-cardapio {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        column-gap: var(--s-32);
      }
    }

    /* Linha aberta de item (sem cartão sombreado repetido) */
    .linha-item {
      padding-block: var(--s-24);
      border-bottom: 1.5px solid var(--linha);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: var(--s-16);
    }
    .linha-item-topo {
      display: flex;
      align-items: flex-start;
      gap: var(--s-16);
    }
    .miniatura-1x1 {
      width: 88px;
      height: 88px;
      flex-shrink: 0;
      aspect-ratio: 1 / 1;
      border-radius: 12px 12px var(--r-foto) var(--r-foto);
      overflow: hidden;
      border: 1.5px solid var(--linha);
      background-color: var(--papel);
    }
    @media (min-width: 640px) {
      .miniatura-1x1 {
        width: 96px;
        height: 96px;
      }
    }
    .linha-item-textos {
      flex: 1 1 auto;
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: var(--s-8);
    }

    /* Composição tipográfica quando o item não tem foto (sem imagem substituta e sem linha pontilhada órfã) */
    .linha-item--tipografica .cabeca-tipografica {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: var(--s-12);
      flex-wrap: wrap;
    }
    .placa-preco {
      max-width: 100%;
    }
    .comanda-item-topo .preco-valor {
      white-space: nowrap;
      flex-shrink: 0;
    }

    .linha-item-cabeca-foto {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      justify-content: space-between;
      gap: var(--s-8);
    }

    .rodape-acao-item {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: var(--s-12);
    }

    /* --- VARIAÇÕES DE CATÁLOGO POR SEGMENTO (SEÇÃO 7) --- */
    /* Brinquedos: grade de duas colunas com foto (ou composição tipográfica), preço e idade indicada */
    .grade-brinquedos {
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--s-24);
    }
    @media (min-width: 350px) {
      .grade-brinquedos {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: var(--s-16);
      }
    }
    @media (min-width: 960px) {
      .grade-brinquedos {
        gap: var(--s-32);
      }
    }
    .item-brinquedo {
      background-color: var(--papel);
      border: 1.5px solid var(--linha);
      border-radius: var(--r-foto);
      padding: var(--s-12);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: var(--s-12);
    }
    @media (min-width: 640px) {
      .item-brinquedo {
        padding: var(--s-24);
      }
    }
    .item-brinquedo .botao {
      width: 100%;
      padding: var(--s-8);
      font-size: 0.9375rem;
      line-height: 1.25;
      white-space: normal;
      text-align: center;
    }
    .etiqueta-idade {
      display: inline-flex;
      align-items: center;
      align-self: flex-start;
      padding: var(--s-4) var(--s-8);
      border-radius: 8px;
      background-color: var(--papel-2);
      border: 1px solid var(--linha);
      font-size: 0.9375rem;
      line-height: 1.3;
      font-weight: 700;
      color: var(--tinta);
    }
    .selo-tipografico-brinquedo {
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-size: 0.9375rem;
      font-weight: 700;
      color: var(--acento);
    }

    /* Infláveis: um bloco grande por brinquedo com tempo, preço, idade, altura e regras */
    .lista-inflaveis {
      display: flex;
      flex-direction: column;
      gap: var(--s-32);
    }
    .bloco-inflavel {
      background-color: var(--papel);
      border: 2px solid var(--tinta);
      border-radius: var(--r-foto);
      padding: var(--s-24);
      display: flex;
      flex-direction: column;
      gap: var(--s-16);
    }
    @media (min-width: 960px) {
      .bloco-inflavel {
        padding: var(--s-32);
      }
    }
    .ficha-tecnica-inflavel {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: var(--s-12);
      padding-block: var(--s-16);
      border-block: 1.5px solid var(--linha);
    }
    .ficha-dado dt {
      font-size: 0.9375rem;
      color: var(--apoio);
    }
    .ficha-dado dd {
      font-size: 1.0625rem;
      font-weight: 700;
      color: var(--tinta);
      margin-top: 2px;
    }
    .regras-inflavel {
      padding-left: var(--s-24);
      display: flex;
      flex-direction: column;
      gap: var(--s-8);
    }

    /* Bicicletas: tabela responsiva de tipo por tempo + documento, caução e devolução */
    .tabela-envoltorio {
      overflow-x: auto;
      max-inline-size: 100%;
      container-type: inline-size;
      background-color: var(--papel);
      border: 2px solid var(--tinta);
      border-radius: var(--r-foto);
      margin-bottom: var(--s-32);
    }
    .tabela-bikes {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      text-align: left;
    }
    .tabela-bikes caption {
      text-align: left;
      padding: var(--s-16) var(--s-24);
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-size: 1.375rem;
      font-weight: 700;
      border-bottom: 2px solid var(--tinta);
      background-color: var(--papel-2);
    }
    .tabela-bikes th,
    .tabela-bikes td {
      padding: var(--s-16) var(--s-24);
      border-bottom: 1px solid var(--linha);
      vertical-align: top;
    }
    .tabela-bikes thead th {
      background-color: var(--papel-2);
      font-weight: 700;
      border-bottom: 1.5px solid var(--tinta);
    }
    .tabela-bikes tbody tr:last-child th,
    .tabela-bikes tbody tr:last-child td {
      border-bottom: none;
    }
    @container (width < 560px) {
      .tabela-bikes, .tabela-bikes thead, .tabela-bikes tbody, .tabela-bikes tr, .tabela-bikes th, .tabela-bikes td {
        display: block;
      }
      .tabela-bikes caption {
        display: block;
      }
      .tabela-bikes thead {
        display: none;
      }
      .tabela-bikes tbody tr {
        border-bottom: 2px solid var(--tinta);
        padding: var(--s-16);
      }
      .tabela-bikes tbody tr:last-child {
        border-bottom: none;
      }
      .tabela-bikes tbody th,
      .tabela-bikes tbody td {
        padding: var(--s-4) 0;
        border-bottom: none;
      }
      .tabela-bikes tbody td[data-tempo-rotulo]::before {
        content: attr(data-tempo-rotulo) ": ";
        font-weight: 400;
        color: var(--apoio);
      }
    }

    .grade-regras-bikes {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: var(--s-16);
      margin-bottom: var(--s-24);
    }
    .bloco-regra-bike {
      background-color: var(--papel);
      border-left: 4px solid var(--acento);
      border-top: 1px solid var(--linha);
      border-right: 1px solid var(--linha);
      border-bottom: 1px solid var(--linha);
      border-radius: 0 var(--r-botao) var(--r-botao) 0;
      padding: var(--s-16);
    }
    .bloco-regra-bike h3 {
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-size: 1.25rem;
      margin-bottom: var(--s-8);
    }

    /* =========================================================================
       BARRA FLUTUANTE DO PEDIDO E GAVETA MODAL (<dialog closedby="any">)
       ========================================================================= */
    .barra-pedido-movel {
      position: fixed;
      inset-inline: var(--s-12);
      bottom: var(--s-12);
      z-index: 40;
      background-color: var(--papel);
      border: 2px solid var(--tinta);
      border-radius: var(--r-foto);
      padding: var(--s-8) var(--s-12);
      /* ÚNICA sombra de repouso na página: só no que flutua */
      box-shadow: var(--sombra-flutuante);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: var(--s-8);
      transition: transform 200ms ease-out;
    }
    .barra-pedido-movel .botao {
      white-space: nowrap;
      padding-inline: var(--s-16);
      flex-shrink: 0;
    }
    .barra-pedido-movel.reagindo {
      transform: translateY(-4px);
    }
    @media (min-width: 1024px) {
      .barra-pedido-movel {
        display: none !important;
      }
    }

    dialog.gaveta-comanda {
      margin: auto 0 0 0;
      width: 100%;
      max-width: 100%;
      max-height: 88svh;
      border: none;
      border-top: 2px solid var(--tinta);
      border-radius: var(--r-foto) var(--r-foto) 0 0;
      background-color: var(--papel);
      color: var(--tinta);
      padding: 0;
      box-shadow: var(--sombra-flutuante);
      overscroll-behavior: contain;
    }
    dialog.gaveta-comanda::backdrop {
      background-color: rgba(36, 23, 15, 0.58);
      overflow: hidden;
      overscroll-behavior: contain;
    }
    @media (prefers-reduced-motion: no-preference) {
      dialog.gaveta-comanda[open] {
        animation: subir-comanda 210ms cubic-bezier(0.22, 1, 0.36, 1) both;
      }
    }
    @keyframes subir-comanda {
      from { transform: translateY(28px); opacity: 0.7; }
      to   { transform: translateY(0); opacity: 1; }
    }
    .gaveta-topo {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: var(--s-12);
      padding: var(--s-16);
      border-bottom: 1.5px solid var(--linha);
      position: sticky;
      top: 0;
      background-color: var(--papel);
      z-index: 2;
    }
    .gaveta-miolo {
      padding: var(--s-16);
    }

    .comanda-acoes-topo {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: var(--s-8);
      padding-bottom: var(--s-12);
      border-bottom: 1.5px solid var(--linha);
      margin-bottom: var(--s-16);
    }
    .botao-limpar {
      display: inline-flex;
      align-items: center;
      gap: var(--s-4);
      min-height: 48px;
      padding-inline: var(--s-12);
      background: transparent;
      border: 1.5px solid var(--linha);
      border-radius: var(--r-botao);
      color: var(--tinta);
      font-family: inherit;
      font-size: 0.9375rem;
      font-weight: 700;
      cursor: pointer;
    }
    .botao-limpar:hover {
      border-color: var(--erro);
      color: var(--erro);
    }

    .previa-texto-pedido {
      margin-top: var(--s-12);
      padding-top: var(--s-12);
      border-top: 1px dashed var(--linha);
      font-size: 0.9375rem;
    }
    .previa-texto-pedido summary {
      cursor: pointer;
      font-weight: 700;
      min-height: 48px;
      display: flex;
      align-items: center;
    }
    .previa-texto-pedido pre {
      margin-top: var(--s-8);
      padding: var(--s-12);
      background-color: var(--papel);
      border: 1px solid var(--linha);
      border-radius: var(--r-botao);
      white-space: pre-wrap;
      font-family: inherit;
      font-size: 0.9375rem;
      line-height: 1.45;
    }

    /* =========================================================================
       SEÇÃO B — COMO CHEGAR E COMO PAGAR (SOBRE --MATA-ESCURA)
       ========================================================================= */
    .secao-como-chegar {
      background-color: var(--mata-escura);
      color: var(--papel);
      padding-block: var(--s-48);
    }
    @media (min-width: 960px) {
      .secao-como-chegar {
        padding-block: var(--s-96);
      }
    }
    .referencia-destaque {
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-optical-sizing: auto;
      font-variation-settings: "SOFT" 45;
      font-size: clamp(1.5rem, 3.6vw, 2.35rem);
      line-height: 1.15;
      font-weight: 680;
      color: var(--papel);
      margin-top: var(--s-16);
    }
    .grade-chegar {
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--s-32);
      margin-top: var(--s-32);
      align-items: start;
    }
    @media (min-width: 960px) {
      .grade-chegar {
        grid-template-columns: repeat(12, minmax(0, 1fr));
        gap: var(--s-32);
      }
      .chegar-col-esq { grid-column: 1 / 8; }
      .chegar-col-dir { grid-column: 8 / 13; }
    }
    .foto-fachada {
      width: 100%;
      aspect-ratio: 4 / 3;
      border-radius: 12px 12px var(--r-foto) var(--r-foto);
      overflow: hidden;
      border: 1.5px solid rgba(255, 249, 240, 0.35);
    }
    .tabela-horarios {
      width: 100%;
      border-collapse: collapse;
      margin-block: var(--s-24);
    }
    .tabela-horarios th,
    .tabela-horarios td {
      padding: var(--s-12) 0;
      border-bottom: 1px solid rgba(255, 249, 240, 0.28);
      text-align: left;
      font-size: 1.0625rem;
    }
    .tabela-horarios th {
      font-weight: 700;
      color: var(--papel);
      padding-right: var(--s-16);
    }
    .tabela-horarios td {
      color: var(--papel-2);
      font-variant-numeric: tabular-nums;
    }

    .bloco-como-pagar {
      margin-top: var(--s-32);
      padding-top: var(--s-32);
      border-top: 1.5px solid rgba(255, 249, 240, 0.28);
    }
    .lista-pagamentos {
      display: flex;
      flex-wrap: wrap;
      gap: var(--s-8);
      list-style: none;
      margin-top: var(--s-16);
    }
    .item-pagamento {
      padding: var(--s-8) var(--s-16);
      border-radius: var(--r-pilula);
      border: 1.5px solid rgba(255, 249, 240, 0.45);
      color: var(--papel);
      font-weight: 700;
      font-size: 0.9375rem;
    }
    .caixa-pix {
      margin-top: var(--s-24);
      padding: var(--s-24);
      border-radius: var(--r-foto);
      border: 1.5px solid rgba(255, 249, 240, 0.4);
      background-color: rgba(255, 249, 240, 0.06);
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: var(--s-12);
    }
    .bolha-status-copia {
      min-height: 24px;
      font-size: 0.9375rem;
      font-weight: 700;
      color: var(--sol);
      opacity: 0;
      transition: opacity 180ms ease-out;
    }
    .bolha-status-copia.visivel {
      opacity: 1;
    }

    /* =========================================================================
       SEÇÃO C — ENCOMENDAS COM PRÉVIA AO VIVO EM BALÃO DE CONVERSA
       ========================================================================= */
    .secao-encomendas {
      background-color: var(--papel-2);
      padding-block: var(--s-48);
      border-bottom: 1.5px solid var(--linha);
    }
    @media (min-width: 960px) {
      .secao-encomendas {
        padding-block: var(--s-96);
      }
    }
    .grade-encomendas {
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--s-32);
      margin-top: var(--s-32);
      align-items: start;
    }
    @media (min-width: 960px) {
      .grade-encomendas {
        grid-template-columns: repeat(12, minmax(0, 1fr));
        gap: var(--s-32);
      }
      .form-encomendas { grid-column: 1 / 8; }
      .painel-previa-conversa {
        grid-column: 8 / 13;
        position: sticky;
        top: 96px;
      }
    }
    .form-encomendas {
      display: flex;
      flex-direction: column;
      gap: var(--s-24);
    }
    .linha-dupla-campos {
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--s-16);
    }
    @media (min-width: 560px) {
      .linha-dupla-campos {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }
    .grupo-campo {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: var(--s-8);
    }
    .grupo-campo label,
    .grupo-campo legend {
      font-weight: 700;
      color: var(--tinta);
      font-size: 1.0625rem;
    }
    fieldset.grupo-campo {
      border: none;
      padding: 0;
    }
    .opcoes-recebimento {
      display: flex;
      flex-wrap: wrap;
      gap: var(--s-12);
      margin-top: var(--s-4);
    }
    .opcao-radio {
      display: inline-flex;
      align-items: center;
      gap: var(--s-8);
      min-height: 48px;
      padding: var(--s-8) var(--s-16);
      border-radius: var(--r-botao);
      border: 1.5px solid var(--linha);
      background-color: var(--papel);
      cursor: pointer;
      font-weight: 700;
    }
    .opcao-radio input[type="radio"] {
      width: 20px;
      height: 20px;
      accent-color: var(--acento);
    }

    /* =========================================================================
       SEÇÃO D — QUEM ATENDE (RETRATO 4:5 + FRASE EM FRAUNCES DESLOCADA)
       ========================================================================= */
    .secao-quem-atende {
      background-color: var(--papel);
      padding-block: var(--s-48);
    }
    @media (min-width: 960px) {
      .secao-quem-atende {
        padding-block: var(--s-96);
      }
    }
    .grade-quem-atende {
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--s-32);
      align-items: start;
    }
    @media (min-width: 960px) {
      .grade-quem-atende {
        grid-template-columns: repeat(12, minmax(0, 1fr));
        gap: var(--s-32);
      }
      .quem-retrato-col {
        grid-column: 1 / 6;
      }
      .quem-frase-col {
        grid-column: 6 / 13;
        /* Composição deslocada no computador */
        padding-top: var(--s-64);
      }
    }
    .moldura-retrato-4x5 {
      width: 100%;
      max-width: 420px;
      aspect-ratio: 4 / 5;
      border-radius: 12px 12px var(--r-foto) var(--r-foto);
      overflow: hidden;
      border: 1.5px solid var(--linha);
      background-color: var(--papel-2);
    }
    .placa-nome-atendente {
      width: 100%;
      max-width: 420px;
      background-color: var(--papel-2);
      border: 2px solid var(--tinta);
      border-radius: var(--r-foto);
      padding: var(--s-32) var(--s-24);
    }
    .citacao-quem-atende {
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-optical-sizing: auto;
      font-variation-settings: "SOFT" 45;
      font-size: clamp(1.5rem, 3.2vw, 2.35rem);
      line-height: 1.22;
      font-weight: 640;
      color: var(--tinta);
    }

    /* =========================================================================
       SEÇÃO E — RODAPÉ (--MATA-ESCURA)
       ========================================================================= */
    .rodape-site {
      background-color: var(--mata-escura);
      color: var(--papel);
      border-top: 4px solid var(--acento);
      padding-block: var(--s-48) var(--s-96);
    }
    .rodape-acoes {
      display: flex;
      flex-wrap: wrap;
      gap: var(--s-12);
      padding-bottom: var(--s-32);
      border-bottom: 1px solid rgba(255, 249, 240, 0.25);
    }
    .rodape-creditos {
      margin-top: var(--s-32);
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--s-24);
    }
    @media (min-width: 960px) {
      .rodape-creditos {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: var(--s-48);
      }
    }
    .rodape-creditos h2 {
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-size: 1.25rem;
      margin-bottom: var(--s-8);
      color: var(--papel);
    }
    .rodape-creditos p {
      color: var(--papel-2);
      font-size: 0.9375rem;
      line-height: 1.55;
    }
"""

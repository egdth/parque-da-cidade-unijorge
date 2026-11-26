"""Sistema Visual 'Toldo Aberto' (Fase 2) — Tokens CSS, Tipografia WOFF2 local, Ícones 2px e Componentes de Assinatura."""

from __future__ import annotations

import html
from pathlib import Path
import shutil

ACCENTS: dict[str, dict[str, str]] = {
    "alimentacao": {
        "codigo": "#B4471F",
        "nome": "Alimentação",
        "padrao_toldo": "Listras largas com borda em ondas",
        "exemplo_barraca": "Barraca Exemplo — Pastel e Caldo",
        "exemplo_item": "Açaí na tigela",
        "tipo_variacao": "tamanho",
        "variacoes": [("300 ml", "R$ 14,00"), ("500 ml", "R$ 20,00")],
    },
    "brinquedos": {
        "codigo": "#A8325A",
        "nome": "Brinquedos e doces",
        "padrao_toldo": "Listras finas com borda em ondas",
        "exemplo_barraca": "Barraca Exemplo — Pipas e Bolhas",
        "exemplo_item": "Kit bolha de sabão gigante",
        "tipo_variacao": "opção",
        "variacoes": [("Com refil 250 ml", "R$ 15,00"), ("Com refil 500 ml", "R$ 18,00")],
    },
    "inflaveis": {
        "codigo": "#1D5A8F",
        "nome": "Infláveis",
        "padrao_toldo": "Ondas grandes de lona",
        "exemplo_barraca": "Barraca Exemplo — Pula-Pula",
        "exemplo_item": "Sessão no tobogã inflável",
        "tipo_variacao": "tempo",
        "variacoes": [("15 minutos", "R$ 15,00"), ("40 minutos livre", "R$ 30,00")],
    },
    "bicicletas": {
        "codigo": "#0F6666",
        "nome": "Bicicletas",
        "padrao_toldo": "Listras diagonais com borda em ondas",
        "exemplo_barraca": "Barraca Exemplo — Aluguel de Bikes",
        "exemplo_item": "Bicicleta passeio aro 26",
        "tipo_variacao": "tempo",
        "variacoes": [("30 minutos", "R$ 18,00"), ("1 hora", "R$ 30,00")],
    },
}

# Conjunto único de ícones vetoriais: traço uniforme de 2px, pontas arredondadas, sempre acompanhados de texto visível.
ICONES_2PX: dict[str, str] = {
    "whatsapp": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21"/><path d="M9 10a.5.5 0 0 0 1 0V9a.5.5 0 0 0-1 0v1a5 5 0 0 0 5 5h1a.5.5 0 0 0 0-1h-1a.5.5 0 0 0 0 1"/></svg>',
    "cardapio": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h10"/></svg>',
    "chegar": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-6-5.2-6-10a6 6 0 1 1 12 0c0 4.8-6 10-6 10z"/><circle cx="12" cy="11" r="2"/></svg>',
    "relogio": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "grupo": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "mais": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14"/><path d="M5 12h14"/></svg>',
    "menos": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/></svg>',
    "confere": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    "copiar": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
    "pedido": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3z"/><path d="M9 8h6"/><path d="M9 12h6"/></svg>',
    "lixeira": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/></svg>',
    "alerta": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>',
    "data": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="17" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/><path d="m9 15 2 2 4-4"/></svg>',
    "compartilhar": '<svg class="icone" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>',
    "carregando": '<svg class="icone icone-giro" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M21 12a9 9 0 1 1-6.2-8.56"/></svg>',
}


def copy_fonts_to(out_dir: Path, project_root: Path) -> list[tuple[str, float]]:
    """Copia os arquivos .woff2 auto-hospedados para out_dir/fonts e retorna lista (nome, kb)."""
    src_dir = project_root / "assets" / "fonts"
    dst_dir = out_dir / "fonts"
    dst_dir.mkdir(parents=True, exist_ok=True)
    copied: list[tuple[str, float]] = []
    for f in sorted(src_dir.glob("*.woff2")):
        target = dst_dir / f.name
        shutil.copyfile(f, target)
        copied.append((f.name, round(target.stat().st_size / 1024, 2)))
    return copied


def render_toldo_svg(segmento: str, altura_lona: int = 44) -> str:
    """Renderiza o Toldo 100% em SVG na cor --acento, casando listras e ondas sem desalinhamento."""
    seg = segmento if segmento in ACCENTS else "alimentacao"
    if seg == "alimentacao":
        # Listras largas (36px cada gomo -> ciclo 72px) casadas com ondas na base
        total_h = altura_lona + 17
        pid = f"toldo-alim-{altura_lona}"
        return (
            f'<svg class="toldo" width="100%" height="{total_h}" aria-hidden="true">'
            f'<defs><pattern id="{pid}" width="72" height="{total_h}" patternUnits="userSpaceOnUse">'
            f'<rect x="0" y="0" width="36" height="{altura_lona}" fill="var(--acento)"/>'
            f'<rect x="36" y="0" width="36" height="{altura_lona}" fill="var(--papel)"/>'
            f'<line x1="0" y1="0.75" x2="72" y2="0.75" stroke="var(--acento)" stroke-width="1.5"/>'
            f'<line x1="0" y1="{altura_lona}" x2="72" y2="{altura_lona}" stroke="var(--tinta)" stroke-opacity="0.18" stroke-width="1.5"/>'
            f'<path d="M0,{altura_lona} Q18,{altura_lona + 24} 36,{altura_lona} Z" fill="var(--acento)"/>'
            f'<path d="M36,{altura_lona} Q54,{altura_lona + 24} 72,{altura_lona} Z" fill="var(--papel)" stroke="var(--acento)" stroke-width="1.5"/>'
            f'</pattern></defs>'
            f'<rect width="100%" height="{total_h}" fill="url(#{pid})"/>'
            f'</svg>'
        )
    if seg == "brinquedos":
        # Listras finas (16px cada gomo -> ciclo 32px) casadas com ondas delicadas
        total_h = altura_lona + 13
        pid = f"toldo-brinq-{altura_lona}"
        return (
            f'<svg class="toldo" width="100%" height="{total_h}" aria-hidden="true">'
            f'<defs><pattern id="{pid}" width="32" height="{total_h}" patternUnits="userSpaceOnUse">'
            f'<rect x="0" y="0" width="16" height="{altura_lona}" fill="var(--acento)"/>'
            f'<rect x="16" y="0" width="16" height="{altura_lona}" fill="var(--papel)"/>'
            f'<line x1="0" y1="0.75" x2="32" y2="0.75" stroke="var(--acento)" stroke-width="1.5"/>'
            f'<line x1="0" y1="{altura_lona}" x2="32" y2="{altura_lona}" stroke="var(--tinta)" stroke-opacity="0.16" stroke-width="1.2"/>'
            f'<path d="M0,{altura_lona} Q8,{altura_lona + 18} 16,{altura_lona} Z" fill="var(--acento)"/>'
            f'<path d="M16,{altura_lona} Q24,{altura_lona + 18} 32,{altura_lona} Z" fill="var(--papel)" stroke="var(--acento)" stroke-width="1.3"/>'
            f'</pattern></defs>'
            f'<rect width="100%" height="{total_h}" fill="url(#{pid})"/>'
            f'</svg>'
        )
    if seg == "inflaveis":
        # Ondas grandes contínuas (ciclo de 88px sem corte na base)
        total_h = altura_lona + 24
        pid = f"toldo-infl-{altura_lona}"
        return (
            f'<svg class="toldo" width="100%" height="{total_h}" aria-hidden="true">'
            f'<defs><pattern id="{pid}" width="88" height="{total_h}" patternUnits="userSpaceOnUse">'
            f'<rect x="0" y="0" width="58" height="{altura_lona}" fill="var(--acento)"/>'
            f'<rect x="58" y="0" width="30" height="{altura_lona}" fill="var(--papel)"/>'
            f'<line x1="0" y1="0.75" x2="88" y2="0.75" stroke="var(--acento)" stroke-width="1.5"/>'
            f'<rect x="0" y="{altura_lona - 4}" width="88" height="4" fill="var(--acento)"/>'
            f'<path d="M0,{altura_lona} Q44,{altura_lona + 38} 88,{altura_lona} Z" fill="var(--acento)"/>'
            f'</pattern></defs>'
            f'<rect width="100%" height="{total_h}" fill="url(#{pid})"/>'
            f'</svg>'
        )
    # Bicicletas: listras diagonais + barra de arremate e onda curta firme
    total_h = altura_lona + 15
    pid_diag = f"toldo-bike-diag-{altura_lona}"
    pid_wave = f"toldo-bike-onda-{altura_lona}"
    return (
        f'<svg class="toldo" width="100%" height="{total_h}" aria-hidden="true">'
        f'<defs>'
        f'<pattern id="{pid_diag}" width="28" height="28" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">'
        f'<rect x="0" y="0" width="15" height="28" fill="var(--acento)"/>'
        f'<rect x="15" y="0" width="13" height="28" fill="var(--papel)"/>'
        f'</pattern>'
        f'<pattern id="{pid_wave}" width="40" height="15" y="{altura_lona}" patternUnits="userSpaceOnUse">'
        f'<path d="M0,0 Q20,22 40,0 Z" fill="var(--acento)"/>'
        f'</pattern>'
        f'</defs>'
        f'<rect x="0" y="0" width="100%" height="{altura_lona}" fill="url(#{pid_diag})"/>'
        f'<line x1="0" y1="0.75" x2="100%" y2="0.75" stroke="var(--acento)" stroke-width="1.5"/>'
        f'<rect x="0" y="{altura_lona - 3}" width="100%" height="3" fill="var(--acento)"/>'
        f'<rect x="0" y="{altura_lona}" width="100%" height="15" fill="url(#{pid_wave})"/>'
        f'</svg>'
    )


def render_serrilhado_svg(posicao: str = "topo") -> str:
    """Borda serrilhada física de bloco de comanda (topo ou base)."""
    pid = f"dente-{posicao}"
    pts = "0,10 8,0 16,10" if posicao == "topo" else "0,0 8,10 16,0"
    line_pts = "0,10 8,1 16,10" if posicao == "topo" else "0,0 8,9 16,0"
    return (
        f'<svg class="comanda-serrilha comanda-serrilha--{posicao}" width="100%" height="10" aria-hidden="true">'
        f'<defs><pattern id="{pid}" width="16" height="10" patternUnits="userSpaceOnUse">'
        f'<polygon points="{pts}" fill="var(--papel-2)"/>'
        f'<polyline points="{line_pts}" fill="none" stroke="var(--linha)" stroke-width="1.2"/>'
        f'</pattern></defs>'
        f'<rect width="100%" height="10" fill="url(#{pid})"/>'
        f'</svg>'
    )


FONT_AND_TOKENS_CSS = r"""
    @font-face {
      font-family: "Fraunces";
      font-style: normal;
      font-weight: 600 800;
      font-display: swap;
      src: url("fonts/fraunces-600-800-latin.woff2") format("woff2");
      unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
    }
    @font-face {
      font-family: "Fraunces";
      font-style: normal;
      font-weight: 600 800;
      font-display: swap;
      src: url("fonts/fraunces-600-800-latin-ext.woff2") format("woff2");
      unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
    }
    @font-face {
      font-family: "Fraunces Fallback";
      src: local("Georgia"), local("Times New Roman");
      size-adjust: 104%;
      ascent-override: 94%;
      descent-override: 24%;
    }
    @font-face {
      font-family: "Atkinson Hyperlegible";
      font-style: normal;
      font-weight: 400;
      font-display: swap;
      src: url("fonts/atkinson-hyperlegible-400-latin.woff2") format("woff2");
      unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
    }
    @font-face {
      font-family: "Atkinson Hyperlegible";
      font-style: normal;
      font-weight: 400;
      font-display: swap;
      src: url("fonts/atkinson-hyperlegible-400-latin-ext.woff2") format("woff2");
      unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
    }
    @font-face {
      font-family: "Atkinson Hyperlegible";
      font-style: normal;
      font-weight: 700;
      font-display: swap;
      src: url("fonts/atkinson-hyperlegible-700-latin.woff2") format("woff2");
      unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
    }
    @font-face {
      font-family: "Atkinson Hyperlegible";
      font-style: normal;
      font-weight: 700;
      font-display: swap;
      src: url("fonts/atkinson-hyperlegible-700-latin-ext.woff2") format("woff2");
      unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
    }

    :root {
      /* Paleta Toldo Aberto */
      --papel: #FFF9F0;
      --papel-2: #F6EBDA;
      --tinta: #24170F;
      --apoio: #5C4A3D;
      --mata: #1F5C3A;
      --mata-escura: #123524;
      --sol: #F2B63D;
      --linha: #8A7563;
      --erro: #A1261D;
      --acento: #B4471F;

      /* Escala de espaço: 4, 8, 12, 16, 24, 32, 48, 64 e 96 px */
      --s-4: 4px;
      --s-8: 8px;
      --s-12: 12px;
      --s-16: 16px;
      --s-24: 24px;
      --s-32: 32px;
      --s-48: 48px;
      --s-64: 64px;
      --s-96: 96px;

      /* Hierarquia de raios */
      --r-foto: 20px;
      --r-botao: 14px;
      --r-pilula: 999px;

      /* Sombra exclusiva para elementos que flutuam */
      --sombra-flutuante: 0 12px 28px rgba(36, 23, 15, 0.24), 0 2px 6px rgba(36, 23, 15, 0.14);
    }

    [data-segmento="alimentacao"] { --acento: #B4471F; }
    [data-segmento="brinquedos"]  { --acento: #A8325A; }
    [data-segmento="inflaveis"]   { --acento: #1D5A8F; }
    [data-segmento="bicicletas"]  { --acento: #0F6666; }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }
    html { color-scheme: light; scrollbar-gutter: stable; }

    body {
      font-family: "Atkinson Hyperlegible", system-ui, -apple-system, sans-serif;
      font-size-adjust: from-font;
      font-size: 1.0625rem;
      line-height: 1.55;
      background-color: var(--papel);
      color: var(--tinta);
      text-align: left;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }

    p, li, dd, .limite-leitura { max-width: 70ch; }

    /* Tipografia Fraunces variável com eixo óptico ativo e SOFT moderado */
    .letreiro-nome,
    .titulo-secao,
    .nome-item,
    .frase-retrato {
      font-family: "Fraunces", "Fraunces Fallback", Georgia, serif;
      font-optical-sizing: auto;
      font-variation-settings: "SOFT" 45;
      color: inherit;
    }

    .letreiro-nome {
      font-size: clamp(2.75rem, 13vw, 6rem);
      line-height: 0.95;
      font-weight: 760;
      letter-spacing: -0.02em;
    }

    .titulo-secao {
      font-size: clamp(1.875rem, 7vw, 3.25rem);
      line-height: 1.05;
      font-weight: 700;
      letter-spacing: -0.015em;
    }

    .nome-item {
      font-size: 1.375rem;
      line-height: 1.2;
      font-weight: 600;
    }

    .texto-apoio {
      font-size: 0.9375rem;
      line-height: 1.55;
      color: var(--apoio);
    }

    .preco-valor {
      font-size: 1.1875rem;
      font-weight: 700;
      line-height: 1.15;
      font-variant-numeric: tabular-nums;
    }

    .preco-destaque {
      font-size: 1.5rem;
      font-weight: 700;
      line-height: 1.15;
      font-variant-numeric: tabular-nums;
    }

    /* Estrutura de página: 16px mobile, 12 colunas e 1200px no computador */
    .conteiner {
      width: 100%;
      max-width: 1200px;
      margin-inline: auto;
      padding-inline: var(--s-16);
    }
    @media (min-width: 960px) {
      .conteiner { padding-inline: var(--s-32); }
    }

    .grade-12 {
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--s-32);
    }
    @media (min-width: 960px) {
      .grade-12 {
        grid-template-columns: repeat(12, minmax(0, 1fr));
        gap: var(--s-24);
      }
    }

    .secao-bloco {
      padding-block: var(--s-32);
    }
    @media (min-width: 960px) {
      .secao-bloco { padding-block: var(--s-96); }
    }
    .secao-alternada { background-color: var(--papel-2); }
    .secao-mata-escura {
      background-color: var(--mata-escura);
      color: var(--papel);
    }
    .secao-mata-escura .texto-apoio {
      color: var(--papel-2);
    }

    /* Foco visível de 3 px: --tinta no claro, --sol no escuro */
    :where(a, button, input, select, textarea, summary, [tabindex]):focus-visible {
      outline: 3px solid var(--tinta);
      outline-offset: 3px;
    }
    .secao-mata-escura :where(a, button, input, select, textarea, summary, [tabindex]):focus-visible,
    .fundo-escuro :where(a, button, input, select, textarea, summary, [tabindex]):focus-visible {
      outline: 3px solid var(--sol);
      outline-offset: 3px;
    }

    :where(button, a, input, select, textarea) {
      touch-action: manipulation;
      -webkit-tap-highlight-color: transparent;
    }

    /* Ícones sempre com traço 2px ao lado do texto */
    .icone {
      width: 20px;
      height: 20px;
      flex-shrink: 0;
    }
    @keyframes giro-curto {
      to { transform: rotate(360deg); }
    }
    .icone-giro {
      animation: giro-curto 0.9s linear infinite;
    }

    /* --- 1. ELEMENTO DE ASSINATURA: TOLDO --- */
    .toldo {
      display: block;
      width: 100%;
    }

    /* --- 2. ELEMENTO DE ASSINATURA: PLACA DE PREÇO (recorte + furo) --- */
    .placa-preco {
      display: inline-flex;
      align-items: center;
      gap: var(--s-8);
      min-height: 40px;
      padding: var(--s-8) var(--s-16) var(--s-8) var(--s-12);
      background-color: var(--acento);
      color: #FFFFFF;
      clip-path: polygon(10px 0, 100% 0, 100% 100%, 10px 100%, 0 calc(100% - 10px), 0 10px);
      transition: transform 180ms ease-out, background-color 180ms ease-out;
    }
    .placa-preco.trocando {
      transform: scale(1.05);
    }
    .placa-furo {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background-color: var(--papel);
      box-shadow: inset 0 0 0 1.5px rgba(36, 23, 15, 0.45);
      flex-shrink: 0;
    }
    .placa-preco--destaque {
      padding: var(--s-8) var(--s-24) var(--s-8) var(--s-16);
    }

    /* --- 3. ELEMENTO DE ASSINATURA: SELO PREÇOS CONFERIDOS --- */
    .selo-conferencia {
      display: inline-flex;
      align-items: center;
      gap: var(--s-8);
      padding: var(--s-8) var(--s-16);
      border-radius: var(--r-pilula);
      background-color: var(--sol);
      color: var(--tinta);
      border: 1.5px solid var(--tinta);
      font-size: 0.9375rem;
      font-weight: 700;
      line-height: 1.25;
    }

    /* --- 4. BOTÕES, PÍLULAS DE VARIAÇÃO E ESTADOS --- */
    .botao {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: var(--s-8);
      min-height: 48px;
      min-width: 48px;
      padding: var(--s-12) var(--s-24);
      border-radius: var(--r-botao);
      font-family: inherit;
      font-size: 1.0625rem;
      font-weight: 700;
      line-height: 1.2;
      text-decoration: none;
      cursor: pointer;
      border: 2px solid transparent;
      transition: background-color 160ms ease-out, border-color 160ms ease-out, color 160ms ease-out, transform 160ms ease-out;
    }
    .botao-mata {
      background-color: var(--mata);
      color: #FFFFFF;
      border-color: var(--mata);
    }
    .botao-mata:hover,
    .botao-mata.is-hover {
      background-color: var(--mata-escura);
      border-color: var(--mata-escura);
    }
    .botao-contorno {
      background-color: transparent;
      color: var(--tinta);
      border-color: var(--tinta);
    }
    .botao-contorno:hover,
    .botao-contorno.is-hover {
      background-color: var(--papel-2);
    }
    .botao-adicionar {
      background-color: transparent;
      color: var(--acento);
      border-color: var(--acento);
    }
    .botao-adicionar:hover,
    .botao-adicionar.is-hover {
      background-color: var(--acento);
      color: #FFFFFF;
    }
    .botao-adicionado {
      background-color: var(--mata);
      color: #FFFFFF;
      border-color: var(--mata);
    }
    .botao-claro-escuro {
      background-color: var(--papel);
      color: var(--mata-escura);
      border-color: var(--papel);
    }
    .botao-claro-escuro:hover {
      background-color: var(--sol);
      border-color: var(--sol);
      color: var(--tinta);
    }
    @media (prefers-reduced-motion: no-preference) {
      .botao:active,
      .botao.is-pressed {
        transform: translateY(2px);
      }
    }
    .botao[disabled],
    .botao[aria-disabled="true"] {
      background-color: var(--papel-2);
      color: var(--apoio);
      border: 2px dashed var(--linha);
      cursor: not-allowed;
      transform: none;
    }

    /* Pílulas de variação: seleção nunca depende só de cor (usa ícone de check + borda dupla/cheia) */
    .grupo-variacoes {
      display: flex;
      flex-wrap: wrap;
      gap: var(--s-8);
    }
    .pilula-variacao {
      display: inline-flex;
      align-items: center;
      gap: var(--s-8);
      min-height: 48px;
      padding: var(--s-8) var(--s-16);
      border-radius: var(--r-pilula);
      border: 1.5px solid var(--linha);
      background-color: var(--papel);
      color: var(--tinta);
      font-family: inherit;
      font-size: 0.9375rem;
      font-weight: 700;
      cursor: pointer;
      transition: background-color 160ms ease-out, border-color 160ms ease-out, color 160ms ease-out;
    }
    .pilula-variacao:hover {
      border-color: var(--tinta);
      background-color: var(--papel-2);
    }
    .pilula-variacao[aria-checked="true"],
    .pilula-variacao[aria-pressed="true"] {
      background-color: var(--acento);
      border-color: var(--acento);
      color: #FFFFFF;
    }
    .pilula-variacao .icone {
      width: 17px;
      height: 17px;
    }

    /* --- 5. ELEMENTO DE ASSINATURA: COMANDA (borda serrilhada + linha pontilhada) --- */
    .comanda-envoltorio {
      max-width: 480px;
    }
    .comanda-serrilha {
      display: block;
    }
    .comanda-corpo {
      background-color: var(--papel-2);
      border-inline: 1.2px solid var(--linha);
      padding: var(--s-24) var(--s-16);
    }
    @media (min-width: 640px) {
      .comanda-corpo { padding: var(--s-24); }
    }
    .comanda-cabecalho {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: var(--s-12);
      padding-bottom: var(--s-12);
      border-bottom: 1.5px solid var(--linha);
      margin-bottom: var(--s-16);
    }
    .comanda-lista {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: var(--s-16);
      margin-bottom: var(--s-24);
    }
    .comanda-item-topo {
      display: flex;
      align-items: baseline;
      gap: var(--s-8);
    }
    .comanda-item-nome {
      font-weight: 700;
      color: var(--tinta);
    }
    .comanda-pontilhado {
      flex: 1 1 24px;
      border-bottom: 2px dotted var(--linha);
      transform: translateY(-4px);
    }
    .comanda-controles {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: var(--s-8);
      margin-top: var(--s-8);
    }
    .passo-qtd {
      display: inline-flex;
      align-items: center;
      gap: var(--s-8);
    }
    .botao-qtd {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: var(--s-4);
      min-width: 48px;
      min-height: 48px;
      padding-inline: var(--s-12);
      border-radius: var(--r-botao);
      border: 1.5px solid var(--tinta);
      background-color: var(--papel);
      color: var(--tinta);
      font-family: inherit;
      font-size: 0.9375rem;
      font-weight: 700;
      cursor: pointer;
    }
    .comanda-total-bloco {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: var(--s-12);
      padding-top: var(--s-16);
      border-top: 2px solid var(--tinta);
      margin-bottom: var(--s-16);
    }
    .comanda-vazia {
      padding: var(--s-24) var(--s-16);
      border: 1.5px dashed var(--linha);
      border-radius: var(--r-botao);
      background-color: var(--papel);
      color: var(--apoio);
    }

    /* Mensagens de erro e aviso */
    .mensagem-erro {
      display: flex;
      align-items: flex-start;
      gap: var(--s-8);
      padding: var(--s-12) var(--s-16);
      border-radius: var(--r-botao);
      border: 1.5px solid var(--erro);
      background-color: #FDF2F2;
      color: var(--erro);
      font-size: 0.9375rem;
      font-weight: 700;
    }
    .campo-entrada {
      font-family: inherit;
      font-size: 1.0625rem;
      line-height: 1.4;
      color: var(--tinta);
      background-color: var(--papel);
      border: 1.5px solid var(--linha);
      border-radius: var(--r-botao);
      min-height: 48px;
      width: 100%;
      padding: var(--s-12) var(--s-16);
    }
    .campo-entrada[aria-invalid="true"] {
      border-color: var(--erro);
      border-width: 2px;
    }

    /* Balão de prévia de encomenda */
    .balao-conversa {
      position: relative;
      background-color: var(--papel);
      border: 1.5px solid var(--linha);
      border-radius: var(--r-foto) var(--r-foto) var(--r-foto) 4px;
      padding: var(--s-16) var(--s-24);
      color: var(--tinta);
      white-space: pre-line;
    }

    @media (forced-colors: active) {
      .toldo { border-bottom: 3px solid CanvasText; }
      .placa-preco { clip-path: none; border: 2px solid ButtonText; }
      .pilula-variacao[aria-checked="true"] { outline: 3px solid Highlight; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
      }
    }
"""

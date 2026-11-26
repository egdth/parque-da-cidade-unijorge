"""Passo único de build estático 'Toldo Aberto': lê `dados.json` + `fotos/`, comprime imagens, gera `index.html`, `placa-a5.html`, `qrcode.svg` e `equipe.html`."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .compilador_toldo import compilar_site_ambulante
from .dados_modelo import carregar_dados_ambulante
from .gerar_equipe_e_placa import gerar_pagina_equipe, gerar_placa_a5


def build_pacote_completo(
    pasta_ambulante: Path,
    out_dir: Path,
    project_root: Path,
    modo_producao: bool = False,
    incluir_equipe: bool = True,
) -> dict[str, object]:
    dados, _ = carregar_dados_ambulante(pasta_ambulante, modo_producao=modo_producao)
    site_info = compilar_site_ambulante(
        pasta_ambulante=pasta_ambulante,
        out_dir=out_dir,
        project_root=project_root,
        modo_producao=modo_producao,
        fase_ate=8,
    )
    placa_info = gerar_placa_a5(dados, out_dir=out_dir, project_root=project_root)
    equipe_path = gerar_pagina_equipe(out_dir=out_dir, project_root=project_root) if incluir_equipe else ""
    return {
        **site_info,
        **placa_info,
        "equipe_path": equipe_path,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Compilador estático Toldo Aberto — Parque Digital Unijorge")
    parser.add_argument("--entrada", required=True, help="Pasta do ambulante contendo dados.json e fotos/ (ou caminho direto para dados.json).")
    parser.add_argument("--saida", required=True, help="Pasta de saída do site estático gerado.")
    parser.add_argument("--producao", action="store_true", help="Ativa trava de produção (exige consentimento, WhatsApp E.164 válido e bloqueia dados de exemplo).")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    info = build_pacote_completo(
        pasta_ambulante=Path(args.entrada).resolve(),
        out_dir=Path(args.saida).resolve(),
        project_root=project_root,
        modo_producao=args.producao,
    )
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

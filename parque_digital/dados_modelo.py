"""Modelo canônico de dados (`dados.json` + pasta `fotos/`) e validador de build de produção."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

SEGMENTOS_VALIDOS = ("alimentacao", "brinquedos", "inflaveis", "bicicletas")

TELEFONES_EXEMPLO_BANIDOS = ("5571" + "98812" + "3456", "71" + "98812" + "3456")

RE_WHATSAPP_E164 = re.compile(r"^55\d{10,11}$")


def formatar_brl(valor: float | int) -> str:
    """Formata float em Real brasileiro (ex.: 14.5 -> 'R$ 14,50')."""
    inteiro, centavos = f"{float(valor):.2f}".split(".")
    inteiro_fmt = f"{int(inteiro):,}".replace(",", ".")
    return f"R$ {inteiro_fmt},{centavos}"


def validar_dados(dados: dict[str, Any], modo_producao: bool = False) -> list[str]:
    """Valida `dados.json`. Em `modo_producao=True`, falha sem consentimento, com WhatsApp inválido ou dado de exemplo."""
    erros: list[str] = []

    seg = str(dados.get("segmento", "")).strip()
    if seg not in SEGMENTOS_VALIDOS:
        erros.append(f"Segmento inválido '{seg}'. Use um de: {', '.join(SEGMENTOS_VALIDOS)}.")

    nome = str(dados.get("nome_negocio", "")).strip()
    if not nome:
        erros.append("Campo obrigatório ausente: 'nome_negocio'.")

    texto_serializado = json.dumps(dados, ensure_ascii=False)
    for banido in TELEFONES_EXEMPLO_BANIDOS:
        if banido in texto_serializado:
            erros.append(f"Número de exemplo proibido encontrado nos dados: {banido}.")

    modo_exemplo = bool(dados.get("modo_exemplo", False))

    if modo_producao:
        if modo_exemplo:
            erros.append("Build de produção rejeitado: 'modo_exemplo' está ativo.")
        if dados.get("consentimento") is not True:
            erros.append("Build de produção rejeitado: consentimento explícito ausente ('consentimento' != true).")
        if "barraca exemplo" in nome.lower() or "dados fictícios" in texto_serializado.lower():
            erros.append("Build de produção rejeitado: dados de exemplo detectados ('Barraca Exemplo' / 'dados fictícios').")
        zap = re.sub(r"\D", "", str(dados.get("whatsapp", "")))
        if not RE_WHATSAPP_E164.fullmatch(zap):
            erros.append(
                f"Build de produção rejeitado: WhatsApp mal formatado ('{dados.get('whatsapp', '')}'). Use DDI 55 + DDD + número (12 ou 13 dígitos)."
            )

    return erros


def carregar_dados_ambulante(pasta_ambulante: Path, modo_producao: bool = False) -> tuple[dict[str, Any], Path]:
    """Lê `dados.json` e localiza a pasta `fotos/` do ambulante, disparando ValueError se inválido."""
    arq_dados = pasta_ambulante / "dados.json" if pasta_ambulante.is_dir() else pasta_ambulante
    base_dir = arq_dados.parent
    dados = json.loads(arq_dados.read_text(encoding="utf-8"))
    erros = validar_dados(dados, modo_producao=modo_producao)
    if erros:
        raise ValueError("Falha na validação de dados.json:\n- " + "\n- ".join(erros))
    pasta_fotos = base_dir / "fotos"
    return dados, pasta_fotos

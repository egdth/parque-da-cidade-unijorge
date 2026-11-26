# Parque Digital Unijorge — Sistema "Toldo Aberto"

Gerador estático de páginas gratuitas, acessíveis sob sol forte (WCAG AA/AAA) e placas A5 com QR Code para vendedores ambulantes do **Parque da Cidade Joventino Silva (Salvador - BA)**, desenvolvido pelo **Projeto de Extensão da Unijorge**.

---

## Estrutura do Repositório

- `parque_digital/` — Compilador estático em Python:
  - `sistema_toldo.py` — Variáveis CSS, fontes `.woff2` auto-hospedadas (`Fraunces` + `Atkinson Hyperlegible`), ícones de `2 px` e elementos gráficos (*toldo*, *placa de preço* e *comanda*).
  - `estilos_site_toldo.py` — Layout responsivo de `320 px` a `1440 px`.
  - `dados_modelo.py` — Contrato `dados.json` e validador estrito de produção (`--producao`).
  - `compressor_fotos.py` — Compressão local via `<canvas>` para WebP até `150 KB`.
  - `compilador_toldo.py` — Geração de `index.html` legível mesmo sem JavaScript.
  - `gerar_equipe_e_placa.py` — Geração da página interna `equipe.html` e da `placa-a5.html` + `qrcode.svg` (`>= 6 cm`).
  - `build_toldo.py` — CLI de comando único.
- `assets/fonts/` — Fontes variáveis e estáticas `.woff2` locais (`151,9 KB` em português).
- `ambulantes_exemplo/` — Quatro modelos fictícios prontos (`alimentacao`, `brinquedos`, `inflaveis`, `bicicletas`), sem dados reais.
- `docs/` — Saída estática pronta para publicação imediata na Vercel, mais os guias de 1 página:
  - `docs/guia_grupos_unijorge.md` — Passo a passo de campo para estudantes extensionistas.
  - `docs/guia_ambulante.md` — Guia simples para entregar ao trabalhador.
- `tests/test_aceitacao_toldo_aberto.py` — Bateria automatizada de testes de aceitação.

---

## Como Rodar e Editar (Para Integrantes da Equipe)

### 1. Instalar o ambiente (Python 3.11+)
```powershell
python -m venv .venv
.\.venv\Scripts\pip install -e .
```

### 2. Coletar ou editar dados de um ambulante
Você pode preencher pela página de campo `docs/equipe.html` (que salva rascunho local e exporta `dados.json`) ou editar diretamente uma pasta com `dados.json` e `fotos/`:

```text
meu_ambulante/
  dados.json
  fotos/
    barraca.jpg
    item1.jpg
```

> **Atenção:** Nunca publique dados reais sem `consentimento: true` assinalado após leitura em voz alta, nem suba fotos contendo crianças ou chaves de API/dados sensíveis não autorizados no repositório público.

### 3. Gerar o site estático e a Placa A5
Para testar um modelo demonstrativo:
```powershell
.\.venv\Scripts\python.exe -m parque_digital.build_toldo --entrada ambulantes_exemplo/alimentacao --saida docs
```

Para gerar o site real de um ambulante com trava de produção (bloqueia ausência de consentimento, WhatsApp fora do padrão `55DDD...` e dados fictícios):
```powershell
.\.venv\Scripts\python.exe -m parque_digital.build_toldo --entrada meu_ambulante --saida dist/meu_ambulante --producao
```

### 4. Rodar a bateria de testes
```powershell
.\.venv\Scripts\python.exe tests/test_aceitacao_toldo_aberto.py
```

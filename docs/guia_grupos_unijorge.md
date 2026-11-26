# Guia de Campo para os Grupos Extensionistas — Parque Digital Unijorge (1 Página)

**Objetivo:** Cadastrar o ambulante no Parque da Cidade Joventino Silva, colher consentimento informado, fotografar sem expor crianças e publicar gratuitamente sua página e sua Placa A5.

---

## 1. Abordagem e Consentimento (5 min)
1. Apresente-se com crachá/camisa da extensão Unijorge e explique em linguagem direta: **o site e a Placa A5 são 100% gratuitos**, sem mensalidade e sem cobrança de comissão.
2. Leia em voz alta o termo de autorização na página interna `equipe.html`: o ambulante escolhe o que entra e pode pedir troca de preço, troca de foto ou retirada do ar a qualquer momento.
3. **Sem consentimento marcado (`consentimento: true`), não fotografe nem gere build de produção.**

## 2. Fotografia sob Sol Forte (5 min)
- **Onde posicionar:** sempre **à sombra** da barraca ou das amendoeiras (evite sol rachando no rosto).
- **Ângulo:** **na altura dos olhos** para quem atende na barraca; **a 45 graus** para comida e produtos sobre o balcão.
- **Enquadramento seguro:** deixe folga acima da cabeça para o recorte `topo` proteger o rosto em celulares pequenos.
- **Regra inegociável:** **zero crianças** nas fotos (nem ao fundo). Não aplique filtros de aplicativo.

## 3. Coleta na Ficha da Equipe (`equipe.html`) (10 min)
1. Abra `equipe.html` no celular da dupla (o rascunho fica salvo no aparelho mesmo se a internet oscilar).
2. Escolha o **segmento** correto: `alimentacao`, `brinquedos`, `inflaveis` ou `bicicletas`.
3. Confira cada **preço**, **variação** (sabores, tamanhos ou tempos), **dias e horários** e o **ponto de referência** exato no parque. Nunca invente regra, avaliação, história ou horário.
4. **Pix é opcional:** só marque se o ambulante pedir e confira letra por letra a chave e o nome do recebedor.
5. Toque em **Exportar `dados.json`**. Lembre-se: **exportar não publica o site**.

## 4. Compilação, Conferência e Entrega da Placa A5
1. Coloque `dados.json` e as fotos originais em `ambulantes/<slug>/` (`ambulantes/<slug>/fotos/`).
2. Rode no computador do grupo:
   ```powershell
   .venv\Scripts\python.exe -m parque_digital.build_toldo --entrada ambulantes/<slug> --saida dist/<slug> --producao
   ```
   *(O comando comprime as fotos para WebP até `150 KB` e bloqueia a saída se faltar consentimento, se o WhatsApp estiver inválido ou se restar qualquer dado de exemplo.)*
3. Abra `dist/<slug>/index.html`, simule um pedido/pergunta **sem enviar mensagem real** e confira os valores junto com o coordenador.
4. Após publicar na URL final, gere novamente para gravar o QR definitivo, imprima `dist/<slug>/placa-a5.html` em papel grosso/plastificado (verificando que o QR Code tem pelo menos `6 cm` de lado) e escaneie com outro celular antes de entregar na barraca.

# Checklist de validação

## Instalação

- [ ] Clone em máquina limpa.
- [ ] `.env` criado a partir de `.env.example`.
- [ ] Docker sobe sem erro.
- [ ] API responde `/health`.
- [ ] Swagger abre.

## Imagens

- [ ] PNG, JPEG e WebP válidos.
- [ ] Arquivo inválido rejeitado.
- [ ] MIME incorreto rejeitado.
- [ ] Upload grande rejeitado.
- [ ] Imagem com muitos pixels rejeitada.
- [ ] EXIF de rotação corrigido.
- [ ] Transparência preservada.
- [ ] Resultado excedente rejeitado.

## Segurança

- [ ] Nenhum segredo no Git.
- [ ] CORS restrito em produção.
- [ ] Auth habilitada em produção.
- [ ] TTL de arquivos definido.
- [ ] Logs sem conteúdo de imagem.
- [ ] Rate limit configurado.

## Providers

- [ ] Cada provider pode ser desabilitado.
- [ ] Timeout e retry limitados.
- [ ] Erro de provider é visível.
- [ ] Credenciais ficam somente no backend.
- [ ] Custos e limites documentados.

## Produto

- [ ] App Canva abre.
- [ ] Seleção e preview funcionam.
- [ ] Resultado volta ao design.
- [ ] Cancelar/repetir funciona.
- [ ] Lote não bloqueia a interface.
- [ ] Presets de encarte funcionam.

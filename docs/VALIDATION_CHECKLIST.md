# Checklist de validação rígida

## Repositório

- [ ] Nenhum `.env`, token, JSON de credencial ou modelo grande.
- [ ] README descreve o estado real.
- [ ] AGENTS.md está atualizado.
- [ ] Branch/PR não apaga trabalho colaborativo.

## Python Lab

- [ ] Instala em Python 3.11+.
- [ ] Testes passam em máquina limpa.
- [ ] Arquivo inexistente gera erro compreensível.
- [ ] Arquivo inválido é rejeitado.
- [ ] Extensão de saída é validada.
- [ ] JPEG converte RGBA para RGB.
- [ ] PNG preserva transparência.
- [ ] Escala só aceita valores suportados.
- [ ] Perspectiva valida quatro pontos e dimensões positivas.
- [ ] Providers opcionais falham com instrução de instalação.

## API

- [ ] `/health` responde 200.
- [ ] Upload limita bytes e pixels.
- [ ] MIME e conteúdo são conferidos.
- [ ] EXIF é corrigido.
- [ ] Erros retornam 4xx/5xx apropriado.
- [ ] CORS não fica aberto em produção.
- [ ] Segredos não aparecem no OpenAPI/logs.

## Produção

- [ ] HTTPS.
- [ ] Autenticação.
- [ ] Rate limit.
- [ ] Timeout e concorrência limitados.
- [ ] Storage privado com TTL.
- [ ] Backup e rollback documentados.
- [ ] Providers externos documentados.

## Canva

- [ ] App criado no portal.
- [ ] Origem configurada.
- [ ] Seleção e preview testados.
- [ ] Resultado inserido no design.
- [ ] Cancelamento/repetição testados.

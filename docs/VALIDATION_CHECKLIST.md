# Checklist de validação rígida

## Repositório

- [x] Nenhum `.env`, token, JSON de credencial ou modelo grande.
- [x] README descreve o estado real.
- [x] AGENTS.md está atualizado.
- [x] Branch/PR não apaga trabalho colaborativo.

## Python Lab

- [x] Instala em Python 3.11+.
- [x] Testes passam em ambiente virtual limpo.
- [x] Arquivo inexistente gera erro compreensível.
- [x] Arquivo inválido é rejeitado.
- [x] Extensão de saída é validada.
- [x] JPEG converte RGBA para RGB.
- [x] PNG preserva transparência.
- [x] Escala só aceita valores suportados.
- [x] Perspectiva valida quatro pontos e dimensões positivas.
- [x] Providers opcionais falham com instrução de instalação/configuração.

## API

- [x] `/health` responde 200.
- [x] Upload limita bytes e pixels.
- [x] MIME declarado e conteúdo real são conferidos.
- [x] EXIF é corrigido.
- [x] Erros retornam 4xx/5xx apropriado.
- [x] CORS não fica aberto em produção.
- [x] Segredos não aparecem no OpenAPI/logs.

## Produção

- [ ] HTTPS.
- [x] Autenticação.
- [x] Rate limit.
- [x] Timeout e concorrência limitados.
- [x] Storage privado com TTL.
- [x] Backup de estado e rollback documentados.
- [x] Providers externos documentados.

## Canva

- [x] App criado no portal.
- [x] Origem local configurada pela Canva CLI.
- [x] Manifesto sincronizado com o portal.
- [x] Lint, tipos, testes e bundle de produção validados.
- [x] Seleção e preview testados manualmente dentro do editor.
- [x] Resultado aplicado e salvo em uma imagem descartável do design.
- [ ] Cancelamento/repetição testados manualmente.

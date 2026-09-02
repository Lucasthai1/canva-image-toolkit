# Roadmap

## Fundação concluída

- [x] API FastAPI.
- [x] Docker Compose.
- [x] Health check.
- [x] Validação de MIME, tamanho e pixels.
- [x] Correção de orientação EXIF.
- [x] Ajustes de brilho, contraste, saturação e nitidez.
- [x] Espelhamento e rotação.
- [x] Upscale provisório seguro.
- [x] Testes automatizados.

## MVP Canva concluído

- [x] App criado com Canva Apps SDK em React/TypeScript.
- [x] Seleção e substituição segura de uma imagem raster.
- [x] Preview e ajustes locais sem servidor externo.
- [x] Presets básicos para fotos de produtos de encartes.
- [x] Limites de bytes/pixels e cancelamento quando a seleção muda.
- [x] Testes, lint, verificação de tipos e build de produção.

## Backlog técnico concluído

- [x] Editor Fabric.js com caneta, borracha de objetos, formas e undo/redo.
- [x] Warp por quatro pontos na API e malha local no app.
- [x] Real-ESRGAN opcional por worker/binário, desativável e com fallback Lanczos.
- [x] Remoção de fundo via Hugging Face, desativada sem token.
- [x] OCR via Google Cloud Vision, desativado sem credencial.
- [x] Fila Redis e jobs assíncronos.
- [x] Presets calibrados para hortifruti, carnes, limpeza e congelados.
- [x] Processamento em lote com limite configurável.
- [x] Autenticação Bearer, CORS fechado, rate limit, timeout e concorrência.

## Evoluções opcionais

- [ ] Autenticação de usuário final baseada no fluxo de backend do Canva.
- [ ] Worker GPU dedicado quando houver hardware e orçamento aprovados.
- [ ] Storage S3/R2 quando o volume local deixar de ser suficiente.

## Critério de pronto

Cada recurso deve ter teste, tratamento de erro, limite de upload, documentação e uma forma clara de desativar providers pagos.

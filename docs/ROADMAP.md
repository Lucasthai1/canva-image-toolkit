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

## Próxima etapa

- [ ] Editor Fabric.js com caneta, borracha, formas e undo/redo.
- [ ] Warp por quatro pontos e malha.
- [ ] Real-ESRGAN opcional por worker GPU.
- [ ] Remoção de fundo via Hugging Face.
- [ ] OCR via Google Cloud Vision.
- [ ] Fila Redis e jobs assíncronos.
- [ ] Presets calibrados por categoria de produto e fundo.
- [ ] Processamento em lote.
- [ ] Autenticação app/API e rate limit.

## Critério de pronto

Cada recurso deve ter teste, tratamento de erro, limite de upload, documentação e uma forma clara de desativar providers pagos.

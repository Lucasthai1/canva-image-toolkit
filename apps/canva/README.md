# Canva Image Toolkit app

App Canva em React/TypeScript para editar uma imagem raster selecionada sem
enviar o arquivo a um serviço externo.

## Recursos atuais

- detecção de uma única imagem selecionada no design;
- prévia de brilho, contraste, saturação, rotação e espelhamento;
- nitidez por convolução no momento da aplicação;
- upscale local em 2x com limite de segurança de 25 megapixels;
- substituição da imagem pelo resultado em PNG usando as APIs oficiais de
  seleção e assets do Canva;
- presets rápidos para fotos de produtos de encarte;
- mensagens de estado e erros recuperáveis em português.

## Requisitos

- Node.js 22 ou 24;
- npm 10 ou superior;
- Canva CLI autenticado;
- app criado no Canva Developer Portal com os escopos declarados em
  `canva-app.json`.

## Desenvolvimento

```powershell
cd apps\canva
npm install
npm run lint:check
npm test
npm run build
npm start
```

No editor do Canva, abra o app de desenvolvimento, selecione exatamente uma
imagem e use **Aplicar na imagem selecionada**. A operação gera um novo asset e
substitui somente a referência da imagem selecionada; os demais elementos do
design não são alterados.

## Limites conhecidos

- funciona apenas com imagens raster selecionadas;
- o upscale é Lanczos/bicúbico do navegador, não Real-ESRGAN;
- o resultado é PNG para preservar transparência;
- a saída é recusada acima de 25 megapixels para evitar travar o editor;
- recortes e efeitos já aplicados pelo Canva podem influenciar a imagem-fonte
  retornada pela Selection API.

# Integração com Canva

## Pré-requisitos

1. Conta de desenvolvedor Canva.
2. App criado no Developer Portal.
3. Starter Kit oficial instalado.
4. Canva CLI autenticado para iniciar a URL HTTPS temporária de preview.
5. Backend separado do frontend somente para operações pesadas futuras.

## Implementação do app

1. O app React/TypeScript fica em `apps/canva`.
2. `useSelection("image")` exige exatamente uma imagem raster selecionada.
3. `getTemporaryUrl` fornece a origem temporária para a prévia e o processamento.
4. Brilho, contraste, saturação, nitidez, rotação, flip e upscale 2x são
   executados localmente com Canvas.
5. A saída PNG é limitada a 25 megapixels e enviada ao Canva com `upload`.
6. Antes de salvar, o app relê a seleção e cancela se ela mudou durante o
   processamento.
7. Somente o `ref` da imagem selecionada é substituído e salvo no draft.
8. Operações pesadas futuras devem usar a API sem expor tokens no frontend.

## Escopos mínimos

- `canva:design:content:read`
- `canva:design:content:write`
- `canva:asset:private:read`
- `canva:asset:private:write`

O manifesto versionado em `apps/canva/canva-app.json` é a fonte de verdade e
deve ser sincronizado com `canva apps config push` depois de alterações.

## Cuidados

- Não expor tokens de provider no app.
- Não assumir que uma imagem selecionada está disponível como URL pública.
- Validar permissões e escopos no portal.
- Testar imagens transparentes, CMYK, EXIF, grandes e com nomes especiais.
- Manter o app em rascunho/preview até o fluxo estar estável; distribuição
  privada para equipes exige Canva Enterprise.

## Critérios de aceitação

- Uma imagem selecionada pode ser previewada.
- Operação local não envia a imagem para terceiros.
- Resultado processado volta ao design sem perda inesperada de transparência.
- Erros de API são compreensíveis.
- Uma troca de seleção durante o processamento cancela a gravação com erro
  recuperável e o usuário consegue repetir.

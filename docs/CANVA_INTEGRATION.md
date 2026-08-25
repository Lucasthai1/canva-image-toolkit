# Integração com Canva

## Pré-requisitos

1. Conta de desenvolvedor Canva.
2. App criado no Developer Portal.
3. Starter Kit oficial instalado.
4. URL HTTPS pública para preview, ou mecanismo de desenvolvimento suportado pela Canva.
5. Backend separado do frontend.

## Implementação do app

1. Criar o app com React/TypeScript.
2. Implementar seleção de imagem.
3. Renderizar preview no painel.
4. Implementar caneta, borracha, formas, filtros e undo/redo localmente.
5. Enviar somente operações pesadas para a API.
6. Inserir o PNG final no design.
7. Mostrar progresso, erro, cancelar e repetir.

## Cuidados

- Não expor tokens de provider no app.
- Não assumir que uma imagem selecionada está disponível como URL pública.
- Validar permissões e escopos no portal.
- Testar imagens transparentes, CMYK, EXIF, grandes e com nomes especiais.
- Manter o app em preview/privado até o fluxo estar estável.

## Critérios de aceitação

- Uma imagem selecionada pode ser previewada.
- Operação local não envia a imagem para terceiros.
- Resultado processado volta ao design sem perda inesperada de transparência.
- Erros de API são compreensíveis.
- O usuário consegue cancelar e repetir.

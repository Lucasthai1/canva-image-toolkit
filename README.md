# Canva Image Toolkit

Toolkit privado para edição de imagens e preparação de encartes no Canva.

## Objetivos

- Upscale 2x/4x.
- Remoção de fundo e objetos.
- Warp, perspectiva e liquify.
- Caneta, pincel, formas e borracha.
- Filtros e ajustes.
- OCR para nome e preço.
- Processamento em lote.

## Estrutura

- `apps/canva`: app React/TypeScript para o Canva.
- `services/api`: API FastAPI para processamento.
- `services/worker`: tarefas de IA e imagem.
- `packages/shared-types`: contratos compartilhados.

## Desenvolvimento

1. Copie `.env.example` para `.env`.
2. Execute `docker compose up --build` para subir a API.
3. Instale o app Canva com o Apps SDK Starter Kit.
4. Configure `VITE_API_URL`.

Este projeto é privado e ainda está em fase de fundação. Nunca comite chaves de API.

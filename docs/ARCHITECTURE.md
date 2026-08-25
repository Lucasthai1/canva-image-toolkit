# Arquitetura

## Componentes

### App Canva

Interface privada no editor Canva. Responsável por seleção de elementos, preview, controles, edição local e inserção do resultado no design.

### API FastAPI

Recebe uploads pequenos e operações rápidas. Deve validar autenticação, MIME real, tamanho, pixels e parâmetros antes de processar.

### Worker

Executa Real-ESRGAN, remoção de fundo, inpainting, OCR e lotes. Não deve bloquear requests HTTP longos.

### Redis

Fila e estado de jobs assíncronos. Não é armazenamento permanente de imagens.

### Storage

Armazenamento temporário S3/R2/local. Cada objeto deve ter TTL, nome aleatório e acesso privado.

## Fluxo recomendado

1. Canva envia imagem ou referência segura.
2. API valida conteúdo e cria job.
3. Worker processa com provider selecionado.
4. Resultado é salvo temporariamente.
5. API devolve URL assinada ou bytes.
6. Canva insere o resultado.
7. Job e arquivos expiram automaticamente.

## Decisões

- Operações locais: Fabric.js/Canvas API.
- Operações pesadas: worker Python.
- Providers atrás de adaptadores: `UpscalerProvider`, `BackgroundRemovalProvider`, `OcrProvider`.
- REST versionada em `/v1`.
- Falhas de provider devem ser explícitas e observáveis.

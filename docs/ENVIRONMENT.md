# Variáveis de ambiente

O arquivo `.env.example` é um mapa de configuração; ele não contém credenciais. Copie-o para `.env` e preencha apenas o necessário.

## API

- `APP_ENV`: `development` ou `production`.
- `API_PORT`: porta publicada localmente.
- `CORS_ORIGINS`: origens permitidas, separadas por vírgula.
- `API_AUTH_TOKEN`: obrigatório em produção quando autenticação for implementada.
- `MAX_UPLOAD_BYTES`: limite de bytes por imagem.
- `MAX_PIXELS`: limite de pixels de entrada.
- `MAX_OUTPUT_PIXELS`: limite de pixels de saída.
- `REQUEST_TIMEOUT_SECONDS`: timeout de operações.
- `LOG_LEVEL`: nível de log.

## Providers

- `UPSCALER_PROVIDER`: `lanczos`, `realesrgan` ou `api`.
- `REALESRGAN_MODEL_PATH`: caminho local do modelo.
- `REALESRGAN_DEVICE`: `cpu` ou `cuda`.
- `HUGGINGFACE_API_TOKEN`: token somente no backend.
- `HF_BACKGROUND_MODEL`: modelo de remoção de fundo.
- `GOOGLE_APPLICATION_CREDENTIALS`: caminho local não versionado para credencial Google.
- `GOOGLE_CLOUD_PROJECT`: projeto Google Cloud.
- `VISION_TIMEOUT_SECONDS`: timeout do OCR.

## Infraestrutura

- `REDIS_URL`: fila Redis.
- `STORAGE_PROVIDER`: `local`, `s3`, `r2` ou `minio`.
- `STORAGE_DIR`: diretório temporário local.
- `STORAGE_BUCKET`, `STORAGE_ENDPOINT`, `STORAGE_REGION`.
- `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`.
- `STORAGE_TTL_SECONDS`: expiração de arquivos.

## Canva

- `CANVA_APP_ID`.
- `CANVA_APP_ORIGIN`.
- `CANVA_BACKEND_URL`.
- `CANVA_ALLOWED_USER_ID` opcional.

Nunca coloque valores reais neste arquivo ou em issues públicas.

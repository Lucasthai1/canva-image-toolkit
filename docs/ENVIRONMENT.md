# Variáveis de ambiente

Copie `.env.example` para `.env`. Nunca comite `.env`.

## API

- `APP_ENV`: `development` ou `production`.
- `API_PORT`: porta HTTP, padrão `8000`.
- `CORS_ORIGINS`: origens separadas por vírgula.
- `API_AUTH_TOKEN`: token interno opcional; obrigatório em produção.
- `MAX_UPLOAD_BYTES`: limite de upload.
- `MAX_PIXELS`: limite de pixels de entrada.
- `MAX_OUTPUT_PIXELS`: limite de pixels de saída.
- `REQUEST_TIMEOUT_SECONDS`: timeout geral.
- `LOG_LEVEL`: `INFO`, `WARNING` ou `ERROR`.

## Redis e storage

- `REDIS_URL`: URL Redis.
- `STORAGE_PROVIDER`: `local`, `s3`, `r2` ou `minio`.
- `STORAGE_BUCKET`.
- `STORAGE_ENDPOINT`.
- `STORAGE_REGION`.
- `STORAGE_ACCESS_KEY`.
- `STORAGE_SECRET_KEY`.
- `STORAGE_TTL_SECONDS`.

## IA

- `UPSCALER_PROVIDER`: `lanczos`, `realesrgan` ou `api`.
- `REALESRGAN_MODEL_PATH`.
- `REALESRGAN_DEVICE`: `cpu` ou `cuda`.
- `HUGGINGFACE_API_TOKEN`.
- `HF_BACKGROUND_MODEL`.
- `GOOGLE_APPLICATION_CREDENTIALS`.
- `GOOGLE_CLOUD_PROJECT`.

## Canva

- `CANVA_APP_ID`.
- `CANVA_APP_ORIGIN`.
- `CANVA_BACKEND_URL`.
- `CANVA_ALLOWED_USER_ID` opcional para modo privado.

## Política

Em produção, falhe ao iniciar se tokens obrigatórios estiverem ausentes. Em desenvolvimento, providers não configurados devem aparecer como indisponíveis, nunca como se funcionassem.

# Contratos HTTP

## Saúde

`GET /health` retorna:

```json
{"status":"ok","service":"canva-image-toolkit","version":"1.0.0"}
```

## Operações de imagem

Endpoints atuais aceitam `multipart/form-data` no campo `file` e retornam `image/png`:

- `POST /v1/image/adjust?brightness=1&contrast=1&saturation=1&sharpness=1`
- `POST /v1/image/flip?horizontal=true`
- `POST /v1/image/rotate?angle=0`
- `POST /v1/image/upscale?scale=2`
- `POST /v1/image/perspective` com `points`, `width` e `height` no formulário.

- `POST /v1/image/remove-background`
- `POST /v1/image/ocr`

Os dois últimos retornam `503` com instrução explícita enquanto seus providers
estiverem desativados. `GET /v1/providers` informa somente disponibilidade, sem
expor credenciais.

## Jobs e lotes

- `POST /v1/jobs`: formulário com `operation`, `file` e `params` JSON; retorna 202.
- `POST /v1/batches`: os mesmos campos e múltiplos `files`; retorna IDs de jobs.
- `GET /v1/jobs/{id}`: estado `queued`, `running`, `completed` ou `failed`.
- `GET /v1/jobs/{id}/result`: PNG ou JSON; retorna 409 antes da conclusão e 410 após TTL.

Todos os endpoints, exceto `/health` e `/ready`, exigem
`Authorization: Bearer <token>` quando `API_AUTH_TOKEN` está configurado.

## Status de erro

- `400`: arquivo inválido ou parâmetro inválido.
- `413`: arquivo ou resultado excede limites.
- `415`: MIME não suportado.
- `503`: provider ou fila indisponível.
- `504`: timeout de processamento.
- `500`: erro inesperado; não exibir detalhes sensíveis.

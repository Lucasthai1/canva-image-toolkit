# Contratos HTTP

## Saúde

`GET /health` retorna:

```json
{"status":"ok","service":"canva-image-toolkit","version":"0.2.0"}
```

## Operações de imagem

Endpoints atuais aceitam `multipart/form-data` no campo `file` e retornam `image/png`:

- `POST /v1/image/adjust?brightness=1&contrast=1&saturation=1&sharpness=1`
- `POST /v1/image/flip?horizontal=true`
- `POST /v1/image/rotate?angle=0`
- `POST /v1/image/upscale?scale=2`

Endpoints reservados retornam `501` até provider ser configurado:

- `POST /v1/image/remove-background`
- `POST /v1/image/ocr`

## Status de erro

- `400`: arquivo inválido ou parâmetro inválido.
- `413`: arquivo ou resultado excede limites.
- `415`: MIME não suportado.
- `501`: recurso ainda não configurado.
- `500`: erro inesperado; não exibir detalhes sensíveis.

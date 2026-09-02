# Troubleshooting

## Docker não inicia

- Confirme Docker Desktop aberto.
- Execute `docker compose config`.
- Veja `docker compose logs api`.
- Remova containers antigos com `docker compose down` e tente novamente.

## Porta 8000 ocupada

Altere `API_PORT` e a porta publicada no `docker-compose.yml`, ou encerre o processo que usa a porta.

## PowerShell bloqueia ativação

Use `Set-ExecutionPolicy -Scope Process Bypass` apenas na sessão atual, ou execute o servidor dentro do Docker.

## CORS

Inclua exatamente a origem do app em `CORS_ORIGINS`, sem barra final indevida.

## Upscale lento

O fallback Lanczos é CPU. Real-ESRGAN deve rodar em worker e pode exigir GPU. Reduza tamanho, use fila e imponha limite.

## OCR/remoção de fundo 503

Isso indica que o adapter existe, mas a credencial do provider não foi injetada.
Consulte `GET /v1/providers`; não trate o estado desativado como sucesso.

## Job permanece na fila

Verifique `docker compose ps worker redis` e os logs do worker. O Redis não é
exposto publicamente e os arquivos de entrada/saída expiram conforme
`STORAGE_TTL_SECONDS`.

## Testes falham

Confirme que o ambiente virtual está ativo e execute `pip install -r services/api/requirements.txt`.

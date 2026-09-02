# Deploy

## VPS com Docker

1. Instale Docker e Git.
2. Clone o repositório.
3. Crie `.env` com valores reais fora do Git.
4. Configure firewall para expor somente 80/443 e SSH.
5. Use reverse proxy HTTPS, como Caddy ou Nginx.
6. Suba com `docker compose up -d --build`.
7. Verifique `/health`.
8. Configure backup apenas para dados necessários.
9. Configure limpeza de uploads e logs.

Na Tencent Lighthouse autorizada, o script idempotente recomendado é:

```bash
sudo bash scripts/deploy_tencent.sh
```

Ele recusa checkout sujo, preserva o commit anterior, cria o token com
`openssl rand`, valida o Compose, não imprime segredo e executa smoke tests
público e autenticado. O domínio padrão é `43.156.64.19.sslip.io`, permitindo
TLS automático pelo Caddy sem alterar DNS. Portas 80/443 ocupadas fazem o script
parar antes de tocar no proxy existente.

Rollback:

```bash
sudo bash /opt/canva-image-toolkit/scripts/rollback_tencent.sh
```

O arquivo `.env`, volumes Redis/storage e estado de rollback permanecem somente
na VPS. Não copie o token para chat, Git ou logs.

## Vercel

Use Vercel principalmente para frontend/app web. Não use funções serverless para Real-ESRGAN pesado sem validar limites de tempo, memória e custo. Aponte `VITE_API_URL` para uma API persistente.

## Produção mínima

- HTTPS.
- Token entre frontend/backend.
- CORS fechado.
- Rate limit.
- Upload privado.
- TTL de arquivos.
- Logs sem imagens ou tokens.
- Monitoramento de erros.
- Health check.
- Plano de rollback.
- Containers sem capabilities, usuário não-root na API/worker e Redis sem porta pública.

## Checklist pós-deploy

```text
GET /health -> 200
OpenAPI não expõe segredo
CORS aceita somente origem esperada
Upload inválido -> 4xx
Arquivo grande -> 413
Provider ausente -> erro explícito
Logs não mostram tokens
Container reinicia sem perder configuração
```

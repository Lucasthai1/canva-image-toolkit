# Segurança

## Segredos

Nunca comite `.env`, tokens Hugging Face, credenciais Google, chaves S3 ou tokens Canva. Use secrets do provedor de deploy.

## Uploads

Validar MIME declarado e conteúdo real, impor limite de bytes/pixels, corrigir EXIF, rejeitar formatos não suportados e evitar nomes fornecidos pelo usuário em caminhos locais.

## API

Adicionar autenticação em produção, CORS restrito, rate limit, timeout, limites de concorrência e mensagens sem stack trace. Não retornar URLs públicas permanentes.

## Imagens

Remover metadados quando apropriado. Não manter arquivos além do TTL. Isolar worker e impedir execução de arquivos enviados.

## Privacidade

O app é privado. Documentar quais imagens são enviadas a providers externos. Dar preferência a modelos locais quando a imagem for sensível.

## Verificação manual

- Procurar padrões `sk-`, `ghp_`, `AIza`, `-----BEGIN`, tokens JWT e credenciais JSON.
- Conferir `.gitignore`.
- Conferir logs.
- Revisar dependências e CVEs.
- Rodar testes de upload malformado.

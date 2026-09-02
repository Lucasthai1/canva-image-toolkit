# Prompt para instalar com outro agente

Copie o texto abaixo para um agente de código:

```text
Você está trabalhando no repositório Lucasthai1/canva-image-toolkit.

Leia primeiro AGENTS.md, README.md e docs/GETTING_STARTED.md. O objetivo é
manter o toolkit de edição de imagens para encartes. Python Lab, API FastAPI,
worker Redis e app Canva já estão implementados; valide o estado real antes de
ampliar qualquer provider.

Antes de codificar:
1. Faça inventário dos arquivos.
2. Não sobrescreva mudanças de colaboradores.
3. Identifique o sistema operacional e versões disponíveis.
4. Nunca peça ou grave credenciais em arquivos versionados.
5. Explique quais providers serão locais e quais enviarão imagens a terceiros.

Para instalar:
- Python 3.11+.
- Criar `python-lab/.venv`.
- Instalar `python-lab/requirements.txt`.
- Rodar `python -m pytest -q` dentro de `python-lab`.
- Opcionalmente copiar `.env.example` e subir `docker compose up --build`.

Ao implementar qualquer recurso:
- Adicione uma função testável.
- Valide entradas e limites.
- Preserve RGBA/EXIF quando aplicável.
- Adicione teste de sucesso e falha.
- Atualize README, docs e roadmap.
- Execute testes, compilação e verificação de segredos.
- Informe claramente o que continua pendente.

Não declare um provider opcional como habilitado sem credencial/hardware e
teste real; adapters implementados mas desativados devem aparecer como tal.
``` 

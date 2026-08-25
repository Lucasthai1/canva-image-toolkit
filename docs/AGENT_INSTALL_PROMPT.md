# Prompt para instalar com outro agente

Copie o texto abaixo para um agente de código:

```text
Você está trabalhando no repositório Lucasthai1/canva-image-toolkit.

Leia primeiro AGENTS.md, README.md e docs/GETTING_STARTED.md. O objetivo é criar um toolkit de edição de imagens para preparar encartes e futuramente integrar ao Canva. O Python Lab é o protótipo inicial; a API FastAPI é a segunda camada; o app Canva ainda não está implementado.

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

Não declare Canva, OCR, Real-ESRGAN, remoção de fundo ou jobs como prontos sem integração e teste real.
``` 

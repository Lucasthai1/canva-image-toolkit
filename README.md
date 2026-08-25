# Canva Image Toolkit

Toolkit privado para edição de imagens e preparação de encartes no Canva.

> Estado atual: fundação técnica pronta para desenvolvimento local. O app Canva, Real-ESRGAN, OCR, remoção de fundo e processamento em lote ainda precisam ser implementados/integrados.

## Quick start

```powershell
git clone https://github.com/Lucasthai1/canva-image-toolkit.git
cd canva-image-toolkit
Copy-Item .env.example .env
docker compose up --build
```

Abra `http://localhost:8000/docs` e teste `GET /health`.

Sem Docker:

```powershell
cd services/api
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Testes:

```powershell
cd services/api
python -m pytest -q
```

## Documentação operacional

- [Passo a passo](docs/GETTING_STARTED.md)
- [Instruções para agentes](AGENTS.md)
- [Arquitetura](docs/ARCHITECTURE.md)
- [APIs e providers](docs/API_PROVIDERS.md)
- [Variáveis de ambiente](docs/ENVIRONMENT.md)
- [Integração Canva](docs/CANVA_INTEGRATION.md)
- [Deploy](docs/DEPLOYMENT.md)
- [Segurança](docs/SECURITY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Contratos da API](docs/API_CONTRACTS.md)
- [Checklist](docs/VALIDATION_CHECKLIST.md)
- [Roadmap](docs/ROADMAP.md)

## Princípios

- Nenhum segredo no Git.
- Processamento caro somente em worker/backend.
- Uploads com limite de tamanho, pixels e MIME.
- Arquivos temporários devem expirar.
- Cada recurso deve possuir teste e tratamento de erro.
- Não declarar um recurso como pronto se ele ainda retorna 501.

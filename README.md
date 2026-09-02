# Canva Image Toolkit

Toolkit colaborativo para testar edição de imagens e, depois, integrar recursos ao Canva. O repositório está público para colaboração; não coloque imagens reais, tokens ou credenciais aqui.

## Estado real

| Área | Estado |
|---|---|
| API FastAPI básica | Funcional |
| Ajustes, flip, rotação | Funcional |
| Upscale Lanczos | Funcional como fallback |
| Python Lab CLI | Funcional para testes locais |
| Perspectiva Python/OpenCV | Funcional |
| Remoção de fundo | Adapter Hugging Face implementado; exige token |
| OCR | Adapter Google Vision implementado; exige credencial injetada |
| Real-ESRGAN | Worker opcional por binário; Lanczos permanece como fallback |
| App Canva | Funcional com ajustes, malha, desenho e objetos Fabric.js |
| Warp/perspectiva | Malha local no app e quatro pontos na API |
| Jobs, storage e lote | Redis, worker, TTL e lote implementados |

## Começo rápido

### Python Lab recomendado

```powershell
git clone https://github.com/Lucasthai1/canva-image-toolkit.git
cd canva-image-toolkit\python-lab
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
```

Exemplo:

```powershell
python image_toolkit.py --input foto.jpg --output saida.png --operation upscale --scale 2
```

### API com Docker

Na raiz:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Abra `http://localhost:8000/docs`.

### App Canva

```powershell
cd apps\canva
npm install
npm run lint:check
npm test
npm run build
npm start
```

O app seleciona uma imagem raster, mostra a prévia de ajustes locais e substitui
somente aquela imagem pelo PNG processado. O editor inclui caneta, formas,
texto, borracha de objetos, desfazer/refazer e perspectivas por malha. Consulte
[`apps/canva/README.md`](apps/canva/README.md) para recursos, escopos e limites.

Operações pesadas usam `POST /v1/jobs` ou `POST /v1/batches`, com Redis e worker
separado. Em produção a API exige Bearer token, CORS explícito, rate limit,
timeout, concorrência limitada e storage privado com TTL.

## Documentação

- [Instruções para agentes](AGENTS.md)
- [Instalação detalhada](docs/GETTING_STARTED.md)
- [Arquitetura](docs/ARCHITECTURE.md)
- [APIs e providers](docs/API_PROVIDERS.md)
- [Variáveis](docs/ENVIRONMENT.md)
- [Integração Canva](docs/CANVA_INTEGRATION.md)
- [Deploy](docs/DEPLOYMENT.md)
- [Segurança](docs/SECURITY.md)
- [Contratos](docs/API_CONTRACTS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Checklist](docs/VALIDATION_CHECKLIST.md)
- [Contribuição](CONTRIBUTING.md)
- [Roadmap](docs/ROADMAP.md)

## Regra de colaboração

Use branches e pull requests quando possível. Não force-push em `main`, não apague trabalho de colaborador e descreva como testar cada mudança.

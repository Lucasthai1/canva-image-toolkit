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
| Remoção de fundo | Opcional no Python Lab; API ainda pendente |
| OCR | Opcional no Python Lab; API ainda pendente |
| Real-ESRGAN | Pendente |
| App Canva | Pendente |
| Warp/liquify avançado | Pendente |
| Jobs, storage e lote | Pendente |

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

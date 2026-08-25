# Começar em 10 minutos

## Opção A: Docker

1. Instale Docker Desktop.
2. Copie `.env.example` para `.env`.
3. Execute `docker compose up --build`.
4. Abra `http://localhost:8000/docs`.
5. Teste `GET /health` e os endpoints de imagem.

## Opção B: Python local

```powershell
cd services/api
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Em Linux/macOS, use `source .venv/bin/activate`.

## Testes

Na raiz:

```powershell
make test
```

No Windows sem Make:

```powershell
cd services/api
python -m pytest -q
```

## Limitações atuais

- Upscale atual usa Lanczos; Real-ESRGAN será adicionado como worker opcional.
- OCR e remoção de fundo retornam 501 até o provider ser configurado.
- O app Canva ainda precisa ser criado a partir do Starter Kit oficial.

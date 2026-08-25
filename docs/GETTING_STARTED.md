# Instalação detalhada

## Pré-requisitos

- Windows 10/11, Linux ou macOS.
- Python 3.11 ou superior para o Python Lab.
- Docker Desktop para a API.
- Git.

## Python Lab

```powershell
git clone https://github.com/Lucasthai1/canva-image-toolkit.git
cd canva-image-toolkit\python-lab
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
```

Se o PowerShell bloquear o ambiente:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.venv\Scripts\Activate.ps1
```

Operações disponíveis:

```text
upscale, adjust, rotate, flip, perspective, remove-background, ocr
```

Providers opcionais:

```powershell
pip install "rembg[cpu]" onnxruntime
pip install easyocr
```

## API

Na raiz do projeto:

```powershell
Copy-Item .env.example .env
docker compose config
docker compose up --build
```

Teste em outro terminal:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Documentação interativa: `http://localhost:8000/docs`.

## Linux/macOS

Use `cp .env.example .env`, `source .venv/bin/activate` e os mesmos comandos Docker.

## Parar e limpar

```powershell
docker compose down
docker compose down -v
```

O segundo comando remove o volume local do Redis/storage. Use somente se quiser apagar os dados locais.

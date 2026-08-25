# Python Image Lab

Ambiente independente para testar recursos de imagem antes da integração com o Canva.

## Instalação no Windows

```powershell
cd python-lab
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Comandos

```powershell
python image_toolkit.py --input foto.jpg --output saida.png --operation upscale --scale 2
python image_toolkit.py --input foto.jpg --output saida.png --operation adjust --brightness 1.1 --contrast 1.2 --saturation 1.1 --sharpness 1.5
python image_toolkit.py --input foto.jpg --output saida.png --operation rotate --angle 12
python image_toolkit.py --input foto.jpg --output saida.png --operation remove-background
python image_toolkit.py --input foto.jpg --output ocr.json --operation ocr
python -m pytest -q
```

## Operações

- `upscale`: fallback Lanczos 2x/4x.
- `adjust`: brilho, contraste, saturação e nitidez.
- `rotate`: rotação com expansão.
- `flip`: espelhamento.
- `perspective`: transformação pelos quatro cantos usando coordenadas JSON.
- `remove-background`: provider `rembg` opcional.
- `ocr`: provider `easyocr` opcional.

Os providers opcionais baixam modelos na primeira execução. Para imagens sensíveis, prefira processamento local e confirme os termos/licenças dos modelos antes de uso comercial.

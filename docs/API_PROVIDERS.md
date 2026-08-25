# APIs e providers

## Obrigatórios por recurso

| Recurso | Provider recomendado | Obrigatório agora? | Observação |
|---|---|---:|---|
| Ajustes/flip/rotação | Pillow/OpenCV | Não | Já existe na API |
| Caneta/formas | Fabric.js | Não | Deve rodar no app Canva |
| Warp/perspectiva | Fabric.js/OpenCV | Não | Implementar com preview e export |
| Upscale | Real-ESRGAN local/GPU | Não | Atual é fallback Lanczos |
| Remoção de fundo | Hugging Face/rembg | Não | Requer token ou modelo local |
| OCR | Google Cloud Vision/PaddleOCR | Não | Requer credencial ou modelo local |
| Jobs | Redis + worker | Não | Necessário para operações demoradas |
| Storage | S3/R2/MinIO/local | Não | Necessário para lotes e arquivos grandes |

## Hugging Face

Variáveis: `HUGGINGFACE_API_TOKEN`, `HF_BACKGROUND_MODEL`, `HF_TIMEOUT_SECONDS`.
Nunca envie o token ao frontend. Use apenas no backend/worker.

## Google Cloud Vision

Variáveis: `GOOGLE_APPLICATION_CREDENTIALS` ou credencial injetada pelo ambiente, `GOOGLE_CLOUD_PROJECT` e `VISION_TIMEOUT_SECONDS`.
Não comite JSON de service account. Em produção prefira identidade gerenciada ou secret manager.

## Real-ESRGAN

Variáveis: `UPSCALER_PROVIDER=local`, `REALESRGAN_MODEL_PATH`, `REALESRGAN_TILE`, `REALESRGAN_DEVICE`.
Comece com fallback Lanczos para validar o fluxo. Só habilite GPU quando houver memória e testes de custo/tempo.

## Canva Apps SDK

É necessário criar um app no portal de desenvolvedores, configurar origem/URL de desenvolvimento e usar o Starter Kit oficial. O backend deve aceitar apenas origens e tokens previstos. Não presumir que uma API do Canva exista sem validar a documentação vigente.

## Regra de provider

Cada provider deve possuir: interface, implementação, timeout, retry limitado, mensagem de erro, teste unitário, teste de indisponibilidade e configuração para desabilitar.

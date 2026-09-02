# APIs e providers

## Obrigatórios por recurso

| Recurso | Provider recomendado | Obrigatório agora? | Observação |
|---|---|---:|---|
| Ajustes/flip/rotação | Pillow/OpenCV | Não | Já existe na API |
| Caneta/formas | Fabric.js | Sim | Implementado no app Canva |
| Warp/perspectiva | Fabric.js/OpenCV | Sim | Malha local e endpoint de quatro pontos |
| Upscale | Real-ESRGAN local/GPU | Não | Adapter implementado; fallback Lanczos |
| Remoção de fundo | Hugging Face | Não | Adapter implementado; exige token |
| OCR | Google Cloud Vision | Não | Adapter implementado; exige credencial |
| Jobs | Redis + worker | Sim | Implementado no Compose |
| Storage | Local privado | Sim | Volume com UUID e TTL; S3/R2 opcional |

## Hugging Face

Variáveis: `HUGGINGFACE_API_TOKEN`, `HF_BACKGROUND_MODEL`, `HF_TIMEOUT_SECONDS`.
Nunca envie o token ao frontend. Use apenas no backend/worker.

## Google Cloud Vision

Variáveis: `GOOGLE_APPLICATION_CREDENTIALS` ou credencial injetada pelo ambiente, `GOOGLE_CLOUD_PROJECT` e `VISION_TIMEOUT_SECONDS`.
Não comite JSON de service account. Em produção prefira identidade gerenciada ou secret manager.

## Real-ESRGAN

Variáveis: `UPSCALER_PROVIDER=realesrgan`, `REALESRGAN_BINARY`,
`REALESRGAN_MODEL` e `REALESRGAN_TILE`. O adapter executa o binário oficial sem
shell, com timeout e diretório aleatório. Só habilite GPU quando houver memória
e testes de custo/tempo; a Lighthouse de 2 GB usa Lanczos por padrão.

## Canva Apps SDK

É necessário criar um app no portal de desenvolvedores, configurar origem/URL de desenvolvimento e usar o Starter Kit oficial. O backend deve aceitar apenas origens e tokens previstos. Não presumir que uma API do Canva exista sem validar a documentação vigente.

## Regra de provider

Cada provider possui status sem segredo, implementação isolada, timeout,
retry limitado quando remoto, erro explícito e configuração para desabilitar.

# Handoff para agentes de IA e desenvolvedores

## Contexto do produto

Este repositório implementa um toolkit privado para uso pessoal em encartes de supermercado no Canva. O usuário quer acelerar a preparação de imagens de produtos: upscale, remoção de fundo, ajustes, distorção, desenho, OCR de nomes/preços e processamento em lote.

## Regras obrigatórias

1. Leia este arquivo e `docs/` antes de alterar código.
2. Não invente credenciais, IDs, URLs de produção ou recursos do Canva.
3. Nunca grave tokens em arquivos, logs, commits ou respostas.
4. Não substitua uma integração real por um mock silencioso.
5. Se algo não estiver implementado, retorne erro explícito/documente como pendência.
6. Preserve compatibilidade com Windows e Docker.
7. Toda alteração deve incluir teste, documentação e atualização do roadmap quando aplicável.
8. Valide tamanho do arquivo, MIME real, pixels, dimensões de saída e timeout.
9. Não armazene imagens permanentemente sem uma decisão explícita.
10. Antes de concluir, execute testes, lint/typecheck quando existirem e verifique o diff.

## Ordem de implementação

1. API e contratos estáveis.
2. Editor local do app Canva.
3. Autenticação app/backend.
4. Jobs assíncronos com Redis.
5. Providers de IA atrás de interfaces.
6. Observabilidade, limites e limpeza.
7. Deploy e testes de aceitação.

## Definition of done

- Funciona em instalação limpa.
- Possui `.env.example` atualizado.
- Possui documentação de configuração.
- Possui testes de sucesso e falha.
- Erros retornam mensagens úteis.
- Não expõe segredo ou dado de usuário.
- Possui limites de custo, tamanho e tempo.
- O README não promete o que o código ainda não faz.

## Comandos esperados

```text
Docker: docker compose up --build
API local: cd services/api && uvicorn main:app --reload --port 8000
Testes: cd services/api && python -m pytest -q
```

## Próxima tarefa recomendada

Criar o app Canva com o Starter Kit oficial, implementar seleção/preview de imagem e adicionar um cliente HTTP tipado para `/v1/image/*`. Depois integrar Fabric.js para desenho e edição local.

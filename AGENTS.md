# Instruções para agentes

## Missão

Construir um toolkit privado de edição de imagens para preparar produtos e encartes no Canva. O usuário é iniciante/intermediário em programação e precisa de instruções executáveis, mensagens claras e soluções compatíveis com Windows.

## Antes de alterar

1. Leia `README.md` e todos os documentos em `docs/` relevantes.
2. Confira o estado real do código; não trate roadmap como funcionalidade pronta.
3. Identifique se a alteração pertence ao `python-lab`, à API ou ao app Canva.
4. Preserve o trabalho de colaboradores e evite reescrever arquivos sem necessidade.

## Regras técnicas

- Python 3.11+ e Docker devem continuar suportados.
- Nunca comite `.env`, tokens, credenciais JSON ou modelos grandes.
- Não exponha chaves no frontend, logs, mensagens de erro ou exemplos.
- Valide MIME real, tamanho, pixels, dimensões de saída e parâmetros.
- Use nomes de arquivos aleatórios e não confie em nomes enviados pelo usuário.
- Operações demoradas devem migrar para jobs assíncronos.
- Providers externos precisam de timeout, retry limitado e erro explícito.
- Não envie imagens a serviços externos sem documentar isso.
- Preserve transparência, orientação EXIF e espaço de cor quando possível.
- Não alegue que OCR, remoção de fundo, Real-ESRGAN ou Canva estão prontos se não estiverem.

## Processo obrigatório

1. Planejar a alteração.
2. Implementar o menor conjunto coerente.
3. Adicionar testes de sucesso e falha.
4. Atualizar documentação e `.env.example`.
5. Executar testes e compilação.
6. Revisar diff, dependências e segredos.
7. Informar limitações e próximos passos.

## Critério de pronto

Uma tarefa só está pronta quando funciona em instalação limpa, possui tratamento de erro, testes, documentação, limites operacionais e não introduz segredo.

## Próxima prioridade

Preservar o deploy Tencent de baixo consumo, manter providers pagos/GPU
desativados por padrão e ampliar somente com evidência de capacidade, custo e
testes de rollback.

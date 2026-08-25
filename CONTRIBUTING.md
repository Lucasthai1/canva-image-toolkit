# Contribuindo

## Fluxo

1. Crie uma branch descritiva: `feat/nome`, `fix/nome` ou `docs/nome`.
2. Faça alterações pequenas.
3. Adicione ou atualize testes.
4. Execute `python -m pytest -q` na área alterada.
5. Atualize documentação.
6. Abra um Pull Request explicando o problema, solução e teste realizado.

## Convenção de commit

Use mensagens como:

```text
feat: add perspective transform
fix: reject oversized uploads
docs: improve Windows setup
test: cover invalid image input
```

## Não enviar

- `.env`.
- Chaves e tokens.
- Imagens de clientes.
- Modelos grandes.
- Dados pessoais.
- Dumps, logs ou outputs de teste.

## Checklist do PR

- [ ] Testes passam.
- [ ] Documentação atualizada.
- [ ] Sem segredos.
- [ ] Compatível com Windows ou limitação documentada.
- [ ] Tratamento de erro incluído.
- [ ] Nenhuma funcionalidade foi declarada pronta sem teste.

# Como atualizar o repositório Nora no GitHub (sem apagar a versão anterior)

**Repositório:** https://github.com/sarahbelchior/nora-case-study

1. Baixe o ZIP desta atualização e escolha **Extrair Tudo**.
2. Abra a pasta **Nora-Atualizacao-GitHub**. Ela inclui o README, as imagens e exemplos anteriores, além da nova pasta **demo** e dos testes.
3. Abra o repositório no GitHub e clique **Add file → Upload files**.
4. Para a **primeira atualização**, você pode selecionar os itens internos desta pasta e arrastá-los. O GitHub pode solicitar confirmação para substituir `README.md` e `.gitignore`. Confira o resumo e não envie a pasta externa.
5. Se o navegador não permitir substituir arquivos existentes durante o upload, envie primeiro os arquivos novos (`demo`, `tests`, `.github`, `requirements.txt`, `requirements-dev.txt`, `INICIAR_DEMO_WINDOWS.bat`, `.gitattributes`) e depois edite `README.md` no GitHub pelo lápis, colando o conteúdo deste ZIP.
6. Clique em **Commit changes** e abra a página principal do repositório.
7. Confira a presença de `demo/main.py`, `demo/static/`, `tests/test_demo.py` e do botão **Actions** na barra do GitHub.
8. Em **Actions**, verifique se o workflow `Testes Nora Demo` executou os testes. O resultado online depende do GitHub Actions estar habilitado.
9. Para testar no computador, siga as instruções do README: rode `INICIAR_DEMO_WINDOWS.bat`, depois visite `http://127.0.0.1:8000`.

**Não envie** arquivos `.env` com senhas, bancos de dados reais, fotos de usuários ou qualquer arquivo do seu projeto privado que não tenha sido revisado.

Esta atualização não precisa ser instalada dentro da Nora real. Ela serve **apenas ao repositório público** do portfólio.

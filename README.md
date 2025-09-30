1) mudar o .env

2) No shell:
export DEPLOY_ACTION="deploy"
export AUTH_ACTION="register"
./deploy_to_agentspace.sh

3) No App do Agentspace, faça uma pergunta para o agente. Caso não enontre dados, pergunte qual a URL devolvida. Analise se aponta corretamente para o app a ser buscado
4) Se a URL estiver correta e o log aponte que não houve erros, remova a autorização
export DEPLOY_ACTION="none"
export AUTH_ACTION="unregister"
./deploy_to_agentspace.sh

5) Adicione a autorização
export DEPLOY_ACTION="none"
export AUTH_ACTION="register"
./deploy_to_agentspace.sh

6) Teste. Se ainda não encontrar dados, remova a autorização, altere o nome do token de autorização no .env e adicione novamente

7) Se ainda não encontrar dados, repita o processo desde o começo:
- Remova a autorização, delete o agente no Agent Engine, faça o deploy do agente e adicione a autorização

Projeto feito com auxílio da IA, para monitorar resultados da Mega-Sena.

As APIs utilizadas são de domínio público, sugeridas pela IA;
Créditos e documentação das APIs:
Vanderson Guidi - https://github.com/guidi/loteria_api
Guto Alves - https://github.com/guto-alves/loterias-api

A intenção é o Script rodar no Agendador de Tarefas (Task Scheduler) do windows, usando o pythonw.exe; dessa forma ele executa sem abrir nenhuma janela e o que aparece para o "usuário" é somente a notificação com os resultados;

Todos os arquivos de controle ficam gravados na mesma pasta do script, para simplicidade.

O Script executa silenciosamente e apresenta uma notificação no Painel de Notificações do windows com os resultados.

PRE-REQUISITOS:
* ter o python versão 3.14.2 ou superior instalado e com todas as dependências também instaladas funcionando no seu ambiente;

INSTRUÇÕES DE INSTALAÇÃO:
1 - Criar uma pasta onde vai ficar o script e seus arquivos;
2 - baixar o arquivo Monitora MegaSena v2.pyw e salvar nessa pasta que vc criou;
3 - opcionalmente vc pode abrir o script no vscode e executar para ver se está tudo ok, ou executar direto com o python.
4 - agendar a execução do script da seguinte forma:
  * Criar uma tarefa no agendador de tarefas:
    * o trigger (gatilho) pode ser à sua escolha, eu agendei diário, as 19h;
    * ação: executar programa:
      * Programa: "[caminho do seu pythonw]\Python\bin\pythonw.exe"
      * Argumentos: "[caminho onde vc salvou o script]\Monitora MegaSena v2.pyw"
      * Iniciar em (isso é importante e tem que ter): [informe aqui o caminho onde vc salvou o script, sem nenhuma aspa]

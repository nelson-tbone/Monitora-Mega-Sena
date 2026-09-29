import os
import requests
from winotify import Notification
from datetime import datetime

# Configurações de arquivos locais para salvar o estado e ícone
# O script, rodando no Task Scheduler, precisa estar lá configurado o parâmetro "Start in" apontando para a pasta onde estão os arquivos de dados, caso contrário, ele não vai conseguir ler/escrever os arquivos.
CONTA_ARQUIVO = "MMS - contador_acumulado v2.txt"
ULTIMO_CONCURSO_ARQUIVO = "MMS - ultimo_concurso v2.txt"
ICONE_DO_APP = os.path.abspath("icone da caixa.ico") 

def ler_dados_caixa():
    # Lista de APIs alternativas para tentar em sequência caso uma falhe
    fontes = [
        {"url": "https://api.guidi.dev.br/loteria/megasena/ultimo", "tipo": "guidi"},
        {"url": "https://loteriascaixa-api.herokuapp.com/api/megasena/latest", "tipo": "guto-alves"} 
    ]
    
    for fonte in fontes:
        try:
            # Aumentamos o timeout para 25 segundos para evitar o erro 'Read timed out'
            response = requests.get(fonte["url"], timeout=25, verify=True)
            
            if response.status_code == 200:
                dados = response.json()
                
                if fonte["tipo"] == "guidi":
                    acumulado_val = dados.get("acumulado", False)
                    if isinstance(acumulado_val, bool):
                        acumulou = acumulado_val
                    else:
                        acumulou = str(acumulado_val).lower() == "sim"
                    numero_concurso = int(dados.get("numero", 0))
                    data_concurso = dados.get("dataApuracao", "")
                    resultados = dados.get("listaDezenas", dados.get("dezenas", []))
                    return acumulou, numero_concurso, resultados, data_concurso
                    
                elif fonte["tipo"] == "guto-alves":
                    # Fallback caso a primeira API falhe
                    acumulou = dados.get("acumulado", False)
                    numero_concurso = int(dados.get("concurso", 0))
                    data_concurso = dados.get("data", "")
                    resultados = dados.get("dezenas")
                    return acumulou, numero_concurso, resultados, data_concurso

        except (requests.exceptions.RequestException, Exception) as e:
            # Se der timeout ou erro em uma, o 'print' avisa e o 'for' pula para a próxima API da lista
            print(f"Aviso: Falha ao conectar na fonte {fonte['url']}. Tentando próxima... Erro: {e}")
            continue
            
    print("Erro crítico: Todas as fontes de dados falharam ou deram timeout.")
    return None, None, None, None

def carregar_valor(arquivo, padrao=0):
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f:
            conteudo = f.read().strip()
            return int(conteudo) if conteudo.isdigit() else padrao
    return padrao

def salvar_valor(arquivo, valor):
    with open(arquivo, "w") as f:
        f.write(str(valor))

def enviar_notificacao_windows(contador):
    notificacao = Notification(
        app_id="Monitor Mega-Sena", 
        icon=ICONE_DO_APP,
        title="Alerta Mega-Sena!",
        msg=f"A Mega-Sena acumulou pela {contador}ª vez consecutiva!", 
        duration="short"
    )
    notificacao.add_actions(label="Aposte!", launch="https://www.loteriasonline.caixa.gov.br/silce-web/#/mega-sena")
    notificacao.show()

def enviar_notificacao_windows_generica(mensagem):
    notificacao = Notification(
        app_id="Monitor Mega-Sena",
        icon=ICONE_DO_APP,
        title="Informações Mega-Sena!",
        msg=mensagem,
        duration="short"
    )
    notificacao.show()

def main():

    hoje = datetime.now()

    acumulou, numero_concurso, resultados, data_concurso = ler_dados_caixa()
    # formata o resultado para exibição na notificação
    resultados_texto = ", ".join(resultados)
    
    if acumulou is None:
        return  # Falha na leitura, encerra para tentar na próxima execução

    ultimo_concurso_salvo = carregar_valor(ULTIMO_CONCURSO_ARQUIVO)
    contador_atual = carregar_valor(CONTA_ARQUIVO)

    # mensagem de processamento genérico
    mensagem = (
        f"Concurso: {numero_concurso} ({data_concurso})\n"
        f"Resultado: {resultados_texto}\n"
        #f"Último concurso salvo: {ultimo_concurso_salvo}, "
        f"{f'🚨' if acumulou else f'🟢'} Acumulou: {f'Sim, {contador_atual} vezes' if acumulou else 'Não'}\n"
        f"Verificado em: {hoje.strftime('%d/%m/%Y %H:%M')};"
    )
    enviar_notificacao_windows_generica(mensagem)


    # Só processa se for um concurso novo que ainda não foi analisado
    if numero_concurso > ultimo_concurso_salvo:
        if acumulou:
            contador_atual += 1
            # Se acumulou pela terceira vez
            if contador_atual >= 3:
                enviar_notificacao_windows(contador_atual)
        else:
            # Se alguém ganhou, o ciclo de acúmulos consecutivos quebra e o contador reseta
            contador_atual = 0
        
        # Atualiza os arquivos locais com o status atual
        salvar_valor(CONTA_ARQUIVO, contador_atual)
        salvar_valor(ULTIMO_CONCURSO_ARQUIVO, numero_concurso)

# isso aqui serve para se o script for importado para outro script, ele não executa o main() automaticamente, 
# mas se for executado diretamente (via linha de comando ou agendado), ele chama a função main() e executa.
if __name__ == "__main__":
    main()

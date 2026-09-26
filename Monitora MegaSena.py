import os
import requests
from plyer import notification

# Configurações de arquivos locais para salvar o estado
CONTA_ARQUIVO = "MMS - contador_acumulado.txt"
ULTIMO_CONCURSO_ARQUIVO = "MMS - ultimo_concurso.txt"

def ler_dados_caixa():
    # Lista de APIs alternativas para tentar em sequência caso uma falhe
    fontes = [
        {"url": "https://api.guidi.dev.br/loteria/megasena/ultimo", "tipo": "guidi"},
        {"url": "https://loteriascaixa-api.herokuapp.com/api/megasena/latest", "tipo": "herokufix"} 
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
                    return acumulou, numero_concurso
                    
                elif fonte["tipo"] == "herokufix":
                    # Fallback caso a primeira API falhe
                    acumulou = dados.get("acumulado", False)
                    numero_concurso = int(dados.get("concurso", 0))
                    return acumulou, numero_concurso
                    
        except (requests.exceptions.RequestException, Exception) as e:
            # Se der timeout ou erro em uma, o 'print' avisa e o 'for' pula para a próxima API da lista
            print(f"Aviso: Falha ao conectar na fonte {fonte['url']}. Tentando próxima... Erro: {e}")
            continue
            
    print("Erro crítico: Todas as fontes de dados falharam ou deram timeout.")
    return None, None

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
    notification.notify(
        title="Alerta Mega-Sena!",
        message=f"A Mega-Sena acumulou pela {contador}ª vez consecutiva!",
        app_name="Monitor Mega-Sena",
        timeout=10  # Tempo que a notificação fica visível em segundos
    )

def main():
    acumulou, numero_concurso = ler_dados_caixa()
    
    if acumulou is None:
        return  # Falha na leitura, encerra para tentar na próxima execução

    ultimo_concurso_salvo = carregar_valor(ULTIMO_CONCURSO_ARQUIVO)
    contador_atual = carregar_valor(CONTA_ARQUIVO)

    # Só processa se for um concurso novo que ainda não foi analisado
    if numero_concurso > ultimo_concurso_salvo:
        if acumulou:
            contador_atual += 1
            # Se acumulou pela terceira vez (ou múltiplos de 3, caso queira continuar monitorando)
            if contador_atual == 3:
                enviar_notificacao_windows(contador_atual)
        else:
            # Se alguém ganhou, o ciclo de acúmulos consecutivos quebra e o contador reseta
            contador_atual = 0
        
        # Atualiza os arquivos locais com o status atual
        salvar_valor(CONTA_ARQUIVO, contador_atual)
        salvar_valor(ULTIMO_CONCURSO_ARQUIVO, numero_concurso)
    
if __name__ == "__main__":
    main()

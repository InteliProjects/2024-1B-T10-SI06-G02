from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
import threading
import schedule
import time
import pandas as pd
import io

# Initialize the Bolt app
app = App(token="")

def generate_markdown_graph(sentiments_data):
    max_value = max(sentiments_data.values())
    bar_length = 50  # Comprimento máximo da barra

    markdown = ""
    for label, value in sentiments_data.items():
        bar = "█" * int((value / max_value) * bar_length)
        markdown += f"{label} | {bar} {value}\n"

    return markdown

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # Dados para o gráfico (substitua por dados reais)
        sentiments_data = requests.get("http://localhost:5000/infos/graph-infos/1").json()
        
        lastest_tweet = requests.get("http://localhost:5000/infos/last_tweets").json()["last_tweets"][0]
        lastest_tweet = {
            "text": lastest_tweet[1],
            "date": lastest_tweet[3],
            "prediction": "Positivo" if lastest_tweet[2] == 1 else "Negativo",
        }
        
        markdown_graph = generate_markdown_graph(sentiments_data)

        home_view = {
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Análise de Sentimentos :bar_chart:",
                    }
                },
                { 
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":wave: Bem-vindo(a)! :wave:\n\nPara começar, digite `/predict` seguido de um texto para obter uma previsão de sentimento. Por exemplo, `/predict Bom dia!`"
                    },
                },
                {"type": "divider"},
                {  # Gráfico de barras com formatação aprimorada
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 Análise de Sentimentos:*\n`{markdown_graph}`"
                    }
                },
                {"type": "divider"},
                {  # Último Tweet com estilo e imagem do usuário
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Último Tweet Analisado:*\n{lastest_tweet['text']}\n\n*Data:* {lastest_tweet['date']}\n*Previsão:* {lastest_tweet['prediction']}{':large_green_circle:' if lastest_tweet['prediction'] == 'Positivo' else ':large_red_circle:'}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Ver no Twitter"},
                            "url": f"https://twitter.com/"
                        }
                    ]
                }
            ]
        }

        client.views_publish(user_id=event["user"], view=home_view)

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

        client.views_publish(user_id=event["user"], view=home_view)
        
@app.command("/predict-csv")
def predict_csv_command(ack, say, command):
    """
    Manipulador de comando para o comando /predict-csv.

    Args:
        ack (ack): Uma função para confirmar a execução do comando.
        say (callable): Uma função para enviar uma mensagem de volta para o canal do Slack.
        command (dict): O payload do comando contendo informações sobre o comando.

    Funcionalidade:
        1. Extrai o texto do comando.
        2. Envia uma solicitação POST para uma API local com o texto para obter uma previsão.
        3. Lida com a resposta da API:
            a. Se for bem-sucedida, analisa a resposta JSON e envia uma mensagem para o canal do Slack com a previsão.
            b. Se a resposta não puder ser analisada como JSON, envia uma mensagem de erro para o canal do Slack.
        4. Lida com quaisquer exceções de solicitação imprimindo o erro e enviando uma mensagem de erro para o canal do Slack.
    """

    ack()
    #pegar o arquivo csv enviado pelo usuário
    file = command["files"][0]
    
    # Enviar solicitação para limpeza de dados
    url_predict = "http://localhost:5000/process/csv"
    
    request_predict = requests.post(url_predict, files={"file": (file["name"], file["url_private"])})
    request_predict.raise_for_status()
    response_predict_file = request_predict.content
    
    analyse = pd.read_csv(io.BytesIO(response_predict_file))
    
    num_positive = len(analyse[analyse["sentiment"] == 1])
    num_negative = len(analyse[analyse["sentiment"] == 0])
    
    text = f"Análise de Sentimentos do arquivo CSV:\n\n:large_green_circle: *Sentimentos Positivos:* {num_positive}\n:large_red_circle: *Sentimentos Negativos:* {num_negative}"
    
    say(text)
    #enviar arquivo csv com as previsões
    say(f"Previsões do arquivo CSV:")
    say(file=response_predict_file, blocks=[])
    say(":white_check_mark: *Concluído!*")
    
    # Verificar o resultado da previsão

@app.command("/predict")
def predict_command(ack, say, command):
    """
    Manipulador de comando para o comando /predict.

    Args:
        ack (ack): Uma função para confirmar a execução do comando.
        say (callable): Uma função para enviar uma mensagem de volta para o canal do Slack.
        command (dict): O payload do comando contendo informações sobre o comando.

    Funcionalidade:
        1. Extrai o texto do comando.
        2. Envia uma solicitação POST para uma API local com o texto para obter uma previsão.
        3. Lida com a resposta da API:
            a. Se for bem-sucedida, analisa a resposta JSON e envia uma mensagem para o canal do Slack com a previsão.
            b. Se a resposta não puder ser analisada como JSON, envia uma mensagem de erro para o canal do Slack.
        4. Lida com quaisquer exceções de solicitação imprimindo o erro e enviando uma mensagem de erro para o canal do Slack.
    """

    ack()
    text = command["text"]
    # Quebrar text a cada vírgula
    texts = text.split(",")

    for t in texts:
        t = t.strip()
        say(f"*Analisando:* `{t}`")

        try:
            # Enviar solicitação para limpeza de dados
            request_clean = requests.post("http://localhost:5000/clean_data/tweet", json={"data": t})
            request_clean.raise_for_status()
            response_clean = request_clean.json()
            cleaned_data = response_clean["text"]

            # Enviar solicitação para vetorização
            request_vetor = requests.post("http://localhost:5000/vectorize/vectorize", json={"text": cleaned_data})
            request_vetor.raise_for_status()
            response_vetor = request_vetor.json()
            vetor = response_vetor["vector"]

            # Enviar solicitação para previsão
            request_predict = requests.post("http://localhost:5000/predict/predict", json={"data": vetor})
            request_predict.raise_for_status()
            response_predict = request_predict.json()
            
            # Verificar o resultado da previsão
            if response_predict["predictions"][0] == 1:
                sentiment = "Sentimento Positivo :large_green_circle:"
            else:
                sentiment = ":large_red_circle: Sentimento Negativo!"
            
            say(f"Resultado: {sentiment}")
            
        except requests.exceptions.RequestException as e:
            say(f":x: *Erro ao processar:* `{t}`\n> {str(e)}")
            break
    say(":white_check_mark: *Concluído!*")

# Função para chamar a API periodicamente e enviar a mensagem para o canal
def fetch_and_notify():
    try:
        response = requests.get("http://localhost:5000/infos/alert")
        response.raise_for_status()
        data = response.json()
        print(data)
        if data["alert"]:
            last_tweets = requests.get("http://localhost:5000/infos/last_tweets")
            last_tweets.raise_for_status()
            last_tweets = last_tweets.json()["last_tweets"]
            print(last_tweets)
            last3tweets = {
                "tweet1":{
                    "text": last_tweets[0][1],
                    "sentiment": "Positive" if last_tweets[0][2] == 1 else "Negative"
                },
                "tweet2":{
                    "text": last_tweets[1][1],
                    "sentiment": "Positive" if last_tweets[1][2] == 1 else "Negative"
                },
                "tweet3":{
                    "text": last_tweets[2][1],
                    "sentiment": "Positive" if last_tweets[2][2] == 1 else "Negative"
                }
            }
            
            print(last3tweets)

            text = (
    f":exclamation::exclamation: Negative comments have increased by {data['increase']*100:.2f}% in the last 24 hours! :exclamation::exclamation:\n"
    f"These are the last 3 comments:\n"
    f"{last3tweets['tweet1']['text']} - {last3tweets['tweet1']['sentiment']} {':red_circle:' if last3tweets['tweet1']['sentiment'] == 'Negative' else ':large_green_circle:'}\n"
    f"{last3tweets['tweet2']['text']} - {last3tweets['tweet2']['sentiment']} {':red_circle:' if last3tweets['tweet2']['sentiment'] == 'Negative' else ':large_green_circle:'}\n"
    f"{last3tweets['tweet3']['text']} - {last3tweets['tweet3']['sentiment']} {':red_circle:' if last3tweets['tweet3']['sentiment'] == 'Negative' else ':large_green_circle:'}"
)
            print(text)
            #postar mensagen no canal #alert
            app.client.chat_postMessage(channel="alertas", text=text)
    except Exception as e:
        print(f"Erro ao chamar a API ou enviar mensagem: {e}")

# Agendar a chamada da API a cada 5 minutos
schedule.every(0.5).minutes.do(fetch_and_notify)

# Função para rodar o agendador em um thread separado
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Iniciar o agendador em um thread separado
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    # Iniciar o bot do Slack no thread principal
    SocketModeHandler(app, "").start()

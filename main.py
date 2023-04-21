import requests
from bs4 import BeautifulSoup
import re
import datetime
import schedule
import time
import os

# Configurações do bot e do canal do Telegram
bot_token = '6029369646:AAEPi2j93Vc9-PnpbSniOrBlM5O2ku1vSuM'
chat_id = '-1001942463758'

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message}
    requests.post(url, data=data)

def scrape_data():
    url = 'https://www.aceodds.com/pt/bet365-transmissao-ao-vivo/futebol/e-soccer-battle-8-minutos-de-jogo.html'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Encontra a div com a classe table-responsive-sm
    table_div = soup.find('div', {'class': 'table-responsive-sm'})

    # Encontra a tabela a partir da div
    table = table_div.find('table', {'class': 'table'})

    # Extrai os dados da tabela e formata para exibição
    current_time = datetime.datetime.now()
    for row in table.findAll('tr'):
        cells = row.findAll('td')
        # Verifica se a linha tem o número correto de células
        if len(cells) == 2:
            time_str = cells[0].text.strip()
            time = datetime.datetime.strptime(time_str, '%H:%M')
            time = datetime.datetime.combine(datetime.date.today(), time.time())
            if time > current_time and (time - current_time).total_seconds() < 10 * 60:
                link = 'https://www.bet365.com/#/AC/B1/C1/D1002/E71755867/G40/'  # Link estático
                teams_raw = cells[1].text.strip().split(' x ')
                teams = [re.sub(r'\bEsports\b', '', team).strip() for team in teams_raw]
                players_raw = cells[1].find('a')['title'].split(' - ')[-1].split(' x ')
                players = [re.sub(r'[^()]*\(|\)[^()]*', '', player).strip() for player in players_raw]
                league = cells[1].find('a')['title'].split(' - ')[0].split(': ')[-1]

                # Formata os dados como mensagem para o Telegram
                message = f"🏟️ LIGA: ESB / ECF (FIFA 8 minutos) - {league}\n🎮 Times: {teams[0]} x {teams[1]}\n🙍‍♂️ Players: {players[0]} x {players[1]}\n⌚ Horário: {time_str}\n🟩 Link: {link}"

                # Envia a mensagem para o Telegram
                send_telegram_message(message)

# Roda o scraper uma vez antes de começar o schedule
scrape_data()

# Agendamento do scraper para rodar a cada 5 minutos
schedule.every(5).minutes.do(scrape_data)

while True:
    schedule.run_pending()
    time.sleep(1)

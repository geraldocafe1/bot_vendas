import requests
from bs4 import BeautifulSoup
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

# CONFIGURAÇÕES DO GERALDO
TOKEN = "8775062096:AAGk-Rk_S_WMrXhzYulRKSSHr8FcSXHnpLk"
CHAT_ID = 1528800333

async def buscar_e_postar():
    bot = Bot(token=TOKEN)
    
    # URL de exemplo (Página de promoções do dia)
    # Vamos usar o 'Pelando' que é um agregador público
    url_fonte = "https://www.pelando.com.br/recente"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    print("🔍 Caçando ofertas...")
    response = requests.get(url_fonte, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # No Web Scraping, procuramos as "tags" onde estão os produtos
    # O código abaixo busca os blocos de produtos (ajustado para o padrão do site)
    ofertas = soup.find_all('article', limit=3) # Pega as 3 primeiras ofertas

    for item in ofertas:
        try:
            # Extraindo dados básicos
            titulo = item.find('a', class_='ce-thread-title').text.strip()
            preco = item.find('span', class_='ce-thread-price').text.strip()
            link_original = "https://www.pelando.com.br" + item.find('a', class_='ce-thread-title')['href']
            
            # FORMATANDO A MENSAGEM PARA O GERALDO
            # DICA: Aqui você colocaria sua lógica de converter para LINK DE AFILIADO
            link_afiliado = f"https://seusite.com/afiliado?url={link_original}"

            mensagem = (
                f"🔥 **OFERTA ENCONTRADA PELO CAÇADOR** 🔥\n\n"
                f"📦 **PRODUTO:** {titulo}\n"
                f"💰 **PREÇO:** {preco}\n\n"
                f"🛒 [CLIQUE AQUI PARA VER A PROMOÇÃO]({link_afiliado})\n\n"
                f"☕ *Enviado por @cafe_jc_bot*"
            )

            print(f"✅ Postando: {titulo}")
            await bot.send_message(chat_id=CHAT_ID, text=mensagem, parse_mode=ParseMode.MARKDOWN)
            
            # Espera 5 segundos entre uma postagem e outra para o Telegram não bloquear
            await asyncio.sleep(5)

        except Exception as e:
            print(f"❌ Erro ao processar item: {e}")

if __name__ == "__main__":
    asyncio.run(buscar_e_postar())
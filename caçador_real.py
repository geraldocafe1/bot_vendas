import requests
from bs4 import BeautifulSoup
import asyncio
from telegram import Bot

# CONFIGURAÇÕES DO GERALDO
TOKEN = "8775062096:AAGk-Rk_S_WMrXhzYulRKSSHr8FcSXHnpLk"
CHAT_ID = 1528800333

def buscar_dados_mercado_livre(url_produto):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url_produto, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraindo Título e Preço reais do Mercado Livre
        titulo = soup.find('h1', class_='ui-pdp-title').text.strip()
        
        # O Mercado Livre divide o preço em frações
        parte_inteira = soup.find('span', class_='andes-money-amount__fraction').text
        preco_final = f"R$ {parte_inteira}"
        
        # Pega a imagem do produto
        imagem = soup.find('img', class_='ui-pdp-image')['src']
        
        return titulo, preco_final, imagem
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return None, None, None

async def postar_oferta_real(url_ml):
    bot = Bot(token=TOKEN)
    titulo, preco, imagem = buscar_dados_mercado_livre(url_ml)

    if titulo:
        # AQUI É ONDE VOCÊ COLOCARIA SEU LINK DE AFILIADO
        link_afiliado = f"{url_ml}?ref=SEU_ID_GERALDO" 

        mensagem = (
            f"<b>🔥 OFERTA ENCONTRADA!</b>\n\n"
            f"📦 {titulo}\n"
            f"💰 <b>Por apenas: {preco}</b>\n\n"
            f'<a href="{link_afiliado}">🛒 CLIQUE AQUI PARA COMPRAR</a>\n\n'
            f"👉 <i>Monitorado por @cafe_jc_bot</i>"
        )

        await bot.send_photo(chat_id=CHAT_ID, photo=imagem, caption=mensagem, parse_mode="HTML")
        print("🚀 Oferta real enviada para o Telegram!")
    else:
        print("❌ Não consegui ler os dados desse link.")

if __name__ == "__main__":
    # COLE UM LINK DE QUALQUER PRODUTO DO MERCADO LIVRE ABAIXO PARA TESTAR
    url_teste = "https://www.mercadolivre.com.br/apple-iphone-15-128-gb-preto/p/MLB27375253"
    asyncio.run(postar_oferta_real(url_teste))
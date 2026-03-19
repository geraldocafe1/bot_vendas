import requests
from bs4 import BeautifulSoup
import asyncio
from telegram import Bot

# --- CONFIGURAÇÕES DO GERALDO ---
TOKEN = "8775062096:AAGk-Rk_S_WMrXhzYulRKSSHr8FcSXHnpLk"
CHAT_ID = 1528800333
AMAZON_TAG = "achadodamamy-20"

async def cacar_ofertas_amazon():
    bot = Bot(token=TOKEN)
    
    # URL de Ofertas do Dia (Geralmente mais estável para robôs)
    url_busca = "https://www.amazon.com.br/gp/goldbox"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9"
    }

    print("🔎 Verificando ofertas quentes na Amazon...")
    
    try:
        response = requests.get(url_busca, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Procuramos por todos os "cards" de produtos na página de ofertas
        # Usamos um seletor mais amplo para evitar o erro de 'NoneType'
        produtos = soup.find_all('div', {'data-testid': 'grid-desktop-card'}, limit=5)

        if not produtos:
            print("⚠️ Amazon bloqueou a leitura ou não há ofertas agora. Tentando outro seletor...")
            # Seletor alternativo para a página de Bestsellers
            produtos = soup.select('div[id*="gridItemRoot"]', limit=5)

        for produto in produtos:
            try:
                # Buscando os dados com 'if' para evitar o erro .text
                tag_titulo = produto.find('h2') or produto.select_one('div[class*="title"]')
                tag_preco = produto.select_one('span[class*="price"]')
                tag_link = produto.find('a', href=True)
                tag_img = produto.find('img')

                if tag_titulo and tag_preco and tag_link:
                    titulo = tag_titulo.text.strip()
                    preco = tag_preco.text.strip()
                    link_raw = tag_link['href']
                    
                    # Limpa o link e coloca o seu ID de afiliado
                    link_limpo = link_raw.split('?')[0]
                    if not link_limpo.startswith('http'):
                        link_limpo = "https://www.amazon.com.br" + link_limpo
                    
                    link_afiliado = f"{link_limpo}?tag={AMAZON_TAG}"
                    imagem = tag_img['src'] if tag_img else ""

                    mensagem = (
                        f"🌟 <b>OFERTA DA AMAZON!</b> 🌟\n\n"
                        f"📦 {titulo[:80]}...\n"
                        f"💰 <b>{preco}</b>\n\n"
                        f'🛒 <a href="{link_afiliado}">CLIQUE AQUI PARA COMPRAR</a>\n\n'
                        f"👉 <i>Enviado por @cafe_jc_bot</i>"
                    )

                    print(f"✅ Postando: {titulo[:30]}...")
                    await bot.send_photo(chat_id=CHAT_ID, photo=imagem, caption=mensagem, parse_mode="HTML")
                    await asyncio.sleep(10)
            except Exception as e:
                print(f"⏭️ Pulando um item devido a erro: {e}")
                continue

    except Exception as e:
        print(f"❌ Erro crítico na busca: {e}")

if __name__ == "__main__":
    asyncio.run(cacar_ofertas_amazon())
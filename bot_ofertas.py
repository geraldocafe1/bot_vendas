import streamlit as st
import google.generativeai as genai
import os
import asyncio
import urllib.parse
from telegram import Bot
from dotenv import load_dotenv

# --- CARREGAR CONFIGURAÇÕES ---
load_dotenv()
CHAVE_GEMINI = os.getenv("GEMINI_API_KEY")
TOKEN_TELEGRAM = os.getenv("TELEGRAM_TOKEN")
CHAT_ID_TELEGRAM = os.getenv("TELEGRAM_CHAT_ID")
ID_AMAZON_PADRAO = os.getenv("AMAZON_TAG")

# Configuração da IA Gemini
if CHAVE_GEMINI:
    genai.configure(api_key=CHAVE_GEMINI)
    model = genai.GenerativeModel('gemini-2.5-flash') 
else:
    st.error("❌ Erro: GEMINI_API_KEY não encontrada no .env")

# --- FUNÇÕES DE APOIO ---

def identificar_e_converter(url, id_ama, id_ml, id_sho, id_mag):
    if not url: return "Aguardando...", ""
    if not url.startswith('http'): url = 'https://' + url
    u = url.lower()
    if "amazon.com.br" in u:
        link = url.split("?")[0]
        return "Amazon", f"{link}?tag={id_ama}"
    elif "mercadolivre.com.br" in u or "meli.la" in u:
        return "Mercado Livre", f"{url}?ref={id_ml}" if id_ml else url
    elif "shopee.com.br" in u:
        return "Shopee", f"{url}?smtt=0.0.{id_sho}" if id_sho else url
    elif "magazineluiza.com.br" in u:
        return "Magalu", f"{url}?partner_id={id_mag}" if id_mag else url
    return "Loja Desconhecida", url

async def enviar_telegram(texto):
    bot = Bot(token=TOKEN_TELEGRAM)
    await bot.send_message(chat_id=CHAT_ID_TELEGRAM, text=texto, parse_mode="Markdown")

# --- INTERFACE ---
st.set_page_config(page_title="Geraldo Ofertas Pro", layout="wide", page_icon="💰")

with st.sidebar:
    st.title("⚙️ Configurações")
    id_ama = st.text_input("ID Amazon", value=ID_AMAZON_PADRAO)
    id_ml = st.text_input("ID Mercado Livre", placeholder="Seu ID ML")
    st.info(f"📍 Grupo Telegram fixado: {CHAT_ID_TELEGRAM}")

st.title("🧙‍♂️ Assistente de Vendas Inteligente")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🛒 Dados da Oferta")
    url_input = st.text_input("Link do Produto:")
    preco_input = st.text_input("Preço (R$):")
    contexto_input = st.text_area("Destaques (Frete, Parcelamento, etc):")
    
    loja, link_final = identificar_e_converter(url_input, id_ama, "", "", "")
    
    if url_input:
        st.success(f"✅ Loja: {loja}")

with col2:
    st.subheader("📝 Post Gerado")
    
    if st.button("✨ Gerar Texto com IA"):
        if not url_input or not preco_input:
            st.warning("⚠️ Preencha o link e o preço!")
        else:
            with st.spinner("IA escrevendo..."):
                prompt = f"Crie um post estilo 'Achadinho'. Loja: {loja}, Preço: R$ {preco_input}, Link: {link_final}. Contexto: {contexto_input}. Use muitos emojis e negritos."
                response = model.generate_content(prompt)
                st.session_state['post_resultado'] = response.text

    if 'post_resultado' in st.session_state:
        post_editavel = st.text_area("Edite se necessário:", value=st.session_state['post_resultado'], height=250)
        
        # BOTÕES DE ENVIO
        c1, c2, c3 = st.columns(3)
        
        with c1:
            if st.button("✈️ Telegram"):
                asyncio.run(enviar_telegram(post_editavel))
                st.toast("Enviado para o Telegram!")

        with c2:
            # WhatsApp Link
            texto_zap = urllib.parse.quote(post_editavel)
            link_zap = f"https://api.whatsapp.com/send?text={texto_zap}"
            st.markdown(f'<a href="{link_zap}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:8px 15px; border-radius:5px; width:100%; cursor:pointer;">🟢 WhatsApp</button></a>', unsafe_allow_html=True)

        with c3:
            if st.button("🗑️ Limpar"):
                del st.session_state['post_resultado']
                st.rerun()
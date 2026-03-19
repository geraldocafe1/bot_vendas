import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import os
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Geraldo Ofertas Pro", 
    page_icon="🚀", 
    layout="wide"
)

# --- CSS PARA BOTÕES E ESTILO ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .whatsapp-button {
        display: inline-block;
        background-color: #25D366;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SEGURANÇA E CONFIGURAÇÕES (Secrets) ---
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    TOKEN_TELEGRAM = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID_TELEGRAM = st.secrets["TELEGRAM_CHAT_ID"]
except:
    # Backup para rodar no seu computador (Local)
    CHAVE_GEMINI = os.getenv("GEMINI_API_KEY")
    TOKEN_TELEGRAM = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID_TELEGRAM = os.getenv("TELEGRAM_CHAT_ID")

if CHAVE_GEMINI:
    genai.configure(api_key=CHAVE_GEMINI)
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- FUNÇÕES DE ENVIO ---
def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID_TELEGRAM, "text": mensagem, "parse_mode": "Markdown"}
    return requests.post(url, json=payload)

def gerar_link_whatsapp(texto):
    texto_codificado = urllib.parse.quote(texto)
    return f"https://api.whatsapp.com/send?text={texto_codificado}"

# --- FUNÇÃO DE AFILIADOS ---
def gerar_link_afiliado(link_original, id_amazon, id_magalu, id_shopee):
    try:
        if "amazon.com.br" in link_original:
            char = "&" if "?" in link_original else "?"
            return f"{link_original}{char}tag={id_amazon}"
        
        elif "magazineluiza.com.br" in link_original:
            if "/p/" in link_original:
                # Extrai o código do produto entre /p/ e a próxima barra ou interrogação
                partes = link_original.split("/p/")[1].split("/")
                codigo_prod = partes[0].split("?")[0]
                return f"https://www.magazinevoce.com.br/{id_magalu}/p/{codigo_prod}/"
        
        elif "shopee.com.br" in link_original:
            char = "&" if "?" in link_original else "?"
            return f"{link_original}{char}smtt=0.0.{id_shopee}"
            
        return link_original
    except:
        return link_original

# --- SIDEBAR (PAINEL LATERAL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=60)
    st.title("Configurações")
    st.divider()
    
    st.subheader("🆔 IDs de Afiliado")
    id_amz = st.text_input("ID Amazon", value="achadodamamy-20")
    id_mgl = st.text_input("ID Magalu", value="magazineachadodamammy")
    id_shp = st.text_input("ID Shopee", value="18310470275")
    
    st.divider()
    st.caption("Geraldo Ofertas Pro v3.5")

# --- CONTEÚDO PRINCIPAL ---
st.title("🤖 Central de Vendas Inteligente")

tab1, tab2 = st.tabs(["📝 Gerador de Posts", "🕵️ Vigia de Preços (Beta)"])

with tab1:
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("📦 Dados do Produto")
        with st.container(border=True):
            link_input = st.text_input("Link do Produto (Cole aqui):")
            preco_input = st.text_input("Preço de Oferta (R$):", placeholder="Ex: 99,90")
            destaques = st.text_area("Destaques (Frete, Cupons, Parcelas):")
            
            if st.button("✨ GERAR POST COM IA", type="primary"):
                if link_input and preco_input:
                    link_final = gerar_link_afiliado(link_input, id_amz, id_mgl, id_shp)
                    
                    prompt = f"""
                    Crie um post para Telegram/WhatsApp.
                    Produto: {link_input} (use o link final: {link_final})
                    Preço: R$ {preco_input}
                    Destaques: {destaques}
                    Estilo: Vendedor influenciador, curto, emojis, gatilhos de urgência.
                    """
                    
                    with st.spinner("IA criando sua oferta..."):
                        response = model.generate_content(prompt)
                        st.session_state['post_pronto'] = response.text
                else:
                    st.warning("⚠️ Preencha o link e o preço!")

    with col2:
        st.subheader("📱 Resultado do Post")
        if 'post_pronto' in st.session_state:
            texto_editavel = st.text_area("Revise seu texto:", value=st.session_state['post_pronto'], height=300)
            
            # --- BOTÃO TELEGRAM ---
            if st.button("✈️ Enviar para o Telegram Agora"):
                res = enviar_telegram(texto_editavel)
                if res.status_code == 200:
                    st.success("✅ Post enviado ao seu grupo!")
                else:
                    st.error("❌ Erro ao enviar para o Telegram.")
            
            # --- BOTÃO WHATSAPP ---
            link_zap = gerar_link_whatsapp(texto_editavel)
            st.markdown(f'<a href="{link_zap}" target="_blank" class="whatsapp-button">🟢 Abrir no WhatsApp</a>', unsafe_allow_html=True)
            
            if st.button("🗑️ Limpar e Criar Outro"):
                del st.session_state['post_pronto']
                st.rerun()
        else:
            st.info("Preencha os dados ao lado para ver a mágica acontecer aqui!")

with tab2:
    st.subheader("🕵️ Monitoramento em Tempo Real")
    st.info("Esta aba está sendo preparada para monitorar preços automaticamente.")
    st.text_input("Link para vigiar futuramente:")
    st.button("Vigiar", disabled=True)
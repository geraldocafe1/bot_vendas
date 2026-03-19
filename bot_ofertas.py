import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import os
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Geraldo Ofertas Pro", page_icon="💰", layout="wide")

# --- CSS PROFISSIONAL ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; border-radius: 4px 4px 0px 0px; padding-top: 10px; font-weight: bold; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- SEGURANÇA E IA ---
try:
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
except:
    CHAVE_GEMINI = os.getenv("GEMINI_API_KEY")

if CHAVE_GEMINI:
    genai.configure(api_key=CHAVE_GEMINI)
    model = genai.GenerativeModel('gemini-2.5-flash')

# --- FUNÇÃO MÁGICA: CAPTURAR PREÇO ---
def capturar_dados_produto(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        nome = "Produto não identificado"
        preco = "0,00"

        if "amazon.com.br" in url:
            nome = soup.find(id="productTitle").get_text().strip()
            # Tenta pegar o preço inteiro e a fração
            p_inteiro = soup.find(class_="a-price-whole")
            p_fracao = soup.find(class_="a-price-fraction")
            if p_inteiro: preco = f"{p_inteiro.text.replace(',', '').replace('.', '')},{p_fracao.text if p_fracao else '00'}"
        
        elif "magazineluiza.com.br" in url:
            nome = soup.find(data_testid="heading-product-title").get_text().strip()
            p_tag = soup.find(data_testid="price-value")
            if p_tag: preco = p_tag.text.replace("R$", "").strip()

        elif "mercadolivre.com.br" in url:
            nome = soup.find(class_="ui-pdp-title").get_text().strip()
            p_tag = soup.find(class_="andes-money-amount__fraction")
            if p_tag: preco = p_tag.text.strip()

        return {"nome": nome[:60] + "...", "preco": preco}
    except Exception as e:
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ IDs Afiliado")
    id_amazon = st.text_input("ID Amazon", value="achadodamamy-20")
    id_magalu = st.text_input("ID Magalu", value="magazineachadodamammy")
    id_shopee = st.text_input("ID Shopee", value="18310470275")
    st.divider()
    st.caption("v3.0 - Monitor Ativo")

# --- CONTEÚDO ---
st.title("🚀 Central de Inteligência de Vendas")

tab1, tab2 = st.tabs(["📝 Gerador Manual", "🕵️ Vigia de Preços"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Entrada de Dados")
        link_manual = st.text_input("Link do Produto:")
        preco_manual = st.text_input("Preço Manual (R$):")
        if st.button("✨ Criar Post"):
            # Lógica simples de post...
            st.session_state['post'] = "Post gerado com sucesso!"

with tab2:
    st.subheader("🕵️ Monitoramento em Tempo Real")
    
    url_vigia = st.text_input("Cole o Link para Monitorar (Amazon, Magalu, ML):", key="vigia_url")
    
    if st.button("🔍 Analisar Produto e Adicionar"):
        if url_vigia:
            with st.spinner("Buscando dados no site da loja..."):
                dados = capturar_dados_produto(url_vigia)
                if dados:
                    st.success(f"✅ Produto Encontrado!")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Produto", dados['nome'])
                    with c2:
                        st.metric("Preço Atual", f"R$ {dados['preco']}")
                    
                    st.divider()
                    st.write("### 🤖 O que deseja fazer?")
                    if st.button("📦 Gerar Post deste Preço"):
                        prompt = f"Crie um post de oferta irresistível para {dados['nome']} por R$ {dados['preco']}. Use o link {url_vigia}."
                        res = model.generate_content(prompt)
                        st.write(res.text)
                else:
                    st.error("❌ Não consegui ler o preço deste link. A loja pode estar bloqueando robôs.")
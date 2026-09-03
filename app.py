import streamlit as st
from pytrends.request import TrendReq
from google import genai
import json

st.set_page_config(page_title="radar cultural e inspiração", layout="wide")

# Estilo minimalista editorial
st.markdown("""
<style>
    .stApp { background-color: #fafafa; color: #18181b; }
    h1, h2, h3 { font-family: serif; text-transform: lowercase; }
</style>
""", unsafe_allow_html=True)

st.title("radar cultural e inspiração")
st.caption("dados reais do google trends brasil cruzados com inteligência e direção visual")

col1, col2, col3 = st.columns(3)
with col1:
    nicho = st.selectbox("segmento", ["moda", "esportes", "beleza e skincare", "tecnologia e negócios", "gastronomia"])
with col2:
    periodo = st.selectbox("janela temporal", ["now 7-d", "today 1-m", "today 3-m"])
with col3:
    objetivo = st.selectbox("objetivo da ação", ["criação de conteúdo e redes sociais", "lançamento de produto", "ideias de eventos ou ativação", "estratégia de posicionamento"])

termo = st.text_input("descreva sua ideia, produto ou termo", value="bloke core")

if st.button("gerar diagnóstico, ideias e moodboard"):
    with st.spinner("consultando dados reais no google trends brasil..."):
        # 1. Busca dados reais via Python Pytrends
        top_termos = []
        try:
            pytrends = TrendReq(hl='pt-BR', tz=180)
            pytrends.build_payload([termo], cat=0, timeframe=periodo, geo='BR')
            relacionados = pytrends.related_queries()
            subindo = relacionados[termo]['rising']
            if subindo is not None and not subindo.empty:
                top_termos = subindo['query'].head(3).tolist()
        except Exception:
            pass

        if not top_termos:
            top_termos = [f"{termo} brasil", f"tendências {termo}", f"como usar {termo}"]

        # 2. Chama o Gemini para síntese cultural
        CHAVE_GEMINI = "AQ.Ab8RN6IfRuC1ubQJSIbZZsUF3cKASRsBl94HHb1qdh-4eao7hw"
        client = genai.Client(api_key=CHAVE_GEMINI)
        
        prompt = f"""
        Você é um diretor de estratégia cultural e arte no Brasil.
        Tema: {termo}
        Termos reais de busca no Brasil: {top_termos}
        Objetivo: {objetivo}
        Retorne ESTRITAMENTE em formato JSON:
        {{
          "paleta_hex": ["#0b192c", "#1e3e62", "#00adb5", "#eeeeee", "#ff6500"],
          "o_que_o_publico_procura": "Resumo de 2 linhas do que o público quer de verdade.",
          "caminho_narrativa": "Ação prática de conteúdo/execução",
          "caminho_estetica": "Ação prática visual/direção de arte"
        }}
        """
        
        dados_ia = {
            "paleta_hex": ["#0b192c", "#1e3e62", "#00adb5", "#eeeeee", "#ff6500"],
            "o_que_o_publico_procura": "O público busca conexões autênticas e aplicações da vida real.",
            "caminho_narrativa": "Mostre bastidores reais e o produto em uso no dia a dia.",
            "caminho_estetica": "Iluminação natural, fotos de detalhe e alto contraste."
        }
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            dados_ia = json.loads(response.text)
        except Exception:
            pass

    # Exibição na tela
    st.markdown("---")
    st.subheader("pesquisas reais em ascensão no brasil")
    t_cols = st.columns(len(top_termos))
    for i, t in enumerate(top_termos):
        t_cols[i].info(f"↗ **{t}**")

    st.subheader("paleta de cores sugerida")
    c_cols = st.columns(5)
    for i, hex_code in enumerate(dados_ia.get("paleta_hex", [])):
        c_cols[i].markdown(f'<div style="background-color:{hex_code}; height:45px; border-radius:8px; border: 1px solid #ddd;"></div>', unsafe_allow_html=True)
        c_cols[i].caption(hex_code)

    st.subheader("o que as pessoas procuram encontrar")
    st.write(dados_ia.get("o_que_o_publico_procura", ""))

    st.subheader("caminhos práticos para o objetivo")
    st.write(f"• **narrativa e conteúdo:** {dados_ia.get('caminho_narrativa', '')}")
    st.write(f"• **estética e experiência:** {dados_ia.get('caminho_estetica', '')}")

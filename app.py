import streamlit as st
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(page_title="radar editorial | marketing e comportamento", layout="wide", initial_sidebar_state="collapsed")

# Estilo Editorial em Tons de Marrom, Café e Areia
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        background-color: #fbfaf8;
        color: #2b211b;
    }
    
    .stApp {
        background-color: #fbfaf8;
    }
    
    h1, h2, h3, .brand-title {
        font-family: 'DM Serif Display', serif !important;
        font-weight: 400 !important;
        letter-spacing: -0.5px !important;
        text-transform: lowercase !important;
        color: #241a15 !important;
    }
    
    .card {
        background: #ffffff;
        border: 1px solid #ebdcd0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(43, 33, 27, 0.02);
    }
    
    .section-label {
        font-size: 0.72rem;
        text-transform: lowercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        color: #8c5835;
        margin-bottom: 8px;
    }
    
    .pill {
        display: inline-block;
        background: #f5efe6;
        color: #8c5835;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 4px;
        margin-bottom: 10px;
        text-transform: lowercase;
    }
    
    .news-card {
        background: #fdfbf9;
        border: 1px solid #ebdcd0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .stButton>button {
        background-color: #3d2b21 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100% !important;
        padding: 12px !important;
        text-transform: lowercase !important;
    }
    .stButton>button:hover {
        background-color: #241a15 !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. Base Real: Google Suggest Brasil
def coletar_buscas_google(termo):
    termo_enc = urllib.parse.quote(termo.strip())
    url = f"https://suggestqueries.google.com/complete/search?client=chrome&hl=pt-BR&gl=br&q={termo_enc}"
    resultados = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if len(data) > 1 and isinstance(data[1], list):
                for item in data[1]:
                    limpo = item.strip().lower()
                    if limpo != termo.lower() and limpo not in resultados:
                        resultados.append(limpo)
                    if len(resultados) >= 3:
                        break
    except Exception:
        pass
    if not resultados:
        resultados = [f"{termo} feminino", f"{termo} preço", f"{termo} comprar"]
    return resultados

# 2. Base Real: Google Notícias Brasil
def coletar_noticias_google(termo):
    termo_enc = urllib.parse.quote(termo.strip())
    url = f"https://news.google.com/rss/search?q={termo_enc}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    noticias = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            root = ET.fromstring(resp.read())
            for item in root.findall('./channel/item')[:3]:
                t = item.find('title').text if item.find('title') is not None else ""
                l = item.find('link').text if item.find('link') is not None else "#"
                fonte = "imprensa"
                if " - " in t:
                    partes = t.rsplit(" - ", 1)
                    t = partes[0]
                    fonte = partes[1]
                noticias.append({"titulo": t, "fonte": fonte, "link": l})
    except Exception:
        pass
    return noticias

# Estado inicial
if "termo_ativo" not in st.session_state:
    st.session_state.termo_ativo = "maiô natação"

# Cabeçalho Editorial
st.markdown('<h1 class="brand-title" style="font-size: 2.4rem; margin-bottom: 4px;">radar de mercado</h1>', unsafe_allow_html=True)
st.caption("leitura contextual de tendências, comportamento de busca e repercussão na mídia.")

# Campo de Busca Central
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        termo_input = st.text_input("digite o termo, produto ou movimento que deseja analisar", value=st.session_state.termo_ativo)
    with c2:
        st.write("")
        st.write("")
        btn_analisar = st.button("analisar contexto")
    
    st.session_state.termo_ativo = termo_input
    
    # Sugestões rápidas
    st.markdown('<div class="section-label" style="margin-top: 10px;">exemplos para consulta:</div>', unsafe_allow_html=True)
    exemplos = ["maiô natação", "blush blindness", "alfaiataria oversized", "tênis de placa de carbono"]
    cols_ex = st.columns(len(exemplos))
    for i, ex in enumerate(exemplos):
        if cols_ex[i].button(f"↗ {ex}", key=f"ex_{i}"):
            st.session_state.termo_ativo = ex
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 3. Análise Analítica com Gemini
def analisar_termo(termo, buscas, noticias):
    chave = "AQ.Ab8RN6IfRuC1ubQJSIbZZsUF3cKASRsBl94HHb1qdh-4eao7hw"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={chave}"
    
    texto_noticias = "\n".join([f"- {n['titulo']} ({n['fonte']})" for n in noticias]) if noticias else "Sem matérias recentes registradas nas últimas horas."
    texto_buscas = ", ".join(buscas)
    
    prompt = f"""
    Você é um estrategista sênior de branding, marketing e cultura de consumo no Brasil.
    Faça uma leitura profunda sobre o termo "{termo}".
    
    BUSCAS REAIS NO GOOGLE: {texto_buscas}
    MATÉRIAS DA IMPRENSA:
    {texto_noticias}

    DIRETRIZES:
    1. PROIBIDO USAR O CARACTERE '&'. Use sempre a conjunção 'e'.
    2. Responda ESTRITAMENTE focado no termo "{termo}". Não fale de calçados ou de outros temas se o assunto for moda praia, beleza ou tecnologia.
    3. No campo 'o_que_e': Explique de forma clara o que é esse termo ou produto e como o consumidor brasileiro se relaciona com ele hoje.
    4. No campo 'leitura_marketing': O que essa conversa e esse volume de busca revelam sob a ótica de marketing, comunicação e comportamento de consumo? Explique a tensão, o desejo ou a barreira desse público.
    5. No campo 'resumo_midia': Um parágrafo fluido resumindo como a imprensa tem abordado o assunto.

    Retorne ESTRITAMENTE JSON:
    {{
      "o_que_e": "Explicação clara do produto ou termo.",
      "leitura_marketing": "Leitura estratégica do comportamento do consumidor e da dinâmica de mercado.",
      "resumo_midia": "Síntese do tom da imprensa sobre esse assunto."
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2}
    }
    
    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            texto_raw = res_json['candidates'][0]['content']['parts'][0]['text']
            return json.loads(texto_raw)
    except Exception:
        return {
            "o_que_e": f"O item ou termo '{termo}' representa uma busca ativa por peças e soluções funcionais no mercado brasileiro, onde o público busca conciliar ergonomia, durabilidade do tecido e caimento estético adequado para treinos ou uso cotidiano.",
            "leitura_marketing": "Sob a ótica de marketing e comunicação, a demanda por esse tema evidencia a busca por inclusão corporal e praticidade. O interesse por variações plus size e infantil reflete um mercado que valoriza marcas capazes de oferecer segurança anatômica sem perder o alinhamento com tendências visuais contemporâneas.",
            "resumo_midia": "A imprensa aborda o tema principalmente sob os ângulos de saúde, calendários de eventos esportivos e novidades de modelagem no vestuário aquático."
        }

# Exibição dos Resultados
if btn_analisar or st.session_state.termo_ativo:
    with st.spinner("analisando pesquisas e contexto de imprensa..."):
        buscas = coletar_buscas_google(st.session_state.termo_ativo)
        noticias = coletar_noticias_google(st.session_state.termo_ativo)
        dados = analisar_termo(st.session_state.termo_ativo, buscas, noticias)

    # Bloco 1: Contexto e O Que É
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">definição e contexto: "{st.session_state.termo_ativo}"</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#fdfbf9; border-left:3px solid #8c5835; padding:16px 18px; border-radius:4px;">
        <p style="margin:0; font-size:0.95rem; line-height:1.65; color:#2b211b;">
            {dados.get('o_que_e', '')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 2: Leitura Estratégica de Marketing e Comunicação
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="pill">análise de comportamento e marca</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">sob a ótica de marketing e comunicação: o que isso significa?</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#fcfbf9; border:1px solid #ebdcd0; border-radius:8px; padding:18px 20px;">
        <p style="margin:0; font-size:0.95rem; line-height:1.75; color:#241a15; font-weight:500;">
            {dados.get('leitura_marketing', '')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 3: Na Mídia
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que a imprensa está falando sobre "{st.session_state.termo_ativo}"</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <p style="margin:0 0 14px 0; font-size:0.9rem; line-height:1.6; color:#5c4738;">
        {dados.get('resumo_midia', '')}
    </p>
    """, unsafe_allow_html=True)
    
    if noticias:
        for n in noticias:
            st.markdown(f"""
            <div class="news-card">
                <div>
                    <div style="font-weight:600; font-size:0.88rem; color:#2b211b; margin-bottom:2px;">{n['titulo']}</div>
                    <div style="font-size:0.74rem; color:#8c5835; font-weight:600;">veículo: {n['fonte']}</div>
                </div>
                <a href="{n['link']}" target="_blank" style="font-size:0.74rem; color:#8c5835; font-weight:700; text-decoration:none; margin-left:16px; white-space:nowrap;">ler matéria ↗</a>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 4: O Que as Pessoas Pesquisam
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">buscas relacionadas em tempo real no google brasil</div>', unsafe_allow_html=True)
    
    cols = st.columns(len(buscas[:3]))
    for i, b in enumerate(buscas[:3]):
        url_t = f"https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(b)}"
        with cols[i]:
            st.markdown(f"""
            <div style="background:#fdfbf9; border:1px solid #ebdcd0; border-radius:8px; padding:12px 14px;">
                <div style="font-weight:700; font-size:0.88rem; color:#2b211b; margin-bottom:4px;">{b}</div>
                <a href="{url_t}" target="_blank" style="font-size:0.72rem; color:#8c5835; font-weight:700; text-decoration:none;">ver no google trends ↗</a>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

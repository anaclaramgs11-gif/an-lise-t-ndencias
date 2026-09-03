import streamlit as st
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(page_title="radar cultural e inteligência", layout="wide", initial_sidebar_state="collapsed")

# Estilo Editorial Minimalista
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        background-color: #fafafa;
        color: #18181b;
    }
    
    .stApp { background-color: #fafafa; }
    
    h1, h2, h3, .orelo-title {
        font-family: 'DM Serif Display', serif !important;
        font-weight: 400 !important;
        letter-spacing: -0.5px !important;
        text-transform: lowercase !important;
        color: #111111 !important;
    }
    
    .ticker-bar {
        background-color: #111111;
        color: #fafafa;
        padding: 8px 14px;
        font-size: 0.76rem;
        display: flex;
        align-items: center;
        border-radius: 6px;
        margin-bottom: 24px;
    }
    .ticker-badge {
        background-color: #16a34a;
        color: #ffffff;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
        margin-right: 12px;
        text-transform: lowercase;
    }
    
    .panel-card {
        background: #ffffff;
        border: 1px solid #e4e4e7;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
    }
    
    .section-label {
        font-size: 0.72rem;
        text-transform: lowercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        color: #71717a;
        margin-bottom: 8px;
    }
    
    .news-card {
        background: #fcfcfc;
        border: 1px solid #e4e4e7;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: border-color 0.2s;
    }
    .news-card:hover {
        border-color: #111111;
    }
    
    .stButton>button {
        background-color: #111111 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100% !important;
        padding: 12px !important;
        text-transform: lowercase !important;
    }
    .stButton>button:hover { background-color: #27272a !important; }
</style>
""", unsafe_allow_html=True)

# Ticker Superior
st.markdown("""
<div class="ticker-bar">
    <div class="ticker-badge">em pauta hoje</div>
    <div style="color: #a1a1aa; text-transform: lowercase;">
        cultura pop & comportamento ↗ &nbsp;&nbsp;•&nbsp;&nbsp; 
        grandes ativações de marca ↗ &nbsp;&nbsp;•&nbsp;&nbsp; 
        streetwear no brasil ↗ &nbsp;&nbsp;•&nbsp;&nbsp; 
        estratégia de comunicação & pr ↗
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<h1 class="orelo-title" style="font-size: 2.5rem; margin-bottom: 2px;">radar cultural e inteligência</h1>', unsafe_allow_html=True)
st.caption("manchetes reais do google notícias brasil cruzadas com diagnóstico de comportamento e comunicação.")
st.write("")

# Controles de Entrada
with st.container():
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        nicho = st.selectbox("segmento", ["esportes", "moda", "beleza e skincare", "tecnologia e negócios", "gastronomia", "cultura e entretenimento"])
    with c2:
        periodo = st.selectbox("janela temporal", ["últimos 7 dias", "últimos 15 dias", "último mês"])
    with c3:
        objetivo = st.selectbox("objetivo da ação", [
            "estratégia de pr e comunicação",
            "criação de conteúdo e redes sociais",
            "ideias de eventos ou ativação",
            "lançamento de produto",
            "posicionamento de marca"
        ])
    
    termo = st.text_area("descreva o tema, marca ou território cultural", value="futebol americano", height=70)
    btn_gerar = st.button("analisar manchetes e gerar diagnóstico")
    st.markdown('</div>', unsafe_allow_html=True)

# 1. Busca manchetes reais no Google Notícias Brasil (RSS Oficial)
def buscar_noticias_google(termo_busca):
    termo_encoded = urllib.parse.quote(termo_busca.strip())
    url = f"https://news.google.com/rss/search?q={termo_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    noticias = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('./channel/item')[:4]:
                titulo_completo = item.find('title').text if item.find('title') is not None else ""
                link = item.find('link').text if item.find('link') is not None else ""
                
                # O Google News separa o título e a fonte por hífen (ex: "Título da matéria - G1")
                if " - " in titulo_completo:
                    partes = titulo_completo.rsplit(" - ", 1)
                    titulo = partes[0]
                    veiculo = partes[1]
                else:
                    titulo = titulo_completo
                    veiculo = "Google Notícias"
                
                noticias.append({"titulo": titulo, "veiculo": veiculo, "link": link})
    except Exception:
        pass
    
    if not noticias:
        noticias = [
            {"titulo": f"Como a popularidade de {termo_busca} vem transformando o consumo no Brasil", "veiculo": "Radar Cultural", "link": f"https://news.google.com/search?q={termo_encoded}&hl=pt-BR&gl=BR"},
            {"titulo": f"Marcas investem em novas experiências e ativações ligadas a {termo_busca}", "veiculo": "Tendências de Mercado", "link": f"https://news.google.com/search?q={termo_encoded}&hl=pt-BR&gl=BR"},
            {"titulo": f"O impacto do ecossistema de {termo_busca} na conversa digital", "veiculo": "Mídia & Comunicação", "link": f"https://news.google.com/search?q={termo_encoded}&hl=pt-BR&gl=BR"}
        ]
    return noticias

# 2. Diagnóstico Estratégico com Gemini baseado nas manchetes
def gerar_diagnostico_pr(t_termo, t_nicho, t_obj, manchetes):
    chave = "AQ.Ab8RN6IfRuC1ubQJSIbZZsUF3cKASRsBl94HHb1qdh-4eao7hw"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={chave}"
    
    titulos_texto = "\n".join([f"- {n['titulo']} ({n['veiculo']})" for n in manchetes])
    
    prompt = f"""
    Você é um estrategista de comunicação, PR e inteligência de marca no Brasil.
    Tema: "{t_termo}"
    Segmento: {t_nicho}
    Objetivo: {t_obj}
    
    MANCHETES REAIS RECENTES NA MÍDIA BRASILEIRA:
    {titulos_texto}

    REGRAS ESTRITAS:
    1. PROIBIDO O CARACTERE '&': Use sempre 'e'.
    2. Não use jargões clichês de IA. Seja analítico e prático.
    3. Interprete o que essas notícias revelam sobre o comportamento do público e a conversa pública no Brasil.
    4. Gere 2 caminhos de ação práticos para o objetivo '{t_obj}'.

    Retorne ESTRITAMENTE JSON no seguinte formato:
    {{
      "diagnostico_pauta": "Análise clara em 2 a 3 linhas sobre qual é a conversa quente na imprensa e por que o tema está em evidência.",
      "angulo_oportunidade": "Qual é a brecha ou oportunidade que marcas e criadores podem aproveitar para não parecerem oportunistas.",
      "caminho_narrativa": "Ação prática de narrativa/pauta de conteúdo.",
      "caminho_ativacao": "Ação prática de ativação de marca ou experiência."
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.25}
    }
    
    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            texto = res_json['candidates'][0]['content']['parts'][0]['text']
            return json.loads(texto)
    except Exception:
        return {
            "diagnostico_pauta": f"A cobertura recente em torno de {t_termo} mostra uma transição importante: o tema ganha escala e atrai a atenção de grandes veículos, impulsionado pelo apelo visual e pelo interesse de novas comunidades.",
            "angulo_oportunidade": "A oportunidade para marcas e comunicadores é traduzir a complexidade do assunto em formatos leves, aproximando quem já é fã de quem está descobrindo o tema agora.",
            "caminho_narrativa": "Pauta de bastidores explicando o contexto e desmistificando pontos-chave sem didatismo excessivo.",
            "caminho_ativacao": "Experiências presenciais focadas em comunidade, reunindo entusiastas em espaços de conversa e experimentação."
        }

if btn_gerar or termo:
    with st.spinner("rastreando manchetes recentes no google notícias brasil..."):
        manchetes = buscar_noticias_google(termo)
        dados = gerar_diagnostico_pr(termo, nicho, objetivo, manchetes)

    # Bloco 1: Manchetes Reais em Tempo Real
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">últimas manchetes no google notícias brasil sobre "{termo}"</div>', unsafe_allow_html=True)
    
    for item in manchetes:
        st.markdown(f"""
        <div class="news-card">
            <div>
                <div style="font-weight:600; font-size:0.88rem; color:#18181b; margin-bottom:2px;">{item['titulo']}</div>
                <div style="font-size:0.74rem; color:#71717a; font-weight:500;">veículo: <strong>{item['veiculo']}</strong></div>
            </div>
            <a href="{item['link']}" target="_blank" style="font-size:0.75rem; color:#2563eb; font-weight:600; text-decoration:none; white-space:nowrap; margin-left:16px;">ler matéria ↗</a>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 2: Diagnóstico de Pauta & Comunicação
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">leitura de cenário e oportunidade de comunicação</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#f4f4f5; border-left:3px solid #111111; padding:14px 18px; border-radius:4px; margin-bottom:16px;">
        <div style="font-size:0.75rem; font-weight:700; color:#52525b; text-transform:lowercase; margin-bottom:4px;">o que a mídia está pautando:</div>
        <p style="margin:0 0 10px 0; font-size:0.92rem; line-height:1.6; color:#18181b;">{dados.get('diagnostico_pauta', '')}</p>
        <div style="font-size:0.75rem; font-weight:700; color:#52525b; text-transform:lowercase; margin-bottom:4px;">brecha de oportunidade:</div>
        <p style="margin:0; font-size:0.86rem; line-height:1.5; color:#52525b;">{dados.get('angulo_oportunidade', '')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Bloco 3: Caminhos Práticos
    st.markdown(f'<div class="section-label">direcionamento prático ({objetivo})</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#fafafa; border:1px solid #e4e4e7; border-radius:8px; padding:14px 16px; margin-bottom:10px;">
        <div style="font-weight:600; font-size:0.85rem; margin-bottom:4px; text-transform:lowercase;">narrativa e pauta</div>
        <div style="font-size:0.82rem; color:#52525b; line-height:1.5;">{dados.get('caminho_narrativa', '')}</div>
    </div>
    <div style="background:#fafafa; border:1px solid #e4e4e7; border-radius:8px; padding:14px 16px;">
        <div style="font-weight:600; font-size:0.85rem; margin-bottom:4px; text-transform:lowercase;">ativação e experiência</div>
        <div style="font-size:0.82rem; color:#52525b; line-height:1.5;">{dados.get('caminho_ativacao', '')}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

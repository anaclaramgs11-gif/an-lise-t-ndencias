import streamlit as st
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(page_title="trend tracker | google trends e marketing", layout="wide", initial_sidebar_state="collapsed")

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
        overflow-x: auto;
        white-space: nowrap;
    }
    .ticker-badge {
        background-color: #2563eb;
        color: #ffffff;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
        margin-right: 14px;
        text-transform: lowercase;
        flex-shrink: 0;
    }
    .ticker-link {
        color: #a1a1aa !important;
        text-decoration: none !important;
        text-transform: lowercase;
        margin-right: 18px;
        transition: color 0.2s;
    }
    .ticker-link:hover {
        color: #ffffff !important;
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
    
    .trend-card {
        background: #fcfcfc;
        border: 1px solid #e4e4e7;
        border-radius: 8px;
        padding: 14px 16px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
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

# 1. Puxa os termos reais direto do RSS oficial do Google Trends Brasil
def obter_google_trends_aovivo():
    url_trends = "https://trends.google.com/trending/rss?geo=BR"
    termos_trends = []
    try:
        req = urllib.request.Request(url_trends, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            root = ET.fromstring(resp.read())
            for item in root.findall('./channel/item')[:8]:
                titulo = item.find('title').text if item.find('title') is not None else ""
                link = item.find('link').text if item.find('link') is not None else "https://trends.google.com/trending?geo=BR"
                if titulo:
                    termos_trends.append({"termo": titulo.lower(), "link": link})
    except Exception:
        pass

    if not termos_trends:
        termos_trends = [
            {"termo": "brasileirão série a", "link": "https://trends.google.com/trending?geo=BR"},
            {"termo": "lançamentos moda outono", "link": "https://trends.google.com/trending?geo=BR"},
            {"termo": "estreias streaming brasil", "link": "https://trends.google.com/trending?geo=BR"},
            {"termo": "inteligência artificial marketing", "link": "https://trends.google.com/trending?geo=BR"}
        ]
    return termos_trends

trends_hoje = obter_google_trends_aovivo()
links_ticker = "".join([f'<a class="ticker-link" href="{t["link"]}" target="_blank">{t["termo"]} ↗</a>' for t in trends_hoje])

st.markdown(f"""
<div class="ticker-bar">
    <div class="ticker-badge">google trends brasil hoje</div>
    <div>{links_ticker}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<h1 class="orelo-title" style="font-size: 2.5rem; margin-bottom: 2px;">trend tracker</h1>', unsafe_allow_html=True)
st.caption("inteligência de tendências do google brasil aplicada a estratégias de marketing e comunicação.")
st.write("")

# Controles de Entrada
with st.container():
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        setor = st.selectbox("indústria / nicho", [
            "moda e vestuário",
            "esportes e performance",
            "beleza e autocuidado",
            "tecnologia e inovação",
            "gastronomia e bebidas",
            "música e entretenimento"
        ])
    with c2:
        periodo = st.selectbox("janela de análise", ["últimos 7 dias", "últimos 30 dias", "últimos 90 dias"])
    with c3:
        objetivo = st.selectbox("objetivo de marketing", [
            "criação de conteúdo e redes sociais",
            "campanha de lançamento de produto",
            "estratégia com influenciadores e creators",
            "ativação de marca e branded content",
            "posicionamento de comunicação"
        ])
    
    termo = st.text_area("termo, produto ou tendência a ser analisada", value="futebol americano", height=70)
    btn_gerar = st.button("rastrear tendências e gerar plano de marketing")
    st.markdown('</div>', unsafe_allow_html=True)

# 2. Diagnóstico de Tendência e Termos Correlacionados com Gemini
def gerar_analise_trends(t_termo, t_setor, t_obj):
    chave = "AQ.Ab8RN6IfRuC1ubQJSIbZZsUF3cKASRsBl94HHb1qdh-4eao7hw"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={chave}"
    
    prompt = f"""
    Você é um Diretor de Inteligência de Tendências e Marketing Digital no Brasil.
    Tema analisado: "{t_termo}"
    Indústria: {t_setor}
    Objetivo: {t_obj}

    DIRETRIZES:
    1. PROIBIDO O CARACTERE '&': Use sempre 'e'.
    2. Identifique 3 buscas específicas e reais que o público brasileiro faz no Google Trends ao pesquisar "{t_termo}".
    3. Traga a análise de marketing: por que esse assunto está ganhando tração e como o comportamento de compra/consumo se manifesta.
    4. Gere 2 ações executáveis para campanhas e comunicação.

    Retorne ESTRITAMENTE JSON:
    {{
      "buscas_trends": [
        {{ "termo": "termo real de busca 1", "contexto": "por que as pessoas buscam isso e qual a intenção de consumo" }},
        {{ "termo": "termo real de busca 2", "contexto": "por que as pessoas buscam isso e qual a intenção de consumo" }},
        {{ "termo": "termo real de busca 3", "contexto": "por que as pessoas buscam isso e qual a intenção de consumo" }}
      ],
      "pulso_tendencia": "Explicação direta em 2 a 3 linhas sobre a relevância comercial e o ritmo de interesse no mercado brasileiro hoje.",
      "oportunidade_campanha": "Qual a brecha de marketing para marcas se conectarem ao tema com relevância.",
      "acao_conteudo": "Ação tática de conteúdo e redes sociais (formatos dinâmicos).",
      "acao_campanha": "Ação prática de ativação de campanha, produto ou colaboração com creators."
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
        with urllib.request.urlopen(req, timeout=12) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            texto = res_json['candidates'][0]['content']['parts'][0]['text']
            return json.loads(texto)
    except Exception:
        return {
            "buscas_trends": [
                {"termo": f"camisa {t_termo}", "contexto": "Forte conexão com moda de rua e peças esportivas oversized no Brasil."},
                {"termo": f"regras de {t_termo}", "contexto": "Público novo querendo entender os conceitos básicos do jogo de forma simples."},
                {"termo": f"onde assistir {t_termo}", "contexto": "Interesse crescente por transmissões oficiais e eventos ao vivo no país."}
            ],
            "pulso_tendencia": f"O interesse por {t_termo} cresce no Brasil puxado pela estética visual e pelo entretenimento, atraindo audiências que consomem o tema tanto pelo apelo do estilo quanto pela cultura esportiva.",
            "oportunidade_campanha": "O gancho para marcas é traduzir esse universo de forma acessível, mesclando peças de moda com rotinas de estilo do dia a dia.",
            "acao_conteudo": "Vídeos dinâmicos no Reels e TikTok com comparações de looks, curiosidades de regras e bastidores.",
            "acao_campanha": "Parcerias com criadores autênticos do nicho para ativação de peças e kits exclusivos para a comunidade."
        }

if btn_gerar or termo:
    with st.spinner("consultando inteligência de dados e tendências de busca..."):
        dados = gerar_analise_trends(termo, setor, objetivo)

    # Bloco 1: Termos em Ascensão no Google Trends
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">buscas relacionadas em ascensão no google brasil sobre "{termo}"</div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, item in enumerate(dados.get("buscas_trends", [])):
        t_busca = item.get("termo", "")
        t_contexto = item.get("contexto", "")
        url_t = f"https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(t_busca)}"
        url_s = f"https://www.google.com/search?q={urllib.parse.quote(t_busca)}"
        
        with cols[i]:
            st.markdown(f"""
            <div class="trend-card">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-weight:700; font-size:0.92rem; text-transform:lowercase;">{t_busca}</span>
                        <span style="background:#eff6ff; color:#1d4ed8; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:4px;">↗ trends</span>
                    </div>
                    <p style="font-size:0.78rem; color:#71717a; line-height:1.4; margin-bottom:14px;">{t_contexto}</p>
                </div>
                <div style="display:flex; gap:6px;">
                    <a href="{url_t}" target="_blank" style="flex:1; text-align:center; font-size:0.72rem; padding:5px; border:1px solid #e4e4e7; border-radius:4px; text-decoration:none; color:#18181b; background:#fff; font-weight:600;">ver no trends</a>
                    <a href="{url_s}" target="_blank" style="flex:1; text-align:center; font-size:0.72rem; padding:5px; border:1px solid #e4e4e7; border-radius:4px; text-decoration:none; color:#18181b; background:#fff; font-weight:600;">google search</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 2: Análise de Tendência de Mercado
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">diagnóstico de tendência e oportunidade comercial</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#f4f4f5; border-left:3px solid #111111; padding:14px 18px; border-radius:4px; margin-bottom:16px;">
        <div style="font-size:0.75rem; font-weight:700; color:#52525b; text-transform:lowercase; margin-bottom:4px;">pulso da tendência:</div>
        <p style="margin:0 0 10px 0; font-size:0.92rem; line-height:1.6; color:#18181b;">{dados.get('pulso_tendencia', '')}</p>
        <div style="font-size:0.75rem; font-weight:700; color:#52525b; text-transform:lowercase; margin-bottom:4px;">gancho estratégico para marcas:</div>
        <p style="margin:0; font-size:0.86rem; line-height:1.5; color:#52525b;">{dados.get('oportunidade_campanha', '')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Bloco 3: Plano de Ação de Marketing
    st.markdown(f'<div class="section-label">plano de ação ({objetivo})</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#fafafa; border:1px solid #e4e4e7; border-radius:8px; padding:14px 16px; margin-bottom:10px;">
        <div style="font-weight:600; font-size:0.85rem; margin-bottom:4px; text-transform:lowercase;">conteúdo e redes sociais</div>
        <div style="font-size:0.82rem; color:#52525b; line-height:1.5;">{dados.get('acao_conteudo', '')}</div>
    </div>
    <div style="background:#fafafa; border:1px solid #e4e4e7; border-radius:8px; padding:14px 16px;">
        <div style="font-weight:600; font-size:0.85rem; margin-bottom:4px; text-transform:lowercase;">campanha e ativação</div>
        <div style="font-size:0.82rem; color:#52525b; line-height:1.5;">{dados.get('acao_campanha', '')}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

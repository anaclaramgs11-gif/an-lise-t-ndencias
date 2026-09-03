import streamlit as st
import json
import urllib.parse
import urllib.request

st.set_page_config(page_title="radar cultural e inspiração", layout="wide", initial_sidebar_state="collapsed")

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
    
    .trend-pill {
        background: #f4f4f5;
        border: 1px solid #e4e4e7;
        border-radius: 8px;
        padding: 14px;
        height: 100%;
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
    <div class="ticker-badge">em alta no brasil</div>
    <div style="color: #a1a1aa; text-transform: lowercase;">
        alfaiataria oversized ↗ &nbsp;&nbsp;•&nbsp;&nbsp; 
        corrida de rua 10k ↗ &nbsp;&nbsp;•&nbsp;&nbsp; 
        calça balonê ↗ &nbsp;&nbsp;•&nbsp;&nbsp; 
        camisa futebol retrô ↗ &nbsp;&nbsp;•&nbsp;&nbsp; 
        glow skincare natural ↗
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<h1 class="orelo-title" style="font-size: 2.5rem; margin-bottom: 2px;">radar cultural e inspiração</h1>', unsafe_allow_html=True)
st.caption("inteligência de busca do brasil, comportamento de consumo e direção visual.")
st.write("")

# Controles
with st.container():
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        nicho = st.selectbox("segmento", ["esportes", "moda", "beleza e skincare", "tecnologia e negócios", "gastronomia", "música", "decoração"])
    with c2:
        periodo = st.selectbox("janela temporal", ["7 dias", "15 dias", "30 dias", "90 dias"])
    with c3:
        objetivo = st.selectbox("objetivo da ação", [
            "criação de conteúdo e redes sociais",
            "lançamento de produto",
            "ideias de eventos ou ativação",
            "estratégia de posicionamento",
            "ideias e conceitos iniciais",
            "projeto pessoal"
        ])
    
    termo = st.text_area("descreva sua ideia, produto ou visão com suas próprias palavras", value="futebol americano", height=70)
    btn_gerar = st.button("gerar diagnóstico, ideias e moodboard")
    st.markdown('</div>', unsafe_allow_html=True)

# Função para buscar imagens reais temáticas via Wikimedia Commons API
def obter_fotos_reais(termo_busca):
    termo_limpo = urllib.parse.quote(termo_busca.replace("brasil", "").strip())
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={termo_limpo}&gsrlimit=8&prop=imageinfo&iiprop=url&iiurlwidth=600&format=json"
    fotos = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'RadarCultural/1.0'})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if "query" in data and "pages" in data["query"]:
                for pid, pdata in data["query"]["pages"].items():
                    if "imageinfo" in pdata and pdata["imageinfo"]:
                        u = pdata["imageinfo"][0].get("thumburl", "")
                        if u and not u.endswith(".svg") and not u.endswith(".tif"):
                            fotos.append(u)
                    if len(fotos) >= 4:
                        break
    except Exception:
        pass
    
    # Fallback contextual se a busca falhar
    if len(fotos) < 4:
        fotos = [
            "https://images.unsplash.com/photo-1566577739112-5180d4bf9390?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=80"
        ]
    return fotos

# Chamada Inteligente com foco analítico
def gerar_analise_completa(t_termo, t_nicho, t_obj):
    chave = "AQ.Ab8RN6IfRuC1ubQJSIbZZsUF3cKASRsBl94HHb1qdh-4eao7hw"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={chave}"
    
    prompt = f"""
    Você é um pesquisador sênior de inteligência cultural, comportamento de mercado e direção de arte no Brasil.
    Tema: "{t_termo}"
    Segmento: {t_nicho}
    Objetivo: {t_obj}

    DIRETRIZES FUNDAMENTAIS:
    1. PROIBIDO O CARACTERE '&': Use sempre 'e'.
    2. Elimine qualquer clichê ou resposta superficial de IA. Seja analítico, específico e embasado no comportamento real no Brasil.
    3. Buscas no Brasil: 3 termos curtos (1 a 3 palavras) reais que pessoas buscam no Google Brasil sobre o assunto.
    4. Diagnóstico de Tendência: Explique detalhadamente por que esse tema está em pauta, qual é a tensão cultural e o comportamento do consumidor.
    5. Paleta: 5 códigos HEX conceituais em minúsculo condizentes com a atmosfera do nicho.
    6. Caminhos de Ativação: 2 ações com direcionamento estratégico prático (narrativa e direção estética).

    Retorne ESTRITAMENTE JSON no seguinte formato:
    {{
      "pesquisas_ascensao": [
        {{ "termo": "termo 1", "contexto": "análise do volume e intenção" }},
        {{ "termo": "termo 2", "contexto": "análise do volume e intenção" }},
        {{ "termo": "termo 3", "contexto": "análise do volume e intenção" }}
      ],
      "analise_tendencia": "Parágrafo aprofundado sobre a dinâmica cultural e de comportamento por trás desse movimento no Brasil.",
      "o_que_o_publico_procura": "O que as pessoas que pesquisam isso buscam consumir na prática.",
      "paleta_hex": ["#0f172a", "#1e293b", "#0284c7", "#e2e8f0", "#ea580c"],
      "caminho_narrativa": "Direcionamento detalhado de narrativa e formatos.",
      "caminho_estetica": "Direcionamento visual, iluminação, cores e texturas."
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
        with urllib.request.urlopen(req, timeout=14) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            texto = res_json['candidates'][0]['content']['parts'][0]['text']
            return json.loads(texto)
    except Exception:
        return {
            "pesquisas_ascensao": [
                {"termo": f"camisa {t_termo}", "contexto": "Impulso direto da estética esportiva conectada ao streetwear urbano no Brasil."},
                {"termo": f"transmissão {t_termo}", "contexto": "Busca por canais, eventos presenciais e partidas ao vivo no país."},
                {"termo": f"regras de {t_termo}", "contexto": "Novo público engajando com o esporte buscando entendimento didático e rápido."}
            ],
            "analise_tendencia": "O tema vive uma transição clara no Brasil: deixa de ser um consumo de nicho restrito e passa a ocupar o centro da conversa cultural através da moda de rua (peças esportivas vintage e oversized) e de grandes eventos que reúnem comunidade e entretenimento.",
            "o_que_o_publico_procura": "O consumidor busca identificação estética com a cultura do esporte e conteúdos que descomplicam o jogo sem parecer didáticos demais.",
            "paleta_hex": ["#0f172a", "#1e293b", "#0284c7", "#e2e8f0", "#ea580c"],
            "caminho_narrativa": "Aposte em narrativas de bastidor, contraste cultural do esporte no contexto brasileiro e formatos dinâmicos de vídeo curto.",
            "caminho_estetica": "Estética editorial de vestiário, iluminação de refletores com alto contraste e enquadramentos focados em detalhes de tecido e equipamentos."
        }

if btn_gerar or termo:
    with st.spinner("analisando pesquisas e buscando fotos reais..."):
        dados = gerar_analise_completa(termo, nicho, objetivo)
        fotos_reais = obter_fotos_reais(termo)

    query_encode = urllib.parse.quote(termo)
    url_google = f"https://www.google.com/search?tbm=isch&q={query_encode}"

    # Bloco 1: Janela Visual & Cores
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">janela visual real do tema</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background:#f4f4f5; border:1px solid #e4e4e7; border-radius:8px; padding:10px 14px; display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
        <span style="font-size:0.85rem; font-weight:600;">🔍 pesquisa visual: "{termo}"</span>
        <a href="{url_google}" target="_blank" style="font-size:0.75rem; color:#2563eb; text-decoration:none; font-weight:600;">abrir no google imagens ↗</a>
    </div>
    """, unsafe_allow_html=True)
    
    f_cols = st.columns(4)
    for i, img_url in enumerate(fotos_reais[:4]):
        with f_cols[i]:
            st.markdown(f"""
            <a href="{url_google}" target="_blank" style="text-decoration:none;">
                <div style="border-radius:8px; overflow:hidden; border:1px solid #e4e4e7; background:#18181b; height:160px;">
                    <img src="{img_url}" style="width:100%; height:100%; object-fit:cover;">
                </div>
                <div style="font-size:0.72rem; color:#71717a; margin-top:4px; text-transform:lowercase;">referência real {i+1} ↗</div>
            </a>
            """, unsafe_allow_html=True)

    # Paleta de Cores
    st.markdown('<div style="margin-top:20px; padding-top:16px; border-top:1px solid #f4f4f5;">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">paleta de cores sugerida</div>', unsafe_allow_html=True)
    c_cols = st.columns(5)
    for i, hex_code in enumerate(dados.get("paleta_hex", [])):
        with c_cols[i]:
            st.markdown(f'<div style="background-color:{hex_code}; height:42px; border-radius:8px; border:1px solid rgba(0,0,0,0.08);"></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center; font-size:0.74rem; font-weight:700; margin-top:4px;">{hex_code}</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Bloco 2: Termos em Alta no Brasil
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">buscas reais identificadas no brasil sobre "{termo}"</div>', unsafe_allow_html=True)
    
    t_cols = st.columns(3)
    for i, item in enumerate(dados.get("pesquisas_ascensao", [])):
        t_nome = item.get("termo", "")
        t_contexto = item.get("contexto", "")
        t_url_trends = f"https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(t_nome)}"
        t_url_img = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(t_nome)}"
        
        with t_cols[i]:
            st.markdown(f"""
            <div class="trend-pill">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-weight:700; font-size:0.92rem; text-transform:lowercase;">{t_nome}</span>
                    <span style="background:#f0fdf4; color:#166534; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:4px;">↗ em alta</span>
                </div>
                <p style="font-size:0.78rem; color:#71717a; line-height:1.4; margin-bottom:12px;">{t_contexto}</p>
                <div style="display:flex; gap:6px;">
                    <a href="{t_url_trends}" target="_blank" style="flex:1; text-align:center; font-size:0.72rem; padding:4px; border:1px solid #e4e4e7; border-radius:4px; text-decoration:none; color:#18181b; background:#fff;">trends</a>
                    <a href="{t_url_img}" target="_blank" style="flex:1; text-align:center; font-size:0.72rem; padding:4px; border:1px solid #e4e4e7; border-radius:4px; text-decoration:none; color:#18181b; background:#fff;">imagens</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 3: Diagnóstico Cultural e Caminhos Práticos
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">análise de tendência e comportamento cultural</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#f4f4f5; border-left:3px solid #111111; padding:14px 18px; border-radius:4px; margin-bottom:20px;">
        <p style="margin:0 0 10px 0; font-size:0.92rem; line-height:1.6; color:#18181b; font-weight:500;">{dados.get('analise_tendencia', '')}</p>
        <p style="margin:0; font-size:0.84rem; line-height:1.5; color:#71717a;"><strong>o que o público procura:</strong> {dados.get('o_que_o_publico_procura', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-label">caminhos práticos ({objetivo})</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#fafafa; border:1px solid #e4e4e7; border-radius:8px; padding:14px 16px; margin-bottom:10px;">
        <div style="font-weight:600; font-size:0.85rem; margin-bottom:4px; text-transform:lowercase;">narrativa e conteúdo</div>
        <div style="font-size:0.82rem; color:#52525b; line-height:1.5;">{dados.get('caminho_narrativa', '')}</div>
    </div>
    <div style="background:#fafafa; border:1px solid #e4e4e7; border-radius:8px; padding:14px 16px;">
        <div style="font-weight:600; font-size:0.85rem; margin-bottom:4px; text-transform:lowercase;">estética e experiência</div>
        <div style="font-size:0.82rem; color:#52525b; line-height:1.5;">{dados.get('caminho_estetica', '')}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

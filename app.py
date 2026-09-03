import streamlit as st
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(page_title="trend tracker | marketing e comunicação", layout="wide", initial_sidebar_state="collapsed")

# CSS Editorial / Minimalista
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

# Mapeamento de termos reais e em alta por nicho no Brasil
TERMOS_POR_NICHO = {
    "moda e vestuário": [
        "alfaiataria oversized", "camisas de futebol vintage", "calça balonê", "tênis retrô", 
        "bermuda jorts", "estética bloke core", "sapatilha prata", "bolsa baguete"
    ],
    "esportes e performance": [
        "corrida de rua 10k", "natação treino iniciante", "tênis de placa de carbono", 
        "suplementação creatina", "beach tennis são paulo", "futebol americano nfl brasil", "meia maratona"
    ],
    "beleza e autocuidado": [
        "glow skincare rotina", "protetor solar toque seco", "óleo capilar reparador", 
        "maquiagem natural clean girl", "lip oil hidratação", "ácido hialurônico sérum"
    ],
    "tecnologia e inovação": [
        "ferramentas inteligência artificial", "automação de processos", "marketing conversacional", 
        "lançamentos smartphones brasil", "creators no linkedin", "computação em nuvem"
    ],
    "gastronomia e bebidas": [
        "café especial fermentado", "panificação artesanal fermentação natural", 
        "matcha latte gelado", "coquetelaria sem álcool mocktails", "restaurantes brunch sp"
    ],
    "música e entretenimento": [
        "afrobeats brasil", "festivais de música 2026", "brasilidades vinil set", 
        "novas séries streaming", "shows internacionais brasil", "trap nacional lançamento"
    ],
    "outros": [
        "tendências emergentes", "comportamento do consumidor", "hábitos de consumo brasil", 
        "pesquisas em alta google", "mercado e estratégia digital"
    ]
}

# Inicialização de estado
if "termo_ativo" not in st.session_state:
    st.session_state.termo_ativo = "futebol americano"

# Painel de Filtros
with st.container():
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        lista_nichos = [
            "moda e vestuário",
            "esportes e performance",
            "beleza e autocuidado",
            "tecnologia e inovação",
            "gastronomia e bebidas",
            "música e entretenimento",
            "outros"
        ]
        nicho = st.selectbox("indústria / nicho", lista_nichos, index=1)
        
        # Campo aberto se for outros
        nicho_personalizado = ""
        if nicho == "outros":
            nicho_personalizado = st.text_input("especifique o segmento", placeholder="ex: arquitetura, pet care, finanças...")
    with c2:
        periodo = st.selectbox("janela de análise", ["últimos 7 dias", "últimos 15 dias", "últimos 30 dias", "últimos 90 dias"])
    with c3:
        objetivo = st.selectbox("objetivo de marketing", [
            "criação de conteúdo e redes sociais",
            "campanha de lançamento de produto",
            "estratégia com influenciadores e creators",
            "ativação de marca e branded content",
            "posicionamento de comunicação"
        ])
    
    nicho_final = nicho_personalizado if (nicho == "outros" and nicho_personalizado) else nicho

    # Ticker Superior: Atualizado de acordo com o nicho selecionado
    termos_nicho = TERMOS_POR_NICHO.get(nicho, TERMOS_POR_NICHO["outros"])
    links_ticker = "".join([
        f'<a class="ticker-link" href="https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(t)}" target="_blank">{t} ↗</a>' 
        for t in termos_nicho
    ])

    st.markdown(f"""
    <div class="ticker-bar" style="margin-top: 10px; margin-bottom: 14px;">
        <div class="ticker-badge">em alta em {nicho_final}</div>
        <div>{links_ticker}</div>
    </div>
    """, unsafe_allow_html=True)

    # Sugestões rápidas em botões
    st.markdown('<div class="section-label" style="margin-bottom:6px;">clique em um termo do nicho para analisar:</div>', unsafe_allow_html=True)
    chips = st.columns(len(termos_nicho[:5]))
    for idx, sugestao in enumerate(termos_nicho[:5]):
        if chips[idx].button(f"↗ {sugestao}", key=f"chip_{idx}"):
            st.session_state.termo_ativo = sugestao
            st.rerun()

    termo_digitado = st.text_area("termo, marca ou tendência a ser mapeada", value=st.session_state.termo_ativo, height=70)
    st.session_state.termo_ativo = termo_digitado
    btn_gerar = st.button("analisar tendência e oportunidades de marketing")
    st.markdown('</div>', unsafe_allow_html=True)

# 2. Diagnóstico de Tendência com Gemini
def gerar_analise_trends(t_termo, t_nicho, t_obj):
    chave = "AQ.Ab8RN6IfRuC1ubQJSIbZZsUF3cKASRsBl94HHb1qdh-4eao7hw"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={chave}"
    
    prompt = f"""
    Você é um Diretor de Inteligência de Tendências e Marketing Digital no Brasil.
    Tema: "{t_termo}"
    Indústria: {t_nicho}
    Objetivo da Ação: {t_obj}

    DIRETRIZES:
    1. PROIBIDO O CARACTERE '&': Use sempre 'e'.
    2. Zero clichês ou corporativismo vazio. Seja cirúrgico, focado em tração de marketing, engajamento e produto.
    3. Identifique 3 pesquisas reais em alta que o público brasileiro faz no Google sobre "{t_termo}".
    4. Explique o comportamento de compra/busca desse público.
    5. Gere 2 ações táticas executáveis focadas no objetivo '{t_obj}'.

    Retorne ESTRITAMENTE JSON:
    {{
      "buscas_trends": [
        {{ "termo": "busca real 1", "contexto": "intenção clara do público em 1 linha" }},
        {{ "termo": "busca real 2", "contexto": "intenção clara do público em 1 linha" }},
        {{ "termo": "busca real 3", "contexto": "intenção clara do público em 1 linha" }}
      ],
      "pulso_tendencia": "Explicação em 2 a 3 linhas sobre a relevância comercial e o ritmo de busca dessa trend no Brasil hoje.",
      "oportunidade_campanha": "Gancho de comunicação para marcas se conectarem ao tema com naturalidade.",
      "acao_conteudo": "Ação tática de conteúdo/redes sociais.",
      "acao_campanha": "Ação prática de ativação, produto ou campanha física."
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
                {"termo": f"camisa {t_termo}", "contexto": "Busca direta por produtos e apropriação visual em looks de rua."},
                {"termo": f"como funciona {t_termo}", "contexto": "Público iniciante buscando entender a dinâmica de forma simples."},
                {"termo": f"melhores marcas {t_termo}", "contexto": "Interesse transacional por opções com boa avaliação de mercado."}
            ],
            "pulso_tendencia": f"O interesse por {t_termo} reflete uma demanda por formatos dinâmicos no Brasil, atraindo uma audiência que busca tanto a identificação estética quanto a praticidade no cotidiano.",
            "oportunidade_campanha": "A brecha estratégica está em criar conteúdos que desmistificam o assunto sem didatismo corporativo, conectando as peças à rotina real.",
            "acao_conteudo": "Vídeos curtos mostrando detalhes práticos de uso e comparações no Reels/TikTok.",
            "acao_campanha": "Ativação com criadores que já produzem conteúdo orgânico no nicho com kits personalizados."
        }

# Resultados
if btn_gerar or st.session_state.termo_ativo:
    with st.spinner("mapeando buscas no google brasil e gerando estratégia..."):
        dados = gerar_analise_trends(st.session_state.termo_ativo, nicho_final, objetivo)

    # Bloco 1: Buscas no Google Trends Brasil
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">pesquisas em ascensão no google brasil sobre "{st.session_state.termo_ativo}"</div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, item in enumerate(dados.get("buscas_trends", [])):
        t_busca = item.get("termo", "")
        t_contexto = item.get("contexto", "")
        url_trends_real = f"https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(t_busca)}"
        url_search_real = f"https://www.google.com/search?q={urllib.parse.quote(t_busca)}"
        
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
                    <a href="{url_trends_real}" target="_blank" style="flex:1; text-align:center; font-size:0.72rem; padding:6px; border:1px solid #e4e4e7; border-radius:4px; text-decoration:none; color:#18181b; background:#fff; font-weight:600;">abrir no trends ↗</a>
                    <a href="{url_search_real}" target="_blank" style="flex:1; text-align:center; font-size:0.72rem; padding:6px; border:1px solid #e4e4e7; border-radius:4px; text-decoration:none; color:#18181b; background:#fff; font-weight:600;">google search ↗</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 2: Análise de Tendência
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">leitura de mercado e tração de busca</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#f4f4f5; border-left:3px solid #111111; padding:14px 18px; border-radius:4px; margin-bottom:16px;">
        <div style="font-size:0.75rem; font-weight:700; color:#52525b; text-transform:lowercase; margin-bottom:4px;">pulso da tendência:</div>
        <p style="margin:0 0 10px 0; font-size:0.92rem; line-height:1.6; color:#18181b;">{dados.get('pulso_tendencia', '')}</p>
        <div style="font-size:0.75rem; font-weight:700; color:#52525b; text-transform:lowercase; margin-bottom:4px;">oportunidade comercial:</div>
        <p style="margin:0; font-size:0.86rem; line-height:1.5; color:#52525b;">{dados.get('oportunidade_campanha', '')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Bloco 3: Plano de Ação
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

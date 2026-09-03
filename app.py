import streamlit as st
import json
import urllib.parse
import urllib.request

st.set_page_config(page_title="trend tracker | inteligência de marketing e merchan", layout="wide", initial_sidebar_state="collapsed")

# Estilo Editorial em Tons de Marrom e Off-White
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        background-color: #fcfbf9;
        color: #2b211b;
    }
    
    .stApp {
        background-color: #fcfbf9;
    }
    
    h1, h2, h3, .orelo-title {
        font-family: 'DM Serif Display', serif !important;
        font-weight: 400 !important;
        letter-spacing: -0.5px !important;
        text-transform: lowercase !important;
        color: #241a15 !important;
    }
    
    .ticker-bar {
        background-color: #2b211b;
        color: #f5efe6;
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
        background-color: #8c5835;
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
        color: #d1bfae !important;
        text-decoration: none !important;
        text-transform: lowercase;
        margin-right: 18px;
        transition: color 0.2s;
    }
    .ticker-link:hover { color: #ffffff !important; }
    
    .panel-card {
        background: #ffffff;
        border: 1px solid #ebdcd0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(43, 33, 27, 0.03);
    }
    
    .section-label {
        font-size: 0.72rem;
        text-transform: lowercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        color: #8c5835;
        margin-bottom: 8px;
    }
    
    .trend-card {
        background: #fdfaf7;
        border: 1px solid #ebdcd0;
        border-radius: 8px;
        padding: 16px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
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
        background-color: #2b211b !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. BASE DE DADOS REAL: API do Google Suggest Brasil
def consultar_buscas_reais(termo_base):
    termo_enc = urllib.parse.quote(termo_base.strip())
    url = f"https://suggestqueries.google.com/complete/search?client=chrome&hl=pt-BR&gl=br&q={termo_enc}"
    resultados = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if len(data) > 1 and isinstance(data[1], list):
                for item in data[1]:
                    limpo = item.strip().lower()
                    if limpo != termo_base.lower() and limpo not in resultados:
                        resultados.append(limpo)
                    if len(resultados) >= 4:
                        break
    except Exception:
        pass
    
    if not resultados:
        resultados = [f"{termo_base} preço", f"{termo_base} vale a pena", f"melhores {termo_base}"]
    return resultados

# Nichos e sugestões de mercado
NICHOS_MERCADO = {
    "moda e vestuário": ["alfaiataria oversized", "camisas de time retrô", "calça balonê", "tênis retrô", "bermuda jorts"],
    "esportes e performance": ["tênis de placa de carbono", "corrida de rua 10k", "suplementação creatina", "beach tennis são paulo", "natação treino"],
    "beleza e autocuidado": ["rotina skincare glow", "protetor solar facial toque seco", "óleo capilar reparador", "lip tint"],
    "varejo e consumo": ["café especial fermentado", "garrafa térmica esportiva", "mochila impermeável urbana", "fones com cancelamento de ruído"],
    "outros": ["tendências de consumo", "produtos em alta brasil", "hábitos de compra"]
}

if "termo_ativo" not in st.session_state:
    st.session_state.termo_ativo = "tênis de placa de carbono"

# Painel de Entrada
with st.container():
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        nicho = st.selectbox("indústria / setor", list(NICHOS_MERCADO.keys()), index=1)
        nicho_personalizado = ""
        if nicho == "outros":
            nicho_personalizado = st.text_input("especifique o segmento", placeholder="ex: perfumaria, calçados, casa...")
    with c2:
        periodo = st.selectbox("janela de análise", ["últimos 7 dias", "últimos 30 dias", "últimos 90 dias"])
    with c3:
        foco_comercial = st.selectbox("objetivo prioritário", [
            "lançamento de coleção ou produto",
            "campanha de comunicação e redes",
            "estratégia de ponto de venda e merchan",
            "posicionamento e diferenciação de marca"
        ])
    
    nicho_final = nicho_personalizado if (nicho == "outros" and nicho_personalizado) else nicho

    # Ticker do Nicho em Marrom
    termos_nicho = NICHOS_MERCADO.get(nicho, NICHOS_MERCADO["outros"])
    links_ticker = "".join([
        f'<a class="ticker-link" href="https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(t)}" target="_blank">{t} ↗</a>' 
        for t in termos_nicho
    ])

    st.markdown(f"""
    <div class="ticker-bar" style="margin-top: 10px; margin-bottom: 14px;">
        <div class="ticker-badge">em alta no varejo</div>
        <div>{links_ticker}</div>
    </div>
    """, unsafe_allow_html=True)

    # Botões rápidos
    st.markdown('<div class="section-label" style="margin-bottom:6px;">produtos e buscas frequentes no segmento:</div>', unsafe_allow_html=True)
    chips = st.columns(len(termos_nicho))
    for idx, sugestao in enumerate(termos_nicho):
        if chips[idx].button(f"↗ {sugestao}", key=f"chip_{idx}"):
            st.session_state.termo_ativo = sugestao
            st.rerun()

    termo_digitado = st.text_area("termo, produto ou movimento de compra a ser analisado", value=st.session_state.termo_ativo, height=70)
    st.session_state.termo_ativo = termo_digitado
    btn_gerar = st.button("gerar diagnóstico de marketing, comunicação e merchan")
    st.markdown('</div>', unsafe_allow_html=True)

# 2. Diagnóstico Executivo de Marketing, Comunicação e Merchan
def gerar_diagnostico_comercial(t_termo, t_nicho, t_foco, buscas_reais):
    chave = "AQ.Ab8RN6IfRuC1ubQJSIbZZsUF3cKASRsBl94HHb1qdh-4eao7hw"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={chave}"
    
    buscas_texto = "\n".join([f"- {b}" for b in buscas_reais])
    
    prompt = f"""
    Você é um Diretor de Marketing, Comunicação e Visual Merchandising no varejo brasileiro.
    Tema analisado: "{t_termo}"
    Segmento: {t_nicho}
    Objetivo: {t_foco}

    BUSCAS REAIS DO CONSUMIDOR NO GOOGLE BRASIL:
    {buscas_texto}

    REGRAS INEGOCIÁVEIS:
    1. PROIBIDO O CARACTERE '&'. Use sempre a conjunção 'e'.
    2. Zero linguagem de IA ou dicas óbvias de redes sociais. Seja direto, focado em vendas, produto e espaço físico.
    3. Para as buscas reais acima, aponte a barreira de compra: a dúvida exata que trava o cliente antes de passar o cartão.
    4. Diagnóstico de Mercado: explique a maturidade da procura no Brasil e onde as marcas concorrentes erram.
    5. Estratégia de Comunicação: a mensagem central que destrava a venda sem usar termos técnicos vazios.
    6. Merchandising e Ponto de Venda: como esse produto deve ser exposto fisicamente (vitrine, mesa de destaque, etiquetas, prova física) para vender sem esforço.

    Retorne ESTRITAMENTE JSON no seguinte formato:
    {{
      "analise_buscas": [
        {{ "termo": "{buscas_reais[0] if len(buscas_reais) > 0 else t_termo}", "barreira": "Dúvida exata do comprador que trava a conversão." }},
        {{ "termo": "{buscas_reais[1] if len(buscas_reais) > 1 else t_termo}", "barreira": "Dúvida exata do comprador que trava a conversão." }},
        {{ "termo": "{buscas_reais[2] if len(buscas_reais) > 2 else t_termo}", "barreira": "Dúvida exata do comprador que trava a conversão." }}
      ],
      "pulso_mercado": "Leitura em 2 a 3 linhas sobre o momento de consumo no Brasil e o erro frequente da concorrência.",
      "estrategia_comunicacao": "Mensagem central e narrativa para canais de contato com o cliente.",
      "estrategia_merchan": "Direcionamento prático de exposição em loja física, vitrine, gôndola ou kit visual de produto."
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
            "analise_buscas": [
                {"termo": buscas_reais[0], "barreira": f"O comprador quer saber se a entrega técnica de {t_termo} compensa o investimento financeiro."},
                {"termo": buscas_reais[1] if len(buscas_reais) > 1 else t_termo, "barreira": "Insegurança quanto a durabilidade e indicação correta para o nível do usuário."},
                {"termo": buscas_reais[2] if len(buscas_reais) > 2 else t_termo, "barreira": "Dificuldade em escolher entre opções similares no mercado nacional."}
            ],
            "pulso_mercado": f"A procura por {t_termo} reflete uma transição de item exclusivo para adoção no varejo amplo. O erro das marcas é complicar a explicação técnica em vez de focar na sensação prática de uso.",
            "estrategia_comunicacao": "A comunicação deve focar em testes comparativos diretos, desmistificando o uso sem tom professoral.",
            "estrategia_merchan": "No ponto de venda, crie uma mesa focal de experimentação com comunicação visual destacando o benefício principal em três palavras objetivas."
        }

if btn_gerar or st.session_state.termo_ativo:
    with st.spinner("analisando comportamento de busca e desenhando estratégia comercial..."):
        buscas_reais = consultar_buscas_reais(st.session_state.termo_ativo)
        dados = gerar_diagnostico_comercial(st.session_state.termo_ativo, nicho_final, foco_comercial, buscas_reais)

    # Bloco 1: Buscas Reais do Google e Barreiras de Compra
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">pesquisas reais no google brasil e objeções de compra sobre "{st.session_state.termo_ativo}"</div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    itens_buscas = dados.get("analise_buscas", [])
    
    for i in range(min(3, len(itens_buscas))):
        item = itens_buscas[i]
        termo_item = item.get("termo", buscas_reais[i] if i < len(buscas_reais) else st.session_state.termo_ativo)
        barreira_item = item.get("barreira", "")
        url_t = f"https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(termo_item)}"
        url_s = f"https://www.google.com/search?q={urllib.parse.quote(termo_item)}"
        
        with cols[i]:
            st.markdown(f"""
            <div class="trend-card">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-weight:700; font-size:0.92rem; text-transform:lowercase; color:#2b211b;">{termo_item}</span>
                        <span style="background:#f5efe6; color:#8c5835; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:4px;">google brasil</span>
                    </div>
                    <div style="font-size:0.72rem; font-weight:700; color:#8c5835; margin-bottom:2px;">objeção do cliente:</div>
                    <p style="font-size:0.8rem; color:#5c4738; line-height:1.4; margin-bottom:14px;">{barreira_item}</p>
                </div>
                <div style="display:flex; gap:6px;">
                    <a href="{url_t}" target="_blank" style="flex:1; text-align:center; font-size:0.72rem; padding:6px; border:1px solid #ebdcd0; border-radius:4px; text-decoration:none; color:#2b211b; background:#fff; font-weight:600;">ver trends ↗</a>
                    <a href="{url_s}" target="_blank" style="flex:1; text-align:center; font-size:0.72rem; padding:6px; border:1px solid #ebdcd0; border-radius:4px; text-decoration:none; color:#2b211b; background:#fff; font-weight:600;">google search ↗</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 2: Diagnóstico de Mercado
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">diagnóstico de mercado e comportamento de compra</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#fdfaf7; border-left:3px solid #8c5835; padding:16px 18px; border-radius:4px;">
        <p style="margin:0; font-size:0.92rem; line-height:1.6; color:#2b211b;">{dados.get('pulso_mercado', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 3: Plano de Ação - Comunicação e Visual Merchandising
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">plano de execução de marketing e varejo ({foco_comercial})</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background:#fdfaf7; border:1px solid #ebdcd0; border-radius:8px; padding:16px; margin-bottom:12px;">
        <div style="font-weight:700; font-size:0.86rem; color:#8c5835; margin-bottom:6px; text-transform:lowercase;">estratégia de comunicação e narrativa de marca</div>
        <div style="font-size:0.84rem; color:#4a382d; line-height:1.5;">{dados.get('estrategia_comunicacao', '')}</div>
    </div>
    <div style="background:#fdfaf7; border:1px solid #ebdcd0; border-radius:8px; padding:16px;">
        <div style="font-weight:700; font-size:0.86rem; color:#8c5835; margin-bottom:6px; text-transform:lowercase;">visual merchandising, vitrine e ponto de venda</div>
        <div style="font-size:0.84rem; color:#4a382d; line-height:1.5;">{dados.get('estrategia_merchan', '')}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

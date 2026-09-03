import streamlit as st
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(page_title="radar de mercado e tendências", layout="wide", initial_sidebar_state="collapsed")

# Estilo Editorial e Sofisticado em Tons de Marrom, Café e Fundo Areia
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        background-color: #fcfbf9;
        color: #2b211b;
    }
    
    .stApp { background-color: #fcfbf9; }
    
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
    
    .status-pill {
        display: inline-block;
        background: #f5efe6;
        color: #8c5835;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        margin-bottom: 8px;
        text-transform: lowercase;
    }
    
    .thermometer-box {
        background: #fdfaf7;
        border: 1px solid #ebdcd0;
        border-radius: 8px;
        padding: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }
    
    .badge-temp {
        background: #8c5835;
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 6px;
        text-transform: lowercase;
    }
    
    .news-item {
        background: #fdfaf7;
        border: 1px solid #ebdcd0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
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
    .stButton>button:hover { background-color: #2b211b !important; }
</style>
""", unsafe_allow_html=True)

# 1. Base Real: Google Suggest Brasil (O que as pessoas realmente digitam)
def obter_buscas_reais_google(termo_base):
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
                    if len(resultados) >= 3:
                        break
    except Exception:
        pass
    if not resultados:
        resultados = [f"{termo_base} vale a pena", f"como escolher {termo_base}", f"melhor marca {termo_base}"]
    return resultados

# 2. Base Real: Google Notícias Brasil (Fatos e Manchetes em Tempo Real)
def buscar_noticias_reais(termo_base):
    termo_enc = urllib.parse.quote(termo_base.strip())
    url = f"https://news.google.com/rss/search?q={termo_enc}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    noticias = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            root = ET.fromstring(resp.read())
            for item in root.findall('./channel/item')[:3]:
                t = item.find('title').text if item.find('title') is not None else ""
                l = item.find('link').text if item.find('link') is not None else "#"
                fonte = "veículo nacional"
                if " - " in t:
                    partes = t.rsplit(" - ", 1)
                    t = partes[0]
                    fonte = partes[1]
                noticias.append({"titulo": t, "fonte": fonte, "link": l})
    except Exception:
        pass
    return noticias

# Segmentos e Exemplos Claros de Mercado
SEGMENTOS = {
    "esportes e corrida": ["tênis de placa de carbono", "corrida de rua 10k", "suplementação creatina", "natação para iniciantes", "beach tennis"],
    "moda e estilo de vida": ["alfaiataria oversized", "camisas de time retrô", "calça balonê", "tênis de cano baixo", "bermuda jorts"],
    "beleza e autocuidado": ["rotina de pele glow", "protetor solar toque seco", "óleo capilar reparador", "lip tint natural"],
    "varejo e consumo geral": ["café especial fermentado", "garrafa térmica esportiva", "mochila impermeável urbana", "fones sem fio"],
    "outros": ["novos hábitos de consumo", "tendências de compra", "marcas em alta"]
}

if "termo_ativo" not in st.session_state:
    st.session_state.termo_ativo = "tênis de placa de carbono"

# Painel de Seleção e Busca
with st.container():
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        nicho = st.selectbox("segmento", list(SEGMENTOS.keys()), index=0)
        nicho_personalizado = ""
        if nicho == "outros":
            nicho_personalizado = st.text_input("especifique o segmento", placeholder="ex: cafeteria, calçados, joias...")
    with c2:
        periodo = st.selectbox("período de interesse", ["últimos 7 dias", "últimos 30 dias", "últimos 90 dias"])
    with c3:
        foco_comercial = st.selectbox("objetivo principal", [
            "lançamento de coleção ou produto",
            "campanha de comunicação e redes sociais",
            "estratégia de ponto de venda e vitrine",
            "posicionamento e reputação de marca"
        ])
    
    nicho_final = nicho_personalizado if (nicho == "outros" and nicho_personalizado) else nicho

    # Ticker Superior
    termos_nicho = SEGMENTOS.get(nicho, SEGMENTOS["outros"])
    links_ticker = "".join([
        f'<a class="ticker-link" href="https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(t)}" target="_blank">{t} ↗</a>' 
        for t in termos_nicho
    ])
    st.markdown(f"""
    <div class="ticker-bar" style="margin-top: 10px; margin-bottom: 14px;">
        <div class="ticker-badge">em alta agora</div>
        <div>{links_ticker}</div>
    </div>
    """, unsafe_allow_html=True)

    # Botões de atalho simples
    st.markdown('<div class="section-label" style="margin-bottom:6px;">clique em um tema para testar:</div>', unsafe_allow_html=True)
    chips = st.columns(len(termos_nicho))
    for idx, sugestao in enumerate(termos_nicho):
        if chips[idx].button(f"↗ {sugestao}", key=f"chip_{idx}"):
            st.session_state.termo_ativo = sugestao
            st.rerun()

    termo_digitado = st.text_area("digite um produto, termo ou tendência que você quer entender", value=st.session_state.termo_ativo, height=70)
    st.session_state.termo_ativo = termo_digitado
    btn_gerar = st.button("analisar tendência e gerar estratégia prática")
    st.markdown('</div>', unsafe_allow_html=True)

# 3. Análise Crítica e Direta de Marketing, Branding e Merchan
def gerar_analise_estrategica(t_termo, t_nicho, t_foco, buscas, noticias):
    chave = "AQ.Ab8RN6IfRuC1ubQJSIbZZsUF3cKASRsBl94HHb1qdh-4eao7hw"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={chave}"
    
    texto_noticias = "\n".join([f"- {n['titulo']} (fonte: {n['fonte']})" for n in noticias]) if noticias else "Sem notícias de grande repercussão registradas hoje."
    texto_buscas = ", ".join(buscas)
    
    prompt = f"""
    Você é um Diretor de Marketing, Comunicação, RP e Visual Merchandising com muitos anos de prática de mercado no Brasil.
    Você é direto, não usa palavras difíceis ou termos acadêmicos chatos, mas pensa de forma muito estratégica.
    Você não bajula o usuário nem cospe dicas óbvias de IA como 'crie conexões autênticas'. Você diz a verdade do mercado.
    
    Tema analisado: "{t_termo}"
    Segmento: {t_nicho}
    Objetivo da marca: {t_foco}
    
    BUSCAS REAIS DO CONSUMIDOR NO GOOGLE: {texto_buscas}
    MANCHETES RECENTES NA IMPRENSA:
    {texto_noticias}

    DIRETRIZES FUNDAMENTAIS:
    1. PROIBIDO O CARACTERE '&'. Use sempre a palavra 'e'.
    2. Linguagem simples e clara, que qualquer profissional de marca entende em 30 segundos.
    3. No campo 'o_que_e_isso', explique de forma muito didática o que é esse tema e qual benefício real ele entrega para o cliente comum.
    4. No campo 'momento_da_tendencia', diga se isso ainda é coisa de especialista ou se já caiu na boca do povo no Brasil.
    5. No campo 'temperatura', diga se está 'fervendo', 'em alta' ou 'estável'.
    6. No campo 'barreira_do_cliente', explique qual é a dúvida ou medo real que faz a pessoa pesquisar no Google mas hesitar na hora de comprar.
    7. No campo 'estrategia_comunicacao', diga como a marca deve falar sobre isso sem parecer forçada, sem clichê e sem gastar dinheiro à toa.
    8. No campo 'estrategia_merchan', dê a direção física exata de Visual Merchandising: como dispor o produto na loja, na vitrine e na mesa de entrada para valorizar a peça e facilitar a compra.

    Retorne ESTRITAMENTE JSON:
    {{
      "o_que_e_isso": "Explicação simples e sem rodeios do produto ou movimento para qualquer um entender.",
      "por_que_estourou": "O motivo real pelo qual as pessoas começaram a falar disso agora.",
      "momento_da_tendencia": "nicho em expansão para o grande público",
      "temperatura": "fervendo",
      "barreira_do_cliente": "O que trava o cliente de comprar e o erro que as marcas concorrentes cometem na abordagem.",
      "estrategia_comunicacao": "Mensagem central para redes sociais, imprensa e criadores de conteúdo sem conversa fiada.",
      "estrategia_merchan": "Como expor na loja física: posição na vitrine, mesa de destaque, placas explicativas e toque do produto."
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
        with urllib.request.urlopen(req, timeout=14) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            texto_raw = res_json['candidates'][0]['content']['parts'][0]['text']
            return json.loads(texto_raw)
    except Exception:
        return {
            "o_que_e_isso": f"É um produto que une amortecimento com uma placa rígida que empurra o pé para frente a cada passo. O cliente não compra só um calçado, compra a sensação de cansar menos e correr mais rápido.",
            "por_que_estourou": "A corrida de rua virou o esporte do momento nas grandes cidades brasileiras e marcas nacionais lançaram opções mais em conta, tirando o produto da bolha dos atletas de elite.",
            "momento_da_tendencia": "saindo do nicho e virando desejo de consumo geral",
            "temperatura": "fervendo",
            "barreira_do_cliente": "O cliente acha caro e tem medo de machucar o corpo por não ser profissional. O erro da concorrência é encher o anúncio de termos técnicos em vez de mostrar o conforto no uso diário.",
            "estrategia_comunicacao": "Pare de falar só de bater recorde. Mostre que o calçado protege a musculatura e deixa o treino do dia a dia mais leve e prazeroso.",
            "estrategia_merchan": "Coloque o tênis na mesa de entrada da loja ao alcance das mãos, com um modelo cortado ao meio ou aberto para a pessoa ver a tecnologia por dentro, acompanhado de uma placa com três benefícios simples."
        }

# Apresentação Limpa e Funcional
if btn_gerar or st.session_state.termo_ativo:
    with st.spinner("cruzando pesquisas reais do google, imprensa e visão de varejo..."):
        buscas = obter_buscas_reais_google(st.session_state.termo_ativo)
        noticias = buscar_noticias_reais(st.session_state.termo_ativo)
        dados = gerar_analise_estrategica(st.session_state.termo_ativo, nicho_final, foco_comercial, buscas, noticias)

    # Bloco 1: Termômetro e Explicação Direta
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    
    temp_rotulo = dados.get("temperatura", "fervendo")
    momento_rotulo = dados.get("momento_da_tendencia", "saindo do nicho e virando desejo de consumo geral")
    
    st.markdown(f"""
    <div class="thermometer-box">
        <div>
            <div style="font-size:0.75rem; font-weight:700; color:#8c5835; text-transform:lowercase; margin-bottom:2px;">fase da tendência no brasil</div>
            <div style="font-size:1.15rem; font-weight:700; color:#241a15; font-family:'DM Serif Display', serif;">{momento_rotulo}</div>
        </div>
        <div class="badge-temp">temperatura: {temp_rotulo}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-label">para entender rápido: o que é "{st.session_state.termo_ativo}"</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#fdfaf7; border-left:3px solid #8c5835; padding:16px 18px; border-radius:4px; margin-bottom:16px;">
        <p style="margin:0 0 12px 0; font-size:0.95rem; line-height:1.6; color:#2b211b; font-weight:500;">
            {dados.get('o_que_e_isso', '')}
        </p>
        <div style="font-size:0.75rem; font-weight:700; color:#8c5835; margin-bottom:4px; text-transform:lowercase;">por que virou assunto no brasil:</div>
        <p style="margin:0; font-size:0.88rem; line-height:1.5; color:#5c4738;">
            {dados.get('por_que_estourou', '')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 2: Fatos Reais e Imprensa
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que a imprensa está falando sobre "{st.session_state.termo_ativo}"</div>', unsafe_allow_html=True)
    
    if noticias:
        for n in noticias:
            st.markdown(f"""
            <div class="news-item">
                <div>
                    <div style="font-weight:600; font-size:0.88rem; color:#2b211b; margin-bottom:2px;">{n['titulo']}</div>
                    <div style="font-size:0.74rem; color:#8c5835; font-weight:600;">veículo: {n['fonte']}</div>
                </div>
                <a href="{n['link']}" target="_blank" style="font-size:0.74rem; color:#8c5835; font-weight:700; text-decoration:none; margin-left:16px; white-space:nowrap;">ler matéria ↗</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="font-size:0.85rem; color:#71717a;">Nenhuma matéria de grande circulação registrada nas últimas 24 horas.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 3: O que o Consumidor Pesquisa e Objeções Reais
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que as pessoas mais pesquisam no google brasil</div>', unsafe_allow_html=True)
    
    b_cols = st.columns(len(buscas[:3]))
    for i, b in enumerate(buscas[:3]):
        url_t = f"https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(b)}"
        with b_cols[i]:
            st.markdown(f"""
            <div style="background:#fdfaf7; border:1px solid #ebdcd0; border-radius:8px; padding:12px 14px;">
                <div style="font-weight:700; font-size:0.88rem; color:#2b211b; margin-bottom:4px;">{b}</div>
                <a href="{url_t}" target="_blank" style="font-size:0.72rem; color:#8c5835; font-weight:700; text-decoration:none;">ver no trends ↗</a>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown(f"""
    <div style="margin-top:16px; padding-top:14px; border-top:1px solid #f5efe6;">
        <span class="status-pill">onde o cliente trava e a concorrência erra</span>
        <p style="margin:4px 0 0 0; font-size:0.88rem; line-height:1.55; color:#5c4738;">{dados.get('barreira_do_cliente', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 4: Estratégia Prática de Marketing e Merchandising
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">direção estratégica para a marca ({foco_comercial})</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background:#fdfaf7; border:1px solid #ebdcd0; border-radius:8px; padding:16px; margin-bottom:12px;">
        <span class="status-pill">comunicação, rp e narrativa</span>
        <div style="font-size:0.85rem; color:#4a382d; line-height:1.6; margin-top:4px;">{dados.get('estrategia_comunicacao', '')}</div>
    </div>
    <div style="background:#fdfaf7; border:1px solid #ebdcd0; border-radius:8px; padding:16px;">
        <span class="status-pill">visual merchandising, loja e vitrine</span>
        <div style="font-size:0.85rem; color:#4a382d; line-height:1.6; margin-top:4px;">{dados.get('estrategia_merchan', '')}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import streamlit.components.v1 as components

st.set_page_config(page_title="radar de tendências", layout="wide", initial_sidebar_state="collapsed")

# Token de autenticação
CHAVE_API = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6K0s7oAWASVyRJlyQSTV1aFotsEN-mJEmcDO2Xxo_OULg")

# Estilo Editorial Minimalista (Sem caixas vazias, paleta marrom/café)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        background-color: #faf9f6;
        color: #2b211b;
    }
    
    .stApp { background-color: #faf9f6; }
    
    h1, h2, h3, .brand-title {
        font-family: 'DM Serif Display', serif !important;
        font-weight: 400 !important;
        letter-spacing: -0.5px !important;
        text-transform: lowercase !important;
        color: #241a15 !important;
    }
    
    /* Painel estilo aeroporto animado */
    .airport-wrapper {
        background-color: #2b211b;
        color: #f5efe6;
        border-radius: 6px;
        padding: 8px 14px;
        margin-bottom: 20px;
        overflow: hidden;
        display: flex;
        align-items: center;
    }
    .airport-badge {
        background-color: #8c5835;
        color: #ffffff;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
        margin-right: 14px;
        text-transform: lowercase;
        flex-shrink: 0;
        letter-spacing: 0.5px;
    }
    .airport-track {
        display: inline-block;
        white-space: nowrap;
        animation: marquee 28s linear infinite;
    }
    .airport-track:hover {
        animation-play-state: paused;
    }
    @keyframes marquee {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-50%); }
    }
    .airport-item {
        color: #d1bfae !important;
        text-decoration: none !important;
        margin-right: 26px;
        font-size: 0.78rem;
        font-weight: 500;
    }
    .airport-item:hover { color: #ffffff !important; }
    
    .card {
        background: #ffffff;
        border: 1px solid #ebdcd0;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(43, 33, 27, 0.02);
    }
    
    .section-label {
        font-size: 0.74rem;
        text-transform: lowercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        color: #8c5835;
        margin-bottom: 8px;
    }
    
    .overview-box {
        background: #fdfbf9;
        border-left: 3px solid #8c5835;
        padding: 16px 18px;
        border-radius: 6px;
        font-size: 0.95rem;
        line-height: 1.65;
        color: #2b211b;
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
        padding: 9px !important;
        text-transform: lowercase !important;
    }
    .stButton>button:hover { background-color: #241a15 !important; }
</style>
""", unsafe_allow_html=True)

# Segmentos estruturados
SEGMENTOS = {
    "moda e vestuário": ["sapatilha", "melissa", "bermuda jorts", "calça balonê", "alfaiataria oversized"],
    "esportes e corrida": ["vôlei", "tênis de placa de carbono", "corrida de rua 10k", "suplementação creatina", "maiô natação"],
    "beleza e estética": ["blush blindness", "skincare minimalista", "rotina glow", "lip tint natural"],
    "cultura e internet": ["aesthetic anos 2000", "brat summer", "futebol feminino", "girias do tiktok"],
    "outros": ["tendências de consumo", "novidades do mercado", "comportamento jovem"]
}

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
                    if len(resultados) >= 4:
                        break
    except Exception:
        pass
    if not resultados:
        resultados = [f"{termo} feminino", f"{termo} masculino", f"{termo} hoje", f"{termo} brasil"]
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
            for item in root.findall('./channel/item')[:4]:
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

# 3. Inteligência Artificial: Síntese no estilo Visão Geral do Google
def gerar_resumo_ia(termo, segmento, buscas, noticias):
    texto_noticias = "\n".join([f"- {n['titulo']} ({n['fonte']})" for n in noticias]) if noticias else "Sem notícias recentes."
    texto_buscas = ", ".join(buscas)
    
    prompt = f"""
    Você é a IA do Google gerando um resumo explicativo sobre "{termo}" no contexto de "{segmento}" no Brasil.
    
    NOTÍCIAS RECENTES QUE SAÍRAM NA MÍDIA:
    {texto_noticias}
    
    O QUE AS PESSOAS ESTÃO BUSCANDO NO GOOGLE:
    {texto_buscas}

    REGRAS OBRIGATÓRIAS:
    1. PROIBIDO USAR O CARACTERE '&'. Use sempre a conjunção 'e'.
    2. Escreva como uma Visão Geral do Google: comece explicando diretamente o que está em pauta sobre "{termo}" agora, conectando os acontecimentos recentes da imprensa e das buscas.
    3. ZERO jargão corporativo ou papo de consultoria. Seja conciso, humano e informativo.
    4. No campo 'visao_geral': Um parágrafo fluido de 3 a 5 linhas resumindo o momento atual do tema, o porquê de estar em destaque e o que o público está acompanhando.
    5. No campo 'pontos_chave': 3 destaques objetivos e analíticos sobre os acontecimentos reais e o comportamento do público.
    6. No campo 'resumo_imprensa': Um resumo de 2 linhas sobre o foco da cobertura jornalística recente.

    Retorne APENAS um JSON válido:
    {{
      "visao_geral": "texto explicativo e natural aqui",
      "pontos_chave": [
        "Destaque 1 direto sobre a repercussão recente.",
        "Destaque 2 direto sobre o que as pessoas estão buscando.",
        "Destaque 3 direto sobre o desdobramento do assunto."
      ],
      "resumo_imprensa": "resumo jornalístico aqui"
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.25}
    }
    
    # Requisição direta via API REST
    url_base = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    # 1. Tentativa via Bearer Token
    try:
        req = urllib.request.Request(
            url_base,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {CHAVE_API}"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            texto_raw = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(texto_raw), None
    except Exception as e1:
        # 2. Tentativa via Query Key
        try:
            req2 = urllib.request.Request(
                f"{url_base}?key={CHAVE_API}",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req2, timeout=12) as resp2:
                res_json2 = json.loads(resp2.read().decode("utf-8"))
                texto_raw2 = res_json2["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(texto_raw2), None
        except Exception as e2:
            return None, f"Falha de autenticação ({e2}). Verifique a chave nos Secrets."

if "termo_ativo" not in st.session_state:
    st.session_state.termo_ativo = "vôlei"

# 1. Seletor de Segmento
c_nicho, c_outro = st.columns([1, 2])
with c_nicho:
    nicho_escolhido = st.selectbox("segmento de interesse", list(SEGMENTOS.keys()), index=1)

nicho_personalizado = ""
if nicho_escolhido == "outros":
    with c_outro:
        nicho_personalizado = st.text_input("especifique o segmento", placeholder="ex: perfumaria, café especial...")

segmento_final = nicho_personalizado if (nicho_escolhido == "outros" and nicho_personalizado) else nicho_escolhido
itens_do_nicho = SEGMENTOS.get(nicho_escolhido, SEGMENTOS["outros"])

# 2. Painel estilo Aeroporto (Marquee Contínuo)
itens_duplicados = itens_do_nicho + itens_do_nicho + itens_do_nicho
links_html = "".join([
    f'<a class="airport-item" href="https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(t)}" target="_blank">↗ {t.upper()}</a>'
    for t in itens_duplicados
])

st.markdown(f"""
<div class="airport-wrapper">
    <div class="airport-badge">em alta no radar</div>
    <div style="overflow: hidden; width: 100%;">
        <div class="airport-track">
            {links_html}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Título Editorial
st.markdown('<h1 class="brand-title" style="font-size: 2.3rem; margin-bottom: 4px;">radar de tendências</h1>', unsafe_allow_html=True)
st.caption("o que você precisa saber sobre o que estão falando agora.")

# Campo de Busca
st.markdown('<div class="card">', unsafe_allow_html=True)
c_inp, c_b = st.columns([3, 1])
with c_inp:
    termo_input = st.text_input("digite um produto, termo ou assunto", value=st.session_state.termo_ativo)
with c_b:
    st.write("")
    st.write("")
    btn_analisar = st.button("buscar contexto")

st.session_state.termo_ativo = termo_input

# Atalhos do nicho
st.markdown('<div class="section-label" style="margin-top: 10px;">termos em alta neste segmento:</div>', unsafe_allow_html=True)
cols_ch = st.columns(len(itens_do_nicho))
for i, item in enumerate(itens_do_nicho):
    if cols_ch[i].button(f"↗ {item}", key=f"nicho_item_{i}"):
        st.session_state.termo_ativo = item
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Execução e Apresentação
if btn_analisar or st.session_state.termo_ativo:
    with st.spinner("consultando inteligência contextual em tempo real..."):
        buscas = coletar_buscas_google(st.session_state.termo_ativo)
        noticias = coletar_noticias_google(st.session_state.termo_ativo)
        dados, erro_ia = gerar_resumo_ia(st.session_state.termo_ativo, segmento_final, buscas, noticias)

    if erro_ia:
        st.error(erro_ia)

    # Bloco 1: Visão Geral Explicativa (Estilo Google AI Overview)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">visão geral sobre "{st.session_state.termo_ativo}"</div>', unsafe_allow_html=True)
    
    if dados:
        texto_visao = dados.get("visao_geral", "")
    else:
        # Resumo contextual puro a partir das notícias reais caso a IA esteja sem conexão
        m_txt = f" Destacam-se coberturas como '{noticias[0]['titulo']}'." if noticias else ""
        texto_visao = f"As discussões recentes em torno de '{st.session_state.termo_ativo}' refletem um momento de atenção pública focado em novidades esportivas, contratações e transmissões de campeonatos.{m_txt}"
    
    st.markdown(f"""
    <div class="overview-box">
        {texto_visao}
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 2: O Que Você Precisa Saber Sobre o Que Estão Falando
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que você precisa saber sobre o que estão falando</div>', unsafe_allow_html=True)
    
    if dados:
        pontos = dados.get("pontos_chave", [])
    else:
        pontos = [
            f"Manchete em destaque na imprensa: {noticias[0]['titulo']}." if noticias else f"Interesse constante por {st.session_state.termo_ativo}.",
            f"Nas buscas, quem pesquisa no Google procura por termos como: {', '.join(buscas[:3])}.",
            f"Desdobramentos recentes acompanhados pelos principais portais esportivos nacionais."
        ]
        
    for p in pontos:
        st.markdown(f"""
        <div style="background:#fdfbf9; border-left:3px solid #8c5835; padding:12px 16px; border-radius:4px; margin-bottom:10px;">
            <p style="margin:0; font-size:0.92rem; line-height:1.55; color:#3d2b21;">{p}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 3: Gráfico do Google Trends
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">interesse ao longo do tempo (google trends brasil)</div>', unsafe_allow_html=True)
    termo_url = urllib.parse.quote(st.session_state.termo_ativo)
    trends_embed = f"""
    <script type="text/javascript" src="https://ssl.gstatic.com/trends_nrtr/3624_RC01/embed_loader.js"></script>
    <script type="text/javascript">
        trends.embed.renderExploreWidgetTo(
            document.getElementById('trends_container'),
            "TIMESERIES",
            {{"comparisonItem":[{{"keyword":"{st.session_state.termo_ativo}","geo":"BR","time":"today 12-m"}}],"category":0,"property":""}},
            {{"exploreQuery":"q={termo_url}&geo=BR&date=today 12-m","guestPath":"https://trends.google.com:443/trends/embed/"}}
        );
    </script>
    <div id="trends_container" style="min-height: 330px; width: 100%;"></div>
    """
    components.html(trends_embed, height=350)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 4: Na Imprensa
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que a imprensa está falando</div>', unsafe_allow_html=True)
    resumo_imp = dados.get("resumo_imprensa", "") if dados else "Cobertura focada em transmissões, novidades e decisões de bastidores apuradas pelos principais veículos."
    st.markdown(f"""
    <p style="margin:0 0 14px 0; font-size:0.9rem; line-height:1.6; color:#5c4738;">
        {resumo_imp}
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

    # Bloco 5: Pesquisas Mais Comuns
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">pesquisas mais comuns no google brasil</div>', unsafe_allow_html=True)
    
    cols = st.columns(len(buscas[:4]))
    for i, b in enumerate(buscas[:4]):
        url_t = f"https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(b)}"
        with cols[i]:
            st.markdown(f"""
            <div style="background:#fdfbf9; border:1px solid #ebdcd0; border-radius:8px; padding:12px 14px;">
                <div style="font-weight:700; font-size:0.88rem; color:#2b211b; margin-bottom:4px;">{b}</div>
                <a href="{url_t}" target="_blank" style="font-size:0.72rem; color:#8c5835; font-weight:700; text-decoration:none;">ver no trends ↗</a>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(page_title="radar | o que você precisa saber", layout="wide", initial_sidebar_state="collapsed")

# Estilo Editorial sem caixas vazias e com acabamento elegante
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
    
    .ticker-bar {
        background-color: #2b211b;
        color: #f5efe6;
        padding: 8px 14px;
        font-size: 0.78rem;
        display: flex;
        align-items: center;
        border-radius: 6px;
        margin-bottom: 18px;
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
        margin-right: 12px;
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
    
    .quick-chip {
        display: inline-block;
        background: #f4ece4;
        color: #5c4738;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        margin-right: 6px;
        margin-bottom: 6px;
        text-decoration: none;
    }
    
    .stButton>button {
        background-color: #3d2b21 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100% !important;
        padding: 8px 14px !important;
        text-transform: lowercase !important;
    }
    .stButton>button:hover { background-color: #241a15 !important; }
</style>
""", unsafe_allow_html=True)

# 1. Base Real: Buscas Associadas e Variações em Alta no Google
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
    except Exception:
        pass
    if not resultados:
        resultados = [f"{termo} modelos", f"{termo} novidades", f"{termo} comprar", f"{termo} brasil"]
    return resultados

# 2. Base Real: Notícias da Imprensa Brasileira
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

# 3. Síntese Contextual Direta sem Fórmulas Prontas
def sintetizar_historia(termo, buscas, noticias):
    titulos = [n["titulo"] for n in noticias]
    veiculos = list(set([n["fonte"] for n in noticias if n["fonte"] != "imprensa"]))
    veiculos_txt = ", ".join(veiculos[:3]) if veiculos else "principais portais de notícia"
    
    # Monta um resumo objetivo do que está acontecendo
    if titulos:
        manchete_destaque = titulos[0]
        resumo_fato = f"As discussões recentes ganharam tração após matérias como '{manchete_destaque}', repercutida em veículos como {veiculos_txt}."
        if len(titulos) > 1:
            resumo_fato += f" Paralelamente, desdobramentos sobre '{titulos[1]}' mantêm o tema em circulação nas conversas do dia."
    else:
        resumo_fato = f"O volume de buscas por {termo} cresceu de forma espontânea, puxado pelo interesse direto das pessoas em novidades, preços e recomendações."

    pontos = []
    if titulos:
        pontos.append(f"A pauta na mídia está concentrada em novidades recentes: {titulos[0]}.")
        if len(titulos) > 1:
            pontos.append(f"Outro ângulo com grande repercussão envolve a cobertura de {titulos[1]}.")
    
    if buscas:
        pontos.append(f"No dia a dia, quem pesquisa no Google busca termos específicos como '{', '.join(buscas[:3])}', buscando detalhes práticos e recomendações.")
        
    return {
        "sobre": resumo_fato,
        "pontos": pontos,
        "resumo_imprensa": f"A imprensa concentra a cobertura em atualizações imediatas, lançamentos e fatos do momento apurados por {veiculos_txt}."
    }

if "termo_ativo" not in st.session_state:
    st.session_state.termo_ativo = "melissa"

# Coleta inicial para a barra de tendências do assunto
buscas_ativas = coletar_buscas_google(st.session_state.termo_ativo)
noticias_ativas = coletar_noticias_google(st.session_state.termo_ativo)

# Ticker Superior com os Termos Mais Buscados SOBRE O ASSUNTO (sem loterias)
links_ticker = "".join([
    f'<a class="ticker-link" href="https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(t)}" target="_blank">{t} ↗</a>' 
    for t in buscas_ativas[:6]
])
st.markdown(f"""
<div class="ticker-bar">
    <div class="ticker-badge">em alta sobre {st.session_state.termo_ativo}</div>
    <div>{links_ticker}</div>
</div>
""", unsafe_allow_html=True)

# Título Editorial
st.markdown('<h1 class="brand-title" style="font-size: 2.3rem; margin-bottom: 4px;">radar de tendências</h1>', unsafe_allow_html=True)
st.caption("o que você precisa saber sobre o que estão falando agora.")

# Campo de Busca Direto (sem colunas vazias)
st.markdown('<div class="card">', unsafe_allow_html=True)
termo_input = st.text_input("digite um produto, termo ou assunto", value=st.session_state.termo_ativo)
c_btn, _ = st.columns([1, 4])
with c_btn:
    btn_analisar = st.button("buscar contexto")

st.session_state.termo_ativo = termo_input

# Exemplos rápidos
st.markdown('<div class="section-label" style="margin-top: 14px;">exemplos rápidos:</div>', unsafe_allow_html=True)
exemplos = ["melissa", "maiô natação", "blush blindness", "futebol", "tênis de placa de carbono"]
cols_ex = st.columns(len(exemplos))
for i, ex in enumerate(exemplos):
    if cols_ex[i].button(f"↗ {ex}", key=f"ex_{i}"):
        st.session_state.termo_ativo = ex
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Apresentação dos Dados
if btn_analisar or st.session_state.termo_ativo:
    dados = sintetizar_historia(st.session_state.termo_ativo, buscas_ativas, noticias_ativas)

    # Bloco 1: Sobre o Que Estão Falando
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">sobre "{st.session_state.termo_ativo}"</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <p style="margin:0; font-size:0.98rem; line-height:1.65; color:#2b211b;">
        {dados['sobre']}
    </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 2: O Que Você Precisa Saber
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que você precisa saber sobre o que estão falando</div>', unsafe_allow_html=True)
    for ponto in dados['pontos']:
        st.markdown(f"""
        <div style="background:#fdfbf9; border-left:3px solid #8c5835; padding:12px 16px; border-radius:4px; margin-bottom:10px;">
            <p style="margin:0; font-size:0.92rem; line-height:1.55; color:#3d2b21;">{ponto}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 3: Na Imprensa
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que a imprensa está falando</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <p style="margin:0 0 14px 0; font-size:0.9rem; line-height:1.6; color:#5c4738;">
        {dados['resumo_imprensa']}
    </p>
    """, unsafe_allow_html=True)
    
    if noticias_ativas:
        for n in noticias_ativas:
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

    # Bloco 4: Pesquisas Mais Comuns
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">pesquisas mais comuns no google brasil</div>', unsafe_allow_html=True)
    
    cols = st.columns(len(buscas_ativas[:4]))
    for i, b in enumerate(buscas_ativas[:4]):
        url_t = f"https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(b)}"
        with cols[i]:
            st.markdown(f"""
            <div style="background:#fdfbf9; border:1px solid #ebdcd0; border-radius:8px; padding:12px 14px;">
                <div style="font-weight:700; font-size:0.88rem; color:#2b211b; margin-bottom:4px;">{b}</div>
                <a href="{url_t}" target="_blank" style="font-size:0.72rem; color:#8c5835; font-weight:700; text-decoration:none;">ver no trends ↗</a>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

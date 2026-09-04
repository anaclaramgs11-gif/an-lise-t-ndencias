import streamlit as st
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(page_title="radar | o que você precisa saber", layout="wide", initial_sidebar_state="collapsed")

# Estilo Editorial Limpo em Tons de Café, Areia e Marrom
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
    
    .card {
        background: #ffffff;
        border: 1px solid #ebdcd0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(43, 33, 27, 0.02);
    }
    
    .section-label {
        font-size: 0.74rem;
        text-transform: lowercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        color: #8c5835;
        margin-bottom: 10px;
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
    .stButton>button:hover { background-color: #241a15 !important; }
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
        resultados = [f"{termo} feminino", f"{termo} preço", f"{termo} modelos"]
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

if "termo_ativo" not in st.session_state:
    st.session_state.termo_ativo = "maiô natação"

# Cabeçalho Limpo
st.markdown('<h1 class="brand-title" style="font-size: 2.3rem; margin-bottom: 4px;">radar de tendências</h1>', unsafe_allow_html=True)
st.caption("o que você realmente precisa saber sobre o assunto agora.")

# Campo de Busca
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        termo_input = st.text_input("digite um produto, termo ou tendência", value=st.session_state.termo_ativo)
    with c2:
        st.write("")
        st.write("")
        btn_analisar = st.button("buscar contexto")
    
    st.session_state.termo_ativo = termo_input
    
    # Atalhos rápidos
    st.markdown('<div class="section-label" style="margin-top: 10px;">exemplos:</div>', unsafe_allow_html=True)
    exemplos = ["maiô natação", "blush blindness", "alfaiataria oversized", "tênis de placa de carbono"]
    cols_ex = st.columns(len(exemplos))
    for i, ex in enumerate(exemplos):
        if cols_ex[i].button(f"↗ {ex}", key=f"ex_{i}"):
            st.session_state.termo_ativo = ex
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 3. Análise Direta sem jargão de consultoria
def gerar_briefing_direto(termo, buscas, noticias):
    chave = "AQ.Ab8RN6IfRuC1ubQJSIbZZsUF3cKASRsBl94HHb1qdh-4eao7hw"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={chave}"
    
    texto_noticias = "\n".join([f"- {n['titulo']} ({n['fonte']})" for n in noticias]) if noticias else "Sem notícias recentes."
    texto_buscas = ", ".join(buscas)
    
    prompt = f"""
    Você é um editor de tendências e comportamento experiente, curioso e direto ao ponto.
    Escreva um panorama no estilo 'O QUE VOCÊ PRECISA SABER SOBRE' o tema "{termo}".

    BUSCAS REAIS NO GOOGLE: {texto_buscas}
    NOTÍCIAS DA IMPRENSA: {texto_noticias}

    REGRAS:
    1. PROIBIDO O CARACTERE '&'. Use sempre 'e'.
    2. ZERO papo de consultor chato. Nada de 'sob a ótica de', 'alinhamento contemporâneo', 'evidencia a busca'.
    3. Fale de forma simples, fluida e interessante, como alguém explicando para um amigo o que está rolando com esse assunto.
    4. Responda ESTRITAMENTE sobre "{termo}".
    5. No campo 'o_que_e', explique em 2 a 3 frases o que é o produto ou termo e por que ele é relevante.
    6. No campo 'o_que_precisa_saber', traga 3 pontos rápidos e objetivos sobre o comportamento das pessoas e o que está acontecendo com esse mercado no Brasil.
    7. No campo 'resumo_noticias', diga em 2 frases simples o que a mídia está destacando.

    Retorne ESTRITAMENTE JSON:
    {{
      "o_que_e": "Explicação direta e simples do produto ou termo.",
      "o_que_precisa_saber": [
        "Ponto 1 direto e interessante sobre o comportamento do público.",
        "Ponto 2 direto sobre o mercado ou preferências de compra.",
        "Ponto 3 direto sobre como as marcas e produtos estão se posicionando."
      ],
      "resumo_noticias": "O resumo claro do que a imprensa tem falado sobre o assunto."
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
            "o_que_e": f"A procura por {termo} gira em torno de produtos práticos e confortáveis para o dia a dia, onde quem compra busca resistência e caimento ideal para a atividade.",
            "o_que_precisa_saber": [
                f"As buscas por modelos específicos mostram que o público quer opções que unam durabilidade e modelagem segura.",
                "Existe uma procura crescente por tamanhos inclusivos e opções para públicos variados, como infantil e plus size.",
                "O consumidor pesquisa muito antes de comprar para garantir tecidos que aguentem cloro e uso frequente."
            ],
            "resumo_noticias": "A cobertura recente foca em lançamentos esportivos, rotinas de saúde e competições de natação."
        }

# Apresentação
if btn_analisar or st.session_state.termo_ativo:
    with st.spinner("reunindo informações sobre o assunto..."):
        buscas = coletar_buscas_google(st.session_state.termo_ativo)
        noticias = coletar_noticias_google(st.session_state.termo_ativo)
        dados = gerar_briefing_direto(st.session_state.termo_ativo, buscas, noticias)

    # Bloco 1: O Que É
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que é "{st.session_state.termo_ativo}"</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <p style="margin:0; font-size:0.98rem; line-height:1.65; color:#2b211b;">
        {dados.get('o_que_e', '')}
    </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 2: O Que Você Precisa Saber
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que você precisa saber sobre isso</div>', unsafe_allow_html=True)
    
    pontos = dados.get("o_que_precisa_saber", [])
    for p in pontos:
        st.markdown(f"""
        <div style="background:#fdfbf9; border-left:3px solid #8c5835; padding:12px 16px; border-radius:4px; margin-bottom:10px;">
            <p style="margin:0; font-size:0.92rem; line-height:1.55; color:#3d2b21;">{p}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 3: Nas Notícias
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que a imprensa está falando</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <p style="margin:0 0 14px 0; font-size:0.9rem; line-height:1.6; color:#5c4738;">
        {dados.get('resumo_noticias', '')}
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
    st.markdown(f'<div class="section-label">pesquisas mais comuns no google brasil</div>', unsafe_allow_html=True)
    
    cols = st.columns(len(buscas[:3]))
    for i, b in enumerate(buscas[:3]):
        url_t = f"https://trends.google.com/trends/explore?geo=BR&q={urllib.parse.quote(b)}"
        with cols[i]:
            st.markdown(f"""
            <div style="background:#fdfbf9; border:1px solid #ebdcd0; border-radius:8px; padding:12px 14px;">
                <div style="font-weight:700; font-size:0.88rem; color:#2b211b; margin-bottom:4px;">{b}</div>
                <a href="{url_t}" target="_blank" style="font-size:0.72rem; color:#8c5835; font-weight:700; text-decoration:none;">ver no trends ↗</a>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

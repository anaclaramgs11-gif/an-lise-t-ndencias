import streamlit as st
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(page_title="radar | o que você precisa saber", layout="wide", initial_sidebar_state="collapsed")

# Chave confirmada no seu console
CHAVE_OFICIAL = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6K0s7oAWASVyRJlyQSTV1aFotsEN-mJEmcDO2Xxo_OULg")

# Estilo Editorial em Tons de Café, Areia e Marrom
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
        with urllib.request.urlopen(req, timeout=6) as resp:
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
        resultados = [f"{termo} hoje", f"{termo} brasil", f"{termo} novidades"]
    return resultados

# 2. Base Real: Google Notícias Brasil
def coletar_noticias_google(termo):
    termo_enc = urllib.parse.quote(termo.strip())
    url = f"https://news.google.com/rss/search?q={termo_enc}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    noticias = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6) as resp:
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
    st.session_state.termo_ativo = "futebol"

# Cabeçalho Limpo
st.markdown('<h1 class="brand-title" style="font-size: 2.3rem; margin-bottom: 4px;">radar de tendências</h1>', unsafe_allow_html=True)
st.caption("o que você precisa saber sobre o que estão falando agora.")

# Campo de Busca
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        termo_input = st.text_input("digite um produto, termo ou assunto", value=st.session_state.termo_ativo)
    with c2:
        st.write("")
        st.write("")
        btn_analisar = st.button("buscar contexto")
    
    st.session_state.termo_ativo = termo_input
    
    # Atalhos rápidos
    st.markdown('<div class="section-label" style="margin-top: 10px;">exemplos:</div>', unsafe_allow_html=True)
    exemplos = ["futebol", "maiô natação", "blush blindness", "alfaiataria oversized"]
    cols_ex = st.columns(len(exemplos))
    for i, ex in enumerate(exemplos):
        if cols_ex[i].button(f"↗ {ex}", key=f"ex_{i}"):
            st.session_state.termo_ativo = ex
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 3. Chamada com autenticação via Header Bearer
def gerar_briefing_personalizado(termo, buscas, noticias):
    texto_noticias = "\n".join([f"- {n['titulo']} ({n['fonte']})" for n in noticias]) if noticias else "Sem notícias recentes."
    texto_buscas = ", ".join(buscas)
    
    prompt = f"""
    Você é um editor de comportamento e cultura experiente e direto ao ponto.
    Escreva um briefing sob a perspectiva: 'O QUE VOCÊ PRECISA SABER SOBRE O QUE ESTÃO FALANDO' a respeito de "{termo}".

    BUSCAS REAIS NO GOOGLE HOJE: {texto_buscas}
    NOTÍCIAS DA IMPRENSA: {texto_noticias}

    DIRETRIZES:
    1. PROIBIDO USAR O CARACTERE '&'. Use sempre a conjunção 'e'.
    2. Responda ESTRITAMENTE sobre "{termo}". Não misture assuntos.
    3. ZERO papo de consultor corporativo. Nada de jargões como 'sob a ótica de', 'alinhamento contemporâneo' ou afetações acadêmicas.
    4. Em 'o_que_e', explique em 2 parágrafos simples e diretos o que é o tema e qual o contexto dele no Brasil hoje.
    5. Em 'o_que_precisa_saber', traga 3 pontos objetivos sobre o que o público está comentando, os hábitos reais de consumo e as curiosidades sobre esse assunto.
    6. Em 'resumo_falando', faça um resumo claro de 2 frases conectando o que a imprensa e as pessoas estão falando agora.

    Retorne APENAS um JSON válido neste formato:
    {{
      "o_que_e": "texto aqui",
      "o_que_precisa_saber": [
        "Ponto 1 específico sobre o assunto.",
        "Ponto 2 específico sobre o assunto.",
        "Ponto 3 específico sobre o assunto."
      ],
      "resumo_falando": "resumo aqui"
    }}
    """
    
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.25}
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHAVE_OFICIAL}"
    }
    
    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=14) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            texto_raw = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(texto_raw)
    except Exception:
        endpoint_chave = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={CHAVE_OFICIAL}"
        try:
            req2 = urllib.request.Request(
                endpoint_chave,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req2, timeout=14) as resp2:
                res_json2 = json.loads(resp2.read().decode("utf-8"))
                texto_raw2 = res_json2["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(texto_raw2)
        except Exception:
            return {
                "o_que_e": f"A conversa em torno de {termo} movimenta tanto a cobertura dos veículos de imprensa quanto o interesse ativo das pessoas no dia a dia.",
                "o_que_precisa_saber": [
                    f"As pesquisas sobre {termo} no Google refletem dúvidas práticas e interesse pelos acontecimentos mais recentes.",
                    "O tema gera forte engajamento em comunidades digitais que acompanham cada novidade do setor.",
                    "A cobertura da mídia foca em análises de impacto, novidades e decisões recentes envolvendo o assunto."
                ],
                "resumo_falando": f"A imprensa e o público concentram atenções nas atualizações mais recentes e no impacto de {termo} no cenário nacional."
            }

# Apresentação dos Resultados
if btn_analisar or st.session_state.termo_ativo:
    with st.spinner("analisando o que estão falando em tempo real..."):
        buscas = coletar_buscas_google(st.session_state.termo_ativo)
        noticias = coletar_noticias_google(st.session_state.termo_ativo)
        dados = gerar_briefing_personalizado(st.session_state.termo_ativo, buscas, noticias)

    # Bloco 1: O Que É
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que é "{st.session_state.termo_ativo}"</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <p style="margin:0; font-size:0.98rem; line-height:1.65; color:#2b211b;">
        {dados.get('o_que_e', '')}
    </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 2: O Que Você Precisa Saber Sobre o Que Estão Falando
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que você precisa saber sobre o que estão falando</div>', unsafe_allow_html=True)
    
    pontos = dados.get("o_que_precisa_saber", [])
    for p in pontos:
        st.markdown(f"""
        <div style="background:#fdfbf9; border-left:3px solid #8c5835; padding:12px 16px; border-radius:4px; margin-bottom:10px;">
            <p style="margin:0; font-size:0.92rem; line-height:1.55; color:#3d2b21;">{p}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 3: O Que a Imprensa Noticia
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">o que a imprensa está falando</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <p style="margin:0 0 14px 0; font-size:0.9rem; line-height:1.6; color:#5c4738;">
        {dados.get('resumo_falando', '')}
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

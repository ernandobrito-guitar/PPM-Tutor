import streamlit as st
import os
import app as backend

# Configuração da página Web
st.set_page_config(
    page_title="PPM - Professor Pessoal de Música",
    page_icon="🎸",
    layout="wide"
)

# Inicializa pastas necessárias
backend.inicializar_estrutura()

st.title("🎸 PPM - Professor Pessoal de Música")
st.caption("Seu tutor inteligente de teoria, harmonia e prática musical em qualquer lugar")

# Gerenciamento da chave de API
api_key = st.secrets.get("GEMINI_API_KEY", "") if "GEMINI_API_KEY" in st.secrets else ""

if not api_key:
    api_key = st.sidebar.text_input("Insira sua Gemini API Key:", type="password")

if not api_key:
    st.warning("⚠️ Por favor, insira a sua Gemini API Key na barra lateral para ativar o tutor.")
    st.stop()

# Configura o modelo
model = backend.configurar_gemini(api_key)

# Inicializa o histórico de chat na sessão do usuário
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu Professor Pessoal de Música. O que vamos estudar hoje? (Teoria, escalas, harmonia, campo harmônico...)"}
    ]

# Sidebar - Biblioteca de Materiais
st.sidebar.header("📁 Biblioteca de Estudos")
uploaded_files = st.sidebar.file_uploader(
    "Envie materiais (PDF, MP3, WAV, MP4)",
    accept_multiple_files=True,
    type=["pdf", "mp3", "wav", "mp4"]
)

if uploaded_files:
    for file in uploaded_files:
        caminho_salvo = os.path.join(backend.BIBLIOTECA_DIR, file.name)
        with open(caminho_salvo, "wb") as f:
            f.write(file.getbuffer())
        st.sidebar.success(f"Salvo: {file.name}")

# Exibe o histórico do Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Caixa de Entrada do Aluno
if prompt := st.chat_input("Digite sua dúvida musical ou peça um exercício..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando na resposta didática..."):
            resposta = backend.gerar_resposta_tutor(model, prompt, st.session_state.messages)
            st.write(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})

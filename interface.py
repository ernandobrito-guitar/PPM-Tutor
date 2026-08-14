import os
import glob
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Configuração da página
st.set_page_config(page_title="PPM - Professor Pessoal de Música", page_icon="🎸", layout="wide")

# Recupera a API Key do Streamlit Secrets ou do menu lateral
gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.header("⚙️ Configurações")
    if not gemini_api_key:
        gemini_api_key = st.text_input("Insira sua Gemini API Key:", type="password")
    else:
        st.success("🔑 API Key carregada com sucesso!")

    st.markdown("---")
    st.header("📚 Biblioteca Fixa")

# Função para ler todos os materiais da pasta 'conhecimento'
def carregar_base_conhecimento():
    texto_acumulado = ""
    pasta = "conhecimento"
    
    if not os.path.exists(pasta):
        return texto_acumulado

    # Busca arquivos PDF e TXT na pasta conhecimento
    arquivos_pdf = glob.glob(os.path.join(pasta, "*.pdf"))
    arquivos_txt = glob.glob(os.path.join(pasta, "*.txt"))
    
    # Processa PDFs
    for pdf in arquivos_pdf:
        try:
            reader = PdfReader(pdf)
            for page in reader.pages:
                extraido = page.extract_text()
                if extraido:
                    texto_acumulado += f"\n--- Fonte: {os.path.basename(pdf)} ---\n" + extraido
        except Exception as e:
            st.sidebar.error(f"Erro ao ler {os.path.basename(pdf)}: {e}")

    # Processa TXTs
    for txt in arquivos_txt:
        if os.path.basename(txt) == "LEAME.txt":
            continue
        try:
            with open(txt, "r", encoding="utf-8") as f:
                texto_acumulado += f"\n--- Fonte: {os.path.basename(txt)} ---\n" + f.read()
        except Exception as e:
            st.sidebar.error(f"Erro ao ler {os.path.basename(txt)}: {e}")

    return texto_acumulado

# Título da Aplicação
st.title("🎸 PPM - Professor Pessoal de Música")
st.caption("Seu tutor inteligente de teoria, harmonia e prática musical carregado com sua biblioteca personalizada.")

if not gemini_api_key:
    st.warning("⚠️ Por favor, insira a sua Gemini API Key na barra lateral para ativar o tutor.")
    st.stop()

# Configura o Gemini
genai.configure(api_key=gemini_api_key)

# Carrega a base de conhecimento permanente
base_conhecimento = carregar_base_conhecimento()

if base_conhecimento:
    st.sidebar.info("✅ Base de conhecimento fixa carregada!")
else:
    st.sidebar.warning("ℹ️ Nenhuma apostila encontrada na pasta 'conhecimento'.")

# Prompt de sistema definindo o comportamento do Tutor
system_instruction = f"""
Você é o PPM (Professor Pessoal de Música), um tutor especialista, didático e encorajador.
Sua missão é ensinar teoria musical, harmonia, campo harmônico, escalas (incluindo pentatônica), tríades, acordes e prática de instrumentos.

Regras de Atuação:
1. Responda de forma clara, bem estruturada e fácil de entender.
2. Utilize SEMPRE como prioridade máxima a Base de Conhecimento Fixa fornecida abaixo para responder às perguntas sobre acordes, tríades, pentatônicas e teoria.
3. Se a informação estiver na Base de Conhecimento, explique com base nela. Se não estiver na base, responda usando seu conhecimento musical geral, mantendo a mesma didática.

=== BASE DE CONHECIMENTO FIXA (SEUS MATERIAIS DE ESTUDO) ===
{base_conhecimento}
=========================================================
"""

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Chave 'GEMINI_API_KEY' não encontrada nos st.secrets!")
    st.stop()

# Inicializa o modelo Gemini
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# Inicializa ou Reinicia o Chat
if "chat" not in st.session_state or st.sidebar.button("🔄 Reiniciar Conversa"):
    st.session_state.chat = model.start_chat(history=[])

# Exibe mensagens anteriores do chat
for message in st.session_state.chat.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.write(message.parts[0].text)

# Mensagem de boas-vindas inicial se o chat estiver vazio
if len(st.session_state.chat.history) == 0:
    with st.chat_message("assistant"):
        st.write("Olá! Sou seu Professor Pessoal de Música. Já li sua biblioteca de estudos e estou pronto. O que vamos estudar hoje? (Acordes, tríades, pentatônicas, campo harmônico...)")

# Campo de entrada do usuário
if user_input := st.chat_input("Digite sua dúvida musical aqui..."):
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analisando sua dúvida e consultando sua biblioteca..."):
            response = st.session_state.chat.send_message(user_input)
            st.write(response.text)

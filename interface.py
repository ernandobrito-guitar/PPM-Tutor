import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

st.set_page_config(page_title="Personal Music Professor", page_icon="🎸")
st.title("🎸 Personal Music Professor")
st.markdown("Seu tutor de guitarra e teoria musical baseado na sua biblioteca de estudos.")

# 1. Configuração da API Key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Chave GEMINI_API_KEY não encontrada nos Secrets!")
    st.stop()

# 2. Leitura da Base de Conhecimento (PDFs)
@st.cache_data
def carregar_base():
    texto = ""
    pasta = "data"
    if os.path.exists(pasta):
        for arq in os.listdir(pasta):
            if arq.endswith(".pdf"):
                try:
                    reader = PyPDF2.PdfReader(os.path.join(pasta, arq))
                    for pag in reader.pages:
                        texto += pag.extract_text() + "\n"
                except Exception:
                    pass
    return texto

base_conhecimento = carregar_base()

system_instruction = f"""
Você é o Personal Music Professor (PPM), especialista em guitarra e teoria musical.
Responda sempre com clareza e priorize as informações da base de conhecimento abaixo:

=== BASE DE CONHECIMENTO ===
{base_conhecimento}
"""

# 3. Modelo do Gemini
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# 4. Inicializa o Histórico do Chat na Memória
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe histórico de mensagens da tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Mensagem inicial se a tela estiver limpa
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.write("Olá! Sou seu Professor Pessoal de Música. Já li suas apostilas e estou pronto. O que vamos estudar hoje?")

# 5. Processa novas mensagens do usuário
if user_input := st.chat_input("Pergunte sobre acordes, tríades, pentatônicas..."):
    # Mostra mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # Gera resposta direta do Gemini
    try:
        # Prepara o histórico para o modelo
        prompt_completo = user_input
        response = model.generate_content(user_input)
        
        with st.chat_message("assistant"):
            st.write(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Erro ao obter resposta da API: {e}")

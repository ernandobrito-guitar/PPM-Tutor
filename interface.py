import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

st.set_page_config(page_title="Personal Music Professor", page_icon="🎸")
st.title("🎸 Personal Music Professor")
st.markdown("Seu tutor de guitarra e teoria musical baseado na sua biblioteca de estudos.")

# 1. Autenticação na API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Chave GEMINI_API_KEY não encontrada nos Secrets!")
    st.stop()

# 2. Leitura dos PDFs da pasta 'data'
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

# 3. Inicialização do Modelo Gemini Pro (Compatível universalmente)
model = genai.GenerativeModel("gemini-pro")

# 4. Histórico da conversa
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.write("Olá! Sou seu Professor Pessoal de Música. Já li suas apostilas e estou pronto. O que vamos estudar hoje?")

# 5. Envio de Pergunta
if user_input := st.chat_input("Pergunte sobre acordes, tríades, pentatônicas..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # Monta o prompt injetando a biblioteca de PDFs
    prompt_completo = f"""
Você é o Personal Music Professor (PPM), especialista em guitarra e teoria musical.
Use a base de conhecimento abaixo para responder à pergunta do aluno.

=== BASE DE CONHECIMENTO (APOSTILAS DO ALUNO) ===
{base_conhecimento}
=================================================

Pergunta do aluno: {user_input}
"""
    try:
        response = model.generate_content(prompt_completo)
        with st.chat_message("assistant"):
            st.write(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Erro na API: {e}")

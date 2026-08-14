import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Personal Music Professor",
    page_icon="🎸",
    layout="wide"
)

st.title("🎸 Personal Music Professor")
st.markdown("Seu tutor de guitarra e teoria musical baseado na sua biblioteca de estudos.")

# 1. Autenticação na API do Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Chave GEMINI_API_KEY não encontrada nos Secrets do Streamlit!")
    st.stop()

# 2. Leitura da Base de Conhecimento (PDFs)
@st.cache_data
def carregar_base_conhecimento():
    texto_acumulado = ""
    pasta_pdf = "data"  # Nome da pasta onde estão seus PDFs no repositório
    
    if os.path.exists(pasta_pdf):
        for arquivo in os.listdir(pasta_pdf):
            if arquivo.endswith(".pdf"):
                caminho_pdf = os.path.join(pasta_pdf, arquivo)
                try:
                    with open(caminho_pdf, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        for pagina in reader.pages:
                            texto_acumulado += pagina.extract_text() + "\n"
                except Exception as e:
                    st.warning(f"Não foi possível ler o arquivo {arquivo}: {e}")
    return texto_acumulado

base_conhecimento = carregar_base_conhecimento()

# 3. Prompt do Sistema
system_instruction = f"""
Você é o Personal Music Professor (PPM), um tutor especialista em guitarra, violão, tríades, pentatônicas e teoria musical.
Regras de Atuação:
1. Responda de forma clara, bem estruturada e fácil de entender.
2. Utilize SEMPRE como prioridade máxima a Base de Conhecimento Fixa fornecida abaixo para responder às perguntas sobre acordes, tríades, pentatônicas e teoria.
3. Se a informação estiver na Base de Conhecimento, explique com base nela. Se não estiver, responda usando seu conhecimento musical geral, mantendo a mesma didática.

=== BASE DE CONHECIMENTO FIXA (SEUS MATERIAIS DE ESTUDO) ===
{base_conhecimento}
===========================================================
"""

# 4. Inicialização do Modelo Gemini com Fallback (Tentativas automáticas)
@st.cache_resource
def obter_modelo_gemini():
    # Lista de nomes de modelos suportados em ordem de preferência
    modelos_para_testar = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "models/gemini-1.5-flash"
    ]
    
    for nome_modelo in modelos_para_testar:
        try:
            m = genai.GenerativeModel(
                model_name=nome_modelo,
                system_instruction=system_instruction
            )
            # Testa uma chamada simples rápida para ver se o modelo realmente responde
            m.generate_content("teste")
            return m
        except Exception:
            continue
            
    st.error("❌ Não foi possível conectar a nenhum modelo Gemini disponível. Verifique se sua chave no AI Studio tem permissões ativas.")
    st.stop()

model = obter_modelo_gemini()

# 5. Gerenciamento da Sessão do Chat
if "chat" not in st.session_state or st.sidebar.button("🔄 Reiniciar Conversa"):
    st.session_state.chat = model.start_chat(history=[])

# 6. Exibição das mensagens do histórico
for message in st.session_state.chat.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.write(message.parts[0].text)

# Mensagem de boas-vindas inicial se o chat estiver vazio
if len(st.session_state.chat.history) == 0:
    with st.chat_message("assistant"):
        st.write("Olá! Sou seu Professor Pessoal de Música. Já li sua biblioteca de estudos e estou pronto. O que vamos estudar hoje?")

# 7. Entrada de Pergunta do Usuário
if user_input := st.chat_input("Pergunte algo sobre teoria, acordes ou suas apostilas..."):
    with st.chat_message("user"):
        st.write(user_input)
    
    try:
        response = st.session_state.chat.send_message(user_input)
        with st.chat_message("assistant"):
            st.write(response.text)
    except Exception as e:
        st.error(f"Erro ao processar resposta da API: {e}")

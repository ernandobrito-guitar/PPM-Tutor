import os
import google.generativeai as genai

BIBLIOTECA_DIR = "biblioteca_estudos"

def inicializar_estrutura():
    """Garante que a estrutura de diretórios para materiais existe."""
    if not os.path.exists(BIBLIOTECA_DIR):
        os.makedirs(BIBLIOTECA_DIR)

def configurar_gemini(api_key: str):
    """Configura o SDK do Gemini com a chave fornecida."""
    if api_key:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-pro-latest')
    return None

def gerar_resposta_tutor(model, prompt: str, historico: list) -> str:
    """Envia a dúvida do aluno para o Gemini com o contexto de Tutor de Música."""
    system_instruction = (
        "Você é o PPM (Professor Pessoal de Música), um tutor didático, motivador "
        "e especialista em teoria musical, prática de instrumentos e harmonia. "
        "Responda de forma clara, estruturada e encorajadora."
    )
    
    try:
        chat = model.start_chat(history=[])
        response = model.generate_content(f"{system_instruction}\n\nAluno: {prompt}")
        return response.text
    except Exception as e:
        return f"Erro ao consultar o Professor Pessoal de Música: {str(e)}"

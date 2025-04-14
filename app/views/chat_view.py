import streamlit as st
from app.services.chat_service import chat_with_tools

def render():
    """
    Renderiza la vista de chat con el asistente de IA
    """
    st.title("💬 HALion: Asistente IA con herramientas")
    
    # Mostrar mensajes del chat
    for msg in st.session_state.chat:
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant"):
            st.markdown(msg["bot"])

    # Input del usuario
    prompt = st.chat_input("¿En qué puedo ayudarte hoy?")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    # Obtener API key y configuración del estado de la sesión
                    api_key = st.session_state.get("api_key", "")
                    model_config = st.session_state.get("model_config", {
                        "model": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 1024,
                        "top_p": 1.0,
                        "presence_penalty": 0.0,
                        "frequency_penalty": 0.0,
                        "seed": None
                    })
                    
                    # Llamar al ejecutor con los parámetros
                    reply = chat_with_tools(
                        prompt,
                        user_id="anon",
                        api_key=api_key,
                        model=model_config["model"],
                        temperature=model_config["temperature"],
                        max_tokens=model_config["max_tokens"],
                        top_p=model_config["top_p"],
                        presence_penalty=model_config["presence_penalty"],
                        frequency_penalty=model_config["frequency_penalty"],
                        seed=model_config["seed"]
                    )
                    st.markdown(reply)
                except Exception as e:
                    st.error(f"❌ Lo siento, ha ocurrido un error: {str(e)}")
                    reply = f"Error: {str(e)}"

        # Guardar en el historial
        st.session_state.chat.append({"user": prompt, "bot": reply}) 
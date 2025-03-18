import streamlit as st
import os
import openai
from dotenv import load_dotenv
load_dotenv() 

openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.api_key = (os.getenv("AZURE_OPENAI_API_KEY"))
deployment = "gpt-4o"

search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_api_key = (os.getenv("AZURE_SEARCH_KEY"))
search_index  = "index-chatbot-in-a-day"
def get_completion_from_messages(user_message) -> str:

    completion = openai.ChatCompletion.create(
    deployment_id=deployment,
    messages=[
        {
                "role": "system",
                "content": "Eres un asistente que responde preguntas basadas en los documentos proporcionados. Asegúrate de incluir citas en tus respuestas."
        },
        {
            "role": "user",
            "content": user_message
        }
    ],
    data_sources= [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": search_endpoint,
                    "index_name": search_index,
                    "authentication": {
                        "type": "api_key",
                        "key": search_api_key
                    }
                }
            }
        ]
    
)

    # Imprimir la respuesta completa en JSON para depuración
    #print(completion.model_dump_json(indent=2))

    # Renderizar las citas en el contenido de la respuesta
    content = completion.choices[0].message.content
    context = completion.choices[0].message.context
    referencias = []
    for citation_index, citation in enumerate(context.get("citations", [])):
        citation_reference = f"[doc{citation_index + 1}]"
        # Opcionalmente, puedes quitar el marcador del contenido si se encuentra
        content = content.replace(citation_reference, "")
        url = citation["url"]
        filepath = citation.get("filepath", "Sin título")
        title = citation.get("title", "")
        snippet = citation.get("content", "")
        chunk_id = citation.get("chunk_id", "")
        # Crear el HTML o formato que prefieras para la referencia
        referencia_html = (
            f"{citation_reference} "
            f"<a href='{url}' title='{title}\n{snippet}'>"
            f"(Ver en archivo {filepath}, Parte {chunk_id})"
            f"</a>"
        )
        referencias.append(referencia_html)

    # Agregar las referencias al final del contenido
    


    a = completion
    b = a.choices[0].message.content
    #if referencias:
    #   b += "\n\nReferencias:\n" + "\n".join(referencias)
    return b

print(deployment)

# ─── TÍTULO E INSTRUCCIONES ─────────────────────────────────────────────────────────
st.title("💬 Chatbot con Azure OpenAI y Azure Cognitive Search")
st.caption("Este chatbot utiliza integración on your data para responder basado en documentos.")

# ─── INICIALIZAR HISTORIAL DE MENSAJES ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": "Eres un asistente que responde preguntas basadas en los documentos proporcionados. Asegúrate de incluir citas en tus respuestas."
        },
        {"role": "assistant", "content": "¿En qué puedo ayudarte?"}
    ]

# Mostrar el historial de mensajes
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# ─── ENTRADA DEL USUARIO ───────────────────────────────────────────────────────────
if prompt := st.chat_input("Escribe tu pregunta:"):

    # Agregar el mensaje del usuario al historial y mostrarlo.
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Obtener la respuesta mediante la función creada.
    response = get_completion_from_messages(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
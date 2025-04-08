def send_email(to: str, subject: str, body: str) -> str:
    return f"Correo enviado a {to} con asunto '{subject}'"

schema = {
    "name": "send_email",
    "description": "Envía un correo electrónico simulado",
    "parameters": {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Correo de destino"},
            "subject": {"type": "string", "description": "Asunto del mensaje"},
            "body": {"type": "string", "description": "Contenido del mensaje"}
        },
        "required": ["to", "subject", "body"]
    }
}

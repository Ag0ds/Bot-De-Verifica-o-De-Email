import os
from groq import Groq, BadRequestError

_client = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY não configurado")
        _client = Groq(api_key=api_key)
    return _client

def suggest_with_groq(subject: str, text: str) -> str:
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    prompt = (
        "Você é um assistente de atendimento ao cliente. "
        "Escreva uma resposta curta, objetiva e cordial em PT-BR ao e-mail abaixo. "
        "Se pedir status, peça número do protocolo; se anexos, confirme recebimento; "
        "se erro técnico, solicite detalhes mínimos. Não invente dados.\n\n"
        f"Assunto: {subject}\n\n"
        f"Corpo:\n{text}\n\n"
        "Responda apenas com o texto do e-mail (sem rótulos)."
    )
    client = _get_client()
    base_kwargs = dict(
        model=model,
        messages=[
            {"role": "system", "content": "Você escreve e-mails profissionais e concisos em português."},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.3,
    )
    try:
        resp = client.chat.completions.create(max_completion_tokens=300, **base_kwargs)
    except TypeError:
        resp = client.chat.completions.create(max_tokens=300, **base_kwargs)
    except BadRequestError as e:
        raise RuntimeError(
            f"Erro da Groq: {e}. Tente definir GROQ_MODEL=llama-3.3-70b-versatile ou llama-3.1-8b-instant no .env."
        )
    return resp.choices[0].message.content.strip()
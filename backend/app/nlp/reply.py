def suggest_reply(category: str, text: str) -> str:
    t = (text or "").lower()

    if category == "Produtivo":
        
        if any(k in t for k in ["status", "protocolo", "andamento", "ticket", "chamado"]):
            return (
                "Olá! Recebemos sua solicitação de atualização de status. "
                "Para agilizar, por favor confirme o número do protocolo/ticket e, se possível, o CPF/CNPJ do cadastro. "
                "Assim que recebermos as informações, retornaremos com o andamento."
            )
        if any(k in t for k in ["anexo", "comprovante", "arquivo", "documento", "segue em anexo"]):
            return (
                "Olá! Arquivo recebido com sucesso. "
                "Encaminhamos para análise e retornaremos com os próximos passos. "
                "Se houver algum detalhe adicional (ex.: nº do pedido), por favor informe neste e-mail."
            )
        if any(k in t for k in ["erro", "falha", "indispon", "acesso", "reset de senha", "bloqueio"]):
            return (
                "Olá! Sentimos pelo inconveniente. "
                "Poderia detalhar o cenário (passo a passo, prints, horário) e informar seu e-mail de acesso e nº de protocolo (se existir)? "
                "Com isso, direcionamos a correção com prioridade."
            )
        return (
            "Olá! Obrigado pelo contato. "
            "Para direcionarmos rapidamente, poderia compartilhar o nº de protocolo/ticket e um breve contexto do pedido? "
            "Ficamos à disposição."
        )

    # Improdutivo
    return (
        "Olá! Agradecemos a mensagem. "
        "Se precisar de suporte ou tiver alguma solicitação, estamos à disposição por este canal."
    )

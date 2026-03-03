from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/v1/emprestimos/escrituracoes-remuneracoes")
def get_mock_data(
        dataHoraInicio: str = Query(...),
        dataHoraFim: str = Query(...),
        nroPagina: int = Query(1),
        simularErro: bool = Query(False)
):
    if simularErro:
        return JSONResponse(
            status_code=400,
            content={
                "type": "https://tools.ietf.org/html/rfc9110#section-15.5.1",
                "title": "One or more validation errors occurred.",
                "status": 400,
                "errors": {"numeroInscricaoEmpregador": ["The field is required."]},
                "traceId": "00-1605160a11..."
            }
        )

    registros_por_pagina = 250
    total_paginas = 4
    total_registros = total_paginas * registros_por_pagina

    conteudo = []

    # --- INSERÇÃO DOS DADOS DA IMAGEM (PÁGINA 1) ---
    if nroPagina == 1:
        # Dados extraídos da sua imagem (amostra dos primeiros itens)
        dados_reais = [
            {"id": 1001, "idEv": 101, "vParc": 527.42, "desc": "Evento de remuneração periódico"},
            {"id": 1002, "idEv": 102, "vParc": 1135.45, "desc": "Evento de remuneração periódico"},
            {"id": 1003, "idEv": 103, "vParc": 2825.46, "desc": "Evento de remuneração periódico"},
            {"id": 1004, "idEv": 104, "vParc": 1131.21, "desc": "Evento de remuneração periódico"},
            {"id": 1012, "idEv": 112, "vParc": 1128.73, "desc": "Evento de remuneração afastamento", "codTipo": 1},
        ]

        for item in dados_reais:
            conteudo.append({
                "id": item["id"],
                "idEvento": item["idEv"],
                "periodoReferencia": 202601,
                "codigoIF": 393,
                "contrato": "44",  # Exemplo da imagem
                "valorParcelaDesconto": item["vParc"],
                "cpf": 11153706008,
                "inscricaoEmpregador": {"codigo": 1, "descricao": "CNPJ"},
                "numeroInscricaoEmpregador": 3495672000103,
                "matricula": "150220241",
                "dataHoraInclusaoDataprev": "010220260800",
                "emprestimo": {"codigoIf": 393, "contrato": "44", "valorParcela": item["vParc"]},
                "analise": {
                    "existeTrabalhadorEscriturado": True,
                    "existeNumeroContratoEscriturado": True,
                    "vinculoCorreto": True,
                    "instituicaoFinanceiraCorreta": True,
                    "valorParcelaCorreta": True,
                    "dadosCorrespondentes": True
                },
                "tipoEventoESocial": {
                    "codigo": item.get("codTipo", 0),
                    "descricao": item["desc"]
                }
            })

    # --- PREENCHIMENTO AUTOMÁTICO PARA COMPLETAR A PÁGINA ---
    restante = registros_por_pagina - len(conteudo)
    for i in range(restante):
        # Garante que os IDs automáticos não colidam com os manuais se desejar
        registro_id = ((nroPagina - 1) * registros_por_pagina) + len(conteudo) + 1

        conteudo.append({
            "id": registro_id,
            "idEvento": 100,
            "periodoReferencia": 202602,
            "codigoIF": 393,
            "contrato": "10001",
            "valorParcelaDesconto": 10.0,
            "cpf": 11153706008,
            "inscricaoEmpregador": {"codigo": 1, "descricao": "CNPJ"},
            "numeroInscricaoEmpregador": 3495672000103,
            "matricula": "11153706008",
            "dataHoraInclusaoDataprev": "22022026195013",
            "emprestimo": {"codigoIf": 393, "contrato": "10001", "valorParcela": 300},
            "analise": {
                "existeTrabalhadorEscriturado": True,
                "existeNumeroContratoEscriturado": True,
                "vinculoCorreto": True,
                "instituicaoFinanceiraCorreta": True,
                "valorParcelaCorreta": True,
                "dadosCorrespondentes": True
            },
            "tipoEventoESocial": {"codigo": 0, "descricao": "Evento de remuneração periódico"}
        })

    return {
        "nroPaginaAtual": nroPagina,
        "nroTotalPaginas": total_paginas,
        "nroTotalRegistros": total_registros,
        "qtdRegistrosPorPagina": registros_por_pagina,
        "qtdRegistrosPaginaAtual": len(conteudo),
        "dataHoraInicio": dataHoraInicio,
        "dataHoraFim": dataHoraFim,
        "conteudo": conteudo
    }
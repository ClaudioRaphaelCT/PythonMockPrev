from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse # Importe separado aqui

app = FastAPI()


@app.get("/v1/emprestimos/escrituracoes-remuneracoes")
def get_mock_data(
        dataHoraInicio: str = Query(...),
        dataHoraFim: str = Query(...),
        nroPagina: int = Query(1),
        simularErro: bool = Query(False)  # Adicionei este gatilho para você testar o 400
):
    # --- GATILHO PARA TESTAR O ERRO 400 ---
    # Se você adicionar &simularErro=true na URL, ele retorna o erro que você pediu
    if simularErro:
        return JSONResponse(
            status_code=400,
            content={
                "type": "https://tools.ietf.org/html/rfc9110#section-15.5.1",
                "title": "One or more validation errors occurred.",
                "status": 400,
                "errors": {
                    "numeroInscricaoEmpregador": ["The numeroInscricaoEmpregador field is required."]
                },
                "traceId": "00-1605160a1163d80e1f461ca223fef4ce-548fbb1d0d0dab68-00"
            }
        )

    # --- LÓGICA DE PAGINAÇÃO OK ---
    total_paginas = 4
    registros_por_pagina = 250

    # Se pedir uma página que não existe (ex: 5)
    if nroPagina > total_paginas:
        return {
            "nroPaginaAtual": nroPagina,
            "nroTotalPaginas": total_paginas,
            "nroTotalRegistros": total_paginas * registros_por_pagina,
            "conteudo": []
        }

    conteudo = []
    for i in range(registros_por_pagina):
        # O ID muda conforme a página: Pag 1 (1-250), Pag 2 (251-500)...
        registro_id = ((nroPagina - 1) * registros_por_pagina) + i + 1

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
                "vinculoCorreto": True,
                "valorParcelaCorreta": (i % 2 == 0),
                "dadosCorrespondentes": True
            },
            "tipoEventoESocial": {"codigo": 0, "descricao": "Evento de remuneração periódico"}
        })

    return {
        "nroPaginaAtual": nroPagina,
        "nroTotalPaginas": total_paginas,
        "nroTotalRegistros": total_paginas * registros_por_pagina,
        "qtdRegistrosPorPagina": registros_por_pagina,
        "qtdRegistrosPaginaAtual": len(conteudo),
        "dataHoraInicio": dataHoraInicio,
        "dataHoraFim": dataHoraFim,
        "conteudo": conteudo
    }
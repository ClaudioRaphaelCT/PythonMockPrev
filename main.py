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
        return JSONResponse(status_code=400, content={"status": 400, "title": "Erro"})

    # --- CONFIGURAÇÃO PARA TESTAR PAGINAÇÃO ---
    registros_por_pagina = 20 # Conforme sua planilha
    total_paginas = 4         # Vamos colocar 4 páginas para você testar o scroll
    total_registros = 80     # Total fictício maior para forçar a paginação

    # Se a página solicitada não existir
    if nroPagina > total_paginas:
        return {"nroPaginaAtual": nroPagina, "conteudo": []}

    conteudo = []

    # --- SE FOR A PÁGINA 1: INSERIR OS 12 REAIS DA PLANILHA ---
    if nroPagina == 1:
        raw_data = [
            [1001, 101, "48", 527.42, 44900000000, "150220241", 0, "Evento de remuneração periódico"],
            [1002, 102, "53", 1135.45, 25274606075, "150220241", 0, "Evento de remuneração periódico"],
            [1003, 103, "445", 2825.46, 44900000000, "150220241", 0, "Evento de remuneração periódico"],
            [1004, 104, "45", 1131.21, 44900000000, "150220241", 0, "Evento de remuneração periódico"],
            [1005, 105, "65", 1122.69, 99813582073, "150220241", 0, "Evento de remuneração periódico"],
            [1006, 106, "444", 1830.38, 44900000000, "150220241", 0, "Evento de remuneração periódico"],
            [1007, 107, "44", 1131.21, 44900000000, "150220241", 0, "Evento de remuneração periódico"],
            [1008, 108, "49", 1111.22, 44900000000, "150220241", 0, "Evento de remuneração periódico"],
            [1009, 109, "50", 600.88, 24189796018, "150220241", 0, "Evento de remuneração periódico"],
            [1010, 110, "33", 2833.22, 44900000000, "150220241", 0, "Evento de remuneração periódico"],
            [1011, 111, "46", 1131.21, 59271637003, "150220241", 0, "Evento de remuneração periódico"],
            [1012, 112, "40", 1128.73, 44900000000, "150220241", 1, "Evento de remuneração afastamento"],
        ]

        for row in raw_data:
            conteudo.append(self_build_item(row)) # Usa os dados da planilha

    # --- COMPLEMENTAR A PÁGINA (ATÉ CHEGAR EM 25) OU GERAR PÁGINAS 2, 3... ---
    inicio_loop = len(conteudo)
    for i in range(inicio_loop, registros_por_pagina):
        # Gera IDs automáticos que não batem com os seus (ex: 2000 em diante)
        idx_fake = ((nroPagina - 1) * registros_por_pagina) + i + 2000
        fake_row = [idx_fake, 200, "9999", 10.50, 11153706008, "999999", 0, "Evento Automático"]
        conteudo.append(self_build_item(fake_row))

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

def self_build_item(row):
    """Função auxiliar para montar o JSON de cada item"""
    return {
        "id": row[0],
        "idEvento": row[1],
        "periodoReferencia": 202601,
        "codigoIF": 393,
        "contrato": row[2],
        "valorParcelaDesconto": row[3],
        "cpf": row[4],
        "inscricaoEmpregador": {"codigo": 1, "descricao": "CNPJ"},
        "numeroInscricaoEmpregador": 3495672000103,
        "matricula": row[5],
        "dataHoraInclusaoDataprev": "010220260800",
        "emprestimo": {"codigoIf": 393, "contrato": row[2], "valorParcela": row[3]},
        "analise": {
            "existeTrabalhadorEscriturado": True,
            "existeNumeroContratoEscriturado": True,
            "vinculoCorreto": True,
            "instituicaoFinanceiraCorreta": True,
            "valorParcelaCorreta": True,
            "dadosCorrespondentes": True
        },
        "tipoEventoESocial": {"codigo": row[6], "descricao": row[7]}
    }
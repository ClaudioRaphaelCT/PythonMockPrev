import csv
import os
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

app = FastAPI()

CSV_PATH = os.path.join(os.getcwd(), "dados.csv")


def to_int(value):
    """Converte string/float/notação científica para inteiro."""
    if not value:
        return 0

    try:
        return int(float(str(value).replace(",", ".")))
    except:
        return 0


def to_float(value):
    """Converte valores monetários para float."""
    if not value:
        return 0.0

    try:
        v = str(value).strip().replace('"', '')

        # Caso venha no formato BR
        if "," in v:
            v = v.replace(".", "").replace(",", ".")

        return float(v)

    except:
        return 0.0


def to_bool(value):
    return str(value).strip().upper() == "TRUE"


def carregar_dados_csv():
    if not os.path.exists(CSV_PATH):
        return None

    dados = []

    with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")

        reader.fieldnames = [c.strip().replace('"', '') for c in reader.fieldnames]

        for row in reader:
            clean_row = {
                k.strip(): (v.strip().replace('"', '') if v else "")
                for k, v in row.items()
                if k
            }

            if any(clean_row.values()):
                dados.append(clean_row)

    return dados


@app.get("/v1/emprestimos/escrituracoes-remuneracoes")
def get_mock_data(
        dataHoraInicio: str = Query(...),
        dataHoraFim: str = Query(...),
        nroPagina: int = Query(1)
):

    registros = carregar_dados_csv()

    if registros is None:
        return JSONResponse(
            status_code=500,
            content={"error": "dados.csv nao encontrado"}
        )

    conteudo = []

    for item in registros:

        id_raw = item.get("id") or item.get("ID")
        if not id_raw:
            continue

        conteudo.append({

            "id": to_int(id_raw),

            "idEvento": to_int(item.get("idEvento")),

            "periodoReferencia": 202312,

            "codigoIF": 393,

            "contrato": item.get("contrato", ""),

            # AGORA PEGANDO O CAMPO CORRETO
            "valorParcelaDesconto": to_float(item.get("valorParcelaDesconto")),

            "cpf": to_int(item.get("cpf")),

            "inscricaoEmpregador": {
                "codigo": 1,
                "descricao": "CNPJ"
            },

            "numeroInscricaoEmpregador": 3495672000103,

            "matricula": item.get("matricula", ""),

            "dataHoraInclusaoDataprev": str(
                to_int(item.get("dataHoraInclusaoDataprev"))
            ) or "20260301195013",

            "emprestimo": {
                "codigoIf": 393,
                "contrato": item.get("contrato", ""),
                "valorParcela": to_float(item.get("valorParcela"))
            },

            "analise": {
                "existeTrabalhadorEscriturado": to_bool(item.get("existeTrabalhadorEscriturado")),
                "existeNumeroContratoEscriturado": to_bool(item.get("existeNumeroContratoEscriturado")),
                "vinculoCorreto": to_bool(item.get("vinculoCorreto")),
                "instituicaoFinanceiraCorreta": to_bool(item.get("instituicaoFinanceiraCorreta")),
                "valorParcelaCorreta": to_bool(item.get("valorParcelaCorreta")),
                "dadosCorrespondentes": to_bool(item.get("dadosCorrespondentes")),
            },

            "tipoEventoESocial": {
                "codigo": to_int(item.get("codigo")),
                "descricao": item.get("descricaoEvento", "Evento de remuneração periódico")
            }

        })

    return JSONResponse(
        content={
            "nroPaginaAtual": nroPagina,
            "nroTotalPaginas": 1,
            "nroTotalRegistros": len(conteudo),
            "qtdRegistrosPorPagina": 250,
            "qtdRegistrosPaginaAtual": len(conteudo),
            "dataHoraInicio": dataHoraInicio,
            "dataHoraFim": dataHoraFim,
            "conteudo": conteudo
        },
        headers={"Cache-Control": "no-cache"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
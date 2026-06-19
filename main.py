import csv
import os
from random import randint
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

CSV_PATH = os.path.join(os.getcwd(), "dados.csv")
REGISTROS_POR_PAGINA = 80
TOTAL_PAGINAS = 2


# --- Utilitários de Conversão ---
def to_int(value):
    if not value: return 0
    try:
        return int(float(str(value).replace(",", ".")))
    except:
        return 0


def to_float(value):
    if not value: return 0.0
    try:
        v = str(value).strip().replace('"', '')
        if "," in v:
            v = v.replace(".", "").replace(",", ".")
        return float(v)
    except:
        return 0.0


def to_bool(value):
    return str(value).strip().upper() == "TRUE"


# --- Carregamento de Dados ---
def carregar_dados_csv():
    if not os.path.exists(CSV_PATH):
        return []
    dados = []
    with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')
        reader.fieldnames = [c.strip().replace('"', '') for c in reader.fieldnames]
        for row in reader:
            clean_row = {k.strip(): (v.strip().replace('"', '') if v else "")
                         for k, v in row.items() if k}
            if any(clean_row.values()):
                dados.append(clean_row)
    return dados


@app.get("/v1/emprestimos/escrituracoes-remuneracoes")
def get_mock_data(
        dataHoraInicio: str = Query(...),
        dataHoraFim: str = Query(...),
        nroPagina: int = Query(1)
):
    conteudo = []

    # LÓGICA DE PAGINAÇÃO
    if nroPagina == 1:
        registros = carregar_dados_csv()
        for item in registros:
            id_raw = item.get("id") or item.get("ID")
            if not id_raw: continue

            # Mapeamento de todas as chaves do bloco 'analise' (Chave JSON: Coluna CSV)
            mapeamento_analise = {
                "existeTrabalhadorEscriturado": "existeTrabalhadorEscriturado",
                "existeNumeroContratoEscriturado": "existeNumeroContratoEscriturado",
                "vinculoCorreto": "vinculoCorreto",
                "instituicaoFinanceiraCorreta": "instituicaoFinanceiraCorreta",
                "valorParcelaCorreta": "valorParcelaCorreta",
                "dadosCorrespondentes": "dadosCorrespondentes"
            }

            analise_dict = {}

            # Loop que valida campo por campo do bloco analise
            for chave_json, coluna_csv in mapeamento_analise.items():
                valor_original = item.get(coluna_csv)

                # Se o campo contiver dados (não for vazio nem None), ele entra no JSON
                if valor_original:
                    analise_dict[chave_json] = to_bool(valor_original)

            # 1. Primeiro montamos a base do registro do item
            registro_formatado = {
                "id": to_int(id_raw),
                "idEvento": to_int(item.get("idEvento")),
                "periodoReferencia": 202401,
                "codigoIF": 393,
                "contrato": item.get("contrato", ""),
                "valorParcelaDesconto": to_float(item.get("valorParcelaDesconto")),
                "cpf": to_int(item.get("cpf")),
                "inscricaoEmpregador": {"codigo": 1, "descricao": "CNPJ"},
                "numeroInscricaoEmpregador": 3495672000103,
                "matricula": item.get("matricula", ""),
                "dataHoraInclusaoDataprev": str(to_int(item.get("dataHoraInclusaoDataprev"))),
                "emprestimo": {
                    "codigoIf": 393,
                    "contrato": item.get("contrato", ""),
                    "valorParcela": to_float(item.get("valorParcela"))
                },
                "tipoEventoESocial": {
                    "codigo": to_int(item.get("codigo")),
                    "descricao": item.get("descricaoEvento", "Evento de remuneração periódico")
                }
            }

            # 2. SE o dicionário de análise tiver dados (não estiver vazio), nós o injetamos no registro
            if analise_dict:
                registro_formatado["analise"] = analise_dict

            # 3. Adiciona o objeto final na lista do conteúdo
            conteudo.append(registro_formatado)

    elif 1 < nroPagina <= TOTAL_PAGINAS:
        # GERAR MOCK PARA PÁGINAS 2 EM DIANTE
        for _ in range(REGISTROS_POR_PAGINA):
            conteudo.append({
                "id": randint(2000, 9000),
                "idEvento": randint(100, 200),
                "periodoReferencia": 202312,
                "codigoIF": 393,
                "contrato": "99999",
                "valorParcelaDesconto": round(randint(100, 2000) + 0.55, 2),
                "cpf": randint(10000000000, 99999999999),
                "inscricaoEmpregador": {"codigo": 1, "descricao": "CNPJ"},
                "numeroInscricaoEmpregador": 3495672000103,
                "matricula": str(randint(10000000, 99999999)),
                "dataHoraInclusaoDataprev": "20240215101013",
                "emprestimo": {
                    "codigoIf": 393,
                    "contrato": "99999",
                    "valorParcela": round(randint(100, 2000) + 0.22, 2)
                },
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

    total_csv = len(carregar_dados_csv()) if nroPagina == 1 else 0

    return {
        "nroPaginaAtual": nroPagina,
        "nroTotalPaginas": TOTAL_PAGINAS,
        "nroTotalRegistros": 2250 + (total_csv if nroPagina == 1 else 68),
        "qtdRegistrosPorPagina": REGISTROS_POR_PAGINA,
        "qtdRegistrosPaginaAtual": len(conteudo),
        "dataHoraInicio": dataHoraInicio,
        "dataHoraFim": dataHoraFim,
        "conteudo": conteudo
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
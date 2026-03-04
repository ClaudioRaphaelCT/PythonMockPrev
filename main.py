import csv
import os
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

app = FastAPI()

CSV_PATH = os.path.join(os.getcwd(), "dados.csv")


def carregar_dados_csv():
    dados = []
    if not os.path.exists(CSV_PATH):
        return None

    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
        # Lemos o conteúdo e removemos aspas duplas que o Excel coloca em colunas
        content = f.read().replace('"', '')
        f.seek(0)

        # Usamos o delimitador ';' que é o que aparece na sua imagem
        reader = csv.DictReader(content.splitlines(), delimiter=';')

        # Limpa espaços e possíveis aspas dos nomes das colunas
        reader.fieldnames = [name.strip().replace('"', '') for name in reader.fieldnames]

        for row in reader:
            # Limpa cada valor individualmente
            clean_row = {
                str(k).strip(): (str(v).strip() if v is not None else "")
                for k, v in row.items()
            }
            if any(clean_row.values()):  # Só adiciona se a linha não for totalmente vazia
                dados.append(clean_row)
    return dados


@app.get("/v1/emprestimos/escrituracoes-remuneracoes")
def get_mock_data(
        dataHoraInicio: str = Query(...),
        dataHoraFim: str = Query(...),
        nroPagina: int = Query(1)
):
    todos_registros = carregar_dados_csv()

    if todos_registros is None:
        return JSONResponse(status_code=500, content={"error": "Arquivo dados.csv nao encontrado."})

    conteudo = []
    for item in todos_registros:
        # Debug: Se ainda retornar vazio, descomente a linha abaixo para ver no console o que está chegando
        # print(f"Processando linha: {item}")

        try:
            # Mapeamento dinâmico baseado na sua imagem
            # Note que usamos chaves que ignoram maiúsculas/minúsculas se necessário
            reg_id = item.get('id') or item.get('ID') or item.get('\ufeffid')

            if not reg_id:
                continue

            conteudo.append({
                "id": int(reg_id),
                "idEvento": int(item.get('idEvento', 0)),
                "periodoReferencia": int(item.get('periodoReferencia', 0)),
                "codigoIF": int(item.get('codigoIF', 393)),
                "contrato": item.get('contrato', ''),
                "valorParcelaDesconto": float(item.get('valorParcelaDesconto', '0').replace(',', '.')),
                "cpf": int(item.get('cpf', 0)),
                "inscricaoEmpregador": {"codigo": 1, "descricao": "CNPJ"},
                "numeroInscricaoEmpregador": int(item.get('numeroInscricaoEmpregador', 0)),
                "matricula": item.get('matricula', ''),
                "dataHoraInclusaoDataprev": item.get('dataHoraInclusaoDataprev', ''),
                "emprestimo": {
                    "codigoIf": int(item.get('codigoIF', 393)),
                    "contrato": item.get('contrato', ''),
                    "valorParcela": 300.0
                },
                "analise": {
                    "existeTrabalhadorEscriturado": str(item.get('existeTrabalhadorEscriturado', '')).upper() == 'TRUE',
                    "existeNumeroContratoEscriturado": str(
                        item.get('existeNumeroContratoEscriturado', '')).upper() == 'TRUE',
                    "vinculoCorreto": str(item.get('vinculoCorreto', '')).upper() == 'TRUE',
                    "instituicaoFinanceiraCorreta": str(item.get('instituicaoFinanceiraCorreta', '')).upper() == 'TRUE',
                    "valorParcelaCorreta": str(item.get('valorParcelaCorreta', '')).upper() == 'TRUE',
                    "dadosCorrespondentes": str(item.get('dadosCorrespondentes', '')).upper() == 'TRUE'
                },
                "tipoEventoESocial": {"codigo": 0, "descricao": "Evento de remuneração periódico"}
            })
        except (ValueError, TypeError) as e:
            print(f"Erro ao converter linha: {e}")
            continue

    return {
        "nroPaginaAtual": nroPagina,
        "nroTotalPaginas": 1,
        "nroTotalRegistros": len(conteudo),
        "qtdRegistrosPorPagina": 250,
        "qtdRegistrosPaginaAtual": len(conteudo),
        "dataHoraInicio": dataHoraInicio,
        "dataHoraFim": dataHoraFim,
        "conteudo": conteudo
    }
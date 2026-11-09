from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory
import math
import os

from src.coordenadas import coordenadas, origem
from src.distancia import distancia_rota
from src.parser_lista import analisar_lista
from src.distribuicao import distribuir
from src import regras_obrigatorias

app = Flask(__name__)
CORS(app)  # permite o front (aberto no browser) chamar a API


def _dist_com_flag(fac, cache):
    """
    Distância (metros) da origem até a faculdade, com cache por requisição.
    Se a API de rota falhar, cai para linha reta — mas sinalizado
    ('estimada': True), nunca mascarado como rota real.
    """
    if fac in cache:
        return cache[fac]

    coord = coordenadas.get(fac)
    if coord is None:
        cache[fac] = {"metros": None, "estimada": False}
        return cache[fac]

    try:
        metros, _tempo = distancia_rota(origem, coord)
        cache[fac] = {"metros": metros, "estimada": False}
    except Exception:
        dy = coord[0] - origem[0]
        dx = coord[1] - origem[1]
        metros = math.sqrt(dx ** 2 + dy ** 2) * 111_000
        cache[fac] = {"metros": metros, "estimada": True}

    return cache[fac]


@app.route("/planejar", methods=["POST"])
def planejar():
    """
    Recebe:
      {
        "lista":    "<texto bruto do WhatsApp>",
        "veiculos": [{ "nome": "Ônibus 1", "capacidade": 50 }, ...]
      }

    Retorna (mesmo contrato do motor da AERJ):
      {
        "status": "SUCCESS" | "WARNING" | "CRITICAL",
        "critical": bool,
        "suggestion": { "veiculos", "sem_veiculo", "totais" } | null,
        "warnings": [string],
        "lista": { "data", "faculdades": [{nome, ida, volta, total}] }
      }

    "critical" true → "suggestion" null: a distribuição quebraria uma regra
    obrigatória (UNEX/UNEF separadas, UNIFAN com QUADRIVIUM, IFBA com UNEF)
    e o sistema não inventa uma saída — a decisão é humana.
    """
    body = request.get_json(force=True)

    lista_texto = (body.get("lista") or "").strip()
    frota_input = body.get("veiculos", [])

    if not lista_texto:
        return jsonify({"erro": "Campo 'lista' não pode ser vazio."}), 400
    if not frota_input:
        return jsonify({"erro": "Informe pelo menos um veículo."}), 400

    leitura = analisar_lista(lista_texto, coordenadas)
    dados = leitura["dados"]

    warnings = []
    for d in leitura["desconhecidas"]:
        warnings.append(
            f"Faculdade não reconhecida: {d['nome']} — {d['alunos']} aluno(s) ignorado(s)."
        )
    for fac in leitura["sem_coordenada"]:
        warnings.append(
            f"{fac} sem coordenada cadastrada — distância desconhecida, fica no fim da rota."
        )

    if not dados:
        return jsonify({"erro": "Nenhuma faculdade reconhecida na lista.", "warnings": warnings}), 422

    dist_cache = {}
    faculdades_ordenadas = sorted(
        dados.items(),
        key=lambda x: (_dist_com_flag(x[0], dist_cache)["metros"] or float("inf"))
    )

    resumo_lista = {
        "data": leitura["data"],
        "faculdades": [{"nome": fac, **info} for fac, info in faculdades_ordenadas],
    }

    veiculos_base = distribuir(
        faculdades_ordenadas,
        veiculos_config=[
            {"nome": v.get("nome", f"Veículo {i + 1}"), "capacidade": int(v.get("capacidade", 50))}
            for i, v in enumerate(frota_input)
        ]
    )

    resultado_regras = regras_obrigatorias.aplicar(veiculos_base)
    warnings.extend(resultado_regras["warnings"])

    if resultado_regras["critico"]:
        warnings.append(resultado_regras["motivo_critico"])
        return jsonify({
            "status": "CRITICAL",
            "critical": True,
            "suggestion": None,
            "warnings": warnings,
            "lista": resumo_lista,
        })

    veiculos_final = resultado_regras["veiculos"]

    facs_alocadas = {fac for v in veiculos_final for fac, _ in v["faculdades"]}
    sem_veiculo = [
        {"nome": fac, "ida": info["ida"], "volta": info["volta"], "total": info["total"]}
        for fac, info in faculdades_ordenadas
        if fac not in facs_alocadas
    ]
    if sem_veiculo:
        nomes = ", ".join(sv["nome"] for sv in sem_veiculo)
        warnings.append(f"Sem veículo com capacidade disponível para: {nomes}.")

    # UEFS é dividida entre veículos (não é bloco atômico), então "sem_veiculo"
    # não pega sobra PARCIAL dela — compara direto com a demanda original.
    uefs_original = next((info["total"] for fac, info in faculdades_ordenadas if fac == "UEFS"), 0)
    uefs_alocada = sum(
        info["total"] for v in veiculos_final for fac, info in v["faculdades"] if fac == "UEFS"
    )
    if uefs_alocada < uefs_original:
        sobra = uefs_original - uefs_alocada
        warnings.append(f"Sem capacidade suficiente na frota para {sobra} aluno(s) da UEFS.")
        sem_veiculo.append({"nome": "UEFS", "ida": None, "volta": None, "total": sobra})

    estimadas = set()
    resultado_veiculos = []
    for v in veiculos_final:
        facs = []
        for fac, info in v["faculdades"]:
            d = _dist_com_flag(fac, dist_cache)
            if d["estimada"]:
                estimadas.add(fac)
            facs.append({
                "nome": fac,
                "ida": info["ida"],
                "volta": info["volta"],
                "total": info["total"],
                "distancia_m": d["metros"],
                "rota_estimada": d["estimada"],
            })
        resultado_veiculos.append({
            "nome": v["nome"],
            "capacidade": v["capacidade"],
            "ocupado": v["ocupado"],
            "faculdades": facs,
        })
    for fac in sorted(estimadas):
        warnings.append(
            f"Distância até {fac} estimada em linha reta — rota real indisponível no momento."
        )

    total_alunos = sum(i["total"] for i in dados.values())
    total_ida = sum(f["ida"] for v in resultado_veiculos for f in v["faculdades"])
    total_volta = sum(f["volta"] for v in resultado_veiculos for f in v["faculdades"])
    veic_usados = sum(1 for v in resultado_veiculos if v["ocupado"] > 0)

    return jsonify({
        "status": "WARNING" if warnings else "SUCCESS",
        "critical": False,
        "suggestion": {
            "veiculos": resultado_veiculos,
            "sem_veiculo": sem_veiculo,
            "totais": {
                "alunos": total_alunos,
                "ida": total_ida,
                "volta": total_volta,
                "veiculos_usados": veic_usados,
            },
        },
        "warnings": warnings,
        "lista": resumo_lista,
    })


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_path = os.path.join(base_dir, "..", "frontend")
    return send_from_directory(frontend_path, "index.html")


@app.route("/<path:path>")
def static_files(path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_path = os.path.join(base_dir, "..", "frontend")
    return send_from_directory(frontend_path, path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

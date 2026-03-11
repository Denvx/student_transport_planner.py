from flask import Flask, request, jsonify
from flask_cors import CORS

from src.coordenadas import coordenadas, origem
from src.distancia import distancia_rota
from src.parser_lista import processar_lista
from src.distribuicao import distribuir

app = Flask(__name__)
CORS(app)  # permite o front (aberto no browser) chamar a API


@app.route("/planejar", methods=["POST"])
def planejar():
    """
    Recebe:
      {
        "lista":    "<texto bruto do WhatsApp>",
        "veiculos": [
          { "nome": "Ônibus 1", "capacidade": 50 },
          { "nome": "Van 1",    "capacidade": 20 }
        ]
      }

    Retorna:
      {
        "veiculos": [
          {
            "nome": "Ônibus 1",
            "capacidade": 50,
            "ocupado": 38,
            "faculdades": [
              { "nome": "UEFS", "ida": 8, "volta": 7, "total": 8, "distancia_m": 72400 }
            ]
          }
        ],
        "totais": { "alunos": 38, "ida": 22, "volta": 20, "veiculos_usados": 2 }
      }
    """
    body = request.get_json(force=True)

    lista_texto  = body.get("lista", "").strip()
    frota_input  = body.get("veiculos", [])

    if not lista_texto:
        return jsonify({"erro": "Campo 'lista' não pode ser vazio."}), 400

    if not frota_input:
        return jsonify({"erro": "Informe pelo menos um veículo."}), 400

    dados = processar_lista(lista_texto, coordenadas)

    if not dados:
        return jsonify({"erro": "Nenhuma faculdade reconhecida na lista."}), 422
    def _dist(fac):
        coord = coordenadas.get(fac)
        if coord is None:
            return float("inf")
        try:
            km, _ = distancia_rota(origem, coord)
            return km
        except Exception:
            import math
            dy = coord[0] - origem[0]
            dx = coord[1] - origem[1]
            return math.sqrt(dx**2 + dy**2) * 111_000  # metros

    faculdades_ordenadas = sorted(dados.items(), key=lambda x: _dist(x[0]))

    veiculos_base = distribuir(
        faculdades_ordenadas,
        veiculos_config=[
            {"nome": v.get("nome", f"Veículo {i+1}"), "capacidade": int(v.get("capacidade", 50))}
            for i, v in enumerate(frota_input)
        ]
    )

    facs_alocadas = {fac for v in veiculos_base for fac, _ in v["faculdades"]}
    sem_veiculo = [
        {"nome": fac, "ida": info["ida"], "volta": info["volta"], "total": info["total"]}
        for fac, info in faculdades_ordenadas
        if fac not in facs_alocadas
    ]
    for sv in sem_veiculo:
        app.logger.warning(f"Não coube em nenhum veículo: {sv['nome']}")

    dist_cache = {}

    def get_dist_m(fac):
        if fac not in dist_cache:
            coord = coordenadas.get(fac)
            if coord is None:
                dist_cache[fac] = None
            else:
                try:
                    km, _ = distancia_rota(origem, coord)
                    dist_cache[fac] = km
                except Exception:
                    import math
                    dy = coord[0] - origem[0]
                    dx = coord[1] - origem[1]
                    dist_cache[fac] = math.sqrt(dx**2 + dy**2) * 111_000
        return dist_cache[fac]

    resultado_veiculos = []
    for v in veiculos_base:
        facs = []
        for fac, info in v["faculdades"]:
            facs.append({
                "nome":        fac,
                "ida":         info["ida"],
                "volta":       info["volta"],
                "total":       info["total"],
                "distancia_m": get_dist_m(fac),
            })
        resultado_veiculos.append({
            "nome":       v["nome"],
            "capacidade": v["capacidade"],
            "ocupado":    v["ocupado"],
            "faculdades": facs,
        })

    total_alunos = sum(v["ocupado"] for v in resultado_veiculos)
    total_ida    = sum(f["ida"]   for v in resultado_veiculos for f in v["faculdades"])
    total_volta  = sum(f["volta"] for v in resultado_veiculos for f in v["faculdades"])
    veic_usados  = sum(1 for v in resultado_veiculos if v["ocupado"] > 0)

    return jsonify({
        "veiculos":     resultado_veiculos,
        "sem_veiculo":  sem_veiculo,
        "totais": {
            "alunos":          total_alunos,
            "ida":             total_ida,
            "volta":           total_volta,
            "veiculos_usados": veic_usados,
        }
    })


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
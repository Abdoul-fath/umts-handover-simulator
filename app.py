from flask import Flask, render_template, request, jsonify

from simulation import run_simulation, compare_simulations


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/simulate", methods=["POST"])
def simulate():
    try:
        data = request.get_json(force=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Aucun paramètre reçu."
            }), 400

        result = run_simulation(data)

        return jsonify({
            "success": True,
            "result": result
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except Exception as exc:
        print("Erreur simulation :", exc)

        return jsonify({
            "success": False,
            "error": "Erreur interne pendant la simulation."
        }), 500


@app.route("/api/compare", methods=["POST"])
def compare():
    try:
        data = request.get_json(force=True)

        scenarios = data.get("scenarios", [])

        if len(scenarios) < 2:
            return jsonify({
                "success": False,
                "error": "Enregistrez au moins deux configurations."
            }), 400

        result = compare_simulations(scenarios)

        return jsonify({
            "success": True,
            "result": result
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except Exception as exc:
        print("Erreur comparaison :", exc)

        return jsonify({
            "success": False,
            "error": "Erreur interne pendant la comparaison."
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
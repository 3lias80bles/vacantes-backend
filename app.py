from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({
        "mensaje": "Bienvenido a Vacantes App Backend",
        "estado": "funcionando"
    })


if __name__ == "__main__":
    app.run(debug=True)
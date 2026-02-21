from flask import Flask, request, jsonify

app = Flask(__name__)

logs_storage = []

@app.route('/logs', methods=['POST'])
def receive_logs():
    data = request.json
    logs_storage.append(data)
    if len(logs_storage) > 10:
        logs_storage.pop(0)
    print(f"Received Log: {data}", flush=True)
    return jsonify({"status": "accepted"}), 202

@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(logs_storage), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
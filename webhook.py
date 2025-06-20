from flask import Flask, request, jsonify, render_template, Response
import json
import os

app = Flask(__name__)

WEBHOOK_FILE = "webhooks.json"

# Save a webhook to file, including headers
def save_webhook(headers, body):
    webhook = {
        "headers": dict(headers),
        "body": body
    }
    with open(WEBHOOK_FILE, "a") as file:
        json.dump(webhook, file)
        file.write("\n")

# Load stored webhooks
def load_webhooks():
    if not os.path.exists(WEBHOOK_FILE):
        return []
    with open(WEBHOOK_FILE, "r") as file:
        return [json.loads(line) for line in file if line.strip()]

@app.route('/')
def index():
    webhooks = load_webhooks()
    return render_template('index.html', webhooks=webhooks[::-1])  # Show newest first

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        body = request.get_json(force=True, silent=True)
        if body is None:
            body = request.data.decode('utf-8')  # fallback for non-JSON
        save_webhook(request.headers, body)
        return jsonify({"message": "Webhook received"}), 200
    except Exception as e:
        return jsonify({"error": f"Invalid payload. {str(e)}"}), 400

@app.route('/webhooks', methods=['GET'])
def get_webhooks():
    return jsonify(load_webhooks()[::-1])

@app.route('/clear', methods=['POST'])
def clear_webhooks():
    if os.path.exists(WEBHOOK_FILE):
        os.remove(WEBHOOK_FILE)
    return jsonify({"message": "Webhooks cleared"}), 200

@app.route('/save', methods=['POST'])
def save_webhooks():
    if os.path.exists(WEBHOOK_FILE) and os.path.getsize(WEBHOOK_FILE) > 0:
        with open(WEBHOOK_FILE, "rb") as file:
            data = file.read()
        response = Response(data, content_type="application/json")
        response.headers["Content-Disposition"] = "attachment; filename=webhooks.json"
        return response
    return jsonify({"error": "No webhooks to save"}), 400

@app.route('/delete', methods=['POST'])
def delete_webhooks():
    if os.path.exists(WEBHOOK_FILE):
        os.remove(WEBHOOK_FILE)
    return jsonify({"message": "All webhook records deleted"}), 200

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8000)

from flask import Flask, request, jsonify, render_template, Response
import json
import os

app = Flask(__name__)

WEBHOOK_FILE = "webhooks.json"

# Save a webhook to file, including headers and raw body text
def save_webhook(headers, raw_body_text):
    webhook = {
        "headers": dict(headers),
        "body": raw_body_text  # raw JSON text as string
    }
    with open(WEBHOOK_FILE, "a", encoding="utf-8") as file:
        json.dump(webhook, file)
        file.write("\n")

# Load stored webhooks from file
def load_webhooks():
    if not os.path.exists(WEBHOOK_FILE):
        return []
    with open(WEBHOOK_FILE, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]

@app.route('/')
def index():
    webhooks = load_webhooks()
    return render_template('index.html', webhooks=webhooks[::-1])  # newest first

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get the exact raw JSON body text as string (no parsing)
        raw_body = request.get_data(as_text=True)
        save_webhook(request.headers, raw_body)
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

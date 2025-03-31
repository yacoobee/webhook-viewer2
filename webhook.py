from flask import Flask, request, jsonify, render_template, send_file, Response
import json
import os

app = Flask(__name__)

WEBHOOK_FILE = "webhooks.json"

# Function to save a webhook to a file
def save_webhook(data):
    with open(WEBHOOK_FILE, "a") as file:
        json.dump(data, file)
        file.write("\n")  # New line for each webhook

# Function to load webhooks from the file
def load_webhooks():
    if not os.path.exists(WEBHOOK_FILE):
        return []
    with open(WEBHOOK_FILE, "r") as file:
        return [json.loads(line) for line in file if line.strip()]

@app.route('/')
def index():
    webhooks = load_webhooks()
    return render_template('index.html', webhooks=webhooks[::-1])  # Show latest first

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.is_json:
        data = request.get_json()
        save_webhook(data)  # Save webhook to file
        return jsonify({"message": "Webhook received"}), 200
    return jsonify({"error": "Invalid JSON"}), 400

@app.route('/webhooks', methods=['GET'])
def get_webhooks():
    return jsonify(load_webhooks()[::-1])  # Return latest first

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

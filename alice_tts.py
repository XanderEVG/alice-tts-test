import json
import os
import uuid
from flask import Flask, request, jsonify
import websocket

app = Flask(__name__)

CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    # Значения по умолчанию на основе ваших данных
    return {"station_ip": "192.168.0.130", "station_port": 1961, "port": 5000}


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


config = load_config()


def send_local_tts(text, ip=None, port=None):
    """Отправка TTS через локальный протокол Glagol (без токенов и облака!)"""
    ip = ip or config.get("station_ip")
    port = port or config.get("station_port", 1961)

    if not ip:
        return False, "Не указан IP адрес станции в config.json"

    ws_url = f"ws://{ip}:{port}"
    payload = {
        "command": "sendText",
        "text": text,
        "id": str(uuid.uuid4())
    }

    try:
        # Устанавливаем WebSocket соединение с колонкой
        ws = websocket.create_connection(ws_url, timeout=5)
        ws.send(json.dumps(payload))
        result = ws.recv()
        ws.close()

        # Парсим ответ от колонки
        response_data = json.loads(result)
        if response_data.get("status") == "ok":
            return True, f"Текст успешно отправлен локально на {ip}:{port}"
        else:
            return False, f"Ошибка Glagol: {response_data}"

    except Exception as e:
        return False, f"Ошибка подключения к {ws_url}: {e}. Убедитесь, что сервер и колонка в одной сети и колонка включена."


@app.route('/api/tts', methods=['POST'])
def api_tts():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"success": False, "error": "Parameter 'text' is required"}), 400

    text = data['text']
    ip = data.get('ip')
    port = data.get('port')

    success, message = send_local_tts(text, ip, port)

    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    print(f"✅ Сервер запущен на порту {config.get('port', 5000)}")
    print(f"✅ Целевая станция: {config.get('station_ip')}:{config.get('station_port', 1961)}")
    print("💡 Используем ЛОКАЛЬНЫЙ протокол Glagol (не требует токенов, работает без интернета!)")

    app.run(host='0.0.0.0', port=config.get('port', 5000), debug=False)
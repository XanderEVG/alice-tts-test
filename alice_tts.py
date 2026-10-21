import json
import os
import uuid
import time
import requests
import ssl
from flask import Flask, request, jsonify
import websocket

app = Flask(__name__)

CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "yandex_token": "",
        "station_id": "L01SP3700RJG3V",
        "platform": "plum",
        "station_ip": "192.168.0.60",
        "station_port": 1961,
        "port": 5000,
        "tts_prefix": "Повтори эту фразу: "  # Можно изменить на "Скажи: " или "Произнеси: "
    }


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


config = load_config()


def get_device_token():
    """Получает device_token для локального протокола"""
    station_id = config.get("station_id")
    platform = config.get("platform", "yandexstation")

    url = f"https://quasar.yandex.net/glagol/token?device_id={station_id}&platform={platform}"
    headers = {"Authorization": f"OAuth {config['yandex_token']}"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        resp = response.json()
        if resp.get("status") == "ok":
            return resp["token"]
        else:
            print(f"❌ Ошибка получения device_token: {resp}")
            return None
    except Exception as e:
        print(f"❌ Исключение при получении device_token: {e}")
        return None


def send_local_tts(text, ip=None, port=None):
    """
    Отправка TTS через локальный протокол Glagol.
    Используем хак с префиксом "Повтори эту фразу:" — единственный надёжный
    способ получить чистый TTS на новых прошивках (платформа plum).
    """
    ip = ip or config.get("station_ip")
    port = port or config.get("station_port", 1961)
    station_id = config.get("station_id")

    if not ip or not station_id:
        return False, "Не указаны IP или station_id в config.json"

    device_token = get_device_token()
    if not device_token:
        return False, "Не удалось получить device_token."

    ws_url = f"wss://{ip}:{port}"

    # Формируем текст с префиксом для обхода NLU
    prefix = config.get("tts_prefix", "Повтори эту фразу: ")
    full_text = f"{prefix}{text}"

    payload_inner = {"command": "sendText", "text": full_text}

    try:
        print(f"📡 Отправка TTS на {ws_url}...")
        ws = websocket.create_connection(
            ws_url,
            timeout=10,
            sslopt={"cert_reqs": ssl.CERT_NONE}
        )

        payload_wrapper = {
            "conversationToken": device_token,
            "id": str(uuid.uuid4()),
            "payload": payload_inner,
            "sentTime": int(round(time.time() * 1000))
        }

        ws.send(json.dumps(payload_wrapper))

        # Ждём ответ от станции с увеличенным таймаутом
        ws.settimeout(15.0)
        try:
            result = ws.recv()
            response_data = json.loads(result)
            ws.close()

            if response_data.get("status") == "ok":
                return True, f"Pure TTS успешно отправлен (станция произносит текст)"
            else:
                return False, f"Станция вернула ошибку: {response_data}"

        except websocket.WebSocketTimeoutException:
            ws.close()
            # Таймаут — это нормально: станция может закрыть соединение сразу после приёма
            return True, "Команда отправлена (станция приняла данные, fire-and-forget)"

    except websocket.WebSocketConnectionClosedException:
        # Станция закрыла соединение после приёма команды — это успех
        return True, "Команда отправлена (соединение закрыто станцией после приёма)"
    except ConnectionRefusedError:
        return False, f"Соединение отклонено. Проверьте, что станция включена и IP корректен ({ip})."
    except Exception as e:
        return False, f"Ошибка: {e}"


@app.route('/api/tts', methods=['POST'])
def api_tts():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"success": False, "error": "Parameter 'text' is required"}), 400

    success, message = send_local_tts(data['text'], data.get('ip'), data.get('port'))

    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Позволяет на лету менять префикс TTS"""
    if request.method == 'POST':
        data = request.get_json()
        if 'tts_prefix' in data:
            config['tts_prefix'] = data['tts_prefix']
            save_config(config)
            return jsonify({"success": True, "tts_prefix": config['tts_prefix']}), 200
    return jsonify({"tts_prefix": config.get('tts_prefix', '')}), 200


if __name__ == '__main__':
    print(f"✅ Сервер запущен на порту {config.get('port', 5000)}")
    print(f"✅ Целевая станция: {config.get('station_ip')}:{config.get('station_port')}")
    print(f"✅ Платформа: {config.get('platform')}")
    print(f"✅ Префикс TTS: '{config.get('tts_prefix', '')}'")
    print("💡 Используем sendText с префиксом для надёжного локального TTS")
    app.run(host='0.0.0.0', port=config.get('port', 5000), debug=False)
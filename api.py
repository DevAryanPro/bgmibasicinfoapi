from flask import Flask, request, jsonify
import requests
import json
from urllib.parse import unquote

app = Flask(__name__)

def get_authorization_token():
    url = "https://www.rooter.gg/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/130.0.6723.70 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                  "image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.7"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching Rooter homepage:", e)
        return None

    user_auth = response.cookies.get("user_auth")
    if not user_auth:
        print("No user_auth cookie received")
        return None

    try:
        access_token_json = unquote(user_auth)
        access_token_data = json.loads(access_token_json)
        return access_token_data.get("accessToken")
    except Exception as e:
        print("Token parse error:", e)
        return None

@app.route("/", methods=["GET"])
def get_username():
    user_id = request.args.get("user")
    if not user_id:
        return jsonify({"success": False, "error": "Missing user ID"}), 400

    access_token = get_authorization_token()
    if not access_token:
        return jsonify({"success": False, "error": "Failed to get access token"}), 500

    url = f"https://bazaar.rooter.io/order/getUnipinUsername?gameCode=BGMI_IN&id={user_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Device-Type": "web",
        "App-Version": "1.0.0",
        "Device-Id": "beff6160-9daf-11ef-966f-a9ffd59b9537",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/130.0.6723.70 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return jsonify({"success": False, "error": f"Request failed: {e}"}), 500

    if data.get("transaction") == "SUCCESS":
        return jsonify({
            "success": True,
            "username": data["unipinRes"]["username"],
            "uid": user_id,
            "server": "bgmi",
            "region": "ind"
        })
    else:
        return jsonify({
            "success": False,
            "error": data.get("message", "Unknown error")
        })

if __name__ == "__main__":
    app.run(debug=True)

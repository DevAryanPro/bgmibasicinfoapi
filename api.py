from flask import Flask, request, jsonify
import requests
import json
from urllib.parse import unquote

app = Flask(__name__)

def get_authorization_token():
    url = "https://www.rooter.gg/"
    
    headers = {
        "Host": "www.rooter.gg",
        "Sec-Ch-Ua": "\"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Accept-Language": "en-GB,en;q=0.9",
        "Dnt": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=0, i"
    }
    cookies = {
        "_ga": "GA1.1.816653570.1731056363",
        "FCNEC": "%5B%5B%22AKsRol9pDNTWffO0PwyohEPyt6Yn7jORTJ4OOeHBevSpYBkHxz4Br1knJz49nXqzl1du6trFMrwN4KwnBz1uopDKk1hO011BSU7Mz_yG-Q7h5VNwdiucyz-Fyyerrj5DFyIwjA4454JpR3ayVIAiJCDFu3HNKYRamg%3D%3D%22%5D%5D",
        "WZRK_S_R7R-W57-774Z": "%7B%22p%22%3A3%2C%22s%22%3A1731057930%2C%22t%22%3A1731058051%7D",
        "_ga_WSQC1N0GHD": "GS1.1.1731057931.1.1.1731058076.26.0.0",
        "_ga_H8PYYR9D1R": "GS1.1.1731057931.1.1.1731058076.0.0.0"
    }


    response = requests.get(url, headers=headers, cookies=cookies)
    
    user_auth = response.cookies.get('user_auth')
    if not user_auth:
        return None

    try:
        access_token_json = unquote(user_auth)
        access_token_data = json.loads(access_token_json)
        return access_token_data.get("accessToken")
    except Exception as e:
        print("Token parse error:", e)
        return None

@app.route('/', methods=['GET'])
def get_username():
    user_id = request.args.get('user')
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if data.get('transaction') == 'SUCCESS':
       return jsonify({
        "success": True,
        "username": data['unipinRes']['username'],
        "uid": user_id,
        "server": "bgmi",
        "region": "ind"
    })
    else:
        return jsonify({"success": False, "error": data.get('message', 'Unknown error')})

if __name__ == '__main__':
    app.run(debug=True)
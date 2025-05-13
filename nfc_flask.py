# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from smartcard.System import readers
from smartcard.util import toHexString

app = Flask(__name__)

# データベース
users = {
    "01148E7ED8233B04": "田中雅也",
    "01148E7ED8234504": "江本舜",
    "01148E7ED8233204": "林優斗",
    "01148E7E8C222D00": "古山大成"
}

# UIDを照合してユーザー情報を取得
def get_user_info(uid):
    return users.get(uid, None)

@app.route("/reader_uid")
def reader_uid():
    try:
        # 利用可能なリーダーを取得
        r = readers()
        if not r:
            return jsonify({"status": "error", "message": "リーダーが見つかりません"}), 404

        # 最初のリーダーを選択
        reader = r[0]
        print(f"利用可能なリーダー: {reader}")

        # リーダーと接続
        connection = reader.createConnection()
        connection.connect()
        print("カードが検出されました。")

        # APDUコマンドを送信してUIDを取得
        command = [0xFF, 0xCA, 0x00, 0x00, 0x00]  # UIDを取得するためのコマンド
        response, sw1, sw2 = connection.transmit(command)

        # 受け取ったレスポンスを16進文字列に変換
        uid = toHexString(response).replace(" ", "")
        print(f"カードのUID: {uid}")

        # データベースを照合
        name = get_user_info(uid)
        if name:
            return jsonify({"status": "success", "uid": uid, "name": name})
        else:
            return jsonify({"status": "not_found", "uid": uid, "message": "UIDがデータベースに存在しません"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
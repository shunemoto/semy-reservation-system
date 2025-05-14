# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, request
from smartcard.System import readers
from smartcard.util import toHexString
import gspread
import os

app = Flask(__name__)

# データベース
users = {
    "01148E7ED8233B04": "田中雅也",
    "01148E7ED8234504": "江本舜",
    "01148E7ED8233204": "林優斗",
    "01148E7E8C222D00": "古山大成",
    "01148E7E85222105": "まーちゃん",
    "01148E7E85220905": "おしょう"
}

# UIDを照合してユーザー情報を取得
def get_user_info(uid):
    return users.get(uid, None)

@app.route("/")
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
            # UIDが見つかった場合、reserve.htmlを表示し、UIDと名前を渡す
            return render_template("reserve.html", uid=uid, name=name)
        else:
            return jsonify({
                "status": "not_found",
                "uid": uid,
                "message": "UIDがデータベースに存在しません"
            }), 404

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/reserve", methods=["POST"])
def reserve():
    try:
        # リクエストボディからnameを取得
        data = request.json
        print(data)
        username = data.get("name")

        # 現在のディレクトリパスを取得
        dir_path = os.path.dirname(__file__)

        # Google Sheets API認証
        gc = gspread.oauth(
            credentials_filename=os.path.join(dir_path, "client_secret.json"),
            authorized_user_filename=os.path.join(dir_path, "authorized_user.json"),
        )

        # スプレッドシートにアクセス
        wb = gc.open_by_key("1raabg2CoCNvQDuBINfO6c5Hr0XXCmi9q_ZBegafv41w")  # test02のファイルを開く(キーから)
        ws = wb.get_worksheet(0)  # 最初のシートを開く(idは0始まりの整数)

        # 書き込みたいデータ
        data = [username]

        # セル "C3" にデータを書き込む
        ws.update("C3", [[data[0]]])  # リスト内リストとして書き込む

        # 成功した場合
        return jsonify({
            "status": "success",
            "message": "予約が完了しました。"
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



if __name__ == "__main__":
    app.run(debug=True)
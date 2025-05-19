# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from smartcard.System import readers
from smartcard.util import toHexString
import gspread

#https://docs.google.com/spreadsheets/d/1raabg2CoCNvQDuBINfO6c5Hr0XXCmi9q_ZBegafv41w/edit?usp=sharing

app = Flask(__name__)

# UIDを照合してユーザー情報を取得
def get_user_info(uid):
    # データベース
    dir_path = os.path.dirname(__file__)
    users_list_path = os.path.join(dir_path, "users_list.json")

    # JSON読み込み + 日付確認
    with open(users_list_path, 'r', encoding='utf-8') as file:
        users = json.load(file)

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
            print(f"名前: {name}")
            # UIDが見つかった場合、reserve.htmlを表示し、UIDと名前を渡す
            return render_template("reserve.html", uid=uid, name=name)
        else:
            print("UIDがデータベースに存在しません")
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
        username = data.get("name")
        order = data.get("reservation_order")

        # 現在のディレクトリパスを取得
        dir_path = os.path.dirname(__file__)
        reserve_list_path = os.path.join(dir_path, "reservation_list.json")
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Google Sheets API認証
        gc = gspread.oauth(
            credentials_filename=os.path.join(dir_path, "client_secret.json"),
            authorized_user_filename=os.path.join(dir_path, "authorized_user.json"),
        )

        # JSON読み込み + 日付確認
        if os.path.exists(reserve_list_path):
            with open(reserve_list_path, 'r', encoding='utf-8') as file:
                full_data = json.load(file)
        else:
            full_data = {}

        # 前回更新日と照合
        last_date = full_data.get("last_updated_date", "")
        if last_date != today_str:
            # 日付が変わったら初期化
            reserve_dict = {}
        else:
            reserve_dict = full_data.get("reservations", {})
        
        # キーを整数にして整形し、同じ名前があれば削除
        reserve_dict = {int(k): v for k, v in reserve_dict.items()}
        reserve_dict = {k: v for k, v in reserve_dict.items() if v != username}
        sorted_keys = sorted(reserve_dict.keys())

        # 順番を詰め直す
        reserve_dict = {i + 1: reserve_dict[k] for i, k in enumerate(sorted_keys)}
        sorted_keys = sorted(reserve_dict.keys())

        if order is None or order == 0:
            # orderが指定されていない、または0なら末尾に追加
            new_order = max(sorted_keys) + 1 if sorted_keys else 1
            reserve_dict[new_order] = username
        elif order == -1:
            continue
        else:
            # 指定されたorder位置に追加し、それ以降をずらす
            order = int(order)
            new_reserve = {}
            inserted = False
            for k in sorted_keys:
                if not inserted and k >= order:
                    new_reserve[k] = username
                    inserted = True
                    new_reserve[k + 1] = reserve_dict[k]
                elif inserted:
                    new_reserve[k + 1] = reserve_dict[k]
                else:
                    new_reserve[k] = reserve_dict[k]
            if not inserted:
                new_reserve[order] = username
            reserve_dict = new_reserve
        
        # 保存（last_updated_dateを含む形式で保存）
        with open(reserve_list_path, 'w', encoding='utf-8') as file:
            json.dump({
                "last_updated_date": today_str,
                "reservations": {str(k): v for k, v in reserve_dict.items()}
            }, file, ensure_ascii=False, indent=2)

        # スプレッドシートにアクセス
        wb = gc.open_by_key("1raabg2CoCNvQDuBINfO6c5Hr0XXCmi9q_ZBegafv41w")  # test02のファイルを開く(キーから)
        ws = wb.get_worksheet(0)  # 最初のシートを開く(idは0始まりの整数)

        # セルにデータを書き込む
        for i in range(1, 11):
            name = reserve_dict.get(i, "")
            ws.update(f"C{i+2}", [[name]])

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
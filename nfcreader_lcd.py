# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, request
from smartcard.System import readers
from smartcard.util import toHexString
import gspread
import os
import json
from datetime import datetime
import sys
import jaconv
from kanjiconv import KanjiConv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
import Scripts.i2clcda as lcd

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

def scroll_messages(msg1, msg2):
    lcd.lcd_init()
    lcd.lcd_string_kana(msg1, lcd.LCD_LINE_1)
    lcd.lcd_string_kana(msg2, lcd.LCD_LINE_2)

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

        kanji_conv = KanjiConv(separator="")
        zenkaku = kanji_conv.to_katakana(name)
        hankaku = jaconv.z2h(zenkaku, kana=True, digit=False, ascii=False)
        lcd.lcd_init()
        scroll_messages("ｱﾅﾀﾉﾅﾏｴﾊ", f"{hankaku}ﾀﾞﾈ!")

        if name:
            print(f"名前: {name}")
            # UIDが見つかった場合、reserve.htmlを表示し、UIDと名前を渡す
            return render_template("reserve.html", uid=uid, name=name)
        else:
            print("UIDがデータベースに存在しません")
            return render_template("error.html")

    except Exception as e:
        return render_template("error.html")

@app.route("/finish")
def finish():
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
            return render_template("finish_semy.html", uid=uid, name=name)
        else:
            print("UIDがデータベースに存在しません")
            return render_template("error.html")

    except Exception as e:
        return render_template("error.html")

@app.route("/reserve", methods=["POST"])
def reserve():
    try:
        # リクエストボディからJSONを取得し、nameとreservation_orderを取得
        data = request.json
        if data is None:
            return jsonify({"status": "error", "message": "リクエストボディが空です"}), 400
        
        username = data.get("name")
        order = data.get("reservation_order")

        if not username:
            return jsonify({"status": "error", "message": "名前が指定されていません"}), 400
        
        # 現在のディレクトリパスを取得
        dir_path = os.path.dirname(os.path.abspath(__file__))
        reserve_list_path = os.path.join(dir_path, "reservation_list.json")
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Google Sheets API認証
        gc = gspread.oauth(
            credentials_filename=os.path.join(dir_path, "client_secret.json"),
            authorized_user_filename=os.path.join(dir_path, "authorized_user.json"),
        )

        # JSON読み込み
        if os.path.exists(reserve_list_path):
            with open(reserve_list_path, 'r', encoding='utf-8') as file:
                full_data = json.load(file)
        else:
            full_data = {}

        last_date = full_data.get("last_updated_date", "")
        if last_date != today_str:
            reserve_dict = {}
        else:
            reserve_dict = full_data.get("reservations", {})

        # キーを整数にして整形、同じ名前を削除
        try:
            reserve_dict = {int(k): v for k, v in reserve_dict.items()}
        except Exception:
            reserve_dict = {}
        reserve_dict = {k: v for k, v in reserve_dict.items() if v != username}
        sorted_keys = sorted(reserve_dict.keys())

        # 順番詰め
        reserve_dict = {i + 1: reserve_dict[k] for i, k in enumerate(sorted_keys)}
        sorted_keys = sorted(reserve_dict.keys())

        # orderの扱い
        if order is None or str(order) == "0":
            new_order = max(sorted_keys) + 1 if sorted_keys else 1
            reserve_dict[new_order] = username
        elif str(order) == "-1":
            # -1の場合は何もしない（もしくはエラーメッセージを返す選択肢も）
            pass
        else:
            try:
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
            except Exception:
                return jsonify({"status": "error", "message": "orderの値が不正です"}), 400
        
        # 保存
        with open(reserve_list_path, 'w', encoding='utf-8') as file:
            json.dump({
                "last_updated_date": today_str,
                "reservations": {str(k): v for k, v in reserve_dict.items()}
            }, file, ensure_ascii=False, indent=2)

        # スプレッドシートに書き込み
        wb = gc.open_by_key("1raabg2CoCNvQDuBINfO6c5Hr0XXCmi9q_ZBegafv41w")
        ws = wb.get_worksheet(0)

        for i in range(1, 11):
            name = reserve_dict.get(i, "")
            ws.update([[name]], f"C{i+2}")

        return jsonify({
            "status": "success",
            "message": "予約が完了しました。"
        })

    except Exception as e:
        # 例外メッセージを返す
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
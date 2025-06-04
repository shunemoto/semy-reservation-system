# 必要なモジュールをインポート
import RPi.GPIO as GPIO             # GPIO用のモジュール
import time                         # 時間制御用のモジュール
import sys                          # システム終了用
import webbrowser                   # URLを開くためのモジュール

# ポート番号の定義（ボタン2つ、LED2つ）
Sw_pin1 = 18                        # ボタン1のGPIOピン番号（BCMモード）
Sw_pin2 = 17                        # ボタン2のGPIOピン番号（BCMモード）
Led_pin1 = 23                      # LED1のGPIOピン番号（BCMモード）
Led_pin2 = 24                      # LED2のGPIOピン番号（BCMモード）

# 開きたいURL
TARGET_URL1 = "http://127.0.0.1:5000/"
TARGET_URL2 = "http://127.0.0.1:5000/finish"

# GPIOの設定
GPIO.setmode(GPIO.BCM)              # GPIOモードを"BCM"に設定

GPIO.setup(Sw_pin1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # ボタン1 入力（プルダウン）
GPIO.setup(Sw_pin2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # ボタン2 入力（プルダウン）

GPIO.setup(Led_pin1, GPIO.OUT)      # LED1 出力設定
GPIO.setup(Led_pin2, GPIO.OUT)      # LED2 出力設定

# 状態の保存（前回の入力）
prev_input1 = GPIO.LOW
prev_input2 = GPIO.LOW

try:
    while True:
        current_input1 = GPIO.input(Sw_pin1)
        current_input2 = GPIO.input(Sw_pin2)

        # ボタン1が押されたら
        if current_input1 == GPIO.HIGH:
            GPIO.output(Led_pin1, GPIO.HIGH)
            if prev_input1 == GPIO.LOW:
                print("ボタン1が押されました。URL1を開きます。")
                webbrowser.open(TARGET_URL1)
        else:
            GPIO.output(Led_pin1, GPIO.LOW)

        # ボタン2が押されたら
        if current_input2 == GPIO.HIGH:
            GPIO.output(Led_pin2, GPIO.HIGH)
            if prev_input2 == GPIO.LOW:
                print("ボタン2が押されました。URL2を開きます。")
                webbrowser.open(TARGET_URL2)
        else:
            GPIO.output(Led_pin2, GPIO.LOW)

        prev_input1 = current_input1
        prev_input2 = current_input2

        time.sleep(0.05)

except KeyboardInterrupt:
    GPIO.cleanup()
    sys.exit()

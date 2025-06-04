# semy-reservation-system
https://docs.google.com/spreadsheets/d/1raabg2CoCNvQDuBINfO6c5Hr0XXCmi9q_ZBegafv41w/edit?gid=0#gid=0

![yamachan](https://github.com/shunemoto/semy-reservation-system/tree/6abb0506d1df9f5ace858ec29e534e6eac8d0d75/static/images/yamachan.jpg)
## 概要

本システムは、NFCリーダーとRaspberry Piを活用した個別予約システムです。学生証をかざすことでGoogle Spreadsheetと連携し、予約状況の確認や新規予約をスムーズに行うことができます。

## 背景・目的

本研究室では、個別ゼミを実施するにあたって、研究室で待機をし、順番に個研に一人ずつ移動して行うというシステムとなっています。そのため、順番抜かしや先生側のあと何人待っているのかわからないといった問題が発生していました。本システムはこれらの問題を解決し、より公平で効率的な予約プロセスを実現することを目的として開発されました。

## 作成者
立命館大学理工学研究科環境都市専攻建築都市デザイン
* 田中 雅也
* 江本 舜

## システム構成・設計思想

本システムは、以下の流れで動作します。

1.  **NFC認証**: Raspberry Piに接続されたNFCリーダーに学生証をかざします。
2.  **予約操作**: Google Spreadsheet上に設置された予約ボタンを押すと、予約用のWebインターフェースに遷移します。
3.  **順番確定・予約**: Webインターフェース上で順番を選択したり、直接予約操作を行います。
4.  **リスト更新**: 操作完了後、Google Spreadsheetに戻り、予約者リストに自身の名前が追加・更新されていることを確認できます。

環境としてはRaspberry Piを使用しており、NFCリーダーの他に、物理ボタンによる操作やLCDモニターへの予約者名表示といった、簡易的な電子工作も組み込んでいます。これにより、直感的でわかりやすい操作性を目指しました。

## 主な機能

* **NFCによるユーザー認証**: 学生証のNFCタグを読み取り、利用者を識別します。
* **Webベースの予約インターフェース**: PCやスマートフォンからアクセス可能な画面で予約操作（順番選択、予約確定）を行います。
* **Google Spreadsheet連携**: 予約情報はリアルタイムでGoogle Spreadsheetに記録・更新され、一覧性が確保されます。
* **予約状況のLCD表示**: Raspberry Piに接続されたLCDモニターに現在の予約者名などを表示します。
* **物理ボタン操作**: Raspberry Piに接続された物理ボタンによる簡易的な操作（機能は `switch.py` に依存）が可能です。

## 使用技術

* **ハードウェア**:
    * Raspberry Pi4
    * NFCリーダー
    * LCDディスプレイ
    * プッシュボタン等の電子部品
* **ソフトウェア**:
    * **言語**: Python 
    * **主なライブラリ・フレームワーク**:
        * NFC制御: `smartcard`
        * GPIO制御: `RPi.GPIO` (Raspberry PiのGPIOピン操作用)
        * Google API連携: `gspread`, `oauth2client` (Google Sheets API操作用)
        * Webフレームワーク: `Flask`
    * **データベース/データストレージ**: Google Spreadsheet
    * **その他**: `json` (ユーザーリスト、予約リストの読み書き用)

## ファイル構成
```text
.
├── static/              # CSSファイルや画像ファイル
├── templates/           # HTMLテンプレートファイル
│   ├── error.html
│   └── reserve.html
├── nfc_reader.py        # NFC読み取り処理のメインプログラム
├── nfc_reader_lcd.py    # NFC読み取りとLCD表示処理のプログラム
├── switch.py            # 物理ボタンスイッチ関連のプログラム
├── user_list.json       # ユーザー情報管理用ファイル
└── reservation_list.json # 予約情報管理用ファイル
```

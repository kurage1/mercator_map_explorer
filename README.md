## 概要

matplotlibのインタラクティブプロットを用い、メルカトル図法の地図上で、**実際の大きさを維持したまま**日本を動かすことができるプログラムです。
平面の地図がいかに歪んでいるかを実感することができます。


https://github.com/user-attachments/assets/3ec768c8-c280-472e-a575-ffe37e39fcc6


地図データはhttps://www.naturalearthdata.com/downloads/50m-physical-vectors/50m-coastline/ より。
ただしデータは間引きしています。

## インストール

### 動作環境
 - python 3.11.6で動作確認済み。

### セットアップ
0. pythonをインストール
1. 仮想環境を作成（推奨）
   - macOSまたはLinux
     ```shell
     python -m venv myenv
     source myenv/bin/activate
     ```
   - Windows
     ```shell
     myenv\Scripts\activate
     ```
2. 依存関係をインストール
    ```shell
    pip install -r requirements.txt
    ```
3. 実行
    ```shell
    python mercator_map_explorer.py

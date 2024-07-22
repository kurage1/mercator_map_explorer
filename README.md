## 概要

matplotlibのインタラクティブプロットを用い、メルカトル図法の地図上で、**実際の大きさを維持したまま**日本を動かすことができるプログラムです。
平面の地図がいかに歪んでいるかを実感することができます。


https://github.com/user-attachments/assets/3ec768c8-c280-472e-a575-ffe37e39fcc6


地図データはhttps://www.naturalearthdata.com/downloads/50m-physical-vectors/50m-coastline/ より。
ただしデータは間引きしています。

## 動作環境
 - macOSにて、```python 3.11.6```及び```3.12.2```で動作確認済み。

## セットアップ
0. pythonをインストール
1. リポジトリをクローン・移動
    ```shell
    git clone https://github.com/kurage1/mercator_map_explorer.git
    cd mercator_map_explorer
    ```
3. 仮想環境を作成・有効化（推奨）
   - macOSまたはLinux
     ```shell
     python3 -m venv myenv
     source myenv/bin/activate
     ```
   - Windows
     ```shell
     python -m venv myenv
     myenv\Scripts\activate
     ```
4. 依存関係をインストール
    ```shell
    pip install -r requirements.txt
    ```
5. 実行
   - macOSまたはLinux
     ```shell
     python3 mercator_map_explorer.py
     ```
   - Windows
     ```shell
     python mercator_map_explorer.py
     ```
6. （終了後、仮想環境から抜ける）
    ```shell
    deactivate
    ```

# <PoC> IT Office Gate / poc-itofficegate-device

オフィス管理用デバイスのGUI。各機能の簡易版を実装し、動作検証をする。

---

## 🎯 検証目的（PoCの目的）

本リポジトリは、以下の技術的実現可能性および仮説を検証することを目的としています。

* **目的1:**
* **目的2:**
* **非目的（やらないこと）:**

---

## 🛠 動作環境・ハードウェア構成

### ハードウェア
* **本体:** Raspberry Pi 3 Model B (4GB)
* **OS:** Raspberry Pi OS (64-bit)
* **使用パーツ/センサー:** 

### 開発環境・主要ライブラリ
* **Python:** `3.10.x`
* **主要ライブラリ:**

---

## 🚀 セットアップ & 実行手順

### 1. 配線（回路）
[配線図の画像や、ピン番号の対応表を記載]

* Pin 1 (3.3V) -> VCC
* Pin 3 (GPIO2) -> Data
* Pin 6 (GND) -> GND

### 2. 環境構築
```bash
# リポジトリのクローン
git clone [https://github.com/](https://github.com/)[ユーザー名]/[リポジトリ名].git
cd [リポジトリ名]

# 仮想環境の作成とライブラリインストール
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

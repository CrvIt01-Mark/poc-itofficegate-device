# config_manager.py
import json
from pathlib import Path

# 設定ファイルの保存先（プロジェクトルート配下の config.json）
CONFIG_FILE = Path(__file__).resolve().parent / "config.json"

# デフォルト設定値
DEFAULT_CONFIG = {
    "theme": "Dark",   # "Dark" または "Light"
    "volume": 0.5     # 0.0 ～ 1.0
}

def load_config() -> dict:
    """設定ファイルを読み込む（存在しない場合はデフォルト値を返す）"""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # 必須キーが欠けている場合の補完処理
            for key, val in DEFAULT_CONFIG.items():
                config.setdefault(key, val)
            return config
    except Exception as e:
        print(f"[Config] 読み込みエラー: {e} -> デフォルト値を使用します")
        return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    """設定を JSON ファイルに保存する"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[Config] 保存エラー: {e}")
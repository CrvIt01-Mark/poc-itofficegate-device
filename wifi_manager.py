# wifi_manager.py
import platform
import subprocess
import time

class WifiManager:
    def __init__(self):
        # WSL 環境チェック
        self.is_wsl = "microsoft" in platform.release().lower()

    def scan_ssids(self) -> list:
        """周囲の Wi-Fi SSID 一覧を取得"""
        if self.is_wsl:
            print("[Wifi] WSL環境 ➔ ダミーの Wi-Fi 一覧を返します")
            return ["Home_WiFi_5G", "Shop_Free_Wi-Fi", "MobileHotspot_77", "Test_Network_2G"]

        try:
            # nmcli で Wi-Fi 一覧を取得
            res = subprocess.run(
                ["nmcli", "-f", "SSID", "dev", "wifi", "list"],
                capture_output=True, text=True, timeout=5
            )
            lines = res.stdout.splitlines()[1:]  # ヘッダー行を除外
            ssids = [line.strip() for line in lines if line.strip() and line.strip() != "--"]
            # 重複除去
            return list(dict.fromkeys(ssids))
        except Exception as e:
            print(f"[Wifi] スキャンエラー: {e}")
            return []

    def connect(self, ssid: str, password: str) -> bool:
        """指定した SSID にパスワードで接続"""
        if self.is_wsl:
            print(f"[Wifi] ダミー接続試行: SSID={ssid}, PASS={password}")
            time.sleep(2)  # 接続処理の模擬
            return password != ""  # パスワードが空でなければ成功扱い

        try:
            # nmcli で Wi-Fi に接続
            cmd = ["nmcli", "dev", "wifi", "connect", ssid, "password", password]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return res.returncode == 0
        except Exception as e:
            print(f"[Wifi] 接続エラー: {e}")
            return False
# pages/wifi_page.py
import threading
import customtkinter as ctk
from components import PageFrame, TouchScrollableFrame, BusyOverlay, WifiConnectOverlay
from wifi_manager import WifiManager

class WifiPage(PageFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller, "📶 Wi-Fi 接続設定")

        # ヘッダーに「戻る」ボタンと「再スキャン」ボタンを配置
        back_btn = ctk.CTkButton(
            self.header, text="◀ 戻る", width=80, 
            command=lambda: controller.show_frame("MainMenuPage")
        )
        back_btn.pack(side="left", padx=10, pady=10)

        scan_btn = ctk.CTkButton(
            self.header, text="🔄 再スキャン", width=100, 
            command=self.start_scan
        )
        scan_btn.pack(side="right", padx=10, pady=10)

        self.wifi_mgr = WifiManager()

        # SSIDs 表示用のスクロールエリア
        self.scroll_frame = TouchScrollableFrame(
            self, width=760, height=360, hide_scrollbar=True
        )
        self.scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

    def on_show(self):
        """画面表示時に自動スキャンを実行"""
        super().on_show()
        self.start_scan()

    def start_scan(self):
        """スキャン処理（別スレッド実行）"""
        self.overlay = BusyOverlay(self.controller, message="Wi-Fi ネットワークを\n検索中...")
        self.overlay.show()

        thread = threading.Thread(target=self._scan_worker, daemon=True)
        thread.start()
        self.check_scan_thread(thread)

    def _scan_worker(self):
        self.found_ssids = self.wifi_mgr.scan_ssids()

    def check_scan_thread(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.check_scan_thread(thread))
        else:
            self.overlay.hide()
            self._update_wifi_list()

    def _update_wifi_list(self):
        """スキャン結果をボタン化してスクロールビューに配置"""
        target = getattr(self.scroll_frame, "scrollable_content", self.scroll_frame)

        # 既存のリスト表示をクリア
        for child in target.winfo_children():
            child.destroy()

        if not self.found_ssids:
            no_item = ctk.CTkLabel(target, text="Wi-Fi ネットワークが見つかりませんでした", font=ctk.CTkFont(size=16))
            no_item.pack(pady=30)
            return

        for ssid in self.found_ssids:
            btn = ctk.CTkButton(
                target,
                text=f"📶  {ssid}",
                height=50,
                anchor="w",
                font=ctk.CTkFont(size=16),
                command=lambda s=ssid: self.open_password_dialog(s)
            )
            btn.pack(padx=10, pady=5, fill="x")

        self.scroll_frame.bind_touch_to_children(target)

    def open_password_dialog(self, ssid):
        kb_overlay = WifiConnectOverlay(
            master=self.controller, # App全体に展開
            ssid=ssid,
            on_connect_cb=self.start_connect,
            on_cancel_cb=None
        )
        kb_overlay.show()

    def start_connect(self, ssid, password):
        """Wi-Fi 接続処理（別スレッド実行）"""
        self.overlay = BusyOverlay(self.controller, message=f"「{ssid}」へ\n接続中...")
        self.overlay.show()

        thread = threading.Thread(
            target=self._connect_worker, args=(ssid, password), daemon=True
        )
        thread.start()
        self.check_connect_thread(thread, ssid)

    def _connect_worker(self, ssid, password):
        self.connect_result = self.wifi_mgr.connect(ssid, password)

    def check_connect_thread(self, thread, ssid):
        if thread.is_alive():
            self.after(100, lambda: self.check_connect_thread(thread, ssid))
        else:
            self.overlay.hide()
            if self.connect_result:
                print(f"[Wifi] {ssid} への接続に成功しました")
            else:
                print(f"[Wifi] {ssid} への接続に失敗しました")
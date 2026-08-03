# pages/dashboard.py（ダッシュボード）

import customtkinter as ctk
import threading
import time
from components import PageFrame, BusyOverlay

class DashboardPage(PageFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller, "📊 ダッシュボード")

        back_btn = ctk.CTkButton(
            self.header, text="◀ 戻る", width=80, 
            command=lambda: controller.show_frame("MainMenuPage")
        )
        back_btn.pack(side="left", padx=10, pady=10)

        # カウント状態の変数
        self.count = 0
        self.is_running = False  # 処理動作中フラグ
        self.after_id = None     # after() のキャンセル用ID

        # カウンター表示用ラベル
        self.status_label = ctk.CTkLabel(
            self, 
            text="処理停止中", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.status_label.pack(expand=True)

        # 重い処理を開始するボタン
        self.run_btn = ctk.CTkButton(
            self, 
            text="⚡ 重い処理を実行（5秒）", 
            height=50,
            font=ctk.CTkFont(size=16),
            command=self.start_heavy_task
        )
        self.run_btn.pack(expand=True)

    # 🌟 画面が前面に出た際に自動的に呼ばれる
    def on_show(self):
        super().on_show() # 親クラス(PageFrame)の on_show() を実行
        print("[Dashboard] 画面が表示されました ➔ 定期処理を開始します")
        self.is_running = True
        self.run_process()

    # 🌟 画面が隠れた際に自動的に呼ばれる
    def on_hide(self):
        super().on_hide() # 親クラス(PageFrame)の on_hide() を実行
        print("[Dashboard] 画面が隠れました ➔ 定期処理を停止します")
        self.is_running = False
        # 待機中の after イベントがあれば安全にキャンセル
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def run_process(self):
        """表示中のみ1秒ごとに実行される処理"""
        if not self.is_running:
            return

        self.count += 1
        self.status_label.configure(text=f"リアルタイム計測中: {self.count} 秒")
        
        # 1秒後に再度実行（戻り値を ID として保持）
        self.after_id = self.after(1000, self.run_process)

    def start_heavy_task(self):
        """重い処理をスレッドで開始し、入力遮断オーバーレイを表示"""
        # アプリ全体（controller）の上にオーバーレイを被せる
        self.overlay = BusyOverlay(self.controller, message="データ処理中...\nしばらくお待ちください")
        self.overlay.show()

        # バックグラウンドスレッドで処理を開始
        thread = threading.Thread(target=self._heavy_task_worker, daemon=True)
        thread.start()

        # スレッドの終了をチェックするループを開始
        self.check_thread(thread)

    def _heavy_task_worker(self):
        """【サブスレッド】時間のかかる処理（通信、データ計算、ファイル入出力など）"""
        print("[Thread] 重い処理を開始しました")
        time.sleep(5)  # 5秒かかる処理のダミー
        print("[Thread] 重い処理が完了しました")

    def check_thread(self, thread):
        """【メインスレッド】スレッドの完了を定期監視"""
        if thread.is_alive():
            # スレッドが実行中なら 100ms 後に再チェック
            self.after(100, lambda: self.check_thread(thread))
        else:
            # 処理完了 ➔ オーバーレイを消去して入力を再開
            self.overlay.hide()
            print("[GUI] オーバーレイを解除しました")
import sys
from pathlib import Path

# 🌟 実行ファイルのディレクトリを検索パス(sys.path)の最優先に追加してインポートエラーを防ぐ
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import customtkinter as ctk

# pages フォルダから各画面クラスをインポート
from pages.main_menu import MainMenuPage
from pages.dashboard import DashboardPage
from pages.settings import SettingsPage
from pages.drawing import DrawingPage
from pages.camera_page import CameraPage
from pages.wifi_page import WifiPage

from config_manager import load_config

# --- アプリの初期化前に設定を読み込んでテーマを反映 ---
initial_config = load_config()
ctk.set_appearance_mode(initial_config.get("theme", "Dark"))
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Raspberry Pi GUI App")
        self.geometry("800x480+0+0")
        self.resizable(False, False)

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        # 🌟 現在アクティブな画面の名前を保持する変数
        self.current_page_name = None

        page_classes = (MainMenuPage, DashboardPage, SettingsPage, DrawingPage, CameraPage, WifiPage)

        for PageClass in page_classes:
            page_name = PageClass.__name__
            frame = PageClass(master=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # 初期画面表示
        self.show_frame("MainMenuPage")

    def show_frame(self, page_name):
        """画面切り替えとライフサイクルイベント（on_hide / on_show）の実行"""
        # 1. 直前に表示されていた画面があれば on_hide() を呼び出す
        if self.current_page_name and self.current_page_name in self.frames:
            previous_frame = self.frames[self.current_page_name]
            previous_frame.on_hide()

        # 2. 新しい画面を前面に移動
        next_frame = self.frames[page_name]
        next_frame.tkraise()
        
        # 3. 現在表示中の画面名を更新
        self.current_page_name = page_name

        # 4. 新しい画面の on_show() を呼び出す
        next_frame.on_show()

if __name__ == "__main__":
    app = App()
    app.mainloop()
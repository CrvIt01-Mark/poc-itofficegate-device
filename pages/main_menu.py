# pages/main_menu.py（メインメニュー）

import customtkinter as ctk
from components import PageFrame, TouchScrollableFrame

class MainMenuPage(PageFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller, "メインメニュー (800x480)")

        # hide_scrollbar=True を指定してスクロールバーを非表示化
        self.scroll_frame = TouchScrollableFrame(
            self, 
            width=760, # スクロールバーが消えた分、少し幅を広げられます(740->760)
            height=380,
            hide_scrollbar=True
        )
        self.scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # ボタンを配置するターゲット（代替案の自作スクロールフレームにも対応）
        target_frame = getattr(self.scroll_frame, "scrollable_content", self.scroll_frame)

        menus = [
            ("📊 ダッシュボード画面へ", "DashboardPage"),
            ("📷 カメラモニタ画面へ", "CameraPage"),
            ("🖼️ 画像・描画画面へ", "DrawingPage"),
            ("⚙️ システム設定画面へ", "SettingsPage"),
            ("📶 Wi-Fi 接続設定へ", "WifiPage"),
        ]

        for text, page_name in menus:
            btn = ctk.CTkButton(
                target_frame,
                text=text,
                height=60,
                font=ctk.CTkFont(size=18),
                command=lambda p=page_name: controller.show_frame(p)
            )
            btn.pack(padx=10, pady=10, fill="x")

        # スクロールテスト用のダミーボタンを20個追加
        for i in range(1, 21):
            dummy_btn = ctk.CTkButton(
                target_frame,
                text=(text_value := f"🧪 スクロールテスト用ボタン {i}"),
                height=50,
                fg_color="#3a3a3a",  # メイン機能と区別しやすいようにダークグレーに設定
                hover_color="#555555",
                font=ctk.CTkFont(size=16),
                command=lambda num=i: self.on_dummy_click(num)
            )
            dummy_btn.pack(padx=10, pady=6, fill="x")
        self.scroll_frame.bind_touch_to_children(self.scroll_frame)

    def on_dummy_click(self, button_num):
        """ダミーボタンが押された時のテスト処理"""
        print(f"[Test] ダミーボタン {button_num} がタップされました！")
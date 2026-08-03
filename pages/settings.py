# pages/settings.py（設定）
# pages/settings.py
import customtkinter as ctk
from components import PageFrame
from config_manager import load_config, save_config

class SettingsPage(PageFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller, "⚙️ システム設定")

        # 戻るボタン
        back_btn = ctk.CTkButton(
            self.header, text="◀ 戻る", width=80, 
            command=lambda: controller.show_frame("MainMenuPage")
        )
        back_btn.pack(side="left", padx=10, pady=10)

        # 保存されている現在の設定をロード
        self.config = load_config()

        # --- 1. ダークモード切り替えスイッチ ---
        is_dark = self.config.get("theme", "Dark") == "Dark"
        self.switch_var = ctk.StringVar(value="on" if is_dark else "off")

        self.theme_switch = ctk.CTkSwitch(
            self, 
            text="ダークモード有効化", 
            font=ctk.CTkFont(size=16),
            command=self.toggle_theme,
            variable=self.switch_var,
            onvalue="on", 
            offvalue="off"
        )
        self.theme_switch.pack(pady=30)

        # --- 2. 音量調整スライダー ---
        slider_label = ctk.CTkLabel(self, text="音量調整", font=ctk.CTkFont(size=16))
        slider_label.pack(pady=(10, 5))

        current_vol = self.config.get("volume", 0.5)
        self.slider = ctk.CTkSlider(
            self, 
            width=400, 
            from_=0, 
            to=1,
            command=self.on_volume_change
        )
        self.slider.set(current_vol)
        self.slider.pack(pady=5)

    def toggle_theme(self):
        """テーマ切り替え＆設定保存"""
        new_mode = "Dark" if self.switch_var.get() == "on" else "Light"
        ctk.set_appearance_mode(new_mode)

        # 設定の更新と保存
        self.config["theme"] = new_mode
        save_config(self.config)

    def on_volume_change(self, value):
        """音量変更＆設定保存"""
        self.config["volume"] = round(value, 2)
        save_config(self.config)
# components.py（共通部品）
# タッチスクロールや画面のベース（ヘッダー付きフレーム）など、全画面で共通利用するクラスを定義します。

import socket
import customtkinter as ctk
from datetime import datetime  # 🌟 時刻取得用にインポート

class TouchScrollableFrame(ctk.CTkScrollableFrame):
    """タッチドラッグ操作に対応したスクロールフレーム"""
    def __init__(self, master, hide_scrollbar=False, **kwargs):
        super().__init__(master, **kwargs)
        
        # 🌟 hide_scrollbar=True の場合、右側のスクロールバーを非表示にする
        if hide_scrollbar:
            if hasattr(self, "_scrollbar"):
                self._scrollbar.configure(width=0)
                self._scrollbar.pack_forget()
                self._scrollbar.grid_forget()

        self._start_y = 0
        self.bind("<Button-1>", self._on_touch_start)
        self.bind("<B1-Motion>", self._on_touch_move)

    def _on_touch_start(self, event):
        self._start_y = event.y_root

    def _on_touch_move(self, event):
        delta_y = self._start_y - event.y_root
        self._start_y = event.y_root
        self._parent_canvas.yview_scroll(int(delta_y / 2), "units")

    def bind_touch_to_children(self, widget):
        widget.bind("<Button-1>", self._on_touch_start, add="+")
        widget.bind("<B1-Motion>", self._on_touch_move, add="+")
        for child in widget.winfo_children():
            self.bind_touch_to_children(child)


class PageFrame(ctk.CTkFrame):
    """すべての画面の基本形となるクラス"""
    def __init__(self, master, controller, title_text):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.controller = controller

        # ヘッダーエリア
        self.header = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.header.pack(fill="x", side="top")

        self.title_label = ctk.CTkLabel(
            self.header, 
            text=title_text, 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=10)

        # 🌟 右側: 時計表示用ラベル
        self.time_label = ctk.CTkLabel(
            self.header,
            text="",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.time_label.pack(side="right", padx=15, pady=10)

        # 🌟 右側: ネットワーク状態インジケーター用ラベル（時計の左隣）
        self.net_label = ctk.CTkLabel(
            self.header,
            text="NET --",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.net_label.pack(side="right", padx=(0, 10), pady=10)

        self.update_clock()

    def update_clock(self):
        """ヘッダー時計の更新"""
        # 曜日変換用のリスト（月曜=0, 火曜=1, ..., 日曜=6）
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]   

        now = datetime.now()
        day_of_week = weekdays[now.weekday()]  # 現在の曜日文字列を取得

        # 日付・曜日・時刻のフォーマットを作成（例: "2026/07/30(木) 14:05:23"）
        current_time_str = f"{now.strftime('%Y/%m/%d')}({day_of_week}) {now.strftime('%H:%M:%S')}"

        self.time_label.configure(text=current_time_str)
        self.after(1000, self.update_clock)

    def check_network_connection(self) -> bool:
        """
        ローカルIP等へ簡易接続テスト（8.8.8.8:53 または 127.0.0.1）
        ※高速に応答を返すソケット接続チェック
        """
        try:
            # 外部ソケットへの接続試行（タイムアウト1秒）
            socket.setdefaulttimeout(1.0)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("8.8.8.8", 53))
            return True
        except Exception:
            return False

    def update_network_status(self):
        """定期的にネットワーク状態をインジケーターに反映"""
        if not self._is_monitoring_net:
            return

        is_connected = self.check_network_connection()

        if is_connected:
            # 接続中: 緑色の丸マークとテキスト
            self.net_label.configure(
                text="● NET", 
                text_color="#2ECC71"  # エメラルドグリーン
            )
        else:
            # 切断中: 赤色の丸マークとテキスト
            self.net_label.configure(
                text="● NET", 
                text_color="#E74C3C"  # フラットレッド
            )

        # 3秒ごとに再チェック（負荷を下げるため1秒ではなく3秒周期がおすすめ）
        self.after(3000, self.update_network_status)


    # 画面が表示された時に呼ばれる（必要に応じて各子画面でオーバーライドする）
    def on_show(self):
        """画面表示時にネットワーク監視を開始"""
        self._is_monitoring_net = True
        self.update_network_status()

    # 画面が隠れた時に呼ばれる（必要に応じて各子画面でオーバーライドする）
    def on_hide(self):
        """画面非表示時にネットワーク監視を停止"""
        self._is_monitoring_net = False

# components.py に追加
import threading
import time

class BusyOverlay(ctk.CTkFrame):
    """重い処理中に画面全体を覆い、ユーザー入力をブロックするオーバーレイ"""
    def __init__(self, master, message="処理中..."):
        # 親画面（App全体）の上に重ねる
        super().__init__(
            master, 
            corner_radius=0, 
            fg_color=("gray80", "gray10")
        )
        
        # クリックイベントをキャプチャ（吸い取る）して裏側に届かないようにする
        self.bind("<Button-1>", lambda e: "break")
        self.bind("<B1-Motion>", lambda e: "break")

        # 中央のメッセージカード
        card = ctk.CTkFrame(self, corner_radius=15, width=300, height=150)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # テキスト表示
        self.label = ctk.CTkLabel(card, text=message, font=ctk.CTkFont(size=18, weight="bold"))
        self.label.pack(pady=(30, 10))

        # インジケータ（プログレスバーのアニメーション）
        self.progressbar = ctk.CTkProgressBar(card, mode="indeterminate", width=220)
        self.progressbar.pack(pady=10)
        self.progressbar.start()

    def show(self):
        """画面全体に表示"""
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.tkraise()

    def hide(self):
        """非表示にして破棄"""
        self.progressbar.stop()
        self.destroy()

class OnScreenKeyboard(ctk.CTkFrame):
    """汎用的に再利用可能なオンスクリーンキーボードコンポーネント（敷き詰め巨大ボタン版）"""
    def __init__(self, master, target_entry=None, on_enter_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.target_entry = target_entry          # 文字を入力する対象の CTkEntry
        self.on_enter_callback = on_enter_callback # Enter（確定）押下時のコールバック関数

        # キーボードのモード状態 (0: 小文字, 1: 大文字, 2: 記号・数字)
        self.mode = 0  

        # レイアウト定義
        self.keys_lowercase = [
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["Shift", "z", "x", "c", "v", "b", "n", "m", "⌫"],
            ["123", "Space", "Clear", "Enter"]
        ]
        self.keys_uppercase = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["shift", "Z", "X", "C", "V", "B", "N", "M", "⌫"],
            ["123", "Space", "Clear", "Enter"]
        ]
        self.keys_symbols = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")"],
            ["abc", "-", "_", "=", "+", "[", "]", "{", "}", "⌫"],
            ["abc", "Space", "Clear", "Enter"]
        ]

        self.render_keyboard()

    def set_target_entry(self, entry):
        self.target_entry = entry

    def render_keyboard(self):
        """現在のモードに応じたキーボード描画（ボタン最大化版）"""
        for child in self.winfo_children():
            child.destroy()

        if self.mode == 0:
            layout = self.keys_lowercase
        elif self.mode == 1:
            layout = self.keys_uppercase
        else:
            layout = self.keys_symbols

        for row in layout:
            # 行同士の上下隙間をほぼ排除 (pady=1)
            row_frame = ctk.CTkFrame(self, fg_color="transparent")
            row_frame.pack(fill="both", expand=True, pady=1)

            for key in row:
                width = 40
                fg_color = None
                
                # 特殊キーの比率調整
                if key in ["Shift", "shift", "123", "abc"]:
                    width = 70
                    fg_color = "#34495E"
                elif key == "Space":
                    width = 200
                elif key in ["⌫", "Clear"]:
                    width = 65
                    fg_color = "#C0392B" if key == "Clear" else "#D35400"
                elif key == "Enter":
                    width = 80
                    fg_color = "#2ECC71"

                btn = ctk.CTkButton(
                    row_frame, 
                    text=key, 
                    width=width, 
                    height=58,                  # 🌟 高さを大きく拡大（タッチしやすい）
                    corner_radius=3,             # 🌟 角丸を小さくしてタイトな見た目に
                    font=ctk.CTkFont(size=18, weight="bold"), # 🌟 文字フォントも少し大きく
                    fg_color=fg_color,
                    command=lambda k=key: self._on_key_press(k)
                )
                # ボタン同士の左右隙間を最小限に (padx=1)
                btn.pack(side="left", fill="both", expand=True, padx=1)

    def _on_key_press(self, key):
        if key in ["Shift", "shift"]:
            self.mode = 1 if self.mode == 0 else 0
            self.render_keyboard()
        elif key in ["123", "abc"]:
            self.mode = 2 if key == "123" else 0
            self.render_keyboard()
        elif key == "Enter":
            if self.on_enter_callback:
                self.on_enter_callback()
        else:
            if not self.target_entry:
                return

            if key == "⌫":
                curr = self.target_entry.get()
                self.target_entry.delete(0, "end")
                self.target_entry.insert(0, curr[:-1])
            elif key == "Clear":
                self.target_entry.delete(0, "end")
            elif key == "Space":
                self.target_entry.insert("end", " ")
            else:
                self.target_entry.insert("end", key)

class WifiConnectOverlay(ctk.CTkFrame):
    """Wi-Fi パスワード入力オーバーレイ（キーボードコンポーネントを使用）"""
    def __init__(self, master, ssid, on_connect_cb, on_cancel_cb):
        super().__init__(master, corner_radius=0, fg_color=("#E0E0E0", "#181818"))
        
        self.ssid = ssid
        self.on_connect_cb = on_connect_cb
        self.on_cancel_cb = on_cancel_cb
        self.show_password = False

        # タッチイベントの背面通過をブロック
        self.bind("<Button-1>", lambda e: "break")
        self.bind("<B1-Motion>", lambda e: "break")

        # --- 1. 上部コントロールエリア ---
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(10, 5))

        title_label = ctk.CTkLabel(
            top_frame, 
            text=f"📶 「{ssid}」のパスワード入力", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(side="left")

        cancel_btn = ctk.CTkButton(
            top_frame, text="キャンセル", width=90, height=35,
            fg_color="#7F8C8D", hover_color="#95A5A6", command=self._on_cancel
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        connect_btn = ctk.CTkButton(
            top_frame, text="接続", width=90, height=35,
            fg_color="#2ECC71", hover_color="#27AE60", command=self._on_connect
        )
        connect_btn.pack(side="right")

        # --- 2. パスワード入力フィールド行 ---
        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(fill="x", padx=20, pady=5)

        self.pass_entry = ctk.CTkEntry(
            entry_frame, 
            placeholder_text="パスワードを入力してください", 
            show="*", 
            font=ctk.CTkFont(size=18),
            height=40
        )
        self.pass_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.toggle_btn = ctk.CTkButton(
            entry_frame, text="👁 表示", width=70, height=40,
            fg_color="#555555", command=self._toggle_password_visibility
        )
        self.toggle_btn.pack(side="right")

        # --- 3. 🌟 単体キーボードコンポーネントの組み込み ---
        self.keyboard = OnScreenKeyboard(
            self, 
            target_entry=self.pass_entry,      # 入力先を指定
            on_enter_callback=self._on_connect # Enterキーでも接続を実行
        )
        self.keyboard.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    def show(self):
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.tkraise()

    def _toggle_password_visibility(self):
        self.show_password = not self.show_password
        show_char = "" if self.show_password else "*"
        self.pass_entry.configure(show=show_char)
        self.toggle_btn.configure(text="非表示" if self.show_password else "👁 表示")

    def _on_cancel(self):
        self.destroy()
        if self.on_cancel_cb:
            self.on_cancel_cb()

    def _on_connect(self):
        password = self.pass_entry.get()
        self.destroy()
        if self.on_connect_cb:
            self.on_connect_cb(self.ssid, password)
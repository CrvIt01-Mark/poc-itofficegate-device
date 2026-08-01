# pages/camera_page.py
import customtkinter as ctk
from PIL import ImageTk
from components import PageFrame
from camera_manager import CameraManager

class CameraPage(PageFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller, "📷 カメラ映像モニタ")

        # 戻るボタン
        back_btn = ctk.CTkButton(
            self.header, text="◀ 戻る", width=80, 
            command=lambda: controller.show_frame("MainMenuPage")
        )
        back_btn.pack(side="left", padx=10, pady=10)

        # カメラマネージャーのインスタンス化
        self.camera_mgr = CameraManager()

        # 映像表示用エリア (800x480 画面に合わせて 640x360 程度に設定)
        self.video_width = 640
        self.video_height = 360

        self.video_label = ctk.CTkLabel(
            self, 
            text="カメラを準備中...", 
            width=self.video_width, 
            height=self.video_height,
            fg_color="#101010",
            corner_radius=10
        )
        self.video_label.pack(expand=True, pady=10)

        # 制御フラグとタイマーID
        self.is_streaming = False
        self.after_id = None

    def update_feed(self):
        """フレームを取得して GUI の Label を更新（約30fps）"""
        if not self.is_streaming:
            return

        # フレーム取得 (Pillow Image)
        pil_image = self.camera_mgr.get_frame(self.video_width, self.video_height)
        
        # CTkImage 化してラベルを更新
        ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(self.video_width, self.video_height))
        self.video_label.configure(image=ctk_img, text="")
        
        # 参照保持（ガベージコレクション防止）
        self.video_label.image = ctk_img

        # 約30fps (33ミリ秒周期) で再帰実行
        self.after_id = self.after(33, self.update_feed)

    def on_show(self):
        """画面表示時: ストリーム開始"""
        super().on_show()
        print("[CameraPage] 表示 ➔ カメラストリームを開始します")
        self.is_streaming = True
        self.update_feed()

    def on_hide(self):
        """画面非表示時: ストリーム停止"""
        super().on_hide()
        print("[CameraPage] 非表示 ➔ カメラストリームを停止します")
        self.is_streaming = False
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
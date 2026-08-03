# pages/drawing.py（描画）

import customtkinter as ctk
# ルートの components.py からインポート
from components import PageFrame, TouchScrollableFrame

class DrawingPage(PageFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller, "🖼️ 描画エリア")

        back_btn = ctk.CTkButton(
            self.header, text="◀ 戻る", width=80, 
            command=lambda: controller.show_frame("MainMenuPage")
        )
        back_btn.pack(side="left", padx=10, pady=10)

        canvas = ctk.CTkCanvas(self, width=740, height=360, highlightthickness=0)
        canvas.pack(pady=10)
        canvas.create_rectangle(50, 50, 250, 200, outline="cyan", width=3)
        canvas.create_oval(300, 50, 450, 200, fill="#FF5733", outline="")
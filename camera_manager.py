# camera_manager.py
import platform
import time
import cv2
import numpy as np
from PIL import Image

class CameraManager:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.is_dummy = False
        
        # WSL 環境または Linux/Windows 等でカメラが開けない場合はダミーモードへ
        self._init_camera()

    def _init_camera(self):
        """カメラの初期化（失敗した場合はダミーモードに移行）"""
        # WSL 環境チェック (proc/version から microsoft 検出)
        is_wsl = "microsoft" in platform.release().lower()

        if is_wsl:
            print("[Camera] WSL環境を検出しました ➔ ダミー映像モードで動作します")
            self.is_dummy = True
            return

        # 本番環境（ラズパイ等）でカメラオープンを試行
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("[Camera] カメラのオープンに失敗しました ➔ ダミー映像モードに切り替えます")
            self.is_dummy = True
        else:
            print("[Camera] カメラを正常にオープンしました")

    def get_frame(self, width=640, height=480):
        """1フレーム取得し、PillowのImageオブジェクト(RGB)として返す"""
        if self.is_dummy:
            return self._generate_dummy_frame(width, height)

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return self._generate_dummy_frame(width, height)

        # OpenCV(BGR) から Pillow(RGB) へ変換し、サイズ調整
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height))
        return Image.fromarray(frame_resized)

    def _generate_dummy_frame(self, width, height):
        """WSL開発用: 動くカラーバーと時計を描画したダミー画像を生成"""
        # 背景（ダークグレー）
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[:] = (30, 30, 35)

        # 動く円アニメーション
        t = time.time()
        cx = int((width / 2) + np.sin(t * 2) * (width / 4))
        cy = int(height / 2)
        cv2.circle(img, (cx, cy), 40, (0, 200, 255), -1)

        # テキスト追加
        cv2.putText(
            img, "DUMMY CAMERA STREAM (WSL)", (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (250, 250, 250), 2
        )
        time_str = time.strftime("%H:%M:%S")
        cv2.putText(
            img, f"Time: {time_str}", (20, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1
        )

        return Image.fromarray(img)

    def release(self):
        """カメラリソースの解放"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            print("[Camera] カメラリソースを解放しました")
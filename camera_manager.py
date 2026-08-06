import platform
import cv2
import numpy as np

# ラズパイ環境での Picamera2 読み込み試行
try:
    from picamera2 import Picamera2
    HAS_PICAMERA2 = True
except ImportError:
    HAS_PICAMERA2 = False


class CameraManager:
    """Picamera2 対応のカメラ管理クラス"""
    def __init__(self, width=640, height=480, flip_vertical=False):
        self.width = width
        self.height = height
        self.flip_vertical = flip_vertical  # カメラが上下逆さに設置されている場合用
        self.is_dummy = False
        
        # WSL または Picamera2 がない PC 環境などの判定
        system_name = platform.system()
        release_name = platform.release()
        
        if "microsoft" in release_name.lower() or not HAS_PICAMERA2:
            print("INFO: PC/WSL環境またはPicamera2未検出のため、ダミーカメラモードで起動します。")
            self.is_dummy = True
        else:
            try:
                # Picamera2 の初期化
                self.picam2 = Picamera2()
                
                # 解像度とフォーマットの設定（main={"size": (W, H)}）
                config = self.picam2.create_preview_configuration(
                    main={"size": (self.width, self.height), "format": "RGB888"}
                )
                self.picam2.configure(config)
                self.picam2.start()
                print("SUCCESS: Picamera2 を正常に起動しました。")
            except Exception as e:
                print(f"WARNING: Picamera2 の初期化に失敗したため、ダミーモードへ切り替えます: {e}")
                self.is_dummy = True

    def get_frame(self):
        """
        フレームを取得して (ret, frame_bgr) を返す
        ※ GUI 側（OpenCV/Pillow）で扱いやすいよう BGR フォーマットで統一して返します
        """
        if self.is_dummy:
            return True, self._generate_dummy_frame()

        try:
            # Picamera2 から NumPy 配列（RGB）でキャプチャ
            frame_rgb = self.picam2.capture_array()
            
            # カメラが上下反転している場合の処理（必要に応じて）
            if self.flip_vertical:
                frame_rgb = cv2.flip(frame_rgb, 0)

            return True, frame_rgb
        except Exception as e:
            print(f"ERROR: フレーム取得失敗: {e}")
            return False, None

    def _generate_dummy_frame(self):
        """開発用ダミーフレームの生成"""
        import time
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # 背景（グラデーション）
        img[:, :] = (40, 40, 40)
        
        # 動く円アニメーション
        t = time.time()
        cx = int((self.width / 2) + np.sin(t * 2) * (self.width / 4))
        cy = int(self.height / 2)
        cv2.circle(img, (cx, cy), 40, (0, 255, 128), -1)
        
        # テキスト描画
        cv2.putText(
            img, "DUMMY CAMERA (Picamera2 Mode)", (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
        )
        return img

    def release(self):
        """カメラリソースの解放"""
        if not self.is_dummy and hasattr(self, 'picam2'):
            try:
                self.picam2.stop()
                self.picam2.close()
                print("Picamera2 を正常に停止しました。")
            except Exception as e:
                print(f"Picamera2 停止時のエラー: {e}")
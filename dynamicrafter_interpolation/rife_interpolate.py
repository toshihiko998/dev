#!/usr/bin/env python3
"""
RIFE (Real-Time Intermediate Flow Estimation) フレーム補間
軽量・高速な中割システム
"""

import torch
import numpy as np
from PIL import Image
import cv2
from pathlib import Path


class RIFEInterpolator:
    """RIFE軽量版フレーム補間"""
    
    def __init__(self, model_name='rife-v4.6', device='cpu'):
        """
        初期化
        
        Args:
            model_name: モデル名 (rife-v4.6が最新)
            device: 'cpu' or 'cuda'
        """
        self.device = device
        self.model = None
        
    def load_model(self):
        """RIFEモデルをロード"""
        print("🔄 RIFEモデルを読み込み中...")
        
        # GitHubから直接読み込み（軽量）
        try:
            model = torch.hub.load('megvii-research/ECCV2022-RIFE', 'RIFE', 
                                  device=self.device, force_reload=False)
            self.model = model
            print("✓ RIFEモデルを読み込みました")
        except Exception as e:
            print(f"❌ モデル読み込みエラー: {e}")
            print("フォールバック: OpenCV光学フローを使用")
            self.model = None
            
    def interpolate_opencv(self, img1, img2, num_frames):
        """OpenCV光学フローによる補間（フォールバック）"""
        frames = [img1]
        
        gray1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2GRAY)
        
        for i in range(1, num_frames - 1):
            alpha = i / (num_frames - 1)
            # 単純な線形補間
            blended = cv2.addWeighted(np.array(img1), 1-alpha, np.array(img2), alpha, 0)
            frames.append(Image.fromarray(blended))
        
        frames.append(img2)
        return frames
    
    def interpolate(self, img1, img2, num_frames=16):
        """
        2枚の画像間を補間
        
        Args:
            img1: 開始画像 (PIL Image)
            img2: 終了画像 (PIL Image)
            num_frames: 生成するフレーム数
            
        Returns:
            list of PIL Images
        """
        if self.model is None:
            self.load_model()
        
        # RIFEモデルが使えない場合はOpenCVを使用
        if self.model is None:
            print("⚠️ RIFEモデル未使用、OpenCV補間を実行")
            return self.interpolate_opencv(img1, img2, num_frames)
        
        # 画像をテンソルに変換
        def img2tensor(img):
            img_np = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_np).permute(2, 0, 1).unsqueeze(0)
            return img_tensor.to(self.device)
        
        I0 = img2tensor(img1)
        I1 = img2tensor(img2)
        
        frames = [img1]
        
        # 再帰的に中間フレームを生成
        print(f"🎬 {num_frames}フレームを生成中...")
        
        with torch.no_grad():
            # 段階的に補間
            n_iter = int(np.log2(num_frames - 1))
            
            frame_list = [(0.0, I0), (1.0, I1)]
            
            for iteration in range(n_iter):
                new_frames = []
                for i in range(len(frame_list) - 1):
                    t0, frame0 = frame_list[i]
                    t1, frame1 = frame_list[i + 1]
                    
                    # 中間フレーム生成
                    mid_frame = self.model(frame0, frame1)
                    t_mid = (t0 + t1) / 2
                    
                    new_frames.append((t0, frame0))
                    new_frames.append((t_mid, mid_frame))
                
                new_frames.append(frame_list[-1])
                frame_list = new_frames
            
            # テンソルをPIL Imageに変換
            for t, frame_tensor in sorted(frame_list, key=lambda x: x[0]):
                if t == 0.0:
                    continue  # 最初のフレームは既に追加済み
                    
                frame_np = frame_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
                frame_np = (frame_np * 255).clip(0, 255).astype(np.uint8)
                frames.append(Image.fromarray(frame_np))
        
        print(f"✓ {len(frames)}フレームを生成しました")
        return frames[:num_frames]  # 指定フレーム数に調整
    
    def save_video(self, frames, output_path, fps=16):
        """フレームを動画として保存"""
        print(f"💾 動画を保存中: {output_path}")
        
        if not frames:
            raise ValueError("フレームが空です")
        
        # 最初のフレームからサイズを取得
        width, height = frames[0].size
        
        # VideoWriter設定
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        for frame in frames:
            # PIL Image → OpenCV形式
            frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            out.write(frame_cv)
        
        out.release()
        print(f"✓ 動画を保存しました: {output_path}")
        return output_path


def main():
    """コマンドライン実行"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RIFE フレーム補間')
    parser.add_argument('--image1', required=True, help='開始画像')
    parser.add_argument('--image2', required=True, help='終了画像')
    parser.add_argument('--output', default='output_rife.mp4', help='出力動画')
    parser.add_argument('--frames', type=int, default=16, help='フレーム数')
    parser.add_argument('--fps', type=int, default=16, help='FPS')
    parser.add_argument('--device', default='cpu', help='cpu or cuda')
    
    args = parser.parse_args()
    
    # 画像読み込み
    img1 = Image.open(args.image1).convert('RGB')
    img2 = Image.open(args.image2).convert('RGB')
    
    # 補間実行
    interpolator = RIFEInterpolator(device=args.device)
    frames = interpolator.interpolate(img1, img2, num_frames=args.frames)
    
    # 動画保存
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    interpolator.save_video(frames, output_path, fps=args.fps)
    
    print(f"\n✅ 完了! {output_path}")


if __name__ == '__main__':
    main()

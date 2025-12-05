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
        
    def apply_motion_transform(self, img, pan_x=0, pan_y=0, zoom=1.0, rotate=0):
        """
        画像にモーション変換を適用
        
        Args:
            img: PIL Image
            pan_x: 水平移動 (-1 to 1, 画像幅の割合)
            pan_y: 垂直移動 (-1 to 1, 画像高さの割合)
            zoom: ズーム (0.5 to 2.0)
            rotate: 回転角度 (-180 to 180度)
        
        Returns:
            変換後のPIL Image
        """
        img_np = np.array(img)
        h, w = img_np.shape[:2]
        
        # 変換行列の構築
        center = (w / 2, h / 2)
        
        # 回転行列
        M_rotate = cv2.getRotationMatrix2D(center, rotate, zoom)
        
        # パン（平行移動）を追加
        M_rotate[0, 2] += pan_x * w
        M_rotate[1, 2] += pan_y * h
        
        # 変換を適用
        transformed = cv2.warpAffine(img_np, M_rotate, (w, h), 
                                      borderMode=cv2.BORDER_REFLECT)
        
        return Image.fromarray(transformed)
        
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
    
    def interpolate(self, img1, img2, num_frames=16, mode='basic', 
                   pan_x=0, pan_y=0, zoom=1.0, rotate=0):
        """
        2枚の画像間を補間
        
        Args:
            img1: 開始画像 (PIL Image)
            img2: 終了画像 (PIL Image)
            num_frames: 生成するフレーム数
            mode: 'basic', 'hybrid', 'steerable'
            pan_x, pan_y: パン移動 (-1 to 1)
            zoom: ズーム (0.5 to 2.0)
            rotate: 回転 (-180 to 180度)
            
        Returns:
            list of PIL Images
        """
        if self.model is None:
            self.load_model()
        
        # RIFEモデルが使えない場合はOpenCVを使用
        if self.model is None:
            print("⚠️ RIFEモデル未使用、OpenCV補間を実行")
            return self.interpolate_opencv(img1, img2, num_frames)
        
        # モーション制御モード
        if mode in ['hybrid', 'steerable']:
            return self.interpolate_with_motion(img1, img2, num_frames, mode,
                                               pan_x, pan_y, zoom, rotate)
        
        # 基本モード（モーションなし）
        return self.interpolate_basic(img1, img2, num_frames)
    
    def interpolate_basic(self, img1, img2, num_frames):
        """基本的なRIFE補間（モーションなし）"""
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
    
    def interpolate_with_motion(self, img1, img2, num_frames, mode,
                               pan_x, pan_y, zoom, rotate):
        """
        モーション制御付き補間
        
        Args:
            mode: 'hybrid' (元画像を変換) or 'steerable' (各フレームを変換)
        """
        print(f"🎬 {mode}モードで{num_frames}フレームを生成中...")
        print(f"   パン: ({pan_x:.2f}, {pan_y:.2f}), ズーム: {zoom:.2f}, 回転: {rotate}°")
        
        if mode == 'hybrid':
            # hybrid: 終了フレームにモーションを適用してから補間
            img2_transformed = self.apply_motion_transform(
                img2, pan_x, pan_y, zoom, rotate
            )
            return self.interpolate_basic(img1, img2_transformed, num_frames)
        
        elif mode == 'steerable':
            # steerable: 基本補間後、各フレームに段階的なモーションを適用
            frames_basic = self.interpolate_basic(img1, img2, num_frames)
            frames_motion = []
            
            for i, frame in enumerate(frames_basic):
                # 進行度 (0.0 to 1.0)
                progress = i / (len(frames_basic) - 1)
                
                # 段階的にモーションを適用
                frame_transformed = self.apply_motion_transform(
                    frame,
                    pan_x * progress,
                    pan_y * progress,
                    1.0 + (zoom - 1.0) * progress,
                    rotate * progress
                )
                frames_motion.append(frame_transformed)
            
            print(f"✓ モーション制御付き{len(frames_motion)}フレームを生成")
            return frames_motion
        
        return []
    
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
    parser.add_argument('--mode', default='basic', choices=['basic', 'hybrid', 'steerable'],
                       help='補間モード')
    parser.add_argument('--pan-x', type=float, default=0, help='パン X (-1 to 1)')
    parser.add_argument('--pan-y', type=float, default=0, help='パン Y (-1 to 1)')
    parser.add_argument('--zoom', type=float, default=1.0, help='ズーム (0.5 to 2.0)')
    parser.add_argument('--rotate', type=float, default=0, help='回転 (-180 to 180度)')
    
    args = parser.parse_args()
    
    # 画像読み込み
    img1 = Image.open(args.image1).convert('RGB')
    img2 = Image.open(args.image2).convert('RGB')
    
    # 補間実行
    interpolator = RIFEInterpolator(device=args.device)
    frames = interpolator.interpolate(
        img1, img2, 
        num_frames=args.frames,
        mode=args.mode,
        pan_x=args.pan_x,
        pan_y=args.pan_y,
        zoom=args.zoom,
        rotate=args.rotate
    )
    
    # 動画保存
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    interpolator.save_video(frames, output_path, fps=args.fps)
    
    print(f"\n✅ 完了! {output_path}")


if __name__ == '__main__':
    main()

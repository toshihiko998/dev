"""
DynamiCrafterを使った2枚の静止画から中割りフレームを生成するシステム
"""
import os
import sys
import argparse
import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
from einops import repeat
import torchvision
from pathlib import Path

# DynamiCrafterのモジュールパスを追加
SCRIPT_DIR = Path(__file__).parent
DYNAMICRAFTER_DIR = SCRIPT_DIR.parent / "DynamiCrafter"
if DYNAMICRAFTER_DIR.exists():
    sys.path.insert(0, str(DYNAMICRAFTER_DIR))
else:
    print(f"警告: DynamiCrafterディレクトリが見つかりません: {DYNAMICRAFTER_DIR}")
    print("このスクリプトは /workspaces/dev/DynamiCrafter ディレクトリから実行してください")


class FrameInterpolator:
    """
    DynamiCrafterを使用してフレーム補間を行うクラス
    """
    
    def __init__(self, model_path=None, config_path=None, device='cuda'):
        """
        初期化
        
        Args:
            model_path: DynamiCrafterのモデルパス
            config_path: 設定ファイルのパス
            device: 使用するデバイス ('cuda' or 'cpu')
        """
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.model_path = model_path or 'checkpoints/dynamicrafter_512_interp_v1/model.ckpt'
        self.config_path = config_path or 'configs/inference_512_v1.0.yaml'
        self.model = None
        self.resolution = (320, 512)  # (H, W)
        
    def setup_model(self):
        """
        DynamiCrafterモデルのセットアップ
        """
        # HuggingFaceキャッシュをDynamiCrafterディレクトリ内に設定（ディスク容量節約）
        cache_dir = Path(self.model_path).parent.parent / "hf_cache"
        cache_dir.mkdir(exist_ok=True)
        os.environ['HF_HOME'] = str(cache_dir)
        os.environ['TRANSFORMERS_CACHE'] = str(cache_dir)
        os.environ['HF_DATASETS_CACHE'] = str(cache_dir)
        
        try:
            from omegaconf import OmegaConf
            from utils.utils import instantiate_from_config
            from scripts.evaluation.funcs import load_model_checkpoint
            
            # 設定ファイルを読み込み
            config = OmegaConf.load(self.config_path)
            model_config = config.pop("model", OmegaConf.create())
            model_config['params']['unet_config']['params']['use_checkpoint'] = False
            
            # モデルを初期化
            model = instantiate_from_config(model_config)
            
            # チェックポイントを読み込み
            if os.path.exists(self.model_path):
                model = load_model_checkpoint(model, self.model_path)
                model = model.to(self.device)
                model.eval()
                self.model = model
                print(f"モデルを正常に読み込みました: {self.model_path}")
            else:
                raise FileNotFoundError(f"モデルファイルが見つかりません: {self.model_path}")
                
        except ImportError as e:
            print(f"警告: DynamiCrafterのモジュールが見つかりません: {e}")
            print("このスクリプトはDynamiCrafterリポジトリのルートディレクトリから実行してください。")
            raise
            
    def load_and_preprocess_images(self, image1_path, image2_path):
        """
        2枚の画像を読み込んで前処理
        
        Args:
            image1_path: 最初の画像のパス
            image2_path: 2番目の画像のパス
            
        Returns:
            処理済みのテンソル
        """
        transform = transforms.Compose([
            transforms.Resize(min(self.resolution)),
            transforms.CenterCrop(self.resolution),
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
        ])
        
        # 画像を読み込み
        img1 = Image.open(image1_path).convert('RGB')
        img2 = Image.open(image2_path).convert('RGB')
        
        # 変換
        img1_tensor = transform(img1)
        img2_tensor = transform(img2)
        
        return img1_tensor, img2_tensor
    
    def get_latent_z(self, videos):
        """
        ビデオをLatent spaceに変換
        
        Args:
            videos: 入力ビデオテンソル (b, c, t, h, w)
            
        Returns:
            Latentテンソル
        """
        from einops import rearrange
        
        b, c, t, h, w = videos.shape
        x = rearrange(videos, 'b c t h w -> (b t) c h w')
        z = self.model.encode_first_stage(x)
        z = rearrange(z, '(b t) c h w -> b c t h w', b=b, t=t)
        return z
    
    def interpolate(self, image1_path, image2_path, prompt="", 
                   num_frames=16, ddim_steps=50, cfg_scale=7.5, 
                   eta=1.0, fps=5, seed=123):
        """
        2枚の画像から中割りフレームを生成
        
        Args:
            image1_path: 最初の画像のパス
            image2_path: 2番目の画像のパス
            prompt: テキストプロンプト
            num_frames: 生成するフレーム数
            ddim_steps: DDIMサンプリングのステップ数
            cfg_scale: Classifier-free guidanceのスケール
            eta: DDIMのetaパラメータ
            fps: 出力動画のフレームレート
            seed: ランダムシード
            
        Returns:
            生成された動画テンソル
        """
        from pytorch_lightning import seed_everything
        from scripts.evaluation.funcs import batch_ddim_sampling
        
        # シードを設定
        seed_everything(seed)
        
        if self.model is None:
            self.setup_model()
        
        # 画像を読み込み
        img1_tensor, img2_tensor = self.load_and_preprocess_images(image1_path, image2_path)
        
        # バッチ次元を追加してデバイスに送る
        img1_tensor = img1_tensor.unsqueeze(0).to(self.device)
        img2_tensor = img2_tensor.unsqueeze(0).to(self.device)
        
        with torch.no_grad(), torch.cuda.amp.autocast():
            # テキスト条件付け
            text_emb = self.model.get_learned_conditioning([prompt])
            
            # 画像をLatent spaceに変換
            # 最初と最後のフレームとして使用
            z1 = self.get_latent_z(img1_tensor.unsqueeze(2))  # b,c,1,h,w
            z2 = self.get_latent_z(img2_tensor.unsqueeze(2))  # b,c,1,h,w
            
            # フレーム補間用の条件付けを準備
            # 最初と最後のフレームを条件として設定
            batch_size = 1
            channels = self.model.model.diffusion_model.out_channels
            h, w = self.resolution[0] // 8, self.resolution[1] // 8
            noise_shape = [batch_size, channels, num_frames, h, w]
            
            # 条件画像の埋め込みを取得
            img_emb1 = self.model.embedder(img1_tensor)
            img_emb1 = self.model.image_proj_model(img_emb1)
            
            # テキストと画像の埋め込みを結合
            imtext_cond = torch.cat([text_emb, img_emb1], dim=1)
            
            # 中割り用の条件テンソルを作成
            img_cat_cond = torch.zeros(batch_size, channels, num_frames, h, w).to(self.device)
            img_cat_cond[:, :, 0, :, :] = z1[:, :, 0, :, :]   # 最初のフレーム
            img_cat_cond[:, :, -1, :, :] = z2[:, :, 0, :, :]  # 最後のフレーム
            
            fs = torch.tensor([fps], dtype=torch.long, device=self.device)
            cond = {
                "c_crossattn": [imtext_cond],
                "fs": fs,
                "c_concat": [img_cat_cond]
            }
            
            # サンプリングを実行
            batch_samples = batch_ddim_sampling(
                self.model,
                cond,
                noise_shape,
                n_samples=1,
                ddim_steps=ddim_steps,
                ddim_eta=eta,
                cfg_scale=cfg_scale
            )
            
        return batch_samples
    
    def save_video(self, samples, output_path, fps=5):
        """
        生成された動画を保存
        
        Args:
            samples: 生成された動画テンソル (b, samples, c, t, h, w)
            output_path: 出力ファイルのパス
            fps: フレームレート
        """
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # テンソルを処理
        video = samples[0, 0]  # 最初のバッチ、最初のサンプル
        video = video.detach().cpu()
        video = torch.clamp(video.float(), -1., 1.)
        
        # [-1, 1] -> [0, 1]
        video = (video + 1.0) / 2.0
        
        # [c, t, h, w] -> [t, h, w, c]
        video = video.permute(1, 2, 3, 0)
        
        # [0, 1] -> [0, 255]
        video = (video * 255).to(torch.uint8)
        
        # 動画を保存
        torchvision.io.write_video(
            output_path,
            video,
            fps=fps,
            video_codec='h264',
            options={'crf': '10'}
        )
        
        print(f"動画を保存しました: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='DynamiCrafterを使った画像中割りシステム')
    parser.add_argument('--image1', type=str, required=True, help='最初の画像のパス')
    parser.add_argument('--image2', type=str, required=True, help='2番目の画像のパス')
    parser.add_argument('--output', type=str, default='output_videos/interpolated.mp4', 
                       help='出力動画のパス')
    parser.add_argument('--prompt', type=str, default='', help='テキストプロンプト')
    parser.add_argument('--frames', type=int, default=16, help='生成するフレーム数')
    parser.add_argument('--steps', type=int, default=50, help='DDIMサンプリングのステップ数')
    parser.add_argument('--cfg-scale', type=float, default=7.5, help='Classifier-free guidanceスケール')
    parser.add_argument('--fps', type=int, default=5, help='出力動画のFPS')
    parser.add_argument('--seed', type=int, default=123, help='ランダムシード')
    parser.add_argument('--model-path', type=str, default=None, help='モデルファイルのパス')
    parser.add_argument('--config-path', type=str, default=None, help='設定ファイルのパス')
    
    args = parser.parse_args()
    
    # 補間器を初期化
    interpolator = FrameInterpolator(
        model_path=args.model_path,
        config_path=args.config_path
    )
    
    # モデルをセットアップ
    interpolator.setup_model()
    
    # 中割りを実行
    print(f"画像の中割りを開始します...")
    print(f"入力画像1: {args.image1}")
    print(f"入力画像2: {args.image2}")
    print(f"フレーム数: {args.frames}")
    
    samples = interpolator.interpolate(
        args.image1,
        args.image2,
        prompt=args.prompt,
        num_frames=args.frames,
        ddim_steps=args.steps,
        cfg_scale=args.cfg_scale,
        fps=args.fps,
        seed=args.seed
    )
    
    # 動画を保存
    interpolator.save_video(samples, args.output, fps=args.fps)
    print("完了しました!")


if __name__ == '__main__':
    main()

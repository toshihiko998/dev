"""
シンプルなPythonインターフェースでの使用例
"""
import sys
import os

# DynamiCrafterのパスを追加（必要に応じて）
sys.path.insert(0, '/workspaces/dev/DynamiCrafter')

# interpolate.pyから必要なクラスをインポート
from interpolate import FrameInterpolator


def example_basic_usage():
    """基本的な使用例"""
    print("=== 基本的な使用例 ===")
    
    # 補間器を初期化
    interpolator = FrameInterpolator()
    
    # モデルをセットアップ
    interpolator.setup_model()
    
    # 2枚の画像から中割りを生成
    samples = interpolator.interpolate(
        image1_path='input_images/frame1.jpg',
        image2_path='input_images/frame2.jpg',
        prompt='',
        num_frames=16,
        ddim_steps=50,
        cfg_scale=7.5,
        fps=5,
        seed=123
    )
    
    # 動画を保存
    interpolator.save_video(
        samples,
        output_path='output_videos/basic_example.mp4',
        fps=5
    )
    
    print("完了: output_videos/basic_example.mp4")


def example_with_prompt():
    """テキストプロンプトを使用した例"""
    print("\n=== テキストプロンプト使用例 ===")
    
    interpolator = FrameInterpolator()
    interpolator.setup_model()
    
    samples = interpolator.interpolate(
        image1_path='input_images/start.jpg',
        image2_path='input_images/end.jpg',
        prompt='smooth camera movement',  # テキストで動きを指定
        num_frames=16,
        ddim_steps=50,
        cfg_scale=7.5,
        fps=8,
        seed=456
    )
    
    interpolator.save_video(
        samples,
        output_path='output_videos/with_prompt.mp4',
        fps=8
    )
    
    print("完了: output_videos/with_prompt.mp4")


def example_high_quality():
    """高品質設定の例"""
    print("\n=== 高品質設定の例 ===")
    
    interpolator = FrameInterpolator()
    interpolator.setup_model()
    
    samples = interpolator.interpolate(
        image1_path='input_images/scene1.jpg',
        image2_path='input_images/scene2.jpg',
        prompt='cinematic transition',
        num_frames=32,        # フレーム数を増やす
        ddim_steps=100,       # ステップ数を増やして品質向上
        cfg_scale=7.5,
        fps=10,               # FPSを上げて滑らかに
        seed=789
    )
    
    interpolator.save_video(
        samples,
        output_path='output_videos/high_quality.mp4',
        fps=10
    )
    
    print("完了: output_videos/high_quality.mp4")


def example_batch_processing():
    """複数の画像ペアを処理する例"""
    print("\n=== バッチ処理の例 ===")
    
    interpolator = FrameInterpolator()
    interpolator.setup_model()
    
    # 処理する画像ペアのリスト
    image_pairs = [
        ('input_images/pair1_a.jpg', 'input_images/pair1_b.jpg', 'transition 1'),
        ('input_images/pair2_a.jpg', 'input_images/pair2_b.jpg', 'transition 2'),
        ('input_images/pair3_a.jpg', 'input_images/pair3_b.jpg', 'transition 3'),
    ]
    
    for i, (img1, img2, prompt) in enumerate(image_pairs, 1):
        print(f"\n処理中 {i}/{len(image_pairs)}: {prompt}")
        
        samples = interpolator.interpolate(
            image1_path=img1,
            image2_path=img2,
            prompt=prompt,
            num_frames=16,
            ddim_steps=50,
            cfg_scale=7.5,
            fps=5,
            seed=123 + i
        )
        
        output_path = f'output_videos/batch_{i:02d}.mp4'
        interpolator.save_video(samples, output_path, fps=5)
        print(f"✓ 完了: {output_path}")
    
    print("\nバッチ処理が完了しました！")


def example_custom_settings():
    """カスタム設定の例"""
    print("\n=== カスタム設定の例 ===")
    
    # カスタムモデルパスと設定ファイルを指定
    interpolator = FrameInterpolator(
        model_path='checkpoints/dynamicrafter_512_interp_v1/model.ckpt',
        config_path='configs/inference_512_v1.0.yaml',
        device='cuda'  # または 'cpu'
    )
    
    interpolator.setup_model()
    
    # 異なるパラメータを試す
    configs = [
        {'cfg_scale': 5.0, 'seed': 111, 'output': 'low_guidance.mp4'},
        {'cfg_scale': 7.5, 'seed': 222, 'output': 'medium_guidance.mp4'},
        {'cfg_scale': 10.0, 'seed': 333, 'output': 'high_guidance.mp4'},
    ]
    
    for config in configs:
        print(f"\nCFG Scale: {config['cfg_scale']}")
        
        samples = interpolator.interpolate(
            image1_path='input_images/test1.jpg',
            image2_path='input_images/test2.jpg',
            prompt='',
            num_frames=16,
            ddim_steps=50,
            cfg_scale=config['cfg_scale'],
            fps=5,
            seed=config['seed']
        )
        
        output_path = f"output_videos/{config['output']}"
        interpolator.save_video(samples, output_path, fps=5)
        print(f"✓ 完了: {output_path}")


if __name__ == '__main__':
    print("DynamiCrafter Frame Interpolation - 使用例")
    print("=" * 50)
    
    # 注意: これらの例を実行する前に、input_imagesディレクトリに
    # 対応する画像ファイルを配置する必要があります
    
    # 実行したい例のコメントを外してください
    
    # example_basic_usage()
    # example_with_prompt()
    # example_high_quality()
    # example_batch_processing()
    # example_custom_settings()
    
    print("\n注意: 実際に実行するには、input_imagesディレクトリに")
    print("画像ファイルを配置し、使用したい例のコメントを外してください。")

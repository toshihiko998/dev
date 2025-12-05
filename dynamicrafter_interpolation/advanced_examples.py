"""
DynamiCrafter + Steerable-Motion統合システムの高度な使用例
"""
import sys
sys.path.insert(0, '/workspaces/dev/DynamiCrafter')

from advanced_interpolate import AdvancedFrameInterpolator


def example_1_camera_pan():
    """例1: カメラパン効果"""
    print("=" * 60)
    print("例1: カメラパン効果で中割り生成")
    print("=" * 60)
    
    interpolator = AdvancedFrameInterpolator(interpolation_method='hybrid')
    interpolator.setup_model()
    
    # 右へパン
    motion_control = {
        'camera': {
            'pan_x': 0.5,  # 右へ移動
            'pan_y': 0.0,
            'zoom': 0.0,
            'rotate': 0.0
        }
    }
    
    samples = interpolator.interpolate(
        image1_path='input_images/scene1.jpg',
        image2_path='input_images/scene2.jpg',
        prompt='smooth camera panning',
        num_frames=16,
        ddim_steps=50,
        motion_control=motion_control,
        seed=123
    )
    
    interpolator.save_video(samples, 'output_videos/example_pan.mp4')
    print("✓ 完了: output_videos/example_pan.mp4\n")


def example_2_zoom_effect():
    """例2: ズーム効果"""
    print("=" * 60)
    print("例2: ズームイン効果で中割り生成")
    print("=" * 60)
    
    interpolator = AdvancedFrameInterpolator(interpolation_method='hybrid')
    interpolator.setup_model()
    
    # ズームイン
    motion_control = {
        'camera': {
            'pan_x': 0.0,
            'pan_y': 0.0,
            'zoom': 0.8,  # ズームイン
            'rotate': 0.0
        }
    }
    
    samples = interpolator.interpolate(
        image1_path='input_images/portrait1.jpg',
        image2_path='input_images/portrait2.jpg',
        prompt='dramatic zoom in',
        num_frames=20,
        ddim_steps=60,
        cfg_scale=8.0,
        motion_control=motion_control,
        seed=456
    )
    
    interpolator.save_video(samples, 'output_videos/example_zoom.mp4', fps=8)
    print("✓ 完了: output_videos/example_zoom.mp4\n")


def example_3_rotation():
    """例3: 回転効果"""
    print("=" * 60)
    print("例3: 回転効果で中割り生成")
    print("=" * 60)
    
    interpolator = AdvancedFrameInterpolator(interpolation_method='hybrid')
    interpolator.setup_model()
    
    # 時計回りに45度回転
    motion_control = {
        'camera': {
            'pan_x': 0.0,
            'pan_y': 0.0,
            'zoom': 0.0,
            'rotate': 45  # 45度回転
        }
    }
    
    samples = interpolator.interpolate(
        image1_path='input_images/object1.jpg',
        image2_path='input_images/object2.jpg',
        prompt='rotating view, smooth transition',
        num_frames=16,
        ddim_steps=50,
        motion_control=motion_control,
        seed=789
    )
    
    interpolator.save_video(samples, 'output_videos/example_rotate.mp4')
    print("✓ 完了: output_videos/example_rotate.mp4\n")


def example_4_combined_motion():
    """例4: 複合モーション"""
    print("=" * 60)
    print("例4: パン+ズームの複合モーション")
    print("=" * 60)
    
    interpolator = AdvancedFrameInterpolator(interpolation_method='hybrid')
    interpolator.setup_model()
    
    # パンしながらズームイン
    motion_control = {
        'camera': {
            'pan_x': 0.3,   # 右にパン
            'pan_y': -0.2,  # 上にパン
            'zoom': 0.6,    # ズームイン
            'rotate': 0.0
        }
    }
    
    samples = interpolator.interpolate(
        image1_path='input_images/landscape1.jpg',
        image2_path='input_images/landscape2.jpg',
        prompt='cinematic camera movement, pan and zoom',
        num_frames=24,
        ddim_steps=70,
        cfg_scale=7.5,
        fps=8,
        motion_control=motion_control,
        seed=111
    )
    
    interpolator.save_video(samples, 'output_videos/example_combined.mp4', fps=8)
    print("✓ 完了: output_videos/example_combined.mp4\n")


def example_5_method_comparison():
    """例5: 3つの手法を比較"""
    print("=" * 60)
    print("例5: 手法比較 (DynamiCrafter / Steerable / Hybrid)")
    print("=" * 60)
    
    methods = ['dynamicrafter', 'steerable', 'hybrid']
    
    for method in methods:
        print(f"\n処理中: {method}モード...")
        
        interpolator = AdvancedFrameInterpolator(interpolation_method=method)
        interpolator.setup_model()
        
        motion_control = {
            'camera': {
                'pan_x': 0.4,
                'pan_y': 0.0,
                'zoom': 0.3,
                'rotate': 15
            }
        }
        
        samples = interpolator.interpolate(
            image1_path='input_images/compare1.jpg',
            image2_path='input_images/compare2.jpg',
            prompt='smooth camera motion',
            num_frames=16,
            ddim_steps=50,
            motion_control=motion_control if method != 'dynamicrafter' else None,
            seed=222
        )
        
        output_path = f'output_videos/comparison_{method}.mp4'
        interpolator.save_video(samples, output_path)
        print(f"✓ 完了: {output_path}")
    
    print("\n全ての比較動画が生成されました！")


def example_6_high_quality_cinematic():
    """例6: シネマティック高品質中割り"""
    print("=" * 60)
    print("例6: 高品質シネマティック中割り")
    print("=" * 60)
    
    interpolator = AdvancedFrameInterpolator(interpolation_method='hybrid')
    interpolator.setup_model()
    
    # ドリーズーム風の効果
    motion_control = {
        'camera': {
            'pan_x': 0.0,
            'pan_y': 0.0,
            'zoom': -0.5,  # ズームアウト
            'rotate': 0.0
        }
    }
    
    samples = interpolator.interpolate(
        image1_path='input_images/cinematic1.jpg',
        image2_path='input_images/cinematic2.jpg',
        prompt='cinematic dolly zoom effect, dramatic atmosphere',
        num_frames=32,        # 多めのフレーム
        ddim_steps=100,       # 高品質設定
        cfg_scale=8.5,
        fps=10,
        motion_control=motion_control,
        seed=333
    )
    
    interpolator.save_video(samples, 'output_videos/example_cinematic.mp4', fps=10)
    print("✓ 完了: output_videos/example_cinematic.mp4\n")


def example_7_batch_with_motion():
    """例7: 異なるモーションでバッチ処理"""
    print("=" * 60)
    print("例7: 複数のモーションパターンでバッチ処理")
    print("=" * 60)
    
    interpolator = AdvancedFrameInterpolator(interpolation_method='hybrid')
    interpolator.setup_model()
    
    # 異なるモーションパターン
    motion_patterns = [
        {
            'name': 'pan_left',
            'control': {'camera': {'pan_x': -0.6, 'pan_y': 0, 'zoom': 0, 'rotate': 0}},
            'prompt': 'camera panning left'
        },
        {
            'name': 'zoom_in',
            'control': {'camera': {'pan_x': 0, 'pan_y': 0, 'zoom': 0.8, 'rotate': 0}},
            'prompt': 'zoom in smoothly'
        },
        {
            'name': 'rotate_ccw',
            'control': {'camera': {'pan_x': 0, 'pan_y': 0, 'zoom': 0, 'rotate': -30}},
            'prompt': 'counter-clockwise rotation'
        },
        {
            'name': 'complex',
            'control': {'camera': {'pan_x': 0.3, 'pan_y': -0.2, 'zoom': 0.5, 'rotate': 20}},
            'prompt': 'complex camera movement'
        }
    ]
    
    for i, pattern in enumerate(motion_patterns, 1):
        print(f"\n[{i}/{len(motion_patterns)}] 処理中: {pattern['name']}")
        
        samples = interpolator.interpolate(
            image1_path='input_images/batch_start.jpg',
            image2_path='input_images/batch_end.jpg',
            prompt=pattern['prompt'],
            num_frames=16,
            ddim_steps=50,
            motion_control=pattern['control'],
            seed=400 + i
        )
        
        output_path = f"output_videos/batch_{pattern['name']}.mp4"
        interpolator.save_video(samples, output_path)
        print(f"✓ 完了: {output_path}")
    
    print("\n全てのバッチ処理が完了しました！")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("DynamiCrafter + Steerable-Motion 統合システム")
    print("高度な使用例")
    print("=" * 60 + "\n")
    
    print("注意: これらの例を実行する前に、input_imagesディレクトリに")
    print("対応する画像ファイルを配置してください。\n")
    
    # 実行したい例のコメントを外してください
    
    # example_1_camera_pan()
    # example_2_zoom_effect()
    # example_3_rotation()
    # example_4_combined_motion()
    # example_5_method_comparison()
    # example_6_high_quality_cinematic()
    # example_7_batch_with_motion()
    
    print("\n実行するには、使用したい例のコメントを外してください。")

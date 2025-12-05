#!/usr/bin/env python3
"""
DynamiCrafter Frame Interpolation WebUI
Gradioベースの使いやすいWebインターフェース
"""

import os
import sys
import gradio as gr
from pathlib import Path
import torch
from PIL import Image
import numpy as np

# DynamiCrafterのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "DynamiCrafter"))

from interpolate import FrameInterpolator
from advanced_interpolate import AdvancedFrameInterpolator


class WebUI:
    def __init__(self):
        self.basic_interpolator = None
        self.advanced_interpolator = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def initialize_basic(self):
        """基本モデルの初期化"""
        if self.basic_interpolator is None:
            print("🔄 基本モデルを初期化中...")
            self.basic_interpolator = FrameInterpolator(device=self.device)
            print("✓ 基本モデル初期化完了")
        return self.basic_interpolator
    
    def initialize_advanced(self):
        """高度なモデルの初期化"""
        if self.advanced_interpolator is None:
            print("🔄 高度なモデルを初期化中...")
            self.advanced_interpolator = AdvancedFrameInterpolator(device=self.device)
            print("✓ 高度なモデル初期化完了")
        return self.advanced_interpolator
    
    def basic_interpolate(
        self,
        image1,
        image2,
        num_frames,
        fps,
        prompt,
        cfg_scale,
        ddim_steps,
        progress=gr.Progress()
    ):
        """基本的な中割補間"""
        try:
            progress(0, desc="モデルを初期化中...")
            interpolator = self.initialize_basic()
            
            # 画像をPILに変換
            if isinstance(image1, np.ndarray):
                image1 = Image.fromarray(image1)
            if isinstance(image2, np.ndarray):
                image2 = Image.fromarray(image2)
            
            # 出力パス
            output_dir = Path(__file__).parent / "output_videos"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "webui_basic_output.mp4"
            
            progress(0.2, desc="中割処理を実行中...")
            
            # 中割実行
            video_path = interpolator.interpolate(
                image1=image1,
                image2=image2,
                num_frames=num_frames,
                output_path=str(output_path),
                prompt=prompt if prompt else "high quality, smooth motion",
                fps=fps,
                cfg_scale=cfg_scale,
                ddim_steps=ddim_steps
            )
            
            progress(1.0, desc="完了!")
            
            return str(video_path), f"✓ 動画を生成しました: {video_path}"
            
        except Exception as e:
            error_msg = f"❌ エラー: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return None, error_msg
    
    def advanced_interpolate(
        self,
        image1,
        image2,
        num_frames,
        fps,
        prompt,
        mode,
        pan_x,
        pan_y,
        zoom,
        rotate,
        cfg_scale,
        ddim_steps,
        progress=gr.Progress()
    ):
        """モーション制御付き中割補間"""
        try:
            progress(0, desc="高度なモデルを初期化中...")
            interpolator = self.initialize_advanced()
            
            # 画像をPILに変換
            if isinstance(image1, np.ndarray):
                image1 = Image.fromarray(image1)
            if isinstance(image2, np.ndarray):
                image2 = Image.fromarray(image2)
            
            # 出力パス
            output_dir = Path(__file__).parent / "output_videos"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "webui_advanced_output.mp4"
            
            progress(0.2, desc="モーション制御付き中割処理を実行中...")
            
            # モーションパラメータ
            motion_params = {
                'pan_x': pan_x,
                'pan_y': pan_y,
                'zoom': zoom,
                'rotate': rotate
            }
            
            # 中割実行
            video_path = interpolator.interpolate(
                image1=image1,
                image2=image2,
                num_frames=num_frames,
                output_path=str(output_path),
                prompt=prompt if prompt else "high quality, smooth motion",
                fps=fps,
                mode=mode,
                motion_params=motion_params,
                cfg_scale=cfg_scale,
                ddim_steps=ddim_steps
            )
            
            progress(1.0, desc="完了!")
            
            motion_info = f"カメラワーク: Pan X={pan_x}, Pan Y={pan_y}, Zoom={zoom}, Rotate={rotate}°"
            return str(video_path), f"✓ 動画を生成しました\n{motion_info}\n保存先: {video_path}"
            
        except Exception as e:
            error_msg = f"❌ エラー: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return None, error_msg


def create_ui():
    """WebUIの作成"""
    webui = WebUI()
    
    with gr.Blocks(title="DynamiCrafter Frame Interpolation", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🎬 DynamiCrafter Frame Interpolation WebUI
        
        静止画2枚から滑らかな中割アニメーションを生成します
        """)
        
        with gr.Tabs() as tabs:
            # ====== 基本モード ======
            with gr.Tab("🎨 基本モード"):
                gr.Markdown("### シンプルな中割補間")
                
                with gr.Row():
                    with gr.Column():
                        basic_image1 = gr.Image(label="開始フレーム", type="numpy", height=300)
                        basic_image2 = gr.Image(label="終了フレーム", type="numpy", height=300)
                        
                        basic_prompt = gr.Textbox(
                            label="プロンプト（オプション）",
                            placeholder="high quality, smooth motion",
                            lines=2
                        )
                        
                        with gr.Row():
                            basic_frames = gr.Slider(8, 32, value=16, step=8, label="フレーム数")
                            basic_fps = gr.Slider(8, 30, value=16, step=1, label="FPS")
                        
                        with gr.Accordion("詳細設定", open=False):
                            basic_cfg = gr.Slider(1.0, 20.0, value=7.5, step=0.5, label="CFG Scale")
                            basic_steps = gr.Slider(10, 100, value=50, step=10, label="DDIM Steps")
                        
                        basic_btn = gr.Button("🎬 中割生成", variant="primary", size="lg")
                    
                    with gr.Column():
                        basic_output = gr.Video(label="生成された動画")
                        basic_status = gr.Textbox(label="ステータス", lines=3)
                
                basic_btn.click(
                    fn=webui.basic_interpolate,
                    inputs=[
                        basic_image1, basic_image2, basic_frames, basic_fps,
                        basic_prompt, basic_cfg, basic_steps
                    ],
                    outputs=[basic_output, basic_status]
                )
            
            # ====== モーション制御モード ======
            with gr.Tab("🎥 モーション制御モード"):
                gr.Markdown("### カメラワーク付き高度な中割補間")
                
                with gr.Row():
                    with gr.Column():
                        adv_image1 = gr.Image(label="開始フレーム", type="numpy", height=300)
                        adv_image2 = gr.Image(label="終了フレーム", type="numpy", height=300)
                        
                        adv_prompt = gr.Textbox(
                            label="プロンプト（オプション）",
                            placeholder="cinematic camera movement, smooth motion",
                            lines=2
                        )
                        
                        adv_mode = gr.Radio(
                            choices=["dynamicrafter", "steerable", "hybrid"],
                            value="hybrid",
                            label="モード",
                            info="dynamicrafter: 基本, steerable: モーション重視, hybrid: バランス"
                        )
                        
                        with gr.Row():
                            adv_frames = gr.Slider(8, 32, value=16, step=8, label="フレーム数")
                            adv_fps = gr.Slider(8, 30, value=16, step=1, label="FPS")
                        
                        gr.Markdown("#### 🎬 カメラワーク設定")
                        
                        with gr.Row():
                            adv_pan_x = gr.Slider(-5.0, 5.0, value=0.0, step=0.1, label="パン X (横移動)")
                            adv_pan_y = gr.Slider(-5.0, 5.0, value=0.0, step=0.1, label="パン Y (縦移動)")
                        
                        with gr.Row():
                            adv_zoom = gr.Slider(0.5, 2.0, value=1.0, step=0.1, label="ズーム")
                            adv_rotate = gr.Slider(-180, 180, value=0, step=5, label="回転 (度)")
                        
                        with gr.Accordion("詳細設定", open=False):
                            adv_cfg = gr.Slider(1.0, 20.0, value=7.5, step=0.5, label="CFG Scale")
                            adv_steps = gr.Slider(10, 100, value=50, step=10, label="DDIM Steps")
                        
                        # プリセットボタン
                        gr.Markdown("#### 📋 プリセット")
                        with gr.Row():
                            preset_pan_right = gr.Button("→ 右へパン", size="sm")
                            preset_zoom_in = gr.Button("🔍 ズームイン", size="sm")
                            preset_rotate = gr.Button("🔄 回転", size="sm")
                            preset_reset = gr.Button("↺ リセット", size="sm")
                        
                        adv_btn = gr.Button("🎥 モーション制御中割生成", variant="primary", size="lg")
                    
                    with gr.Column():
                        adv_output = gr.Video(label="生成された動画")
                        adv_status = gr.Textbox(label="ステータス", lines=5)
                
                # プリセット設定
                preset_pan_right.click(
                    lambda: (2.0, 0.0, 1.0, 0),
                    outputs=[adv_pan_x, adv_pan_y, adv_zoom, adv_rotate]
                )
                preset_zoom_in.click(
                    lambda: (0.0, 0.0, 1.5, 0),
                    outputs=[adv_pan_x, adv_pan_y, adv_zoom, adv_rotate]
                )
                preset_rotate.click(
                    lambda: (0.0, 0.0, 1.0, 45),
                    outputs=[adv_pan_x, adv_pan_y, adv_zoom, adv_rotate]
                )
                preset_reset.click(
                    lambda: (0.0, 0.0, 1.0, 0),
                    outputs=[adv_pan_x, adv_pan_y, adv_zoom, adv_rotate]
                )
                
                adv_btn.click(
                    fn=webui.advanced_interpolate,
                    inputs=[
                        adv_image1, adv_image2, adv_frames, adv_fps, adv_prompt,
                        adv_mode, adv_pan_x, adv_pan_y, adv_zoom, adv_rotate,
                        adv_cfg, adv_steps
                    ],
                    outputs=[adv_output, adv_status]
                )
            
            # ====== 使い方 ======
            with gr.Tab("📖 使い方"):
                gr.Markdown("""
                ## 🎬 DynamiCrafter Frame Interpolation の使い方
                
                ### 基本モード
                1. **開始フレーム**と**終了フレーム**の2枚の画像をアップロード
                2. **フレーム数**を選択（8, 16, 24, 32フレーム）
                3. **FPS**を設定（推奨: 16fps）
                4. オプションで**プロンプト**を入力して画質を向上
                5. 「中割生成」ボタンをクリック
                
                ### モーション制御モード（高度）
                基本モードに加えて、カメラワークを制御できます:
                
                #### カメラパラメータ
                - **パン X/Y**: カメラの水平・垂直移動（-5.0 ～ 5.0）
                - **ズーム**: カメラの拡大・縮小（0.5 ～ 2.0）
                - **回転**: カメラの回転角度（-180° ～ 180°）
                
                #### モード選択
                - **dynamicrafter**: 標準のDynamiCrafter（自然な補間）
                - **steerable**: モーション制御重視（カメラワーク強調）
                - **hybrid**: バランス型（推奨）
                
                #### プリセット
                - **右へパン**: Pan X = 2.0（カメラが右に移動）
                - **ズームイン**: Zoom = 1.5（カメラが寄る）
                - **回転**: Rotate = 45°（カメラが回転）
                - **リセット**: すべてデフォルトに戻す
                
                ### 💡 ヒント
                - 解像度は自動的に512x320にリサイズされます
                - プロンプト例: "cinematic motion", "smooth camera movement", "high quality animation"
                - CFG Scaleが高いほど、プロンプトに忠実になります（推奨: 7.5）
                - DDIM Stepsが多いほど高品質ですが、時間がかかります（推奨: 50）
                
                ### ⚙️ 技術仕様
                - **モデル**: DynamiCrafter 512_interp_v1
                - **解像度**: 320x512
                - **フレーム数**: 8～32フレーム
                - **モーション制御**: Steerable-Motionベース
                - **デバイス**: {device}
                """.format(device=webui.device.upper()))
        
        gr.Markdown("""
        ---
        <div style="text-align: center; color: #666;">
            DynamiCrafter Frame Interpolation WebUI v1.0<br>
            Powered by DynamiCrafter + Steerable-Motion
        </div>
        """)
    
    return app


if __name__ == "__main__":
    print("=" * 60)
    print("DynamiCrafter Frame Interpolation WebUI")
    print("=" * 60)
    print(f"🖥️  デバイス: {'CUDA (GPU)' if torch.cuda.is_available() else 'CPU'}")
    print("🌐 WebUIを起動中...")
    print()
    
    app = create_ui()
    app.launch(
        server_name="0.0.0.0",  # すべてのインターフェースでリッスン
        server_port=7860,
        share=False,  # 公開リンクを生成する場合はTrue
        show_error=True
    )

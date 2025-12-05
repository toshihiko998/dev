#!/usr/bin/env python3
"""
DynamiCrafter Frame Interpolation Simple WebUI
軽量版Gradio WebUI
"""

import gradio as gr
import subprocess
import os
from pathlib import Path

# 出力ディレクトリ
OUTPUT_DIR = Path(__file__).parent / "output_videos"
INPUT_DIR = Path(__file__).parent / "input_images"
OUTPUT_DIR.mkdir(exist_ok=True)
INPUT_DIR.mkdir(exist_ok=True)

def run_interpolation(image1, image2, num_frames, fps, mode, pan_x, pan_y, zoom, rotate):
    """中割処理を実行"""
    try:
        # 画像を保存
        img1_path = INPUT_DIR / "temp_frame1.jpg"
        img2_path = INPUT_DIR / "temp_frame2.jpg"
        
        from PIL import Image
        import numpy as np
        
        if isinstance(image1, np.ndarray):
            Image.fromarray(image1).save(img1_path)
        else:
            image1.save(img1_path)
            
        if isinstance(image2, np.ndarray):
            Image.fromarray(image2).save(img2_path)
        else:
            image2.save(img2_path)
        
        output_path = OUTPUT_DIR / f"output_{mode}.mp4"
        
        # コマンド構築
        dynamicrafter_dir = Path(__file__).parent.parent / "DynamiCrafter"
        interp_dir = Path(__file__).parent
        
        if mode == "basic":
            script_path = interp_dir / "interpolate.py"
            cmd = [
                "python3", str(script_path),
                "--image1", str(img1_path.resolve()),
                "--image2", str(img2_path.resolve()),
                "--output", str(output_path.resolve()),
                "--frames", str(num_frames),
                "--fps", str(fps)
            ]
        else:
            script_path = interp_dir / "advanced_interpolate.py"
            cmd = [
                "python3", str(script_path),
                "--image1", str(img1_path.resolve()),
                "--image2", str(img2_path.resolve()),
                "--output", str(output_path.resolve()),
                "--frames", str(num_frames),
                "--fps", str(fps),
                "--mode", mode,
                "--pan-x", str(pan_x),
                "--pan-y", str(pan_y),
                "--zoom", str(zoom),
                "--rotate", str(rotate)
            ]
        
        # 実行（DynamiCrafterディレクトリから実行）
        # CPU版は処理に時間がかかるため、タイムアウトを30分に設定
        result = subprocess.run(
            cmd,
            cwd=str(dynamicrafter_dir),
            capture_output=True,
            text=True,
            timeout=1800  # 30分
        )
        
        if result.returncode == 0:
            if output_path.exists():
                return str(output_path), f"✓ 成功!\n\n生成: {output_path}\n\n{result.stdout}"
            else:
                return None, f"❌ 動画ファイルが生成されませんでした\n\n{result.stdout}\n{result.stderr}"
        else:
            return None, f"❌ エラー (code {result.returncode})\n\n{result.stderr}\n\n{result.stdout}"
            
    except subprocess.TimeoutExpired:
        return None, "❌ タイムアウト: 処理に30分以上かかりました。CPUモードのため時間がかかります。"
    except Exception as e:
        import traceback
        return None, f"❌ エラー: {str(e)}\n\n{traceback.format_exc()}"


# UI作成
with gr.Blocks(title="DynamiCrafter WebUI") as app:
    gr.Markdown("# 🎬 DynamiCrafter Frame Interpolation")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 入力画像")
            image1 = gr.Image(label="開始フレーム", type="numpy")
            image2 = gr.Image(label="終了フレーム", type="numpy")
            
            gr.Markdown("### 設定")
            mode = gr.Radio(
                choices=["basic", "hybrid", "steerable"],
                value="basic",
                label="モード"
            )
            num_frames = gr.Slider(8, 32, value=16, step=8, label="フレーム数")
            fps = gr.Slider(8, 30, value=16, step=1, label="FPS")
            
            with gr.Accordion("カメラワーク（モード=hybrid/steerable時のみ）", open=False):
                pan_x = gr.Slider(-5, 5, value=0, step=0.5, label="パン X")
                pan_y = gr.Slider(-5, 5, value=0, step=0.5, label="パン Y")
                zoom = gr.Slider(0.5, 2, value=1, step=0.1, label="ズーム")
                rotate = gr.Slider(-180, 180, value=0, step=15, label="回転")
            
            btn = gr.Button("🎬 生成", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### 出力")
            output_video = gr.Video(label="生成動画")
            status = gr.Textbox(label="ステータス", lines=10)
    
    btn.click(
        fn=run_interpolation,
        inputs=[image1, image2, num_frames, fps, mode, pan_x, pan_y, zoom, rotate],
        outputs=[output_video, status]
    )
    
    gr.Markdown("""
    ---
    ### 💡 使い方
    1. 開始・終了フレーム画像をアップロード
    2. モードを選択（basic: 基本、hybrid/steerable: カメラワーク付き）
    3. フレーム数・FPSを設定
    4. 「生成」ボタンをクリック
    
    ⚠️ **CPU版のため処理に時間がかかります**
    - 初回実行: CLIPモデルダウンロード（数分） + モデル読み込み（数分） + 生成処理（10-30分）
    - 2回目以降: モデル読み込み（数分） + 生成処理（10-30分）
    - フレーム数が多いほど時間がかかります（8フレーム推奨）
    
    💡 **ヒント**:
    - 処理中はブラウザを閉じないでください
    - タイムアウトは30分に設定されています
    - エラーが出た場合はフレーム数を減らしてください
    """)

if __name__ == "__main__":
    print("=" * 50)
    print("DynamiCrafter Simple WebUI")
    print("=" * 50)
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

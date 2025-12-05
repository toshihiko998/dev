#!/usr/bin/env python3
"""
RIFE軽量版WebUI
高速フレーム補間システム
"""

import gradio as gr
import subprocess
from pathlib import Path
import time

# 出力ディレクトリ
OUTPUT_DIR = Path(__file__).parent / "output_videos"
INPUT_DIR = Path(__file__).parent / "input_images"
OUTPUT_DIR.mkdir(exist_ok=True)
INPUT_DIR.mkdir(exist_ok=True)


def run_rife_interpolation(image1, image2, num_frames, fps):
    """RIFE補間を実行"""
    try:
        from PIL import Image
        import numpy as np
        
        # 画像を保存
        img1_path = INPUT_DIR / "temp_frame1.jpg"
        img2_path = INPUT_DIR / "temp_frame2.jpg"
        
        if isinstance(image1, np.ndarray):
            Image.fromarray(image1).save(img1_path)
        else:
            image1.save(img1_path)
            
        if isinstance(image2, np.ndarray):
            Image.fromarray(image2).save(img2_path)
        else:
            image2.save(img2_path)
        
        output_path = OUTPUT_DIR / "output_rife.mp4"
        
        # RIFEスクリプト実行
        script_path = Path(__file__).parent / "rife_interpolate.py"
        
        cmd = [
            "python3", str(script_path),
            "--image1", str(img1_path),
            "--image2", str(img2_path),
            "--output", str(output_path),
            "--frames", str(num_frames),
            "--fps", str(fps),
            "--device", "cpu"
        ]
        
        start_time = time.time()
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5分
        )
        
        elapsed = int(time.time() - start_time)
        
        if result.returncode == 0:
            if output_path.exists():
                return str(output_path), f"✓ 成功!\n\n処理時間: {elapsed}秒\n\n{result.stdout}"
            else:
                return None, f"❌ 動画ファイルが生成されませんでした\n\n{result.stdout}"
        else:
            return None, f"❌ エラー (code {result.returncode})\n\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        return None, "❌ タイムアウト: 処理に5分以上かかりました"
    except Exception as e:
        import traceback
        return None, f"❌ エラー: {str(e)}\n\n{traceback.format_exc()}"


# UI作成
with gr.Blocks(title="RIFE フレーム補間") as app:
    gr.Markdown("""
    # ⚡ RIFE フレーム補間 (軽量・高速版)
    
    **DynamiCrafterの代わりに軽量なRIFEを使用**
    - モデルサイズ: 30MB (DynamiCrafter: 9.8GB)
    - 処理速度: 1-2分 (DynamiCrafter: 10-30分)
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 入力画像")
            image1 = gr.Image(label="開始フレーム", type="numpy")
            image2 = gr.Image(label="終了フレーム", type="numpy")
            
            gr.Markdown("### 設定")
            num_frames = gr.Slider(4, 32, value=16, step=4, label="フレーム数")
            fps = gr.Slider(8, 30, value=16, step=1, label="FPS")
            
            btn = gr.Button("⚡ 高速生成", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### 出力")
            output_video = gr.Video(label="生成動画")
            status = gr.Textbox(label="ステータス", lines=10)
    
    btn.click(
        fn=run_rife_interpolation,
        inputs=[image1, image2, num_frames, fps],
        outputs=[output_video, status]
    )
    
    gr.Markdown("""
    ---
    ### 💡 使い方
    1. 開始・終了フレーム画像をアップロード
    2. フレーム数・FPSを設定
    3. 「高速生成」ボタンをクリック
    
    ### ✨ RIFEの利点
    - ⚡ **超高速**: 1-2分で完了（CPUでも高速）
    - 🪶 **超軽量**: モデルサイズ30MB
    - 🎨 **高品質**: 最先端の補間アルゴリズム
    - 💻 **低リソース**: メモリ使用量が少ない
    
    ### 📊 比較
    | 項目 | RIFE | DynamiCrafter |
    |------|------|---------------|
    | モデルサイズ | 30MB | 9.8GB |
    | 処理時間(CPU) | 1-2分 | 10-30分 |
    | メモリ使用量 | ~1GB | ~8GB |
    | 品質 | 高 | 非常に高 |
    """)

if __name__ == "__main__":
    print("=" * 50)
    print("RIFE 軽量版 WebUI")
    print("=" * 50)
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,  # 別ポート
        share=False
    )

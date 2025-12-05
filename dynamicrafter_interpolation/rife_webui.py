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


def run_rife_interpolation(image1, image2, num_frames, fps, save_path, mode, 
                          pan_x, pan_y, zoom, rotate):
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
            "--device", "cpu",
            "--mode", mode,
            "--pan-x", str(pan_x),
            "--pan-y", str(pan_y),
            "--zoom", str(zoom),
            "--rotate", str(rotate)
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
                # ユーザー指定の保存パス、または自動生成
                import shutil
                if save_path and save_path.strip():
                    download_path = Path(save_path.strip())
                    download_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    download_path = OUTPUT_DIR / f"rife_{mode}_{timestamp}.mp4"
                
                shutil.copy(output_path, download_path)
                return str(download_path), f"✓ 成功!\n\n保存先: {download_path}\n処理時間: {elapsed}秒\n\n{result.stdout}"
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
            
            mode = gr.Radio(
                choices=["basic", "hybrid", "steerable"],
                value="basic",
                label="モード",
                info="basic: 基本 | hybrid: 終了フレーム変換 | steerable: 段階的モーション"
            )
            
            with gr.Accordion("🎥 カメラワーク (hybrid/steerable時のみ)", open=False):
                with gr.Row():
                    pan_x = gr.Slider(-1, 1, value=0, step=0.1, label="パン X")
                    pan_y = gr.Slider(-1, 1, value=0, step=0.1, label="パン Y")
                with gr.Row():
                    zoom = gr.Slider(0.5, 2, value=1, step=0.1, label="ズーム")
                    rotate = gr.Slider(-180, 180, value=0, step=15, label="回転")
            
            gr.Markdown("### 💾 保存先")
            save_path = gr.Textbox(
                label="保存先パス (空欄=自動生成)",
                placeholder="例: /workspaces/dev/my_video.mp4 または C:\\Users\\name\\video.mp4",
                value=""
            )
            
            btn = gr.Button("⚡ 高速生成", variant="primary", size="lg")
        
        with gr.Column():
            gr.Markdown("### 出力")
            output_video = gr.Video(label="生成動画プレビュー")
            status = gr.Textbox(label="ステータス", lines=10)
            download_btn = gr.File(label="📥 ダウンロード")
    
    btn.click(
        fn=run_rife_interpolation,
        inputs=[image1, image2, num_frames, fps, save_path, mode, pan_x, pan_y, zoom, rotate],
        outputs=[download_btn, status]
    )
    
    gr.Markdown("""
    ---
    ### 💡 使い方
    1. 開始・終了フレーム画像をアップロード
    2. モードを選択
       - **basic**: 基本的な補間のみ
       - **hybrid**: 終了フレームにモーション適用してから補間
       - **steerable**: 各フレームに段階的なモーション適用
    3. hybrid/steerableの場合、カメラワークを設定
    4. 「高速生成」ボタンをクリック
    5. **📥ダウンロードボタンからローカルに保存**
    
    ### 🎥 モーション制御
    - **パン X/Y**: カメラの水平/垂直移動 (-1 〜 1)
    - **ズーム**: カメラのズームイン/アウト (0.5 〜 2.0)
    - **回転**: カメラの回転 (-180° 〜 180°)
    
    ### ✨ RIFEの利点
    - ⚡ **超高速**: 1-2分で完了（CPUでも高速）
    - 🪶 **超軽量**: モデルサイズ30MB
    - 🎨 **高品質**: 最先端の補間アルゴリズム
    - 💻 **低リソース**: メモリ使用量が少ない
    - 🎬 **モーション制御**: DynamiCrafter同様のカメラワーク
    
    ### 📊 比較
    | 項目 | RIFE | DynamiCrafter |
    |------|------|---------------|
    | モデルサイズ | 30MB | 9.8GB |
    | 処理時間(CPU) | 1-2分 | 10-30分 |
    | メモリ使用量 | ~1GB | ~8GB |
    | 品質 | 高 | 非常に高 |
    | モーション制御 | ✅ | ✅ |
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

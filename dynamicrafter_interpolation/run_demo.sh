#!/bin/bash
# デモスクリプト - サンプル画像を使った中割りのデモ

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_DIR="/workspaces/dev"

echo "=========================================="
echo "DynamiCrafter Frame Interpolation Demo"
echo "=========================================="
echo ""

# DynamiCrafterディレクトリに移動
cd "$WORKSPACE_DIR/DynamiCrafter"

# サンプル画像が存在するか確認
if [ -d "prompts/512_interp" ]; then
    echo "DynamiCrafterのサンプル画像を使用します"
    
    # サンプル1: 笑顔の遷移
    if [ -f "prompts/512_interp/smile_01.png" ] && [ -f "prompts/512_interp/smile_02.png" ]; then
        echo ""
        echo "[デモ 1/3] 笑顔の遷移を生成中..."
        python ../dynamicrafter_interpolation/interpolate.py \
            --image1 prompts/512_interp/smile_01.png \
            --image2 prompts/512_interp/smile_02.png \
            --output ../dynamicrafter_interpolation/output_videos/demo_smile.mp4 \
            --prompt "a smiling girl" \
            --frames 16 \
            --steps 50 \
            --fps 5 \
            --seed 12306
        echo "✓ 完了: output_videos/demo_smile.mp4"
    fi
    
    # サンプル2: ストーンの回転
    if [ -f "prompts/512_interp/stone01_01.png" ] && [ -f "prompts/512_interp/stone01_02.png" ]; then
        echo ""
        echo "[デモ 2/3] オブジェクトの回転を生成中..."
        python ../dynamicrafter_interpolation/interpolate.py \
            --image1 prompts/512_interp/stone01_01.png \
            --image2 prompts/512_interp/stone01_02.png \
            --output ../dynamicrafter_interpolation/output_videos/demo_stone.mp4 \
            --prompt "rotating view" \
            --frames 16 \
            --steps 50 \
            --fps 5 \
            --seed 123
        echo "✓ 完了: output_videos/demo_stone.mp4"
    fi
    
    # サンプル3: 歩行の動き
    if [ -f "prompts/512_interp/walk_01.png" ] && [ -f "prompts/512_interp/walk_02.png" ]; then
        echo ""
        echo "[デモ 3/3] 歩行動作を生成中..."
        python ../dynamicrafter_interpolation/interpolate.py \
            --image1 prompts/512_interp/walk_01.png \
            --image2 prompts/512_interp/walk_02.png \
            --output ../dynamicrafter_interpolation/output_videos/demo_walk.mp4 \
            --prompt "man walking" \
            --frames 16 \
            --steps 50 \
            --fps 5 \
            --seed 345
        echo "✓ 完了: output_videos/demo_walk.mp4"
    fi
    
    echo ""
    echo "=========================================="
    echo "デモが完了しました！"
    echo "=========================================="
    echo ""
    echo "生成された動画:"
    echo "  - $SCRIPT_DIR/output_videos/demo_smile.mp4"
    echo "  - $SCRIPT_DIR/output_videos/demo_stone.mp4"
    echo "  - $SCRIPT_DIR/output_videos/demo_walk.mp4"
    echo ""
else
    echo "エラー: DynamiCrafterのサンプル画像が見つかりません"
    echo "setup.shを実行してDynamiCrafterをセットアップしてください"
    exit 1
fi

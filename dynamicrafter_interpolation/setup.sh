#!/bin/bash
# DynamiCrafter Frame Interpolation System セットアップスクリプト

set -e  # エラーが発生したら停止

echo "=========================================="
echo "DynamiCrafter Frame Interpolation System"
echo "セットアップスクリプト"
echo "=========================================="
echo ""

# 現在のディレクトリを保存
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_DIR="/workspaces/dev"

# 1. DynamiCrafterのクローン
echo "[1/4] DynamiCrafterリポジトリのクローン..."
cd "$WORKSPACE_DIR"
if [ ! -d "DynamiCrafter" ]; then
    git clone https://github.com/Doubiiu/DynamiCrafter.git
    echo "✓ DynamiCrafterをクローンしました"
else
    echo "✓ DynamiCrafterは既に存在します"
fi

# 2. DynamiCrafterの依存関係をインストール
echo ""
echo "[2/4] DynamiCrafterの依存関係をインストール..."
cd "$WORKSPACE_DIR/DynamiCrafter"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ DynamiCrafterの依存関係をインストールしました"
fi

# 3. このシステムの依存関係をインストール
echo ""
echo "[3/4] Frame Interpolation Systemの依存関係をインストール..."
cd "$SCRIPT_DIR"
pip install -r requirements.txt
echo "✓ 依存関係をインストールしました"

# 4. モデルのダウンロード
echo ""
echo "[4/4] DynamiCrafterモデルのダウンロード..."
cd "$WORKSPACE_DIR/DynamiCrafter"
mkdir -p checkpoints/dynamicrafter_512_interp_v1

if [ ! -f "checkpoints/dynamicrafter_512_interp_v1/model.ckpt" ]; then
    echo "モデルをダウンロードしています（これには時間がかかる場合があります）..."
    
    # Hugging Face CLIを使用してダウンロード
    if command -v huggingface-cli &> /dev/null; then
        huggingface-cli download Doubiiu/DynamiCrafter_512_Interp model.ckpt \
            --local-dir checkpoints/dynamicrafter_512_interp_v1/ \
            --local-dir-use-symlinks False
        echo "✓ モデルをダウンロードしました"
    else
        echo "警告: huggingface-cli が見つかりません"
        echo "手動でモデルをダウンロードしてください："
        echo "  https://huggingface.co/Doubiiu/DynamiCrafter_512_Interp/resolve/main/model.ckpt"
        echo "  保存先: checkpoints/dynamicrafter_512_interp_v1/model.ckpt"
    fi
else
    echo "✓ モデルは既に存在します"
fi

# 設定ファイルの確認
if [ ! -f "configs/inference_512_v1.0.yaml" ]; then
    echo "警告: configs/inference_512_v1.0.yaml が見つかりません"
    echo "DynamiCrafterリポジトリが正しくクローンされているか確認してください"
fi

echo ""
echo "=========================================="
echo "セットアップが完了しました！"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  cd $WORKSPACE_DIR/DynamiCrafter"
echo "  python ../dynamicrafter_interpolation/interpolate.py \\"
echo "    --image1 path/to/image1.jpg \\"
echo "    --image2 path/to/image2.jpg \\"
echo "    --output ../dynamicrafter_interpolation/output_videos/result.mp4"
echo ""
echo "サンプルを実行するには:"
echo "  cd $WORKSPACE_DIR/DynamiCrafter"
echo "  bash ../dynamicrafter_interpolation/run_demo.sh"
echo ""

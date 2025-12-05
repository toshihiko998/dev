#!/bin/bash

echo "=========================================="
echo "DynamiCrafter WebUI 起動スクリプト"
echo "=========================================="
echo ""

# DynamiCrafterディレクトリに移動（PYTHONPATHのため）
cd /workspaces/dev/DynamiCrafter

# Gradioがインストールされているか確認
if ! python3 -c "import gradio" 2>/dev/null; then
    echo "📦 Gradioをインストール中..."
    pip install -q gradio
    echo "✓ Gradioをインストールしました"
fi

echo "🌐 WebUIを起動中..."
echo ""
echo "ブラウザで以下のURLにアクセスしてください:"
echo "  → http://localhost:7860"
echo ""
echo "終了するには Ctrl+C を押してください"
echo ""

# WebUIを起動
python3 ../dynamicrafter_interpolation/webui.py

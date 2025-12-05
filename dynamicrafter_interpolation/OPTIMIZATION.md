# DynamiCrafter 軽量化ガイド

現在の問題：
- モデルサイズ: 9.8GB
- CLIP モデル: 4GB
- CPU処理: 非常に遅い（10-30分）

## 🚀 軽量化オプション

### オプション1: フレーム補間ライブラリに切り替え（推奨）
より軽量な代替手段：

#### A. FILM (Frame Interpolation for Large Motion)
- サイズ: ~100MB
- 処理速度: GPU 1-2秒/フレーム、CPU 10-30秒/フレーム
- 品質: 高品質
- 実装: TensorFlow

#### B. RIFE (Real-Time Intermediate Flow Estimation)
- サイズ: ~30MB
- 処理速度: GPU サブ秒、CPU 5-10秒/フレーム
- 品質: 非常に高品質
- 実装: PyTorch
- **最も軽量で高速**

#### C. FFmpeg minterpolate
- サイズ: 0MB（既にインストール済み）
- 処理速度: 非常に高速
- 品質: 中程度
- 実装: コマンドライン

### オプション2: DynamiCrafterの軽量化
- モデル量子化（8bit/4bit）
- バッチサイズ削減
- 解像度ダウンスケール
- それでも数GB必要

### オプション3: クラウドGPU利用
- Google Colab (無料GPU)
- Hugging Face Spaces
- Replicate API

## 💡 推奨: RIFEへの移行

RIFEは：
- ✅ 30MBと超軽量
- ✅ CPU でも比較的高速（1-2分/動画）
- ✅ 高品質な補間
- ✅ シンプルなAPI

実装しますか？

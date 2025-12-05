# DynamiCrafter + Steerable-Motion 統合中割りシステム

DynamiCrafterとSteerable-Motionを組み合わせた、次世代の画像中割りシステムです。

## 概要

このシステムは2つの最先端AIモデルを統合して、高品質で制御可能な中割りフレームを生成します：

- **DynamiCrafter**: 高品質なフレーム生成エンジン
- **Steerable-Motion**: 詳細なモーション制御機能

アニメーション、動画編集、モーフィング、シネマティック効果など、幅広い用途に対応します。

## 特徴

### 🎯 高度なモーション制御
- **カメラモーション**: パン、ズーム、回転の制御
- **複合モーション**: 複数の動きを同時に適用
- **テキストプロンプト**: 自然言語でモーションを指定

### 🎨 高品質な生成
- **DynamiCrafter**: 最先端の生成品質
- **3つのモード**: DynamiCrafter単体、Steerable、ハイブリッド
- **柔軟な設定**: フレーム数、品質、スタイルを自由に調整

### 🚀 使いやすさ
- **シンプルなCLI**: コマンドライン1行で実行
- **Pythonスクリプト**: 高度な制御が可能
- **豊富な例**: 7種類の使用例を提供

## セットアップ

### 1. DynamiCrafterのインストール

まず、DynamiCrafterの公式リポジトリをクローンします：

```bash
cd /workspaces/dev
git clone https://github.com/Doubiiu/DynamiCrafter.git
cd DynamiCrafter
```

### 2. 依存関係のインストール

DynamiCrafterの依存関係をインストールします：

```bash
# DynamiCrafterの依存関係
pip install -r requirements.txt

# このシステムの追加依存関係
cd ../dynamicrafter_interpolation
pip install -r requirements.txt
```

### 3. モデルのダウンロード

DynamiCrafter 512の中割りモデルをダウンロードします：

```bash
cd ../DynamiCrafter

# checkpointsディレクトリを作成
mkdir -p checkpoints/dynamicrafter_512_interp_v1

# Hugging Faceからモデルをダウンロード
# 方法1: huggingface-cliを使用
huggingface-cli download Doubiiu/DynamiCrafter_512_Interp model.ckpt \
  --local-dir checkpoints/dynamicrafter_512_interp_v1/

# 方法2: wgetを使用（直接ダウンロード）
# wget https://huggingface.co/Doubiiu/DynamiCrafter_512_Interp/resolve/main/model.ckpt \
#   -O checkpoints/dynamicrafter_512_interp_v1/model.ckpt
```

## 使い方

### 基本的な使用方法（シンプルモード）

```bash
# DynamiCrafterのルートディレクトリから実行
cd /workspaces/dev/DynamiCrafter

# 基本的な中割り
python ../dynamicrafter_interpolation/interpolate.py \
  --image1 path/to/first_image.jpg \
  --image2 path/to/second_image.jpg \
  --output ../dynamicrafter_interpolation/output_videos/result.mp4
```

### 高度な使用方法（モーション制御付き）

```bash
# カメラパン付き中割り
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 img1.jpg \
  --image2 img2.jpg \
  --camera-pan-x 0.5 \
  --prompt "smooth camera panning"

# ズームイン効果
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 img1.jpg \
  --image2 img2.jpg \
  --camera-zoom 0.8 \
  --prompt "dramatic zoom in"

# 回転効果
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 img1.jpg \
  --image2 img2.jpg \
  --camera-rotate 45 \
  --prompt "rotating view"

# 複合モーション（パン+ズーム+回転）
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 img1.jpg \
  --image2 img2.jpg \
  --camera-pan-x 0.3 \
  --camera-pan-y -0.2 \
  --camera-zoom 0.6 \
  --camera-rotate 15 \
  --prompt "cinematic camera movement"
```

### パラメータの説明

#### 基本パラメータ
- `--image1`: 最初の画像のパス（必須）
- `--image2`: 2番目の画像のパス（必須）
- `--output`: 出力動画のパス（デフォルト: `output_videos/interpolated.mp4`）
- `--prompt`: テキストプロンプト（デフォルト: 空文字列）
- `--frames`: 生成するフレーム数（デフォルト: 16）
- `--steps`: DDIMサンプリングのステップ数（デフォルト: 50）
- `--cfg-scale`: Classifier-free guidanceスケール（デフォルト: 7.5）
- `--fps`: 出力動画のFPS（デフォルト: 5）
- `--seed`: ランダムシード（デフォルト: 123）

#### モーション制御パラメータ（advanced_interpolate.py）
- `--method`: 中割り手法 (`dynamicrafter` | `steerable` | `hybrid`)
- `--camera-pan-x`: 水平パン（-1.0=左、1.0=右）
- `--camera-pan-y`: 垂直パン（-1.0=上、1.0=下）
- `--camera-zoom`: ズーム（-1.0=アウト、1.0=イン）
- `--camera-rotate`: 回転（度数、-180〜180）

## 使用例

### 基本例: シンプルな中割り

```bash
cd /workspaces/dev/DynamiCrafter

python ../dynamicrafter_interpolation/interpolate.py \
  --image1 ../dynamicrafter_interpolation/input_images/frame1.jpg \
  --image2 ../dynamicrafter_interpolation/input_images/frame2.jpg \
  --output ../dynamicrafter_interpolation/output_videos/basic_interp.mp4
```

### モーション制御例

#### 例1: カメラパン

```bash
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 input_images/scene1.jpg \
  --image2 input_images/scene2.jpg \
  --camera-pan-x 0.5 \
  --prompt "smooth camera panning right" \
  --output output_videos/pan_example.mp4
```

#### 例2: ズームイン

```bash
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 input_images/portrait1.jpg \
  --image2 input_images/portrait2.jpg \
  --camera-zoom 0.8 \
  --prompt "dramatic zoom in" \
  --frames 20 \
  --steps 60 \
  --output output_videos/zoom_example.mp4
```

#### 例3: 回転効果

```bash
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 input_images/object1.jpg \
  --image2 input_images/object2.jpg \
  --camera-rotate 45 \
  --prompt "rotating view, smooth transition" \
  --output output_videos/rotate_example.mp4
```

#### 例4: 複合モーション（シネマティック）

```bash
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 input_images/landscape1.jpg \
  --image2 input_images/landscape2.jpg \
  --camera-pan-x 0.3 \
  --camera-pan-y -0.2 \
  --camera-zoom 0.6 \
  --camera-rotate 15 \
  --prompt "cinematic camera movement, pan zoom and rotate" \
  --frames 24 \
  --fps 8 \
  --output output_videos/cinematic_example.mp4
```

### 高品質設定

```bash
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 input_images/start.jpg \
  --image2 input_images/end.jpg \
  --frames 32 \
  --steps 100 \
  --cfg-scale 8.5 \
  --fps 10 \
  --camera-zoom -0.5 \
  --prompt "high quality dolly zoom effect" \
  --output output_videos/high_quality.mp4
```

## プロジェクト構造

```
dynamicrafter_interpolation/
├── interpolate.py              # シンプルモード（DynamiCrafter）
├── advanced_interpolate.py     # 高度なモード（モーション制御付き）
├── examples.py                 # 基本的な使用例
├── advanced_examples.py        # 高度な使用例（7種類）
├── requirements.txt            # 依存関係
├── setup.sh                    # 自動セットアップ
├── run_demo.sh                 # デモ実行
├── README.md                   # このファイル
├── QUICKSTART.md              # クイックスタート
├── PROJECT_SUMMARY.md         # プロジェクト概要
├── input_images/              # 入力画像用ディレクトリ
└── output_videos/             # 出力動画用ディレクトリ
```

## 機能比較

| 機能 | interpolate.py | advanced_interpolate.py |
|------|---------------|------------------------|
| 基本的な中割り | ✅ | ✅ |
| テキストプロンプト | ✅ | ✅ |
| カメラパン | ❌ | ✅ |
| カメラズーム | ❌ | ✅ |
| カメラ回転 | ❌ | ✅ |
| 複合モーション | ❌ | ✅ |
| 3つのモード切替 | ❌ | ✅ |
| 推奨用途 | シンプルな中割り | 高度な制御が必要な場合 |

## トラブルシューティング

### CUDA out of memory エラー

メモリ不足の場合は、以下を試してください：

- `--frames` を減らす（例: 16 → 8）
- `--steps` を減らす（例: 50 → 30）
- より小さい解像度の画像を使用する

### モデルが見つからないエラー

DynamiCrafterのルートディレクトリから実行していることを確認してください：

```bash
cd /workspaces/dev/DynamiCrafter
python ../dynamicrafter_interpolation/interpolate.py ...
```

## 技術詳細

### 統合アーキテクチャ

このシステムは2つのAIモデルを効果的に組み合わせています：

#### 1. DynamiCrafter
- **役割**: 高品質なフレーム生成
- **技術**: Stable Diffusion ベースの拡散モデル
- **入力解像度**: 320x512 (H x W)
- **出力**: 8〜32フレームの動画

#### 2. Steerable-Motion（統合）
- **役割**: モーション制御とガイダンス
- **機能**: カメラモーション（パン、ズーム、回転）の生成
- **統合方法**: モーションベクトルとプロンプト拡張

### 3つのモード

1. **DynamiCrafterモード**: 
   - DynamiCrafterのみを使用
   - シンプルで高速
   
2. **Steerableモード**: 
   - モーション制御を最大限活用
   - 詳細な動きの制御が可能

3. **Hybridモード** (推奨):
   - 両方の長所を組み合わせ
   - 高品質 + モーション制御

### 処理フロー

```
入力画像 → 前処理 → Latent変換
    ↓
テキスト埋め込み + モーション情報
    ↓
条件付けテンソル作成（最初/最後フレーム + モーション）
    ↓
DDIMサンプリング（DynamiCrafter）
    ↓
モーションガイダンス適用（Steerable）
    ↓
Latent → ピクセル変換
    ↓
動画保存
```

## 参考リンク

### DynamiCrafter
- [公式リポジトリ](https://github.com/Doubiiu/DynamiCrafter)
- [論文](https://arxiv.org/abs/2310.12190)
- [Hugging Face モデル](https://huggingface.co/Doubiiu/DynamiCrafter_512_Interp)

### Steerable-Motion
- [公式リポジトリ](https://github.com/zhouyifan233/Steerable-Motion)
- モーション制御技術を参考に実装

### このプロジェクト
- [advanced_examples.py](advanced_examples.py) - 7種類の使用例
- [QUICKSTART.md](QUICKSTART.md) - 最速で始める方法
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 技術概要

## ライセンス

このシステムはDynamiCrafterを使用しています。DynamiCrafterのライセンスに従ってください。

## クレジット

- DynamiCrafter: Jinbo Xing, Menghan Xia, Yong Zhang, Haoxin Chen, et al.
- このシステム: フレーム補間の簡易インターフェースとして実装

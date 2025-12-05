# クイックスタートガイド

DynamiCrafter + Steerable-Motion統合システムで画像の中割りを最速で試す方法です。

## モード選択

### 🎯 シンプルモード
基本的な中割りのみ → `interpolate.py` を使用

### 🚀 高度なモード  
モーション制御付き → `advanced_interpolate.py` を使用

## 1. セットアップ（初回のみ）

```bash
cd /workspaces/dev/dynamicrafter_interpolation
bash setup.sh
```

このスクリプトは以下を自動で行います：
- DynamiCrafterリポジトリのクローン
- 必要なPythonパッケージのインストール
- モデルファイルのダウンロード

⏱️ 所要時間: 5〜10分（ネットワーク速度による）

## 2. デモの実行

セットアップ完了後、すぐにデモを実行できます：

```bash
cd /workspaces/dev/DynamiCrafter
bash ../dynamicrafter_interpolation/run_demo.sh
```

これにより、DynamiCrafterの公式サンプル画像を使用して3つの動画が生成されます。

## 3. 自分の画像で試す

### 方法A: シンプルな中割り

```bash
cd /workspaces/dev/DynamiCrafter

python ../dynamicrafter_interpolation/interpolate.py \
  --image1 /path/to/your/first_image.jpg \
  --image2 /path/to/your/second_image.jpg \
  --output ../dynamicrafter_interpolation/output_videos/my_video.mp4
```

### 方法B: モーション制御付き中割り ⭐新機能

```bash
cd /workspaces/dev/DynamiCrafter

# カメラパン
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 your_img1.jpg \
  --image2 your_img2.jpg \
  --camera-pan-x 0.5 \
  --prompt "smooth camera movement"

# ズームイン
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 your_img1.jpg \
  --image2 your_img2.jpg \
  --camera-zoom 0.8 \
  --prompt "zoom in effect"

# 回転
python ../dynamicrafter_interpolation/advanced_interpolate.py \
  --image1 your_img1.jpg \
  --image2 your_img2.jpg \
  --camera-rotate 45 \
  --prompt "rotating view"
```

## パラメータの調整

### 品質を上げたい
```bash
--frames 32 --steps 100 --fps 10
```

### 処理を速くしたい
```bash
--frames 8 --steps 30
```

### モーション効果を追加したい ⭐新機能
```bash
# 右へパン
--camera-pan-x 0.5 --prompt "camera panning right"

# ズームイン
--camera-zoom 0.8 --prompt "zoom in smoothly"

# 回転
--camera-rotate 45 --prompt "rotating view"

# 複合モーション
--camera-pan-x 0.3 --camera-zoom 0.6 --prompt "pan and zoom"

# シネマティック（複数の動きを組み合わせ）
--camera-pan-x 0.3 --camera-pan-y -0.2 --camera-zoom 0.5 --camera-rotate 15 \
--prompt "cinematic camera movement"
```

### モード選択
```bash
# DynamiCrafter単体（デフォルト）
--method dynamicrafter

# Steerable-Motion重視
--method steerable  

# ハイブリッド（推奨）
--method hybrid
```

## トラブルシューティング

### メモリ不足エラー
```bash
--frames 8  # フレーム数を減らす
```

### モデルが見つからない
```bash
# DynamiCrafterディレクトリから実行していることを確認
cd /workspaces/dev/DynamiCrafter
```

## 次のステップ

- [README.md](README.md) - 詳細なドキュメント
- [examples.py](examples.py) - Pythonでの高度な使用例
- [DynamiCrafter公式](https://github.com/Doubiiu/DynamiCrafter) - 元のリポジトリ

## よくある質問

**Q: どのくらいの時間がかかりますか？**  
A: GPU使用時、1つの動画生成に約30秒〜2分です。モーション制御を使用しても大きな違いはありません。

**Q: どんな画像が使えますか？**  
A: JPG、PNG形式の画像。最適な結果には同じシーンの2枚の画像を推奨。

**Q: 動画の長さは？**  
A: デフォルトで約3秒（16フレーム@5fps）。`--frames`と`--fps`で調整可能。最大32フレーム推奨。

**Q: モーション制御とは何ですか？** ⭐  
A: カメラの動き（パン、ズーム、回転）を数値で指定できる機能です。より自然で意図的な動きを生成できます。

**Q: どのモードを使うべきですか？**  
A: 
- シンプルな中割りのみ → `interpolate.py`
- モーション制御が必要 → `advanced_interpolate.py --method hybrid`

**Q: モーションパラメータの値はどう設定しますか？**  
A:
- パン: -1.0〜1.0（0.3〜0.5が自然）
- ズーム: -1.0〜1.0（0.5〜0.8が効果的）
- 回転: -180〜180度（15〜45度が一般的）

**Q: 商用利用できますか？**  
A: DynamiCrafterとSteerable-Motionのライセンスを確認してください。

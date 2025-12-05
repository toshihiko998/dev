# dev

## プロジェクト

### DynamiCrafter + Steerable-Motion 統合中割りシステム

2枚の静止画から高品質な中割りフレームを生成する次世代AIシステムです。

📁 **場所**: `dynamicrafter_interpolation/`

🚀 **クイックスタート**: 
```bash
cd dynamicrafter_interpolation
bash setup.sh
```

📖 **ドキュメント**: 
- [README.md](dynamicrafter_interpolation/README.md) - 完全ガイド
- [QUICKSTART.md](dynamicrafter_interpolation/QUICKSTART.md) - 最速スタート

✨ **主な機能**:
- **DynamiCrafter**: 高品質なフレーム生成
- **Steerable-Motion**: カメラモーション制御（パン、ズーム、回転）
- **3つのモード**: シンプル / Steerable / ハイブリッド
- **簡単なCLI**: コマンドライン1行で実行
- **豊富な例**: 7種類の高度な使用例を提供

🎯 **使用例**:
```bash
# シンプルな中割り
python interpolate.py --image1 img1.jpg --image2 img2.jpg

# モーション制御付き
python advanced_interpolate.py --image1 img1.jpg --image2 img2.jpg \
  --camera-pan-x 0.5 --camera-zoom 0.8 --prompt "cinematic movement"
```

---

# What is this?

The github.dev web-based editor is a lightweight editing experience that runs entirely in your browser. You can navigate files and source code repositories from GitHub, and make and commit code changes.

There are two ways to go directly to a VS Code environment in your browser and start coding:

* Press the . key on any repository or pull request.
* Swap `.com` with `.dev` in the URL. For example, this repo https://github.com/github/dev becomes http://github.dev/github/dev

Preview the gif below to get a quick demo of github.dev in action.

![github dev](https://user-images.githubusercontent.com/856858/130119109-4769f2d7-9027-4bc4-a38c-10f297499e8f.gif)

# Why?
It’s a quick way to edit and navigate code. It's especially useful if you want to edit multiple files at a time or take advantage of all the powerful code editing features of Visual Studio Code when making a quick change. For more information, see our [documentation](https://github.co/codespaces-editor-help).

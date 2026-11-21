# 🌍 地心探險號：地球結構 3D 實驗室 (`p4-earth-explorer-3d`)

專為**香港小學四年級科學科**設計的互動式 3D 網頁學習遊戲，課程內容嚴格對齊香港教育局**《科學（小一至小六）課程指引》（2025）**：
- **範疇三：地球與太空** → **主題 A：地球的特徵和資源**
- **核心重點 `4EA1`**：說出地球的結構（**地殼、地幔和地核**）及其物理特性（相對位置、厚度、組成物質、溫度與狀態）。
- **延伸探索 `4EA2`**：認識地殼由岩石組成，觀察**花崗岩、砂岩、大理岩**的外觀特徵。
- **探究模式 `PDAR`**：結合「提問和規劃（Plan）」、「實施和記錄（Do）」、「整理和分析（Analyse）」、「表達和反思（Review）」。

---

## ✨ 專案特色

1. **Blender Python (`bpy`) 全雲端無頭資產管線**
   - 內建 `blender-scripts/` 宣告式建模腳本，自動生成 3/4 剖面地球（含「教學放大比例」與「真實科學比例」Shape Keys 形態鍵）、Q 版地心鑽探艙與三大岩石標本 `.glb` 模型。
   - 透過 **GitHub Actions** 在雲端自動安裝 Blender 建置 `.glb` 並部署至 GitHub Pages，本機免安裝 Blender 亦可維護。
2. **學校 iPad / 電子白板 60 FPS 極速優化**
   - 限制 DPR 上限、低多邊形（Low-Poly < 16,000 Tris）設計、支援觸控旋轉縮放及粵語語音朗讀（Web Speech API `zh-HK`）。
   - 內建離線程序化幾何備援機制（Fallback Geometry），即使本機尚未執行 Blender 匯出，直接執行 `npm run dev` 仍可即時預覽完整遊戲。

---

## 🚀 本機開發指南

```bash
# 1. 安裝依賴套件
npm install

# 2. （選用）若本機已安裝 Blender，可一鍵生成 .glb 模型至 public/models/
npm run build:models

# 3. 啟動開發伺服器
npm run dev

# 4. 編譯生產版本
npm run build
```

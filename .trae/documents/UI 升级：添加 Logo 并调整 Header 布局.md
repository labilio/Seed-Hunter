我将修改 `web/src/App.jsx` 文件中的 `header` 部分，以实现 UI 升级。

### 修改计划：

1.  **新增 Logo 和标题组件**：
    *   在 `LevelSelect` 组件之前，添加一个新的 Logo 区域。
    *   **Logo**：使用 🔑 (Key Emoji) 作为图标，字号调大。
    *   **标题**：
        *   英文名 "Seed Hunter"：使用大号、粗体字体，突出显示。
        *   中文名 "助记词猎手"：使用较小、灰色的字体，作为副标题显示在英文名旁边或下方。

2.  **调整 Header 布局结构**：
    *   目前的 Header 左侧容器 `div.mx-auto.w-full.max-w-2xl` 包含 `LevelSelect` 和 `ProgressBar`。
    *   我将修改这个容器的内部结构：
        *   创建一个新的 Flex 容器来包裹 Logo/标题区域 和 原有的 Level选择器/进度条区域。
        *   确保 Logo 区域位于最左侧。
        *   `LevelSelect` 和 `ProgressBar` 整体向右移动，紧跟在 Logo 区域之后。

### 预期效果：
Header 左侧将变成： `[🔑 Seed Hunter (助记词猎手)] [Level选择器] [进度条]` 的排列顺序。

具体代码结构调整如下：
```jsx
<div className="mx-auto w-full max-w-2xl">
  <div className="flex items-center gap-6"> {/* 增加 gap 以区分 Logo 区和功能区 */}
    
    {/* 新增 Logo 区域 */}
    <div className="flex items-center gap-3 select-none">
      <span className="text-3xl">🔑</span>
      <div className="flex flex-col">
        <span className="text-lg font-black tracking-tight text-content leading-none">Seed Hunter</span>
        <span className="text-[10px] font-medium text-content-dim/80 leading-none mt-0.5">助记词猎手</span>
      </div>
    </div>

    {/* 原有的功能区域 (右移) */}
    <div className="flex items-center gap-4">
      <LevelSelect ... />
      <ProgressBar ... />
    </div>
    
  </div>
</div>
```
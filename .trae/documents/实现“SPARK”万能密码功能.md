我将执行以下修改以支持“SPARK”万能密码功能：

### 1. 后端修改 (`backend/judge.py`)
*   修改 `verify_password` 方法：
    *   增加一个特殊的判断逻辑：如果 `submitted_password` 为 "SPARK"（忽略大小写），则直接返回 `True`，视为验证通过。

### 2. 前端修改 (`web/src/App.jsx`)
*   修改 `handleSubmit` 函数中的逻辑：
    *   在验证通过后的逻辑块中（`if (ok)`）：
        *   获取用户输入的原始值 (`raw`)。
        *   判断：如果 `raw.toUpperCase() === 'SPARK'`，则在更新 `collectedWords`（已收集助记词）时，将其值设为 "SPARK"。
        *   同时，在渲染“已破解助记词”列表时（`collectedWords` 的遍历部分），增加样式判断：
            *   如果助记词内容是 "SPARK"，则**不应用**亮绿色高亮样式（`text-action`），而是应用灰色样式（`text-gray-400` 或保持默认暗淡色），以区别于正常破解。

### 计划步骤
1.  **修改后端**：更新 `backend/judge.py` 中的 `verify_password` 方法。
2.  **修改前端**：更新 `web/src/App.jsx` 中的 `handleSubmit` 和渲染逻辑。
3.  **验证**：重启服务并测试输入 "SPARK" 是否能通关且 UI 显示符合预期。
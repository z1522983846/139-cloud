# 139 云手机自动点击

自动点击 139 云手机的小白点，并执行退出云手机和返回主屏幕操作。

## 功能

- 每小时自动执行一次
- 点击左侧小白点（辅助触控按钮）
- 点击弹出菜单中的"退出云手机"
- 点击蓝色区域的"进入云手机"按钮

## 配置步骤

### 1. Fork 本仓库

### 2. 配置 Cookie Secret

1. 进入仓库 Settings → Secrets and variables → Actions
2. 点击 New repository secret
3. 添加以下 Secrets：

| Name | Value |
|------|-------|
| `COOKIE_SMID` | 你的 smidV2 Cookie 值 |
| `COOKIE_THUMBCACHE` | 你的 .thumbcache_xxx Cookie 值 |

### 3. 获取 Cookie 的方法

1. 在浏览器登录 139 云盘
2. 进入云手机实例页面
3. 按 F12 打开开发者工具
4. 在 Console 输入：
   ```javascript
   document.cookie
   ```
5. 复制输出结果，提取 `smidV2` 和 `.thumbcache_xxx` 的值

示例：
```
smidV2=20260521200950c6a360f70ba7286e70dbf7e14ae92dd000cbe4e8a12902940
.thumbcache_5b7c44fefb14167545f4272c83419943=m+5KhTyMTCbdtBJJ9ayDO7faB1vNOWGRb42TvPJ2gA5FfpKV6t014YU0t9Pd9+Kf6B+4m33g1cl3j3IPX4HyyQ==
```

### 4. 启用 GitHub Actions

1. 进入仓库 Actions 标签
2. 如果是首次使用，点击"Enable GitHub Actions"
3. 工作流会自动运行（每小时一次）

### 5. 查看运行日志

- Actions → 点击运行的工作流 → 查看日志
- 成功时会显示 "任务执行完成"
- 失败时会显示错误信息

## 注意事项

1. **Cookie 有效期**：约 1-2 周，失效后需要重新获取并更新 Secrets
2. **运行时间**：GitHub Actions 免费版每月 2000 分钟
3. **失败通知**：可在 GitHub Settings 中配置邮件通知

## 修改执行频率

如需修改执行间隔，编辑 `.github/workflows/auto-click.yml`：

```yaml
schedule:
  # 每小时的第 0 分钟执行
  - cron: '0 * * * *'
```

Cron 表达式说明：
- `0 * * * *` = 每小时
- `0 */2 * * *` = 每 2 小时
- `0 0 * * *` = 每天
- `0 0,6,12,18 * * *` = 每天 4 次（0 点、6 点、12 点、18 点）

# 长期维护手册

这个软件的长期稳定性重点不是“永远不改代码”，而是让数据、迁移路径、测试和构建方式始终清楚。

## 维护原则

- 数据优先：复习记录保存在 SQLite，升级前自动备份。
- 配置集中：默认只有一个主数据目录，设置、数据库、备份、插件都在里面。
- 路径迁移稳健：主数据目录迁移到空目录时直接使用；迁移到已有普通目录时自动创建 `LiFileReviewer2` 子目录，保护用户原有文件。
- 长路径兼容：内部文件读写、数据库、导出、备份、笔记使用 Windows 长路径适配，减少深层目录和长文件名导致的失败。
- 笔记开放：笔记保存为真实 Markdown 文件，默认在 `notes\`，可迁移到用户自定义路径，支持批量导出和删除。
- 导出明确：CSV、JSON、迁移包、手动备份、分享包、笔记导出、导入前备份都会先让用户选择保存位置；`exports\` 只作为默认起点。
- 可迁移：设置页支持 JSON 导出和完整迁移包导出/导入；导入后会修正笔记路径到当前电脑。
- 可验证：每次改动后运行测试、体检、源码服务冒烟测试、打包版冒烟测试。
- 可扩展：设置页有插件管理。成就系统和社交资料已经作为内置插件注册，可启用/关闭；关闭后对应 UI 模块会从布局中移除，启用后动态挂载；`plugins\` 目录继续支持读取外部清单，默认不执行插件代码，避免破坏稳定性。

## 常用命令

```powershell
python -m py_compile app.py tests\test_core.py
python -m unittest discover -s tests -v
python app.py --health-check
python app.py --backup
python app.py --export-portable
python app.py --export-profile
python app.py --no-window --port 8897
```

打包：

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "智能文件复习系统2.12.0_WebUI" --add-data "web;web" --hidden-import webview.platforms.winforms app.py
```

## 升级数据库规则

1. 修改 `SCHEMA_VERSION`。
2. 在 `init_db()` 中添加向前兼容迁移。
3. 保留自动备份逻辑。
4. 新增或变更数据结构后补测试。
5. 运行 `python app.py --health-check`。

## 迁移出口

- `exports\review_portable_*.json`：开放 JSON 数据，便于未来迁移到其他程序。
- `exports\review_items_*.csv`：表格数据，便于用户自行分析。
- `exports\LiFileReviewer2_profile_*.zip`：完整迁移包，包含配置、数据库备份、备份目录、插件目录、笔记目录。
- 笔记导出：复制选中的 Markdown 笔记到用户选择的导出目录。

2.9.0 起，以上只是默认文件名示例。桌面界面会在每次导出或备份前弹出保存位置，用户可以放到任意可写路径。

## 成就插件

成就系统本身由内置插件 `achievement_core` 控制，可在设置页插件管理里关闭。关闭后总览页成就面板会从布局中移除，而不是显示“已关闭”占位。插件目录下可创建子目录，例如 `plugins\achievement_pack\plugin.json`：

2.12.0 起，设置页插件管理可以导入插件 zip 包、导入插件文件夹、打开插件目录。导入时会校验 `plugin.json`，复制到主数据目录的 `plugins\` 下，并由配置文件统一控制启用/关闭。

```json
{
  "id": "achievement_pack",
  "name": "Achievement Pack",
  "version": "1.0.0",
  "enabled": true,
  "achievements": [
    {
      "id": "review_5000",
      "title": "复习 5000 次",
      "description": "累计完成 5000 次复习",
      "metric": "reviews",
      "target": 5000,
      "points": 1200,
      "tier": "legend"
    }
  ]
}
```

可用 metric 包括 `items`、`single_files`、`custom_decks`、`tagged_items`、`reviews`、`notes`、`done_items`、`streak`，以及活动事件 `event:export_csv`、`event:export_json`、`event:export_profile`、`event:backup_database`、`event:export_share`、`event:export_notes`、`event:create_deck`、`event:create_note`、`event:add_item`、`event:study_seconds`。

## 社交插件

内置插件 `social_profile` 保存本地社交资料：显示名称、账号 ID、简介、主页、联系信息、统计分享偏好、成就分享偏好、未来好友发现开关。关闭后设置页社交资料表单会从布局中移除，启用后再显示并恢复编辑入口。

当前版本只保存本地资料并生成 `LiFileReviewerSocialCard` JSON，不连接外部网络、不上传数据。后续好友、动态、协作学习、公开成就墙等功能可以基于这个插件继续扩展。

即使很多年后 Python、Windows 或浏览器生态变化，只要 JSON 和 SQLite 仍能读取，数据就能继续迁移。

## 建议节奏

- 每月：体检一次，备份数据库一次。
- 每次大量扫描前：先备份数据库。
- 每次升级前：导出迁移包，并保留旧 exe。
- 每次发给别人前：运行测试和打包版健康检查。

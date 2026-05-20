# 长期维护手册

这个软件的长期稳定性重点不是“永远不改代码”，而是让数据、迁移路径、测试和构建方式始终清楚。

## 维护原则

- 数据优先：复习记录保存在 SQLite，升级前自动备份。
- 配置集中：默认只有一个主数据目录，设置、数据库、备份、插件都在里面。
- 笔记开放：笔记保存为真实 Markdown 文件，默认在 `notes\`，可迁移到用户自定义路径，支持批量导出和删除。
- 导出明确：CSV、JSON、迁移包、手动备份、笔记导出默认进入 `exports\`，也可由用户指定路径。
- 可迁移：设置页支持 JSON 导出和完整迁移包导出/导入；导入后会修正笔记路径到当前电脑。
- 可验证：每次改动后运行测试、体检、源码服务冒烟测试、打包版冒烟测试。
- 可扩展：`plugins\` 目录和插件清单读取已经预留，默认不执行插件代码，避免破坏稳定性。

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
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "智能文件复习系统2.0_WebUI" --add-data "web;web" --hidden-import webview.platforms.winforms app.py
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

即使很多年后 Python、Windows 或浏览器生态变化，只要 JSON 和 SQLite 仍能读取，数据就能继续迁移。

## 建议节奏

- 每月：体检一次，备份数据库一次。
- 每次大量扫描前：先备份数据库。
- 每次升级前：导出迁移包，并保留旧 exe。
- 每次发给别人前：运行测试和打包版健康检查。

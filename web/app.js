const state = {
  view: "dashboard",
  overview: null,
  config: null,
  lang: "zh-CN",
  onboardingStep: 0,
  items: [],
  libraries: [],
  notes: [],
  activeNoteId: null,
  selectedNoteIds: new Set(),
  activeLibraryId: null,
  treeRel: "",
  commonPaths: [],
  plugins: [],
  filters: {
    search: "",
    status: "active",
    due: "all",
    sort: "due_at",
    direction: "asc",
  },
  selectedIds: new Set(),
  review: {
    item: null,
    sessionId: null,
    startedAt: null,
    timerId: null,
  },
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

let I18N = {
  "zh-CN": {
    "brand.title": "文件复习",
    "nav.dashboard": "总览",
    "nav.library": "文件库",
    "nav.review": "复习",
    "nav.notes": "笔记",
    "nav.settings": "设置",
    "actions.chooseLibrary": "选择本地文件库",
    "actions.addLibrary": "添加文件库",
    "actions.scanAll": "扫描全部文件库",
    "actions.rescan": "重新扫描",
    "actions.startDue": "开始下一项复习",
    "actions.startReview": "开始复习",
    "actions.enter": "进入",
    "actions.exportCsv": "导出 CSV",
    "actions.openDefault": "用系统默认程序打开",
    "actions.openWith": "选择其他应用打开",
    "actions.openWithShort": "其他应用",
    "actions.openFile": "打开文件",
    "actions.openFolder": "打开所在文件夹",
    "actions.folder": "所在文件夹",
    "actions.note": "笔记",
    "actions.createLinkedNote": "为当前资料新建笔记",
    "actions.newNote": "新建笔记",
    "actions.newLocalNote": "本地方式新建",
    "actions.openNotesFolder": "打开笔记目录",
    "actions.saveNote": "保存笔记",
    "actions.next": "下一项",
    "actions.save": "保存",
    "actions.health": "体检",
    "actions.exportJson": "导出 JSON",
    "actions.exportProfile": "导出迁移包",
    "actions.backupDb": "备份数据库",
    "actions.scanPath": "扫描路径",
    "actions.chooseFolder": "选择文件夹",
    "actions.moveProfile": "迁移到此目录",
    "actions.importProfile": "导入迁移包",
    "actions.choosePackage": "选择迁移包",
    "actions.openProfileFolder": "打开数据目录",
    "actions.refresh": "刷新",
    "actions.close": "关闭",
    "actions.previous": "上一步",
    "actions.nextStep": "下一步",
    "actions.done": "完成",
    "actions.chooseLibraryNow": "现在选择文件库",
    "search.placeholder": "搜索文件、路径、标签",
    "metrics.dueToday": "今日到期",
    "metrics.waiting": "等待复习",
    "metrics.total": "全部资料",
    "metrics.localIndex": "本地索引",
    "metrics.reviewedToday": "今日已复习",
    "metrics.streak": "连续天数",
    "metrics.studyTrace": "学习轨迹",
    "dashboard.title": "总览",
    "dashboard.subtitle": "今日复习队列与文件库状态",
    "dashboard.queue": "复习队列",
    "dashboard.futureDue": "未来到期",
    "library.title": "文件库",
    "library.subtitle": "像 Obsidian 一样浏览本地资料，并批量加入复习系统",
    "library.localLibraries": "本地文件库",
    "library.manualPath": "手动添加文件夹路径",
    "library.manualPathPlaceholder": "例如 C:\\Users\\你的名字\\Documents\\资料库",
    "review.title": "复习",
    "review.subtitle": "按记忆曲线完成阅读、评价和下次提醒",
    "review.waiting": "等待开始",
    "review.chooseOne": "请选择一项资料开始复习",
    "review.previewTitle": "复习区",
    "review.previewHint": "打开资料后，这里会显示可预览文件或文件信息。",
    "review.ratingTitle": "完成评价",
    "review.history": "复习历史",
    "notes.title": "笔记",
    "notes.subtitle": "记录复习笔记，保存为真实 Markdown 文件",
    "notes.titlePlaceholder": "笔记标题",
    "notes.editorPlaceholder": "在这里记录复习笔记...",
    "notes.empty": "还没有笔记。可以新建一篇，或在复习时为当前资料建立关联笔记。",
    "settings.title": "设置",
    "settings.subtitle": "个性化界面、调度算法与本地配置路径",
    "settings.personalization": "个性化",
    "settings.algorithm": "算法",
    "settings.fixed": "固定间隔",
    "settings.retention": "目标记忆率",
    "settings.maxReviews": "每日复习上限",
    "settings.reminderTime": "提醒时间",
    "settings.reminderEnabled": "提醒开关",
    "settings.autoOpen": "复习开始时外部打开文件",
    "settings.notesDir": "笔记存储目录",
    "settings.localNoteOpen": "本地方式新建后打开所在文件夹",
    "settings.theme": "主题",
    "settings.accent": "强调色",
    "settings.language": "语言",
    "settings.customCss": "自定义 CSS",
    "settings.paths": "配置位置",
    "settings.profileDir": "主数据目录",
    "settings.importProfile": "导入迁移包路径",
    "theme.light": "明亮",
    "theme.dark": "深色",
    "theme.paper": "纸面",
    "paths.config": "配置文件",
    "paths.database": "数据库",
    "paths.appDir": "程序数据目录",
    "paths.log": "日志",
    "paths.plugins": "插件目录",
    "paths.notes": "笔记目录",
    "paths.pointer": "位置指针",
    "help.title": "帮助说明",
    "help.body": "复习开始默认只在软件内预览，不会自动打开本地默认程序。无法预览的格式可以点击“默认打开”或“其他应用”。笔记是真实 Markdown 文件，可在软件里编辑，也可用资源管理器和本地编辑器继续处理。",
    "plugins.title": "插件开发预留",
    "plugins.empty": "暂无插件。以后把插件文件夹放在这里即可。",
    "health.title": "长期稳定性体检",
    "health.hint": "点击体检，检查数据库、配置、资源文件和原始文件可见性。",
    "filters.all": "全部",
    "filters.due": "到期",
    "filters.new": "新资料",
    "filters.future": "未到期",
    "filters.status": "状态筛选",
    "status.active": "活动",
    "status.suspended": "暂停",
    "status.done": "完成",
    "status.all": "全部状态",
    "batch.tag": "批量标签",
    "batch.tagShort": "标签",
    "batch.suspend": "暂停或恢复",
    "batch.suspendShort": "暂停",
    "batch.activate": "恢复为活动",
    "batch.activateShort": "恢复",
    "batch.dueToday": "设为今天复习",
    "batch.todayShort": "今天",
    "batch.done": "标记完成",
    "batch.doneShort": "完成",
    "batch.delete": "删除索引记录",
    "batch.deleteShort": "删除",
    "table.file": "文件",
    "table.due": "到期",
    "table.retention": "记忆率",
    "table.count": "次数",
    "table.time": "时长",
    "table.actions": "操作",
    "ratings.again": "忘记",
    "ratings.againHint": "很快再看",
    "ratings.hard": "困难",
    "ratings.hardHint": "缩短间隔",
    "ratings.good": "良好",
    "ratings.goodHint": "正常推进",
    "ratings.easy": "简单",
    "ratings.easyHint": "拉长间隔",
    "onboarding.step1Title": "欢迎使用智能文件复习系统",
    "onboarding.step1Body": "它不会移动你的资料，只会索引本地文件，并按记忆曲线提醒你复习。",
    "onboarding.step2Title": "选择一个本地文件库",
    "onboarding.step2Body": "从你的 PDF、笔记、图片、视频文件夹开始。扫描后就能浏览、搜索和批量管理。",
    "onboarding.step3Title": "每天从“开始复习”进入",
    "onboarding.step3Body": "阅读资料后选择忘记、困难、良好或简单，系统会自动安排下一次复习。",
    "empty.noDueTitle": "今天没有到期资料",
    "empty.noDueBody": "可以浏览文件库添加新资料，或安心收工。",
    "empty.noFuture": "暂无未来到期数据。",
    "empty.noLibraryTitle": "还没有文件库",
    "empty.noLibraryBody": "点击添加文件库，选择你已有的资料文件夹。",
    "empty.noTree": "这个文件夹里没有可显示内容。",
    "empty.noItemsTitle": "没有匹配文件",
    "empty.noItemsBody": "调整筛选条件，或扫描一个本地文件库。",
    "empty.fileMissing": "文件不存在",
    "empty.noHistory": "暂无历史记录。",
    "labels.noTags": "无标签",
    "labels.fileMissing": "文件缺失",
    "labels.folder": "文件夹",
    "labels.unscanned": "未扫描",
    "labels.files": "个文件",
    "labels.reviewButton": "复习",
    "labels.reviewRound": "第 {count} 次",
    "labels.intervalDays": "间隔 {days} 天",
    "labels.report": "报告：{path}",
    "time.unscheduled": "未安排",
    "time.today": "今天 {time}",
    "time.tomorrow": "明天 {time}",
    "time.yesterday": "昨天 {time}",
    "toast.openingFolderPicker": "正在打开文件夹选择窗口...",
    "toast.cancelled": "已取消选择；你也可以直接粘贴文件夹路径后扫描。",
    "toast.pathRequired": "请先输入一个有效路径",
    "toast.profileMoved": "主数据目录已迁移：{path}",
    "toast.profileImported": "迁移包已导入，导入前备份：{path}",
    "toast.profileExported": "迁移包已导出：{path}",
    "toast.packageSelected": "已选择迁移包",
    "toast.noteCreated": "笔记已创建",
    "toast.noteSaved": "笔记已保存",
    "toast.noNoteSelected": "请先选择或新建一篇笔记",
    "toast.scanDone": "扫描完成：新增 {added}，更新 {updated}",
    "toast.scanAll": "正在扫描全部文件库...",
    "toast.scanAllDone": "扫描完成，处理 {count} 条记录",
    "toast.noDue": "当前没有到期资料",
    "toast.startFirst": "请先开始一项复习",
    "toast.reviewSaved": "已记录，下一次：{date}",
    "toast.selectFirst": "请先勾选文件",
    "toast.tagUpdated": "已更新 {count} 个文件的标签",
    "toast.suspended": "已暂停 {count} 个文件",
    "toast.statusChanged": "已{label} {count} 个文件",
    "toast.dueToday": "已设为今天复习：{count} 个文件",
    "toast.deleted": "已删除 {count} 条索引记录",
    "toast.settingsSaved": "设置已保存",
    "toast.backupDone": "数据库备份完成：{path}",
    "toast.healthOk": "体检通过",
    "toast.healthBad": "体检发现需要处理的问题",
    "toast.exported": "已导出：{path}",
    "toast.exportedJson": "已导出可移植 JSON：{path}",
    "prompt.tags": "输入标签，多个标签用英文逗号分隔：",
    "confirm.delete": "确定删除 {count} 条索引记录？不会删除原始文件。",
    "health.good": "状态良好",
    "health.needsAttention": "需要关注",
  },
  "en-US": {
    "brand.title": "File Review",
    "nav.dashboard": "Dashboard",
    "nav.library": "Library",
    "nav.review": "Review",
    "nav.notes": "Notes",
    "nav.settings": "Settings",
    "actions.chooseLibrary": "Choose a local library",
    "actions.addLibrary": "Add Library",
    "actions.scanAll": "Scan all libraries",
    "actions.rescan": "Rescan",
    "actions.startDue": "Start next due item",
    "actions.startReview": "Start Review",
    "actions.enter": "Open",
    "actions.exportCsv": "Export CSV",
    "actions.openDefault": "Open with the default app",
    "actions.openWith": "Choose another app",
    "actions.openWithShort": "Other App",
    "actions.openFile": "Open File",
    "actions.openFolder": "Open containing folder",
    "actions.folder": "Folder",
    "actions.note": "Note",
    "actions.createLinkedNote": "Create a linked note",
    "actions.newNote": "New Note",
    "actions.newLocalNote": "Create as Local File",
    "actions.openNotesFolder": "Open Notes Folder",
    "actions.saveNote": "Save Note",
    "actions.next": "Next",
    "actions.save": "Save",
    "actions.health": "Check",
    "actions.exportJson": "Export JSON",
    "actions.exportProfile": "Export Profile",
    "actions.backupDb": "Back Up DB",
    "actions.scanPath": "Scan Path",
    "actions.chooseFolder": "Choose Folder",
    "actions.moveProfile": "Move Here",
    "actions.importProfile": "Import Profile",
    "actions.choosePackage": "Choose Package",
    "actions.openProfileFolder": "Open Data Folder",
    "actions.refresh": "Refresh",
    "actions.close": "Close",
    "actions.previous": "Back",
    "actions.nextStep": "Next",
    "actions.done": "Done",
    "actions.chooseLibraryNow": "Choose Library Now",
    "search.placeholder": "Search files, paths, tags",
    "metrics.dueToday": "Due Today",
    "metrics.waiting": "Waiting",
    "metrics.total": "All Items",
    "metrics.localIndex": "Local index",
    "metrics.reviewedToday": "Reviewed Today",
    "metrics.streak": "Streak",
    "metrics.studyTrace": "Study trace",
    "dashboard.title": "Dashboard",
    "dashboard.subtitle": "Today's review queue and library status",
    "dashboard.queue": "Review Queue",
    "dashboard.futureDue": "Future Due",
    "library.title": "Library",
    "library.subtitle": "Browse local files like Obsidian and add them to review in batches",
    "library.localLibraries": "Local Libraries",
    "library.manualPath": "Manual folder path",
    "library.manualPathPlaceholder": "Example: C:\\Users\\Name\\Documents\\Library",
    "review.title": "Review",
    "review.subtitle": "Read, rate, and schedule the next review",
    "review.waiting": "Ready",
    "review.chooseOne": "Choose an item to begin",
    "review.previewTitle": "Review Area",
    "review.previewHint": "Previewable files and file details appear here after you start.",
    "review.ratingTitle": "Rate This Review",
    "review.history": "Review History",
    "notes.title": "Notes",
    "notes.subtitle": "Write review notes as real Markdown files",
    "notes.titlePlaceholder": "Note title",
    "notes.editorPlaceholder": "Write review notes here...",
    "notes.empty": "No notes yet. Create one here, or create a linked note while reviewing.",
    "settings.title": "Settings",
    "settings.subtitle": "Personalization, scheduling, and local data paths",
    "settings.personalization": "Personalization",
    "settings.algorithm": "Algorithm",
    "settings.fixed": "Fixed interval",
    "settings.retention": "Target retention",
    "settings.maxReviews": "Daily review limit",
    "settings.reminderTime": "Reminder time",
    "settings.reminderEnabled": "Reminder",
    "settings.autoOpen": "Open externally when review starts",
    "settings.notesDir": "Notes folder",
    "settings.localNoteOpen": "Open containing folder after local note creation",
    "settings.theme": "Theme",
    "settings.accent": "Accent",
    "settings.language": "Language",
    "settings.customCss": "Custom CSS",
    "settings.paths": "Data Paths",
    "settings.profileDir": "Main data folder",
    "settings.importProfile": "Profile package path",
    "theme.light": "Light",
    "theme.dark": "Dark",
    "theme.paper": "Paper",
    "paths.config": "Config file",
    "paths.database": "Database",
    "paths.appDir": "App data folder",
    "paths.log": "Log",
    "paths.plugins": "Plugins folder",
    "paths.notes": "Notes folder",
    "paths.pointer": "Location pointer",
    "help.title": "Help",
    "help.body": "Reviews now stay inside the app by default and do not launch the system default app automatically. If a file cannot be previewed, use Default Open or Other App. Notes are real Markdown files, editable inside the app or with any local editor.",
    "plugins.title": "Plugin Development",
    "plugins.empty": "No plugins yet. Future plugin folders can live here.",
    "health.title": "Long-term Health Check",
    "health.hint": "Check the database, config, app resources, and original file visibility.",
    "filters.all": "All",
    "filters.due": "Due",
    "filters.new": "New",
    "filters.future": "Future",
    "filters.status": "Status filter",
    "status.active": "Active",
    "status.suspended": "Suspended",
    "status.done": "Done",
    "status.all": "All statuses",
    "batch.tag": "Batch tags",
    "batch.tagShort": "Tags",
    "batch.suspend": "Suspend selected",
    "batch.suspendShort": "Suspend",
    "batch.activate": "Reactivate selected",
    "batch.activateShort": "Reactivate",
    "batch.dueToday": "Make due today",
    "batch.todayShort": "Today",
    "batch.done": "Mark done",
    "batch.doneShort": "Done",
    "batch.delete": "Delete index records",
    "batch.deleteShort": "Delete",
    "table.file": "File",
    "table.due": "Due",
    "table.retention": "Retention",
    "table.count": "Reviews",
    "table.time": "Time",
    "table.actions": "Actions",
    "ratings.again": "Again",
    "ratings.againHint": "Review soon",
    "ratings.hard": "Hard",
    "ratings.hardHint": "Shorter interval",
    "ratings.good": "Good",
    "ratings.goodHint": "Normal progress",
    "ratings.easy": "Easy",
    "ratings.easyHint": "Longer interval",
    "onboarding.step1Title": "Welcome to File Review",
    "onboarding.step1Body": "It never moves your files. It indexes local files and reminds you to review them with a memory schedule.",
    "onboarding.step2Title": "Choose a local library",
    "onboarding.step2Body": "Start with a folder of PDFs, notes, images, or videos. After scanning, you can browse, search, and batch manage everything.",
    "onboarding.step3Title": "Use Start Review each day",
    "onboarding.step3Body": "After reading, rate the item as Again, Hard, Good, or Easy. The app schedules the next review automatically.",
    "empty.noDueTitle": "Nothing due today",
    "empty.noDueBody": "Add items from your library, or enjoy a clear queue.",
    "empty.noFuture": "No future due data yet.",
    "empty.noLibraryTitle": "No library yet",
    "empty.noLibraryBody": "Click Add Library and choose a folder that already contains your learning files.",
    "empty.noTree": "No visible content in this folder.",
    "empty.noItemsTitle": "No matching files",
    "empty.noItemsBody": "Adjust filters or scan a local library.",
    "empty.fileMissing": "File not found",
    "empty.noHistory": "No history yet.",
    "labels.noTags": "No tags",
    "labels.fileMissing": "Missing file",
    "labels.folder": "Folder",
    "labels.unscanned": "Not scanned",
    "labels.files": "files",
    "labels.reviewButton": "Review",
    "labels.reviewRound": "Review #{count}",
    "labels.intervalDays": "{days} days interval",
    "labels.report": "Report: {path}",
    "time.unscheduled": "Unscheduled",
    "time.today": "Today {time}",
    "time.tomorrow": "Tomorrow {time}",
    "time.yesterday": "Yesterday {time}",
    "toast.openingFolderPicker": "Opening folder picker...",
    "toast.cancelled": "Cancelled. You can also paste a folder path and scan it.",
    "toast.pathRequired": "Enter a valid path first",
    "toast.profileMoved": "Main data folder moved: {path}",
    "toast.profileImported": "Profile imported. Backup before import: {path}",
    "toast.profileExported": "Profile package exported: {path}",
    "toast.packageSelected": "Profile package selected",
    "toast.noteCreated": "Note created",
    "toast.noteSaved": "Note saved",
    "toast.noNoteSelected": "Select or create a note first",
    "toast.scanDone": "Scan complete: {added} added, {updated} updated",
    "toast.scanAll": "Scanning all libraries...",
    "toast.scanAllDone": "Scan complete, processed {count} records",
    "toast.noDue": "No due items right now",
    "toast.startFirst": "Start a review first",
    "toast.reviewSaved": "Saved. Next review: {date}",
    "toast.selectFirst": "Select files first",
    "toast.tagUpdated": "Updated tags for {count} files",
    "toast.suspended": "Suspended {count} files",
    "toast.statusChanged": "{label} {count} files",
    "toast.dueToday": "Made {count} files due today",
    "toast.deleted": "Deleted {count} index records",
    "toast.settingsSaved": "Settings saved",
    "toast.backupDone": "Database backup complete: {path}",
    "toast.healthOk": "Health check passed",
    "toast.healthBad": "Health check found issues",
    "toast.exported": "Exported: {path}",
    "toast.exportedJson": "Portable JSON exported: {path}",
    "prompt.tags": "Enter tags, separated by commas:",
    "confirm.delete": "Delete {count} index records? Original files will not be deleted.",
    "health.good": "Healthy",
    "health.needsAttention": "Needs attention",
  },
};

I18N["zh-CN"] = {
  "brand.title": "文件复习",
  "nav.dashboard": "总览",
  "nav.library": "文件库",
  "nav.review": "复习",
  "nav.notes": "笔记",
  "nav.settings": "设置",
  "nav.help": "帮助",
  "actions.chooseLibrary": "选择本地文件库",
  "actions.addLibrary": "添加文件库",
  "actions.scanAll": "扫描全部文件库",
  "actions.rescan": "重新扫描",
  "actions.startDue": "开始下一项复习",
  "actions.startReview": "开始复习",
  "actions.enter": "进入",
  "actions.exportCsv": "导出 CSV",
  "actions.openDefault": "用系统默认程序打开",
  "actions.openWith": "选择其他应用打开",
  "actions.openWithShort": "其他应用",
  "actions.openFile": "打开文件",
  "actions.openFolder": "打开所在文件夹",
  "actions.folder": "所在文件夹",
  "actions.note": "笔记",
  "actions.createLinkedNote": "为当前资料新建笔记",
  "actions.newNote": "新建笔记",
  "actions.newLocalNote": "本地方式新建",
  "actions.openNotesFolder": "打开笔记目录",
  "actions.saveNote": "保存笔记",
  "actions.next": "下一项",
  "actions.save": "保存",
  "actions.health": "体检",
  "actions.exportJson": "导出 JSON",
  "actions.exportProfile": "导出迁移包",
  "actions.backupDb": "备份数据库",
  "actions.scanPath": "扫描路径",
  "actions.chooseFolder": "选择文件夹",
  "actions.chooseExportDir": "选择导出目录",
  "actions.openExportFolder": "打开导出目录",
  "actions.moveProfile": "迁移到此目录",
  "actions.importProfile": "导入迁移包",
  "actions.choosePackage": "选择迁移包",
  "actions.openProfileFolder": "打开数据目录",
  "actions.refresh": "刷新",
  "actions.close": "关闭",
  "actions.previous": "上一步",
  "actions.nextStep": "下一步",
  "actions.done": "完成",
  "actions.chooseLibraryNow": "现在选择文件库",
  "search.placeholder": "搜索文件、路径、标签",
  "metrics.dueToday": "今日到期",
  "metrics.waiting": "等待复习",
  "metrics.total": "全部资料",
  "metrics.localIndex": "本地索引",
  "metrics.reviewedToday": "今日已复习",
  "metrics.streak": "连续天数",
  "metrics.studyTrace": "学习轨迹",
  "dashboard.title": "总览",
  "dashboard.subtitle": "今日复习队列与文件库状态",
  "dashboard.queue": "复习队列",
  "dashboard.futureDue": "未来到期",
  "library.title": "文件库",
  "library.subtitle": "像 Obsidian 一样浏览本地资料，并批量加入复习系统",
  "library.localLibraries": "本地文件库",
  "library.manualPath": "手动添加文件夹路径",
  "library.manualPathPlaceholder": "例如 C:\\Users\\你的名字\\Documents\\资料库",
  "review.title": "复习",
  "review.subtitle": "按记忆曲线完成阅读、评价和下次提醒",
  "review.waiting": "等待开始",
  "review.chooseOne": "请选择一项资料开始复习",
  "review.previewTitle": "复习区",
  "review.previewHint": "打开资料后，这里会显示可预览文件或文件信息。",
  "review.ratingTitle": "完成评价",
  "review.history": "复习历史",
  "notes.title": "笔记",
  "notes.subtitle": "记录复习笔记，保存为真实 Markdown 文件",
  "notes.titlePlaceholder": "笔记标题",
  "notes.editorPlaceholder": "在这里记录复习笔记...",
  "notes.empty": "还没有笔记。可以新建一篇，或在复习时为当前资料建立关联笔记。",
  "notes.selectAll": "全选",
  "notes.clearSelection": "取消选择",
  "notes.exportSelected": "导出所选",
  "notes.deleteSelected": "删除所选",
  "notes.deleteCurrent": "删除当前",
  "notes.selectionEmpty": "未选择笔记",
  "notes.selectionCount": "已选择 {count} 篇笔记",
  "settings.title": "设置",
  "settings.subtitle": "个性化界面、调度算法与本地配置路径",
  "settings.personalization": "个性化",
  "settings.algorithm": "算法",
  "settings.fixed": "固定间隔",
  "settings.retention": "目标记忆率",
  "settings.maxReviews": "每日复习上限",
  "settings.reminderTime": "提醒时间",
  "settings.reminderEnabled": "提醒开关",
  "settings.autoOpen": "复习开始时外部打开文件",
  "settings.notesDir": "笔记存储目录",
  "settings.exportDir": "默认导出目录",
  "settings.localNoteOpen": "本地方式新建后打开所在文件夹",
  "settings.theme": "主题",
  "settings.accent": "强调色",
  "settings.language": "语言",
  "settings.customCss": "自定义 CSS",
  "settings.paths": "配置位置",
  "settings.profileDir": "主数据目录",
  "settings.importProfile": "导入迁移包路径",
  "theme.light": "明亮",
  "theme.dark": "深色",
  "theme.paper": "纸面",
  "paths.config": "配置文件",
  "paths.database": "数据库",
  "paths.appDir": "程序数据目录",
  "paths.log": "日志",
  "paths.plugins": "插件目录",
  "paths.notes": "笔记目录",
  "paths.exports": "导出目录",
  "paths.pointer": "位置指针",
  "help.title": "帮助说明",
  "help.body": "完整教程已经放在左侧“帮助”页。这里保存的是个性化配置：复习算法、提醒、主题、笔记目录、导出目录和自定义 CSS。",
  "help.startTitle": "快速入门",
  "help.subtitle": "从选择文件库到迁移备份，一页看清软件怎么用",
  "help.libraryTitle": "文件库",
  "help.libraryBody": "点击“添加文件库”选择已有资料文件夹，或把路径粘贴到文件库页手动扫描。软件只建立索引，不移动原始文件。",
  "help.reviewTitle": "复习",
  "help.reviewBody": "每天点击“开始复习”。读完资料后选择忘记、困难、良好或简单，系统会自动安排下一次复习。",
  "help.openTitle": "打开方式",
  "help.openBody": "复习开始默认只在软件内预览，不会弹出系统默认软件。无法预览时再点“默认打开”或“其他应用”。",
  "help.notesTitle": "笔记",
  "help.notesBody": "笔记是真实 Markdown 文件。可以在软件里新建、编辑、保存，也可以用“本地方式新建”让资源管理器接管。",
  "help.notesManageTitle": "笔记管理",
  "help.notesManageBody": "在笔记列表勾选多篇笔记后，可以批量导出到默认导出目录，或确认后删除笔记文件和数据库记录。",
  "help.exportTitle": "导出与迁移",
  "help.exportBody": "在设置页先选择默认导出目录，再导出 CSV、JSON、数据库备份或完整迁移包。迁移包包含配置、数据库备份、插件和笔记。",
  "help.pathsTitle": "配置路径",
  "help.pathsBody": "设置页会显示配置文件、数据库、日志、插件、笔记、导出目录的完整路径。主数据目录可一键迁移。",
  "help.pluginsTitle": "插件与未来升级",
  "help.pluginsBody": "插件目录已预留，默认只读取清单不执行插件代码。长期稳定依靠 SQLite、JSON、迁移包和体检流程。",
  "help.safetyTitle": "安全边界",
  "help.safetyBody": "删除文件库索引不会删除原始资料。删除笔记会删除你创建的笔记文件，软件会先弹出确认。",
  "plugins.title": "插件开发预留",
  "plugins.empty": "暂无插件。以后把插件文件夹放在这里即可。",
  "health.title": "长期稳定性体检",
  "health.hint": "点击体检，检查数据库、配置、资源文件和原始文件可见性。",
  "filters.all": "全部",
  "filters.due": "到期",
  "filters.new": "新资料",
  "filters.future": "未到期",
  "filters.status": "状态筛选",
  "status.active": "活动",
  "status.suspended": "暂停",
  "status.done": "完成",
  "status.all": "全部状态",
  "batch.tag": "批量标签",
  "batch.tagShort": "标签",
  "batch.suspend": "暂停所选",
  "batch.suspendShort": "暂停",
  "batch.activate": "恢复为活动",
  "batch.activateShort": "恢复",
  "batch.dueToday": "设为今天复习",
  "batch.todayShort": "今天",
  "batch.done": "标记完成",
  "batch.doneShort": "完成",
  "batch.delete": "删除索引记录",
  "batch.deleteShort": "删除",
  "table.file": "文件",
  "table.due": "到期",
  "table.retention": "记忆率",
  "table.count": "次数",
  "table.time": "时长",
  "table.actions": "操作",
  "ratings.again": "忘记",
  "ratings.againHint": "很快再看",
  "ratings.hard": "困难",
  "ratings.hardHint": "缩短间隔",
  "ratings.good": "良好",
  "ratings.goodHint": "正常推进",
  "ratings.easy": "简单",
  "ratings.easyHint": "拉长间隔",
  "onboarding.step1Title": "欢迎使用智能文件复习系统",
  "onboarding.step1Body": "它不会移动你的资料，只会索引本地文件，并按记忆曲线提醒你复习。",
  "onboarding.step2Title": "选择一个本地文件库",
  "onboarding.step2Body": "从你的 PDF、笔记、图片、视频文件夹开始。扫描后就能浏览、搜索和批量管理。",
  "onboarding.step3Title": "每天从“开始复习”进入",
  "onboarding.step3Body": "阅读资料后选择忘记、困难、良好或简单，系统会自动安排下一次复习。",
  "empty.noDueTitle": "今天没有到期资料",
  "empty.noDueBody": "可以浏览文件库添加新资料，或安心收工。",
  "empty.noFuture": "暂无未来到期数据。",
  "empty.noLibraryTitle": "还没有文件库",
  "empty.noLibraryBody": "点击添加文件库，选择你已有的资料文件夹。",
  "empty.noTree": "这个文件夹里没有可显示内容。",
  "empty.noItemsTitle": "没有匹配文件",
  "empty.noItemsBody": "调整筛选条件，或扫描一个本地文件库。",
  "empty.fileMissing": "文件不存在",
  "empty.noHistory": "暂无历史记录。",
  "labels.noTags": "无标签",
  "labels.fileMissing": "文件缺失",
  "labels.folder": "文件夹",
  "labels.unscanned": "未扫描",
  "labels.files": "个文件",
  "labels.reviewButton": "复习",
  "labels.reviewRound": "第 {count} 次",
  "labels.intervalDays": "间隔 {days} 天",
  "labels.report": "报告：{path}",
  "time.unscheduled": "未安排",
  "time.today": "今天 {time}",
  "time.tomorrow": "明天 {time}",
  "time.yesterday": "昨天 {time}",
  "toast.openingFolderPicker": "正在打开文件夹选择窗口...",
  "toast.cancelled": "已取消选择；你也可以直接粘贴文件夹路径后扫描。",
  "toast.pathRequired": "请先输入一个有效路径",
  "toast.profileMoved": "主数据目录已迁移：{path}",
  "toast.profileImported": "迁移包已导入，导入前备份：{path}",
  "toast.profileExported": "迁移包已导出：{path}",
  "toast.packageSelected": "已选择迁移包",
  "toast.exportDirSelected": "已选择导出目录：{path}",
  "toast.noteCreated": "笔记已创建",
  "toast.noteSaved": "笔记已保存",
  "toast.noNoteSelected": "请先选择或新建一篇笔记",
  "toast.notesExported": "已导出 {count} 篇笔记到：{path}",
  "toast.notesDeleted": "已删除 {count} 篇笔记",
  "toast.scanDone": "扫描完成：新增 {added}，更新 {updated}",
  "toast.scanAll": "正在扫描全部文件库...",
  "toast.scanAllDone": "扫描完成，处理 {count} 条记录",
  "toast.noDue": "当前没有到期资料",
  "toast.startFirst": "请先开始一项复习",
  "toast.reviewSaved": "已记录，下一次：{date}",
  "toast.selectFirst": "请先勾选文件",
  "toast.selectNotesFirst": "请先勾选笔记",
  "toast.tagUpdated": "已更新 {count} 个文件的标签",
  "toast.suspended": "已暂停 {count} 个文件",
  "toast.statusChanged": "已{label} {count} 个文件",
  "toast.dueToday": "已设为今天复习：{count} 个文件",
  "toast.deleted": "已删除 {count} 条索引记录",
  "toast.settingsSaved": "设置已保存",
  "toast.backupDone": "数据库备份完成：{path}",
  "toast.healthOk": "体检通过",
  "toast.healthBad": "体检发现需要处理的问题",
  "toast.exported": "已导出：{path}",
  "toast.exportedJson": "已导出可移植 JSON：{path}",
  "prompt.tags": "输入标签，多个标签用英文逗号分隔：",
  "confirm.delete": "确定删除 {count} 条索引记录？不会删除原始文件。",
  "confirm.deleteNotes": "确定删除 {count} 篇笔记？这会删除笔记文件和数据库记录。",
  "health.good": "状态良好",
  "health.needsAttention": "需要关注",
};

Object.assign(I18N["en-US"], {
  "nav.help": "Help",
  "actions.chooseExportDir": "Choose Export Folder",
  "actions.openExportFolder": "Open Export Folder",
  "notes.selectAll": "Select All",
  "notes.clearSelection": "Clear",
  "notes.exportSelected": "Export Selected",
  "notes.deleteSelected": "Delete Selected",
  "notes.deleteCurrent": "Delete Current",
  "notes.selectionEmpty": "No notes selected",
  "notes.selectionCount": "{count} notes selected",
  "settings.exportDir": "Default export folder",
  "paths.exports": "Exports folder",
  "help.body": "The full tutorial is now on the Help page. This page stores personalization: scheduling, reminders, theme, notes folder, export folder, and custom CSS.",
  "help.startTitle": "Quick Start",
  "help.subtitle": "From choosing a library to backup and migration",
  "help.libraryTitle": "Library",
  "help.libraryBody": "Choose an existing folder or paste its path on the Library page. The app indexes files and does not move your originals.",
  "help.reviewTitle": "Review",
  "help.reviewBody": "Use Start Review each day. After reading, rate Again, Hard, Good, or Easy so the next review is scheduled.",
  "help.openTitle": "Opening Files",
  "help.openBody": "Reviews stay inside the app by default. If a format cannot be previewed, use Default Open or Other App.",
  "help.notesTitle": "Notes",
  "help.notesBody": "Notes are real Markdown files. Create, edit, and save them in the app, or use local file workflows.",
  "help.notesManageTitle": "Note Management",
  "help.notesManageBody": "Select notes in the list to export them to the default export folder or delete note files and database records after confirmation.",
  "help.exportTitle": "Export and Migration",
  "help.exportBody": "Choose a default export folder first, then export CSV, JSON, database backups, or a full profile package with config, backups, plugins, and notes.",
  "help.pathsTitle": "Data Paths",
  "help.pathsBody": "Settings shows config, database, log, plugins, notes, and export folders. The main data folder can be moved in one step.",
  "help.pluginsTitle": "Plugins and Future Upgrades",
  "help.pluginsBody": "The plugins folder is reserved. The app reads manifests only by default. Long-term stability depends on SQLite, JSON, profile packages, and health checks.",
  "help.safetyTitle": "Safety",
  "help.safetyBody": "Deleting library index records never deletes source files. Deleting notes deletes note files after confirmation.",
  "toast.exportDirSelected": "Export folder selected: {path}",
  "toast.notesExported": "Exported {count} notes to: {path}",
  "toast.notesDeleted": "Deleted {count} notes",
  "toast.selectNotesFirst": "Select notes first",
  "confirm.deleteNotes": "Delete {count} notes? This removes note files and database records.",
});

function t(key, vars = {}) {
  const pack = I18N[state.lang] || I18N["zh-CN"];
  const fallback = I18N["zh-CN"][key] || key;
  return String(pack[key] || fallback).replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? "");
}

function applyI18n() {
  document.documentElement.lang = state.lang;
  document.body.dataset.lang = state.lang;
  $$("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  $$("[data-i18n-title]").forEach((node) => {
    node.setAttribute("title", t(node.dataset.i18nTitle));
  });
  $$("[data-i18n-placeholder]").forEach((node) => {
    node.setAttribute("placeholder", t(node.dataset.i18nPlaceholder));
  });
  document.title = state.lang === "en-US" ? "File Review 2.4" : "智能文件复习系统 2.4";
  updateOnboardingButtons();
}

function pad(num) {
  return String(num).padStart(2, "0");
}

function hms(seconds) {
  const value = Math.max(0, Math.floor(seconds || 0));
  return `${pad(Math.floor(value / 3600))}:${pad(Math.floor((value % 3600) / 60))}:${pad(value % 60)}`;
}

function dayText(value) {
  if (!value) return t("time.unscheduled");
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const today = new Date();
  const start = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const target = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const diff = Math.round((target - start) / 86400000);
  const time = `${pad(date.getHours())}:${pad(date.getMinutes())}`;
  if (diff === 0) return t("time.today", { time });
  if (diff === 1) return t("time.tomorrow", { time });
  if (diff === -1) return t("time.yesterday", { time });
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${time}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function api(path, options = {}) {
  const init = {
    method: options.method || "GET",
    headers: { "Content-Type": "application/json" },
  };
  if (options.body !== undefined) init.body = JSON.stringify(options.body);
  const response = await fetch(path, init);
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    throw new Error(data.error || data || `Request failed: ${response.status}`);
  }
  return data;
}

function toast(message, isError = false) {
  const node = $("#toast");
  node.textContent = message;
  node.style.background = isError ? "#b91c1c" : "#111827";
  node.classList.add("show");
  clearTimeout(node._timer);
  node._timer = setTimeout(() => node.classList.remove("show"), 3200);
}

function setView(view) {
  state.view = view;
  $$(".nav-item").forEach((button) => button.classList.toggle("active", button.dataset.view === view));
  $$(".view").forEach((node) => node.classList.remove("active"));
  const activeView = $(`#${view}View`);
  if (!activeView) return;
  activeView.classList.add("active");
  const titles = {
    dashboard: [t("dashboard.title"), t("dashboard.subtitle")],
    library: [t("library.title"), t("library.subtitle")],
    review: [t("review.title"), t("review.subtitle")],
    notes: [t("notes.title"), t("notes.subtitle")],
    settings: [t("settings.title"), t("settings.subtitle")],
    help: [t("help.title"), t("help.subtitle")],
  };
  $("#viewTitle").textContent = titles[view]?.[0] || "";
  $("#viewSubtitle").textContent = titles[view]?.[1] || "";
  if (view === "library") loadItems();
  if (view === "notes") loadNotes();
  if (view === "settings") renderSettings();
}

function applyTheme() {
  const config = state.config || {};
  const ui = config.ui || {};
  document.body.classList.toggle("dark", ui.theme === "dark");
  document.body.classList.toggle("paper", ui.theme === "paper");
  const css = `
    :root {
      --accent: ${ui.accent || "#2563eb"};
      --surface: ${ui.surface || "#ffffff"};
      --bg: ${ui.background || "#f4f6f8"};
      --text: ${ui.text || "#172033"};
      --sidebar: ${ui.sidebar || "#111827"};
    }
    ${ui.custom_css || ""}
  `;
  $("#runtimeTheme").textContent = css;
}

async function loadOverview() {
  state.overview = await api("/api/overview");
  state.config = state.overview.config;
  state.lang = localStorage.getItem("fileReviewerLanguage") || state.config?.ui?.language || "zh-CN";
  state.libraries = state.overview.libraries || [];
  await loadCommonPaths();
  applyI18n();
  applyTheme();
  renderDashboard();
  renderLibraries();
  renderSettings();
}

async function loadCommonPaths() {
  try {
    const data = await api("/api/common-paths");
    state.commonPaths = data.paths || [];
  } catch {
    state.commonPaths = [];
  }
}

function renderDashboard() {
  const stats = state.overview?.stats || {};
  $("#metricDue").textContent = stats.due || 0;
  $("#metricTotal").textContent = stats.total || 0;
  $("#metricReviewedToday").textContent = stats.reviewed_today || 0;
  $("#metricSecondsToday").textContent = hms(stats.seconds_today || 0);
  $("#metricStreak").textContent = stats.streak || 0;

  const dueList = $("#dueList");
  const dueItems = state.overview?.due_items || [];
  dueList.innerHTML = dueItems.length
    ? dueItems.map((item) => `
      <div class="due-item">
        <div>
          <strong>${escapeHtml(item.file_name)}</strong>
          <span>${escapeHtml(item.tags || t("labels.noTags"))} · ${dayText(item.due_at)} · ${Math.round(item.retrievability * 100)}%</span>
        </div>
        <button class="primary-button" data-start-review="${item.id}">${t("labels.reviewButton")}</button>
      </div>
    `).join("")
    : `<div class="empty-state friendly-empty">
        <strong>${t("empty.noDueTitle")}</strong>
        <span>${t("empty.noDueBody")}</span>
        <button class="secondary-button" data-view-link="library">${t("actions.addLibrary")}</button>
      </div>`;

  const rows = state.overview?.future_due || [];
  const max = Math.max(1, ...rows.map((row) => row.count));
  $("#futureBars").innerHTML = rows.length
    ? rows.map((row) => `
      <div class="future-row">
        <span>${escapeHtml(row.day)}</span>
        <div class="bar-track"><div class="bar-fill" style="width:${Math.max(5, row.count / max * 100)}%"></div></div>
        <strong>${row.count}</strong>
      </div>
    `).join("")
    : `<p class="muted">${t("empty.noFuture")}</p>`;
}

function renderLibraries() {
  const list = $("#libraryList");
  const libraries = state.libraries || [];
  if (!state.activeLibraryId && libraries.length) state.activeLibraryId = libraries[0].id;
  list.innerHTML = libraries.length
    ? libraries.map((library) => `
      <div class="library-item ${library.id === state.activeLibraryId ? "active" : ""}" data-library-id="${library.id}">
        <strong>${escapeHtml(library.display_name)}</strong>
        <small>${escapeHtml(library.root_path)}</small>
        <small>${library.file_count || 0} ${t("labels.files")} · ${library.last_scan_at ? dayText(library.last_scan_at) : t("labels.unscanned")}</small>
      </div>
    `).join("")
    : `<div class="empty-state friendly-empty">
        <strong>${t("empty.noLibraryTitle")}</strong>
        <span>${t("empty.noLibraryBody")}</span>
        <button class="primary-button" id="emptyAddLibraryBtn">${t("actions.addLibrary")}</button>
      </div>`;
  renderCommonPaths();
  if (state.activeLibraryId) loadTree(state.activeLibraryId, state.treeRel);
}

function renderCommonPaths() {
  const target = $("#commonPathChips");
  if (!target) return;
  target.innerHTML = (state.commonPaths || []).map((item) => `
    <button type="button" class="chip" data-common-path="${escapeHtml(item.path)}" title="${escapeHtml(item.path)}">
      ${escapeHtml(item.label)}
    </button>
  `).join("");
}

async function loadTree(libraryId, rel = "") {
  try {
    const data = await api(`/api/tree?library_id=${libraryId}&rel=${encodeURIComponent(rel)}`);
    state.treeRel = data.rel || "";
    const parentRel = state.treeRel.split(/[\\/]/).slice(0, -1).join("/");
    const rows = [];
    if (state.treeRel) {
      rows.push(`<div class="tree-row dir" data-tree-rel="${escapeHtml(parentRel)}"><strong>..</strong><span></span></div>`);
    }
    rows.push(...data.children.map((node) => `
      <div class="tree-row ${node.is_dir ? "dir" : ""}" data-tree-rel="${escapeHtml(node.rel)}" data-indexed-id="${node.indexed_id || ""}" data-is-dir="${node.is_dir}">
        <strong>${escapeHtml(node.name)}</strong>
        <span>${node.is_dir ? t("labels.folder") : `${escapeHtml(node.ext || "")} · ${escapeHtml(node.size)}`}</span>
      </div>
    `));
    $("#treeList").innerHTML = rows.join("") || `<p class="muted">${t("empty.noTree")}</p>`;
  } catch (error) {
    $("#treeList").innerHTML = `<p class="danger">${escapeHtml(error.message)}</p>`;
  }
}

async function loadItems() {
  const params = new URLSearchParams({
    search: state.filters.search,
    status: state.filters.status,
    due: state.filters.due,
    sort: state.filters.sort,
    direction: state.filters.direction,
    page_size: "150",
  });
  const data = await api(`/api/items?${params.toString()}`);
  state.items = data.items || [];
  renderItems();
}

function renderItems() {
  const body = $("#itemsBody");
  body.innerHTML = state.items.map((item) => {
    const checked = state.selectedIds.has(item.id) ? "checked" : "";
    const tags = (item.tags || "").split(",").map((tag) => tag.trim()).filter(Boolean);
    const tagHtml = tags.length ? tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("") : `<span class="muted">${t("labels.noTags")}</span>`;
    const missing = item.exists ? "" : `<span class="danger">${t("labels.fileMissing")}</span>`;
    return `
      <tr data-item-id="${item.id}">
        <td class="check-cell"><input class="row-check" type="checkbox" data-id="${item.id}" ${checked}></td>
        <td class="file-cell">
          <div class="file-main">
            <strong title="${escapeHtml(item.file_path)}">${escapeHtml(item.file_name)}</strong>
            <span class="file-sub">${escapeHtml(item.relative_path || item.file_path)} ${missing}</span>
            <div class="tag-line">${tagHtml}</div>
          </div>
        </td>
        <td>${dayText(item.due_at)}</td>
        <td>${Math.round(item.retrievability * 100)}%</td>
        <td>${item.review_count}</td>
        <td>${hms(item.total_read_seconds)}</td>
        <td>
          <div class="actions-cell">
            <button class="icon-button" title="${t("labels.reviewButton")}" data-start-review="${item.id}">▶</button>
            <button class="icon-button" title="${t("actions.openFile")}" data-open-item="${item.id}">↗</button>
            <button class="icon-button" title="${t("actions.folder")}" data-folder-item="${item.id}">⌖</button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
  if (!state.items.length) {
    body.innerHTML = `<tr><td colspan="7"><div class="empty-state friendly-empty">
      <strong>${t("empty.noItemsTitle")}</strong>
      <span>${t("empty.noItemsBody")}</span>
      <button class="primary-button" id="emptyTableAddLibraryBtn">${t("actions.addLibrary")}</button>
    </div></td></tr>`;
  }
}

async function chooseLibrary() {
  toast(t("toast.openingFolderPicker"));
  const result = await api("/api/libraries/select", { method: "POST", body: {} });
  if (result.cancelled) {
    toast(t("toast.cancelled"));
    return;
  }
  if (result.scan) {
    toast(t("toast.scanDone", { added: result.scan.added, updated: result.scan.updated }));
    await loadOverview();
    await loadItems();
    return;
  }
  await addLibraryPath(result.path);
}

async function addLibraryPath(path) {
  const rootPath = String(path || "").trim();
  if (!rootPath) {
    toast(t("toast.pathRequired"), true);
    return;
  }
  const result = await api("/api/libraries/add", { method: "POST", body: { path: rootPath } });
  toast(t("toast.scanDone", { added: result.scan.added, updated: result.scan.updated }));
  await loadOverview();
  await loadItems();
}

async function scanAll() {
  toast(t("toast.scanAll"));
  const result = await api("/api/libraries/scan", { method: "POST", body: {} });
  const total = (result.scans || []).reduce((sum, scan) => sum + scan.added + scan.updated, 0);
  toast(t("toast.scanAllDone", { count: total }));
  await loadOverview();
  await loadItems();
}

async function startReview(itemId = null) {
  const result = await api("/api/review/start", { method: "POST", body: itemId ? { item_id: Number(itemId) } : {} });
  if (!result.item) {
    toast(t("toast.noDue"));
    return;
  }
  state.review.item = result.item;
  state.review.sessionId = result.session_id;
  state.review.startedAt = Date.now();
  setView("review");
  renderReview();
  loadHistory(result.item.id);
}

function renderReview() {
  const item = state.review.item;
  if (!item) return;
  $("#reviewFileName").textContent = item.file_name;
  $("#reviewMeta").textContent = `${item.tags || t("labels.noTags")} · ${t("labels.reviewRound", { count: item.review_count + 1 })} · ${item.file_path}`;
  renderPreview(item);
  startTimer();
}

function renderPreview(item) {
  const area = $("#previewArea");
  const ext = (item.ext || "").toLowerCase();
  const url = item.preview_url;
  if (!item.exists) {
    area.innerHTML = `<div class="empty-state"><strong>${t("empty.fileMissing")}</strong><span>${escapeHtml(item.file_path)}</span></div>`;
    return;
  }
  if ([".pdf"].includes(ext)) {
    area.innerHTML = `<embed src="${url}" type="application/pdf">`;
  } else if ([".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"].includes(ext)) {
    area.innerHTML = `<img src="${url}" alt="${escapeHtml(item.file_name)}">`;
  } else if ([".mp4", ".mkv", ".mov", ".avi", ".wmv"].includes(ext)) {
    area.innerHTML = `<video src="${url}" controls></video>`;
  } else if ([".mp3", ".wav", ".m4a"].includes(ext)) {
    area.innerHTML = `<div class="empty-state"><strong>${escapeHtml(item.file_name)}</strong><audio src="${url}" controls></audio></div>`;
  } else if ([".html", ".htm", ".txt", ".md"].includes(ext)) {
    area.innerHTML = `<iframe src="${url}" title="${escapeHtml(item.file_name)}"></iframe>`;
  } else {
    area.innerHTML = `
      <div class="empty-state">
        <strong>${escapeHtml(item.file_name)}</strong>
        <span>${escapeHtml(item.file_path)}</span>
        <div class="review-actions">
          <button class="primary-button" data-open-item="${item.id}">${t("actions.openFile")}</button>
          <button class="secondary-button" onclick="openItemWith(${item.id})">${t("actions.openWithShort")}</button>
        </div>
      </div>
    `;
  }
}

function startTimer() {
  clearInterval(state.review.timerId);
  state.review.timerId = setInterval(() => {
    if (!state.review.startedAt) return;
    $("#reviewTimer").textContent = hms((Date.now() - state.review.startedAt) / 1000);
  }, 500);
}

async function finishReview(rating) {
  const item = state.review.item;
  if (!item) {
    toast(t("toast.startFirst"), true);
    return;
  }
  const duration = Math.floor((Date.now() - state.review.startedAt) / 1000);
  const result = await api("/api/review/finish", {
    method: "POST",
    body: {
      item_id: item.id,
      session_id: state.review.sessionId,
      rating: Number(rating),
      duration_seconds: duration,
    },
  });
  state.review.item = result.item;
  toast(t("toast.reviewSaved", { date: dayText(result.item.due_at) }));
  await loadOverview();
  await loadItems();
  await loadHistory(item.id);
}

async function loadHistory(itemId) {
  const data = await api(`/api/history/${itemId}`);
  const rows = data.history || [];
  $("#historyList").innerHTML = rows.length
    ? rows.map((row) => `
      <div class="history-row">
        <strong>${escapeHtml(row.rating_label)} · ${hms(row.duration_seconds)}</strong>
        <span>${dayText(row.ended_at)} · ${escapeHtml(row.algorithm || "")} · ${t("labels.intervalDays", { days: Number(row.scheduled_days || 0).toFixed(1) })}</span>
      </div>
    `).join("")
    : `<p class="muted">${t("empty.noHistory")}</p>`;
}

async function openItem(id) {
  await api("/api/items/open", { method: "POST", body: { id: Number(id) } });
}

async function openItemWith(id) {
  await api("/api/items/open-with", { method: "POST", body: { id: Number(id) } });
}

async function openFolder(id) {
  await api("/api/items/open-folder", { method: "POST", body: { id: Number(id) } });
}

async function openFolderByPath(path) {
  await api("/api/path/open", { method: "POST", body: { path } });
}

async function loadNotes(itemId = null) {
  const suffix = itemId ? `?item_id=${encodeURIComponent(itemId)}` : "";
  const data = await api(`/api/notes${suffix}`);
  state.notes = data.notes || [];
  const available = new Set(state.notes.map((note) => note.id));
  state.selectedNoteIds = new Set(Array.from(state.selectedNoteIds).filter((id) => available.has(id)));
  renderNotesList();
}

function renderNotesList() {
  const target = $("#notesList");
  if (!target) return;
  const count = state.selectedNoteIds.size;
  const summary = $("#noteSelectionSummary");
  if (summary) summary.textContent = count ? t("notes.selectionCount", { count }) : t("notes.selectionEmpty");
  target.innerHTML = state.notes.length
    ? state.notes.map((note) => `
      <div class="note-row ${note.id === state.activeNoteId ? "active" : ""}">
        <label class="note-check">
          <input class="note-row-check" type="checkbox" data-note-check="${note.id}" ${state.selectedNoteIds.has(note.id) ? "checked" : ""}>
          <span></span>
        </label>
        <button class="note-row-main" data-note-id="${note.id}">
          <strong>${escapeHtml(note.title)}</strong>
          <span>${dayText(note.updated_at)} · ${escapeHtml(note.size || "")}</span>
          <span>${escapeHtml(note.file_path)}</span>
        </button>
      </div>
    `).join("")
    : `<div class="empty-state friendly-empty"><strong>${t("notes.empty")}</strong></div>`;
}

async function createNote({ itemId = null, localMode = false } = {}) {
  const baseTitle = state.review.item && itemId ? `${state.review.item.file_name} 复习笔记` : t("actions.newNote");
  const result = await api("/api/notes/create", {
    method: "POST",
    body: {
      item_id: itemId,
      title: baseTitle,
      source: localMode ? "local" : "app",
      open_local: localMode || Boolean(state.config?.notes?.open_local_note_after_create),
    },
  });
  state.activeNoteId = result.note.id;
  toast(t("toast.noteCreated"));
  await loadNotes();
  await loadNote(result.note.id);
  setView("notes");
}

async function loadNote(noteId) {
  const result = await api(`/api/notes/${noteId}`);
  const note = result.note;
  state.activeNoteId = note.id;
  $("#noteTitleInput").value = note.title || "";
  $("#noteEditor").value = note.content || "";
  $("#notePath").textContent = note.file_path || "";
  renderNotesList();
}

async function saveNote() {
  if (!state.activeNoteId) {
    toast(t("toast.noNoteSelected"), true);
    return;
  }
  const result = await api("/api/notes/save", {
    method: "POST",
    body: {
      id: state.activeNoteId,
      title: $("#noteTitleInput").value,
      content: $("#noteEditor").value,
    },
  });
  toast(t("toast.noteSaved"));
  await loadNotes();
  await loadNote(result.note.id);
}

async function openNote(chooseApp = false) {
  if (!state.activeNoteId) {
    toast(t("toast.noNoteSelected"), true);
    return;
  }
  await api("/api/notes/open", { method: "POST", body: { id: state.activeNoteId, choose_app: chooseApp } });
}

function selectedNoteIdsOrActive() {
  const ids = Array.from(state.selectedNoteIds);
  if (!ids.length && state.activeNoteId) ids.push(state.activeNoteId);
  return ids;
}

async function exportSelectedNotes() {
  const ids = selectedNoteIdsOrActive();
  if (!ids.length) {
    toast(t("toast.selectNotesFirst"), true);
    return;
  }
  const result = await api("/api/notes/export", {
    method: "POST",
    body: { ids, target_dir: getExportDir() },
  });
  toast(t("toast.notesExported", { count: result.exported || 0, path: result.export_dir || "" }));
}

async function deleteSelectedNotes(ids = selectedNoteIdsOrActive()) {
  if (!ids.length) {
    toast(t("toast.selectNotesFirst"), true);
    return;
  }
  if (!confirm(t("confirm.deleteNotes", { count: ids.length }))) return;
  const result = await api("/api/notes/delete", { method: "POST", body: { ids, delete_files: true } });
  ids.forEach((id) => state.selectedNoteIds.delete(Number(id)));
  if (ids.includes(state.activeNoteId)) {
    state.activeNoteId = null;
    $("#noteTitleInput").value = "";
    $("#noteEditor").value = "";
    $("#notePath").textContent = "";
  }
  toast(t("toast.notesDeleted", { count: result.deleted || ids.length }));
  await loadNotes();
}

async function batchTag() {
  const ids = Array.from(state.selectedIds);
  if (!ids.length) {
    toast(t("toast.selectFirst"), true);
    return;
  }
  const value = prompt(t("prompt.tags"));
  if (value === null) return;
  await api("/api/items/update", { method: "POST", body: { ids, fields: { tags: value } } });
  toast(t("toast.tagUpdated", { count: ids.length }));
  await loadItems();
}

async function batchSuspend() {
  const ids = Array.from(state.selectedIds);
  if (!ids.length) {
    toast(t("toast.selectFirst"), true);
    return;
  }
  await api("/api/items/update", { method: "POST", body: { ids, fields: { status: "suspended" } } });
  toast(t("toast.suspended", { count: ids.length }));
  state.selectedIds.clear();
  await loadItems();
  await loadOverview();
}

async function batchSetStatus(status, label) {
  const ids = Array.from(state.selectedIds);
  if (!ids.length) {
    toast(t("toast.selectFirst"), true);
    return;
  }
  await api("/api/items/update", { method: "POST", body: { ids, fields: { status } } });
  toast(t("toast.statusChanged", { label, count: ids.length }));
  state.selectedIds.clear();
  await loadItems();
  await loadOverview();
}

async function batchDueToday() {
  const ids = Array.from(state.selectedIds);
  if (!ids.length) {
    toast(t("toast.selectFirst"), true);
    return;
  }
  await api("/api/items/update", {
    method: "POST",
    body: { ids, fields: { due_at: new Date().toISOString().slice(0, 19) } },
  });
  toast(t("toast.dueToday", { count: ids.length }));
  state.selectedIds.clear();
  await loadItems();
  await loadOverview();
}

async function batchDelete() {
  const ids = Array.from(state.selectedIds);
  if (!ids.length) {
    toast(t("toast.selectFirst"), true);
    return;
  }
  if (!confirm(t("confirm.delete", { count: ids.length }))) return;
  await api("/api/items/delete", { method: "POST", body: { ids } });
  toast(t("toast.deleted", { count: ids.length }));
  state.selectedIds.clear();
  await loadItems();
  await loadOverview();
}

function renderSettings() {
  if (!state.config) return;
  const scheduler = state.config.scheduler || {};
  const reminders = state.config.reminders || {};
  const review = state.config.review || {};
  const ui = state.config.ui || {};
  const notes = state.config.notes || {};
  const exportsConfig = state.config.exports || {};
  $("#algorithmSelect").value = scheduler.algorithm || "FSRS-Lite";
  $("#retentionInput").value = scheduler.desired_retention || 0.9;
  $("#maxReviewsInput").value = scheduler.max_reviews_per_day || 120;
  $("#reminderTimeInput").value = reminders.time || "20:30";
  $("#reminderEnabledInput").checked = Boolean(reminders.enabled);
  $("#autoOpenInput").checked = Boolean(review.auto_open_file);
  $("#notesDirInput").value = notes.storage_dir || state.overview?.app?.notes_dir || "";
  $("#exportDirInput").value = exportsConfig.default_dir || state.overview?.app?.export_dir || "";
  $("#localNoteOpenInput").checked = Boolean(notes.open_local_note_after_create);
  $("#themeSelect").value = ui.theme || "light";
  $("#languageSelect").value = ui.language || state.lang || "zh-CN";
  $("#accentInput").value = ui.accent || "#2563eb";
  $("#customCssInput").value = ui.custom_css || "";
  const app = state.overview?.app || {};
  $("#configPath").textContent = app.config_path || "";
  $("#dbPath").textContent = app.db_path || "";
  $("#appDir").textContent = app.app_dir || "";
  $("#logPath").textContent = app.log_path || "";
  $("#pluginsPath").textContent = app.plugins_dir || "";
  $("#notesPath").textContent = app.notes_dir || "";
  $("#exportsPath").textContent = app.export_dir || "";
  $("#pointerPath").textContent = app.profile_pointer_path || "";
  $("#profileDirInput").value = app.app_dir || "";
  renderPlugins();
}

async function saveSettings() {
  const config = {
    scheduler: {
      algorithm: $("#algorithmSelect").value,
      desired_retention: Number($("#retentionInput").value || 0.9),
      max_reviews_per_day: Number($("#maxReviewsInput").value || 120),
    },
    reminders: {
      enabled: $("#reminderEnabledInput").checked,
      time: $("#reminderTimeInput").value || "20:30",
      browser_notifications: true,
    },
    review: {
      auto_open_file: $("#autoOpenInput").checked,
    },
    notes: {
      storage_dir: $("#notesDirInput").value.trim(),
      default_extension: ".md",
      open_local_note_after_create: $("#localNoteOpenInput").checked,
    },
    exports: {
      default_dir: $("#exportDirInput").value.trim(),
    },
    ui: {
      language: $("#languageSelect").value,
      theme: $("#themeSelect").value,
      accent: $("#accentInput").value,
      custom_css: $("#customCssInput").value,
    },
  };
  const result = await api("/api/settings", { method: "POST", body: { config } });
  state.config = result.config;
  state.lang = result.config?.ui?.language || "zh-CN";
  localStorage.setItem("fileReviewerLanguage", state.lang);
  applyI18n();
  applyTheme();
  toast(t("toast.settingsSaved"));
  await loadOverview();
}

function getExportDir() {
  return ($("#exportDirInput")?.value || state.config?.exports?.default_dir || state.overview?.app?.export_dir || "").trim();
}

async function chooseExportDir() {
  toast(t("toast.openingFolderPicker"));
  const result = await api("/api/export/select-dir", { method: "POST", body: {} });
  if (result.cancelled) {
    toast(t("toast.cancelled"));
    return;
  }
  $("#exportDirInput").value = result.path || "";
  const config = { exports: { default_dir: result.path || "" } };
  const saved = await api("/api/settings", { method: "POST", body: { config } });
  state.config = saved.config;
  toast(t("toast.exportDirSelected", { path: result.path || "" }));
  await loadOverview();
}

async function openExportDir() {
  const target = getExportDir();
  if (!target) {
    toast(t("toast.pathRequired"), true);
    return;
  }
  await openFolderByPath(target);
}

async function backup() {
  const result = await api("/api/backup", { method: "POST", body: { target_dir: getExportDir() } });
  toast(t("toast.backupDone", { path: result.backup_path }));
}

async function exportProfile() {
  const result = await api("/api/export-profile", { method: "POST", body: { target_dir: getExportDir() } });
  toast(t("toast.profileExported", { path: result.export_path }));
}

async function chooseProfileDir() {
  toast(t("toast.openingFolderPicker"));
  const result = await api("/api/profile/select", { method: "POST", body: {} });
  if (result.cancelled) {
    toast(t("toast.cancelled"));
    return;
  }
  $("#profileDirInput").value = result.path || "";
}

async function moveProfile() {
  const path = $("#profileDirInput").value.trim();
  if (!path) {
    toast(t("toast.pathRequired"), true);
    return;
  }
  const result = await api("/api/profile/move", { method: "POST", body: { path } });
  state.overview.app = result.app || state.overview.app;
  toast(t("toast.profileMoved", { path: result.app?.app_dir || path }));
  await loadOverview();
  await healthCheck();
}

async function chooseImportProfilePackage() {
  const result = await api("/api/profile/select-package", { method: "POST", body: {} });
  if (result.cancelled) {
    toast(t("toast.cancelled"));
    return;
  }
  $("#importProfilePathInput").value = result.path || "";
  toast(t("toast.packageSelected"));
}

async function importProfile() {
  const path = $("#importProfilePathInput").value.trim();
  if (!path) {
    toast(t("toast.pathRequired"), true);
    return;
  }
  const result = await api("/api/profile/import", { method: "POST", body: { path } });
  toast(t("toast.profileImported", { path: result.backup_before_import }));
  await loadOverview();
  await loadItems();
  await healthCheck();
}

async function openProfileFolder() {
  const appDir = state.overview?.app?.app_dir;
  if (appDir) await openFolderByPath(appDir);
}

async function loadPlugins() {
  try {
    const result = await api("/api/plugins");
    state.plugins = result.plugins || [];
  } catch {
    state.plugins = [];
  }
  renderPlugins();
}

function renderPlugins() {
  const target = $("#pluginsList");
  if (!target) return;
  const plugins = state.plugins || [];
  target.innerHTML = plugins.length
    ? plugins.map((plugin) => `
      <div class="plugin-row">
        <strong>${escapeHtml(plugin.name || plugin.id)}</strong>
        <span>${escapeHtml(plugin.version || "")} ${plugin.has_manifest ? "manifest" : ""}</span>
        <span>${escapeHtml(plugin.description || plugin.path || "")}</span>
      </div>
    `).join("")
    : `<p class="muted">${t("plugins.empty")}</p>`;
}

async function healthCheck() {
  const result = await api("/api/health");
  renderHealth(result);
  toast(result.ok ? t("toast.healthOk") : t("toast.healthBad"), !result.ok);
}

function renderHealth(result) {
  $("#healthSummary").textContent = `${result.checked_at} · ${result.ok ? t("health.good") : t("health.needsAttention")} · ${t("labels.report", { path: result.report_path || "" })}`;
  $("#healthList").innerHTML = (result.checks || []).map((check) => `
    <div class="health-row">
      <div class="${check.ok ? "health-ok" : "health-bad"}">${check.ok ? "✓" : "!"}</div>
      <div>
        <strong>${escapeHtml(check.name)}</strong>
        <span>${escapeHtml(check.detail || "")}</span>
      </div>
    </div>
  `).join("");
}

async function exportCsv() {
  const result = await api("/api/export", { method: "POST", body: { target_dir: getExportDir() } });
  toast(t("toast.exported", { path: result.export_path }));
}

async function exportPortableJson() {
  const result = await api("/api/export-portable", { method: "POST", body: { target_dir: getExportDir() } });
  toast(t("toast.exportedJson", { path: result.export_path }));
}

function requestNotificationsIfNeeded() {
  if (!("Notification" in window)) return;
  if (Notification.permission === "default") {
    Notification.requestPermission().catch(() => {});
  }
}

function setupReminderLoop() {
  setInterval(() => {
    const config = state.config || {};
    const reminders = config.reminders || {};
    const stats = state.overview?.stats || {};
    if (!reminders.enabled || !reminders.browser_notifications || !stats.due) return;
    const now = new Date();
    const [hour, minute] = String(reminders.time || "20:30").split(":").map(Number);
    if (now.getHours() === hour && now.getMinutes() === minute && Notification.permission === "granted") {
      new Notification(state.lang === "en-US" ? "File Review" : "智能文件复习系统", {
        body: state.lang === "en-US"
          ? `${stats.due} items are due today.`
          : `今天还有 ${stats.due} 个资料等待复习。`,
      });
    }
  }, 60000);
}

function setOnboardingStep(step) {
  state.onboardingStep = Math.max(0, Math.min(2, step));
  $$(".onboarding-step").forEach((node) => {
    node.classList.toggle("active", Number(node.dataset.step) === state.onboardingStep);
  });
  updateOnboardingButtons();
}

function updateOnboardingButtons() {
  const prev = $("#onboardingPrevBtn");
  const next = $("#onboardingNextBtn");
  const library = $("#onboardingLibraryBtn");
  if (!prev || !next || !library) return;
  prev.disabled = state.onboardingStep === 0;
  next.classList.toggle("hidden", state.onboardingStep === 2);
  library.classList.toggle("hidden", state.onboardingStep !== 2);
}

function showOnboardingIfNeeded() {
  const seen = localStorage.getItem("fileReviewerOnboardingDone") === "1";
  const hasLibrary = (state.libraries || []).length > 0;
  if (!seen && !hasLibrary) {
    setOnboardingStep(0);
    $("#onboarding").classList.remove("hidden");
  }
}

function closeOnboarding() {
  localStorage.setItem("fileReviewerOnboardingDone", "1");
  $("#onboarding").classList.add("hidden");
}

function bindEvents() {
  document.addEventListener("click", async (event) => {
    const nav = event.target.closest("[data-view]");
    if (nav) setView(nav.dataset.view);

    const viewLink = event.target.closest("[data-view-link]");
    if (viewLink) setView(viewLink.dataset.viewLink);

    const start = event.target.closest("[data-start-review]");
    if (start) await startReview(start.dataset.startReview);

    const open = event.target.closest("[data-open-item]");
    if (open) await openItem(open.dataset.openItem);

    const folder = event.target.closest("[data-folder-item]");
    if (folder) await openFolder(folder.dataset.folderItem);

    const noteCheck = event.target.closest("[data-note-check]");
    if (noteCheck) {
      const id = Number(noteCheck.dataset.noteCheck);
      if (noteCheck.checked) state.selectedNoteIds.add(id);
      else state.selectedNoteIds.delete(id);
      renderNotesList();
      return;
    }

    const note = event.target.closest("[data-note-id]");
    if (note) await loadNote(Number(note.dataset.noteId));

    const library = event.target.closest("[data-library-id]");
    if (library) {
      state.activeLibraryId = Number(library.dataset.libraryId);
      state.treeRel = "";
      renderLibraries();
    }

    const tree = event.target.closest("[data-tree-rel]");
    if (tree) {
      const isDir = tree.dataset.isDir === "true" || tree.classList.contains("dir");
      if (isDir) {
        await loadTree(state.activeLibraryId, tree.dataset.treeRel || "");
      } else if (tree.dataset.indexedId) {
        await startReview(tree.dataset.indexedId);
      }
    }

    if (event.target.closest("#emptyAddLibraryBtn") || event.target.closest("#emptyTableAddLibraryBtn")) {
      await chooseLibrary();
    }

    const commonPath = event.target.closest("[data-common-path]");
    if (commonPath) {
      $("#manualLibraryPath").value = commonPath.dataset.commonPath || "";
    }
  });

  $("#chooseLibraryBtn").addEventListener("click", chooseLibrary);
  $("#chooseLibraryBtn2").addEventListener("click", chooseLibrary);
  $("#manualLibraryForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await addLibraryPath($("#manualLibraryPath").value);
  });
  $("#scanAllBtn").addEventListener("click", scanAll);
  $("#startDueBtn").addEventListener("click", () => startReview());
  $("#reviewStartNextBtn").addEventListener("click", () => startReview());
  $("#reviewOpenBtn").addEventListener("click", () => state.review.item && openItem(state.review.item.id));
  $("#reviewOpenWithBtn").addEventListener("click", () => state.review.item && openItemWith(state.review.item.id));
  $("#reviewFolderBtn").addEventListener("click", () => state.review.item && openFolder(state.review.item.id));
  $("#reviewCreateNoteBtn").addEventListener("click", () => state.review.item && createNote({ itemId: state.review.item.id }));
  $("#newNoteBtn").addEventListener("click", () => createNote());
  $("#newLocalNoteBtn").addEventListener("click", () => createNote({ localMode: true }));
  $("#openNotesFolderBtn").addEventListener("click", () => openFolderByPath(state.overview?.app?.notes_dir || state.overview?.app?.default_notes_dir));
  $("#selectAllNotesBtn").addEventListener("click", () => {
    state.notes.forEach((note) => state.selectedNoteIds.add(note.id));
    renderNotesList();
  });
  $("#clearNoteSelectionBtn").addEventListener("click", () => {
    state.selectedNoteIds.clear();
    renderNotesList();
  });
  $("#exportNotesBtn").addEventListener("click", exportSelectedNotes);
  $("#deleteNotesBtn").addEventListener("click", () => deleteSelectedNotes());
  $("#saveNoteBtn").addEventListener("click", saveNote);
  $("#openNoteBtn").addEventListener("click", () => openNote(false));
  $("#openNoteWithBtn").addEventListener("click", () => openNote(true));
  $("#deleteActiveNoteBtn").addEventListener("click", () => state.activeNoteId && deleteSelectedNotes([state.activeNoteId]));
  $("#saveSettingsBtn").addEventListener("click", saveSettings);
  $("#backupBtn").addEventListener("click", backup);
  $("#healthBtn").addEventListener("click", healthCheck);
  $("#portableExportBtn").addEventListener("click", exportPortableJson);
  $("#profileExportBtn").addEventListener("click", exportProfile);
  $("#chooseExportDirBtn").addEventListener("click", chooseExportDir);
  $("#openExportDirBtn").addEventListener("click", openExportDir);
  $("#chooseProfileDirBtn").addEventListener("click", chooseProfileDir);
  $("#moveProfileBtn").addEventListener("click", moveProfile);
  $("#chooseImportProfileBtn").addEventListener("click", chooseImportProfilePackage);
  $("#importProfileBtn").addEventListener("click", importProfile);
  $("#openProfileBtn").addEventListener("click", openProfileFolder);
  $("#refreshPluginsBtn").addEventListener("click", loadPlugins);
  $("#exportBtn").addEventListener("click", exportCsv);
  $("#batchTagBtn").addEventListener("click", batchTag);
  $("#batchSuspendBtn").addEventListener("click", batchSuspend);
  $("#batchActivateBtn").addEventListener("click", () => batchSetStatus("active", t("batch.activateShort")));
  $("#batchDoneBtn").addEventListener("click", () => batchSetStatus("done", t("batch.doneShort")));
  $("#batchDueTodayBtn").addEventListener("click", batchDueToday);
  $("#batchDeleteBtn").addEventListener("click", batchDelete);
  $("#languageSelect").addEventListener("change", async (event) => {
    state.lang = event.target.value;
    localStorage.setItem("fileReviewerLanguage", state.lang);
    state.config.ui = state.config.ui || {};
    state.config.ui.language = state.lang;
    applyI18n();
    setView(state.view);
    renderDashboard();
    renderLibraries();
    renderItems();
  });
  $("#onboardingCloseBtn").addEventListener("click", closeOnboarding);
  $("#onboardingPrevBtn").addEventListener("click", () => setOnboardingStep(state.onboardingStep - 1));
  $("#onboardingNextBtn").addEventListener("click", () => setOnboardingStep(state.onboardingStep + 1));
  $("#onboardingLibraryBtn").addEventListener("click", async () => {
    closeOnboarding();
    await chooseLibrary();
  });

  $$(".rating").forEach((button) => {
    button.addEventListener("click", () => finishReview(button.dataset.rating));
  });

  $("#globalSearch").addEventListener("input", (event) => {
    state.filters.search = event.target.value;
    if (state.view !== "library") setView("library");
    clearTimeout(state._searchTimer);
    state._searchTimer = setTimeout(loadItems, 220);
  });

  $("#statusFilter").addEventListener("change", (event) => {
    state.filters.status = event.target.value;
    loadItems();
  });

  $$(".seg").forEach((button) => {
    button.addEventListener("click", () => {
      $$(".seg").forEach((node) => node.classList.remove("active"));
      button.classList.add("active");
      state.filters.due = button.dataset.due;
      loadItems();
    });
  });

  $$(".item-table th[data-sort]").forEach((th) => {
    th.addEventListener("click", () => {
      const sort = th.dataset.sort;
      if (state.filters.sort === sort) {
        state.filters.direction = state.filters.direction === "asc" ? "desc" : "asc";
      } else {
        state.filters.sort = sort;
        state.filters.direction = "asc";
      }
      loadItems();
    });
  });

  $("#itemsBody").addEventListener("change", (event) => {
    if (!event.target.classList.contains("row-check")) return;
    const id = Number(event.target.dataset.id);
    if (event.target.checked) state.selectedIds.add(id);
    else state.selectedIds.delete(id);
  });

  $("#selectAll").addEventListener("change", (event) => {
    state.selectedIds.clear();
    if (event.target.checked) state.items.forEach((item) => state.selectedIds.add(item.id));
    renderItems();
  });

  window.addEventListener("keydown", (event) => {
    if (event.target.matches("input, textarea, select")) return;
    if (event.key === "r") startReview();
    if (["1", "2", "3", "4"].includes(event.key)) finishReview(Number(event.key) - 1);
    if (event.key === "/") {
      event.preventDefault();
      $("#globalSearch").focus();
    }
  });
}

async function init() {
  bindEvents();
  requestNotificationsIfNeeded();
  setupReminderLoop();
  await loadOverview();
  await loadPlugins();
  await loadItems();
  await loadNotes();
  setView("dashboard");
  showOnboardingIfNeeded();
  setInterval(loadOverview, 60000);
}

init().catch((error) => {
  console.error(error);
  toast(error.message, true);
});

# GalHub - CDN控制器

一个用于管理网页游戏的CDN系统，游戏以纯静态HTML网站形式存储和提供服务。

## 功能特点

- 使用Python开发
- SQLite数据库存储游戏信息
- 支持游戏上传、删除和列表查看
- 内置HTTP服务器提供游戏内容服务
- 游戏以静态HTML网站形式提供服务
- 图形化用户界面（基于Tkinter）
- 支持自定义域名设置
- 一键复制游戏访问链接

## 系统要求

- Python 3.6+
- 无需额外依赖（仅使用Python标准库）
- （可选）pyperclip库用于复制链接到剪贴板

## 安装和初始化

```bash
# 克隆或下载项目后，初始化系统
python main.py init
```

这将创建SQLite数据库和游戏存储目录。

如果要使用复制链接功能，需要安装pyperclip库：

```bash
pip install pyperclip
```

## 编译为可执行文件

本项目支持使用PyInstaller编译为Windows可执行文件，便于在没有Python环境的计算机上运行。

### 编译步骤

1. 安装PyInstaller：
   ```bash
   pip install pyinstaller
   ```

2. 使用提供的spec文件进行编译：
   ```bash
   pyinstaller main.spec
   ```

3. 编译完成后，可执行文件将位于 `dist/GalHub-CDN/` 目录中

### 编译配置说明

- 入口文件: [main_ui.py](/main_ui.py) (默认启动UI界面)
- 图形界面: 使用Tkinter构建
- 控制台: 禁用控制台窗口（图形界面模式）
- 输出目录: `dist/GalHub-CDN/`
- 包含文件:
  - README.md
  - games.db (数据库文件)
  - games/ (游戏存储目录)

### 运行编译后的程序

编译后的程序有多种运行方式：

1. **默认运行（推荐）**：
   双击 `dist/GalHub-CDN/GalHub-CDN.exe` 文件，将直接启动图形用户界面。

2. **命令行运行**：
   打开命令提示符，导航到 `dist/GalHub-CDN/` 目录，然后运行：
   ```bash
   # 启动图形界面
   GalHub-CDN.exe ui
   
   # 启动HTTP服务器
   GalHub-CDN.exe serve [--port 8000]
   
   # 查看游戏列表
   GalHub-CDN.exe list
   
   # 上传游戏
   GalHub-CDN.exe upload --name "游戏名称" --alias "游戏别名" --path "/path/to/game/files"
   
   # 删除游戏
   GalHub-CDN.exe remove --alias "游戏别名"
   
   # 初始化系统
   GalHub-CDN.exe init
   ```

### 注意事项

1. **首次运行**：
   - 首次运行编译后的程序时，会自动创建数据库和游戏目录
   - 可以将整个 `dist/GalHub-CDN/` 目录复制到其他计算机上直接运行

2. **数据存储**：
   - 游戏数据存储在 `games.db` SQLite数据库文件中
   - 游戏文件存储在 `games/` 目录中
   - 这些文件会随着程序的使用而自动创建和更新

3. **故障排除**：
   - 如果遇到DLL加载错误，请在同一版本的Windows系统上重新编译
   - 如果图形界面无法启动，请确保系统已安装完整的Tkinter支持
   - 如果链接复制功能无法使用，请在目标系统上安装pyperclip库：
     ```bash
     pip install pyperclip
     ```

## 使用方法

### 1. 图形用户界面（推荐）

```bash
python main.py ui
```

图形界面提供直观的操作方式，包括：
- 上传新游戏
- 查看游戏列表
- 删除游戏
- 启动和停止HTTP服务器
- 设置自定义域名
- 一键复制游戏访问链接

#### 域名设置

在"设置"标签页中可以配置自定义域名：
- 默认域名为`localhost`
- 可以设置为服务器的公网IP或域名
- 保存后，生成的链接将使用新设置的域名

#### 复制游戏链接

在"游戏管理"标签页中：
- 在游戏列表中选择一个游戏
- 在"链接设置"区域选择协议（HTTP或HTTPS）
- 如需要可输入端口号
- 在链接设置下方点击"复制选中游戏链接"按钮
- 如果安装了pyperclip库，链接将自动复制到剪贴板
- 如果未安装pyperclip库，会弹出窗口显示链接内容供手动复制

### 2. 命令行界面

#### 上传游戏

```bash
python main.py upload --name "游戏名称" --alias "游戏别名" --path "/path/to/game/files"
```

- `--name`: 游戏名称（用于显示）
- `--alias`: 游戏别名（将作为游戏的文件夹名和URL路径）
- `--path`: 游戏源文件路径

#### 查看游戏列表

```bash
python main.py list
```

#### 删除游戏

```bash
python main.py remove --alias "游戏别名"
```

#### 启动HTTP服务器

```bash
python main.py serve [--port 8000]
```

- `--port`: 指定服务器端口，默认为8000

访问 `http://localhost:8000/` 查看游戏列表，点击游戏名称开始游戏。

### 其他常见问题

1. **游戏无法访问**：
   - 确保服务器已启动
   - 检查域名设置是否正确
   - 确认游戏文件路径是否存在

2. **上传游戏失败**：
   - 检查游戏别名是否已存在
   - 确认源文件路径是否正确

## 数据库结构

系统使用SQLite数据库存储以下游戏信息：

- `name`: 游戏名称
- `alias`: 游戏别名（唯一，用作文件夹名）
- `upload_time`: 上传时间
- `path`: 游戏文件在服务器上的路径

系统还存储以下设置信息：
- `domain`: 用于生成访问链接的域名

## 目录结构

```
.
├── games.db              # SQLite数据库文件
├── games/                # 游戏文件存储目录
│   └── [game_alias]/     # 各个游戏的文件夹
├── main.py               # 主程序入口
├── database.py           # 数据库操作模块
├── manager.py            # 游戏管理模块
├── server.py             # HTTP服务器模块
├── ui.py                 # 图形用户界面模块
├── build.py              # 编译脚本
├── .gitignore            # Git忽略文件
└── README.md             # 说明文档
```

## 访问游戏

启动HTTP服务器后，可以通过以下URL访问游戏：

```
http://localhost:8000/[游戏别名]/
```

例如，如果游戏别名"tetris"，则访问：

```
http://localhost:8000/tetris/
```

系统会自动寻找游戏目录下的`index.html`文件作为首页。

如果设置了自定义域名，链接将变为：

```
http://yourdomain.com:8000/[游戏别名]/
```

或者不带端口（如果使用标准端口）：

```
http://yourdomain.com/[游戏别名]/
```
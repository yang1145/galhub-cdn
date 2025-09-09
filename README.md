# GalHub - 游戏CDN管理系统

一个用于管理网页游戏的CDN系统，游戏以纯静态HTML网站形式存储和提供服务。

## 功能特点

- 使用Python和SQLite开发
- 支持游戏上传、删除和列表查看
- 内置HTTP服务器提供游戏内容服务
- 图形化用户界面，操作简单直观
- 支持自定义域名和链接生成

## 系统要求

- Python 3.6+
- Windows 7/8/10/11

## 安装和初始化

1. 克隆或下载本项目
2. 安装依赖库（可选）:
   ```
   pip install pyperclip
   ```
3. 初始化系统:
   ```
   python main.py init
   ```

## 使用方法

### 命令行方式

```bash
# 启动图形界面
python main.py ui

# 上传游戏
python main.py upload --name "游戏名称" --alias "游戏别名" --path "游戏文件路径"

# 列出所有游戏
python main.py list

# 删除游戏
python main.py remove --alias "游戏别名"

# 启动HTTP服务器
python main.py serve [--port 8000]
```

### 图形界面方式

运行 `python main.py ui` 启动图形界面，通过界面操作管理游戏和服务器。

## 编译为可执行文件

### 方法一：使用编译脚本（推荐）

直接运行项目中的 `build.bat` 文件，将自动完成以下步骤：
1. 检查并安装必要的依赖（PyInstaller）
2. 使用PyInstaller编译程序
3. 复制必要文件到编译目录

或者在命令行中运行:
```
python build.py
```

### 方法二：手动编译

1. 安装PyInstaller:
   ```
   pip install pyinstaller
   ```

2. 使用spec文件编译:
   ```
   pyinstaller main.spec
   ```

编译后的程序位于 `dist/main/` 目录中。

## 运行编译后的程序

### 图形界面方式

双击 `dist/main/main.exe` 直接启动图形界面。

### 命令行方式

```bash
# 在dist/main目录中运行:
main.exe [command]

# 示例:
main.exe upload --name "游戏名称" --alias "游戏别名" --path "游戏文件路径"
main.exe list
main.exe serve --port 8000
```

## 目录结构

- `games/` - 游戏文件存储目录
- `logs/` - 服务器日志目录
- `games.db` - SQLite数据库文件
- `index.html` - 默认主页文件

## 注意事项

1. 首次运行需要执行初始化命令 `python main.py init`
2. 如需复制链接功能，请安装pyperclip库
3. 防火墙可能会阻止服务器端口访问，需要手动放行
4. 编译后的程序默认不显示控制台窗口

## 故障排除

### DLL加载错误

如果在Windows上运行编译后的程序时遇到DLL加载错误，请尝试重新运行编译脚本。

### 图形界面无法启动

确保系统已安装Tkinter支持。大多数Python发行版默认包含Tkinter。

### 链接复制功能不可用

安装pyperclip库:
```
pip install pyperclip
```

### 无法访问服务器

1. 检查服务器是否已启动
2. 确认端口号是否正确
3. 查看防火墙设置
4. 尝试命令行方式启动

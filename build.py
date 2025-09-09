#!/usr/bin/env python3
"""
GalHub - 编译脚本
用于自动化编译GalHub项目为Windows可执行文件
"""

import os
import sys
import subprocess
import shutil

def check_python():
    """检查Python环境"""
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"找到Python: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("错误: 未找到Python环境")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        print("检查PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                      check=True)
        print("PyInstaller安装完成")
        return True
    except subprocess.CalledProcessError:
        print("错误: 安装PyInstaller失败")
        return False

def create_directories():
    """创建必要的目录"""
    dirs = ["games", "logs"]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"创建目录: {dir_name}")

def copy_files():
    """复制必要文件到编译目录"""
    files_to_copy = ["README.md", "LICENSE", "index.html", "games.db"]
    
    # 如果games.db不存在，创建一个空的
    if not os.path.exists("games.db"):
        open("games.db", "w").close()
        print("创建空的数据库文件: games.db")
    
    # 复制其他文件（如果存在）
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            try:
                shutil.copy2(file_name, file_name)
                print(f"复制文件: {file_name}")
            except Exception as e:
                print(f"警告: 复制文件 {file_name} 失败: {e}")
        else:
            # 对于某些关键文件，创建空文件
            if file_name in ["README.md", "LICENSE", "index.html"]:
                open(file_name, "w").close()
                print(f"创建空文件: {file_name}")

def build_executable():
    """使用PyInstaller编译可执行文件"""
    try:
        print("开始编译...")
        # 使用spec文件进行编译
        subprocess.run([sys.executable, "-m", "PyInstaller", "main.spec"], 
                      check=True)
        print("编译完成!")
        return True
    except subprocess.CalledProcessError:
        print("错误: 编译失败")
        return False

def show_instructions():
    """显示使用说明"""
    print("\n" + "="*50)
    print("编译完成!")
    print("="*50)
    print("编译后的程序位于: dist/main/")
    print("\n运行方式:")
    print("1. 图形界面方式: 双击 dist/main/main.exe")
    print("2. 命令行方式: 在dist/main目录中运行 main.exe [命令]")
    print("\n示例命令:")
    print("  main.exe ui                 # 启动图形界面")
    print("  main.exe upload --name \"游戏名称\" --alias \"游戏别名\" --path \"游戏文件路径\"")
    print("  main.exe list               # 列出所有游戏")
    print("  main.exe serve --port 8000  # 启动HTTP服务器")
    print("="*50)

def main():
    """主函数"""
    print("GalHub - 编译脚本")
    print("="*30)
    
    # 检查Python环境
    if not check_python():
        return False
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return False
    
    # 创建必要目录
    create_directories()
    
    # 复制必要文件
    copy_files()
    
    # 编译可执行文件
    if not build_executable():
        return False
    
    # 显示使用说明
    show_instructions()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
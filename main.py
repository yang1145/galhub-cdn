#!/usr/bin/env python3
"""
GalHub - CDN控制器
A CDN program for managing web-based games as static HTML sites
"""

import os
import sys
import argparse
from database import init_db, get_all_games
from manager import upload_game, list_games, remove_game, init_manager
from server import start_server

def show_games():
    """
    显示游戏列表
    """
    games = list_games()
    
    if not games:
        print("No games available")
        return
    
    print("\nAvailable Games:")
    print("-" * 80)
    print(f"{'Name':<30} {'Alias':<20} {'Upload Time':<20}")
    print("-" * 80)
    
    for game in games:
        name, alias, upload_time = game
        print(f"{name:<30} {alias:<20} {upload_time:<20}")
    print()

def main():
    # 初始化数据库和目录
    init_manager()
    
    parser = argparse.ArgumentParser(description="GalHub - CDN控制器")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # 上传命令
    upload_parser = subparsers.add_parser('upload', help='Upload a game')
    upload_parser.add_argument('--name', required=True, help='Game name')
    upload_parser.add_argument('--alias', required=True, help='Game alias (folder name)')
    upload_parser.add_argument('--path', required=True, help='Source path of the game files')
    
    # 列表命令
    subparsers.add_parser('list', help='List all games')
    
    # 删除命令
    remove_parser = subparsers.add_parser('remove', help='Remove a game')
    remove_parser.add_argument('--alias', required=True, help='Game alias to remove')
    
    # 启动服务器命令
    server_parser = subparsers.add_parser('serve', help='Start the HTTP server')
    server_parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    
    # 初始化命令
    subparsers.add_parser('init', help='Initialize the system')
    
    # UI界面命令
    subparsers.add_parser('ui', help='Start the graphical user interface')
    
    args = parser.parse_args()
    
    if args.command == 'upload':
        upload_game(args.name, args.alias, args.path)
    elif args.command == 'list':
        show_games()
    elif args.command == 'remove':
        remove_game(args.alias)
    elif args.command == 'serve':
        start_server(args.port)
    elif args.command == 'init':
        init_manager()
    elif args.command == 'ui':
        # 启动图形界面
        try:
            from ui import main as ui_main
            ui_main()
        except ImportError as e:
            print(f"Error importing UI module: {e}")
            print("Make sure all required modules are installed")
    else:
        # 默认显示帮助信息
        # 修复PyInstaller打包后的帮助信息显示问题
        try:
            parser.print_help()
        except AttributeError:
            # 当stdout不可用时，使用print函数
            print("GalHub - CDN控制器")
            print("Available commands:")
            print("  upload    Upload a game")
            print("  list      List all games")
            print("  remove    Remove a game")
            print("  serve     Start the HTTP server")
            print("  init      Initialize the system")
            print("  ui        Start the graphical user interface")
        print("\nAvailable games:")
        show_games()

# 添加一个专门用于启动UI的函数
def ui_main():
    """启动UI界面的专用函数"""
    try:
        from ui import main as ui_main_func
        ui_main_func()
    except ImportError as e:
        print(f"Error importing UI module: {e}")
        print("Make sure all required modules are installed")

if __name__ == "__main__":
    main()
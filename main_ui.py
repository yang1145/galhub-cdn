#!/usr/bin/env python3
"""
GalHub - CDN控制器 (UI默认入口)
A CDN program for managing web-based games as static HTML sites
"""

import os
import sys

def main():
    # 如果没有提供命令行参数，则默认启动UI界面
    if len(sys.argv) == 1:
        # 直接调用main.py中的ui功能
        from main import ui_main
        ui_main()
    else:
        # 有参数时，使用main.py的原始逻辑
        from main import main as main_main
        main_main()

if __name__ == "__main__":
    main()
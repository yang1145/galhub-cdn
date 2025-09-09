import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from database import init_db, get_all_games, get_domain, set_domain
from manager import upload_game, remove_game, init_manager, get_game_url, update_domain
from server import start_server, stop_server, get_server_logs
import threading
import time

# 尝试导入pyperclip，如果失败则设置为None
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    pyperclip = None
    PYPERCLIP_AVAILABLE = False

class GameCDNUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GalHub - CDN控制器")
        self.root.geometry("900x700")
        
        # 服务器相关变量
        self.server_thread = None
        self.log_update_job = None
        
        # 初始化数据库
        init_manager()
        
        # 创建界面
        self.create_widgets()
        
        # 刷新游戏列表
        self.refresh_game_list()
        
        # 加载域名设置
        self.load_domain_settings()
    
    def create_widgets(self):
        # 创建标签页
        tab_control = ttk.Notebook(self.root)
        
        # 游戏管理标签页
        self.manage_tab = ttk.Frame(tab_control)
        tab_control.add(self.manage_tab, text="游戏管理")
        
        # 服务器控制标签页
        self.server_tab = ttk.Frame(tab_control)
        tab_control.add(self.server_tab, text="服务器控制")
        
        # 设置标签页
        self.settings_tab = ttk.Frame(tab_control)
        tab_control.add(self.settings_tab, text="设置")
        
        # 关于标签页
        self.about_tab = ttk.Frame(tab_control)
        tab_control.add(self.about_tab, text="关于")
        
        tab_control.pack(expand=1, fill="both")
        
        # 游戏管理标签页内容
        self.create_manage_tab()
        
        # 服务器控制标签页内容
        self.create_server_tab()
        
        # 设置标签页内容
        self.create_settings_tab()
        
        # 关于标签页内容
        self.create_about_tab()
    
    def create_manage_tab(self):
        # 上传游戏区域
        upload_frame = ttk.LabelFrame(self.manage_tab, text="上传新游戏", padding="10")
        upload_frame.pack(fill="x", padx=10, pady=10)
        
        # 游戏名称
        ttk.Label(upload_frame, text="游戏名称:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_entry = ttk.Entry(upload_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # 游戏别名
        ttk.Label(upload_frame, text="游戏别名:").grid(row=1, column=0, sticky="w", pady=2)
        self.alias_entry = ttk.Entry(upload_frame, width=30)
        self.alias_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # 源文件路径
        ttk.Label(upload_frame, text="源文件路径:").grid(row=2, column=0, sticky="w", pady=2)
        self.path_entry = ttk.Entry(upload_frame, width=30)
        self.path_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # 浏览按钮
        browse_button = ttk.Button(upload_frame, text="浏览", command=self.browse_folder)
        browse_button.grid(row=2, column=2, padx=(10, 0), pady=2)
        
        # 上传按钮
        upload_button = ttk.Button(upload_frame, text="上传游戏", command=self.upload_game)
        upload_button.grid(row=3, column=1, pady=10)
        
        upload_frame.columnconfigure(1, weight=1)
        
        # 游戏列表区域
        list_frame = ttk.LabelFrame(self.manage_tab, text="游戏列表", padding="10")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 创建Treeview来显示游戏列表
        columns = ("alias", "name", "upload_time")
        self.game_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 定义列标题（调整列顺序，将游戏名称放在游戏别名之后）
        self.game_tree.heading("alias", text="游戏别名")
        self.game_tree.heading("name", text="游戏名称")
        self.game_tree.heading("upload_time", text="上传时间")
        
        # 设置列宽
        self.game_tree.column("alias", width=150)
        self.game_tree.column("name", width=200)
        self.game_tree.column("upload_time", width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.game_tree.yview)
        self.game_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.game_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 操作区域
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # 链接设置区域
        link_settings_frame = ttk.LabelFrame(button_frame, text="链接设置", padding="5")
        link_settings_frame.pack(fill="x", pady=(0, 10))
        
        # 协议选择
        protocol_frame = ttk.Frame(link_settings_frame)
        protocol_frame.pack(anchor="w", pady=(0, 5))
        
        ttk.Label(protocol_frame, text="协议:").pack(side="left")
        self.protocol_var = tk.StringVar(value="http")
        protocol_http = ttk.Radiobutton(protocol_frame, text="HTTP", variable=self.protocol_var, value="http")
        protocol_https = ttk.Radiobutton(protocol_frame, text="HTTPS", variable=self.protocol_var, value="https")
        protocol_http.pack(side="left", padx=(5, 0))
        protocol_https.pack(side="left", padx=(5, 0))
        
        # 端口设置
        port_frame = ttk.Frame(link_settings_frame)
        port_frame.pack(anchor="w")
        
        ttk.Label(port_frame, text="端口:").pack(side="left")
        self.port_var = tk.StringVar()
        port_entry = ttk.Entry(port_frame, textvariable=self.port_var, width=8)
        port_entry.pack(side="left", padx=(5, 0))
        
        # 如果pyperclip不可用，显示提示信息
        if not PYPERCLIP_AVAILABLE:
            ttk.Label(link_settings_frame, text="(需要安装pyperclip库)", foreground="red").pack(anchor="w", pady=(5, 0))
        
        # 按钮区域（竖向排列）
        buttons_frame = ttk.Frame(button_frame)
        buttons_frame.pack(fill="x")
        
        refresh_button = ttk.Button(buttons_frame, text="刷新列表", command=self.refresh_game_list)
        refresh_button.pack(fill="x", pady=(0, 5))
        
        delete_button = ttk.Button(buttons_frame, text="删除选中游戏", command=self.delete_game)
        delete_button.pack(fill="x", pady=(0, 5))
        
        copy_link_button = ttk.Button(buttons_frame, text="复制选中游戏链接", command=self.copy_game_link)
        copy_link_button.pack(fill="x")
    
    def create_server_tab(self):
        # 服务器控制区域
        server_frame = ttk.LabelFrame(self.server_tab, text="服务器控制", padding="10")
        server_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 端口设置
        port_frame = ttk.Frame(server_frame)
        port_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(port_frame, text="端口:").pack(side="left")
        self.port_entry = ttk.Entry(port_frame, width=10)
        self.port_entry.insert(0, "8000")
        self.port_entry.pack(side="left", padx=(10, 0))
        
        # 服务器状态
        self.server_status = ttk.Label(server_frame, text="服务器状态: 未运行", foreground="red")
        self.server_status.pack(anchor="w", pady=(0, 20))
        
        # 控制按钮
        button_frame = ttk.Frame(server_frame)
        button_frame.pack()
        
        self.start_button = ttk.Button(button_frame, text="启动服务器", command=self.start_server)
        self.start_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="停止服务器", state="disabled", command=self.stop_server)
        self.stop_button.pack(side="left")
        
        # 访问地址提示
        ttk.Label(server_frame, text="启动服务器后，可通过以下地址访问:").pack(anchor="w", pady=(30, 5))
        self.url_label = ttk.Label(server_frame, text="http://localhost:8000", foreground="blue")
        self.url_label.pack(anchor="w")
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(self.server_tab, text="服务器日志", padding="10")
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建日志文本框和滚动条
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill="both", expand=True)
        
        self.log_text = tk.Text(log_text_frame, height=10, state="disabled")
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        # 清空日志按钮
        clear_log_button = ttk.Button(log_frame, text="清空日志", command=self.clear_logs)
        clear_log_button.pack(anchor="e", pady=(10, 0))
    
    def create_settings_tab(self):
        # 设置区域
        settings_frame = ttk.LabelFrame(self.settings_tab, text="系统设置", padding="10")
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 域名设置
        domain_frame = ttk.Frame(settings_frame)
        domain_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(domain_frame, text="域名设置:").pack(anchor="w")
        ttk.Label(domain_frame, text="用于生成游戏访问链接的域名", foreground="gray").pack(anchor="w")
        
        domain_input_frame = ttk.Frame(domain_frame)
        domain_input_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(domain_input_frame, text="域名:").pack(side="left")
        self.domain_entry = ttk.Entry(domain_input_frame, width=30)
        self.domain_entry.pack(side="left", padx=(10, 10), fill="x", expand=True)
        save_domain_button = ttk.Button(domain_input_frame, text="保存", command=self.save_domain)
        save_domain_button.pack(side="left")
        
        # 当前域名显示
        self.current_domain_label = ttk.Label(domain_frame, text="当前域名: localhost")
        self.current_domain_label.pack(anchor="w", pady=(10, 0))
        
        # 使用说明
        ttk.Label(settings_frame, text="说明:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(20, 5))
        instructions = [
            "1. 域名设置用于生成游戏的访问链接",
            "2. 如果使用默认设置(localhost)，只能在本机访问",
            "3. 如果要外网访问，请设置为服务器的公网IP或域名",
            "4. 保存后，复制链接功能将使用新设置的域名"
        ]
        
        for instruction in instructions:
            ttk.Label(settings_frame, text=instruction, font=("Arial", 9)).pack(anchor="w")
    
    def create_about_tab(self):
        # 关于信息
        about_frame = ttk.Frame(self.about_tab, padding="20")
        about_frame.pack(fill="both", expand=True)
        
        ttk.Label(about_frame, text="GalHub - 游戏CDN管理系统", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        ttk.Label(about_frame, text="版本: 1.0.0", font=("Arial", 12)).pack(pady=(0, 10))
        ttk.Label(about_frame, text="一个用于管理网页游戏的CDN系统", font=("Arial", 12)).pack(pady=(0, 10))
        ttk.Label(about_frame, text="游戏以纯静态HTML网站形式存储和提供服务", font=("Arial", 12)).pack(pady=(0, 20))
        
        # 功能特点
        ttk.Label(about_frame, text="功能特点:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        features = [
            "• 使用Python和SQLite开发",
            "• 支持游戏上传、删除和列表查看",
            "• 内置HTTP服务器提供游戏内容服务",
            "• 图形化用户界面，操作简单直观",
            "• 支持自定义域名和链接生成"
        ]
        
        for feature in features:
            ttk.Label(about_frame, text=feature, font=("Arial", 10)).pack(anchor="w")
        
        # pyperclip提示
        if not PYPERCLIP_AVAILABLE:
            ttk.Label(about_frame, text="注意: 未安装pyperclip库，无法自动复制链接到剪贴板", 
                     foreground="red", font=("Arial", 10)).pack(anchor="w", pady=(20, 0))
            ttk.Label(about_frame, text="请运行 'pip install pyperclip' 安装", 
                     foreground="red", font=("Arial", 10)).pack(anchor="w")
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_path)
    
    def upload_game(self):
        name = self.name_entry.get().strip()
        alias = self.alias_entry.get().strip()
        path = self.path_entry.get().strip()
        
        # 验证输入
        if not name:
            messagebox.showerror("错误", "请输入游戏名称")
            return
        
        if not alias:
            messagebox.showerror("错误", "请输入游戏别名")
            return
        
        if not path:
            messagebox.showerror("错误", "请选择游戏源文件路径")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("错误", "指定的路径不存在")
            return
        
        # 上传游戏
        success = upload_game(name, alias, path)
        
        if success:
            messagebox.showinfo("成功", f"游戏 '{name}' 上传成功")
            # 清空输入框
            self.name_entry.delete(0, tk.END)
            self.alias_entry.delete(0, tk.END)
            self.path_entry.delete(0, tk.END)
            # 刷新游戏列表
            self.refresh_game_list()
        else:
            messagebox.showerror("错误", "游戏上传失败，请检查是否已存在同名别名的游戏")
    
    def refresh_game_list(self):
        # 清空现有列表
        for item in self.game_tree.get_children():
            self.game_tree.delete(item)
        
        # 获取游戏列表并添加到Treeview
        games = get_all_games()
        for game in games:
            self.game_tree.insert("", "end", values=game)
    
    def delete_game(self):
        # 获取选中的游戏
        selected = self.game_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的游戏")
            return
        
        # 获取选中游戏的别名
        item = self.game_tree.item(selected[0])
        alias = item["values"][0]  # 游戏别名在第一列
        name = item["values"][1]   # 游戏名称在第二列
        
        # 确认删除
        result = messagebox.askyesno("确认删除", f"确定要删除游戏 '{name}' 吗？此操作不可撤销。")
        if result:
            success = remove_game(alias)
            if success:
                messagebox.showinfo("成功", f"游戏 '{name}' 已删除")
                self.refresh_game_list()
            else:
                messagebox.showerror("错误", "删除游戏失败")
    
    def copy_game_link(self):
        # 获取选中的游戏
        selected = self.game_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择游戏")
            return
        
        # 获取选中游戏的别名
        item = self.game_tree.item(selected[0])
        alias = item["values"][0]  # 游戏别名在第一列
        
        # 获取协议和端口设置
        protocol = self.protocol_var.get()
        port_str = self.port_var.get()
        port = None
        if port_str:
            try:
                port = int(port_str)
            except ValueError:
                messagebox.showerror("错误", "端口号必须是数字")
                return
        
        # 生成链接
        try:
            url = get_game_url(alias, protocol, port)
        except Exception as e:
            messagebox.showerror("错误", f"生成链接时出错: {str(e)}")
            return
        
        # 复制到剪贴板
        if PYPERCLIP_AVAILABLE:
            try:
                pyperclip.copy(url)
                messagebox.showinfo("成功", f"链接已复制到剪贴板:\n{url}")
            except Exception as e:
                messagebox.showinfo("链接", f"请手动复制以下链接:\n{url}\n\n错误信息: {str(e)}")
        else:
            # 如果pyperclip不可用，显示链接让用户手动复制
            messagebox.showinfo("链接", f"请手动复制以下链接:\n{url}\n\n提示：安装pyperclip库可自动复制到剪贴板")
    
    def start_server(self):
        try:
            port = int(self.port_entry.get())
        except ValueError:
            messagebox.showerror("错误", "端口号必须是数字")
            return
        
        # 在后台线程中启动服务器
        self.server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
        self.server_thread.start()
        
        # 更新UI
        self.server_status.config(text=f"服务器状态: 运行中 (端口: {port})", foreground="green")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.url_label.config(text=f"http://localhost:{port}")
        
        # 开始更新日志
        self.update_logs()
        
        messagebox.showinfo("服务器启动", f"服务器已在端口 {port} 上启动")
    
    def stop_server(self):
        # 停止服务器
        success = stop_server()
        
        # 更新UI
        self.server_status.config(text="服务器状态: 已停止", foreground="red")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        # 停止日志更新
        if self.log_update_job:
            self.root.after_cancel(self.log_update_job)
            self.log_update_job = None
        
        if success:
            messagebox.showinfo("服务器停止", "服务器已停止")
        else:
            messagebox.showinfo("服务器停止", "已请求停止服务器。注意：程序仍在后台运行，需要完全停止请关闭整个应用程序。")
    
    def update_logs(self):
        """更新日志显示"""
        try:
            logs = get_server_logs()
            if logs:
                self.log_text.config(state="normal")
                self.log_text.delete(1.0, tk.END)
                for log in logs:
                    self.log_text.insert(tk.END, log + "\n")
                self.log_text.config(state="disabled")
                # 滚动到底部
                self.log_text.see(tk.END)
        except Exception as e:
            print(f"Error updating logs: {e}")
        
        # 每秒更新一次日志
        if self.server_thread and self.server_thread.is_alive():
            self.log_update_job = self.root.after(1000, self.update_logs)
    
    def clear_logs(self):
        """清空日志显示"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
    
    def load_domain_settings(self):
        """加载域名设置"""
        domain = get_domain()
        self.domain_entry.delete(0, tk.END)
        self.domain_entry.insert(0, domain)
        self.current_domain_label.config(text=f"当前域名: {domain}")
    
    def save_domain(self):
        """保存域名设置"""
        domain = self.domain_entry.get().strip()
        if not domain:
            messagebox.showerror("错误", "请输入有效的域名")
            return
        
        update_domain(domain)
        self.current_domain_label.config(text=f"当前域名: {domain}")
        messagebox.showinfo("成功", "域名设置已保存")

def main():
    root = tk.Tk()
    app = GameCDNUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
import http.server
import socketserver
import urllib.parse
import os
import mimetypes
import json
import sys
import threading
from datetime import datetime
from database import get_game_by_alias, get_all_games

# 默认端口
PORT = 8000
# 游戏文件根目录
GAMES_ROOT = "games"
# 日志目录
LOGS_DIR = "logs"

# 全局变量用于存储服务器实例和日志
server_instance = None
server_logs = []
log_lock = threading.Lock()

# 检查是否在PyInstaller打包环境中运行
def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包环境
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境
    return os.path.join(os.path.abspath("."), relative_path)

def setup_log_directory():
    """创建日志目录"""
    os.makedirs(LOGS_DIR, exist_ok=True)

def get_log_filename():
    """获取当前日期的日志文件名"""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOGS_DIR, f"server_{today}.log")

def log_message(message):
    """记录日志消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    with log_lock:
        server_logs.append(log_entry)
        # 限制日志数量，只保留最近的1000条
        if len(server_logs) > 1000:
            server_logs.pop(0)
        
        # 保存日志到文件
        try:
            setup_log_directory()
            log_file = get_log_filename()
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            # 如果无法写入文件，至少打印到控制台
            print(f"Failed to write to log file: {e}")
    
    # 同时打印到控制台
    print(log_entry)

def get_server_logs():
    """获取服务器日志"""
    with log_lock:
        return list(server_logs)

class GameRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        """重写日志消息方法，使用我们自定义的日志记录"""
        log_message(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        # 解析请求路径
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/', 1)
        
        # 记录请求
        log_message(f"GET {self.path} from {self.address_string()}")
        
        # 如果请求根路径，显示默认主页
        if parsed_path.path == '/' or parsed_path.path == '':
            # 检查是否存在index.html文件
            index_path = get_resource_path('index.html')
            if os.path.exists(index_path):
                self.serve_file(index_path)
            else:
                self.send_game_list()
            return
            
        # 如果请求API获取游戏列表
        if parsed_path.path == '/api/games':
            self.send_game_list_api()
            return
        
        # 如果请求游戏，提供游戏内容
        if len(path_parts) >= 1 and path_parts[0]:
            game_alias = path_parts[0]
            game = get_game_by_alias(game_alias)
            
            if game:
                # 构建文件路径
                remaining_path = path_parts[1] if len(path_parts) > 1 else 'index.html'
                if not remaining_path:
                    remaining_path = 'index.html'
                
                file_path = os.path.join(GAMES_ROOT, game_alias, remaining_path)
                
                # 检查文件是否存在
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    self.serve_file(file_path)
                    return
                else:
                    # 尝试添加index.html
                    if not remaining_path.endswith('/') and not '.' in remaining_path.split('/')[-1]:
                        index_path = os.path.join(file_path, 'index.html')
                        if os.path.exists(index_path):
                            self.serve_file(index_path)
                            return
            
            # 游戏未找到
            log_message(f"404 Not Found: {self.path}")
            self.send_error(404, "Game or file not found")
            return
        
        # 其他情况返回404
        log_message(f"404 Not Found: {self.path}")
        self.send_error(404, "Not found")
    
    def send_game_list_api(self):
        """
        发送游戏列表API响应
        """
        games = get_all_games()
        
        # 转换为字典列表
        games_data = []
        for game in games:
            games_data.append({
                'name': game[0],
                'alias': game[1],
                'upload_time': game[2]
            })
        
        response = {
            'games': games_data
        }
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def send_game_list(self):
        """
        发送游戏列表页面
        """
        games = get_all_games()
        
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Game CDN Platform</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                .game-list { margin-top: 20px; }
                .game-item { 
                    border: 1px solid #ddd; 
                    margin: 10px 0; 
                    padding: 15px; 
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }
                .game-name { font-size: 1.2em; font-weight: bold; }
                .game-alias { color: #666; }
                .game-time { color: #999; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <h1>Available Games</h1>
            <div class="game-list">
        '''
        
        if games:
            for game in games:
                name, alias, upload_time = game
                html += f'''
                <div class="game-item">
                    <div class="game-name"><a href="/{alias}/">{name}</a></div>
                    <div class="game-alias">Alias: {alias}</div>
                    <div class="game-time">Uploaded: {upload_time}</div>
                </div>
                '''
        else:
            html += '<p>No games available yet.</p>'
        
        html += '''
            </div>
        </body>
        </html>
        '''
        
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_file(self, file_path):
        """
        提供文件内容服务
        """
        try:
            # 确定文件MIME类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            # 读取文件内容
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 发送响应
            self.send_response(200)
            self.send_header("Content-type", mime_type)
            self.end_headers()
            self.wfile.write(content)
            
            log_message(f"200 OK: {self.path} ({mime_type})")
        except Exception as e:
            log_message(f"500 Internal Server Error: {self.path} - {str(e)}")
            self.send_error(500, f"Error serving file: {str(e)}")

class StoppableHTTPServer(socketserver.TCPServer):
    """可停止的HTTP服务器"""
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.running = True

def start_server(port=PORT):
    """
    启动HTTP服务器
    
    Args:
        port (int): 服务器端口，默认8000
    """
    global server_instance
    
    # 确保游戏目录存在
    os.makedirs(GAMES_ROOT, exist_ok=True)
    
    # 创建服务器实例
    server_instance = StoppableHTTPServer(("", port), GameRequestHandler)
    
    log_message(f"Game CDN server starting at http://localhost:{port}/")
    
    try:
        while server_instance.running:
            server_instance.handle_request()
    except Exception as e:
        log_message(f"Server error: {str(e)}")
    
    log_message("Server stopped")

def stop_server():
    """停止服务器"""
    global server_instance
    
    if server_instance:
        server_instance.running = False
        log_message("Server stop requested")
        return True
    return False
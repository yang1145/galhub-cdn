import http.server
import socketserver
import urllib.parse
import os
import mimetypes
from database import get_game_by_alias, get_all_games

# 默认端口
PORT = 8000
# 游戏文件根目录
GAMES_ROOT = "games"

class GameRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 解析请求路径
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/', 1)
        
        # 如果请求根路径，显示游戏列表
        if parsed_path.path == '/' or parsed_path.path == '':
            self.send_game_list()
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
            self.send_error(404, "Game or file not found")
            return
        
        # 其他情况返回404
        self.send_error(404, "Not found")
    
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
        except Exception as e:
            self.send_error(500, f"Error serving file: {str(e)}")

def start_server(port=PORT):
    """
    启动HTTP服务器
    
    Args:
        port (int): 服务器端口，默认8000
    """
    # 确保游戏目录存在
    os.makedirs(GAMES_ROOT, exist_ok=True)
    
    with socketserver.TCPServer(("", port), GameRequestHandler) as httpd:
        print(f"Game CDN server running at http://localhost:{port}/")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
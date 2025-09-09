import os
import shutil
from database import add_game, get_all_games, delete_game, init_db, get_domain, set_domain
from datetime import datetime

# 游戏文件根目录
GAMES_ROOT = "games"

def upload_game(name, alias, source_path):
    """
    上传游戏到CDN
    
    Args:
        name (str): 游戏名
        alias (str): 游戏别名（将作为文件夹名）
        source_path (str): 源文件路径
    
    Returns:
        bool: 上传成功返回True，否则返回False
    """
    # 确保games目录存在
    os.makedirs(GAMES_ROOT, exist_ok=True)
    
    # 检查源路径是否存在
    if not os.path.exists(source_path):
        print(f"Error: Source path {source_path} does not exist")
        return False
    
    # 目标路径
    target_path = os.path.join(GAMES_ROOT, alias)
    
    # 检查是否已存在同名游戏
    if os.path.exists(target_path):
        print(f"Error: Game with alias '{alias}' already exists")
        return False
    
    try:
        # 复制游戏文件
        if os.path.isfile(source_path):
            # 如果是单个文件，创建目录并将文件复制进去
            os.makedirs(target_path, exist_ok=True)
            shutil.copy2(source_path, os.path.join(target_path, os.path.basename(source_path)))
        else:
            # 如果是目录，直接复制整个目录
            shutil.copytree(source_path, target_path)
        
        # 添加到数据库
        if add_game(name, alias, target_path):
            print(f"Game '{name}' uploaded successfully with alias '{alias}'")
            return True
        else:
            # 如果数据库添加失败，清理已复制的文件
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            print(f"Error: Failed to add game to database")
            return False
            
    except Exception as e:
        # 清理已复制的文件
        if os.path.exists(target_path):
            if os.path.isfile(target_path):
                os.remove(target_path)
            else:
                shutil.rmtree(target_path)
        print(f"Error uploading game: {str(e)}")
        return False

def list_games():
    """
    列出所有游戏
    
    Returns:
        list: 游戏信息列表
    """
    return get_all_games()

def remove_game(alias):
    """
    删除游戏
    
    Args:
        alias (str): 游戏别名
    
    Returns:
        bool: 删除成功返回True，否则返回False
    """
    # 获取游戏信息
    game_path = os.path.join(GAMES_ROOT, alias)
    
    # 从数据库删除
    db_success = delete_game(alias)
    
    # 从文件系统删除
    fs_success = False
    if os.path.exists(game_path):
        try:
            if os.path.isfile(game_path):
                os.remove(game_path)
            else:
                shutil.rmtree(game_path)
            fs_success = True
        except Exception as e:
            print(f"Error removing game files: {str(e)}")
    
    if db_success:
        print(f"Game '{alias}' removed from database")
    
    if fs_success:
        print(f"Game files for '{alias}' removed from filesystem")
    
    return db_success or fs_success

def init_manager():
    """
    初始化管理器
    """
    # 初始化数据库
    init_db()
    # 确保游戏目录存在
    os.makedirs(GAMES_ROOT, exist_ok=True)
    print("Manager initialized successfully")

def get_game_url(alias, protocol='http', port=None):
    """
    获取游戏访问链接
    
    Args:
        alias (str): 游戏别名
        protocol (str): 协议，'http' 或 'https'
        port (int): 端口号，如果为None则不显示端口
    
    Returns:
        str: 游戏访问链接
    """
    # 验证参数
    if not alias:
        raise ValueError("游戏别名不能为空")
    
    if protocol not in ['http', 'https']:
        raise ValueError("协议必须是 'http' 或 'https'")
    
    domain = get_domain()
    
    if port:
        return f"{protocol}://{domain}:{port}/{alias}/"
    else:
        return f"{protocol}://{domain}/{alias}/"

def update_domain(domain):
    """
    更新域名设置
    
    Args:
        domain (str): 新域名
    """
    set_domain(domain)
    print(f"Domain updated to: {domain}")
import sqlite3
from datetime import datetime
import os

# 数据库文件路径
DB_PATH = 'games.db'

def init_db():
    """
    初始化数据库，创建游戏信息表
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建游戏信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            alias TEXT NOT NULL UNIQUE,
            upload_time TIMESTAMP NOT NULL,
            path TEXT NOT NULL
        )
    ''')
    
    # 创建设置表，用于存储域名等设置
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # 插入默认域名设置
    cursor.execute('''
        INSERT OR IGNORE INTO settings (key, value) 
        VALUES ('domain', 'localhost')
    ''')
    
    conn.commit()
    conn.close()

def add_game(name, alias, path):
    """
    添加游戏到数据库
    
    Args:
        name (str): 游戏名
        alias (str): 游戏别名（文件夹名）
        path (str): 游戏文件路径
    
    Returns:
        bool: 添加成功返回True，否则返回False
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO games (name, alias, upload_time, path)
            VALUES (?, ?, ?, ?)
        ''', (name, alias, datetime.now(), path))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # 别名重复
        return False
    except Exception:
        return False

def get_all_games():
    """
    获取所有游戏信息
    
    Returns:
        list: 游戏信息列表
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 修改查询顺序以匹配UI显示顺序：alias, name, upload_time
    cursor.execute('SELECT alias, name, upload_time FROM games ORDER BY upload_time DESC')
    games = cursor.fetchall()
    
    conn.close()
    return games

def get_game_by_alias(alias):
    """
    根据别名获取游戏信息
    
    Args:
        alias (str): 游戏别名
    
    Returns:
        dict: 游戏信息或None
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT name, alias, upload_time, path FROM games WHERE alias = ?', (alias,))
    game = cursor.fetchone()
    
    conn.close()
    
    if game:
        return {
            'name': game[0],
            'alias': game[1],
            'upload_time': game[2],
            'path': game[3]
        }
    return None

def delete_game(alias):
    """
    根据别名删除游戏
    
    Args:
        alias (str): 游戏别名
    
    Returns:
        bool: 删除成功返回True，否则返回False
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM games WHERE alias = ?', (alias,))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    except Exception:
        return False

def get_domain():
    """
    获取当前设置的域名
    
    Returns:
        str: 域名
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('domain',))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    return 'localhost'

def set_domain(domain):
    """
    设置域名
    
    Args:
        domain (str): 新域名
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('domain', domain))
    
    conn.commit()
    conn.close()
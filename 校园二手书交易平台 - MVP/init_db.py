"""
数据库初始化脚本
首次运行时创建数据表，可独立执行或在 app 启动时自动调用。
"""

import os
import sys

# 将项目根目录加入路径，以便直接运行本脚本时能正确导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import init_db

if __name__ == "__main__":
    init_db()
    print("数据库初始化完成。")

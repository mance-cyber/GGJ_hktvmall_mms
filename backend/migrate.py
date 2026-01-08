#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
數據庫遷移腳本
用於手動運行數據庫遷移
"""

import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from alembic.config import Config
    from alembic import command

    # 讀取 alembic.ini 配置
    alembic_cfg = Config("alembic.ini")

    print("開始運行數據庫遷移...")
    command.upgrade(alembic_cfg, "head")
    print("✓ 數據庫遷移完成")

except Exception as e:
    print(f"✗ 數據庫遷移失敗: {e}")
    sys.exit(1)

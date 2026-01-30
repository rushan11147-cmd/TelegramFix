#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для сброса базы данных (удаление всех пользователей)
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

USE_POSTGRES = DATABASE_URL is not None

def reset_database():
    """Удаляет всех пользователей из базы данных"""
    
    if USE_POSTGRES:
        # PostgreSQL
        import psycopg2
        print("🔄 Подключение к PostgreSQL...")
        
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # Удаляем всех пользователей
            cursor.execute('DELETE FROM users')
            deleted_count = cursor.rowcount
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Удалено пользователей: {deleted_count}")
            print("✅ База данных PostgreSQL сброшена!")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            sys.exit(1)
    else:
        # SQLite
        import sqlite3
        DB_PATH = os.getenv('DATABASE_PATH', 'game_data.db')
        
        print(f"🔄 Подключение к SQLite ({DB_PATH})...")
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Удаляем всех пользователей
            cursor.execute('DELETE FROM users')
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"✅ Удалено пользователей: {deleted_count}")
            print("✅ База данных SQLite сброшена!")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            sys.exit(1)

if __name__ == '__main__':
    print("⚠️  ВНИМАНИЕ! Это удалит ВСЕХ пользователей из базы данных!")
    print("⚠️  Все игроки начнут игру заново!")
    print()
    
    response = input("Продолжить? (yes/no): ")
    
    if response.lower() in ['yes', 'y', 'да', 'д']:
        reset_database()
    else:
        print("❌ Отменено")
        sys.exit(0)

#!/usr/bin/env python3
"""
Скрипт для автоматической миграции кода от users_data кэша к прямой работе с БД
"""

import re

def migrate_function(content):
    """Мигрирует функцию от users_data к get_user_data/update_user_data"""
    
    # Заменяем проверки существования пользователя
    content = re.sub(
        r'if user_id not in users_data:',
        r'user = get_user_data(user_id)\n    if not user:',
        content
    )
    
    # Заменяем получение пользователя
    content = re.sub(
        r'user = users_data\[user_id\]',
        r'user = get_user_data(user_id)',
        content
    )
    
    # Заменяем сохранение
    content = re.sub(
        r'save_user_data\(user_id, users_data\[user_id\]\)',
        r'update_user_data(user_id, user)',
        content
    )
    
    # Заменяем прямое обращение к users_data[user_id]
    content = re.sub(
        r'users_data\[user_id\]\[',
        r'user[',
        content
    )
    
    return content

print("Этот скрипт нужно запустить вручную для миграции")
print("Или можно сделать массовую замену в редакторе")

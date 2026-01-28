#!/usr/bin/env python3
"""
Скрипт для автоматической миграции app.py
Заменяет все users_data[user_id] на get_user_data_safe(user_id)
"""

import re

# Читаем файл
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Замены
replacements = [
    # users_data[user_id] -> user (в начале функции)
    (r"if user_id not in users_data:\s+return jsonify\(\{\"error\": \"User not found\"\}\), 404\s+user = users_data\[user_id\]",
     "user = get_user_data_safe(user_id)\n    if not user:\n        return jsonify({\"error\": \"Invalid user_id\"}), 400"),
    
    # save_user_data(user_id, users_data[user_id]) -> save_user_data_safe(user_id, user)
    (r"save_user_data\(user_id, users_data\[user_id\]\)",
     "save_user_data_safe(user_id, user)"),
    
    # Удаляем cache_lock usage
    (r"with cache_lock:\s+if user_id in users_data:\s+del users_data\[user_id\]",
     "# Cache removed - data always from DB"),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Сохраняем
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Migration completed!")
print("Please review the changes manually")

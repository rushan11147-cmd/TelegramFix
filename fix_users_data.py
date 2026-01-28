#!/usr/bin/env python3
"""Автоматическое исправление всех users_data в app.py"""

import re

# Читаем файл
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Замена 1: if user_id not in users_data -> user = get_user_data_safe(user_id)
pattern1 = r'if user_id not in users_data:\s+return jsonify\(\{"error": "User not found"\}\), 404\s+user = users_data\[user_id\]'
replacement1 = '''user = get_user_data_safe(user_id)
    if not user:
        return jsonify({"error": "Invalid user_id"}), 400'''

content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)

# Замена 2: save_user_data(user_id, user) -> save_user_data_safe(user_id, user)
content = content.replace('save_user_data(user_id, user)', 'save_user_data_safe(user_id, user)')

# Сохраняем
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Исправлено!")
print("Проверьте app.py и закоммитьте изменения")

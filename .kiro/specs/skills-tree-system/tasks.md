# Implementation Plan: Skills Tree System

## Overview

Реализация системы навыков с древом развития для игры "Survive Until Payday". Система включает редкую экономику звезд (3 звезды/месяц + достижения), 5 веток навыков с 10 уровнями, интеграцию со всеми игровыми системами, и property-based тестирование.

## Tasks

- [x] 1. Создать конфигурацию и модели данных
  - Создать `skills_config.py` с конфигурацией древа навыков
  - Определить все 5 веток навыков (Luck, Charisma, Intelligence, Endurance, Business)
  - Создать dataclass модели: SkillNode, SkillData
  - Определить константы экономики звезд (MONTHLY_STARS, WEALTH_TIER_STARS, и т.д.)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 5.2, 5.3, 5.4_

- [x] 2. Реализовать SkillRepository (персистентность)
  - [x] 2.1 Создать `skills_repository.py` с классом SkillRepository
    - Реализовать `load_skill_data()` с инициализацией defaults
    - Реализовать `save_skill_data()` с валидацией
    - Реализовать `save_star_history()` и `get_star_history()`
    - Добавить валидацию и repair corrupted data
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 2.2 Написать property test для persistence round trip
    - **Property 10: Skill Data Persistence Round Trip**
    - **Validates: Requirements 3.5, 9.1, 9.2**
  
  - [x] 2.3 Написать unit tests для data initialization и repair
    - Тест инициализации defaults для нового игрока
    - Тест repair corrupted data (invalid levels, negative stars)
    - Тест backward compatibility с старым форматом
    - _Requirements: 9.3, 9.4, 9.5_

- [x] 3. Реализовать StarEconomyManager
  - [x] 3.1 Создать `star_economy.py` с классом StarEconomyManager
    - Реализовать `award_monthly_stars()` с проверкой 30-дневного цикла
    - Реализовать `award_wealth_tier_stars()` с защитой от дубликатов
    - Реализовать `award_achievement_stars()` с tracking claimed achievements
    - Реализовать `check_milestone_stars()` для 1M earned и 100 days
    - Реализовать `track_star_source()` для истории
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 10.1, 10.4_
  
  - [x] 3.2 Написать property test для monthly star awards
    - **Property 1: Monthly Star Award Consistency**
    - **Validates: Requirements 1.1**
  
  - [x] 3.3 Написать property test для milestone awards
    - **Property 4: Milestone Star Awards**
    - **Validates: Requirements 1.4, 1.5**
  
  - [x] 3.4 Написать unit tests для star sources
    - Тест wealth tier award (Property 2)
    - Тест achievement award (Property 3)
    - Тест routine action exclusion (Property 5)
    - Тест duplicate prevention
    - _Requirements: 1.2, 1.3, 1.6_

- [x] 4. Реализовать SkillManager
  - [x] 4.1 Создать `skill_manager.py` с классом SkillManager
    - Реализовать `can_upgrade_skill()` с проверкой stars и prerequisites
    - Реализовать `calculate_skill_cost()` по формуле base_cost + level
    - Реализовать `apply_skill_upgrade()` с атомарным обновлением
    - Реализовать `get_skill_effects()` для отображения бонусов
    - Реализовать `validate_prerequisites()` для dependency checking
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 5.1_
  
  - [x] 4.2 Написать property test для skill cost formula
    - **Property 12: Skill Cost Formula**
    - **Validates: Requirements 5.1, 5.5**
  
  - [x] 4.3 Написать property test для upgrade atomicity
    - **Property 9: Upgrade Atomicity**
    - **Validates: Requirements 3.2**
  
  - [x] 4.4 Написать property test для valid upgrade preconditions
    - **Property 8: Valid Upgrade Preconditions**
    - **Validates: Requirements 3.1, 3.3, 3.4**
  
  - [x] 4.5 Написать unit tests для skill level bounds
    - Тест level bounds 1-10 (Property 7)
    - Тест max level prevention
    - Тест invalid skill ID handling
    - _Requirements: 2.4, 2.5_

- [x] 5. Checkpoint - Убедиться что базовые компоненты работают
  - Убедиться что все тесты проходят, спросить пользователя если возникли вопросы

- [ ] 6. Реализовать SkillTreeManager (главный оркестратор)
  - [x] 6.1 Создать `skills_system.py` с классом SkillTreeManager
    - Реализовать `__init__()` с инициализацией всех менеджеров
    - Реализовать `process_monthly_stars()` для ежемесячных наград
    - Реализовать `upgrade_skill()` с полной валидацией и эффектами
    - Реализовать `reset_skills()` с 80% refund и cooldown
    - Реализовать `get_skill_tree()` для отображения
    - _Requirements: 3.1, 3.2, 7.1, 7.2, 7.5_
  
  - [x] 6.2 Написать property test для skill reset refund
    - **Property 13: Skill Reset Refund**
    - **Validates: Requirements 7.1, 7.2**
  
  - [x] 6.3 Написать property test для reset cooldown
    - **Property 15: Reset Cooldown Enforcement**
    - **Validates: Requirements 7.5**
  
  - [x] 6.4 Написать unit tests для skill tree display
    - Тест display completeness (Property 6)
    - Тест locked skill indication
    - Тест upgrade availability highlighting
    - Тест completion indication
    - _Requirements: 2.2, 2.3, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 7. Интегрировать с существующими системами
  - [ ] 7.1 Интегрировать с Side Jobs System
    - Модифицировать `side_jobs_system.py` для учета Luck skill (success rate)
    - Модифицировать расчет payment для Charisma (social jobs)
    - Модифицировать расчет payment для Intelligence (mental jobs)
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ] 7.2 Интегрировать с Balance System
    - Модифицировать `balance_system.py` для учета Endurance skill
    - Применить expense reduction в `calculate_daily_expenses()`
    - _Requirements: 4.4_
  
  - [ ] 7.3 Интегрировать с Business System
    - Модифицировать `business_system.py` для учета Business skill
    - Применить revenue multiplier в `calculate_daily_revenue()`
    - _Requirements: 4.5_
  
  - [ ] 7.4 Интегрировать с Entertainment System
    - Модифицировать `entertainment_system.py` для учета Entertainment skill
    - Применить win rate bonus в каждом игровом движке
    - _Requirements: 4.6_
  
  - [ ] 7.5 Написать property test для skill effects integration
    - **Property 11: Skill Effects Integration**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**
  
  - [ ] 7.6 Написать property test для reset effects cleanup
    - **Property 14: Skill Reset Effects Cleanup**
    - **Validates: Requirements 7.3**

- [ ] 8. Реализовать систему достижений
  - [ ] 8.1 Создать achievement tracking в SkillTreeManager
    - Добавить проверку "Master" achievement (любой skill level 10)
    - Добавить проверку branch-specific achievements (все skills в ветке level 10)
    - Добавить проверку "Grandmaster" achievement (все skills level 10)
    - Добавить проверку "Big Spender" achievement (100 stars spent)
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ] 8.2 Написать property test для achievement triggering
    - **Property 16: Achievement Triggering**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**
  
  - [ ] 8.3 Написать property test для achievement persistence
    - **Property 17: Achievement Persistence**
    - **Validates: Requirements 8.5**

- [ ] 9. Checkpoint - Убедиться что интеграция работает
  - Убедиться что все тесты проходят, спросить пользователя если возникли вопросы

- [ ] 10. Добавить Flask routes и UI
  - [ ] 10.1 Создать Flask routes в `app.py`
    - Добавить `/skills` route для отображения skill tree
    - Добавить `/skills/upgrade` route для прокачки навыка
    - Добавить `/skills/reset` route для сброса навыков
    - Добавить `/skills/history` route для истории звезд
    - _Requirements: 2.2, 6.5, 10.3_
  
  - [ ] 10.2 Создать HTML template `templates/skills.html`
    - Отобразить star balance prominently
    - Отобразить все 5 веток навыков
    - Показать locked skills с 🔒 и prerequisites
    - Показать available skills с ✨
    - Показать maxed skills с ✅
    - Добавить кнопки upgrade для доступных навыков
    - Добавить кнопку reset с confirmation
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.4_
  
  - [ ] 10.3 Создать HTML template `templates/star_history.html`
    - Отобразить последние 10 star earning events
    - Показать timestamp, source, amount для каждого
    - _Requirements: 10.3, 10.4_

- [ ] 11. Добавить star notifications
  - [ ] 11.1 Создать notification system для star awards
    - Добавить flash messages при получении звезд
    - Показать source и amount в уведомлении
    - Агрегировать multiple simultaneous awards
    - _Requirements: 10.1, 10.2_
  
  - [ ] 11.2 Написать property test для star notification completeness
    - **Property 20: Star Notification Completeness**
    - **Validates: Requirements 10.1, 10.4**
  
  - [ ] 11.3 Написать property test для star history bounds
    - **Property 21: Star History Bounds**
    - **Validates: Requirements 10.3, 10.5**

- [ ] 12. Интегрировать star awards в игровой цикл
  - [ ] 12.1 Добавить monthly star check в daily cycle
    - Модифицировать `process_new_day()` для проверки 30-дневного цикла
    - Вызвать `process_monthly_stars()` при достижении месяца
    - _Requirements: 1.1_
  
  - [ ] 12.2 Добавить star awards в wealth tier changes
    - Модифицировать `BalanceManager.process_new_day()` для award stars при tier change
    - _Requirements: 1.2_
  
  - [ ] 12.3 Добавить star awards в achievement system
    - Модифицировать achievement unlock для award stars
    - _Requirements: 1.3_
  
  - [ ] 12.4 Добавить milestone tracking
    - Добавить проверку cumulative earnings (1M)
    - Добавить проверку survival days (100)
    - _Requirements: 1.4, 1.5_

- [ ] 13. Финальное тестирование и полировка
  - [ ] 13.1 Запустить все property tests
    - Убедиться что все 21 property проходят с 100+ итерациями
  
  - [ ] 13.2 Запустить все unit tests
    - Убедиться что все edge cases покрыты
  
  - [ ] 13.3 Провести интеграционное тестирование
    - Протестировать полный цикл: earn stars → upgrade skills → see effects
    - Протестировать reset functionality
    - Протестировать achievement unlocking
    - Протестировать persistence через save/load
  
  - [ ] 13.4 Добавить документацию
    - Создать README для skills system
    - Документировать API endpoints
    - Добавить примеры использования

- [ ] 14. Final checkpoint - Убедиться что все работает
  - Убедиться что все тесты проходят, спросить пользователя если возникли вопросы

## Notes

- Все задачи являются обязательными для comprehensive implementation
- Каждая задача ссылается на конкретные requirements для трассируемости
- Checkpoints обеспечивают инкрементальную валидацию
- Property tests валидируют универсальные свойства корректности
- Unit tests валидируют конкретные примеры и edge cases
- Интеграционные тесты проверяют взаимодействие со всеми системами

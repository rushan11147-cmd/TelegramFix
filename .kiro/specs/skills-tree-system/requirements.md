# Requirements Document: Skills Tree System

## Introduction

Система навыков с веткой развития (Skill Tree) для игры "Survive Until Payday". Система позволяет игрокам развивать персонажа через древо навыков, используя звезды (⭐) как валюту прогрессии. Текущая проблема: система дает слишком много звезд, что делает прогрессию слишком быстрой и неинтересной.

## Glossary

- **Skill_Tree**: Древо навыков - иерархическая структура навыков с зависимостями
- **Skill**: Навык - улучшение характеристик игрока (удача, харизма, интеллект и т.д.)
- **Star**: Звезда (⭐) - валюта для покупки навыков
- **Skill_Level**: Уровень навыка - текущий прогресс в конкретном навыке (1-10)
- **Skill_Node**: Узел навыка - элемент древа навыков с требованиями и эффектами
- **Prerequisite**: Предварительное требование - навык, который должен быть изучен перед текущим
- **Star_Source**: Источник звезд - действие или событие, дающее звезды игроку
- **Balance_System**: Система балансировки - существующая система экономики игры
- **Side_Job_System**: Система подработок - существующая система побочных заработков
- **Business_System**: Система бизнеса - существующая система управления бизнесом
- **Entertainment_System**: Система развлечений - существующая система казино и игр

## Requirements

### Requirement 1: Star Economy Balancing

**User Story:** Как игрок, я хочу зарабатывать звезды за значимые достижения и ежемесячно, чтобы прогрессия была медленной и ценной

#### Acceptance Criteria

1. WHEN a new month begins (every 30 game days), THE Star_Source SHALL award 3 stars as monthly salary
2. WHEN a player reaches a new wealth tier, THE Star_Source SHALL award 5 stars as milestone reward
3. WHEN a player completes a major achievement (businessman, tycoon, etc.), THE Star_Source SHALL award 3 stars
4. WHEN a player earns cumulative 1,000,000₽ total, THE Star_Source SHALL award 5 stars as one-time reward
5. WHEN a player survives 100 game days, THE Star_Source SHALL award 10 stars as survival milestone
6. THE Star_Source SHALL NOT award stars for routine actions like daily work, side jobs, or entertainment

### Requirement 2: Skill Tree Structure

**User Story:** Как игрок, я хочу видеть древо навыков с понятной структурой, чтобы планировать развитие персонажа

#### Acceptance Criteria

1. THE Skill_Tree SHALL contain at least 5 distinct skill branches (Luck, Charisma, Intelligence, Endurance, Business)
2. WHEN displaying the skill tree, THE System SHALL show all available skills with their current levels and costs
3. WHEN a skill has prerequisites, THE System SHALL display locked skills with clear indication of requirements
4. THE Skill_Tree SHALL support skills with levels from 1 to 10
5. WHEN a skill is at maximum level (10), THE System SHALL mark it as completed and prevent further upgrades

### Requirement 3: Skill Unlocking and Progression

**User Story:** Как игрок, я хочу разблокировать навыки за звезды, чтобы улучшать характеристики персонажа

#### Acceptance Criteria

1. WHEN a player has sufficient stars and meets prerequisites, THE System SHALL allow skill upgrade
2. WHEN upgrading a skill, THE System SHALL deduct the star cost and increment skill level by 1
3. WHEN a player lacks sufficient stars, THE System SHALL prevent upgrade and display required amount
4. WHEN a skill has unmet prerequisites, THE System SHALL prevent unlock and display required skills
5. THE System SHALL persist skill levels and star balance across game sessions

### Requirement 4: Skill Effects Integration

**User Story:** Как игрок, я хочу чтобы навыки влияли на игровой процесс, чтобы развитие было осмысленным

#### Acceptance Criteria

1. WHEN Luck skill is upgraded, THE Side_Job_System SHALL increase success rate by 5% per level
2. WHEN Charisma skill is upgraded, THE Side_Job_System SHALL increase social job payment by 5% per level
3. WHEN Intelligence skill is upgraded, THE Side_Job_System SHALL increase mental job payment by 5% per level
4. WHEN Endurance skill is upgraded, THE Balance_System SHALL reduce daily expenses by 3% per level
5. WHEN Business skill is upgraded, THE Business_System SHALL increase business revenue by 5% per level
6. WHEN Entertainment skill is upgraded, THE Entertainment_System SHALL improve win rates by 2% per level

### Requirement 5: Star Cost Scaling

**User Story:** Как разработчик, я хочу чтобы стоимость навыков росла с уровнем, чтобы поздняя прогрессия была сложнее

#### Acceptance Criteria

1. WHEN calculating skill cost, THE System SHALL use formula: base_cost + (current_level * level_multiplier)
2. FOR basic skills (Luck, Charisma, Intelligence), THE System SHALL set base_cost to 2 stars
3. FOR advanced skills (Endurance, Business, Entertainment), THE System SHALL set base_cost to 3 stars
4. THE System SHALL set level_multiplier to 1 for all skills
5. WHEN a skill reaches level 10, THE total cost SHALL be at least 20 stars for basic skills

### Requirement 6: Skill Tree Visualization

**User Story:** Как игрок, я хочу видеть визуальное представление древа навыков, чтобы понимать структуру и прогресс

#### Acceptance Criteria

1. WHEN viewing skill tree, THE System SHALL display each skill with name, emoji, current level, and max level
2. WHEN a skill is locked, THE System SHALL display it with visual indication (🔒) and prerequisites
3. WHEN a skill is available for upgrade, THE System SHALL highlight it with visual indication (✨)
4. WHEN a skill is maxed out, THE System SHALL display it with completion indication (✅)
5. THE System SHALL display player's current star balance prominently in the skill tree view

### Requirement 7: Skill Reset Functionality

**User Story:** Как игрок, я хочу иметь возможность сбросить навыки, чтобы перераспределить звезды

#### Acceptance Criteria

1. WHEN a player requests skill reset, THE System SHALL refund 80% of spent stars
2. WHEN resetting skills, THE System SHALL reset all skill levels to 1 (base level)
3. WHEN resetting skills, THE System SHALL remove all skill effects from game systems
4. THE System SHALL require confirmation before performing skill reset
5. THE System SHALL allow skill reset only once per 7 game days

### Requirement 8: Achievement Integration

**User Story:** Как игрок, я хочу получать достижения за развитие навыков, чтобы иметь дополнительную мотивацию

#### Acceptance Criteria

1. WHEN a player maxes out any skill (level 10), THE System SHALL unlock "Master" achievement
2. WHEN a player maxes out all skills in one branch, THE System SHALL unlock branch-specific achievement
3. WHEN a player maxes out all skills in all branches, THE System SHALL unlock "Grandmaster" achievement
4. WHEN a player spends 100 stars total, THE System SHALL unlock "Big Spender" achievement
5. THE System SHALL persist achievement progress across game sessions

### Requirement 9: Skill Data Persistence

**User Story:** Как разработчик, я хочу чтобы данные навыков сохранялись надежно, чтобы игроки не теряли прогресс

#### Acceptance Criteria

1. WHEN a player upgrades a skill, THE System SHALL immediately persist changes to database
2. WHEN a player earns stars, THE System SHALL immediately persist star balance to database
3. WHEN loading player data, THE System SHALL initialize default skill structure if missing
4. THE System SHALL validate skill data integrity on load and repair corrupted data
5. THE System SHALL maintain backward compatibility with existing player data

### Requirement 10: Star Earning Notifications

**User Story:** Как игрок, я хочу видеть уведомления о заработанных звездах, чтобы понимать источники прогрессии

#### Acceptance Criteria

1. WHEN a player earns stars, THE System SHALL display notification with amount and source
2. WHEN a player earns stars from multiple sources simultaneously, THE System SHALL aggregate notifications
3. THE System SHALL display star earning history for last 10 events
4. WHEN viewing star history, THE System SHALL show timestamp, source, and amount for each event
5. THE System SHALL clear star history older than 30 days automatically

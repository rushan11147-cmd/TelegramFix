# Design Document: Skills Tree System

## Overview

Система навыков с древом развития для игры "Survive Until Payday". Система предоставляет долгосрочную прогрессию через редкую валюту (звезды ⭐), которая зарабатывается за значимые достижения и ежемесячно. Навыки организованы в древовидную структуру с зависимостями и влияют на все игровые системы.

**Ключевые особенности:**
- Редкая экономика звезд (3 звезды/месяц + достижения)
- 5 веток навыков с 10 уровнями каждая
- Интеграция со всеми существующими системами
- Визуальное древо с индикацией статуса
- Система сброса навыков (80% возврат)

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Flask Application                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │           SkillTreeManager (Orchestrator)         │  │
│  │  - process_monthly_stars()                        │  │
│  │  - upgrade_skill()                                │  │
│  │  - reset_skills()                                 │  │
│  │  - get_skill_tree()                               │  │
│  └────────┬─────────────────────────────────┬────────┘  │
│           │                                  │            │
│  ┌────────▼────────┐              ┌─────────▼────────┐  │
│  │  StarEconomy    │              │  SkillManager    │  │
│  │  Manager        │              │                  │  │
│  │                 │              │                  │  │
│  │ - award_stars() │              │ - can_upgrade()  │  │
│  │ - track_source()│              │ - apply_effects()│  │
│  └────────┬────────┘              └─────────┬────────┘  │
│           │                                  │            │
│  ┌────────▼──────────────────────────────────▼────────┐  │
│  │              SkillRepository                       │  │
│  │  - save_skill_data()                               │  │
│  │  - load_skill_data()                               │  │
│  │  - save_star_history()                             │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                                │
└──────────────────────────┼────────────────────────────────┘
                           │
                  ┌────────▼────────┐
                  │  SQLite Database │
                  │  (user_data)     │
                  └──────────────────┘
```

### Integration Points

Система навыков интегрируется с существующими системами:

1. **Balance System** - Endurance навык снижает расходы
2. **Side Jobs System** - Luck, Charisma, Intelligence влияют на подработки
3. **Business System** - Business навык увеличивает доход бизнеса
4. **Entertainment System** - Entertainment навык улучшает шансы в казино

## Components and Interfaces

### 1. SkillTreeManager (Main Orchestrator)

Главный оркестратор системы навыков.

```python
class SkillTreeManager:
    """Main orchestrator for skill tree system"""
    
    def __init__(self, get_user_func, save_user_func):
        """
        Initialize with database access functions
        
        Args:
            get_user_func: Function to get user data
            save_user_func: Function to save user data
        """
        self.get_user = get_user_func
        self.save_user = save_user_func
        self.star_economy = StarEconomyManager()
        self.skill_manager = SkillManager()
        self.repository = SkillRepository(get_user_func, save_user_func)
    
    def process_monthly_stars(self, user_id: str, current_day: int) -> Dict:
        """
        Awards monthly stars (every 30 days)
        
        Args:
            user_id: Player ID
            current_day: Current game day
            
        Returns:
            {
                'success': bool,
                'stars_awarded': int,
                'new_balance': int,
                'next_award_day': int
            }
        """
        pass
    
    def upgrade_skill(self, user_id: str, skill_id: str) -> Dict:
        """
        Upgrades a skill by one level
        
        Args:
            user_id: Player ID
            skill_id: Skill identifier
            
        Returns:
            {
                'success': bool,
                'skill_id': str,
                'new_level': int,
                'stars_spent': int,
                'new_star_balance': int,
                'error': str (if failed)
            }
        """
        pass
    
    def reset_skills(self, user_id: str) -> Dict:
        """
        Resets all skills and refunds 80% of stars
        
        Args:
            user_id: Player ID
            
        Returns:
            {
                'success': bool,
                'stars_refunded': int,
                'new_star_balance': int,
                'next_reset_day': int,
                'error': str (if failed)
            }
        """
        pass
    
    def get_skill_tree(self, user_id: str) -> Dict:
        """
        Returns complete skill tree with current state
        
        Args:
            user_id: Player ID
            
        Returns:
            {
                'star_balance': int,
                'skills': Dict[str, SkillNode],
                'total_stars_spent': int,
                'can_reset': bool,
                'days_until_reset': int
            }
        """
        pass
```

### 2. StarEconomyManager

Управляет экономикой звезд и источниками получения.

```python
class StarEconomyManager:
    """Manages star economy and award sources"""
    
    MONTHLY_STARS = 3
    WEALTH_TIER_STARS = 5
    ACHIEVEMENT_STARS = 3
    MILLION_EARNED_STARS = 5
    SURVIVAL_100_DAYS_STARS = 10
    
    def award_monthly_stars(self, user_data: Dict, current_day: int) -> int:
        """
        Awards monthly stars if eligible
        
        Args:
            user_data: Player data
            current_day: Current game day
            
        Returns:
            Number of stars awarded (0 if not eligible)
        """
        pass
    
    def award_wealth_tier_stars(self, user_data: Dict, new_tier: str) -> int:
        """
        Awards stars for reaching new wealth tier
        
        Args:
            user_data: Player data
            new_tier: New wealth tier reached
            
        Returns:
            Number of stars awarded
        """
        pass
    
    def award_achievement_stars(self, user_data: Dict, achievement: str) -> int:
        """
        Awards stars for completing achievement
        
        Args:
            user_data: Player data
            achievement: Achievement identifier
            
        Returns:
            Number of stars awarded
        """
        pass
    
    def check_milestone_stars(self, user_data: Dict) -> int:
        """
        Checks and awards milestone stars (1M earned, 100 days)
        
        Args:
            user_data: Player data
            
        Returns:
            Number of stars awarded
        """
        pass
    
    def track_star_source(self, user_data: Dict, source: str, amount: int) -> None:
        """
        Records star earning event in history
        
        Args:
            user_data: Player data
            source: Source of stars
            amount: Number of stars
        """
        pass
```

### 3. SkillManager

Управляет навыками, их эффектами и валидацией.

```python
class SkillManager:
    """Manages skills, effects, and validation"""
    
    def can_upgrade_skill(self, user_data: Dict, skill_id: str) -> Tuple[bool, str]:
        """
        Checks if skill can be upgraded
        
        Args:
            user_data: Player data
            skill_id: Skill identifier
            
        Returns:
            (can_upgrade, error_message)
        """
        pass
    
    def calculate_skill_cost(self, skill_id: str, current_level: int) -> int:
        """
        Calculates cost to upgrade skill
        
        Formula: base_cost + (current_level * 1)
        
        Args:
            skill_id: Skill identifier
            current_level: Current skill level
            
        Returns:
            Star cost for next level
        """
        pass
    
    def apply_skill_upgrade(self, user_data: Dict, skill_id: str) -> None:
        """
        Applies skill upgrade effects
        
        Args:
            user_data: Player data (modified in place)
            skill_id: Skill identifier
        """
        pass
    
    def get_skill_effects(self, user_data: Dict, skill_id: str) -> Dict:
        """
        Returns current effects of a skill
        
        Args:
            user_data: Player data
            skill_id: Skill identifier
            
        Returns:
            {
                'bonus_percentage': float,
                'affected_systems': List[str],
                'description': str
            }
        """
        pass
    
    def validate_prerequisites(self, user_data: Dict, skill_id: str) -> bool:
        """
        Checks if skill prerequisites are met
        
        Args:
            user_data: Player data
            skill_id: Skill identifier
            
        Returns:
            True if prerequisites met
        """
        pass
```

### 4. SkillRepository

Управляет персистентностью данных навыков.

```python
class SkillRepository:
    """Handles skill data persistence"""
    
    def __init__(self, get_user_func, save_user_func):
        self.get_user = get_user_func
        self.save_user = save_user_func
    
    def load_skill_data(self, user_id: str) -> Dict:
        """
        Loads skill data, initializes if missing
        
        Args:
            user_id: Player ID
            
        Returns:
            {
                'star_balance': int,
                'skills': Dict[str, int],  # skill_id -> level
                'total_stars_spent': int,
                'last_monthly_award_day': int,
                'last_reset_day': int,
                'milestones_claimed': List[str]
            }
        """
        pass
    
    def save_skill_data(self, user_id: str, skill_data: Dict) -> None:
        """
        Saves skill data to database
        
        Args:
            user_id: Player ID
            skill_data: Skill data to save
        """
        pass
    
    def save_star_history(self, user_id: str, event: Dict) -> None:
        """
        Saves star earning event to history
        
        Args:
            user_id: Player ID
            event: {
                'timestamp': str,
                'source': str,
                'amount': int
            }
        """
        pass
    
    def get_star_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Retrieves recent star earning history
        
        Args:
            user_id: Player ID
            limit: Maximum events to return
            
        Returns:
            List of star earning events
        """
        pass
```

## Data Models

### SkillNode

Представляет узел в древе навыков.

```python
@dataclass
class SkillNode:
    """Represents a skill node in the tree"""
    skill_id: str
    name: str
    emoji: str
    branch: str  # 'luck', 'charisma', 'intelligence', 'endurance', 'business'
    base_cost: int  # 2 for basic, 3 for advanced
    max_level: int = 10
    prerequisites: List[str] = field(default_factory=list)
    description: str = ""
    
    def calculate_cost(self, current_level: int) -> int:
        """
        Calculates cost for next level
        Formula: base_cost + current_level
        """
        return self.base_cost + current_level
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            'skill_id': self.skill_id,
            'name': self.name,
            'emoji': self.emoji,
            'branch': self.branch,
            'base_cost': self.base_cost,
            'max_level': self.max_level,
            'prerequisites': self.prerequisites,
            'description': self.description
        }
```

### Skill Tree Configuration

```python
SKILL_TREE_CONFIG = {
    # Luck Branch
    'luck_1': SkillNode(
        skill_id='luck_1',
        name='Удача I',
        emoji='🍀',
        branch='luck',
        base_cost=2,
        prerequisites=[],
        description='+5% шанс успеха подработок за уровень'
    ),
    'luck_2': SkillNode(
        skill_id='luck_2',
        name='Удача II',
        emoji='🎲',
        branch='luck',
        base_cost=2,
        prerequisites=['luck_1'],
        description='+2% шанс выигрыша в развлечениях за уровень'
    ),
    
    # Charisma Branch
    'charisma_1': SkillNode(
        skill_id='charisma_1',
        name='Харизма I',
        emoji='💬',
        branch='charisma',
        base_cost=2,
        prerequisites=[],
        description='+5% оплата социальных подработок за уровень'
    ),
    
    # Intelligence Branch
    'intelligence_1': SkillNode(
        skill_id='intelligence_1',
        name='Интеллект I',
        emoji='🧠',
        branch='intelligence',
        base_cost=2,
        prerequisites=[],
        description='+5% оплата умственных подработок за уровень'
    ),
    
    # Endurance Branch
    'endurance_1': SkillNode(
        skill_id='endurance_1',
        name='Выносливость I',
        emoji='💪',
        branch='endurance',
        base_cost=3,
        prerequisites=[],
        description='-3% ежедневные расходы за уровень'
    ),
    
    # Business Branch
    'business_1': SkillNode(
        skill_id='business_1',
        name='Бизнес I',
        emoji='💼',
        branch='business',
        base_cost=3,
        prerequisites=[],
        description='+5% доход от бизнеса за уровень'
    ),
}
```

### SkillData

Данные навыков игрока.

```python
@dataclass
class SkillData:
    """Player's skill data"""
    star_balance: int = 0
    skills: Dict[str, int] = field(default_factory=dict)  # skill_id -> level
    total_stars_spent: int = 0
    last_monthly_award_day: int = 0
    last_reset_day: int = -7  # Allow immediate first reset
    milestones_claimed: List[str] = field(default_factory=list)
    star_history: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            'star_balance': self.star_balance,
            'skills': self.skills,
            'total_stars_spent': self.total_stars_spent,
            'last_monthly_award_day': self.last_monthly_award_day,
            'last_reset_day': self.last_reset_day,
            'milestones_claimed': self.milestones_claimed,
            'star_history': self.star_history
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'SkillData':
        """Deserialize from dictionary"""
        return SkillData(
            star_balance=data.get('star_balance', 0),
            skills=data.get('skills', {}),
            total_stars_spent=data.get('total_stars_spent', 0),
            last_monthly_award_day=data.get('last_monthly_award_day', 0),
            last_reset_day=data.get('last_reset_day', -7),
            milestones_claimed=data.get('milestones_claimed', []),
            star_history=data.get('star_history', [])
        )
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Monthly Star Award Consistency

*For any* player and any sequence of game days, when exactly 30 days have passed since the last monthly award, the system should award exactly 3 stars and update the last award day.

**Validates: Requirements 1.1**

### Property 2: Wealth Tier Star Award

*For any* player transitioning to a new wealth tier, the system should award exactly 5 stars and record the tier change to prevent duplicate awards.

**Validates: Requirements 1.2**

### Property 3: Achievement Star Award

*For any* major achievement completion (businessman, tycoon, etc.), the system should award exactly 3 stars and mark the achievement as claimed to prevent duplicate awards.

**Validates: Requirements 1.3**

### Property 4: Milestone Star Awards

*For any* player reaching cumulative milestones (1M earned, 100 days survived), the system should award the appropriate stars exactly once and mark the milestone as claimed.

**Validates: Requirements 1.4, 1.5**

### Property 5: Routine Action Exclusion

*For any* routine action (daily work, side job, entertainment), the system should NOT award any stars.

**Validates: Requirements 1.6**

### Property 6: Skill Tree Display Completeness

*For any* skill tree state, the display should contain all required information: skill names, emojis, current levels, max levels, costs, lock status, upgrade availability, completion status, and star balance.

**Validates: Requirements 2.2, 2.3, 6.1, 6.2, 6.3, 6.4, 6.5**

### Property 7: Skill Level Bounds

*For any* skill, the level should always be between 1 and 10 inclusive, and attempts to upgrade beyond level 10 should be rejected.

**Validates: Requirements 2.4, 2.5**

### Property 8: Valid Upgrade Preconditions

*For any* skill upgrade attempt, if the player has sufficient stars AND meets all prerequisites, the upgrade should succeed; otherwise it should fail with appropriate error message.

**Validates: Requirements 3.1, 3.3, 3.4**

### Property 9: Upgrade Atomicity

*For any* successful skill upgrade, both the star deduction and level increment should occur atomically - either both happen or neither happens.

**Validates: Requirements 3.2**

### Property 10: Skill Data Persistence Round Trip

*For any* skill data state, saving then loading should produce an equivalent state with all skill levels, star balance, and history preserved.

**Validates: Requirements 3.5, 9.1, 9.2**

### Property 11: Skill Effects Integration

*For any* skill at level N, the integrated systems (Side Jobs, Balance, Business, Entertainment) should apply the correct bonus percentage (5% for Luck/Charisma/Intelligence/Business, 3% for Endurance, 2% for Entertainment) multiplied by N.

**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**

### Property 12: Skill Cost Formula

*For any* skill at current level L, the cost to upgrade to level L+1 should be exactly base_cost + L, where base_cost is 2 for basic skills and 3 for advanced skills.

**Validates: Requirements 5.1, 5.5**

### Property 13: Skill Reset Refund

*For any* skill reset operation, the player should receive exactly 80% of total stars spent (rounded down), and all skill levels should be reset to 1.

**Validates: Requirements 7.1, 7.2**

### Property 14: Skill Reset Effects Cleanup

*For any* skill reset operation, all skill effects should be removed from integrated systems (success rates, payment bonuses, expense reductions, revenue multipliers should return to base values).

**Validates: Requirements 7.3**

### Property 15: Reset Cooldown Enforcement

*For any* player, skill reset should be allowed only if at least 7 game days have passed since the last reset.

**Validates: Requirements 7.5**

### Property 16: Achievement Triggering

*For any* achievement condition (max skill, max branch, max all, 100 stars spent), when the condition is met, the corresponding achievement should be unlocked exactly once.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4**

### Property 17: Achievement Persistence

*For any* unlocked achievement, saving then loading should preserve the achievement status.

**Validates: Requirements 8.5**

### Property 18: Data Initialization

*For any* player with missing skill data, loading should initialize default skill structure with star_balance=0, all skills at level 1, and empty history.

**Validates: Requirements 9.3**

### Property 19: Data Integrity Validation

*For any* corrupted skill data (invalid levels, negative stars, missing fields), loading should repair the data to valid state.

**Validates: Requirements 9.4**

### Property 20: Star Notification Completeness

*For any* star earning event, the notification should contain timestamp, source description, and amount.

**Validates: Requirements 10.1, 10.4**

### Property 21: Star History Bounds

*For any* star history, only the most recent 10 events should be displayed, and events older than 30 days should be automatically removed.

**Validates: Requirements 10.3, 10.5**

## Error Handling

### Star Economy Errors

1. **Insufficient Stars**: When attempting to upgrade with insufficient stars, return error with required amount
2. **Invalid Milestone**: When attempting to claim already-claimed milestone, silently skip
3. **Invalid Source**: When tracking star from unknown source, log warning and continue

### Skill Upgrade Errors

1. **Unmet Prerequisites**: When attempting to upgrade locked skill, return error listing required skills
2. **Max Level Reached**: When attempting to upgrade maxed skill, return error indicating completion
3. **Invalid Skill ID**: When referencing non-existent skill, return error with valid skill list

### Reset Errors

1. **Cooldown Active**: When attempting reset before cooldown expires, return error with days remaining
2. **No Skills to Reset**: When attempting reset with all skills at level 1, return error

### Persistence Errors

1. **Database Unavailable**: When database operations fail, retry up to 3 times with exponential backoff
2. **Corrupted Data**: When loading corrupted data, attempt repair; if repair fails, initialize defaults
3. **Migration Failure**: When migrating old data format fails, log error and initialize defaults

## Testing Strategy

### Dual Testing Approach

The system will use both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples of skill upgrades
- Edge cases (level 1, level 10, insufficient stars)
- Error conditions (invalid skill IDs, unmet prerequisites)
- Integration points with existing systems
- Achievement unlocking scenarios

**Property-Based Tests** focus on:
- Universal properties across all skills and levels
- Cost calculation formulas
- Persistence round trips
- Effect application correctness
- Bounds checking

### Property-Based Testing Configuration

- **Library**: Use `hypothesis` for Python property-based testing
- **Iterations**: Minimum 100 iterations per property test
- **Tagging**: Each property test must reference its design property number
- **Tag Format**: `# Feature: skills-tree-system, Property N: [property description]`

### Test Coverage Requirements

1. **Star Economy**: Test all star sources and award conditions
2. **Skill Upgrades**: Test all skills at all levels with various star balances
3. **Prerequisites**: Test all prerequisite chains
4. **Effects**: Test integration with all game systems
5. **Persistence**: Test save/load cycles with various data states
6. **Achievements**: Test all achievement conditions
7. **Reset**: Test reset with various skill configurations

### Integration Testing

Test integration with existing systems:
- **Balance System**: Verify Endurance skill reduces expenses
- **Side Jobs System**: Verify Luck/Charisma/Intelligence affect jobs
- **Business System**: Verify Business skill increases revenue
- **Entertainment System**: Verify Entertainment skill improves odds

### Example Property Test

```python
from hypothesis import given, strategies as st
import hypothesis

@hypothesis.settings(max_examples=100)
@given(
    current_level=st.integers(min_value=1, max_value=9),
    skill_type=st.sampled_from(['basic', 'advanced'])
)
def test_skill_cost_formula(current_level, skill_type):
    """
    Feature: skills-tree-system, Property 12: Skill Cost Formula
    
    For any skill at current level L, the cost to upgrade to level L+1
    should be exactly base_cost + L.
    """
    base_cost = 2 if skill_type == 'basic' else 3
    expected_cost = base_cost + current_level
    
    skill_id = 'luck_1' if skill_type == 'basic' else 'endurance_1'
    skill_manager = SkillManager()
    
    actual_cost = skill_manager.calculate_skill_cost(skill_id, current_level)
    
    assert actual_cost == expected_cost, \
        f"Cost formula incorrect: expected {expected_cost}, got {actual_cost}"
```

## Implementation Notes

### Performance Considerations

1. **Caching**: Cache skill tree configuration in memory (it's static)
2. **Batch Operations**: When resetting skills, batch database updates
3. **Lazy Loading**: Load star history only when requested
4. **Indexing**: Index user_id in database for fast lookups

### Security Considerations

1. **Validation**: Always validate skill IDs and levels server-side
2. **Atomicity**: Use database transactions for multi-step operations
3. **Rate Limiting**: Limit skill upgrade requests to prevent abuse
4. **Audit Trail**: Log all star awards and skill upgrades for debugging

### Backward Compatibility

1. **Migration**: Detect old data format and migrate to new structure
2. **Defaults**: Provide sensible defaults for missing fields
3. **Versioning**: Include version field in skill data for future migrations

### Future Extensibility

1. **New Skills**: Design allows easy addition of new skill nodes
2. **New Branches**: Structure supports adding new skill branches
3. **New Star Sources**: Star economy manager easily extended with new sources
4. **Skill Synergies**: Architecture supports future skill combination bonuses

# Design Document: Career Progression System

## Overview

The Career Progression System introduces a structured career advancement mechanism that integrates with the existing game's job and skills systems. Players begin by selecting one of six professions (Courier, Office Worker, Salesperson, Waiter, Security Guard, IT Support), each with unique characteristics and a four-level career ladder. Progression through career levels is governed by multiple metrics (work experience, skill levels, money earned, days survived), and promotions unlock higher salaries, reduced energy costs, and special abilities.

The system is designed to be modular and extensible, allowing for future addition of new professions or career levels without disrupting existing functionality. It integrates seamlessly with the current Flask-based game architecture and SQLite database storage.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Flask App (app.py)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Routes     │  │  Templates   │  │   Database   │      │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘      │
│         │                                     │              │
└─────────┼─────────────────────────────────────┼──────────────┘
          │                                     │
          ▼                                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Career Progression System                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           CareerManager (Facade)                      │  │
│  │  - select_profession()                                │  │
│  │  - check_promotion_eligibility()                      │  │
│  │  - promote_player()                                   │  │
│  │  - get_career_info()                                  │  │
│  │  - calculate_work_income()                            │  │
│  └────┬─────────────────────────────────────────────┬────┘  │
│       │                                              │       │
│  ┌────▼──────────────┐                    ┌─────────▼─────┐ │
│  │ ProfessionConfig  │                    │ CareerState   │ │
│  │ - definitions     │                    │ - profession  │ │
│  │ - requirements    │                    │ - level       │ │
│  │ - salary_scales   │                    │ - metrics     │ │
│  └───────────────────┘                    └───────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           PromotionEvaluator                          │  │
│  │  - evaluate_requirements()                            │  │
│  │  - calculate_progress()                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                                     │
          ▼                                     ▼
┌─────────────────────┐           ┌─────────────────────────┐
│   Skills System     │           │   Database (SQLite)     │
│   (skills_system)   │           │   - career_state table  │
└─────────────────────┘           └─────────────────────────┘
```

### Component Interaction Flow

1. **Profession Selection**: Player → Flask Route → CareerManager.select_profession() → Database
2. **Work Action**: Player → Flask Route → CareerManager.calculate_work_income() → Update metrics → Check promotion
3. **Promotion Check**: CareerManager → PromotionEvaluator → Skills System → Return eligibility
4. **Promotion Execution**: Player → Flask Route → CareerManager.promote_player() → Update state → Database

## Components and Interfaces

### 1. CareerManager (Facade)

The main interface for all career-related operations.

```python
class CareerManager:
    """
    Manages all career progression operations including profession selection,
    promotion evaluation, and career state management.
    """
    
    def __init__(self, db_connection, skills_system):
        """
        Initialize the career manager.
        
        Args:
            db_connection: Database connection for persistence
            skills_system: Reference to the skills system for skill checks
        """
        self.db = db_connection
        self.skills = skills_system
        self.config = ProfessionConfig()
        self.evaluator = PromotionEvaluator(self.config, self.skills)
    
    def select_profession(self, player_id: int, profession: str) -> CareerState:
        """
        Set the player's initial profession.
        
        Args:
            player_id: Unique identifier for the player
            profession: One of 'courier', 'office_worker', 'salesperson', 'waiter', 'security_guard', 'it_support'
        
        Returns:
            CareerState object with initial profession settings
        
        Raises:
            ValueError: If profession is not valid
        """
        pass
    
    def check_promotion_eligibility(self, player_id: int) -> dict:
        """
        Check if player is eligible for promotion.
        
        Args:
            player_id: Unique identifier for the player
        
        Returns:
            Dictionary with:
                - eligible: bool
                - requirements_met: dict of requirement -> bool
                - progress: dict of requirement -> percentage
                - next_level: str (career level name)
        """
        pass
    
    def promote_player(self, player_id: int) -> CareerState:
        """
        Promote player to next career level.
        
        Args:
            player_id: Unique identifier for the player
        
        Returns:
            Updated CareerState object
        
        Raises:
            ValueError: If player is not eligible for promotion
        """
        pass
    
    def get_career_info(self, player_id: int) -> dict:
        """
        Get comprehensive career information for display.
        
        Args:
            player_id: Unique identifier for the player
        
        Returns:
            Dictionary with career state, progress, and statistics
        """
        pass
    
    def calculate_work_income(self, player_id: int) -> int:
        """
        Calculate income for a work action based on career level.
        
        Args:
            player_id: Unique identifier for the player
        
        Returns:
            Total income amount including base salary and bonuses
        """
        pass
    
    def record_work_action(self, player_id: int) -> None:
        """
        Record that a work action was completed and update metrics.
        
        Args:
            player_id: Unique identifier for the player
        """
        pass
    
    def get_energy_cost_multiplier(self, player_id: int) -> float:
        """
        Get the energy cost multiplier for the player's career level.
        
        Args:
            player_id: Unique identifier for the player
        
        Returns:
            Multiplier to apply to base energy cost (e.g., 0.95 for 5% reduction)
        """
        pass
```

### 2. ProfessionConfig

Configuration and definitions for all professions and career levels.

```python
class ProfessionConfig:
    """
    Stores all profession definitions, career ladders, and requirements.
    """
    
    PROFESSIONS = {
        'courier': {
            'name_ru': 'Курьер',
            'starting_salary': 150,
            'progression_multiplier': 1.5,
            'primary_skills': ['strength', 'endurance'],
            'levels': [
                {
                    'id': 0,
                    'name': 'Courier',
                    'name_ru': 'Курьер',
                    'salary': 150,
                    'requirements': {
                        'work_actions': 0,
                        'skills': {},
                        'money_earned': 0,
                        'days_survived': 0
                    }
                },
                {
                    'id': 1,
                    'name': 'Senior Courier',
                    'name_ru': 'Старший курьер',
                    'salary': 250,
                    'requirements': {
                        'work_actions': 20,
                        'skills': {'strength': 3, 'endurance': 3},
                        'money_earned': 3000,
                        'days_survived': 10
                    }
                },
                {
                    'id': 2,
                    'name': 'Delivery Manager',
                    'name_ru': 'Менеджер доставки',
                    'salary': 400,
                    'requirements': {
                        'work_actions': 50,
                        'skills': {'strength': 5, 'endurance': 5, 'intelligence': 3},
                        'money_earned': 10000,
                        'days_survived': 25
                    }
                },
                {
                    'id': 3,
                    'name': 'Logistics Director',
                    'name_ru': 'Директор логистики',
                    'salary': 700,
                    'requirements': {
                        'work_actions': 100,
                        'skills': {'strength': 7, 'endurance': 7, 'intelligence': 6},
                        'money_earned': 30000,
                        'days_survived': 50
                    }
                }
            ]
        },
        'office_worker': {
            'name_ru': 'Офисный работник',
            'starting_salary': 250,
            'progression_multiplier': 1.0,
            'primary_skills': ['intelligence', 'focus'],
            'levels': [
                {
                    'id': 0,
                    'name': 'Office Worker',
                    'name_ru': 'Офисный работник',
                    'salary': 250,
                    'requirements': {
                        'work_actions': 0,
                        'skills': {},
                        'money_earned': 0,
                        'days_survived': 0
                    }
                },
                {
                    'id': 1,
                    'name': 'Senior Specialist',
                    'name_ru': 'Старший специалист',
                    'salary': 400,
                    'requirements': {
                        'work_actions': 25,
                        'skills': {'intelligence': 4, 'focus': 3},
                        'money_earned': 5000,
                        'days_survived': 15
                    }
                },
                {
                    'id': 2,
                    'name': 'Team Lead',
                    'name_ru': 'Руководитель группы',
                    'salary': 650,
                    'requirements': {
                        'work_actions': 60,
                        'skills': {'intelligence': 6, 'focus': 5, 'charisma': 4},
                        'money_earned': 15000,
                        'days_survived': 35
                    }
                },
                {
                    'id': 3,
                    'name': 'Department Manager',
                    'name_ru': 'Начальник отдела',
                    'salary': 1000,
                    'requirements': {
                        'work_actions': 120,
                        'skills': {'intelligence': 8, 'focus': 7, 'charisma': 6},
                        'money_earned': 40000,
                        'days_survived': 60
                    }
                }
            ]
        },
        'salesperson': {
            'name_ru': 'Продавец',
            'starting_salary': 200,
            'progression_multiplier': 1.2,
            'primary_skills': ['charisma', 'intelligence'],
            'bonus_skill': 'charisma',  # Skill that provides commission bonus
            'bonus_multiplier': 0.1,  # 10% bonus per charisma level
            'levels': [
                {
                    'id': 0,
                    'name': 'Salesperson',
                    'name_ru': 'Продавец',
                    'salary': 200,
                    'requirements': {
                        'work_actions': 0,
                        'skills': {},
                        'money_earned': 0,
                        'days_survived': 0
                    }
                },
                {
                    'id': 1,
                    'name': 'Senior Salesperson',
                    'name_ru': 'Старший продавец',
                    'salary': 350,
                    'requirements': {
                        'work_actions': 22,
                        'skills': {'charisma': 4, 'intelligence': 2},
                        'money_earned': 4000,
                        'days_survived': 12
                    }
                },
                {
                    'id': 2,
                    'name': 'Sales Manager',
                    'name_ru': 'Менеджер по продажам',
                    'salary': 550,
                    'requirements': {
                        'work_actions': 55,
                        'skills': {'charisma': 6, 'intelligence': 5},
                        'money_earned': 12000,
                        'days_survived': 30
                    }
                },
                {
                    'id': 3,
                    'name': 'Regional Director',
                    'name_ru': 'Региональный директор',
                    'salary': 900,
                    'requirements': {
                        'work_actions': 110,
                        'skills': {'charisma': 8, 'intelligence': 7},
                        'money_earned': 35000,
                        'days_survived': 55
                    }
                }
            ]
        }
    }
    
    def get_profession(self, profession: str) -> dict:
        """Get profession configuration."""
        pass
    
    def get_level(self, profession: str, level_id: int) -> dict:
        """Get specific career level configuration."""
        pass
    
    def get_next_level(self, profession: str, current_level: int) -> dict:
        """Get next career level or None if at max."""
        pass
```

### 3. CareerState

Data class representing a player's current career state.

```python
@dataclass
class CareerState:
    """
    Represents the current career state of a player.
    """
    player_id: int
    profession: str  # 'courier', 'office_worker', 'salesperson'
    career_level: int  # 0-3
    work_actions_completed: int
    total_money_earned: int
    promotion_history: list  # List of (level_id, timestamp) tuples
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for database storage."""
        pass
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CareerState':
        """Deserialize from dictionary."""
        pass
    
    def get_current_level_name(self, config: ProfessionConfig) -> str:
        """Get the display name of current career level."""
        pass
    
    def get_base_salary(self, config: ProfessionConfig) -> int:
        """Get base salary for current level."""
        pass
```

### 4. PromotionEvaluator

Evaluates promotion eligibility based on requirements.

```python
class PromotionEvaluator:
    """
    Evaluates whether a player meets promotion requirements.
    """
    
    def __init__(self, config: ProfessionConfig, skills_system):
        self.config = config
        self.skills = skills_system
    
    def evaluate(self, career_state: CareerState, player_stats: dict) -> dict:
        """
        Evaluate promotion eligibility.
        
        Args:
            career_state: Current career state
            player_stats: Dictionary with 'days_survived' and other stats
        
        Returns:
            Dictionary with:
                - eligible: bool
                - requirements_met: dict of requirement -> bool
                - progress: dict of requirement -> float (0.0-1.0)
                - next_level: dict or None
        """
        pass
    
    def check_work_actions(self, completed: int, required: int) -> tuple:
        """Check work actions requirement. Returns (met: bool, progress: float)."""
        pass
    
    def check_skills(self, player_id: int, required_skills: dict) -> tuple:
        """Check skills requirement. Returns (met: bool, progress: float)."""
        pass
    
    def check_money_earned(self, earned: int, required: int) -> tuple:
        """Check money earned requirement. Returns (met: bool, progress: float)."""
        pass
    
    def check_days_survived(self, days: int, required: int) -> tuple:
        """Check days survived requirement. Returns (met: bool, progress: float)."""
        pass
```

## Data Models

### Database Schema

```sql
-- Career state table
CREATE TABLE IF NOT EXISTS career_state (
    player_id INTEGER PRIMARY KEY,
    profession TEXT NOT NULL,
    career_level INTEGER NOT NULL DEFAULT 0,
    work_actions_completed INTEGER NOT NULL DEFAULT 0,
    total_money_earned INTEGER NOT NULL DEFAULT 0,
    promotion_history TEXT,  -- JSON array of promotion records
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES users(id)
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_career_profession ON career_state(profession);
CREATE INDEX IF NOT EXISTS idx_career_level ON career_state(career_level);
```

### Promotion History Format

```python
# Stored as JSON in database
promotion_history = [
    {
        'from_level': 0,
        'to_level': 1,
        'timestamp': '2024-01-15T10:30:00',
        'work_actions_at_promotion': 20,
        'money_earned_at_promotion': 3000
    },
    # ... more promotions
]
```

### Career Info Response Format

```python
career_info = {
    'profession': 'courier',
    'profession_display': 'Курьер',
    'current_level': {
        'id': 1,
        'name': 'Senior Courier',
        'name_ru': 'Старший курьер',
        'salary': 250
    },
    'next_level': {
        'id': 2,
        'name': 'Delivery Manager',
        'name_ru': 'Менеджер доставки',
        'salary': 400
    },
    'promotion_eligible': False,
    'requirements': {
        'work_actions': {
            'current': 35,
            'required': 50,
            'met': False,
            'progress': 0.70
        },
        'skills': {
            'current': {'strength': 4, 'endurance': 5, 'intelligence': 2},
            'required': {'strength': 5, 'endurance': 5, 'intelligence': 3},
            'met': False,
            'progress': 0.80
        },
        'money_earned': {
            'current': 8000,
            'required': 10000,
            'met': False,
            'progress': 0.80
        },
        'days_survived': {
            'current': 25,
            'required': 25,
            'met': True,
            'progress': 1.0
        }
    },
    'statistics': {
        'total_promotions': 1,
        'work_actions_completed': 35,
        'total_money_earned': 8000
    }
}
```


"""
Skills Tree System Configuration

Defines the skill tree structure, data models, and economy constants
for the "Survive Until Payday" game.

Features:
- 5 skill branches: Luck, Charisma, Intelligence, Endurance, Business
- 10 levels per skill with scaling costs
- Star economy constants for progression
- Dataclass models for type safety
"""

from dataclasses import dataclass, field
from typing import Dict, List


# ============================================================================
# STAR ECONOMY CONSTANTS
# ============================================================================

# Monthly star awards (every 30 game days)
MONTHLY_STARS = 3

# Wealth tier milestone awards
WEALTH_TIER_STARS = 5

# Major achievement awards (businessman, tycoon, etc.)
ACHIEVEMENT_STARS = 3

# One-time milestone: cumulative 1,000,000₽ earned
MILLION_EARNED_STARS = 5

# One-time milestone: survive 100 game days
SURVIVAL_100_DAYS_STARS = 10

# Skill reset refund percentage
RESET_REFUND_PERCENTAGE = 0.80  # 80% refund

# Skill reset cooldown (game days)
RESET_COOLDOWN_DAYS = 7


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class SkillNode:
    """
    Represents a skill node in the skill tree.
    
    Attributes:
        skill_id: Unique identifier for the skill
        name: Display name (in Russian)
        emoji: Visual icon for the skill
        branch: Branch category (luck, charisma, intelligence, endurance, business)
        base_cost: Base star cost (2 for basic, 3 for advanced)
        max_level: Maximum skill level (default 10)
        prerequisites: List of skill_ids that must be learned first
        description: Effect description for players
    """
    skill_id: str
    name: str
    emoji: str
    branch: str
    base_cost: int
    max_level: int = 10
    prerequisites: List[str] = field(default_factory=list)
    description: str = ""
    
    def calculate_cost(self, current_level: int) -> int:
        """
        Calculates the star cost to upgrade from current_level to current_level+1.
        
        Formula: base_cost + current_level
        
        Args:
            current_level: Current skill level (1-9)
            
        Returns:
            Star cost for next level
            
        Examples:
            - Basic skill (base_cost=2) at level 1: 2 + 1 = 3 stars
            - Basic skill at level 5: 2 + 5 = 7 stars
            - Advanced skill (base_cost=3) at level 1: 3 + 1 = 4 stars
        """
        if current_level >= self.max_level:
            return 0  # Cannot upgrade beyond max level
        return self.base_cost + current_level
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for JSON/database storage"""
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


@dataclass
class SkillData:
    """
    Player's skill progression data.
    
    Attributes:
        star_balance: Current number of stars available
        skills: Mapping of skill_id to current level (1-10)
        total_stars_spent: Cumulative stars spent on upgrades
        last_monthly_award_day: Last day monthly stars were awarded
        last_reset_day: Last day skills were reset
        milestones_claimed: List of claimed milestone identifiers
        star_history: Recent star earning events (last 10)
    """
    star_balance: int = 0
    skills: Dict[str, int] = field(default_factory=dict)
    total_stars_spent: int = 0
    last_monthly_award_day: int = 0
    last_reset_day: int = -7  # Allow immediate first reset
    milestones_claimed: List[str] = field(default_factory=list)
    star_history: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for database storage"""
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


# ============================================================================
# SKILL TREE CONFIGURATION
# ============================================================================

# Define all skill nodes in the tree
SKILL_TREE_CONFIG: Dict[str, SkillNode] = {
    # ========================================================================
    # LUCK BRANCH - Affects success rates and random outcomes
    # ========================================================================
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
    
    # ========================================================================
    # CHARISMA BRANCH - Affects social interactions and payments
    # ========================================================================
    'charisma_1': SkillNode(
        skill_id='charisma_1',
        name='Харизма I',
        emoji='💬',
        branch='charisma',
        base_cost=2,
        prerequisites=[],
        description='+5% оплата социальных подработок за уровень'
    ),
    'charisma_2': SkillNode(
        skill_id='charisma_2',
        name='Харизма II',
        emoji='🎭',
        branch='charisma',
        base_cost=2,
        prerequisites=['charisma_1'],
        description='+3% бонус к переговорам и сделкам за уровень'
    ),
    
    # ========================================================================
    # INTELLIGENCE BRANCH - Affects mental tasks and learning
    # ========================================================================
    'intelligence_1': SkillNode(
        skill_id='intelligence_1',
        name='Интеллект I',
        emoji='🧠',
        branch='intelligence',
        base_cost=2,
        prerequisites=[],
        description='+5% оплата умственных подработок за уровень'
    ),
    'intelligence_2': SkillNode(
        skill_id='intelligence_2',
        name='Интеллект II',
        emoji='📚',
        branch='intelligence',
        base_cost=2,
        prerequisites=['intelligence_1'],
        description='+3% эффективность обучения и анализа за уровень'
    ),
    
    # ========================================================================
    # ENDURANCE BRANCH - Affects survival and resource management
    # ========================================================================
    'endurance_1': SkillNode(
        skill_id='endurance_1',
        name='Выносливость I',
        emoji='💪',
        branch='endurance',
        base_cost=3,  # Advanced skill
        prerequisites=[],
        description='-3% ежедневные расходы за уровень'
    ),
    'endurance_2': SkillNode(
        skill_id='endurance_2',
        name='Выносливость II',
        emoji='🏃',
        branch='endurance',
        base_cost=3,  # Advanced skill
        prerequisites=['endurance_1'],
        description='+2% энергия и выносливость за уровень'
    ),
    
    # ========================================================================
    # BUSINESS BRANCH - Affects business operations and revenue
    # ========================================================================
    'business_1': SkillNode(
        skill_id='business_1',
        name='Бизнес I',
        emoji='💼',
        branch='business',
        base_cost=3,  # Advanced skill
        prerequisites=[],
        description='+5% доход от бизнеса за уровень'
    ),
    'business_2': SkillNode(
        skill_id='business_2',
        name='Бизнес II',
        emoji='📈',
        branch='business',
        base_cost=3,  # Advanced skill
        prerequisites=['business_1'],
        description='+3% эффективность управления бизнесом за уровень'
    ),
}


# ============================================================================
# SKILL BRANCHES METADATA
# ============================================================================

SKILL_BRANCHES = {
    'luck': {
        'name': 'Удача',
        'emoji': '🍀',
        'description': 'Влияет на случайные события и шансы успеха',
        'color': '#4CAF50'
    },
    'charisma': {
        'name': 'Харизма',
        'emoji': '💬',
        'description': 'Улучшает социальные взаимодействия и оплату',
        'color': '#2196F3'
    },
    'intelligence': {
        'name': 'Интеллект',
        'emoji': '🧠',
        'description': 'Повышает эффективность умственной работы',
        'color': '#9C27B0'
    },
    'endurance': {
        'name': 'Выносливость',
        'emoji': '💪',
        'description': 'Снижает расходы и повышает выживаемость',
        'color': '#FF9800'
    },
    'business': {
        'name': 'Бизнес',
        'emoji': '💼',
        'description': 'Увеличивает доход от бизнеса',
        'color': '#F44336'
    }
}


# ============================================================================
# SKILL EFFECTS CONFIGURATION
# ============================================================================

# Defines how each skill affects game systems
SKILL_EFFECTS = {
    'luck_1': {
        'system': 'side_jobs',
        'effect_type': 'success_rate',
        'bonus_per_level': 0.05  # 5% per level
    },
    'luck_2': {
        'system': 'entertainment',
        'effect_type': 'win_rate',
        'bonus_per_level': 0.02  # 2% per level
    },
    'charisma_1': {
        'system': 'side_jobs',
        'effect_type': 'social_payment',
        'bonus_per_level': 0.05  # 5% per level
    },
    'charisma_2': {
        'system': 'side_jobs',
        'effect_type': 'negotiation',
        'bonus_per_level': 0.03  # 3% per level
    },
    'intelligence_1': {
        'system': 'side_jobs',
        'effect_type': 'mental_payment',
        'bonus_per_level': 0.05  # 5% per level
    },
    'intelligence_2': {
        'system': 'side_jobs',
        'effect_type': 'learning',
        'bonus_per_level': 0.03  # 3% per level
    },
    'endurance_1': {
        'system': 'balance',
        'effect_type': 'expense_reduction',
        'bonus_per_level': 0.03  # 3% per level
    },
    'endurance_2': {
        'system': 'balance',
        'effect_type': 'energy',
        'bonus_per_level': 0.02  # 2% per level
    },
    'business_1': {
        'system': 'business',
        'effect_type': 'revenue',
        'bonus_per_level': 0.05  # 5% per level
    },
    'business_2': {
        'system': 'business',
        'effect_type': 'efficiency',
        'bonus_per_level': 0.03  # 3% per level
    }
}


# ============================================================================
# ACHIEVEMENT CONFIGURATION
# ============================================================================

SKILL_ACHIEVEMENTS = {
    'master': {
        'name': 'Мастер',
        'description': 'Прокачайте любой навык до максимума',
        'emoji': '⭐',
        'condition': 'any_skill_max'
    },
    'luck_master': {
        'name': 'Мастер Удачи',
        'description': 'Прокачайте все навыки ветки Удачи до максимума',
        'emoji': '🍀',
        'condition': 'branch_max',
        'branch': 'luck'
    },
    'charisma_master': {
        'name': 'Мастер Харизмы',
        'description': 'Прокачайте все навыки ветки Харизмы до максимума',
        'emoji': '💬',
        'condition': 'branch_max',
        'branch': 'charisma'
    },
    'intelligence_master': {
        'name': 'Мастер Интеллекта',
        'description': 'Прокачайте все навыки ветки Интеллекта до максимума',
        'emoji': '🧠',
        'condition': 'branch_max',
        'branch': 'intelligence'
    },
    'endurance_master': {
        'name': 'Мастер Выносливости',
        'description': 'Прокачайте все навыки ветки Выносливости до максимума',
        'emoji': '💪',
        'condition': 'branch_max',
        'branch': 'endurance'
    },
    'business_master': {
        'name': 'Мастер Бизнеса',
        'description': 'Прокачайте все навыки ветки Бизнеса до максимума',
        'emoji': '💼',
        'condition': 'branch_max',
        'branch': 'business'
    },
    'grandmaster': {
        'name': 'Грандмастер',
        'description': 'Прокачайте все навыки всех веток до максимума',
        'emoji': '👑',
        'condition': 'all_skills_max'
    },
    'big_spender': {
        'name': 'Большой Транжира',
        'description': 'Потратьте 100 звезд на навыки',
        'emoji': '💸',
        'condition': 'stars_spent',
        'threshold': 100
    }
}


# ============================================================================
# MILESTONE CONFIGURATION
# ============================================================================

MILESTONES = {
    'million_earned': {
        'name': 'Миллионер',
        'description': 'Заработайте 1,000,000₽ за всё время',
        'stars': MILLION_EARNED_STARS,
        'condition': 'cumulative_earnings',
        'threshold': 1000000
    },
    'survival_100': {
        'name': 'Столетний Выживший',
        'description': 'Проживите 100 игровых дней',
        'stars': SURVIVAL_100_DAYS_STARS,
        'condition': 'days_survived',
        'threshold': 100
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_skills_by_branch(branch: str) -> List[SkillNode]:
    """
    Returns all skills in a specific branch.
    
    Args:
        branch: Branch name (luck, charisma, intelligence, endurance, business)
        
    Returns:
        List of SkillNode objects in the branch
    """
    return [skill for skill in SKILL_TREE_CONFIG.values() if skill.branch == branch]


def get_skill_by_id(skill_id: str) -> SkillNode:
    """
    Returns a skill node by its ID.
    
    Args:
        skill_id: Skill identifier
        
    Returns:
        SkillNode object or None if not found
    """
    return SKILL_TREE_CONFIG.get(skill_id)


def get_total_cost_to_max(skill_id: str) -> int:
    """
    Calculates total stars needed to max out a skill from level 1.
    
    Args:
        skill_id: Skill identifier
        
    Returns:
        Total star cost to reach max level
        
    Example:
        Basic skill (base_cost=2):
        Level 1->2: 2+1=3
        Level 2->3: 2+2=4
        ...
        Level 9->10: 2+9=11
        Total: 3+4+5+6+7+8+9+10+11 = 63 stars
    """
    skill = get_skill_by_id(skill_id)
    if not skill:
        return 0
    
    total = 0
    for level in range(1, skill.max_level):
        total += skill.calculate_cost(level)
    return total


def initialize_default_skills() -> Dict[str, int]:
    """
    Initializes default skill levels for a new player.
    All skills start at level 1.
    
    Returns:
        Dictionary mapping skill_id to level 1
    """
    return {skill_id: 1 for skill_id in SKILL_TREE_CONFIG.keys()}


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_skill_level(level: int) -> bool:
    """
    Validates that a skill level is within valid bounds (1-10).
    
    Args:
        level: Skill level to validate
        
    Returns:
        True if valid, False otherwise
    """
    return 1 <= level <= 10


def validate_star_balance(balance: int) -> bool:
    """
    Validates that star balance is non-negative.
    
    Args:
        balance: Star balance to validate
        
    Returns:
        True if valid, False otherwise
    """
    return balance >= 0

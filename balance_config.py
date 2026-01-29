# -*- coding: utf-8 -*-
"""
Economy Balancing System Configuration

This module contains all configuration parameters for the economy balancing system.
All values can be modified here without changing code.
"""

# ============================================================================
# DAILY EXPENSES
# ============================================================================

DAILY_EXPENSES = {
    'food': 30,        # Minimum food cost per day (₽) - reduced from 50
    'transport': 20,   # Minimum transport cost per day (₽) - reduced from 30
}

# ============================================================================
# JOB INCOME RATES (REDUCED FROM ORIGINAL)
# ============================================================================

JOB_INCOME = {
    'delivery': 150,   # Was 80₽ - adjusted for balance
    'office': 200,     # Was 120₽ - adjusted for balance
    'freelance': 300,  # Was 200₽ - adjusted for balance
    'crypto': 450,     # Was 300₽ - adjusted for balance
}

# Original rates for reference (not used in calculations)
ORIGINAL_JOB_INCOME = {
    'delivery': 80,
    'office': 120,
    'freelance': 200,
    'crypto': 300,
}

# ============================================================================
# WEALTH TIERS
# ============================================================================

WEALTH_TIERS = {
    'poor': {
        'min': 0,
        'max': 3000,
        'multiplier': 1.0,
        'name': 'Бедный',
        'emoji': '💸'
    },
    'middle': {
        'min': 3001,
        'max': 10000,
        'multiplier': 1.5,
        'name': 'Средний класс',
        'emoji': '💰'
    },
    'rich': {
        'min': 10001,
        'max': float('inf'),
        'multiplier': 2.0,
        'name': 'Богатый',
        'emoji': '💎'
    }
}

# ============================================================================
# NEGATIVE EVENTS
# ============================================================================

NEGATIVE_EVENTS = {
    'medical_emergency': {
        'min_cost': 500,
        'max_cost': 1500,
        'name': 'Медицинская помощь',
        'description': 'Внезапная болезнь требует лечения',
        'emoji': '🏥'
    },
    'fine': {
        'min_cost': 300,
        'max_cost': 800,
        'name': 'Штраф',
        'description': 'Административный штраф',
        'emoji': '🚔'
    },
    'equipment_breakdown': {
        'min_cost': 400,
        'max_cost': 1200,
        'name': 'Поломка техники',
        'description': 'Сломался телефон/компьютер',
        'emoji': '💻'
    },
    'unexpected_bill': {
        'min_cost': 200,
        'max_cost': 600,
        'name': 'Неожиданный счет',
        'description': 'Пришел неожиданный счет',
        'emoji': '📄'
    }
}

# ============================================================================
# EVENT PROBABILITIES
# ============================================================================

EVENT_PROBABILITY = {
    'base': 0.25,           # 25% chance per day (normal conditions)
    'debt_3_days': 0.40,    # 40% chance when in debt for 3+ days
}

# ============================================================================
# DEBT SETTINGS
# ============================================================================

DEBT_SETTINGS = {
    'collector_trigger_days': 7,      # Debt collector appears after 7 days
    'collector_percentage': 0.20,     # Debt collector takes 20% of debt
    'high_probability_days': 3,       # Event probability increases after 3 days
}

# ============================================================================
# BUDGET SURVIVAL MECHANICS
# ============================================================================

SURVIVAL_SETTINGS = {
    'expense_to_income_min': 0.50,    # Minimum ratio of expenses to income
    'expense_to_income_max': 0.70,    # Maximum ratio of expenses to income
    'days_to_negative': 3,            # Days without work to go negative
    'days_to_debt_500': 5,            # Days without work to reach 500₽ debt
}

# ============================================================================
# HISTORY SETTINGS
# ============================================================================

HISTORY_SETTINGS = {
    'max_days': 30,                   # Maximum days to keep in history
    'auto_cleanup': True,             # Automatically cleanup old records
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_wealth_tier_by_balance(balance: float) -> str:
    """
    Determines wealth tier based on balance.
    
    Args:
        balance: Current player balance
        
    Returns:
        Tier name: 'poor', 'middle', or 'rich'
    """
    for tier_name, tier_config in WEALTH_TIERS.items():
        if tier_config['min'] <= balance <= tier_config['max']:
            return tier_name
    return 'poor'  # Default fallback


def get_expense_multiplier(tier: str) -> float:
    """
    Returns expense multiplier for given tier.
    
    Args:
        tier: Wealth tier name
        
    Returns:
        Multiplier value (1.0, 1.5, or 2.0)
    """
    return WEALTH_TIERS.get(tier, WEALTH_TIERS['poor'])['multiplier']


def get_event_probability(debt_days: int) -> float:
    """
    Returns event probability based on debt days.
    
    Args:
        debt_days: Number of consecutive days in debt
        
    Returns:
        Probability value (0.25 or 0.40)
    """
    if debt_days >= DEBT_SETTINGS['high_probability_days']:
        return EVENT_PROBABILITY['debt_3_days']
    return EVENT_PROBABILITY['base']

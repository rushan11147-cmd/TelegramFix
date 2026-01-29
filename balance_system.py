# -*- coding: utf-8 -*-
"""
Economy Balancing System

This module implements the economy balancing system for "Survive Until Payday" game.
It manages daily expenses, income adjustments, negative events, and wealth tiers.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import random
from balance_config import (
    DAILY_EXPENSES, JOB_INCOME, WEALTH_TIERS, NEGATIVE_EVENTS,
    EVENT_PROBABILITY, DEBT_SETTINGS, HISTORY_SETTINGS,
    get_wealth_tier_by_balance, get_expense_multiplier, get_event_probability
)


# ============================================================================
# EXPENSE CALCULATOR
# ============================================================================

class ExpenseCalculator:
    """Calculates daily expenses for player"""
    
    def calculate_daily_expenses(self, user_data: Dict) -> Dict:
        """
        Calculates total daily expenses with breakdown.
        
        Args:
            user_data: Player data including balance, property, wealth tier
            
        Returns:
            {
                'rent': float,
                'food': float,
                'transport': float,
                'base_total': float,
                'tier_multiplier': float,
                'final_total': float
            }
        """
        # Calculate rent
        rent = self.calculate_rent(user_data)
        
        # Get base expenses
        base_expenses = self.get_base_expenses()
        food = base_expenses['food']
        transport = base_expenses['transport']
        
        # Calculate base total
        base_total = rent + food + transport
        
        # Get wealth tier multiplier
        balance = user_data.get('money', 0)
        tier = get_wealth_tier_by_balance(balance)
        tier_multiplier = get_expense_multiplier(tier)
        
        # Calculate final total with multiplier
        final_total = base_total * tier_multiplier
        
        return {
            'rent': rent,
            'food': food,
            'transport': transport,
            'base_total': base_total,
            'tier': tier,
            'tier_multiplier': tier_multiplier,
            'final_total': final_total,
            'date': datetime.now().isoformat()
        }
    
    def calculate_rent(self, user_data: Dict) -> float:
        """
        Calculates daily rent from monthly property rent.
        Formula: monthly_rent / 30
        
        Args:
            user_data: Player data with monthly_rent field
            
        Returns:
            Daily rent amount
        """
        monthly_rent = user_data.get('monthly_rent', 0)
        
        # Handle edge case: if monthly_rent is 0 or missing
        if monthly_rent <= 0:
            return 0.0
        
        # Calculate daily rent
        daily_rent = monthly_rent / 30.0
        
        return round(daily_rent, 2)
    
    def get_base_expenses(self) -> Dict:
        """
        Returns base food and transport costs.
        
        Returns:
            {'food': float, 'transport': float}
        """
        return {
            'food': DAILY_EXPENSES['food'],
            'transport': DAILY_EXPENSES['transport']
        }


# ============================================================================
# WEALTH TIER MANAGER
# ============================================================================

class WealthTierManager:
    """Manages player wealth tier classification"""
    
    def get_wealth_tier(self, balance: float) -> str:
        """
        Determines wealth tier based on current balance.
        
        Args:
            balance: Current player balance
            
        Returns:
            'poor', 'middle', or 'rich'
        """
        return get_wealth_tier_by_balance(balance)
    
    def get_expense_multiplier(self, tier: str) -> float:
        """
        Returns expense multiplier for tier.
        
        Args:
            tier: Wealth tier name
            
        Returns:
            Multiplier (1.0, 1.5, or 2.0)
        """
        return get_expense_multiplier(tier)
    
    def check_tier_change(self, user_data: Dict, new_balance: float) -> Optional[str]:
        """
        Checks if player changed wealth tier.
        
        Args:
            user_data: Current player data
            new_balance: New balance after transaction
            
        Returns:
            New tier name if changed, None otherwise
        """
        # Get current tier
        current_balance = user_data.get('money', 0)
        current_tier = self.get_wealth_tier(current_balance)
        
        # Get new tier
        new_tier = self.get_wealth_tier(new_balance)
        
        # Check if tier changed
        if current_tier != new_tier:
            return new_tier
        
        return None
    
    def get_tier_info(self, tier: str) -> Dict:
        """
        Returns full information about a tier.
        
        Args:
            tier: Tier name
            
        Returns:
            Tier configuration dict
        """
        return WEALTH_TIERS.get(tier, WEALTH_TIERS['poor'])


# ============================================================================
# DEBT TRACKER
# ============================================================================

class DebtTracker:
    """Tracks player debt and applies consequences"""
    
    def track_debt(self, user_data: Dict) -> None:
        """
        Updates debt tracking when balance is negative.
        Tracks consecutive days in debt.
        
        Args:
            user_data: Player data (modified in place)
        """
        balance = user_data.get('money', 0)
        
        # Initialize balance_data if not exists
        if 'balance_data' not in user_data:
            user_data['balance_data'] = {
                'wealth_tier': 'poor',
                'debt_days': 0,
                'last_expense_breakdown': {}
            }
        
        # If balance is negative, increment debt days
        if balance < 0:
            user_data['balance_data']['debt_days'] = user_data['balance_data'].get('debt_days', 0) + 1
        else:
            # Reset debt days if balance is positive
            user_data['balance_data']['debt_days'] = 0
    
    def get_debt_amount(self, balance: float) -> float:
        """
        Returns absolute debt amount (positive number).
        
        Args:
            balance: Current balance
            
        Returns:
            Debt amount (0 if balance is positive)
        """
        if balance < 0:
            return abs(balance)
        return 0.0
    
    def get_debt_days(self, user_data: Dict) -> int:
        """
        Returns consecutive days in debt.
        
        Args:
            user_data: Player data
            
        Returns:
            Number of days in debt
        """
        if 'balance_data' not in user_data:
            return 0
        return user_data['balance_data'].get('debt_days', 0)
    
    def should_trigger_collector(self, user_data: Dict) -> bool:
        """
        Returns True if debt collector event should trigger.
        
        Args:
            user_data: Player data
            
        Returns:
            True if collector should trigger
        """
        debt_days = self.get_debt_days(user_data)
        balance = user_data.get('money', 0)
        
        # Trigger if in debt for 7+ days
        return balance < 0 and debt_days >= DEBT_SETTINGS['collector_trigger_days']
    
    def calculate_collector_cost(self, debt_amount: float) -> float:
        """
        Calculates debt collector cost (20% of debt).
        
        Args:
            debt_amount: Current debt amount
            
        Returns:
            Collector cost
        """
        return round(debt_amount * DEBT_SETTINGS['collector_percentage'], 2)
    
    def get_event_probability_modifier(self, debt_days: int) -> float:
        """
        Returns modified event probability based on debt days.
        3+ days: 40%, otherwise: 25%
        
        Args:
            debt_days: Number of days in debt
            
        Returns:
            Event probability
        """
        return get_event_probability(debt_days)


# ============================================================================
# NEGATIVE EVENT MANAGER
# ============================================================================

class NegativeEventManager:
    """Manages negative random events"""
    
    def should_trigger_event(self, base_probability: float) -> bool:
        """
        Determines if event should trigger based on probability.
        
        Args:
            base_probability: Base probability (0.25 or 0.40)
            
        Returns:
            True if event triggers
        """
        return random.random() < base_probability
    
    def select_random_event(self) -> Dict:
        """
        Selects random event from pool.
        
        Returns:
            Event configuration with cost range, name, emoji
        """
        event_type = random.choice(list(NEGATIVE_EVENTS.keys()))
        return {
            'type': event_type,
            **NEGATIVE_EVENTS[event_type]
        }
    
    def calculate_event_cost(self, event_config: Dict) -> int:
        """
        Calculates random cost within event's range.
        
        Args:
            event_config: Event configuration
            
        Returns:
            Random cost between min_cost and max_cost
        """
        min_cost = event_config['min_cost']
        max_cost = event_config['max_cost']
        return random.randint(min_cost, max_cost)
    
    def apply_event(self, user_data: Dict, event: Dict, cost: int) -> Dict:
        """
        Applies event to player (deducts cost, records history).
        
        Args:
            user_data: Player data (modified in place)
            event: Event configuration
            cost: Event cost
            
        Returns:
            Event result summary
        """
        # Deduct cost from balance
        user_data['money'] = user_data.get('money', 0) - cost
        
        # Return event summary
        return {
            'event_type': event['type'],
            'name': event['name'],
            'description': event.get('description', ''),
            'emoji': event['emoji'],
            'cost': cost,
            'new_balance': user_data['money'],
            'date': datetime.now().isoformat()
        }


# ============================================================================
# FINANCIAL HISTORY MANAGER
# ============================================================================

class FinancialHistoryManager:
    """Manages financial history tracking"""
    
    def __init__(self):
        """Initialize history manager"""
        self.max_days = HISTORY_SETTINGS['max_days']
    
    def record_daily_expenses(self, user_data: Dict, expense_data: Dict) -> None:
        """
        Records daily expense breakdown.
        
        Args:
            user_data: Player data (modified in place)
            expense_data: Expense breakdown
        """
        self._ensure_history_structure(user_data)
        
        # Add expense record
        user_data['financial_history']['expenses'].append(expense_data)
        
        # Cleanup old records
        self._cleanup_old_records(user_data, 'expenses')
    
    def record_daily_income(self, user_data: Dict, income_data: Dict) -> None:
        """
        Records daily income by source.
        
        Args:
            user_data: Player data (modified in place)
            income_data: Income information
        """
        self._ensure_history_structure(user_data)
        
        # Add income record
        income_record = {
            'date': datetime.now().isoformat(),
            **income_data
        }
        user_data['financial_history']['income'].append(income_record)
        
        # Cleanup old records
        self._cleanup_old_records(user_data, 'income')
    
    def record_negative_event(self, user_data: Dict, event_data: Dict) -> None:
        """
        Records negative event occurrence.
        
        Args:
            user_data: Player data (modified in place)
            event_data: Event information
        """
        self._ensure_history_structure(user_data)
        
        # Add event record
        user_data['financial_history']['events'].append(event_data)
        
        # Cleanup old records
        self._cleanup_old_records(user_data, 'events')
    
    def record_tier_change(self, user_data: Dict, old_tier: str, new_tier: str) -> None:
        """
        Records wealth tier change.
        
        Args:
            user_data: Player data (modified in place)
            old_tier: Previous tier
            new_tier: New tier
        """
        self._ensure_history_structure(user_data)
        
        # Add tier change record
        tier_change = {
            'date': datetime.now().isoformat(),
            'old_tier': old_tier,
            'new_tier': new_tier,
            'balance': user_data.get('money', 0)
        }
        user_data['financial_history']['tier_changes'].append(tier_change)
        
        # Cleanup old records
        self._cleanup_old_records(user_data, 'tier_changes')
    
    def get_history(self, user_data: Dict, days: int = 30) -> Dict:
        """
        Retrieves financial history for last N days.
        
        Args:
            user_data: Player data
            days: Number of days to retrieve
            
        Returns:
            {
                'expenses': List[Dict],
                'income': List[Dict],
                'events': List[Dict],
                'tier_changes': List[Dict]
            }
        """
        self._ensure_history_structure(user_data)
        
        # Get cutoff date
        cutoff_date = datetime.now()
        cutoff_timestamp = cutoff_date.timestamp() - (days * 24 * 60 * 60)
        
        # Filter records by date
        history = user_data['financial_history']
        
        def filter_by_date(records):
            filtered = []
            for record in records:
                try:
                    record_date = datetime.fromisoformat(record['date'])
                    if record_date.timestamp() >= cutoff_timestamp:
                        filtered.append(record)
                except:
                    # If date parsing fails, include the record
                    filtered.append(record)
            return filtered
        
        return {
            'expenses': filter_by_date(history.get('expenses', [])),
            'income': filter_by_date(history.get('income', [])),
            'events': filter_by_date(history.get('events', [])),
            'tier_changes': filter_by_date(history.get('tier_changes', []))
        }
    
    def _ensure_history_structure(self, user_data: Dict) -> None:
        """Ensures financial_history structure exists"""
        if 'financial_history' not in user_data:
            user_data['financial_history'] = {
                'expenses': [],
                'income': [],
                'events': [],
                'tier_changes': []
            }
    
    def _cleanup_old_records(self, user_data: Dict, record_type: str) -> None:
        """
        Removes records older than max_days.
        
        Args:
            user_data: Player data
            record_type: Type of records to cleanup
        """
        if not HISTORY_SETTINGS['auto_cleanup']:
            return
        
        cutoff_date = datetime.now()
        cutoff_timestamp = cutoff_date.timestamp() - (self.max_days * 24 * 60 * 60)
        
        records = user_data['financial_history'].get(record_type, [])
        filtered_records = []
        
        for record in records:
            try:
                record_date = datetime.fromisoformat(record['date'])
                if record_date.timestamp() >= cutoff_timestamp:
                    filtered_records.append(record)
            except:
                # If date parsing fails, keep the record
                filtered_records.append(record)
        
        user_data['financial_history'][record_type] = filtered_records


# ============================================================================
# BALANCE MANAGER (MAIN ORCHESTRATOR)
# ============================================================================

class BalanceManager:
    """Main orchestrator for economy balancing system"""
    
    def __init__(self, get_user_func, save_user_func):
        """
        Initialize with database access functions.
        
        Args:
            get_user_func: Function to get user data
            save_user_func: Function to save user data
        """
        self.get_user = get_user_func
        self.save_user = save_user_func
        self.expense_calculator = ExpenseCalculator()
        self.wealth_tier_manager = WealthTierManager()
        self.debt_tracker = DebtTracker()
        self.event_manager = NegativeEventManager()
        self.history_manager = FinancialHistoryManager()
    
    def process_new_day(self, user_id: str) -> Dict:
        """
        Processes all balance operations for new day:
        1. Calculate and deduct daily expenses
        2. Check and update wealth tier
        3. Track debt if balance negative
        4. Trigger negative events
        5. Record history
        
        Args:
            user_id: Player ID
            
        Returns:
            Summary of operations performed
        """
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        result = {
            'success': True,
            'expenses': None,
            'tier_change': None,
            'event': None,
            'debt_info': None
        }
        
        # 1. Calculate and deduct daily expenses
        expenses = self.expense_calculator.calculate_daily_expenses(user)
        user['money'] = user.get('money', 0) - expenses['final_total']
        
        # Store last expense breakdown
        if 'balance_data' not in user:
            user['balance_data'] = {}
        user['balance_data']['last_expense_breakdown'] = expenses
        
        # Record expenses in history
        self.history_manager.record_daily_expenses(user, expenses)
        result['expenses'] = expenses
        
        # 2. Check and update wealth tier
        old_tier = user['balance_data'].get('wealth_tier', 'poor')
        new_tier = self.wealth_tier_manager.get_wealth_tier(user['money'])
        
        if old_tier != new_tier:
            user['balance_data']['wealth_tier'] = new_tier
            self.history_manager.record_tier_change(user, old_tier, new_tier)
            result['tier_change'] = {
                'old': old_tier,
                'new': new_tier
            }
        
        # 3. Track debt if balance negative
        self.debt_tracker.track_debt(user)
        debt_days = self.debt_tracker.get_debt_days(user)
        debt_amount = self.debt_tracker.get_debt_amount(user['money'])
        
        result['debt_info'] = {
            'in_debt': user['money'] < 0,
            'debt_amount': debt_amount,
            'debt_days': debt_days
        }
        
        # 4. Check for debt collector
        if self.debt_tracker.should_trigger_collector(user):
            collector_cost = self.debt_tracker.calculate_collector_cost(debt_amount)
            user['money'] -= collector_cost
            
            # Record as special event
            collector_event = {
                'event_type': 'debt_collector',
                'name': 'Коллектор',
                'description': f'Коллектор забрал {collector_cost}₽',
                'emoji': '👔',
                'cost': collector_cost,
                'new_balance': user['money'],
                'date': datetime.now().isoformat()
            }
            self.history_manager.record_negative_event(user, collector_event)
            result['event'] = collector_event
        else:
            # 5. Trigger negative events (if no collector)
            event_probability = self.debt_tracker.get_event_probability_modifier(debt_days)
            
            if self.event_manager.should_trigger_event(event_probability):
                event = self.event_manager.select_random_event()
                cost = self.event_manager.calculate_event_cost(event)
                event_result = self.event_manager.apply_event(user, event, cost)
                
                # Record event in history
                self.history_manager.record_negative_event(user, event_result)
                result['event'] = event_result
        
        # Save user data
        self.save_user(user_id, user)
        
        return result
    
    def apply_job_income(self, user_id: str, job_type: str) -> Dict:
        """
        Applies reduced job income to player.
        
        Args:
            user_id: Player ID
            job_type: 'delivery', 'office', 'freelance', 'crypto'
            
        Returns:
            Income amount and updated balance
        """
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        # Get income amount
        if job_type not in JOB_INCOME:
            return {'success': False, 'error': f'Invalid job type: {job_type}'}
        
        income = JOB_INCOME[job_type]
        
        # Apply income
        user['money'] = user.get('money', 0) + income
        
        # Record income in history
        income_data = {
            'source': job_type,
            'amount': income
        }
        self.history_manager.record_daily_income(user, income_data)
        
        # Check for tier change
        old_tier = user.get('balance_data', {}).get('wealth_tier', 'poor')
        new_tier = self.wealth_tier_manager.get_wealth_tier(user['money'])
        
        tier_changed = False
        if old_tier != new_tier:
            if 'balance_data' not in user:
                user['balance_data'] = {}
            user['balance_data']['wealth_tier'] = new_tier
            self.history_manager.record_tier_change(user, old_tier, new_tier)
            tier_changed = True
        
        # Save user data
        self.save_user(user_id, user)
        
        return {
            'success': True,
            'job_type': job_type,
            'income': income,
            'new_balance': user['money'],
            'tier_changed': tier_changed,
            'new_tier': new_tier if tier_changed else old_tier
        }
    
    def get_financial_summary(self, user_id: str) -> Dict:
        """
        Returns current financial status.
        
        Args:
            user_id: Player ID
            
        Returns:
            {
                'balance': float,
                'wealth_tier': str,
                'debt_amount': float,
                'debt_days': int,
                'last_expenses': Dict,
                'event_probability': float
            }
        """
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        balance = user.get('money', 0)
        debt_days = self.debt_tracker.get_debt_days(user)
        debt_amount = self.debt_tracker.get_debt_amount(balance)
        tier = self.wealth_tier_manager.get_wealth_tier(balance)
        event_probability = self.debt_tracker.get_event_probability_modifier(debt_days)
        
        last_expenses = user.get('balance_data', {}).get('last_expense_breakdown', {})
        
        return {
            'success': True,
            'balance': balance,
            'wealth_tier': tier,
            'tier_info': self.wealth_tier_manager.get_tier_info(tier),
            'debt_amount': debt_amount,
            'debt_days': debt_days,
            'in_debt': balance < 0,
            'last_expenses': last_expenses,
            'event_probability': event_probability,
            'collector_warning': debt_days >= DEBT_SETTINGS['collector_trigger_days'] - 1
        }

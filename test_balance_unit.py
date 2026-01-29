# -*- coding: utf-8 -*-
"""
Unit Tests for Economy Balancing System

These tests verify specific examples and edge cases.
"""

import pytest
from balance_system import (
    ExpenseCalculator, WealthTierManager, DebtTracker,
    NegativeEventManager, FinancialHistoryManager, BalanceManager
)
from balance_config import DAILY_EXPENSES, JOB_INCOME, WEALTH_TIERS


# ============================================================================
# EXPENSE CALCULATOR TESTS
# ============================================================================

class TestExpenseCalculator:
    """Unit tests for ExpenseCalculator"""
    
    def test_calculate_rent_with_valid_monthly_rent(self):
        """Test rent calculation with various monthly rent values"""
        calculator = ExpenseCalculator()
        
        # Test case 1: 3000₽ monthly rent
        user_data = {'monthly_rent': 3000}
        rent = calculator.calculate_rent(user_data)
        assert rent == 100.0, f"Expected 100.0, got {rent}"
        
        # Test case 2: 6000₽ monthly rent
        user_data = {'monthly_rent': 6000}
        rent = calculator.calculate_rent(user_data)
        assert rent == 200.0, f"Expected 200.0, got {rent}"
        
        # Test case 3: 15000₽ monthly rent
        user_data = {'monthly_rent': 15000}
        rent = calculator.calculate_rent(user_data)
        assert rent == 500.0, f"Expected 500.0, got {rent}"
    
    def test_calculate_rent_with_zero_rent(self):
        """Test rent calculation when monthly rent is 0"""
        calculator = ExpenseCalculator()
        user_data = {'monthly_rent': 0}
        rent = calculator.calculate_rent(user_data)
        assert rent == 0.0, f"Expected 0.0, got {rent}"
    
    def test_calculate_rent_with_missing_rent(self):
        """Test rent calculation when monthly_rent is missing"""
        calculator = ExpenseCalculator()
        user_data = {}
        rent = calculator.calculate_rent(user_data)
        assert rent == 0.0, f"Expected 0.0, got {rent}"
    
    def test_get_base_expenses(self):
        """Test that base expenses return correct minimums"""
        calculator = ExpenseCalculator()
        expenses = calculator.get_base_expenses()
        
        assert expenses['food'] == 30, f"Expected food=30, got {expenses['food']}"
        assert expenses['transport'] == 20, f"Expected transport=20, got {expenses['transport']}"
    
    def test_calculate_daily_expenses_poor_tier(self):
        """Test daily expense calculation for poor tier (multiplier 1.0)"""
        calculator = ExpenseCalculator()
        user_data = {
            'money': 1000,  # Poor tier
            'monthly_rent': 3000
        }
        
        expenses = calculator.calculate_daily_expenses(user_data)
        
        # Check components
        assert expenses['rent'] == 100.0
        assert expenses['food'] == 30
        assert expenses['transport'] == 20
        assert expenses['base_total'] == 150.0
        assert expenses['tier'] == 'poor'
        assert expenses['tier_multiplier'] == 1.0
        assert expenses['final_total'] == 150.0
    
    def test_calculate_daily_expenses_middle_tier(self):
        """Test daily expense calculation for middle tier (multiplier 1.5)"""
        calculator = ExpenseCalculator()
        user_data = {
            'money': 5000,  # Middle tier
            'monthly_rent': 6000
        }
        
        expenses = calculator.calculate_daily_expenses(user_data)
        
        # Check components
        assert expenses['rent'] == 200.0
        assert expenses['food'] == 30
        assert expenses['transport'] == 20
        assert expenses['base_total'] == 250.0
        assert expenses['tier'] == 'middle'
        assert expenses['tier_multiplier'] == 1.5
        assert expenses['final_total'] == 375.0  # 250 * 1.5
    
    def test_calculate_daily_expenses_rich_tier(self):
        """Test daily expense calculation for rich tier (multiplier 2.0)"""
        calculator = ExpenseCalculator()
        user_data = {
            'money': 15000,  # Rich tier
            'monthly_rent': 15000
        }
        
        expenses = calculator.calculate_daily_expenses(user_data)
        
        # Check components
        assert expenses['rent'] == 500.0
        assert expenses['food'] == 30
        assert expenses['transport'] == 20
        assert expenses['base_total'] == 550.0
        assert expenses['tier'] == 'rich'
        assert expenses['tier_multiplier'] == 2.0
        assert expenses['final_total'] == 1100.0  # 550 * 2.0


# ============================================================================
# WEALTH TIER MANAGER TESTS
# ============================================================================

class TestWealthTierManager:
    """Unit tests for WealthTierManager"""
    
    def test_tier_boundaries(self):
        """Test tier classification at boundary values"""
        manager = WealthTierManager()
        
        # Poor tier boundaries
        assert manager.get_wealth_tier(0) == 'poor'
        assert manager.get_wealth_tier(1500) == 'poor'
        assert manager.get_wealth_tier(3000) == 'poor'
        
        # Middle tier boundaries
        assert manager.get_wealth_tier(3001) == 'middle'
        assert manager.get_wealth_tier(5000) == 'middle'
        assert manager.get_wealth_tier(10000) == 'middle'
        
        # Rich tier boundaries
        assert manager.get_wealth_tier(10001) == 'rich'
        assert manager.get_wealth_tier(50000) == 'rich'
        assert manager.get_wealth_tier(1000000) == 'rich'
    
    def test_negative_balance_tier(self):
        """Test tier classification with negative balance"""
        manager = WealthTierManager()
        assert manager.get_wealth_tier(-500) == 'poor'
        assert manager.get_wealth_tier(-5000) == 'poor'
    
    def test_expense_multipliers(self):
        """Test correct multipliers for each tier"""
        manager = WealthTierManager()
        
        assert manager.get_expense_multiplier('poor') == 1.0
        assert manager.get_expense_multiplier('middle') == 1.5
        assert manager.get_expense_multiplier('rich') == 2.0
    
    def test_check_tier_change_no_change(self):
        """Test tier change detection when tier doesn't change"""
        manager = WealthTierManager()
        user_data = {'money': 2000}  # Poor tier
        
        # New balance still in poor tier
        result = manager.check_tier_change(user_data, 2500)
        assert result is None
    
    def test_check_tier_change_poor_to_middle(self):
        """Test tier change from poor to middle"""
        manager = WealthTierManager()
        user_data = {'money': 2000}  # Poor tier
        
        # New balance in middle tier
        result = manager.check_tier_change(user_data, 5000)
        assert result == 'middle'
    
    def test_check_tier_change_middle_to_rich(self):
        """Test tier change from middle to rich"""
        manager = WealthTierManager()
        user_data = {'money': 5000}  # Middle tier
        
        # New balance in rich tier
        result = manager.check_tier_change(user_data, 15000)
        assert result == 'rich'
    
    def test_check_tier_change_downgrade(self):
        """Test tier change when downgrading"""
        manager = WealthTierManager()
        user_data = {'money': 5000}  # Middle tier
        
        # New balance in poor tier
        result = manager.check_tier_change(user_data, 2000)
        assert result == 'poor'


# ============================================================================
# DEBT TRACKER TESTS
# ============================================================================

class TestDebtTracker:
    """Unit tests for DebtTracker"""
    
    def test_get_debt_amount_negative_balance(self):
        """Test debt amount calculation with negative balance"""
        tracker = DebtTracker()
        
        assert tracker.get_debt_amount(-500) == 500
        assert tracker.get_debt_amount(-1234.56) == 1234.56
    
    def test_get_debt_amount_positive_balance(self):
        """Test debt amount with positive balance"""
        tracker = DebtTracker()
        
        assert tracker.get_debt_amount(500) == 0.0
        assert tracker.get_debt_amount(0) == 0.0
    
    def test_track_debt_increments_days(self):
        """Test that debt days increment when balance is negative"""
        tracker = DebtTracker()
        user_data = {
            'money': -500,
            'balance_data': {'debt_days': 2}
        }
        
        tracker.track_debt(user_data)
        assert user_data['balance_data']['debt_days'] == 3
    
    def test_track_debt_resets_on_positive_balance(self):
        """Test that debt days reset when balance becomes positive"""
        tracker = DebtTracker()
        user_data = {
            'money': 500,
            'balance_data': {'debt_days': 5}
        }
        
        tracker.track_debt(user_data)
        assert user_data['balance_data']['debt_days'] == 0
    
    def test_should_trigger_collector_after_7_days(self):
        """Test debt collector trigger after 7 days"""
        tracker = DebtTracker()
        user_data = {
            'money': -1000,
            'balance_data': {'debt_days': 7}
        }
        
        assert tracker.should_trigger_collector(user_data) is True
    
    def test_should_not_trigger_collector_before_7_days(self):
        """Test debt collector doesn't trigger before 7 days"""
        tracker = DebtTracker()
        user_data = {
            'money': -1000,
            'balance_data': {'debt_days': 6}
        }
        
        assert tracker.should_trigger_collector(user_data) is False
    
    def test_should_not_trigger_collector_positive_balance(self):
        """Test debt collector doesn't trigger with positive balance"""
        tracker = DebtTracker()
        user_data = {
            'money': 500,
            'balance_data': {'debt_days': 10}
        }
        
        assert tracker.should_trigger_collector(user_data) is False
    
    def test_calculate_collector_cost(self):
        """Test debt collector cost calculation (20% of debt)"""
        tracker = DebtTracker()
        
        assert tracker.calculate_collector_cost(1000) == 200.0
        assert tracker.calculate_collector_cost(5000) == 1000.0
        assert tracker.calculate_collector_cost(250) == 50.0
    
    def test_event_probability_modifier_normal(self):
        """Test event probability for normal conditions"""
        tracker = DebtTracker()
        
        assert tracker.get_event_probability_modifier(0) == 0.25
        assert tracker.get_event_probability_modifier(1) == 0.25
        assert tracker.get_event_probability_modifier(2) == 0.25
    
    def test_event_probability_modifier_high_debt(self):
        """Test event probability increases after 3 days in debt"""
        tracker = DebtTracker()
        
        assert tracker.get_event_probability_modifier(3) == 0.40
        assert tracker.get_event_probability_modifier(5) == 0.40
        assert tracker.get_event_probability_modifier(10) == 0.40


# ============================================================================
# NEGATIVE EVENT MANAGER TESTS
# ============================================================================

class TestNegativeEventManager:
    """Unit tests for NegativeEventManager"""
    
    def test_select_random_event_returns_valid_type(self):
        """Test that random event selection returns valid event types"""
        manager = NegativeEventManager()
        valid_types = ['medical_emergency', 'fine', 'equipment_breakdown', 'unexpected_bill']
        
        # Test multiple times to check randomness
        for _ in range(20):
            event = manager.select_random_event()
            assert event['type'] in valid_types
            assert 'name' in event
            assert 'emoji' in event
            assert 'min_cost' in event
            assert 'max_cost' in event
    
    def test_calculate_event_cost_within_range(self):
        """Test that event cost is within configured range"""
        manager = NegativeEventManager()
        
        event = {
            'type': 'fine',
            'min_cost': 300,
            'max_cost': 800
        }
        
        # Test multiple times
        for _ in range(20):
            cost = manager.calculate_event_cost(event)
            assert 300 <= cost <= 800
    
    def test_apply_event_deducts_cost(self):
        """Test that applying event deducts cost from balance"""
        manager = NegativeEventManager()
        user_data = {'money': 5000}
        
        event = {
            'type': 'fine',
            'name': 'Штраф',
            'emoji': '🚔'
        }
        cost = 500
        
        result = manager.apply_event(user_data, event, cost)
        
        assert user_data['money'] == 4500
        assert result['cost'] == 500
        assert result['new_balance'] == 4500
        assert result['event_type'] == 'fine'


# ============================================================================
# FINANCIAL HISTORY MANAGER TESTS
# ============================================================================

class TestFinancialHistoryManager:
    """Unit tests for FinancialHistoryManager"""
    
    def test_record_daily_expenses(self):
        """Test recording daily expenses"""
        from datetime import datetime
        
        manager = FinancialHistoryManager()
        user_data = {'money': 5000}
        
        expense_data = {
            'rent': 100,
            'food': 50,
            'transport': 30,
            'final_total': 180,
            'date': datetime.now().isoformat()
        }
        
        manager.record_daily_expenses(user_data, expense_data)
        
        assert 'financial_history' in user_data
        assert len(user_data['financial_history']['expenses']) == 1
        assert user_data['financial_history']['expenses'][0]['rent'] == 100
    
    def test_record_daily_income(self):
        """Test recording daily income"""
        manager = FinancialHistoryManager()
        user_data = {'money': 5000}
        
        income_data = {
            'source': 'delivery',
            'amount': 50
        }
        
        manager.record_daily_income(user_data, income_data)
        
        assert 'financial_history' in user_data
        assert len(user_data['financial_history']['income']) == 1
        assert user_data['financial_history']['income'][0]['source'] == 'delivery'
    
    def test_record_negative_event(self):
        """Test recording negative event"""
        from datetime import datetime
        
        manager = FinancialHistoryManager()
        user_data = {'money': 5000}
        
        event_data = {
            'event_type': 'fine',
            'cost': 500,
            'date': datetime.now().isoformat()
        }
        
        manager.record_negative_event(user_data, event_data)
        
        assert 'financial_history' in user_data
        assert len(user_data['financial_history']['events']) == 1
        assert user_data['financial_history']['events'][0]['event_type'] == 'fine'
    
    def test_record_tier_change(self):
        """Test recording tier change"""
        manager = FinancialHistoryManager()
        user_data = {'money': 5000}
        
        manager.record_tier_change(user_data, 'poor', 'middle')
        
        assert 'financial_history' in user_data
        assert len(user_data['financial_history']['tier_changes']) == 1
        assert user_data['financial_history']['tier_changes'][0]['old_tier'] == 'poor'
        assert user_data['financial_history']['tier_changes'][0]['new_tier'] == 'middle'
    
    def test_get_history_returns_all_types(self):
        """Test that get_history returns all record types"""
        from datetime import datetime
        
        manager = FinancialHistoryManager()
        user_data = {'money': 5000}
        
        # Add various records
        manager.record_daily_expenses(user_data, {
            'rent': 100, 'food': 50, 'transport': 30,
            'final_total': 180, 'date': datetime.now().isoformat()
        })
        manager.record_daily_income(user_data, {'source': 'delivery', 'amount': 50})
        manager.record_negative_event(user_data, {
            'event_type': 'fine', 'cost': 500, 'date': datetime.now().isoformat()
        })
        manager.record_tier_change(user_data, 'poor', 'middle')
        
        history = manager.get_history(user_data, days=30)
        
        assert 'expenses' in history
        assert 'income' in history
        assert 'events' in history
        assert 'tier_changes' in history


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

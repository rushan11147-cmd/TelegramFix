# -*- coding: utf-8 -*-
"""
Property-Based Tests for SkillTreeManager

Tests universal properties for the main orchestrator:
- Property 13: Skill Reset Refund
- Property 15: Reset Cooldown Enforcement

Uses hypothesis for property-based testing with 100+ iterations per test.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from copy import deepcopy

from skills_system import SkillTreeManager
from skills_config import (
    SkillData,
    SKILL_TREE_CONFIG,
    RESET_REFUND_PERCENTAGE,
    RESET_COOLDOWN_DAYS,
    initialize_default_skills
)


# ============================================================================
# MOCK DATABASE FUNCTIONS
# ============================================================================

test_users = {}


def mock_get_user(user_id):
    """Mock function to get user data"""
    return test_users.get(user_id)


def mock_save_user(user_data):
    """Mock function to save user data"""
    if 'user_id' in user_data:
        test_users[user_data['user_id']] = user_data


def reset_test_db():
    """Reset test database"""
    test_users.clear()


# ============================================================================
# PROPERTY 13: Skill Reset Refund
# ============================================================================

@settings(max_examples=100)
@given(
    total_stars_spent=st.integers(min_value=1, max_value=500),  # Changed from 0 to 1
    initial_balance=st.integers(min_value=0, max_value=100),
    current_day=st.integers(min_value=7, max_value=365)
)
def test_property_13_skill_reset_refund(total_stars_spent, initial_balance, current_day):
    """
    Feature: skills-tree-system, Property 13: Skill Reset Refund
    
    For any skill reset operation, the player should receive exactly 80% of 
    total stars spent (rounded down), and all skill levels should be reset to 1.
    
    **Validates: Requirements 7.1, 7.2**
    
    Formula: refund = floor(total_stars_spent * 0.80)
    
    Verification:
    1. Refund amount is exactly 80% of total spent (rounded down)
    2. All skill levels are reset to 1
    3. Star balance increases by refund amount
    4. Total stars spent is reset to 0
    
    Note: Requires at least 1 star spent (can't reset if no upgrades)
    """
    reset_test_db()
    
    # Create user with some skills upgraded
    user_id = f'user_reset_{total_stars_spent}_{initial_balance}_{current_day}'
    
    # Create skill levels that reflect the total spent
    # For simplicity, upgrade luck_1 multiple times
    skills = initialize_default_skills()
    
    # Distribute spent stars across skills to create realistic levels
    # We'll upgrade luck_1 as much as possible with the spent amount
    remaining_spent = total_stars_spent
    current_level = 1
    
    # Calculate what level we can reach with total_stars_spent
    # Cost formula: base_cost + level, for luck_1 base_cost = 2
    while remaining_spent > 0 and current_level < 10:
        cost = 2 + current_level  # luck_1 base_cost is 2
        if remaining_spent >= cost:
            remaining_spent -= cost
            current_level += 1
        else:
            break
    
    skills['luck_1'] = current_level
    
    # If there's still spent amount, upgrade charisma_1
    if remaining_spent > 0:
        charisma_level = 1
        while remaining_spent > 0 and charisma_level < 10:
            cost = 2 + charisma_level
            if remaining_spent >= cost:
                remaining_spent -= cost
                charisma_level += 1
            else:
                break
        skills['charisma_1'] = charisma_level
    
    test_users[user_id] = {
        'user_id': user_id,
        'skill_data': {
            'star_balance': initial_balance,
            'skills': skills,
            'total_stars_spent': total_stars_spent,
            'last_monthly_award_day': 0,
            'last_reset_day': -7,  # Allow reset
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    # Create manager
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    # Calculate expected refund (80% rounded down)
    expected_refund = int(total_stars_spent * RESET_REFUND_PERCENTAGE)
    expected_new_balance = initial_balance + expected_refund
    
    # Perform reset
    result = manager.reset_skills(user_id, current_day)
    
    # Verify success
    assert result['success'] == True, \
        f"Reset should succeed, got error: {result.get('error', 'none')}"
    
    # Verify refund amount is exactly 80% (rounded down)
    assert result['stars_refunded'] == expected_refund, \
        f"Refund should be {expected_refund} (80% of {total_stars_spent}), " \
        f"got {result['stars_refunded']}"
    
    # Verify new balance is correct
    assert result['new_star_balance'] == expected_new_balance, \
        f"New balance should be {expected_new_balance} " \
        f"({initial_balance} + {expected_refund}), " \
        f"got {result['new_star_balance']}"
    
    # Verify all skills are reset to level 1
    user_data = test_users[user_id]
    for skill_id, level in user_data['skill_data']['skills'].items():
        assert level == 1, \
            f"Skill {skill_id} should be reset to level 1, got {level}"
    
    # Verify total stars spent is reset to 0
    assert user_data['skill_data']['total_stars_spent'] == 0, \
        f"Total stars spent should be reset to 0, " \
        f"got {user_data['skill_data']['total_stars_spent']}"
    
    # Verify last reset day is updated
    assert user_data['skill_data']['last_reset_day'] == current_day, \
        f"Last reset day should be updated to {current_day}, " \
        f"got {user_data['skill_data']['last_reset_day']}"


@settings(max_examples=100)
@given(
    stars_spent_list=st.lists(
        st.integers(min_value=1, max_value=100),
        min_size=1,
        max_size=5
    ),
    current_day=st.integers(min_value=7, max_value=100)
)
def test_property_13_refund_percentage_is_exactly_80_percent(stars_spent_list, current_day):
    """
    Property 13: Verify that refund is always exactly 80% (rounded down).
    
    For any amount of stars spent, the refund should be floor(spent * 0.80).
    """
    reset_test_db()
    
    for i, total_spent in enumerate(stars_spent_list):
        user_id = f'user_refund_test_{i}_{current_day}'
        
        # Create user with spent stars
        skills = initialize_default_skills()
        skills['luck_1'] = 2  # Some upgrade
        
        test_users[user_id] = {
            'user_id': user_id,
            'skill_data': {
                'star_balance': 0,
                'skills': skills,
                'total_stars_spent': total_spent,
                'last_monthly_award_day': 0,
                'last_reset_day': -7,
                'milestones_claimed': [],
                'star_history': []
            }
        }
        
        manager = SkillTreeManager(mock_get_user, mock_save_user)
        
        # Calculate expected refund
        expected_refund = int(total_spent * 0.80)
        
        # Perform reset
        result = manager.reset_skills(user_id, current_day + i * 10)
        
        # Verify refund is exactly 80%
        assert result['stars_refunded'] == expected_refund, \
            f"For {total_spent} spent, refund should be {expected_refund}, " \
            f"got {result['stars_refunded']}"
        
        # Verify it's rounded down (not up or rounded)
        assert result['stars_refunded'] == int(total_spent * 0.80), \
            f"Refund should be floor(spent * 0.80)"
        
        # Verify it's not more than 80%
        assert result['stars_refunded'] <= total_spent * 0.80, \
            f"Refund should not exceed 80% of spent"


@settings(max_examples=50)
@given(
    initial_balance=st.integers(min_value=0, max_value=100),
    total_spent=st.integers(min_value=10, max_value=200),
    current_day=st.integers(min_value=7, max_value=100)
)
def test_property_13_all_skills_reset_to_level_1(initial_balance, total_spent, current_day):
    """
    Property 13: All skills must be reset to level 1 after reset.
    
    For any skill configuration, after reset all skills should be at level 1.
    """
    reset_test_db()
    
    user_id = f'user_all_reset_{current_day}'
    
    # Create user with various skill levels
    skills = initialize_default_skills()
    
    # Set different levels for different skills
    skills['luck_1'] = 5
    skills['charisma_1'] = 3
    skills['intelligence_1'] = 7
    skills['endurance_1'] = 2
    skills['business_1'] = 4
    
    test_users[user_id] = {
        'user_id': user_id,
        'skill_data': {
            'star_balance': initial_balance,
            'skills': skills,
            'total_stars_spent': total_spent,
            'last_monthly_award_day': 0,
            'last_reset_day': -7,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    # Perform reset
    result = manager.reset_skills(user_id, current_day)
    
    assert result['success'] == True
    
    # Verify ALL skills are at level 1
    user_data = test_users[user_id]
    for skill_id in SKILL_TREE_CONFIG.keys():
        level = user_data['skill_data']['skills'][skill_id]
        assert level == 1, \
            f"After reset, {skill_id} should be at level 1, got {level}"


@settings(max_examples=50)
@given(
    total_spent=st.integers(min_value=1, max_value=500),
    current_day=st.integers(min_value=7, max_value=100)
)
def test_property_13_total_spent_reset_to_zero(total_spent, current_day):
    """
    Property 13: Total stars spent should be reset to 0 after reset.
    """
    reset_test_db()
    
    user_id = f'user_spent_reset_{current_day}'
    
    skills = initialize_default_skills()
    skills['luck_1'] = 3
    
    test_users[user_id] = {
        'user_id': user_id,
        'skill_data': {
            'star_balance': 10,
            'skills': skills,
            'total_stars_spent': total_spent,
            'last_monthly_award_day': 0,
            'last_reset_day': -7,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    # Perform reset
    result = manager.reset_skills(user_id, current_day)
    
    assert result['success'] == True
    
    # Verify total spent is 0
    user_data = test_users[user_id]
    assert user_data['skill_data']['total_stars_spent'] == 0, \
        f"Total stars spent should be 0 after reset, " \
        f"got {user_data['skill_data']['total_stars_spent']}"


# ============================================================================
# PROPERTY 15: Reset Cooldown Enforcement
# ============================================================================

@settings(max_examples=100)
@given(
    last_reset_day=st.integers(min_value=0, max_value=365),
    current_day=st.integers(min_value=0, max_value=400),
    total_spent=st.integers(min_value=10, max_value=100)
)
def test_property_15_reset_cooldown_enforcement(last_reset_day, current_day, total_spent):
    """
    Feature: skills-tree-system, Property 15: Reset Cooldown Enforcement
    
    For any player, skill reset should be allowed only if at least 7 game days 
    have passed since the last reset.
    
    **Validates: Requirements 7.5**
    
    Verification:
    1. If days_since_reset >= 7: reset succeeds
    2. If days_since_reset < 7: reset fails with appropriate error
    3. Error message indicates days remaining until next reset
    """
    reset_test_db()
    
    user_id = f'user_cooldown_{last_reset_day}_{current_day}'
    
    # Create user with last reset day
    skills = initialize_default_skills()
    skills['luck_1'] = 3  # Some upgrades
    
    test_users[user_id] = {
        'user_id': user_id,
        'skill_data': {
            'star_balance': 5,
            'skills': skills,
            'total_stars_spent': total_spent,
            'last_monthly_award_day': 0,
            'last_reset_day': last_reset_day,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    # Calculate days since last reset
    days_since_reset = current_day - last_reset_day
    
    # Perform reset attempt
    result = manager.reset_skills(user_id, current_day)
    
    # Verify cooldown enforcement
    if days_since_reset >= RESET_COOLDOWN_DAYS:
        # Should succeed
        assert result['success'] == True, \
            f"Reset should succeed when {days_since_reset} days passed " \
            f"(cooldown is {RESET_COOLDOWN_DAYS} days), " \
            f"got error: {result.get('error', 'none')}"
        
        # Verify refund was given
        expected_refund = int(total_spent * RESET_REFUND_PERCENTAGE)
        assert result['stars_refunded'] == expected_refund, \
            f"Should refund {expected_refund} stars"
        
        # Verify next reset day is set correctly
        expected_next_reset = current_day + RESET_COOLDOWN_DAYS
        assert result['next_reset_day'] == expected_next_reset, \
            f"Next reset day should be {expected_next_reset}, " \
            f"got {result['next_reset_day']}"
        
    else:
        # Should fail
        assert result['success'] == False, \
            f"Reset should fail when only {days_since_reset} days passed " \
            f"(cooldown is {RESET_COOLDOWN_DAYS} days)"
        
        # Verify no refund
        assert result['stars_refunded'] == 0, \
            f"Should not refund stars when cooldown active"
        
        # Verify error message mentions cooldown
        assert 'error' in result, "Should have error message"
        assert 'дней' in result['error'] or 'день' in result['error'], \
            f"Error should mention days: {result['error']}"
        
        # Verify next reset day is correct
        expected_next_reset = last_reset_day + RESET_COOLDOWN_DAYS
        assert result['next_reset_day'] == expected_next_reset, \
            f"Next reset day should be {expected_next_reset}, " \
            f"got {result['next_reset_day']}"
        
        # Verify skills were NOT reset
        user_data = test_users[user_id]
        assert user_data['skill_data']['skills']['luck_1'] == 3, \
            f"Skills should not be reset when cooldown active"
        
        # Verify total spent was NOT reset
        assert user_data['skill_data']['total_stars_spent'] == total_spent, \
            f"Total spent should not change when cooldown active"


@settings(max_examples=100)
@given(
    days_since_reset=st.integers(min_value=0, max_value=20)
)
def test_property_15_cooldown_boundary_at_7_days(days_since_reset):
    """
    Property 15: Verify exact boundary at 7 days.
    
    Reset should fail for days 0-6, succeed for days 7+.
    """
    reset_test_db()
    
    user_id = f'user_boundary_{days_since_reset}'
    
    last_reset_day = 100
    current_day = last_reset_day + days_since_reset
    
    skills = initialize_default_skills()
    skills['luck_1'] = 2
    
    test_users[user_id] = {
        'user_id': user_id,
        'skill_data': {
            'star_balance': 5,
            'skills': skills,
            'total_stars_spent': 10,
            'last_monthly_award_day': 0,
            'last_reset_day': last_reset_day,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    result = manager.reset_skills(user_id, current_day)
    
    # Verify boundary
    if days_since_reset >= 7:
        assert result['success'] == True, \
            f"Reset should succeed at day {days_since_reset} (>= 7)"
    else:
        assert result['success'] == False, \
            f"Reset should fail at day {days_since_reset} (< 7)"
        
        # Verify days remaining is correct
        days_remaining = 7 - days_since_reset
        assert str(days_remaining) in result['error'] or \
               str(days_remaining) in result['message'], \
            f"Error should mention {days_remaining} days remaining"


@settings(max_examples=50)
@given(
    reset_sequence=st.lists(
        st.integers(min_value=7, max_value=15),
        min_size=2,
        max_size=5
    )
)
def test_property_15_multiple_resets_respect_cooldown(reset_sequence):
    """
    Property 15: Multiple resets should each respect the 7-day cooldown.
    
    For any sequence of reset attempts, each must wait 7 days from the previous.
    """
    reset_test_db()
    
    user_id = 'user_multiple_resets'
    
    skills = initialize_default_skills()
    
    test_users[user_id] = {
        'user_id': user_id,
        'skill_data': {
            'star_balance': 100,
            'skills': skills,
            'total_stars_spent': 50,
            'last_monthly_award_day': 0,
            'last_reset_day': -7,  # Allow first reset
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    current_day = 0
    successful_resets = 0
    
    for days_to_advance in reset_sequence:
        current_day += days_to_advance
        
        # Upgrade a skill to have something to reset
        test_users[user_id]['skill_data']['skills']['luck_1'] = 2
        test_users[user_id]['skill_data']['total_stars_spent'] = 10
        
        result = manager.reset_skills(user_id, current_day)
        
        if result['success']:
            successful_resets += 1
            # Verify cooldown is set
            assert test_users[user_id]['skill_data']['last_reset_day'] == current_day
    
    # Should have at least one successful reset
    assert successful_resets >= 1, \
        f"Should have at least one successful reset in sequence"


@settings(max_examples=50)
@given(
    current_day=st.integers(min_value=0, max_value=100)
)
def test_property_15_first_reset_always_allowed(current_day):
    """
    Property 15: First reset should always be allowed (last_reset_day = -7).
    
    New players with last_reset_day = -7 should be able to reset immediately.
    """
    reset_test_db()
    
    user_id = f'user_first_reset_{current_day}'
    
    skills = initialize_default_skills()
    skills['luck_1'] = 3
    
    test_users[user_id] = {
        'user_id': user_id,
        'skill_data': {
            'star_balance': 5,
            'skills': skills,
            'total_stars_spent': 20,
            'last_monthly_award_day': 0,
            'last_reset_day': -7,  # Initial value
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    result = manager.reset_skills(user_id, current_day)
    
    # First reset should always succeed
    assert result['success'] == True, \
        f"First reset should always be allowed, got error: {result.get('error', 'none')}"
    
    # Verify refund was given
    assert result['stars_refunded'] > 0, \
        f"Should refund stars on first reset"


if __name__ == '__main__':
    print("Running property-based tests for SkillTreeManager...\n")
    
    # Run with pytest
    pytest.main([__file__, '-v'])

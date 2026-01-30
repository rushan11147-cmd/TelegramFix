# -*- coding: utf-8 -*-
"""
Property-Based Tests for Star Economy Manager

These tests use hypothesis to verify universal properties of star awards
across all valid inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime

from star_economy import StarEconomyManager
from skills_config import (
    SkillData,
    MONTHLY_STARS,
    WEALTH_TIER_STARS,
    ACHIEVEMENT_STARS,
    MILLION_EARNED_STARS,
    SURVIVAL_100_DAYS_STARS,
    initialize_default_skills
)


# ============================================================================
# HYPOTHESIS STRATEGIES
# ============================================================================

def valid_skill_data():
    """Strategy for generating valid SkillData objects"""
    return st.builds(
        SkillData,
        star_balance=st.integers(min_value=0, max_value=1000),
        skills=st.just(initialize_default_skills()),
        total_stars_spent=st.integers(min_value=0, max_value=500),
        last_monthly_award_day=st.integers(min_value=0, max_value=365),
        last_reset_day=st.integers(min_value=-7, max_value=365),
        milestones_claimed=st.lists(st.text(), max_size=10),
        star_history=st.lists(st.fixed_dictionaries({
            'timestamp': st.just(datetime.now().isoformat()),
            'source': st.text(),
            'amount': st.integers(min_value=1, max_value=10)
        }), max_size=10)
    )


# ============================================================================
# PROPERTY 1: Monthly Star Award Consistency
# Feature: skills-tree-system, Property 1
# ============================================================================

@given(
    last_award_day=st.integers(min_value=0, max_value=365),
    current_day=st.integers(min_value=0, max_value=400)
)
@settings(max_examples=100)
def test_property_1_monthly_star_award_consistency(last_award_day, current_day):
    """
    Property 1: Monthly Star Award Consistency
    
    For any player and any sequence of game days, when exactly 30 days have 
    passed since the last monthly award, the system should award exactly 3 stars 
    and update the last award day.
    
    **Validates: Requirements 1.1**
    """
    manager = StarEconomyManager()
    
    # Create skill data with specific last award day
    skill_data = SkillData(
        star_balance=10,
        skills=initialize_default_skills(),
        last_monthly_award_day=last_award_day
    )
    
    initial_balance = skill_data.star_balance
    days_since_last = current_day - last_award_day
    
    # Award monthly stars
    stars_awarded = manager.award_monthly_stars(skill_data, current_day)
    
    # Verify consistency
    if days_since_last >= 30:
        # Should award exactly 3 stars
        assert stars_awarded == MONTHLY_STARS, \
            f"Should award {MONTHLY_STARS} stars when 30+ days passed, got {stars_awarded}"
        
        # Balance should increase by 3
        assert skill_data.star_balance == initial_balance + MONTHLY_STARS, \
            f"Balance should increase by {MONTHLY_STARS}, got {skill_data.star_balance - initial_balance}"
        
        # Last award day should be updated
        assert skill_data.last_monthly_award_day == current_day, \
            f"Last award day should be updated to {current_day}, got {skill_data.last_monthly_award_day}"
    else:
        # Should not award any stars
        assert stars_awarded == 0, \
            f"Should not award stars when less than 30 days passed, got {stars_awarded}"
        
        # Balance should not change
        assert skill_data.star_balance == initial_balance, \
            f"Balance should not change, got {skill_data.star_balance}"
        
        # Last award day should not change
        assert skill_data.last_monthly_award_day == last_award_day, \
            f"Last award day should not change, got {skill_data.last_monthly_award_day}"


@given(
    initial_day=st.integers(min_value=0, max_value=100),
    days_to_advance=st.integers(min_value=0, max_value=200)
)
@settings(max_examples=100)
def test_monthly_awards_accumulate_correctly(initial_day, days_to_advance):
    """
    For any starting day and number of days advanced, the total stars awarded
    should equal (days_advanced // 30) * MONTHLY_STARS.
    
    **Validates: Requirements 1.1**
    """
    manager = StarEconomyManager()
    
    skill_data = SkillData(
        star_balance=0,
        skills=initialize_default_skills(),
        last_monthly_award_day=initial_day
    )
    
    current_day = initial_day
    total_awarded = 0
    
    # Advance day by day
    for day in range(initial_day, initial_day + days_to_advance + 1):
        stars = manager.award_monthly_stars(skill_data, day)
        total_awarded += stars
        current_day = day
    
    # Calculate expected awards
    expected_awards = days_to_advance // 30
    expected_total = expected_awards * MONTHLY_STARS
    
    # Verify total matches expected
    assert total_awarded == expected_total, \
        f"Expected {expected_total} stars over {days_to_advance} days, got {total_awarded}"


# ============================================================================
# PROPERTY 4: Milestone Star Awards
# Feature: skills-tree-system, Property 4
# ============================================================================

@given(
    cumulative_earnings=st.integers(min_value=0, max_value=5000000),
    days_survived=st.integers(min_value=0, max_value=500)
)
@settings(max_examples=100)
def test_property_4_milestone_star_awards(cumulative_earnings, days_survived):
    """
    Property 4: Milestone Star Awards
    
    For any player reaching cumulative milestones (1M earned, 100 days survived), 
    the system should award the appropriate stars exactly once and mark the 
    milestone as claimed.
    
    **Validates: Requirements 1.4, 1.5**
    """
    manager = StarEconomyManager()
    
    skill_data = SkillData(
        star_balance=0,
        skills=initialize_default_skills(),
        milestones_claimed=[]
    )
    
    initial_balance = skill_data.star_balance
    
    # Check milestones
    stars_awarded = manager.check_milestone_stars(
        skill_data,
        cumulative_earnings=cumulative_earnings,
        days_survived=days_survived
    )
    
    # Calculate expected awards
    expected_stars = 0
    expected_milestones = []
    
    if cumulative_earnings >= 1000000:
        expected_stars += MILLION_EARNED_STARS
        expected_milestones.append('milestone_million_earned')
    
    if days_survived >= 100:
        expected_stars += SURVIVAL_100_DAYS_STARS
        expected_milestones.append('milestone_survival_100')
    
    # Verify correct stars awarded
    assert stars_awarded == expected_stars, \
        f"Expected {expected_stars} stars, got {stars_awarded}"
    
    # Verify balance updated correctly
    assert skill_data.star_balance == initial_balance + expected_stars, \
        f"Balance should be {initial_balance + expected_stars}, got {skill_data.star_balance}"
    
    # Verify milestones marked as claimed
    for milestone in expected_milestones:
        assert milestone in skill_data.milestones_claimed, \
            f"Milestone {milestone} should be marked as claimed"
    
    # Call again with same values - should award 0 stars (no duplicates)
    stars_awarded_again = manager.check_milestone_stars(
        skill_data,
        cumulative_earnings=cumulative_earnings,
        days_survived=days_survived
    )
    
    assert stars_awarded_again == 0, \
        f"Should not award stars again for same milestones, got {stars_awarded_again}"
    
    # Balance should not change
    assert skill_data.star_balance == initial_balance + expected_stars, \
        f"Balance should not change on duplicate check"


@given(
    earnings_sequence=st.lists(
        st.integers(min_value=0, max_value=500000),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100)
def test_milestone_awarded_only_once_across_multiple_checks(earnings_sequence):
    """
    For any sequence of earnings checks, the 1M milestone should be awarded
    exactly once, even if earnings continue to increase.
    
    **Validates: Requirements 1.4**
    """
    manager = StarEconomyManager()
    
    skill_data = SkillData(
        star_balance=0,
        skills=initialize_default_skills(),
        milestones_claimed=[]
    )
    
    total_awarded = 0
    cumulative = 0
    
    # Check milestones multiple times with increasing earnings
    for earnings in earnings_sequence:
        cumulative += earnings
        stars = manager.check_milestone_stars(
            skill_data,
            cumulative_earnings=cumulative,
            days_survived=0
        )
        total_awarded += stars
    
    # If we ever crossed 1M, should have awarded exactly MILLION_EARNED_STARS once
    if cumulative >= 1000000:
        assert total_awarded == MILLION_EARNED_STARS, \
            f"Should award {MILLION_EARNED_STARS} exactly once, got {total_awarded}"
        assert 'milestone_million_earned' in skill_data.milestones_claimed
    else:
        assert total_awarded == 0, \
            f"Should not award any stars if threshold not reached"


# ============================================================================
# ADDITIONAL PROPERTY TESTS
# ============================================================================

@given(
    skill_data=valid_skill_data(),
    wealth_tier=st.sampled_from(['poor', 'middle_class', 'wealthy', 'rich'])
)
@settings(max_examples=100)
def test_wealth_tier_awards_exactly_once(skill_data, wealth_tier):
    """
    For any wealth tier, stars should be awarded exactly once per tier.
    
    **Validates: Requirements 1.2 (Property 2)**
    """
    manager = StarEconomyManager()
    
    initial_balance = skill_data.star_balance
    
    # Award for first time
    stars1 = manager.award_wealth_tier_stars(skill_data, wealth_tier)
    
    # Should award WEALTH_TIER_STARS
    assert stars1 == WEALTH_TIER_STARS, \
        f"First award should be {WEALTH_TIER_STARS}, got {stars1}"
    
    # Award for same tier again
    stars2 = manager.award_wealth_tier_stars(skill_data, wealth_tier)
    
    # Should not award again
    assert stars2 == 0, \
        f"Second award for same tier should be 0, got {stars2}"
    
    # Total balance should increase by WEALTH_TIER_STARS only once
    assert skill_data.star_balance == initial_balance + WEALTH_TIER_STARS, \
        f"Balance should increase by {WEALTH_TIER_STARS} once"


@given(
    skill_data=valid_skill_data(),
    achievement=st.sampled_from(['businessman', 'tycoon', 'millionaire', 'survivor'])
)
@settings(max_examples=100)
def test_achievement_awards_exactly_once(skill_data, achievement):
    """
    For any achievement, stars should be awarded exactly once per achievement.
    
    **Validates: Requirements 1.3 (Property 3)**
    """
    manager = StarEconomyManager()
    
    initial_balance = skill_data.star_balance
    
    # Award for first time
    stars1 = manager.award_achievement_stars(skill_data, achievement)
    
    # Should award ACHIEVEMENT_STARS
    assert stars1 == ACHIEVEMENT_STARS, \
        f"First award should be {ACHIEVEMENT_STARS}, got {stars1}"
    
    # Award for same achievement again
    stars2 = manager.award_achievement_stars(skill_data, achievement)
    
    # Should not award again
    assert stars2 == 0, \
        f"Second award for same achievement should be 0, got {stars2}"
    
    # Total balance should increase by ACHIEVEMENT_STARS only once
    assert skill_data.star_balance == initial_balance + ACHIEVEMENT_STARS, \
        f"Balance should increase by {ACHIEVEMENT_STARS} once"


@given(
    source=st.text(min_size=1, max_size=50),
    amount=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
def test_track_star_source_records_correctly(source, amount):
    """
    For any star source and amount, tracking should record all details correctly.
    
    **Validates: Requirements 10.1, 10.4 (Property 20)**
    """
    manager = StarEconomyManager()
    
    skill_data = SkillData(
        star_balance=0,
        skills=initialize_default_skills(),
        star_history=[]
    )
    
    # Track source
    manager.track_star_source(skill_data, source, amount)
    
    # Verify event recorded
    assert len(skill_data.star_history) == 1, \
        f"Should have 1 history event, got {len(skill_data.star_history)}"
    
    event = skill_data.star_history[0]
    
    # Verify all required fields present
    assert 'timestamp' in event, "Event should have timestamp"
    assert 'source' in event, "Event should have source"
    assert 'amount' in event, "Event should have amount"
    
    # Verify values correct
    assert event['source'] == source, \
        f"Source should be '{source}', got '{event['source']}'"
    assert event['amount'] == amount, \
        f"Amount should be {amount}, got {event['amount']}"


@given(
    num_events=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=50)
def test_star_history_limited_to_10_events(num_events):
    """
    For any number of star tracking events, history should be limited to last 10.
    
    **Validates: Requirements 10.3 (Property 21)**
    """
    manager = StarEconomyManager()
    
    skill_data = SkillData(
        star_balance=0,
        skills=initialize_default_skills(),
        star_history=[]
    )
    
    # Track multiple events
    for i in range(num_events):
        manager.track_star_source(skill_data, f'source_{i}', i + 1)
    
    # Should have at most 10 events
    assert len(skill_data.star_history) <= 10, \
        f"History should be limited to 10 events, got {len(skill_data.star_history)}"
    
    # If we had more than 10, verify we kept the last 10
    if num_events > 10:
        assert len(skill_data.star_history) == 10
        # Last event should be the most recent
        assert skill_data.star_history[-1]['source'] == f'source_{num_events - 1}'


@given(
    skill_data=valid_skill_data(),
    source=st.text(min_size=1, max_size=50),
    amount=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
def test_award_and_track_combines_operations(skill_data, source, amount):
    """
    For any award and track operation, both balance update and history
    tracking should occur correctly.
    
    **Validates: Requirements 1.1, 10.1**
    """
    manager = StarEconomyManager()
    
    initial_balance = skill_data.star_balance
    initial_history_len = len(skill_data.star_history)
    
    # Award and track
    stars_awarded = manager.award_and_track(skill_data, source, amount)
    
    # Verify stars awarded
    assert stars_awarded == amount, \
        f"Should award {amount} stars, got {stars_awarded}"
    
    # Verify balance updated
    assert skill_data.star_balance == initial_balance + amount, \
        f"Balance should increase by {amount}"
    
    # Verify history updated
    assert len(skill_data.star_history) == min(initial_history_len + 1, 10), \
        f"History should have one more event (up to 10)"
    
    # Verify last event has correct data
    last_event = skill_data.star_history[-1]
    assert last_event['source'] == source
    assert last_event['amount'] == amount

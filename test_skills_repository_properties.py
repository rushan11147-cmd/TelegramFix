# -*- coding: utf-8 -*-
"""
Property-Based Tests for Skills Repository

These tests use hypothesis to verify universal properties across all valid inputs.
Focus: Data persistence, round-trip integrity, and data validation.
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta

from skills_repository import SkillRepository
from skills_config import SkillData, SKILL_TREE_CONFIG, initialize_default_skills


# ============================================================================
# HYPOTHESIS STRATEGIES
# ============================================================================

def valid_skill_levels():
    """Strategy for generating valid skill level dictionaries"""
    # Generate a subset of skills with valid levels (1-10)
    return st.dictionaries(
        keys=st.sampled_from(list(SKILL_TREE_CONFIG.keys())),
        values=st.integers(min_value=1, max_value=10),
        min_size=1,
        max_size=len(SKILL_TREE_CONFIG)
    )


def valid_star_history():
    """Strategy for generating valid star history events"""
    # Use recent timestamps (within last 29 days) to avoid cleanup
    now = datetime.now()
    recent_start = now - timedelta(days=29)
    
    return st.lists(
        st.fixed_dictionaries({
            'timestamp': st.datetimes(
                min_value=recent_start,
                max_value=now
            ).map(lambda dt: dt.isoformat()),
            'source': st.sampled_from(['monthly', 'wealth_tier', 'achievement', 'milestone']),
            'amount': st.integers(min_value=1, max_value=10)
        }),
        min_size=0,
        max_size=15  # More than 10 to test truncation
    )


def valid_skill_data():
    """Strategy for generating valid SkillData objects"""
    return st.builds(
        SkillData,
        star_balance=st.integers(min_value=0, max_value=1000),
        skills=valid_skill_levels(),
        total_stars_spent=st.integers(min_value=0, max_value=500),
        last_monthly_award_day=st.integers(min_value=0, max_value=365),
        last_reset_day=st.integers(min_value=-7, max_value=365),
        milestones_claimed=st.lists(
            st.sampled_from(['million_earned', 'survival_100']),
            min_size=0,
            max_size=2,
            unique=True
        ),
        star_history=valid_star_history()
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_mock_database():
    """Create a fresh mock database for testing"""
    db = {}
    
    def get_user(user_id):
        return db.get(user_id)
    
    def save_user(user_data):
        db[user_data['user_id']] = user_data
    
    return db, get_user, save_user


# ============================================================================
# PROPERTY 10: Skill Data Persistence Round Trip
# Feature: skills-tree-system, Property 10
# ============================================================================

@given(skill_data=valid_skill_data())
@settings(max_examples=100)
def test_property_10_skill_data_persistence_round_trip(skill_data):
    """
    Property 10: Skill Data Persistence Round Trip
    
    For any skill data state, saving then loading should produce an 
    equivalent state with all skill levels, star balance, and history preserved.
    
    **Validates: Requirements 3.5, 9.1, 9.2**
    """
    db, get_user, save_user = create_mock_database()
    repository = SkillRepository(get_user, save_user)
    
    # Create user
    user_id = 'test_user'
    db[user_id] = {'user_id': user_id}
    
    # Ensure all skills are present (fill in missing ones with level 1)
    all_skills = initialize_default_skills()
    all_skills.update(skill_data.skills)
    skill_data.skills = all_skills
    
    # Save skill data
    repository.save_skill_data(user_id, skill_data)
    
    # Load skill data
    loaded_data = repository.load_skill_data(user_id)
    
    # Verify star balance preserved
    assert loaded_data.star_balance == skill_data.star_balance, \
        f"Star balance not preserved: expected {skill_data.star_balance}, got {loaded_data.star_balance}"
    
    # Verify total stars spent preserved
    assert loaded_data.total_stars_spent == skill_data.total_stars_spent, \
        f"Total stars spent not preserved: expected {skill_data.total_stars_spent}, got {loaded_data.total_stars_spent}"
    
    # Verify all skill levels preserved
    for skill_id in SKILL_TREE_CONFIG.keys():
        original_level = skill_data.skills.get(skill_id, 1)
        loaded_level = loaded_data.skills.get(skill_id, 1)
        assert loaded_level == original_level, \
            f"Skill {skill_id} level not preserved: expected {original_level}, got {loaded_level}"
    
    # Verify monthly award day preserved
    assert loaded_data.last_monthly_award_day == skill_data.last_monthly_award_day, \
        f"Last monthly award day not preserved: expected {skill_data.last_monthly_award_day}, got {loaded_data.last_monthly_award_day}"
    
    # Verify reset day preserved
    assert loaded_data.last_reset_day == skill_data.last_reset_day, \
        f"Last reset day not preserved: expected {skill_data.last_reset_day}, got {loaded_data.last_reset_day}"
    
    # Verify milestones preserved
    assert set(loaded_data.milestones_claimed) == set(skill_data.milestones_claimed), \
        f"Milestones not preserved: expected {skill_data.milestones_claimed}, got {loaded_data.milestones_claimed}"
    
    # Verify star history preserved (note: may be truncated to last 10)
    # If original had more than 10, only last 10 should be preserved
    expected_history_count = min(len(skill_data.star_history), 10)
    assert len(loaded_data.star_history) == expected_history_count, \
        f"Star history count not correct: expected {expected_history_count}, got {len(loaded_data.star_history)}"
    
    # Verify the preserved history events match (last N events)
    if expected_history_count > 0:
        original_last_events = skill_data.star_history[-expected_history_count:]
        for i, (original, loaded) in enumerate(zip(original_last_events, loaded_data.star_history)):
            assert loaded['source'] == original['source'], \
                f"History event {i} source not preserved: expected {original['source']}, got {loaded['source']}"
            assert loaded['amount'] == original['amount'], \
                f"History event {i} amount not preserved: expected {original['amount']}, got {loaded['amount']}"
            # Timestamp should be preserved
            assert loaded['timestamp'] == original['timestamp'], \
                f"History event {i} timestamp not preserved"


# ============================================================================
# ADDITIONAL PROPERTY TESTS FOR PERSISTENCE
# ============================================================================

@given(
    star_balance=st.integers(min_value=0, max_value=1000),
    skills=valid_skill_levels()
)
@settings(max_examples=100)
def test_persistence_preserves_minimal_state(star_balance, skills):
    """
    For any minimal skill state (just balance and skills), 
    saving and loading should preserve the state and add defaults for missing fields.
    
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    db, get_user, save_user = create_mock_database()
    repository = SkillRepository(get_user, save_user)
    
    user_id = 'test_user'
    db[user_id] = {'user_id': user_id}
    
    # Create minimal skill data
    all_skills = initialize_default_skills()
    all_skills.update(skills)
    
    skill_data = SkillData(
        star_balance=star_balance,
        skills=all_skills
    )
    
    # Save and load
    repository.save_skill_data(user_id, skill_data)
    loaded_data = repository.load_skill_data(user_id)
    
    # Verify core data preserved
    assert loaded_data.star_balance == star_balance
    for skill_id, level in skills.items():
        assert loaded_data.skills[skill_id] == level
    
    # Verify defaults added
    assert loaded_data.total_stars_spent == 0
    assert loaded_data.last_monthly_award_day == 0
    assert loaded_data.last_reset_day == -7
    assert isinstance(loaded_data.milestones_claimed, list)
    assert isinstance(loaded_data.star_history, list)


@given(
    num_events=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=50)
def test_star_history_truncation_to_10_events(num_events):
    """
    For any number of star history events, after saving and loading,
    only the last 10 events should be preserved.
    
    **Validates: Requirements 10.3**
    """
    db, get_user, save_user = create_mock_database()
    repository = SkillRepository(get_user, save_user)
    
    user_id = 'test_user'
    db[user_id] = {'user_id': user_id}
    
    # Create skill data with many history events
    history = []
    for i in range(num_events):
        history.append({
            'timestamp': datetime.now().isoformat(),
            'source': f'event_{i}',
            'amount': i + 1
        })
    
    skill_data = SkillData(
        star_balance=10,
        skills=initialize_default_skills(),
        star_history=history
    )
    
    # Save and load
    repository.save_skill_data(user_id, skill_data)
    loaded_data = repository.load_skill_data(user_id)
    
    # Should have at most 10 events
    assert len(loaded_data.star_history) <= 10, \
        f"Star history should be truncated to 10, got {len(loaded_data.star_history)}"
    
    # If we had more than 10, verify we kept the last 10
    if num_events > 10:
        assert len(loaded_data.star_history) == 10
        # Last event should be the most recent one
        assert loaded_data.star_history[-1]['source'] == f'event_{num_events - 1}'


@given(
    days_old=st.integers(min_value=0, max_value=60)
)
@settings(max_examples=50)
def test_old_star_history_cleanup(days_old):
    """
    For any star history event older than 30 days,
    it should be removed during save/load cycle.
    
    **Validates: Requirements 10.5**
    """
    db, get_user, save_user = create_mock_database()
    repository = SkillRepository(get_user, save_user)
    
    user_id = 'test_user'
    db[user_id] = {'user_id': user_id}
    
    # Create event with specific age
    event_time = datetime.now() - timedelta(days=days_old)
    
    history = [{
        'timestamp': event_time.isoformat(),
        'source': 'old_event',
        'amount': 5
    }]
    
    skill_data = SkillData(
        star_balance=10,
        skills=initialize_default_skills(),
        star_history=history
    )
    
    # Save and load
    repository.save_skill_data(user_id, skill_data)
    loaded_data = repository.load_skill_data(user_id)
    
    # If event is older than 30 days, it should be removed
    if days_old >= 30:
        assert len(loaded_data.star_history) == 0, \
            f"Event older than 30 days should be removed, but found {len(loaded_data.star_history)} events"
    else:
        assert len(loaded_data.star_history) == 1, \
            f"Event younger than 30 days should be preserved, but found {len(loaded_data.star_history)} events"


@given(
    skill_data=valid_skill_data()
)
@settings(max_examples=100)
def test_multiple_save_load_cycles_preserve_data(skill_data):
    """
    For any skill data, multiple save/load cycles should preserve the data
    without corruption or data loss.
    
    **Validates: Requirements 9.1, 9.2**
    """
    db, get_user, save_user = create_mock_database()
    repository = SkillRepository(get_user, save_user)
    
    user_id = 'test_user'
    db[user_id] = {'user_id': user_id}
    
    # Ensure all skills present
    all_skills = initialize_default_skills()
    all_skills.update(skill_data.skills)
    skill_data.skills = all_skills
    
    # Perform multiple save/load cycles
    current_data = skill_data
    for cycle in range(3):
        repository.save_skill_data(user_id, current_data)
        current_data = repository.load_skill_data(user_id)
    
    # After 3 cycles, data should still match original (accounting for history truncation)
    assert current_data.star_balance == skill_data.star_balance
    assert current_data.total_stars_spent == skill_data.total_stars_spent
    
    # All skill levels should be preserved
    for skill_id in SKILL_TREE_CONFIG.keys():
        assert current_data.skills[skill_id] == skill_data.skills[skill_id]


@given(
    balance=st.integers(min_value=-1000, max_value=1000),
    level=st.integers(min_value=-5, max_value=15)
)
@settings(max_examples=100)
def test_invalid_data_repair_during_load(balance, level):
    """
    For any corrupted skill data (negative balance, invalid levels),
    loading should repair the data to valid state.
    
    **Validates: Requirements 9.4**
    """
    db, get_user, save_user = create_mock_database()
    repository = SkillRepository(get_user, save_user)
    
    user_id = 'test_user'
    
    # Create user with corrupted data
    db[user_id] = {
        'user_id': user_id,
        'skill_data': {
            'star_balance': balance,
            'skills': {'luck_1': level},
            'total_stars_spent': 10
        }
    }
    
    # Load (should trigger repair)
    loaded_data = repository.load_skill_data(user_id)
    
    # Verify repairs
    # Star balance should be non-negative
    assert loaded_data.star_balance >= 0, \
        f"Star balance should be repaired to non-negative, got {loaded_data.star_balance}"
    
    # Skill level should be clamped to 1-10
    assert 1 <= loaded_data.skills['luck_1'] <= 10, \
        f"Skill level should be clamped to 1-10, got {loaded_data.skills['luck_1']}"
    
    # All skills should be present
    assert len(loaded_data.skills) == len(SKILL_TREE_CONFIG), \
        f"All skills should be present after repair, got {len(loaded_data.skills)}"

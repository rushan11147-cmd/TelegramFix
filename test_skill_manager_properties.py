# -*- coding: utf-8 -*-
"""
Property-Based Tests for SkillManager

Tests universal properties that should hold across all valid inputs:
- Property 12: Skill Cost Formula
- Property 9: Upgrade Atomicity
- Property 8: Valid Upgrade Preconditions

Uses hypothesis for property-based testing with 100+ iterations per test.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from copy import deepcopy

from skill_manager import SkillManager
from skills_config import (
    SkillData,
    SkillNode,
    SKILL_TREE_CONFIG,
    get_skill_by_id,
    initialize_default_skills
)


# ============================================================================
# PROPERTY 12: Skill Cost Formula
# ============================================================================

@settings(max_examples=100)
@given(
    current_level=st.integers(min_value=1, max_value=9),
    skill_id=st.sampled_from(list(SKILL_TREE_CONFIG.keys()))
)
def test_property_12_skill_cost_formula(current_level, skill_id):
    """
    Feature: skills-tree-system, Property 12: Skill Cost Formula
    
    For any skill at current level L, the cost to upgrade to level L+1
    should be exactly base_cost + L, where base_cost is 2 for basic skills
    and 3 for advanced skills.
    
    **Validates: Requirements 5.1, 5.5**
    
    Formula: cost = base_cost + current_level
    - Basic skills (luck, charisma, intelligence): base_cost = 2
    - Advanced skills (endurance, business): base_cost = 3
    """
    manager = SkillManager()
    skill = get_skill_by_id(skill_id)
    
    # Calculate expected cost
    expected_cost = skill.base_cost + current_level
    
    # Calculate actual cost
    actual_cost = manager.calculate_skill_cost(skill_id, current_level)
    
    # Verify formula
    assert actual_cost == expected_cost, \
        f"Cost formula incorrect for {skill_id} at level {current_level}: " \
        f"expected {expected_cost}, got {actual_cost}"
    
    # Verify base cost is correct for skill type
    if skill.branch in ['luck', 'charisma', 'intelligence']:
        assert skill.base_cost == 2, \
            f"Basic skill {skill_id} should have base_cost=2, got {skill.base_cost}"
    elif skill.branch in ['endurance', 'business']:
        assert skill.base_cost == 3, \
            f"Advanced skill {skill_id} should have base_cost=3, got {skill.base_cost}"


@settings(max_examples=100)
@given(
    skill_id=st.sampled_from(list(SKILL_TREE_CONFIG.keys()))
)
def test_property_12_cost_increases_with_level(skill_id):
    """
    Property 12 corollary: Cost should strictly increase with level.
    
    For any skill, cost(level+1) > cost(level) for all valid levels.
    """
    manager = SkillManager()
    
    for level in range(1, 9):
        cost_current = manager.calculate_skill_cost(skill_id, level)
        cost_next = manager.calculate_skill_cost(skill_id, level + 1)
        
        assert cost_next > cost_current, \
            f"Cost should increase with level for {skill_id}: " \
            f"level {level} costs {cost_current}, level {level+1} costs {cost_next}"


@settings(max_examples=100)
@given(
    skill_id=st.sampled_from(list(SKILL_TREE_CONFIG.keys()))
)
def test_property_12_max_level_cost_is_zero(skill_id):
    """
    Property 12 edge case: Cost at max level should be 0 (cannot upgrade).
    """
    manager = SkillManager()
    skill = get_skill_by_id(skill_id)
    
    cost_at_max = manager.calculate_skill_cost(skill_id, skill.max_level)
    
    assert cost_at_max == 0, \
        f"Cost at max level should be 0 for {skill_id}, got {cost_at_max}"


# ============================================================================
# PROPERTY 9: Upgrade Atomicity
# ============================================================================

@settings(max_examples=100)
@given(
    initial_stars=st.integers(min_value=0, max_value=100),
    skill_id=st.sampled_from(list(SKILL_TREE_CONFIG.keys())),
    initial_level=st.integers(min_value=1, max_value=9)
)
def test_property_9_upgrade_atomicity_success(initial_stars, skill_id, initial_level):
    """
    Feature: skills-tree-system, Property 9: Upgrade Atomicity
    
    For any successful skill upgrade, both the star deduction and level
    increment should occur atomically - either both happen or neither happens.
    
    **Validates: Requirements 3.2**
    
    This test verifies the success case: when upgrade succeeds, both
    star balance decreases and skill level increases by exactly the right amounts.
    """
    manager = SkillManager()
    skill = get_skill_by_id(skill_id)
    
    # Calculate cost
    cost = manager.calculate_skill_cost(skill_id, initial_level)
    
    # Only test cases where player has enough stars
    assume(initial_stars >= cost)
    
    # Create skill data
    skills = initialize_default_skills()
    skills[skill_id] = initial_level
    skill_data = SkillData(
        star_balance=initial_stars,
        skills=skills,
        total_stars_spent=0
    )
    
    # Save initial state
    initial_balance = skill_data.star_balance
    initial_skill_level = skill_data.skills[skill_id]
    initial_total_spent = skill_data.total_stars_spent
    
    # Attempt upgrade
    result = manager.apply_skill_upgrade(skill_data, skill_id)
    
    if result:
        # Both operations must have occurred
        assert skill_data.star_balance == initial_balance - cost, \
            f"Stars not deducted correctly: expected {initial_balance - cost}, " \
            f"got {skill_data.star_balance}"
        
        assert skill_data.skills[skill_id] == initial_skill_level + 1, \
            f"Level not incremented correctly: expected {initial_skill_level + 1}, " \
            f"got {skill_data.skills[skill_id]}"
        
        assert skill_data.total_stars_spent == initial_total_spent + cost, \
            f"Total spent not updated correctly: expected {initial_total_spent + cost}, " \
            f"got {skill_data.total_stars_spent}"


@settings(max_examples=100)
@given(
    initial_stars=st.integers(min_value=0, max_value=20),
    skill_id=st.sampled_from(list(SKILL_TREE_CONFIG.keys())),
    initial_level=st.integers(min_value=1, max_value=9)
)
def test_property_9_upgrade_atomicity_failure(initial_stars, skill_id, initial_level):
    """
    Property 9: Upgrade Atomicity - Failure Case
    
    When upgrade fails (insufficient stars), neither star balance nor
    skill level should change.
    """
    manager = SkillManager()
    
    # Calculate cost
    cost = manager.calculate_skill_cost(skill_id, initial_level)
    
    # Only test cases where player doesn't have enough stars
    assume(initial_stars < cost)
    
    # Create skill data
    skills = initialize_default_skills()
    skills[skill_id] = initial_level
    skill_data = SkillData(
        star_balance=initial_stars,
        skills=skills,
        total_stars_spent=0
    )
    
    # Save initial state
    initial_balance = skill_data.star_balance
    initial_skill_level = skill_data.skills[skill_id]
    initial_total_spent = skill_data.total_stars_spent
    
    # Attempt upgrade (should fail)
    result = manager.apply_skill_upgrade(skill_data, skill_id)
    
    # Verify nothing changed
    assert not result, "Upgrade should have failed with insufficient stars"
    assert skill_data.star_balance == initial_balance, \
        "Star balance should not change on failed upgrade"
    assert skill_data.skills[skill_id] == initial_skill_level, \
        "Skill level should not change on failed upgrade"
    assert skill_data.total_stars_spent == initial_total_spent, \
        "Total spent should not change on failed upgrade"


@settings(max_examples=50)
@given(
    initial_stars=st.integers(min_value=50, max_value=200),
    skill_id=st.sampled_from(list(SKILL_TREE_CONFIG.keys()))
)
def test_property_9_multiple_upgrades_atomicity(initial_stars, skill_id):
    """
    Property 9: Multiple sequential upgrades should each be atomic.
    """
    manager = SkillManager()
    
    # Create skill data
    skills = initialize_default_skills()
    skill_data = SkillData(
        star_balance=initial_stars,
        skills=skills,
        total_stars_spent=0
    )
    
    # Track total changes
    total_cost = 0
    upgrades_performed = 0
    
    # Perform multiple upgrades
    for _ in range(9):  # Max 9 upgrades (level 1 to 10)
        current_level = skill_data.skills[skill_id]
        if current_level >= 10:
            break
        
        cost = manager.calculate_skill_cost(skill_id, current_level)
        if skill_data.star_balance < cost:
            break
        
        initial_balance = skill_data.star_balance
        initial_level = skill_data.skills[skill_id]
        
        result = manager.apply_skill_upgrade(skill_data, skill_id)
        
        if result:
            # Verify atomic operation
            assert skill_data.star_balance == initial_balance - cost
            assert skill_data.skills[skill_id] == initial_level + 1
            total_cost += cost
            upgrades_performed += 1
    
    # Verify total consistency
    assert skill_data.total_stars_spent == total_cost, \
        f"Total stars spent should equal sum of costs: {total_cost}, " \
        f"got {skill_data.total_stars_spent}"


# ============================================================================
# PROPERTY 8: Valid Upgrade Preconditions
# ============================================================================

@settings(max_examples=100)
@given(
    star_balance=st.integers(min_value=0, max_value=100),
    skill_id=st.sampled_from(list(SKILL_TREE_CONFIG.keys())),
    skill_level=st.integers(min_value=1, max_value=9)
)
def test_property_8_valid_upgrade_preconditions(star_balance, skill_id, skill_level):
    """
    Feature: skills-tree-system, Property 8: Valid Upgrade Preconditions
    
    For any skill upgrade attempt, if the player has sufficient stars AND
    meets all prerequisites, the upgrade should succeed; otherwise it should
    fail with appropriate error message.
    
    **Validates: Requirements 3.1, 3.3, 3.4**
    
    Preconditions:
    1. Skill exists
    2. Skill not at max level
    3. Prerequisites met
    4. Sufficient stars
    """
    manager = SkillManager()
    skill = get_skill_by_id(skill_id)
    
    # Create skill data with all prerequisites met
    skills = initialize_default_skills()
    skills[skill_id] = skill_level
    
    # Ensure all prerequisites are at level 1 (met)
    for prereq_id in skill.prerequisites:
        skills[prereq_id] = 1
    
    skill_data = SkillData(
        star_balance=star_balance,
        skills=skills
    )
    
    # Calculate cost
    cost = manager.calculate_skill_cost(skill_id, skill_level)
    
    # Check if upgrade should succeed
    can_upgrade, error = manager.can_upgrade_skill(skill_data, skill_id)
    
    # Determine expected result
    has_sufficient_stars = star_balance >= cost
    is_not_max_level = skill_level < skill.max_level
    prerequisites_met = True  # We set them all to level 1
    
    should_succeed = has_sufficient_stars and is_not_max_level and prerequisites_met
    
    # Verify precondition check matches expected result
    assert can_upgrade == should_succeed, \
        f"Precondition check mismatch for {skill_id} at level {skill_level} " \
        f"with {star_balance} stars (cost: {cost}): " \
        f"expected {should_succeed}, got {can_upgrade}. Error: {error}"
    
    # Verify error message is appropriate
    if not can_upgrade:
        assert len(error) > 0, "Error message should not be empty when upgrade fails"
        
        if not has_sufficient_stars:
            assert "звезд" in error.lower() or "требуется" in error.lower(), \
                f"Error should mention stars when insufficient: {error}"


@settings(max_examples=100)
@given(
    star_balance=st.integers(min_value=100, max_value=200),
    skill_id=st.sampled_from([sid for sid, s in SKILL_TREE_CONFIG.items() if s.prerequisites])
)
def test_property_8_prerequisite_validation(star_balance, skill_id):
    """
    Property 8: Prerequisites must be validated correctly.
    
    Skills with unmet prerequisites should fail upgrade even with sufficient stars.
    """
    manager = SkillManager()
    skill = get_skill_by_id(skill_id)
    
    # Create skill data WITHOUT prerequisites met
    skills = initialize_default_skills()
    skills[skill_id] = 1
    
    # Deliberately set prerequisites to 0 (unmet)
    for prereq_id in skill.prerequisites:
        skills[prereq_id] = 0
    
    skill_data = SkillData(
        star_balance=star_balance,  # Plenty of stars
        skills=skills
    )
    
    # Should fail due to unmet prerequisites
    can_upgrade, error = manager.can_upgrade_skill(skill_data, skill_id)
    
    assert not can_upgrade, \
        f"Upgrade should fail for {skill_id} with unmet prerequisites"
    assert len(error) > 0, "Error message should explain unmet prerequisites"


@settings(max_examples=100)
@given(
    star_balance=st.integers(min_value=100, max_value=200),
    skill_id=st.sampled_from(list(SKILL_TREE_CONFIG.keys()))
)
def test_property_8_max_level_prevention(star_balance, skill_id):
    """
    Property 8: Skills at max level should not be upgradeable.
    """
    manager = SkillManager()
    skill = get_skill_by_id(skill_id)
    
    # Create skill data with skill at max level
    skills = initialize_default_skills()
    skills[skill_id] = skill.max_level
    
    # Ensure prerequisites are met
    for prereq_id in skill.prerequisites:
        skills[prereq_id] = 1
    
    skill_data = SkillData(
        star_balance=star_balance,  # Plenty of stars
        skills=skills
    )
    
    # Should fail due to max level
    can_upgrade, error = manager.can_upgrade_skill(skill_data, skill_id)
    
    assert not can_upgrade, \
        f"Upgrade should fail for {skill_id} at max level {skill.max_level}"
    assert "максимальном" in error.lower() or "max" in error.lower(), \
        f"Error should mention max level: {error}"


@settings(max_examples=100)
@given(
    star_balance=st.integers(min_value=100, max_value=200),
    skill_id=st.sampled_from(list(SKILL_TREE_CONFIG.keys())),
    skill_level=st.integers(min_value=1, max_value=9)
)
def test_property_8_sufficient_stars_with_prerequisites(star_balance, skill_id, skill_level):
    """
    Property 8: With sufficient stars AND met prerequisites, upgrade should succeed.
    """
    manager = SkillManager()
    skill = get_skill_by_id(skill_id)
    
    # Create skill data with prerequisites met
    skills = initialize_default_skills()
    skills[skill_id] = skill_level
    
    # Ensure all prerequisites are met
    for prereq_id in skill.prerequisites:
        skills[prereq_id] = 5  # Well above minimum
    
    skill_data = SkillData(
        star_balance=star_balance,  # Plenty of stars
        skills=skills
    )
    
    # Calculate cost
    cost = manager.calculate_skill_cost(skill_id, skill_level)
    
    # Only test when we have enough stars
    assume(star_balance >= cost)
    
    # Should succeed
    can_upgrade, error = manager.can_upgrade_skill(skill_data, skill_id)
    
    assert can_upgrade, \
        f"Upgrade should succeed for {skill_id} at level {skill_level} " \
        f"with {star_balance} stars (cost: {cost}). Error: {error}"
    assert error == "", "Error message should be empty on success"


# ============================================================================
# PROPERTY TEST: Cost Consistency
# ============================================================================

@settings(max_examples=100)
@given(
    skill_id=st.sampled_from(list(SKILL_TREE_CONFIG.keys()))
)
def test_cost_consistency_across_methods(skill_id):
    """
    Verify that cost calculation is consistent between SkillManager
    and SkillNode methods.
    """
    manager = SkillManager()
    skill = get_skill_by_id(skill_id)
    
    for level in range(1, 10):
        manager_cost = manager.calculate_skill_cost(skill_id, level)
        node_cost = skill.calculate_cost(level)
        
        assert manager_cost == node_cost, \
            f"Cost mismatch for {skill_id} at level {level}: " \
            f"manager={manager_cost}, node={node_cost}"

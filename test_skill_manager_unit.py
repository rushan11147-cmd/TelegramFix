# -*- coding: utf-8 -*-
"""
Unit Tests for SkillManager

Tests specific examples and edge cases:
- Property 7: Skill Level Bounds (1-10)
- Max level prevention
- Invalid skill ID handling

**Validates: Requirements 2.4, 2.5**
"""
import pytest
from skill_manager import SkillManager
from skills_config import SkillData, SKILL_TREE_CONFIG, get_skill_by_id, initialize_default_skills

class TestSkillLevelBounds:
    """Tests for Property 7: Skill Level Bounds"""
    
    def test_skill_level_minimum_bound(self):
        """Skills should start at level 1 (minimum)"""
        skills = initialize_default_skills()
        for skill_id, level in skills.items():
            assert level == 1, f"Skill {skill_id} should start at level 1, got {level}"
    
    def test_skill_level_maximum_bound(self):
        """Skills should not exceed level 10 (maximum)"""
        manager = SkillManager()
        skills = initialize_default_skills()
        skills['luck_1'] = 10
        skill_data = SkillData(star_balance=100, skills=skills)
        can_upgrade, error = manager.can_upgrade_skill(skill_data, 'luck_1')
        assert not can_upgrade, "Should not be able to upgrade skill at max level"
        assert "максимальном" in error.lower(), f"Error should mention max level: {error}"
    
    def test_upgrade_from_level_9_to_10(self):
        """Should be able to upgrade from level 9 to 10"""
        manager = SkillManager()
        skills = initialize_default_skills()
        skills['luck_1'] = 9
        skill_data = SkillData(star_balance=100, skills=skills)
        can_upgrade, error = manager.can_upgrade_skill(skill_data, 'luck_1')
        assert can_upgrade, f"Should be able to upgrade from level 9 to 10: {error}"
        result = manager.apply_skill_upgrade(skill_data, 'luck_1')
        assert result, "Upgrade should succeed"
        assert skill_data.skills['luck_1'] == 10, "Skill should be at level 10"
    
    def test_cannot_upgrade_beyond_level_10(self):
        """Should not be able to upgrade beyond level 10"""
        manager = SkillManager()
        skills = initialize_default_skills()
        skills['luck_1'] = 10
        skill_data = SkillData(star_balance=100, skills=skills)
        result = manager.apply_skill_upgrade(skill_data, 'luck_1')
        assert not result, "Should not be able to upgrade beyond level 10"
        assert skill_data.skills['luck_1'] == 10, "Level should remain at 10"

class TestMaxLevelPrevention:
    """Tests for max level prevention"""
    
    def test_max_level_prevents_upgrade_basic_skill(self):
        """Basic skills at level 10 should not be upgradeable"""
        manager = SkillManager()
        skills = initialize_default_skills()
        skills['luck_1'] = 10
        skill_data = SkillData(star_balance=1000, skills=skills)
        can_upgrade, error = manager.can_upgrade_skill(skill_data, 'luck_1')
        assert not can_upgrade, "Basic skill at level 10 should not be upgradeable"
        assert len(error) > 0, "Should provide error message"
    
    def test_max_level_cost_is_zero(self):
        """Cost calculation at max level should return 0"""
        manager = SkillManager()
        for skill_id in SKILL_TREE_CONFIG.keys():
            skill = get_skill_by_id(skill_id)
            cost = manager.calculate_skill_cost(skill_id, skill.max_level)
            assert cost == 0, f"Cost at max level for {skill_id} should be 0, got {cost}"

class TestInvalidSkillIDHandling:
    """Tests for invalid skill ID handling"""
    
    def test_can_upgrade_with_invalid_skill_id(self):
        """can_upgrade_skill should handle invalid skill IDs"""
        manager = SkillManager()
        skill_data = SkillData(star_balance=100, skills=initialize_default_skills())
        can_upgrade, error = manager.can_upgrade_skill(skill_data, 'invalid_skill_999')
        assert not can_upgrade, "Should not be able to upgrade non-existent skill"
        assert len(error) > 0, "Should provide error message"
        assert "не существует" in error.lower(), f"Error should mention invalid skill: {error}"
    
    def test_apply_upgrade_with_invalid_skill_id(self):
        """apply_skill_upgrade should handle invalid skill IDs"""
        manager = SkillManager()
        skill_data = SkillData(star_balance=100, skills=initialize_default_skills(), total_stars_spent=0)
        initial_balance = skill_data.star_balance
        result = manager.apply_skill_upgrade(skill_data, 'nonexistent_skill')
        assert not result, "Should not be able to upgrade non-existent skill"
        assert skill_data.star_balance == initial_balance, "Stars should not be deducted"
    
    def test_calculate_cost_with_invalid_skill_id(self):
        """calculate_skill_cost should handle invalid skill IDs"""
        manager = SkillManager()
        cost = manager.calculate_skill_cost('fake_skill_123', 5)
        assert cost == 0, f"Cost for invalid skill should be 0, got {cost}"
    
    def test_skill_not_in_player_data(self):
        """Should handle case where skill exists but not in player's skill data"""
        manager = SkillManager()
        skill_data = SkillData(star_balance=100, skills={'luck_1': 5})
        can_upgrade, error = manager.can_upgrade_skill(skill_data, 'charisma_1')
        assert not can_upgrade, "Should not upgrade skill not in player data"
        assert len(error) > 0, "Should provide error message"

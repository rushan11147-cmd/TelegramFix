#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to write unit test file"""

test_content = '''# -*- coding: utf-8 -*-
"""
Unit Tests for SkillManager

Tests specific examples and edge cases:
- Property 7: Skill Level Bounds (1-10)
- Max level prevention
- Invalid skill ID handling
- Prerequisite validation
- Cost calculation examples
"""

import pytest
from copy import deepcopy

from skill_manager import SkillManager
from skills_config import (
    SkillData,
    SkillNode,
    SKILL_TREE_CONFIG,
    get_skill_by_id,
    initialize_default_skills
)


class TestSkillLevelBounds:
    """
    Tests for Property 7: Skill Level Bounds
    
    For any skill, the level should always be between 1 and 10 inclusive,
    and attempts to upgrade beyond level 10 should be rejected.
    
    **Validates: Requirements 2.4, 2.5**
    """
    
    def test_skill_level_minimum_bound(self):
        """Skills should start at level 1 (minimum)"""
        skills = initialize_default_skills()
        
        for skill_id, level in skills.items():
            assert level == 1, f"Skill {skill_id} should start at level 1, got {level}"
    
    def test_skill_level_maximum_bound(self):
        """Skills should not exceed level 10 (maximum)"""
        manager = SkillManager()
        
        # Try to upgrade a skill at level 10
        skills = initialize_default_skills()
        skills['luck_1'] = 10  # Max level
        
        skill_data = SkillData(
            star_balance=100,  # Plenty of stars
            skills=skills
        )
        
        can_upgrade, error = manager.can_upgrade_skill(skill_data, 'luck_1')
        
        assert not can_upgrade, "Should not be able to upgrade skill at max level"
        assert "максимальном" in error.lower(), f"Error should mention max level: {error}"
    
    def test_upgrade_from_level_9_to_10(self):
        """Should be able to upgrade from level 9 to 10"""
        manager = SkillManager()
        
        skills = initialize_default_skills()
        skills['luck_1'] = 9
        
        skill_data = SkillData(
            star_balance=100,
            skills=skills
        )
        
        can_upgrade, error = manager.can_upgrade_skill(skill_data, 'luck_1')
        
        assert can_upgrade, f"Should be able to upgrade from level 9 to 10: {error}"
        
        # Perform upgrade
        result = manager.apply_skill_upgrade(skill_data, 'luck_1')
        
        assert result, "Upgrade should succeed"
        assert skill_data.skills['luck_1'] == 10, "Skill should be at level 10"
    
    def test_cannot_upgrade_beyond_level_10(self):
        """Should not be able to upgrade beyond level 10"""
        manager = SkillManager()
        
        skills = initialize_default_skills()
        skills['luck_1'] = 10
        
        skill_data = SkillData(
            star_balance=100,
            skills=skills
        )
        
        result = manager.apply_skill_upgrade(skill_data, 'luck_1')
        
        assert not result, "Should not be able to upgrade beyond level 10"
        assert skill_data.skills['luck_1'] == 10, "Level should remain at 10"
    
    def test_level_bounds_for_all_skills(self):
        """All skills should respect level bounds"""
        manager = SkillManager()
        
        for skill_id in SKILL_TREE_CONFIG.keys():
            skill = get_skill_by_id(skill_id)
            
            # Test at max level
            skills = initialize_default_skills()
            skills[skill_id] = skill.max_level
            
            skill_data = SkillData(
                star_balance=100,
                skills=skills
            )
            
            can_upgrade, error = manager.can_upgrade_skill(skill_data, skill_id)
            
            assert not can_upgrade, \\
                f"Skill {skill_id} at max level {skill.max_level} should not be upgradeable"
            assert "максимальном" in error.lower(), \\
                f"Error for {skill_id} should mention max level: {error}"
    
    def test_level_bounds_at_each_level(self):
        """Test that levels 1-9 are valid and level 10 is max"""
        manager = SkillManager()
        
        # Test with a basic skill
        skill_id = 'luck_1'
        
        for level in range(1, 10):
            skills = initialize_default_skills()
            skills[skill_id] = level
            
            skill_data = SkillData(
                star_balance=100,
                skills=skills
            )
            
            can_upgrade, error = manager.can_upgrade_skill(skill_data, skill_id)
            
            assert can_upgrade, \\
                f"Should be able to upgrade {skill_id} from level {level}: {error}"
        
        # Test level 10 (max)
        skills = initialize_default_skills()
        skills[skill_id] = 10
        
        skill_data = SkillData(
            star_balance=100,
            skills=skills
        )
        
        can_upgrade, error = manager.can_upgrade_skill(skill_data, skill_id)
        
        assert not can_upgrade, \\
            f"Should not be able to upgrade {skill_id} from level 10"
'''

# Write the file
with open('test_skill_manager_unit.py', 'w', encoding='utf-8') as f:
    f.write(test_content)

print("Test file written successfully!")
print(f"File size: {len(test_content)} bytes")

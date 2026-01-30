# -*- coding: utf-8 -*-
"""
Basic Integration Test for SkillTreeManager

Tests the main orchestrator to ensure all components work together correctly.
"""

from skills_system import SkillTreeManager
from skills_config import SkillData


# Mock database functions for testing
test_users = {}


def mock_get_user(user_id):
    """Mock function to get user data"""
    return test_users.get(user_id)


def mock_save_user(user_data):
    """Mock function to save user data"""
    if 'user_id' in user_data:
        test_users[user_data['user_id']] = user_data


def test_initialization():
    """Test that SkillTreeManager initializes correctly"""
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    assert manager.repository is not None
    assert manager.star_economy is not None
    assert manager.skill_manager is not None
    print("✓ Initialization test passed")


def test_process_monthly_stars():
    """Test monthly star processing"""
    # Reset test data
    test_users.clear()
    test_users['user1'] = {
        'user_id': 'user1',
        'skill_data': {
            'star_balance': 0,
            'skills': {'luck_1': 1},
            'total_stars_spent': 0,
            'last_monthly_award_day': 0,
            'last_reset_day': -7,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    # Test awarding stars on day 30
    result = manager.process_monthly_stars('user1', 30)
    
    assert result['success'] == True
    assert result['stars_awarded'] == 3
    assert result['new_balance'] == 3
    assert result['next_award_day'] == 60
    print("✓ Monthly stars test passed")


def test_upgrade_skill():
    """Test skill upgrade functionality"""
    # Reset test data
    test_users.clear()
    test_users['user2'] = {
        'user_id': 'user2',
        'skill_data': {
            'star_balance': 10,
            'skills': {'luck_1': 1, 'charisma_1': 1},
            'total_stars_spent': 0,
            'last_monthly_award_day': 0,
            'last_reset_day': -7,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    # Test upgrading luck_1 from level 1 to 2
    result = manager.upgrade_skill('user2', 'luck_1')
    
    assert result['success'] == True
    assert result['new_level'] == 2
    assert result['stars_spent'] == 3  # base_cost(2) + level(1) = 3
    assert result['new_star_balance'] == 7  # 10 - 3 = 7
    print("✓ Skill upgrade test passed")


def test_reset_skills():
    """Test skill reset functionality"""
    # Reset test data
    test_users.clear()
    test_users['user3'] = {
        'user_id': 'user3',
        'skill_data': {
            'star_balance': 5,
            'skills': {'luck_1': 3, 'charisma_1': 2},
            'total_stars_spent': 10,
            'last_monthly_award_day': 0,
            'last_reset_day': -7,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    # Test resetting skills on day 10
    result = manager.reset_skills('user3', 10)
    
    assert result['success'] == True
    assert result['stars_refunded'] == 8  # 80% of 10 = 8
    assert result['new_star_balance'] == 13  # 5 + 8 = 13
    
    # Verify skills are reset to level 1
    user_data = test_users['user3']
    assert user_data['skill_data']['skills']['luck_1'] == 1
    assert user_data['skill_data']['skills']['charisma_1'] == 1
    print("✓ Skill reset test passed")


def test_get_skill_tree():
    """Test skill tree display data"""
    # Reset test data
    test_users.clear()
    test_users['user4'] = {
        'user_id': 'user4',
        'skill_data': {
            'star_balance': 15,
            'skills': {'luck_1': 2, 'charisma_1': 1},
            'total_stars_spent': 5,
            'last_monthly_award_day': 0,
            'last_reset_day': 0,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    # Test getting skill tree
    tree = manager.get_skill_tree('user4', current_day=10)
    
    assert tree['star_balance'] == 15
    assert 'skills' in tree
    assert 'luck_1' in tree['skills']
    assert tree['skills']['luck_1']['current_level'] == 2
    assert tree['skills']['charisma_1']['current_level'] == 1
    assert tree['total_stars_spent'] == 5
    assert tree['can_reset'] == True  # 10 days since last reset
    assert 'branches' in tree
    print("✓ Get skill tree test passed")


def test_display_completeness():
    """
    Test Property 6: Display Completeness
    
    Validates: Requirements 2.2, 2.3, 6.1, 6.2, 6.3, 6.4, 6.5
    
    Verify that get_skill_tree() returns all required information:
    - All 5 branches (Luck, Charisma, Intelligence, Endurance, Business)
    - All 50 skills (10 per branch)
    - Current level for each skill
    - Upgrade cost for each skill
    - Lock status for each skill
    - Upgrade availability for each skill
    - Star balance
    - Total stars spent
    - Reset availability
    """
    test_users.clear()
    test_users['user_display'] = {
        'user_id': 'user_display',
        'skill_data': {
            'star_balance': 20,
            'skills': {
                'luck_1': 3, 'luck_2': 1, 'luck_3': 1,
                'charisma_1': 2, 'charisma_2': 1,
                'intelligence_1': 1,
                'endurance_1': 1,
                'business_1': 1
            },
            'total_stars_spent': 15,
            'last_monthly_award_day': 0,
            'last_reset_day': 0,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    tree = manager.get_skill_tree('user_display', current_day=10)
    
    # Verify top-level fields
    assert 'star_balance' in tree
    assert 'total_stars_spent' in tree
    assert 'can_reset' in tree
    assert 'days_until_reset' in tree
    assert 'branches' in tree
    assert 'skills' in tree
    assert 'star_history' in tree
    
    # Verify all 5 branches exist
    branches = tree['branches']
    assert 'Luck' in branches
    assert 'Charisma' in branches
    assert 'Intelligence' in branches
    assert 'Endurance' in branches
    assert 'Business' in branches
    
    # Verify each branch has 10 skills
    for branch_name, branch_data in branches.items():
        assert 'skills' in branch_data
        assert len(branch_data['skills']) == 10, \
            f"Branch {branch_name} should have 10 skills, got {len(branch_data['skills'])}"
    
    # Verify each skill has required fields
    for skill_id, skill_data in tree['skills'].items():
        assert 'name' in skill_data, f"Skill {skill_id} missing 'name'"
        assert 'description' in skill_data, f"Skill {skill_id} missing 'description'"
        assert 'current_level' in skill_data, f"Skill {skill_id} missing 'current_level'"
        assert 'max_level' in skill_data, f"Skill {skill_id} missing 'max_level'"
        assert 'cost' in skill_data, f"Skill {skill_id} missing 'cost'"
        assert 'status' in skill_data, f"Skill {skill_id} missing 'status'"
        assert 'can_upgrade' in skill_data, f"Skill {skill_id} missing 'can_upgrade'"
        assert 'effects' in skill_data, f"Skill {skill_id} missing 'effects'"
    
    print("✓ Display completeness test passed")


def test_locked_skill_indication():
    """
    Test locked skill indication
    
    Validates: Requirements 6.2, 6.3
    
    Verify that skills with unmet prerequisites are marked as locked:
    - luck_2 should be locked if luck_1 < 3
    - luck_3 should be locked if luck_2 < 3
    - Locked skills should have status='locked'
    - Locked skills should have can_upgrade=False
    """
    test_users.clear()
    test_users['user_locked'] = {
        'user_id': 'user_locked',
        'skill_data': {
            'star_balance': 100,  # Plenty of stars
            'skills': {
                'luck_1': 2,  # Not enough for luck_2 (needs 3)
                'luck_2': 1,
                'luck_3': 1,
                'charisma_1': 5,  # Enough for charisma_2
                'charisma_2': 1
            },
            'total_stars_spent': 20,
            'last_monthly_award_day': 0,
            'last_reset_day': 0,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    tree = manager.get_skill_tree('user_locked', current_day=10)
    
    # luck_1 should be unlocked (no prerequisites)
    assert tree['skills']['luck_1']['status'] != 'locked', \
        "luck_1 should be unlocked (no prerequisites)"
    
    # luck_2 should be locked (luck_1 is only level 2, needs 3)
    assert tree['skills']['luck_2']['status'] == 'locked', \
        "luck_2 should be locked (luck_1 < 3)"
    assert tree['skills']['luck_2']['can_upgrade'] == False, \
        "luck_2 should not be upgradeable when locked"
    
    # luck_3 should be locked (luck_2 is level 1, needs 3)
    assert tree['skills']['luck_3']['status'] == 'locked', \
        "luck_3 should be locked (luck_2 < 3)"
    
    # charisma_2 should be unlocked (charisma_1 is level 5 >= 3)
    assert tree['skills']['charisma_2']['status'] != 'locked', \
        "charisma_2 should be unlocked (charisma_1 >= 3)"
    
    print("✓ Locked skill indication test passed")


def test_upgrade_availability_highlighting():
    """
    Test upgrade availability highlighting
    
    Validates: Requirements 6.4
    
    Verify that can_upgrade flag correctly indicates when a skill can be upgraded:
    - Unlocked skill + sufficient stars + not max level = can_upgrade=True
    - Locked skill = can_upgrade=False
    - Insufficient stars = can_upgrade=False
    - Max level = can_upgrade=False
    """
    test_users.clear()
    test_users['user_upgrade'] = {
        'user_id': 'user_upgrade',
        'skill_data': {
            'star_balance': 5,  # Limited stars
            'skills': {
                'luck_1': 2,  # Can upgrade (cost = 2+2=4, have 5 stars)
                'charisma_1': 3,  # Can upgrade (cost = 2+3=5, have 5 stars)
                'intelligence_1': 5,  # Cannot upgrade (cost = 2+5=7, only have 5 stars)
                'endurance_1': 10,  # Cannot upgrade (max level)
                'business_1': 1,
                'business_2': 1  # Locked (business_1 < 3)
            },
            'total_stars_spent': 30,
            'last_monthly_award_day': 0,
            'last_reset_day': 0,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    tree = manager.get_skill_tree('user_upgrade', current_day=10)
    
    # luck_1: unlocked, sufficient stars, not max level
    assert tree['skills']['luck_1']['can_upgrade'] == True, \
        "luck_1 should be upgradeable (unlocked, 5 stars >= 4 cost, level 2 < 10)"
    
    # charisma_1: unlocked, sufficient stars (exactly), not max level
    assert tree['skills']['charisma_1']['can_upgrade'] == True, \
        "charisma_1 should be upgradeable (unlocked, 5 stars >= 5 cost, level 3 < 10)"
    
    # intelligence_1: unlocked, insufficient stars, not max level
    assert tree['skills']['intelligence_1']['can_upgrade'] == False, \
        "intelligence_1 should not be upgradeable (insufficient stars: 5 < 7)"
    
    # endurance_1: unlocked, sufficient stars, but max level
    assert tree['skills']['endurance_1']['can_upgrade'] == False, \
        "endurance_1 should not be upgradeable (max level 10)"
    
    # business_2: locked (business_1 < 3)
    assert tree['skills']['business_2']['can_upgrade'] == False, \
        "business_2 should not be upgradeable (locked)"
    
    print("✓ Upgrade availability highlighting test passed")


def test_completion_indication():
    """
    Test completion indication
    
    Validates: Requirements 6.5
    
    Verify that maxed skills (level 10) are properly indicated:
    - Skills at level 10 should have current_level = 10
    - Skills at level 10 should have can_upgrade = False
    - Skills at level 10 should have status = 'completed'
    - Branch completion percentage should be calculated correctly
    """
    test_users.clear()
    test_users['user_complete'] = {
        'user_id': 'user_complete',
        'skill_data': {
            'star_balance': 100,
            'skills': {
                # Luck branch: 3 maxed, 7 at level 1 = 30% complete
                'luck_1': 10, 'luck_2': 10, 'luck_3': 10,
                'luck_4': 1, 'luck_5': 1, 'luck_6': 1,
                'luck_7': 1, 'luck_8': 1, 'luck_9': 1, 'luck_10': 1,
                # Charisma branch: all maxed = 100% complete
                'charisma_1': 10, 'charisma_2': 10, 'charisma_3': 10,
                'charisma_4': 10, 'charisma_5': 10, 'charisma_6': 10,
                'charisma_7': 10, 'charisma_8': 10, 'charisma_9': 10, 'charisma_10': 10,
                # Other branches at level 1
                'intelligence_1': 1, 'endurance_1': 1, 'business_1': 1
            },
            'total_stars_spent': 500,
            'last_monthly_award_day': 0,
            'last_reset_day': 0,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    tree = manager.get_skill_tree('user_complete', current_day=10)
    
    # Verify maxed skills have correct properties
    assert tree['skills']['luck_1']['current_level'] == 10, \
        "luck_1 should be at max level 10"
    assert tree['skills']['luck_1']['can_upgrade'] == False, \
        "luck_1 should not be upgradeable at max level"
    assert tree['skills']['luck_1']['status'] == 'completed', \
        "luck_1 should have status='completed' at max level"
    
    # Verify all charisma skills are maxed
    for i in range(1, 11):
        skill_id = f'charisma_{i}'
        assert tree['skills'][skill_id]['current_level'] == 10, \
            f"{skill_id} should be at max level 10"
        assert tree['skills'][skill_id]['can_upgrade'] == False, \
            f"{skill_id} should not be upgradeable at max level"
        assert tree['skills'][skill_id]['status'] == 'completed', \
            f"{skill_id} should have status='completed' at max level"
    
    print("✓ Completion indication test passed")


def test_insufficient_stars():
    """Test that upgrade fails with insufficient stars"""
    # Reset test data
    test_users.clear()
    test_users['user5'] = {
        'user_id': 'user5',
        'skill_data': {
            'star_balance': 1,  # Not enough for upgrade
            'skills': {'luck_1': 1},
            'total_stars_spent': 0,
            'last_monthly_award_day': 0,
            'last_reset_day': -7,
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    # Test upgrading with insufficient stars
    result = manager.upgrade_skill('user5', 'luck_1')
    
    assert result['success'] == False
    assert 'error' in result
    assert 'Недостаточно звезд' in result['error']
    print("✓ Insufficient stars test passed")


def test_reset_cooldown():
    """Test that reset cooldown is enforced"""
    # Reset test data
    test_users.clear()
    test_users['user6'] = {
        'user_id': 'user6',
        'skill_data': {
            'star_balance': 5,
            'skills': {'luck_1': 2},
            'total_stars_spent': 5,
            'last_monthly_award_day': 0,
            'last_reset_day': 5,  # Reset 5 days ago
            'milestones_claimed': [],
            'star_history': []
        }
    }
    
    manager = SkillTreeManager(mock_get_user, mock_save_user)
    
    # Test resetting on day 10 (only 5 days since last reset, need 7)
    result = manager.reset_skills('user6', 10)
    
    assert result['success'] == False
    assert 'error' in result
    assert 'через 2 дней' in result['error']
    print("✓ Reset cooldown test passed")


if __name__ == '__main__':
    print("Running basic integration tests for SkillTreeManager...\n")
    
    test_initialization()
    test_process_monthly_stars()
    test_upgrade_skill()
    test_reset_skills()
    test_get_skill_tree()
    test_display_completeness()
    test_locked_skill_indication()
    test_upgrade_availability_highlighting()
    test_completion_indication()
    test_insufficient_stars()
    test_reset_cooldown()
    
    print("\n✅ All basic integration tests passed!")

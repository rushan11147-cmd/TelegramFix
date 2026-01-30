"""
Unit Tests for Star Economy Manager

Tests specific examples and edge cases for star award functionality.

Test Coverage:
- Monthly star awards (every 30 days)
- Wealth tier awards with duplicate prevention
- Achievement awards with duplicate prevention
- Milestone awards (1M earned, 100 days survived)
- Star source tracking
- Routine action exclusion

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 10.1, 10.4
"""

import pytest
from datetime import datetime, timedelta

from star_economy import (
    StarEconomyManager,
    format_star_notification,
    get_wealth_tier_name,
    get_achievement_name
)
from skills_config import (
    SkillData,
    MONTHLY_STARS,
    WEALTH_TIER_STARS,
    ACHIEVEMENT_STARS,
    MILLION_EARNED_STARS,
    SURVIVAL_100_DAYS_STARS
)


class TestMonthlyStarAwards:
    """Tests for monthly star awards (Requirement 1.1)"""
    
    def test_award_monthly_stars_at_30_days(self):
        """Test that 3 stars are awarded at exactly 30 days"""
        skill_data = SkillData(last_monthly_award_day=0)
        manager = StarEconomyManager()
        
        awarded = manager.award_monthly_stars(skill_data, 30)
        
        assert awarded == MONTHLY_STARS
        assert skill_data.star_balance == MONTHLY_STARS
        assert skill_data.last_monthly_award_day == 30
    
    def test_no_award_before_30_days(self):
        """Test that no stars are awarded before 30 days"""
        skill_data = SkillData(last_monthly_award_day=0)
        manager = StarEconomyManager()
        
        awarded = manager.award_monthly_stars(skill_data, 29)
        
        assert awarded == 0
        assert skill_data.star_balance == 0
        assert skill_data.last_monthly_award_day == 0
    
    def test_award_monthly_stars_after_30_days(self):
        """Test that stars are awarded after more than 30 days"""
        skill_data = SkillData(last_monthly_award_day=0)
        manager = StarEconomyManager()
        
        awarded = manager.award_monthly_stars(skill_data, 45)
        
        assert awarded == MONTHLY_STARS
        assert skill_data.star_balance == MONTHLY_STARS
        assert skill_data.last_monthly_award_day == 45
    
    def test_multiple_monthly_awards(self):
        """Test multiple monthly awards over time"""
        skill_data = SkillData(last_monthly_award_day=0)
        manager = StarEconomyManager()
        
        # First month
        awarded1 = manager.award_monthly_stars(skill_data, 30)
        assert awarded1 == MONTHLY_STARS
        
        # Second month
        awarded2 = manager.award_monthly_stars(skill_data, 60)
        assert awarded2 == MONTHLY_STARS
        assert skill_data.star_balance == MONTHLY_STARS * 2
        
        # Third month
        awarded3 = manager.award_monthly_stars(skill_data, 90)
        assert awarded3 == MONTHLY_STARS
        assert skill_data.star_balance == MONTHLY_STARS * 3
    
    def test_no_duplicate_award_same_day(self):
        """Test that stars are not awarded twice on the same day"""
        skill_data = SkillData(last_monthly_award_day=0)
        manager = StarEconomyManager()
        
        # First award
        awarded1 = manager.award_monthly_stars(skill_data, 30)
        assert awarded1 == MONTHLY_STARS
        
        # Try to award again on same day
        awarded2 = manager.award_monthly_stars(skill_data, 30)
        assert awarded2 == 0
        assert skill_data.star_balance == MONTHLY_STARS


class TestWealthTierAwards:
    """Tests for wealth tier awards (Requirement 1.2)"""
    
    def test_award_wealth_tier_stars_first_time(self):
        """Test that 5 stars are awarded for new wealth tier"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        awarded = manager.award_wealth_tier_stars(skill_data, "middle_class")
        
        assert awarded == WEALTH_TIER_STARS
        assert skill_data.star_balance == WEALTH_TIER_STARS
        assert "wealth_tier_middle_class" in skill_data.milestones_claimed
    
    def test_no_duplicate_wealth_tier_award(self):
        """Test that wealth tier stars are not awarded twice"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        # First award
        awarded1 = manager.award_wealth_tier_stars(skill_data, "middle_class")
        assert awarded1 == WEALTH_TIER_STARS
        
        # Try to award again
        awarded2 = manager.award_wealth_tier_stars(skill_data, "middle_class")
        assert awarded2 == 0
        assert skill_data.star_balance == WEALTH_TIER_STARS
    
    def test_multiple_different_wealth_tiers(self):
        """Test awards for multiple different wealth tiers"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        # Award for different tiers
        awarded1 = manager.award_wealth_tier_stars(skill_data, "stable")
        awarded2 = manager.award_wealth_tier_stars(skill_data, "middle_class")
        awarded3 = manager.award_wealth_tier_stars(skill_data, "wealthy")
        
        assert awarded1 == WEALTH_TIER_STARS
        assert awarded2 == WEALTH_TIER_STARS
        assert awarded3 == WEALTH_TIER_STARS
        assert skill_data.star_balance == WEALTH_TIER_STARS * 3
        assert len(skill_data.milestones_claimed) == 3


class TestAchievementAwards:
    """Tests for achievement awards (Requirement 1.3)"""
    
    def test_award_achievement_stars_first_time(self):
        """Test that 3 stars are awarded for new achievement"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        awarded = manager.award_achievement_stars(skill_data, "businessman")
        
        assert awarded == ACHIEVEMENT_STARS
        assert skill_data.star_balance == ACHIEVEMENT_STARS
        assert "achievement_businessman" in skill_data.milestones_claimed
    
    def test_no_duplicate_achievement_award(self):
        """Test that achievement stars are not awarded twice"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        # First award
        awarded1 = manager.award_achievement_stars(skill_data, "businessman")
        assert awarded1 == ACHIEVEMENT_STARS
        
        # Try to award again
        awarded2 = manager.award_achievement_stars(skill_data, "businessman")
        assert awarded2 == 0
        assert skill_data.star_balance == ACHIEVEMENT_STARS
    
    def test_multiple_different_achievements(self):
        """Test awards for multiple different achievements"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        # Award for different achievements
        awarded1 = manager.award_achievement_stars(skill_data, "businessman")
        awarded2 = manager.award_achievement_stars(skill_data, "tycoon")
        awarded3 = manager.award_achievement_stars(skill_data, "millionaire")
        
        assert awarded1 == ACHIEVEMENT_STARS
        assert awarded2 == ACHIEVEMENT_STARS
        assert awarded3 == ACHIEVEMENT_STARS
        assert skill_data.star_balance == ACHIEVEMENT_STARS * 3
        assert len(skill_data.milestones_claimed) == 3


class TestMilestoneAwards:
    """Tests for milestone awards (Requirements 1.4, 1.5)"""
    
    def test_award_million_earned_milestone(self):
        """Test that 5 stars are awarded for earning 1M"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        awarded = manager.check_milestone_stars(
            skill_data, 
            cumulative_earnings=1000000
        )
        
        assert awarded == MILLION_EARNED_STARS
        assert skill_data.star_balance == MILLION_EARNED_STARS
        assert "milestone_million_earned" in skill_data.milestones_claimed
    
    def test_no_award_before_million(self):
        """Test that no stars are awarded before reaching 1M"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        awarded = manager.check_milestone_stars(
            skill_data, 
            cumulative_earnings=999999
        )
        
        assert awarded == 0
        assert skill_data.star_balance == 0
    
    def test_no_duplicate_million_earned_award(self):
        """Test that million earned stars are not awarded twice"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        # First award
        awarded1 = manager.check_milestone_stars(
            skill_data, 
            cumulative_earnings=1000000
        )
        assert awarded1 == MILLION_EARNED_STARS
        
        # Try to award again
        awarded2 = manager.check_milestone_stars(
            skill_data, 
            cumulative_earnings=2000000
        )
        assert awarded2 == 0
        assert skill_data.star_balance == MILLION_EARNED_STARS
    
    def test_award_survival_100_days_milestone(self):
        """Test that 10 stars are awarded for surviving 100 days"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        awarded = manager.check_milestone_stars(
            skill_data, 
            days_survived=100
        )
        
        assert awarded == SURVIVAL_100_DAYS_STARS
        assert skill_data.star_balance == SURVIVAL_100_DAYS_STARS
        assert "milestone_survival_100" in skill_data.milestones_claimed
    
    def test_no_award_before_100_days(self):
        """Test that no stars are awarded before 100 days"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        awarded = manager.check_milestone_stars(
            skill_data, 
            days_survived=99
        )
        
        assert awarded == 0
        assert skill_data.star_balance == 0
    
    def test_no_duplicate_survival_100_award(self):
        """Test that survival 100 stars are not awarded twice"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        # First award
        awarded1 = manager.check_milestone_stars(
            skill_data, 
            days_survived=100
        )
        assert awarded1 == SURVIVAL_100_DAYS_STARS
        
        # Try to award again
        awarded2 = manager.check_milestone_stars(
            skill_data, 
            days_survived=200
        )
        assert awarded2 == 0
        assert skill_data.star_balance == SURVIVAL_100_DAYS_STARS
    
    def test_both_milestones_simultaneously(self):
        """Test awarding both milestones at once"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        awarded = manager.check_milestone_stars(
            skill_data,
            cumulative_earnings=1000000,
            days_survived=100
        )
        
        expected = MILLION_EARNED_STARS + SURVIVAL_100_DAYS_STARS
        assert awarded == expected
        assert skill_data.star_balance == expected
        assert len(skill_data.milestones_claimed) == 2


class TestStarSourceTracking:
    """Tests for star source tracking (Requirements 10.1, 10.4)"""
    
    def test_track_star_source_basic(self):
        """Test basic star source tracking"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        manager.track_star_source(skill_data, "Monthly Salary", 3)
        
        assert len(skill_data.star_history) == 1
        assert skill_data.star_history[0]['source'] == "Monthly Salary"
        assert skill_data.star_history[0]['amount'] == 3
        assert 'timestamp' in skill_data.star_history[0]
    
    def test_track_multiple_sources(self):
        """Test tracking multiple star sources"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        manager.track_star_source(skill_data, "Monthly Salary", 3)
        manager.track_star_source(skill_data, "Wealth Tier", 5)
        manager.track_star_source(skill_data, "Achievement", 3)
        
        assert len(skill_data.star_history) == 3
        assert skill_data.star_history[0]['source'] == "Monthly Salary"
        assert skill_data.star_history[1]['source'] == "Wealth Tier"
        assert skill_data.star_history[2]['source'] == "Achievement"
    
    def test_track_star_source_with_custom_timestamp(self):
        """Test tracking with custom timestamp"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        custom_time = "2024-01-15T10:30:00"
        manager.track_star_source(skill_data, "Test Source", 5, custom_time)
        
        assert skill_data.star_history[0]['timestamp'] == custom_time
    
    def test_history_limited_to_10_events(self):
        """Test that history is limited to last 10 events"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        # Add 15 events
        for i in range(15):
            manager.track_star_source(skill_data, f"Source {i}", 1)
        
        # Should only keep last 10
        assert len(skill_data.star_history) == 10
        assert skill_data.star_history[0]['source'] == "Source 5"
        assert skill_data.star_history[-1]['source'] == "Source 14"
    
    def test_award_and_track_combined(self):
        """Test combined award and track operation"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        awarded = manager.award_and_track(skill_data, "Special Event", 5)
        
        assert awarded == 5
        assert skill_data.star_balance == 5
        assert len(skill_data.star_history) == 1
        assert skill_data.star_history[0]['source'] == "Special Event"
        assert skill_data.star_history[0]['amount'] == 5
    
    def test_award_and_track_zero_amount(self):
        """Test that zero amount awards nothing"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        awarded = manager.award_and_track(skill_data, "Invalid", 0)
        
        assert awarded == 0
        assert skill_data.star_balance == 0
        assert len(skill_data.star_history) == 0
    
    def test_award_and_track_negative_amount(self):
        """Test that negative amount awards nothing"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        awarded = manager.award_and_track(skill_data, "Invalid", -5)
        
        assert awarded == 0
        assert skill_data.star_balance == 0
        assert len(skill_data.star_history) == 0


class TestRoutineActionExclusion:
    """Tests for routine action exclusion (Requirement 1.6)"""
    
    def test_no_stars_for_routine_actions(self):
        """
        Test that routine actions (daily work, side jobs, entertainment)
        do NOT award stars through the star economy system.
        
        This is a design test - the StarEconomyManager should not have
        methods for awarding stars for routine actions.
        """
        manager = StarEconomyManager()
        
        # Verify no methods exist for routine actions
        assert not hasattr(manager, 'award_daily_work_stars')
        assert not hasattr(manager, 'award_side_job_stars')
        assert not hasattr(manager, 'award_entertainment_stars')
    
    def test_only_significant_sources_award_stars(self):
        """Test that only significant sources are implemented"""
        manager = StarEconomyManager()
        
        # Verify only significant award methods exist
        assert hasattr(manager, 'award_monthly_stars')
        assert hasattr(manager, 'award_wealth_tier_stars')
        assert hasattr(manager, 'award_achievement_stars')
        assert hasattr(manager, 'check_milestone_stars')


class TestHelperFunctions:
    """Tests for helper functions"""
    
    def test_format_star_notification_single(self):
        """Test notification formatting for 1 star"""
        result = format_star_notification("Test", 1)
        assert "⭐" in result
        assert "+1" in result
        assert "звезда" in result
        assert "Test" in result
    
    def test_format_star_notification_few(self):
        """Test notification formatting for 2-4 stars"""
        result = format_star_notification("Test", 3)
        assert "⭐" in result
        assert "+3" in result
        assert "звезды" in result
        assert "Test" in result
    
    def test_format_star_notification_many(self):
        """Test notification formatting for 5+ stars"""
        result = format_star_notification("Test", 10)
        assert "⭐" in result
        assert "+10" in result
        assert "звезд" in result
        assert "Test" in result
    
    def test_get_wealth_tier_name(self):
        """Test wealth tier name localization"""
        assert get_wealth_tier_name("middle_class") == "Средний класс"
        assert get_wealth_tier_name("wealthy") == "Богатство"
        assert get_wealth_tier_name("unknown") == "unknown"
    
    def test_get_achievement_name(self):
        """Test achievement name localization"""
        assert get_achievement_name("businessman") == "Бизнесмен"
        assert get_achievement_name("tycoon") == "Магнат"
        assert get_achievement_name("unknown") == "unknown"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def test_monthly_award_at_exact_boundary(self):
        """Test monthly award at exactly 30 days"""
        skill_data = SkillData(last_monthly_award_day=0)
        manager = StarEconomyManager()
        
        # Day 29: no award
        awarded29 = manager.award_monthly_stars(skill_data, 29)
        assert awarded29 == 0
        
        # Day 30: award
        awarded30 = manager.award_monthly_stars(skill_data, 30)
        assert awarded30 == MONTHLY_STARS
    
    def test_milestone_at_exact_threshold(self):
        """Test milestone awards at exact thresholds"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        # Just below threshold: no award
        awarded_below = manager.check_milestone_stars(
            skill_data,
            cumulative_earnings=999999,
            days_survived=99
        )
        assert awarded_below == 0
        
        # At threshold: award
        awarded_at = manager.check_milestone_stars(
            skill_data,
            cumulative_earnings=1000000,
            days_survived=100
        )
        assert awarded_at == MILLION_EARNED_STARS + SURVIVAL_100_DAYS_STARS
    
    def test_star_balance_accumulation(self):
        """Test that star balance accumulates correctly"""
        skill_data = SkillData()
        manager = StarEconomyManager()
        
        # Award from different sources
        manager.award_monthly_stars(skill_data, 30)
        manager.award_wealth_tier_stars(skill_data, "middle_class")
        manager.award_achievement_stars(skill_data, "businessman")
        manager.check_milestone_stars(skill_data, cumulative_earnings=1000000)
        
        expected = (MONTHLY_STARS + WEALTH_TIER_STARS + 
                   ACHIEVEMENT_STARS + MILLION_EARNED_STARS)
        assert skill_data.star_balance == expected


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

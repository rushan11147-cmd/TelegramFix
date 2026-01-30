"""
Star Economy Manager - Star Award and Tracking System

Manages the star economy for the Skills Tree System in "Survive Until Payday".
Handles all star award sources, duplicate prevention, and history tracking.

Features:
- Monthly star awards (every 30 days)
- Wealth tier milestone awards
- Achievement completion awards
- One-time milestone awards (1M earned, 100 days survived)
- Star earning history tracking
- Duplicate award prevention

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 10.1, 10.4
"""

from typing import Dict, Optional
from datetime import datetime

from skills_config import (
    MONTHLY_STARS,
    WEALTH_TIER_STARS,
    ACHIEVEMENT_STARS,
    MILLION_EARNED_STARS,
    SURVIVAL_100_DAYS_STARS,
    SkillData
)


class StarEconomyManager:
    """
    Manages star economy and award sources.
    
    Responsibilities:
    - Award monthly stars (every 30 game days)
    - Award wealth tier milestone stars
    - Award achievement completion stars
    - Award one-time milestone stars (1M earned, 100 days)
    - Track star earning history
    - Prevent duplicate awards
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 10.1, 10.4
    """
    
    def award_monthly_stars(self, skill_data: SkillData, current_day: int) -> int:
        """
        Awards monthly stars if eligible (every 30 game days).
        
        This method checks if 30 days have passed since the last monthly award
        and awards 3 stars if eligible. It updates the last_monthly_award_day
        to prevent duplicate awards.
        
        Args:
            skill_data: Player's skill data (modified in place)
            current_day: Current game day
            
        Returns:
            Number of stars awarded (0 if not eligible, 3 if awarded)
            
        Requirements:
        - 1.1: WHEN a new month begins (every 30 game days), 
               THE Star_Source SHALL award 3 stars as monthly salary
               
        Example:
            >>> skill_data = SkillData(last_monthly_award_day=0)
            >>> manager = StarEconomyManager()
            >>> manager.award_monthly_stars(skill_data, 30)
            3
            >>> skill_data.star_balance
            3
            >>> skill_data.last_monthly_award_day
            30
        """
        # Check if 30 days have passed since last award
        days_since_last_award = current_day - skill_data.last_monthly_award_day
        
        if days_since_last_award >= 30:
            # Award stars
            skill_data.star_balance += MONTHLY_STARS
            skill_data.last_monthly_award_day = current_day
            
            return MONTHLY_STARS
        
        return 0
    
    def award_wealth_tier_stars(self, skill_data: SkillData, new_tier: str) -> int:
        """
        Awards stars for reaching a new wealth tier.
        
        This method awards 5 stars when a player reaches a new wealth tier.
        It prevents duplicate awards by tracking claimed tiers in milestones_claimed.
        
        Args:
            skill_data: Player's skill data (modified in place)
            new_tier: New wealth tier reached (e.g., "middle_class", "wealthy")
            
        Returns:
            Number of stars awarded (0 if already claimed, 5 if awarded)
            
        Requirements:
        - 1.2: WHEN a player reaches a new wealth tier, 
               THE Star_Source SHALL award 5 stars as milestone reward
               
        Example:
            >>> skill_data = SkillData()
            >>> manager = StarEconomyManager()
            >>> manager.award_wealth_tier_stars(skill_data, "middle_class")
            5
            >>> manager.award_wealth_tier_stars(skill_data, "middle_class")
            0  # Already claimed
        """
        # Create milestone identifier
        milestone_id = f"wealth_tier_{new_tier}"
        
        # Check if already claimed
        if milestone_id in skill_data.milestones_claimed:
            return 0
        
        # Award stars
        skill_data.star_balance += WEALTH_TIER_STARS
        skill_data.milestones_claimed.append(milestone_id)
        
        return WEALTH_TIER_STARS
    
    def award_achievement_stars(self, skill_data: SkillData, achievement: str) -> int:
        """
        Awards stars for completing a major achievement.
        
        This method awards 3 stars when a player completes a major achievement
        (businessman, tycoon, etc.). It prevents duplicate awards by tracking
        claimed achievements in milestones_claimed.
        
        Args:
            skill_data: Player's skill data (modified in place)
            achievement: Achievement identifier (e.g., "businessman", "tycoon")
            
        Returns:
            Number of stars awarded (0 if already claimed, 3 if awarded)
            
        Requirements:
        - 1.3: WHEN a player completes a major achievement (businessman, tycoon, etc.), 
               THE Star_Source SHALL award 3 stars
               
        Example:
            >>> skill_data = SkillData()
            >>> manager = StarEconomyManager()
            >>> manager.award_achievement_stars(skill_data, "businessman")
            3
            >>> manager.award_achievement_stars(skill_data, "businessman")
            0  # Already claimed
        """
        # Create milestone identifier
        milestone_id = f"achievement_{achievement}"
        
        # Check if already claimed
        if milestone_id in skill_data.milestones_claimed:
            return 0
        
        # Award stars
        skill_data.star_balance += ACHIEVEMENT_STARS
        skill_data.milestones_claimed.append(milestone_id)
        
        return ACHIEVEMENT_STARS
    
    def check_milestone_stars(
        self, 
        skill_data: SkillData, 
        cumulative_earnings: int = 0,
        days_survived: int = 0
    ) -> int:
        """
        Checks and awards milestone stars for one-time achievements.
        
        This method checks two milestones:
        1. Cumulative 1,000,000₽ earned -> 5 stars
        2. 100 game days survived -> 10 stars
        
        Each milestone can only be claimed once.
        
        Args:
            skill_data: Player's skill data (modified in place)
            cumulative_earnings: Total money earned across all time (default 0)
            days_survived: Total game days survived (default 0)
            
        Returns:
            Total number of stars awarded (0, 5, 10, or 15)
            
        Requirements:
        - 1.4: WHEN a player earns cumulative 1,000,000₽ total, 
               THE Star_Source SHALL award 5 stars as one-time reward
        - 1.5: WHEN a player survives 100 game days, 
               THE Star_Source SHALL award 10 stars as survival milestone
               
        Example:
            >>> skill_data = SkillData()
            >>> manager = StarEconomyManager()
            >>> manager.check_milestone_stars(skill_data, cumulative_earnings=1000000)
            5
            >>> manager.check_milestone_stars(skill_data, days_survived=100)
            10
            >>> manager.check_milestone_stars(skill_data, cumulative_earnings=2000000, days_survived=200)
            0  # Both already claimed
        """
        total_awarded = 0
        
        # Check 1M earned milestone
        if cumulative_earnings >= 1000000:
            milestone_id = "milestone_million_earned"
            if milestone_id not in skill_data.milestones_claimed:
                skill_data.star_balance += MILLION_EARNED_STARS
                skill_data.milestones_claimed.append(milestone_id)
                total_awarded += MILLION_EARNED_STARS
        
        # Check 100 days survived milestone
        if days_survived >= 100:
            milestone_id = "milestone_survival_100"
            if milestone_id not in skill_data.milestones_claimed:
                skill_data.star_balance += SURVIVAL_100_DAYS_STARS
                skill_data.milestones_claimed.append(milestone_id)
                total_awarded += SURVIVAL_100_DAYS_STARS
        
        return total_awarded
    
    def track_star_source(
        self, 
        skill_data: SkillData, 
        source: str, 
        amount: int,
        timestamp: Optional[str] = None
    ) -> None:
        """
        Records a star earning event in history.
        
        This method adds a star earning event to the player's history.
        The history is automatically limited to the last 10 events and
        events older than 30 days are cleaned up by the repository.
        
        Args:
            skill_data: Player's skill data (modified in place)
            source: Description of star source (e.g., "Monthly Salary", "Wealth Tier: Middle Class")
            amount: Number of stars earned
            timestamp: ISO format datetime string (default: current time)
            
        Requirements:
        - 10.1: WHEN a player earns stars, THE System SHALL display notification 
                with amount and source
        - 10.4: WHEN viewing star history, THE System SHALL show timestamp, 
                source, and amount for each event
                
        Example:
            >>> skill_data = SkillData()
            >>> manager = StarEconomyManager()
            >>> manager.track_star_source(skill_data, "Monthly Salary", 3)
            >>> len(skill_data.star_history)
            1
            >>> skill_data.star_history[0]['source']
            'Monthly Salary'
        """
        # Use current time if not provided
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        # Create event record
        event = {
            'timestamp': timestamp,
            'source': source,
            'amount': amount
        }
        
        # Add to history
        skill_data.star_history.append(event)
        
        # Keep only last 10 events (repository will also enforce this)
        if len(skill_data.star_history) > 10:
            skill_data.star_history = skill_data.star_history[-10:]
    
    def award_and_track(
        self,
        skill_data: SkillData,
        source: str,
        amount: int,
        timestamp: Optional[str] = None
    ) -> int:
        """
        Awards stars and tracks the source in one operation.
        
        This is a convenience method that combines awarding stars and
        tracking the source. It's useful for custom star awards that
        don't fit the standard categories.
        
        Args:
            skill_data: Player's skill data (modified in place)
            source: Description of star source
            amount: Number of stars to award
            timestamp: ISO format datetime string (default: current time)
            
        Returns:
            Number of stars awarded
            
        Example:
            >>> skill_data = SkillData()
            >>> manager = StarEconomyManager()
            >>> manager.award_and_track(skill_data, "Special Event", 5)
            5
            >>> skill_data.star_balance
            5
        """
        if amount <= 0:
            return 0
        
        # Award stars
        skill_data.star_balance += amount
        
        # Track source
        self.track_star_source(skill_data, source, amount, timestamp)
        
        return amount


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_star_notification(source: str, amount: int) -> str:
    """
    Formats a star earning notification message.
    
    Args:
        source: Description of star source
        amount: Number of stars earned
        
    Returns:
        Formatted notification message
        
    Example:
        >>> format_star_notification("Monthly Salary", 3)
        '⭐ +3 звезд: Monthly Salary'
    """
    star_word = "звезда" if amount == 1 else "звезд" if amount >= 5 else "звезды"
    return f"⭐ +{amount} {star_word}: {source}"


def get_wealth_tier_name(tier: str) -> str:
    """
    Returns a human-readable name for a wealth tier.
    
    Args:
        tier: Wealth tier identifier
        
    Returns:
        Localized tier name
        
    Example:
        >>> get_wealth_tier_name("middle_class")
        'Средний класс'
    """
    tier_names = {
        'poor': 'Бедность',
        'struggling': 'Выживание',
        'stable': 'Стабильность',
        'middle_class': 'Средний класс',
        'comfortable': 'Комфорт',
        'wealthy': 'Богатство',
        'rich': 'Роскошь',
        'very_rich': 'Очень богат',
        'millionaire': 'Миллионер'
    }
    return tier_names.get(tier, tier)


def get_achievement_name(achievement: str) -> str:
    """
    Returns a human-readable name for an achievement.
    
    Args:
        achievement: Achievement identifier
        
    Returns:
        Localized achievement name
        
    Example:
        >>> get_achievement_name("businessman")
        'Бизнесмен'
    """
    achievement_names = {
        'businessman': 'Бизнесмен',
        'tycoon': 'Магнат',
        'entrepreneur': 'Предприниматель',
        'investor': 'Инвестор',
        'millionaire': 'Миллионер',
        'survivor': 'Выживший',
        'lucky': 'Везунчик',
        'social_butterfly': 'Душа компании',
        'genius': 'Гений',
        'iron_man': 'Железный человек'
    }
    return achievement_names.get(achievement, achievement)

# -*- coding: utf-8 -*-
"""
Skills Tree System - Main Orchestrator

Main orchestrator for the Skills Tree System in "Survive Until Payday".
Coordinates all skill-related operations including upgrades, resets,
monthly star awards, and skill tree display.

Features:
- Monthly star processing (every 30 days)
- Skill upgrades with full validation
- Skill reset with 80% refund and cooldown
- Complete skill tree display
- Integration with all game systems

Requirements: 3.1, 3.2, 7.1, 7.2, 7.5
"""

from typing import Dict, Callable, Optional
from copy import deepcopy

from skills_config import (
    SkillData,
    SkillNode,
    SKILL_TREE_CONFIG,
    SKILL_BRANCHES,
    RESET_REFUND_PERCENTAGE,
    RESET_COOLDOWN_DAYS,
    get_skills_by_branch
)
from skills_repository import SkillRepository
from star_economy import StarEconomyManager
from skill_manager import SkillManager


class SkillTreeManager:
    """
    Main orchestrator for the Skills Tree System.
    
    This class coordinates all skill-related operations and serves as the
    primary interface for the game to interact with the skill system.
    
    Responsibilities:
    - Process monthly star awards
    - Handle skill upgrades with validation
    - Manage skill resets with refunds
    - Provide skill tree display data
    - Coordinate between repository, economy, and skill managers
    
    Requirements: 3.1, 3.2, 7.1, 7.2, 7.5
    """
    
    def __init__(self, get_user_func: Callable, save_user_func: Callable):
        """
        Initialize the skill tree manager with database access functions.
        
        Args:
            get_user_func: Function to retrieve user data by user_id
            save_user_func: Function to save user data
            
        Example:
            >>> manager = SkillTreeManager(get_user, save_user)
        """
        self.get_user = get_user_func
        self.save_user = save_user_func
        
        # Initialize component managers
        self.repository = SkillRepository(get_user_func, save_user_func)
        self.star_economy = StarEconomyManager()
        self.skill_manager = SkillManager()
    
    def process_monthly_stars(self, user_id: str, current_day: int) -> Dict:
        """
        Awards monthly stars if eligible (every 30 game days).
        
        This method checks if 30 days have passed since the last monthly award
        and awards 3 stars if eligible. It automatically tracks the award in
        star history and updates the last award day.
        
        Args:
            user_id: Player identifier
            current_day: Current game day
            
        Returns:
            Dictionary with keys:
                - success: bool - Whether stars were awarded
                - stars_awarded: int - Number of stars awarded (0 or 3)
                - new_balance: int - Updated star balance
                - next_award_day: int - Day when next award is available
                - message: str - Human-readable message
                
        Requirements:
        - 1.1: Award 3 stars every 30 game days as monthly salary
        - 10.1: Display notification with amount and source
        
        Example:
            >>> result = manager.process_monthly_stars("user123", 30)
            >>> result['success']
            True
            >>> result['stars_awarded']
            3
        """
        # Load skill data
        skill_data = self.repository.load_skill_data(user_id)
        
        # Check if eligible for monthly stars
        stars_awarded = self.star_economy.award_monthly_stars(skill_data, current_day)
        
        if stars_awarded > 0:
            # Track the award in history
            self.star_economy.track_star_source(
                skill_data,
                "Ежемесячная зарплата",
                stars_awarded
            )
            
            # Save updated data
            self.repository.save_skill_data(user_id, skill_data)
            
            # Calculate next award day
            next_award_day = skill_data.last_monthly_award_day + 30
            
            return {
                'success': True,
                'stars_awarded': stars_awarded,
                'new_balance': skill_data.star_balance,
                'next_award_day': next_award_day,
                'message': f'⭐ Получено {stars_awarded} звезд за месяц работы!'
            }
        else:
            # Not eligible yet
            days_until_next = 30 - (current_day - skill_data.last_monthly_award_day)
            next_award_day = skill_data.last_monthly_award_day + 30
            
            return {
                'success': False,
                'stars_awarded': 0,
                'new_balance': skill_data.star_balance,
                'next_award_day': next_award_day,
                'message': f'Следующая награда через {days_until_next} дней'
            }
    
    def upgrade_skill(self, user_id: str, skill_id: str) -> Dict:
        """
        Upgrades a skill by one level with full validation.
        
        This method performs comprehensive validation before upgrading:
        1. Checks if skill exists
        2. Validates prerequisites are met
        3. Ensures player has sufficient stars
        4. Verifies skill is not at max level
        5. Applies upgrade atomically (both star deduction and level increment)
        
        Args:
            user_id: Player identifier
            skill_id: Skill identifier (e.g., 'luck_1', 'business_1')
            
        Returns:
            Dictionary with keys:
                - success: bool - Whether upgrade succeeded
                - skill_id: str - Skill identifier
                - new_level: int - Updated skill level (if successful)
                - stars_spent: int - Stars deducted (if successful)
                - new_star_balance: int - Updated star balance
                - error: str - Error message (if failed)
                - message: str - Human-readable message
                
        Requirements:
        - 3.1: Allow skill upgrade if sufficient stars and prerequisites met
        - 3.2: Deduct star cost and increment skill level atomically
        - 3.3: Prevent upgrade if insufficient stars
        - 3.4: Prevent upgrade if prerequisites not met
        
        Example:
            >>> result = manager.upgrade_skill("user123", "luck_1")
            >>> result['success']
            True
            >>> result['new_level']
            2
        """
        # Load skill data
        skill_data = self.repository.load_skill_data(user_id)
        
        # Get skill info
        skill = SKILL_TREE_CONFIG.get(skill_id)
        if not skill:
            return {
                'success': False,
                'skill_id': skill_id,
                'new_star_balance': skill_data.star_balance,
                'error': f'Навык "{skill_id}" не существует',
                'message': 'Ошибка: навык не найден'
            }
        
        # Check if can upgrade
        can_upgrade, error_message = self.skill_manager.can_upgrade_skill(skill_data, skill_id)
        
        if not can_upgrade:
            return {
                'success': False,
                'skill_id': skill_id,
                'new_star_balance': skill_data.star_balance,
                'error': error_message,
                'message': f'Невозможно улучшить {skill.name}: {error_message}'
            }
        
        # Get current level and cost
        current_level = skill_data.skills[skill_id]
        cost = self.skill_manager.calculate_skill_cost(skill_id, current_level)
        
        # Apply upgrade atomically
        success = self.skill_manager.apply_skill_upgrade(skill_data, skill_id)
        
        if not success:
            return {
                'success': False,
                'skill_id': skill_id,
                'new_star_balance': skill_data.star_balance,
                'error': 'Не удалось применить улучшение',
                'message': 'Ошибка при улучшении навыка'
            }
        
        # Save updated data
        self.repository.save_skill_data(user_id, skill_data)
        
        # Get new level
        new_level = skill_data.skills[skill_id]
        
        return {
            'success': True,
            'skill_id': skill_id,
            'new_level': new_level,
            'stars_spent': cost,
            'new_star_balance': skill_data.star_balance,
            'message': f'✨ {skill.name} улучшен до уровня {new_level}!'
        }
    
    def reset_skills(self, user_id: str, current_day: int) -> Dict:
        """
        Resets all skills to level 1 and refunds 80% of spent stars.
        
        This method performs a complete skill reset:
        1. Checks if cooldown has expired (7 days since last reset)
        2. Calculates 80% refund of total stars spent
        3. Resets all skills to level 1
        4. Refunds stars to player's balance
        5. Updates last reset day
        6. Clears total stars spent counter
        
        Note: Skill effects must be removed by the calling code when
        integrating with game systems.
        
        Args:
            user_id: Player identifier
            current_day: Current game day
            
        Returns:
            Dictionary with keys:
                - success: bool - Whether reset succeeded
                - stars_refunded: int - Stars returned to player
                - new_star_balance: int - Updated star balance
                - next_reset_day: int - Day when next reset is available
                - error: str - Error message (if failed)
                - message: str - Human-readable message
                
        Requirements:
        - 7.1: Refund 80% of spent stars when resetting
        - 7.2: Reset all skill levels to 1
        - 7.5: Allow reset only once per 7 game days
        
        Example:
            >>> result = manager.reset_skills("user123", 50)
            >>> result['success']
            True
            >>> result['stars_refunded']
            40  # 80% of 50 stars spent
        """
        # Load skill data
        skill_data = self.repository.load_skill_data(user_id)
        
        # Check cooldown
        days_since_last_reset = current_day - skill_data.last_reset_day
        
        if days_since_last_reset < RESET_COOLDOWN_DAYS:
            days_remaining = RESET_COOLDOWN_DAYS - days_since_last_reset
            next_reset_day = skill_data.last_reset_day + RESET_COOLDOWN_DAYS
            
            return {
                'success': False,
                'stars_refunded': 0,
                'new_star_balance': skill_data.star_balance,
                'next_reset_day': next_reset_day,
                'error': f'Сброс навыков доступен через {days_remaining} дней',
                'message': f'⏳ Подождите {days_remaining} дней до следующего сброса'
            }
        
        # Check if there are any skills to reset
        has_upgraded_skills = any(level > 1 for level in skill_data.skills.values())
        
        if not has_upgraded_skills and skill_data.total_stars_spent == 0:
            return {
                'success': False,
                'stars_refunded': 0,
                'new_star_balance': skill_data.star_balance,
                'next_reset_day': current_day + RESET_COOLDOWN_DAYS,
                'error': 'Нет навыков для сброса',
                'message': 'Все навыки уже на базовом уровне'
            }
        
        # Calculate refund (80% of total spent)
        refund_amount = int(skill_data.total_stars_spent * RESET_REFUND_PERCENTAGE)
        
        # Reset all skills to level 1
        for skill_id in skill_data.skills.keys():
            skill_data.skills[skill_id] = 1
        
        # Refund stars
        skill_data.star_balance += refund_amount
        
        # Update reset tracking
        skill_data.last_reset_day = current_day
        skill_data.total_stars_spent = 0
        
        # Track the refund in history
        self.star_economy.track_star_source(
            skill_data,
            "Возврат за сброс навыков",
            refund_amount
        )
        
        # Save updated data
        self.repository.save_skill_data(user_id, skill_data)
        
        next_reset_day = current_day + RESET_COOLDOWN_DAYS
        
        return {
            'success': True,
            'stars_refunded': refund_amount,
            'new_star_balance': skill_data.star_balance,
            'next_reset_day': next_reset_day,
            'message': f'🔄 Навыки сброшены! Возвращено {refund_amount} звезд (80%)'
        }
    
    def get_skill_tree(self, user_id: str, current_day: Optional[int] = None) -> Dict:
        """
        Returns complete skill tree with current state and display information.
        
        This method provides all data needed to display the skill tree UI:
        - Current star balance
        - All skills with their levels, costs, and status
        - Lock status (prerequisites not met)
        - Upgrade availability (can afford and prerequisites met)
        - Completion status (at max level)
        - Reset availability
        
        Args:
            user_id: Player identifier
            current_day: Current game day (optional, for reset cooldown calculation)
            
        Returns:
            Dictionary with keys:
                - star_balance: int - Current stars available
                - skills: Dict[str, Dict] - All skills with detailed info
                - branches: Dict[str, Dict] - Branch metadata
                - total_stars_spent: int - Cumulative stars spent
                - can_reset: bool - Whether reset is available
                - days_until_reset: int - Days until reset cooldown expires
                - star_history: List[Dict] - Recent star earning events
                
        Requirements:
        - 2.2: Show all skills with current levels and costs
        - 2.3: Display locked skills with prerequisites
        - 6.1: Display each skill with name, emoji, level, max level
        - 6.2: Display locked skills with 🔒 and prerequisites
        - 6.3: Highlight available skills with ✨
        - 6.4: Display maxed skills with ✅
        - 6.5: Display star balance prominently
        
        Example:
            >>> tree = manager.get_skill_tree("user123", 50)
            >>> tree['star_balance']
            15
            >>> tree['skills']['luck_1']['current_level']
            3
            >>> tree['skills']['luck_1']['status']
            'available'
        """
        # Load skill data
        skill_data = self.repository.load_skill_data(user_id)
        
        # Build skill information
        skills_info = {}
        
        for skill_id, skill_node in SKILL_TREE_CONFIG.items():
            current_level = skill_data.skills.get(skill_id, 1)
            
            # Calculate cost for next level
            cost = self.skill_manager.calculate_skill_cost(skill_id, current_level)
            
            # Check if can upgrade
            can_upgrade, error_msg = self.skill_manager.can_upgrade_skill(skill_data, skill_id)
            
            # Determine status
            if current_level >= skill_node.max_level:
                status = 'completed'  # ✅
                status_icon = '✅'
            elif not self.skill_manager.validate_prerequisites(skill_data, skill_id):
                status = 'locked'  # 🔒
                status_icon = '🔒'
            elif can_upgrade:
                status = 'available'  # ✨
                status_icon = '✨'
            else:
                status = 'unavailable'  # Not enough stars
                status_icon = '⭐'
            
            # Get skill effects
            effects = self.skill_manager.get_skill_effects(skill_data, skill_id)
            
            # Build skill info
            skills_info[skill_id] = {
                'name': skill_node.name,
                'emoji': skill_node.emoji,
                'branch': skill_node.branch,
                'current_level': current_level,
                'max_level': skill_node.max_level,
                'cost': cost,
                'base_cost': skill_node.base_cost,
                'prerequisites': skill_node.prerequisites,
                'description': skill_node.description,
                'status': status,
                'status_icon': status_icon,
                'can_upgrade': can_upgrade,
                'error_message': error_msg if not can_upgrade else '',
                'effects': effects
            }
        
        # Calculate reset availability
        can_reset = True
        days_until_reset = 0
        
        if current_day is not None:
            days_since_reset = current_day - skill_data.last_reset_day
            if days_since_reset < RESET_COOLDOWN_DAYS:
                can_reset = False
                days_until_reset = RESET_COOLDOWN_DAYS - days_since_reset
        
        # Get star history
        star_history = self.repository.get_star_history(user_id, limit=10)
        
        return {
            'star_balance': skill_data.star_balance,
            'skills': skills_info,
            'branches': SKILL_BRANCHES,
            'total_stars_spent': skill_data.total_stars_spent,
            'can_reset': can_reset,
            'days_until_reset': days_until_reset,
            'star_history': star_history
        }
    
    # ========================================================================
    # ADDITIONAL HELPER METHODS
    # ========================================================================
    
    def award_stars(
        self,
        user_id: str,
        amount: int,
        source: str
    ) -> Dict:
        """
        Awards stars to a player from a custom source.
        
        This is a convenience method for awarding stars from sources
        not covered by the standard economy methods (monthly, wealth tier,
        achievements, milestones).
        
        Args:
            user_id: Player identifier
            amount: Number of stars to award
            source: Description of star source
            
        Returns:
            Dictionary with keys:
                - success: bool - Whether stars were awarded
                - stars_awarded: int - Number of stars awarded
                - new_balance: int - Updated star balance
                - message: str - Human-readable message
                
        Example:
            >>> result = manager.award_stars("user123", 5, "Special Event")
            >>> result['success']
            True
        """
        if amount <= 0:
            return {
                'success': False,
                'stars_awarded': 0,
                'new_balance': 0,
                'message': 'Количество звезд должно быть положительным'
            }
        
        # Load skill data
        skill_data = self.repository.load_skill_data(user_id)
        
        # Award and track
        awarded = self.star_economy.award_and_track(skill_data, source, amount)
        
        # Save updated data
        self.repository.save_skill_data(user_id, skill_data)
        
        return {
            'success': True,
            'stars_awarded': awarded,
            'new_balance': skill_data.star_balance,
            'message': f'⭐ Получено {awarded} звезд: {source}'
        }
    
    def get_skill_bonus(
        self,
        user_id: str,
        skill_id: str
    ) -> float:
        """
        Returns the current bonus percentage for a specific skill.
        
        This method is useful for game systems that need to apply
        skill bonuses to their calculations.
        
        Args:
            user_id: Player identifier
            skill_id: Skill identifier
            
        Returns:
            Bonus percentage as a float (e.g., 0.15 for 15% bonus)
            
        Example:
            >>> bonus = manager.get_skill_bonus("user123", "luck_1")
            >>> bonus
            0.15  # 15% bonus at level 3
        """
        skill_data = self.repository.load_skill_data(user_id)
        effects = self.skill_manager.get_skill_effects(skill_data, skill_id)
        return effects.get('bonus_percentage', 0.0)
    
    def get_branch_skills(
        self,
        user_id: str,
        branch: str
    ) -> Dict:
        """
        Returns all skills in a specific branch with their current state.
        
        Args:
            user_id: Player identifier
            branch: Branch name (luck, charisma, intelligence, endurance, business)
            
        Returns:
            Dictionary with branch info and skills
            
        Example:
            >>> branch_data = manager.get_branch_skills("user123", "luck")
            >>> branch_data['branch_name']
            'Удача'
        """
        # Get full skill tree
        tree = self.get_skill_tree(user_id)
        
        # Filter skills by branch
        branch_skills = {
            skill_id: skill_info
            for skill_id, skill_info in tree['skills'].items()
            if skill_info['branch'] == branch
        }
        
        # Get branch metadata
        branch_info = SKILL_BRANCHES.get(branch, {})
        
        return {
            'branch': branch,
            'branch_name': branch_info.get('name', branch),
            'branch_emoji': branch_info.get('emoji', ''),
            'branch_description': branch_info.get('description', ''),
            'skills': branch_skills,
            'star_balance': tree['star_balance']
        }

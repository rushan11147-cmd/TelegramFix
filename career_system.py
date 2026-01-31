# -*- coding: utf-8 -*-
"""
Career Progression System

Main module for managing career progression, profession selection,
promotions, and career-related calculations.
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
import career_config


@dataclass
class CareerState:
    """Represents the current career state of a player."""
    player_id: int
    profession: str
    career_level: int = 0
    work_actions_completed: int = 0
    total_money_earned: int = 0
    promotion_history: List[Dict] = None
    
    def __post_init__(self):
        if self.promotion_history is None:
            self.promotion_history = []
    
    def to_dict(self):
        """Serialize to dictionary for database storage."""
        return {
            'player_id': self.player_id,
            'profession': self.profession,
            'career_level': self.career_level,
            'work_actions_completed': self.work_actions_completed,
            'total_money_earned': self.total_money_earned,
            'promotion_history': json.dumps(self.promotion_history)
        }
    
    @classmethod
    def from_dict(cls, data):
        """Deserialize from dictionary."""
        promotion_history = data.get('promotion_history', '[]')
        if isinstance(promotion_history, str):
            promotion_history = json.loads(promotion_history)
        
        return cls(
            player_id=data['player_id'],
            profession=data['profession'],
            career_level=data.get('career_level', 0),
            work_actions_completed=data.get('work_actions_completed', 0),
            total_money_earned=data.get('total_money_earned', 0),
            promotion_history=promotion_history
        )
    
    def get_current_level_name(self):
        """Get the display name of current career level."""
        level = career_config.get_profession_level(self.profession, self.career_level)
        return level['name_ru'] if level else 'Неизвестно'
    
    def get_base_salary(self):
        """Get base salary for current level."""
        level = career_config.get_profession_level(self.profession, self.career_level)
        return level['salary'] if level else 0


class CareerManager:
    """
    Manages all career progression operations including profession selection,
    promotion evaluation, and career state management.
    """
    
    def __init__(self, db_connection):
        """
        Initialize the career manager.
        
        Args:
            db_connection: Database connection for persistence
        """
        self.db = db_connection
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Create career_state table if it doesn't exist."""
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS career_state (
                player_id INTEGER PRIMARY KEY,
                profession TEXT NOT NULL,
                career_level INTEGER NOT NULL DEFAULT 0,
                work_actions_completed INTEGER NOT NULL DEFAULT 0,
                total_money_earned INTEGER NOT NULL DEFAULT 0,
                promotion_history TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db.commit()
    
    def select_profession(self, player_id: int, profession: str) -> CareerState:
        """
        Set the player's initial profession.
        
        Args:
            player_id: Unique identifier for the player
            profession: One of the profession IDs from career_config
        
        Returns:
            CareerState object with initial profession settings
        
        Raises:
            ValueError: If profession is not valid
        """
        if profession not in career_config.get_all_professions():
            raise ValueError(f"Invalid profession: {profession}")
        
        # Create new career state
        career_state = CareerState(
            player_id=player_id,
            profession=profession,
            career_level=0,
            work_actions_completed=0,
            total_money_earned=0,
            promotion_history=[]
        )
        
        # Save to database
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO career_state 
            (player_id, profession, career_level, work_actions_completed, 
             total_money_earned, promotion_history, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_id,
            profession,
            0,
            0,
            0,
            json.dumps([]),
            datetime.now().isoformat()
        ))
        self.db.commit()
        
        return career_state
    
    def get_career_state(self, player_id: int) -> Optional[CareerState]:
        """
        Get the current career state for a player.
        
        Args:
            player_id: Unique identifier for the player
        
        Returns:
            CareerState object or None if not found
        """
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT player_id, profession, career_level, work_actions_completed,
                   total_money_earned, promotion_history
            FROM career_state
            WHERE player_id = ?
        ''', (player_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        data = {
            'player_id': row[0],
            'profession': row[1],
            'career_level': row[2],
            'work_actions_completed': row[3],
            'total_money_earned': row[4],
            'promotion_history': row[5]
        }
        
        return CareerState.from_dict(data)
    
    def record_work_action(self, player_id: int, money_earned: int = 0):
        """
        Record that a work action was completed and update metrics.
        
        Args:
            player_id: Unique identifier for the player
            money_earned: Amount of money earned from this work action
        """
        career_state = self.get_career_state(player_id)
        if not career_state:
            return
        
        career_state.work_actions_completed += 1
        career_state.total_money_earned += money_earned
        
        # Save updated state
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE career_state
            SET work_actions_completed = ?,
                total_money_earned = ?,
                updated_at = ?
            WHERE player_id = ?
        ''', (
            career_state.work_actions_completed,
            career_state.total_money_earned,
            datetime.now().isoformat(),
            player_id
        ))
        self.db.commit()
    
    def calculate_work_income(self, player_id: int, player_data: dict) -> int:
        """
        Calculate income for a work action based on career level and bonuses.
        
        Args:
            player_id: Unique identifier for the player
            player_data: Dictionary with player stats (skills, mood, etc.)
        
        Returns:
            Total income amount including base salary and bonuses
        """
        career_state = self.get_career_state(player_id)
        if not career_state:
            return 0
        
        # Get base salary
        base_salary = career_state.get_base_salary()
        
        # Get profession config
        profession = career_config.get_profession(career_state.profession)
        if not profession:
            return base_salary
        
        total_income = base_salary
        
        # Apply profession-specific bonuses
        if 'bonus_skill' in profession:
            # Skill-based bonus (salesperson, it_support)
            skill_name = profession['bonus_skill']
            skill_level = player_data.get('skills', {}).get(skill_name, 1)
            bonus_multiplier = profession.get('bonus_multiplier', 0)
            bonus = int(base_salary * skill_level * bonus_multiplier)
            total_income += bonus
        
        elif 'bonus_stat' in profession:
            # Stat-based bonus (waiter - mood)
            stat_name = profession['bonus_stat']
            stat_value = player_data.get(stat_name, 50)
            bonus_multiplier = profession.get('bonus_multiplier', 0)
            bonus = int(base_salary * stat_value * bonus_multiplier)
            total_income += bonus
        
        return total_income
    
    def get_energy_cost_multiplier(self, player_id: int) -> float:
        """
        Get the energy cost multiplier for the player's career level.
        
        Args:
            player_id: Unique identifier for the player
        
        Returns:
            Multiplier to apply to base energy cost (e.g., 0.95 for 5% reduction)
        """
        career_state = self.get_career_state(player_id)
        if not career_state:
            return 1.0
        
        level = career_config.get_profession_level(
            career_state.profession,
            career_state.career_level
        )
        
        if not level:
            return 1.0
        
        reduction = level.get('energy_cost_reduction', 0)
        return 1.0 - reduction

    
    def get_career_info(self, player_id: int, player_data: dict) -> dict:
        """
        Get comprehensive career information for display.
        
        Args:
            player_id: Unique identifier for the player
            player_data: Dictionary with player stats (days_survived, skills, etc.)
        
        Returns:
            Dictionary with career state, progress, and statistics
        """
        career_state = self.get_career_state(player_id)
        if not career_state:
            return {
                'has_profession': False,
                'message': 'Профессия не выбрана'
            }
        
        profession = career_config.get_profession(career_state.profession)
        current_level = career_config.get_profession_level(
            career_state.profession,
            career_state.career_level
        )
        next_level = career_config.get_next_level(
            career_state.profession,
            career_state.career_level
        )
        
        # Check promotion eligibility
        promotion_check = self.check_promotion_eligibility(player_id, player_data)
        
        result = {
            'has_profession': True,
            'profession': career_state.profession,
            'profession_display': profession['name_ru'],
            'profession_emoji': profession['emoji'],
            'current_level': {
                'id': current_level['id'],
                'name': current_level['name'],
                'name_ru': current_level['name_ru'],
                'salary': current_level['salary']
            },
            'next_level': None,
            'at_max_level': next_level is None,
            'promotion_eligible': promotion_check['eligible'],
            'requirements': promotion_check.get('requirements', {}),
            'statistics': {
                'total_promotions': len(career_state.promotion_history),
                'work_actions_completed': career_state.work_actions_completed,
                'total_money_earned': career_state.total_money_earned
            }
        }
        
        if next_level:
            result['next_level'] = {
                'id': next_level['id'],
                'name': next_level['name'],
                'name_ru': next_level['name_ru'],
                'salary': next_level['salary']
            }
        
        return result
    
    def check_promotion_eligibility(self, player_id: int, player_data: dict) -> dict:
        """
        Check if player is eligible for promotion.
        
        Args:
            player_id: Unique identifier for the player
            player_data: Dictionary with player stats (days_survived, skills, etc.)
        
        Returns:
            Dictionary with:
                - eligible: bool
                - requirements: dict of requirement -> {current, required, met, progress}
        """
        career_state = self.get_career_state(player_id)
        if not career_state:
            return {'eligible': False, 'message': 'No career state'}
        
        next_level = career_config.get_next_level(
            career_state.profession,
            career_state.career_level
        )
        
        if not next_level:
            return {
                'eligible': False,
                'at_max_level': True,
                'message': 'Максимальный уровень достигнут'
            }
        
        requirements = next_level['requirements']
        result = {
            'eligible': True,
            'requirements': {}
        }
        
        # Check work actions
        work_req = requirements.get('work_actions', 0)
        work_current = career_state.work_actions_completed
        work_met = work_current >= work_req
        result['requirements']['work_actions'] = {
            'current': work_current,
            'required': work_req,
            'met': work_met,
            'progress': min(1.0, work_current / work_req) if work_req > 0 else 1.0
        }
        if not work_met:
            result['eligible'] = False
        
        # Check skills
        skill_reqs = requirements.get('skills', {})
        player_skills = player_data.get('skills', {})
        skills_met = True
        skills_progress = []
        
        for skill_name, required_level in skill_reqs.items():
            current_level = player_skills.get(skill_name, 1)
            met = current_level >= required_level
            if not met:
                skills_met = False
                result['eligible'] = False
            skills_progress.append(min(1.0, current_level / required_level) if required_level > 0 else 1.0)
        
        avg_progress = sum(skills_progress) / len(skills_progress) if skills_progress else 1.0
        result['requirements']['skills'] = {
            'current': player_skills,
            'required': skill_reqs,
            'met': skills_met,
            'progress': avg_progress
        }
        
        # Check money earned
        money_req = requirements.get('money_earned', 0)
        money_current = career_state.total_money_earned
        money_met = money_current >= money_req
        result['requirements']['money_earned'] = {
            'current': money_current,
            'required': money_req,
            'met': money_met,
            'progress': min(1.0, money_current / money_req) if money_req > 0 else 1.0
        }
        if not money_met:
            result['eligible'] = False
        
        # Check days survived
        days_req = requirements.get('days_survived', 0)
        days_current = player_data.get('days_survived', 0)
        days_met = days_current >= days_req
        result['requirements']['days_survived'] = {
            'current': days_current,
            'required': days_req,
            'met': days_met,
            'progress': min(1.0, days_current / days_req) if days_req > 0 else 1.0
        }
        if not days_met:
            result['eligible'] = False
        
        return result
    
    def promote_player(self, player_id: int, player_data: dict) -> CareerState:
        """
        Promote player to next career level.
        
        Args:
            player_id: Unique identifier for the player
            player_data: Dictionary with player stats
        
        Returns:
            Updated CareerState object
        
        Raises:
            ValueError: If player is not eligible for promotion
        """
        # Check eligibility
        eligibility = self.check_promotion_eligibility(player_id, player_data)
        if not eligibility['eligible']:
            raise ValueError('Player is not eligible for promotion')
        
        career_state = self.get_career_state(player_id)
        if not career_state:
            raise ValueError('No career state found')
        
        # Record promotion in history
        promotion_record = {
            'from_level': career_state.career_level,
            'to_level': career_state.career_level + 1,
            'timestamp': datetime.now().isoformat(),
            'work_actions_at_promotion': career_state.work_actions_completed,
            'money_earned_at_promotion': career_state.total_money_earned
        }
        career_state.promotion_history.append(promotion_record)
        
        # Promote to next level
        career_state.career_level += 1
        
        # Save to database
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE career_state
            SET career_level = ?,
                promotion_history = ?,
                updated_at = ?
            WHERE player_id = ?
        ''', (
            career_state.career_level,
            json.dumps(career_state.promotion_history),
            datetime.now().isoformat(),
            player_id
        ))
        self.db.commit()
        
        return career_state

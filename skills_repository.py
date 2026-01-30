"""
Skills Repository - Data Persistence Layer

Handles loading, saving, and validation of skill data for the
"Survive Until Payday" game. Provides data integrity guarantees
and automatic repair of corrupted data.

Features:
- Load skill data with automatic initialization
- Save skill data with validation
- Star earning history tracking
- Corrupted data repair
- Backward compatibility
"""

import json
from typing import Dict, List, Callable, Optional
from datetime import datetime

from skills_config import (
    SkillData,
    SKILL_TREE_CONFIG,
    initialize_default_skills,
    validate_skill_level,
    validate_star_balance
)


class SkillRepository:
    """
    Handles skill data persistence with validation and repair.
    
    Responsibilities:
    - Load skill data from database
    - Initialize defaults for new players
    - Validate and repair corrupted data
    - Save skill data atomically
    - Track star earning history
    
    Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
    """
    
    def __init__(self, get_user_func: Callable, save_user_func: Callable):
        """
        Initialize repository with database access functions.
        
        Args:
            get_user_func: Function to retrieve user data by user_id
            save_user_func: Function to save user data
        """
        self.get_user = get_user_func
        self.save_user = save_user_func
    
    def load_skill_data(self, user_id: str) -> SkillData:
        """
        Loads skill data for a player, initializing defaults if missing.
        
        This method ensures data integrity by:
        1. Loading existing data from database
        2. Initializing defaults if no data exists
        3. Validating all fields
        4. Repairing corrupted data
        5. Ensuring backward compatibility
        
        Args:
            user_id: Player identifier
            
        Returns:
            SkillData object with validated data
            
        Requirements:
        - 9.1: Immediately persist changes to database
        - 9.3: Initialize default skill structure if missing
        - 9.4: Validate skill data integrity and repair corrupted data
        - 9.5: Maintain backward compatibility
        """
        user = self.get_user(user_id)
        
        # Check if skill data exists
        if not user or 'skill_data' not in user:
            # Initialize defaults for new player
            skill_data = self._initialize_defaults()
            
            # Save initialized data
            if user:
                user['skill_data'] = skill_data.to_dict()
                self.save_user(user)
            
            return skill_data
        
        # Load existing data
        raw_data = user['skill_data']
        
        # Validate and repair if needed
        repaired_data = self._validate_and_repair(raw_data)
        
        # If data was repaired, save it back
        if repaired_data != raw_data:
            user['skill_data'] = repaired_data
            self.save_user(user)
        
        # Convert to SkillData object
        return SkillData.from_dict(repaired_data)
    
    def save_skill_data(self, user_id: str, skill_data: SkillData) -> None:
        """
        Saves skill data to database with validation.
        
        This method ensures data integrity by:
        1. Validating all fields before saving
        2. Converting to dictionary format
        3. Atomically updating database
        
        Args:
            user_id: Player identifier
            skill_data: SkillData object to save
            
        Raises:
            ValueError: If skill data validation fails
            
        Requirements:
        - 9.1: Immediately persist changes to database
        - 9.2: Immediately persist star balance to database
        """
        # Validate before saving
        self._validate_skill_data(skill_data)
        
        # Get user and update skill data
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Convert to dictionary and save
        user['skill_data'] = skill_data.to_dict()
        self.save_user(user)
    
    def save_star_history(self, user_id: str, event: Dict) -> None:
        """
        Saves a star earning event to history.
        
        History is limited to the last 10 events and automatically
        cleans up events older than 30 days.
        
        Args:
            user_id: Player identifier
            event: Star earning event with keys:
                - timestamp: ISO format datetime string
                - source: Description of star source
                - amount: Number of stars earned
                
        Requirements:
        - 10.3: Display star earning history for last 10 events
        - 10.4: Show timestamp, source, and amount for each event
        - 10.5: Clear star history older than 30 days automatically
        """
        # Load current skill data
        skill_data = self.load_skill_data(user_id)
        
        # Add timestamp if not present
        if 'timestamp' not in event:
            event['timestamp'] = datetime.now().isoformat()
        
        # Validate event structure
        required_keys = ['timestamp', 'source', 'amount']
        for key in required_keys:
            if key not in event:
                raise ValueError(f"Star history event missing required key: {key}")
        
        # Add event to history
        skill_data.star_history.append(event)
        
        # Clean up old events (older than 30 days)
        skill_data.star_history = self._cleanup_old_history(skill_data.star_history)
        
        # Keep only last 10 events
        if len(skill_data.star_history) > 10:
            skill_data.star_history = skill_data.star_history[-10:]
        
        # Save updated data
        self.save_skill_data(user_id, skill_data)
    
    def get_star_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Retrieves recent star earning history.
        
        Args:
            user_id: Player identifier
            limit: Maximum number of events to return (default 10)
            
        Returns:
            List of star earning events, most recent first
            
        Requirements:
        - 10.3: Display star earning history for last 10 events
        - 10.4: Show timestamp, source, and amount for each event
        """
        skill_data = self.load_skill_data(user_id)
        
        # Return most recent events first
        history = skill_data.star_history[-limit:]
        history.reverse()
        
        return history
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _initialize_defaults(self) -> SkillData:
        """
        Initializes default skill data for a new player.
        
        Returns:
            SkillData with all skills at level 1 and 0 stars
            
        Requirements:
        - 9.3: Initialize default skill structure if missing
        """
        return SkillData(
            star_balance=0,
            skills=initialize_default_skills(),
            total_stars_spent=0,
            last_monthly_award_day=0,
            last_reset_day=-7,  # Allow immediate first reset
            milestones_claimed=[],
            star_history=[]
        )
    
    def _validate_and_repair(self, raw_data: Dict) -> Dict:
        """
        Validates skill data and repairs corruption.
        
        Repairs include:
        - Invalid skill levels (< 1 or > 10) -> clamp to valid range
        - Negative star balance -> set to 0
        - Missing skills -> initialize to level 1
        - Invalid skill IDs -> remove
        - Missing fields -> add with defaults
        
        Args:
            raw_data: Raw skill data dictionary
            
        Returns:
            Repaired skill data dictionary
            
        Requirements:
        - 9.4: Validate skill data integrity and repair corrupted data
        """
        repaired = raw_data.copy()
        
        # Ensure all required fields exist
        if 'star_balance' not in repaired:
            repaired['star_balance'] = 0
        if 'skills' not in repaired:
            repaired['skills'] = {}
        if 'total_stars_spent' not in repaired:
            repaired['total_stars_spent'] = 0
        if 'last_monthly_award_day' not in repaired:
            repaired['last_monthly_award_day'] = 0
        if 'last_reset_day' not in repaired:
            repaired['last_reset_day'] = -7
        if 'milestones_claimed' not in repaired:
            repaired['milestones_claimed'] = []
        if 'star_history' not in repaired:
            repaired['star_history'] = []
        
        # Validate and repair star balance
        if not validate_star_balance(repaired['star_balance']):
            repaired['star_balance'] = 0
        
        # Validate and repair total stars spent
        if repaired['total_stars_spent'] < 0:
            repaired['total_stars_spent'] = 0
        
        # Validate and repair skills
        valid_skills = {}
        for skill_id, level in repaired['skills'].items():
            # Check if skill exists in config
            if skill_id not in SKILL_TREE_CONFIG:
                continue  # Skip invalid skill IDs
            
            # Validate and clamp level
            if not isinstance(level, int):
                level = 1
            elif level < 1:
                level = 1
            elif level > 10:
                level = 10
            
            valid_skills[skill_id] = level
        
        # Add missing skills with level 1
        for skill_id in SKILL_TREE_CONFIG.keys():
            if skill_id not in valid_skills:
                valid_skills[skill_id] = 1
        
        repaired['skills'] = valid_skills
        
        # Validate milestones_claimed is a list
        if not isinstance(repaired['milestones_claimed'], list):
            repaired['milestones_claimed'] = []
        
        # Validate star_history is a list
        if not isinstance(repaired['star_history'], list):
            repaired['star_history'] = []
        
        # Clean up old history
        repaired['star_history'] = self._cleanup_old_history(repaired['star_history'])
        
        # Keep only last 10 events
        if len(repaired['star_history']) > 10:
            repaired['star_history'] = repaired['star_history'][-10:]
        
        return repaired
    
    def _validate_skill_data(self, skill_data: SkillData) -> None:
        """
        Validates skill data before saving.
        
        Args:
            skill_data: SkillData object to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Validate star balance
        if not validate_star_balance(skill_data.star_balance):
            raise ValueError(f"Invalid star balance: {skill_data.star_balance}")
        
        # Validate total stars spent
        if skill_data.total_stars_spent < 0:
            raise ValueError(f"Invalid total stars spent: {skill_data.total_stars_spent}")
        
        # Validate all skill levels
        for skill_id, level in skill_data.skills.items():
            if skill_id not in SKILL_TREE_CONFIG:
                raise ValueError(f"Invalid skill ID: {skill_id}")
            
            if not validate_skill_level(level):
                raise ValueError(f"Invalid level {level} for skill {skill_id}")
    
    def _cleanup_old_history(self, history: List[Dict]) -> List[Dict]:
        """
        Removes star history events older than 30 days.
        
        Args:
            history: List of star earning events
            
        Returns:
            Filtered list with only recent events
            
        Requirements:
        - 10.5: Clear star history older than 30 days automatically
        """
        if not history:
            return []
        
        # Calculate cutoff date (30 days ago)
        now = datetime.now()
        cutoff_days = 30
        
        filtered = []
        for event in history:
            try:
                # Parse timestamp
                event_time = datetime.fromisoformat(event['timestamp'])
                
                # Calculate age in days
                age_days = (now - event_time).days
                
                # Keep if less than 30 days old
                if age_days < cutoff_days:
                    filtered.append(event)
            except (KeyError, ValueError):
                # Skip events with invalid timestamps
                continue
        
        return filtered

# -*- coding: utf-8 -*-
from typing import Dict, Tuple
from skills_config import SkillData, get_skill_by_id, SKILL_EFFECTS

class SkillManager:
    def can_upgrade_skill(self, skill_data: SkillData, skill_id: str) -> Tuple[bool, str]:
        skill = get_skill_by_id(skill_id)
        if not skill:
            return False, f"Навык '{skill_id}' не существует"
        if skill_id not in skill_data.skills:
            return False, f"Навык '{skill_id}' не найден в данных игрока"
        current_level = skill_data.skills[skill_id]
        if current_level >= skill.max_level:
            return False, f"Навык '{skill.name}' уже на максимальном уровне"
        if not self.validate_prerequisites(skill_data, skill_id):
            return False, "Требуются навыки"
        cost = self.calculate_skill_cost(skill_id, current_level)
        if skill_data.star_balance < cost:
            return False, f"Недостаточно звезд. Требуется: {cost}"
        return True, ""
    
    def calculate_skill_cost(self, skill_id: str, current_level: int) -> int:
        skill = get_skill_by_id(skill_id)
        if not skill:
            return 0
        return skill.calculate_cost(current_level)
    
    def apply_skill_upgrade(self, skill_data: SkillData, skill_id: str) -> bool:
        can_upgrade, error = self.can_upgrade_skill(skill_data, skill_id)
        if not can_upgrade:
            return False
        current_level = skill_data.skills[skill_id]
        cost = self.calculate_skill_cost(skill_id, current_level)
        skill_data.star_balance -= cost
        skill_data.skills[skill_id] += 1
        skill_data.total_stars_spent += cost
        return True
    
    def get_skill_effects(self, skill_data: SkillData, skill_id: str) -> Dict:
        skill = get_skill_by_id(skill_id)
        if not skill or skill_id not in SKILL_EFFECTS:
            return {'bonus_percentage': 0.0, 'affected_systems': [], 'description': 'Нет эффектов'}
        current_level = skill_data.skills.get(skill_id, 1)
        effect_config = SKILL_EFFECTS[skill_id]
        bonus_per_level = effect_config['bonus_per_level']
        total_bonus = bonus_per_level * current_level
        return {'bonus_percentage': total_bonus, 'affected_systems': [effect_config['system']], 'description': skill.description}
    
    def validate_prerequisites(self, skill_data: SkillData, skill_id: str) -> bool:
        skill = get_skill_by_id(skill_id)
        if not skill:
            return False
        for prereq_id in skill.prerequisites:
            if prereq_id not in skill_data.skills or skill_data.skills[prereq_id] < 1:
                return False
        return True

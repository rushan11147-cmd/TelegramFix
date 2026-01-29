"""
Business Management System for "Survive Until Payday" Game

This module implements the business branch feature, allowing players to create
and manage food service businesses from kiosks to restaurant chains.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import random


# ============================================================================
# ENUMS
# ============================================================================

class BusinessType(Enum):
    """Types of businesses available to players"""
    KIOSK = "kiosk"
    CAFE = "cafe"
    RESTAURANT = "restaurant"
    RESTAURANT_CHAIN = "restaurant_chain"


class EmployeeType(Enum):
    """Types of employees that can be hired"""
    CHEF = "chef"
    CASHIER = "cashier"
    MANAGER = "manager"


class UpgradeType(Enum):
    """Types of upgrades available for businesses"""
    NEW_MENU = "new_menu"
    DELIVERY = "delivery"
    RENOVATION = "renovation"
    ADVERTISING = "advertising"


class EventType(Enum):
    """Types of random events that can affect businesses"""
    HEALTH_INSPECTION = "health_inspection"
    COMPETITOR_OPENS = "competitor_opens"
    VIRAL_POST = "viral_post"
    EQUIPMENT_BREAKDOWN = "equipment_breakdown"


class EventOutcome(Enum):
    """Possible outcomes of business events"""
    FINE = "fine"
    CLOSURE = "closure"
    REVENUE_BOOST = "revenue_boost"
    REVENUE_PENALTY = "revenue_penalty"
    REQUIRES_REPAIR = "requires_repair"


# ============================================================================
# CONFIGURATION DICTIONARIES
# ============================================================================

BUSINESS_CONFIGS = {
    BusinessType.KIOSK: {
        "cost": 50000,
        "base_revenue": 8000,
        "base_rent": 2000,
        "max_employees": 2,
        "name": "Киоск с шаурмой",
        "emoji": "🏪"
    },
    BusinessType.CAFE: {
        "cost": 300000,
        "base_revenue": 40000,
        "base_rent": 10000,
        "max_employees": 4,
        "name": "Кафе",
        "emoji": "☕"
    },
    BusinessType.RESTAURANT: {
        "cost": 1000000,
        "base_revenue": 150000,
        "base_rent": 30000,
        "max_employees": 6,
        "name": "Ресторан",
        "emoji": "🍽️"
    },
    BusinessType.RESTAURANT_CHAIN: {
        "cost": 5000000,
        "base_revenue": 800000,
        "base_rent": 150000,
        "max_employees": 10,
        "name": "Сеть ресторанов",
        "emoji": "🏢"
    }
}

EMPLOYEE_CONFIGS = {
    EmployeeType.CHEF: {
        "daily_salary": 5000,
        "quality_bonus": 0.30,
        "rating_bonus": 0.5,
        "revenue_multiplier": 1.0,
        "name": "Повар",
        "emoji": "👨‍🍳"
    },
    EmployeeType.CASHIER: {
        "daily_salary": 3000,
        "service_speed_bonus": 0.20,
        "rating_bonus": 0.0,
        "revenue_multiplier": 1.0,
        "name": "Кассир",
        "emoji": "💰"
    },
    EmployeeType.MANAGER: {
        "daily_salary": 8000,
        "rating_bonus": 0.0,
        "revenue_multiplier": 1.25,
        "name": "Менеджер",
        "emoji": "👔"
    }
}

UPGRADE_CONFIGS = {
    UpgradeType.NEW_MENU: {
        "cost": 50000,
        "revenue_multiplier": 1.30,
        "rating_bonus": 0.0,
        "is_permanent": True,
        "duration_days": None,
        "name": "Новое меню",
        "emoji": "📋",
        "description": "+30% к доходу"
    },
    UpgradeType.DELIVERY: {
        "cost": 80000,
        "revenue_multiplier": 1.50,
        "rating_bonus": 0.0,
        "is_permanent": True,
        "duration_days": None,
        "name": "Доставка",
        "emoji": "🚚",
        "description": "+50% к доходу"
    },
    UpgradeType.RENOVATION: {
        "cost": 100000,
        "revenue_multiplier": 1.0,
        "rating_bonus": 1.0,
        "is_permanent": True,
        "duration_days": None,
        "name": "Ремонт",
        "emoji": "🔨",
        "description": "+1 звезда к рейтингу"
    },
    UpgradeType.ADVERTISING: {
        "cost": 30000,
        "revenue_multiplier": 1.20,
        "rating_bonus": 0.0,
        "is_permanent": False,
        "duration_days": 7,
        "name": "Реклама",
        "emoji": "📢",
        "description": "+20% клиентов на 7 дней"
    }
}

EVENT_CONFIGS = {
    EventType.HEALTH_INSPECTION: {
        "probability": 0.05,
        "name": "Проверка санэпидемстанции",
        "emoji": "🏥",
        "outcomes": [
            {
                "type": EventOutcome.FINE,
                "cost": 50000,
                "rating_penalty": 1.0,
                "weight": 0.7,
                "description": "Штраф 50,000₽"
            },
            {
                "type": EventOutcome.CLOSURE,
                "duration_days": 2,
                "weight": 0.3,
                "description": "Закрытие на 2 дня"
            }
        ]
    },
    EventType.COMPETITOR_OPENS: {
        "probability": 0.03,
        "revenue_multiplier": 0.80,
        "duration_days": 14,
        "name": "Открылся конкурент",
        "emoji": "🏪",
        "description": "-20% дохода на 14 дней"
    },
    EventType.VIRAL_POST: {
        "probability": 0.02,
        "revenue_multiplier": 1.50,
        "duration_days": 3,
        "name": "Вирусный пост в соцсетях",
        "emoji": "📱",
        "description": "+50% дохода на 3 дня"
    },
    EventType.EQUIPMENT_BREAKDOWN: {
        "probability": 0.04,
        "repair_cost": 20000,
        "revenue_multiplier": 0.70,
        "requires_action": True,
        "name": "Поломка оборудования",
        "emoji": "⚙️",
        "description": "Требуется ремонт 20,000₽"
    }
}


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Employee:
    """Represents an employee working in a business"""
    employee_id: str
    employee_type: EmployeeType
    hired_at: datetime
    
    def get_daily_salary(self) -> float:
        """Returns daily salary cost"""
        return EMPLOYEE_CONFIGS[self.employee_type]["daily_salary"]
    
    def get_quality_bonus(self) -> float:
        """Returns quality improvement (0.0 to 1.0)"""
        return EMPLOYEE_CONFIGS[self.employee_type].get("quality_bonus", 0.0)
    
    def get_revenue_multiplier(self) -> float:
        """Returns revenue multiplier (1.0 = no change)"""
        return EMPLOYEE_CONFIGS[self.employee_type].get("revenue_multiplier", 1.0)
    
    def get_rating_bonus(self) -> float:
        """Returns rating bonus from this employee"""
        return EMPLOYEE_CONFIGS[self.employee_type].get("rating_bonus", 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "employee_id": self.employee_id,
            "employee_type": self.employee_type.value,
            "hired_at": self.hired_at.isoformat()
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Employee':
        """Deserialize from dictionary"""
        return Employee(
            employee_id=data["employee_id"],
            employee_type=EmployeeType(data["employee_type"]),
            hired_at=datetime.fromisoformat(data["hired_at"])
        )


@dataclass
class Upgrade:
    """Represents an upgrade purchased for a business"""
    upgrade_type: UpgradeType
    purchased_at: datetime
    expires_at: Optional[datetime] = None
    
    def get_cost(self) -> float:
        """Returns purchase cost"""
        return UPGRADE_CONFIGS[self.upgrade_type]["cost"]
    
    def get_revenue_multiplier(self) -> float:
        """Returns revenue multiplier (1.0 = no change)"""
        return UPGRADE_CONFIGS[self.upgrade_type].get("revenue_multiplier", 1.0)
    
    def get_rating_bonus(self) -> float:
        """Returns rating increase"""
        return UPGRADE_CONFIGS[self.upgrade_type].get("rating_bonus", 0.0)
    
    def is_active(self) -> bool:
        """Returns True if upgrade is currently active"""
        if self.expires_at is None:
            return True  # Permanent upgrade
        return datetime.now() < self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "upgrade_type": self.upgrade_type.value,
            "purchased_at": self.purchased_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Upgrade':
        """Deserialize from dictionary"""
        return Upgrade(
            upgrade_type=UpgradeType(data["upgrade_type"]),
            purchased_at=datetime.fromisoformat(data["purchased_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
        )


@dataclass
class BusinessEvent:
    """Represents a random event affecting a business"""
    event_id: str
    event_type: EventType
    outcome: EventOutcome
    triggered_at: datetime
    expires_at: Optional[datetime] = None
    is_resolved: bool = False
    outcome_data: Dict[str, Any] = field(default_factory=dict)
    
    def get_revenue_multiplier(self) -> float:
        """Returns revenue multiplier while event is active"""
        if self.is_resolved:
            return 1.0
        
        if self.outcome == EventOutcome.CLOSURE:
            return 0.0  # No revenue during closure
        
        if self.outcome == EventOutcome.REVENUE_BOOST:
            config = EVENT_CONFIGS.get(self.event_type, {})
            return config.get("revenue_multiplier", 1.0)
        
        if self.outcome == EventOutcome.REVENUE_PENALTY:
            config = EVENT_CONFIGS.get(self.event_type, {})
            return config.get("revenue_multiplier", 1.0)
        
        if self.outcome == EventOutcome.REQUIRES_REPAIR:
            config = EVENT_CONFIGS.get(self.event_type, {})
            return config.get("revenue_multiplier", 1.0)
        
        return 1.0
    
    def get_immediate_cost(self) -> float:
        """Returns immediate cost (fines, repairs)"""
        if self.outcome == EventOutcome.FINE:
            return self.outcome_data.get("cost", 0)
        return 0.0
    
    def requires_player_action(self) -> bool:
        """Returns True if player must take action to resolve"""
        return self.outcome == EventOutcome.REQUIRES_REPAIR
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "outcome": self.outcome.value,
            "triggered_at": self.triggered_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_resolved": self.is_resolved,
            "outcome_data": self.outcome_data
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BusinessEvent':
        """Deserialize from dictionary"""
        return BusinessEvent(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            outcome=EventOutcome(data["outcome"]),
            triggered_at=datetime.fromisoformat(data["triggered_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            is_resolved=data.get("is_resolved", False),
            outcome_data=data.get("outcome_data", {})
        )


@dataclass
class Business:
    """Represents a player's business"""
    business_id: str
    owner_id: str
    business_type: BusinessType
    created_at: datetime
    inventory_level: float = 100.0  # 0.0 to 100.0
    rating: float = 3.0  # 1.0 to 5.0
    low_inventory_days: int = 0  # Consecutive days with low inventory
    employees: List[Employee] = field(default_factory=list)
    upgrades: List[Upgrade] = field(default_factory=list)
    active_events: List[BusinessEvent] = field(default_factory=list)
    
    def get_max_employees(self) -> int:
        """Returns maximum employee capacity based on business type"""
        return BUSINESS_CONFIGS[self.business_type]["max_employees"]
    
    def get_base_revenue(self) -> float:
        """Returns base daily revenue for business type"""
        return BUSINESS_CONFIGS[self.business_type]["base_revenue"]
    
    def get_base_rent(self) -> float:
        """Returns base daily rent for business type"""
        return BUSINESS_CONFIGS[self.business_type]["base_rent"]
    
    def calculate_total_investment(self) -> float:
        """Returns total amount invested (initial cost + upgrades)"""
        initial_cost = BUSINESS_CONFIGS[self.business_type]["cost"]
        upgrade_costs = sum(upgrade.get_cost() for upgrade in self.upgrades)
        return initial_cost + upgrade_costs
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "business_id": self.business_id,
            "owner_id": self.owner_id,
            "business_type": self.business_type.value,
            "created_at": self.created_at.isoformat(),
            "inventory_level": self.inventory_level,
            "rating": self.rating,
            "low_inventory_days": self.low_inventory_days,
            "employees": [emp.to_dict() for emp in self.employees],
            "upgrades": [upg.to_dict() for upg in self.upgrades],
            "active_events": [evt.to_dict() for evt in self.active_events]
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Business':
        """Deserialize from dictionary"""
        return Business(
            business_id=data["business_id"],
            owner_id=data["owner_id"],
            business_type=BusinessType(data["business_type"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            inventory_level=data.get("inventory_level", 100.0),
            rating=data.get("rating", 3.0),
            low_inventory_days=data.get("low_inventory_days", 0),
            employees=[Employee.from_dict(emp) for emp in data.get("employees", [])],
            upgrades=[Upgrade.from_dict(upg) for upg in data.get("upgrades", [])],
            active_events=[BusinessEvent.from_dict(evt) for evt in data.get("active_events", [])]
        )



# ============================================================================
# RESULT TYPE FOR ERROR HANDLING
# ============================================================================

@dataclass
class Result:
    """Result type for operations that can succeed or fail"""
    success: bool
    data: Any = None
    error: str = None
    
    @staticmethod
    def ok(data: Any = None) -> 'Result':
        """Create a successful result"""
        return Result(success=True, data=data)
    
    @staticmethod
    def fail(error: str) -> 'Result':
        """Create a failed result"""
        return Result(success=False, error=error)


# ============================================================================
# EMPLOYEE MANAGER
# ============================================================================

class EmployeeManager:
    """Manages employee hiring, firing, and effects"""
    
    def hire_employee(self, business: Business, employee_type: EmployeeType) -> Result:
        """
        Hires employee for business.
        Validates capacity, creates employee, updates business.
        """
        # Check capacity
        if len(business.employees) >= business.get_max_employees():
            return Result.fail(
                f"Нельзя нанять больше сотрудников. Максимум: {business.get_max_employees()}"
            )
        
        # Create employee
        employee = Employee(
            employee_id=str(uuid.uuid4()),
            employee_type=employee_type,
            hired_at=datetime.now()
        )
        
        # Add to business
        business.employees.append(employee)
        
        # Apply rating bonus if Chef
        if employee_type == EmployeeType.CHEF:
            business.rating = min(5.0, business.rating + employee.get_rating_bonus())
        
        return Result.ok(employee)
    
    def fire_employee(self, business: Business, employee_id: str) -> Result:
        """
        Fires employee from business.
        Removes employee and their effects.
        """
        # Find employee
        employee = None
        for emp in business.employees:
            if emp.employee_id == employee_id:
                employee = emp
                break
        
        if not employee:
            return Result.fail(f"Сотрудник не найден: {employee_id}")
        
        # Remove rating bonus if Chef
        if employee.employee_type == EmployeeType.CHEF:
            business.rating = max(1.0, business.rating - employee.get_rating_bonus())
        
        # Remove employee
        business.employees.remove(employee)
        
        return Result.ok()
    
    def get_total_daily_salaries(self, business: Business) -> float:
        """Returns sum of all employee salaries for business"""
        return sum(emp.get_daily_salary() for emp in business.employees)
    
    def calculate_employee_effects(self, business: Business) -> Dict[str, float]:
        """
        Calculates combined effects of all employees.
        Returns: revenue_multiplier, quality_bonus, rating_bonus
        """
        revenue_multiplier = 1.0
        quality_bonus = 0.0
        rating_bonus = 0.0
        
        for employee in business.employees:
            # Manager gives revenue multiplier
            if employee.employee_type == EmployeeType.MANAGER:
                revenue_multiplier *= employee.get_revenue_multiplier()
            
            quality_bonus += employee.get_quality_bonus()
            rating_bonus += employee.get_rating_bonus()
        
        return {
            "revenue_multiplier": revenue_multiplier,
            "quality_bonus": quality_bonus,
            "rating_bonus": rating_bonus
        }


# ============================================================================
# INVENTORY MANAGER
# ============================================================================

class InventoryManager:
    """Manages inventory levels and purchases"""
    
    INVENTORY_COST = 5000
    INVENTORY_AMOUNT = 50.0
    LOW_INVENTORY_THRESHOLD = 20.0
    DAILY_CONSUMPTION = 10.0
    LOW_INVENTORY_PENALTY_DAYS = 3
    
    def purchase_inventory(self, business: Business, user_funds: float) -> Result:
        """
        Purchases inventory for business (5,000₽ for 50%).
        Validates funds, deducts cost, increases inventory (capped at 100%).
        """
        if user_funds < self.INVENTORY_COST:
            return Result.fail(
                f"Недостаточно средств. Нужно {self.INVENTORY_COST}₽, есть {user_funds}₽"
            )
        
        # Increase inventory (cap at 100%)
        business.inventory_level = min(100.0, business.inventory_level + self.INVENTORY_AMOUNT)
        
        return Result.ok({"cost": self.INVENTORY_COST})
    
    def decrease_daily_inventory(self, business: Business) -> None:
        """Decreases inventory by 10% for daily consumption"""
        business.inventory_level = max(0.0, business.inventory_level - self.DAILY_CONSUMPTION)
    
    def is_low_inventory(self, business: Business) -> bool:
        """Returns True if inventory < 20%"""
        return business.inventory_level < self.LOW_INVENTORY_THRESHOLD
    
    def get_inventory_penalty(self, business: Business) -> float:
        """Returns revenue multiplier (0.5 if low, 1.0 otherwise)"""
        return 0.5 if self.is_low_inventory(business) else 1.0
    
    def track_low_inventory_days(self, business: Business) -> None:
        """Tracks consecutive days with low inventory"""
        if self.is_low_inventory(business):
            business.low_inventory_days += 1
        else:
            business.low_inventory_days = 0
    
    def apply_rating_penalty_for_low_inventory(self, business: Business) -> None:
        """Decreases rating by 0.5 if low inventory for 3+ days"""
        if business.low_inventory_days >= self.LOW_INVENTORY_PENALTY_DAYS:
            business.rating = max(1.0, business.rating - 0.5)
            business.low_inventory_days = 0  # Reset counter


# ============================================================================
# UPGRADE MANAGER
# ============================================================================

class UpgradeManager:
    """Manages business upgrades"""
    
    def purchase_upgrade(self, business: Business, upgrade_type: UpgradeType, user_funds: float) -> Result:
        """
        Purchases upgrade for business.
        Validates funds, checks for duplicates (permanent upgrades),
        deducts cost, adds upgrade to business.
        """
        config = UPGRADE_CONFIGS[upgrade_type]
        cost = config["cost"]
        
        # Check funds
        if user_funds < cost:
            return Result.fail(
                f"Недостаточно средств. Нужно {cost}₽, есть {user_funds}₽"
            )
        
        # Check for duplicate permanent upgrades
        if config["is_permanent"]:
            for upgrade in business.upgrades:
                if upgrade.upgrade_type == upgrade_type and upgrade.is_active():
                    return Result.fail(f"Улучшение уже куплено: {config['name']}")
        
        # Create upgrade
        purchased_at = datetime.now()
        expires_at = None
        
        if not config["is_permanent"]:
            duration_days = config["duration_days"]
            expires_at = purchased_at + timedelta(days=duration_days)
        
        upgrade = Upgrade(
            upgrade_type=upgrade_type,
            purchased_at=purchased_at,
            expires_at=expires_at
        )
        
        # Add to business
        business.upgrades.append(upgrade)
        
        # Apply rating bonus if Renovation
        if upgrade_type == UpgradeType.RENOVATION:
            business.rating = min(5.0, business.rating + upgrade.get_rating_bonus())
        
        return Result.ok({"upgrade": upgrade, "cost": cost})
    
    def get_active_upgrades(self, business: Business) -> List[Upgrade]:
        """Returns list of currently active upgrades (not expired)"""
        return [upg for upg in business.upgrades if upg.is_active()]
    
    def process_upgrade_expirations(self, business: Business) -> None:
        """Checks and marks expired upgrades as inactive"""
        # Upgrades are checked via is_active() method
        pass
    
    def calculate_upgrade_effects(self, business: Business) -> Dict[str, float]:
        """
        Calculates combined effects of all active upgrades.
        Returns: revenue_multiplier, rating_bonus
        """
        revenue_multiplier = 1.0
        rating_bonus = 0.0
        
        for upgrade in self.get_active_upgrades(business):
            revenue_multiplier *= upgrade.get_revenue_multiplier()
            rating_bonus += upgrade.get_rating_bonus()
        
        return {
            "revenue_multiplier": revenue_multiplier,
            "rating_bonus": rating_bonus
        }


# ============================================================================
# EVENT MANAGER
# ============================================================================

class EventManager:
    """Manages random business events"""
    
    def trigger_random_events(self, business: Business) -> List[BusinessEvent]:
        """
        Randomly triggers business events based on probabilities.
        Returns list of newly triggered events.
        """
        new_events = []
        
        for event_type, config in EVENT_CONFIGS.items():
            probability = config["probability"]
            
            # Roll for event
            if random.random() < probability:
                event = self._create_event(event_type, config)
                business.active_events.append(event)
                new_events.append(event)
        
        return new_events
    
    def _create_event(self, event_type: EventType, config: Dict[str, Any]) -> BusinessEvent:
        """Creates a business event based on type and config"""
        event_id = str(uuid.uuid4())
        triggered_at = datetime.now()
        
        # Health Inspection - choose outcome
        if event_type == EventType.HEALTH_INSPECTION:
            outcomes = config["outcomes"]
            weights = [o["weight"] for o in outcomes]
            chosen_outcome = random.choices(outcomes, weights=weights)[0]
            
            if chosen_outcome["type"] == EventOutcome.FINE:
                return BusinessEvent(
                    event_id=event_id,
                    event_type=event_type,
                    outcome=EventOutcome.FINE,
                    triggered_at=triggered_at,
                    expires_at=triggered_at,  # Immediate
                    outcome_data={"cost": chosen_outcome["cost"], "rating_penalty": chosen_outcome["rating_penalty"]}
                )
            else:  # CLOSURE
                duration = chosen_outcome["duration_days"]
                return BusinessEvent(
                    event_id=event_id,
                    event_type=event_type,
                    outcome=EventOutcome.CLOSURE,
                    triggered_at=triggered_at,
                    expires_at=triggered_at + timedelta(days=duration)
                )
        
        # Competitor Opens
        elif event_type == EventType.COMPETITOR_OPENS:
            duration = config["duration_days"]
            return BusinessEvent(
                event_id=event_id,
                event_type=event_type,
                outcome=EventOutcome.REVENUE_PENALTY,
                triggered_at=triggered_at,
                expires_at=triggered_at + timedelta(days=duration)
            )
        
        # Viral Post
        elif event_type == EventType.VIRAL_POST:
            duration = config["duration_days"]
            return BusinessEvent(
                event_id=event_id,
                event_type=event_type,
                outcome=EventOutcome.REVENUE_BOOST,
                triggered_at=triggered_at,
                expires_at=triggered_at + timedelta(days=duration)
            )
        
        # Equipment Breakdown
        elif event_type == EventType.EQUIPMENT_BREAKDOWN:
            return BusinessEvent(
                event_id=event_id,
                event_type=event_type,
                outcome=EventOutcome.REQUIRES_REPAIR,
                triggered_at=triggered_at,
                outcome_data={"repair_cost": config["repair_cost"]}
            )
    
    def get_active_events(self, business: Business) -> List[BusinessEvent]:
        """Returns list of currently active events"""
        now = datetime.now()
        active = []
        
        for event in business.active_events:
            if event.is_resolved:
                continue
            if event.expires_at and now > event.expires_at:
                continue
            active.append(event)
        
        return active
    
    def process_event_expirations(self, business: Business) -> None:
        """Checks and marks expired events as inactive"""
        now = datetime.now()
        
        for event in business.active_events:
            if event.expires_at and now > event.expires_at and not event.is_resolved:
                event.is_resolved = True
    
    def resolve_event(self, business: Business, event_id: str, action: str, user_funds: float) -> Result:
        """
        Resolves event requiring player action (e.g., pay for repair).
        Validates action, applies effects, marks event as resolved.
        """
        # Find event
        event = None
        for evt in business.active_events:
            if evt.event_id == event_id:
                event = evt
                break
        
        if not event:
            return Result.fail(f"Событие не найдено: {event_id}")
        
        if not event.requires_player_action():
            return Result.fail("Это событие не требует действий игрока")
        
        if event.is_resolved:
            return Result.fail("Событие уже разрешено")
        
        # Handle repair
        if event.outcome == EventOutcome.REQUIRES_REPAIR and action == "repair":
            repair_cost = event.outcome_data.get("repair_cost", 0)
            
            if user_funds < repair_cost:
                return Result.fail(
                    f"Недостаточно средств для ремонта. Нужно {repair_cost}₽, есть {user_funds}₽"
                )
            
            event.is_resolved = True
            return Result.ok({"cost": repair_cost})
        
        return Result.fail("Неизвестное действие")
    
    def calculate_event_effects(self, business: Business) -> Dict[str, Any]:
        """
        Calculates combined effects of all active events.
        Returns: revenue_multiplier, immediate_costs, closure_days
        """
        revenue_multiplier = 1.0
        immediate_costs = 0.0
        closure_days = 0
        
        for event in self.get_active_events(business):
            event_multiplier = event.get_revenue_multiplier()
            revenue_multiplier *= event_multiplier
            
            immediate_costs += event.get_immediate_cost()
        
        return {
            "revenue_multiplier": revenue_multiplier,
            "immediate_costs": immediate_costs,
            "closure_days": closure_days
        }
    
    def apply_event_to_rating(self, business: Business, event: BusinessEvent) -> None:
        """Applies rating changes from events (e.g., health inspection fine)"""
        if event.outcome == EventOutcome.FINE:
            rating_penalty = event.outcome_data.get("rating_penalty", 0)
            business.rating = max(1.0, business.rating - rating_penalty)


# ============================================================================
# REVENUE CALCULATOR
# ============================================================================

class RevenueCalculator:
    """Calculates daily revenue, expenses, and net profit"""
    
    def __init__(self):
        self.employee_manager = EmployeeManager()
        self.upgrade_manager = UpgradeManager()
        self.event_manager = EventManager()
        self.inventory_manager = InventoryManager()
    
    def calculate_daily_revenue(self, business: Business) -> float:
        """
        Calculates total daily revenue for business.
        
        Formula:
        base_revenue = business.get_base_revenue()
        rating_multiplier = business.rating / 3.0
        revenue = base_revenue * rating_multiplier
        
        Apply employee multipliers (Manager: 1.25x)
        Apply upgrade multipliers (New Menu: 1.30x, Delivery: 1.50x, Advertising: 1.20x)
        Apply event multipliers (Viral Post: 1.50x, Competitor: 0.80x, etc.)
        Apply inventory penalty (if < 20%: 0.50x)
        """
        # Base revenue
        base_revenue = business.get_base_revenue()
        
        # Rating multiplier
        rating_multiplier = business.rating / 3.0
        
        revenue = base_revenue * rating_multiplier
        
        # Employee effects
        employee_effects = self.employee_manager.calculate_employee_effects(business)
        revenue *= employee_effects["revenue_multiplier"]
        
        # Upgrade effects
        upgrade_effects = self.upgrade_manager.calculate_upgrade_effects(business)
        revenue *= upgrade_effects["revenue_multiplier"]
        
        # Event effects
        event_effects = self.event_manager.calculate_event_effects(business)
        revenue *= event_effects["revenue_multiplier"]
        
        # Inventory penalty
        inventory_penalty = self.inventory_manager.get_inventory_penalty(business)
        revenue *= inventory_penalty
        
        return revenue
    
    def calculate_daily_expenses(self, business: Business) -> float:
        """
        Calculates total daily expenses for business.
        
        Formula:
        base_rent = business.get_base_rent()
        employee_salaries = sum of all employee salaries
        total_expenses = base_rent + employee_salaries
        """
        base_rent = business.get_base_rent()
        employee_salaries = self.employee_manager.get_total_daily_salaries(business)
        
        return base_rent + employee_salaries
    
    def calculate_net_profit(self, business: Business) -> float:
        """
        Calculates net profit (revenue - expenses).
        Returns positive or negative amount.
        """
        revenue = self.calculate_daily_revenue(business)
        expenses = self.calculate_daily_expenses(business)
        
        return revenue - expenses



# ============================================================================
# BUSINESS REPOSITORY (Data Access Layer)
# ============================================================================

class BusinessRepository:
    """Handles database operations for businesses"""
    
    def __init__(self, get_user_data_func, save_user_data_func):
        """
        Initialize with functions to get/save user data from main game
        
        Args:
            get_user_data_func: Function that takes user_id and returns user data dict
            save_user_data_func: Function that takes user_id and user data dict and saves it
        """
        self.get_user_data = get_user_data_func
        self.save_user_data = save_user_data_func
    
    def save_business(self, business: Business) -> None:
        """Persists business to database"""
        user_data = self.get_user_data(business.owner_id)
        
        if "businesses" not in user_data:
            user_data["businesses"] = []
        
        # Find and update existing business or add new one
        business_dict = business.to_dict()
        found = False
        
        for i, biz in enumerate(user_data["businesses"]):
            if biz["business_id"] == business.business_id:
                user_data["businesses"][i] = business_dict
                found = True
                break
        
        if not found:
            user_data["businesses"].append(business_dict)
        
        self.save_user_data(business.owner_id, user_data)
    
    def load_business(self, business_id: str, user_id: str) -> Optional[Business]:
        """Loads business from database"""
        user_data = self.get_user_data(user_id)
        
        if "businesses" not in user_data:
            return None
        
        for biz_dict in user_data["businesses"]:
            if biz_dict["business_id"] == business_id:
                return Business.from_dict(biz_dict)
        
        return None
    
    def load_user_businesses(self, user_id: str) -> List[Business]:
        """Loads all businesses for user"""
        user_data = self.get_user_data(user_id)
        
        if "businesses" not in user_data:
            return []
        
        return [Business.from_dict(biz) for biz in user_data["businesses"]]
    
    def delete_business(self, business_id: str, user_id: str) -> None:
        """Deletes business from database"""
        user_data = self.get_user_data(user_id)
        
        if "businesses" not in user_data:
            return
        
        user_data["businesses"] = [
            biz for biz in user_data["businesses"]
            if biz["business_id"] != business_id
        ]
        
        self.save_user_data(user_id, user_data)
    
    def update_user_funds(self, user_id: str, amount: float) -> None:
        """Updates user funds (add or subtract)"""
        user_data = self.get_user_data(user_id)
        user_data["money"] = user_data.get("money", 0) + amount
        self.save_user_data(user_id, user_data)
    
    def get_user_funds(self, user_id: str) -> float:
        """Returns current user funds"""
        user_data = self.get_user_data(user_id)
        return user_data.get("money", 0)


# ============================================================================
# BUSINESS MANAGER (Main Orchestrator)
# ============================================================================

@dataclass
class DailyReport:
    """Report of daily business operations"""
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    total_net_profit: float = 0.0
    businesses_processed: int = 0
    new_events: List[BusinessEvent] = field(default_factory=list)
    immediate_costs: float = 0.0


class BusinessManager:
    """Main orchestrator for business operations"""
    
    def __init__(self, repository: BusinessRepository):
        self.repository = repository
        self.employee_manager = EmployeeManager()
        self.inventory_manager = InventoryManager()
        self.upgrade_manager = UpgradeManager()
        self.event_manager = EventManager()
        self.revenue_calculator = RevenueCalculator()
    
    def create_business(self, user_id: str, business_type: BusinessType) -> Result:
        """
        Creates a new business for the user.
        Validates funds, deducts cost, initializes business with defaults.
        """
        cost = BUSINESS_CONFIGS[business_type]["cost"]
        user_funds = self.repository.get_user_funds(user_id)
        
        # Validate funds
        if user_funds < cost:
            return Result.fail(
                f"Недостаточно средств. Нужно {cost}₽, есть {user_funds}₽"
            )
        
        # Create business with defaults
        business = Business(
            business_id=str(uuid.uuid4()),
            owner_id=user_id,
            business_type=business_type,
            created_at=datetime.now(),
            inventory_level=100.0,
            rating=3.0,
            low_inventory_days=0,
            employees=[],
            upgrades=[],
            active_events=[]
        )
        
        # Deduct cost
        self.repository.update_user_funds(user_id, -cost)
        
        # Save business
        self.repository.save_business(business)
        
        return Result.ok(business)
    
    def get_user_businesses(self, user_id: str) -> List[Business]:
        """Returns all businesses owned by user"""
        return self.repository.load_user_businesses(user_id)
    
    def get_business(self, business_id: str, user_id: str) -> Optional[Business]:
        """Returns specific business by ID"""
        return self.repository.load_business(business_id, user_id)
    
    def sell_business(self, business_id: str, user_id: str) -> Result:
        """
        Sells business, returns 50% of total investment.
        Deletes business and returns sale amount.
        """
        business = self.repository.load_business(business_id, user_id)
        
        if not business:
            return Result.fail(f"Бизнес не найден: {business_id}")
        
        # Calculate sale price (50% of total investment)
        total_investment = business.calculate_total_investment()
        sale_price = total_investment * 0.5
        
        # Add funds to user
        self.repository.update_user_funds(user_id, sale_price)
        
        # Delete business
        self.repository.delete_business(business_id, user_id)
        
        return Result.ok({"sale_price": sale_price, "total_investment": total_investment})
    
    def process_daily_operations(self, user_id: str) -> DailyReport:
        """
        Processes all businesses for daily cycle:
        - Decreases inventory
        - Calculates revenue and expenses
        - Applies event effects
        - Updates player funds
        - Triggers new random events
        Returns summary report of all operations.
        """
        report = DailyReport()
        businesses = self.get_user_businesses(user_id)
        
        for business in businesses:
            # Process inventory
            self.inventory_manager.decrease_daily_inventory(business)
            self.inventory_manager.track_low_inventory_days(business)
            self.inventory_manager.apply_rating_penalty_for_low_inventory(business)
            
            # Process event expirations
            self.event_manager.process_event_expirations(business)
            self.upgrade_manager.process_upgrade_expirations(business)
            
            # Calculate revenue and expenses
            daily_revenue = self.revenue_calculator.calculate_daily_revenue(business)
            daily_expenses = self.revenue_calculator.calculate_daily_expenses(business)
            net_profit = daily_revenue - daily_expenses
            
            # Apply immediate event costs (fines)
            event_effects = self.event_manager.calculate_event_effects(business)
            immediate_costs = event_effects["immediate_costs"]
            
            # Apply fines to rating
            for event in business.active_events:
                if event.outcome == EventOutcome.FINE and not event.is_resolved:
                    self.event_manager.apply_event_to_rating(business, event)
                    event.is_resolved = True
            
            # Update funds
            total_change = net_profit - immediate_costs
            self.repository.update_user_funds(user_id, total_change)
            
            # Trigger new random events
            new_events = self.event_manager.trigger_random_events(business)
            
            # Save business
            self.repository.save_business(business)
            
            # Update report
            report.total_revenue += daily_revenue
            report.total_expenses += daily_expenses
            report.total_net_profit += net_profit
            report.immediate_costs += immediate_costs
            report.businesses_processed += 1
            report.new_events.extend(new_events)
        
        # Check achievements
        self._check_achievements(user_id, businesses, report)
        
        return report
    
    def _check_achievements(self, user_id: str, businesses: List[Business], report: DailyReport) -> None:
        """Check and unlock achievements"""
        user_data = self.repository.get_user_data(user_id)
        
        if "completed_goals" not in user_data:
            user_data["completed_goals"] = []
        
        # Businessman achievement (100,000₽ total net profit)
        if report.total_net_profit >= 100000 and "businessman" not in user_data["completed_goals"]:
            user_data["completed_goals"].append("businessman")
            self.repository.save_user_data(user_id, user_data)
        
        # Tycoon achievement (owns Restaurant Chain)
        has_restaurant_chain = any(
            biz.business_type == BusinessType.RESTAURANT_CHAIN
            for biz in businesses
        )
        
        if has_restaurant_chain and "tycoon" not in user_data["completed_goals"]:
            user_data["completed_goals"].append("tycoon")
            self.repository.save_user_data(user_id, user_data)

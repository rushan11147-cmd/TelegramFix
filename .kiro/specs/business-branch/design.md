# Design Document: Business Branch Feature

## Overview

The Business Branch feature adds a business management simulation layer to the "Survive Until Payday" game. Players can create and manage food service businesses ranging from small kiosks to restaurant chains. The system integrates with the existing game economy, providing passive income opportunities balanced by active management requirements.

The design follows a modular architecture with clear separation between business logic, data persistence, and API layers. The system processes daily business operations during the game's day transition, calculating revenue, expenses, and applying event effects.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (JavaScript)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Business List│  │Business Detail│  │ Action Buttons│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│                    Flask Backend (Python)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Business API Routes                      │   │
│  │  /api/business/create, /hire, /upgrade, etc.        │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Business Management System                  │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐       │   │
│  │  │  Business  │ │  Employee  │ │   Event    │       │   │
│  │  │  Manager   │ │  Manager   │ │  Manager   │       │   │
│  │  └────────────┘ └────────────┘ └────────────┘       │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐       │   │
│  │  │  Revenue   │ │  Upgrade   │ │ Inventory  │       │   │
│  │  │ Calculator │ │  Manager   │ │  Manager   │       │   │
│  │  └────────────┘ └────────────┘ └────────────┘       │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Data Access Layer                        │   │
│  │         (Business Repository Pattern)                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Database (SQLite/PostgreSQL)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  user_data.businesses (JSON field)                   │   │
│  │  - business_id, type, employees[], upgrades[],       │   │
│  │    inventory, rating, events[], created_at           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**Business Manager**: Core orchestrator for business operations. Handles creation, deletion, and daily processing of businesses.

**Employee Manager**: Manages hiring, firing, and employee effects on business performance.

**Revenue Calculator**: Computes daily revenue based on business type, rating, employees, upgrades, inventory, and active events.

**Upgrade Manager**: Handles purchase and application of business upgrades.

**Inventory Manager**: Tracks inventory levels, handles purchases, and applies low-inventory penalties.

**Event Manager**: Triggers random events, tracks active events, applies event effects, and handles event expiration.

**Data Access Layer**: Abstracts database operations using repository pattern for clean separation.

## Components and Interfaces

### Business Model

```python
class BusinessType(Enum):
    KIOSK = "kiosk"
    CAFE = "cafe"
    RESTAURANT = "restaurant"
    RESTAURANT_CHAIN = "restaurant_chain"

class Business:
    business_id: str
    owner_id: int
    business_type: BusinessType
    created_at: datetime
    inventory_level: float  # 0.0 to 100.0
    rating: float  # 1.0 to 5.0
    employees: List[Employee]
    upgrades: List[Upgrade]
    active_events: List[BusinessEvent]
    
    def get_max_employees(self) -> int:
        """Returns maximum employee capacity based on business type"""
        
    def get_base_revenue(self) -> float:
        """Returns base daily revenue for business type"""
        
    def get_base_rent(self) -> float:
        """Returns base daily rent for business type"""
        
    def calculate_total_investment(self) -> float:
        """Returns total amount invested (initial cost + upgrades)"""
```

### Employee Model

```python
class EmployeeType(Enum):
    CHEF = "chef"
    CASHIER = "cashier"
    MANAGER = "manager"

class Employee:
    employee_id: str
    employee_type: EmployeeType
    hired_at: datetime
    
    def get_daily_salary(self) -> float:
        """Returns daily salary cost"""
        
    def get_quality_bonus(self) -> float:
        """Returns quality improvement (0.0 to 1.0)"""
        
    def get_revenue_multiplier(self) -> float:
        """Returns revenue multiplier (1.0 = no change)"""
```

### Upgrade Model

```python
class UpgradeType(Enum):
    NEW_MENU = "new_menu"
    DELIVERY = "delivery"
    RENOVATION = "renovation"
    ADVERTISING = "advertising"

class Upgrade:
    upgrade_type: UpgradeType
    purchased_at: datetime
    expires_at: Optional[datetime]  # None for permanent upgrades
    
    def get_cost(self) -> float:
        """Returns purchase cost"""
        
    def get_revenue_multiplier(self) -> float:
        """Returns revenue multiplier (1.0 = no change)"""
        
    def get_rating_bonus(self) -> float:
        """Returns rating increase"""
        
    def is_active(self) -> bool:
        """Returns True if upgrade is currently active"""
```

### Business Event Model

```python
class EventType(Enum):
    HEALTH_INSPECTION = "health_inspection"
    COMPETITOR_OPENS = "competitor_opens"
    VIRAL_POST = "viral_post"
    EQUIPMENT_BREAKDOWN = "equipment_breakdown"

class EventOutcome(Enum):
    FINE = "fine"
    CLOSURE = "closure"
    REVENUE_BOOST = "revenue_boost"
    REVENUE_PENALTY = "revenue_penalty"
    REQUIRES_REPAIR = "requires_repair"

class BusinessEvent:
    event_id: str
    event_type: EventType
    outcome: EventOutcome
    triggered_at: datetime
    expires_at: Optional[datetime]
    is_resolved: bool
    
    def get_revenue_multiplier(self) -> float:
        """Returns revenue multiplier while event is active"""
        
    def get_immediate_cost(self) -> float:
        """Returns immediate cost (fines, repairs)"""
        
    def requires_player_action(self) -> bool:
        """Returns True if player must take action to resolve"""
```

### Business Manager Interface

```python
class BusinessManager:
    def create_business(self, user_id: int, business_type: BusinessType) -> Result[Business]:
        """
        Creates a new business for the user.
        Validates funds, deducts cost, initializes business with defaults.
        Returns Result with Business or error message.
        """
        
    def get_user_businesses(self, user_id: int) -> List[Business]:
        """Returns all businesses owned by user"""
        
    def get_business(self, business_id: str) -> Optional[Business]:
        """Returns specific business by ID"""
        
    def sell_business(self, business_id: str) -> Result[float]:
        """
        Sells business, returns 50% of total investment.
        Deletes business and returns sale amount.
        """
        
    def process_daily_operations(self, user_id: int) -> DailyReport:
        """
        Processes all businesses for daily cycle:
        - Decreases inventory
        - Calculates revenue and expenses
        - Applies event effects
        - Updates player funds
        - Triggers new random events
        Returns summary report of all operations.
        """
```

### Employee Manager Interface

```python
class EmployeeManager:
    def hire_employee(self, business_id: str, employee_type: EmployeeType) -> Result[Employee]:
        """
        Hires employee for business.
        Validates capacity, creates employee, updates business.
        Returns Result with Employee or error message.
        """
        
    def fire_employee(self, business_id: str, employee_id: str) -> Result[None]:
        """
        Fires employee from business.
        Removes employee and their effects.
        """
        
    def get_total_daily_salaries(self, business: Business) -> float:
        """Returns sum of all employee salaries for business"""
        
    def calculate_employee_effects(self, business: Business) -> EmployeeEffects:
        """
        Calculates combined effects of all employees.
        Returns: revenue_multiplier, quality_bonus, rating_bonus
        """
```

### Revenue Calculator Interface

```python
class RevenueCalculator:
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
        
        Returns final daily revenue amount.
        """
        
    def calculate_daily_expenses(self, business: Business) -> float:
        """
        Calculates total daily expenses for business.
        
        Formula:
        base_rent = business.get_base_rent()
        employee_salaries = sum of all employee salaries
        total_expenses = base_rent + employee_salaries
        
        Returns final daily expense amount.
        """
        
    def calculate_net_profit(self, business: Business) -> float:
        """
        Calculates net profit (revenue - expenses).
        Returns positive or negative amount.
        """
```

### Upgrade Manager Interface

```python
class UpgradeManager:
    def purchase_upgrade(self, business_id: str, upgrade_type: UpgradeType) -> Result[Upgrade]:
        """
        Purchases upgrade for business.
        Validates funds, checks for duplicates (permanent upgrades),
        deducts cost, adds upgrade to business.
        Returns Result with Upgrade or error message.
        """
        
    def get_active_upgrades(self, business: Business) -> List[Upgrade]:
        """Returns list of currently active upgrades (not expired)"""
        
    def process_upgrade_expirations(self, business: Business) -> None:
        """Checks and marks expired upgrades as inactive"""
        
    def calculate_upgrade_effects(self, business: Business) -> UpgradeEffects:
        """
        Calculates combined effects of all active upgrades.
        Returns: revenue_multiplier, rating_bonus
        """
```

### Inventory Manager Interface

```python
class InventoryManager:
    def purchase_inventory(self, business_id: str) -> Result[None]:
        """
        Purchases inventory for business (5,000₽ for 50%).
        Validates funds, deducts cost, increases inventory (capped at 100%).
        """
        
    def decrease_daily_inventory(self, business: Business) -> None:
        """Decreases inventory by 10% for daily consumption"""
        
    def is_low_inventory(self, business: Business) -> bool:
        """Returns True if inventory < 20%"""
        
    def get_inventory_penalty(self, business: Business) -> float:
        """Returns revenue multiplier (0.5 if low, 1.0 otherwise)"""
        
    def track_low_inventory_days(self, business: Business) -> int:
        """Returns consecutive days with low inventory"""
        
    def apply_rating_penalty_for_low_inventory(self, business: Business) -> None:
        """Decreases rating by 0.5 if low inventory for 3+ days"""
```

### Event Manager Interface

```python
class EventManager:
    def trigger_random_events(self, business: Business) -> List[BusinessEvent]:
        """
        Randomly triggers business events based on probabilities.
        Returns list of newly triggered events.
        """
        
    def get_active_events(self, business: Business) -> List[BusinessEvent]:
        """Returns list of currently active events"""
        
    def process_event_expirations(self, business: Business) -> None:
        """Checks and marks expired events as inactive"""
        
    def resolve_event(self, business_id: str, event_id: str, action: str) -> Result[None]:
        """
        Resolves event requiring player action (e.g., pay for repair).
        Validates action, applies effects, marks event as resolved.
        """
        
    def calculate_event_effects(self, business: Business) -> EventEffects:
        """
        Calculates combined effects of all active events.
        Returns: revenue_multiplier, immediate_costs, closure_days
        """
        
    def apply_event_to_rating(self, business: Business, event: BusinessEvent) -> None:
        """Applies rating changes from events (e.g., health inspection fine)"""
```

### Business Repository Interface

```python
class BusinessRepository:
    def save_business(self, business: Business) -> None:
        """Persists business to database"""
        
    def load_business(self, business_id: str) -> Optional[Business]:
        """Loads business from database"""
        
    def load_user_businesses(self, user_id: int) -> List[Business]:
        """Loads all businesses for user"""
        
    def delete_business(self, business_id: str) -> None:
        """Deletes business from database"""
        
    def update_user_funds(self, user_id: int, amount: float) -> None:
        """Updates user funds (add or subtract)"""
        
    def get_user_funds(self, user_id: int) -> float:
        """Returns current user funds"""
```

## Data Models

### Database Schema

The business data is stored as a JSON field in the existing `user_data` table:

```python
# user_data table structure
{
    "user_id": int,
    "username": str,
    "funds": float,
    "businesses": [  # New JSON field
        {
            "business_id": str,
            "business_type": str,  # "kiosk", "cafe", "restaurant", "restaurant_chain"
            "created_at": str,  # ISO 8601 datetime
            "inventory_level": float,  # 0.0 to 100.0
            "rating": float,  # 1.0 to 5.0
            "low_inventory_days": int,  # Consecutive days with low inventory
            "employees": [
                {
                    "employee_id": str,
                    "employee_type": str,  # "chef", "cashier", "manager"
                    "hired_at": str  # ISO 8601 datetime
                }
            ],
            "upgrades": [
                {
                    "upgrade_type": str,  # "new_menu", "delivery", "renovation", "advertising"
                    "purchased_at": str,  # ISO 8601 datetime
                    "expires_at": str | null  # ISO 8601 datetime or null for permanent
                }
            ],
            "active_events": [
                {
                    "event_id": str,
                    "event_type": str,  # "health_inspection", "competitor_opens", etc.
                    "outcome": str,  # "fine", "closure", "revenue_boost", etc.
                    "triggered_at": str,  # ISO 8601 datetime
                    "expires_at": str | null,  # ISO 8601 datetime or null
                    "is_resolved": bool
                }
            ]
        }
    ],
    "achievements": [str],  # Includes "businessman", "tycoon"
    # ... other existing fields
}
```

### Business Type Constants

```python
BUSINESS_CONFIGS = {
    BusinessType.KIOSK: {
        "cost": 50000,
        "base_revenue": 8000,
        "base_rent": 2000,
        "max_employees": 2
    },
    BusinessType.CAFE: {
        "cost": 300000,
        "base_revenue": 40000,
        "base_rent": 10000,
        "max_employees": 4
    },
    BusinessType.RESTAURANT: {
        "cost": 1000000,
        "base_revenue": 150000,
        "base_rent": 30000,
        "max_employees": 6
    },
    BusinessType.RESTAURANT_CHAIN: {
        "cost": 5000000,
        "base_revenue": 800000,
        "base_rent": 150000,
        "max_employees": 10
    }
}

EMPLOYEE_CONFIGS = {
    EmployeeType.CHEF: {
        "daily_salary": 5000,
        "quality_bonus": 0.30,
        "rating_bonus": 0.5
    },
    EmployeeType.CASHIER: {
        "daily_salary": 3000,
        "service_speed_bonus": 0.20,
        "rating_bonus": 0.0
    },
    EmployeeType.MANAGER: {
        "daily_salary": 8000,
        "revenue_multiplier": 1.25,
        "rating_bonus": 0.0
    }
}

UPGRADE_CONFIGS = {
    UpgradeType.NEW_MENU: {
        "cost": 50000,
        "revenue_multiplier": 1.30,
        "is_permanent": True
    },
    UpgradeType.DELIVERY: {
        "cost": 80000,
        "revenue_multiplier": 1.50,
        "is_permanent": True
    },
    UpgradeType.RENOVATION: {
        "cost": 100000,
        "rating_bonus": 1.0,
        "is_permanent": True
    },
    UpgradeType.ADVERTISING: {
        "cost": 30000,
        "revenue_multiplier": 1.20,
        "duration_days": 7,
        "is_permanent": False
    }
}

EVENT_CONFIGS = {
    EventType.HEALTH_INSPECTION: {
        "probability": 0.05,  # 5% chance per day
        "outcomes": [
            {"type": EventOutcome.FINE, "cost": 50000, "rating_penalty": 1.0, "weight": 0.7},
            {"type": EventOutcome.CLOSURE, "duration_days": 2, "weight": 0.3}
        ]
    },
    EventType.COMPETITOR_OPENS: {
        "probability": 0.03,  # 3% chance per day
        "revenue_multiplier": 0.80,
        "duration_days": 14
    },
    EventType.VIRAL_POST: {
        "probability": 0.02,  # 2% chance per day
        "revenue_multiplier": 1.50,
        "duration_days": 3
    },
    EventType.EQUIPMENT_BREAKDOWN: {
        "probability": 0.04,  # 4% chance per day
        "repair_cost": 20000,
        "revenue_multiplier": 0.70,
        "requires_action": True
    }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies and consolidations:

**Revenue Calculation Properties (5.7-5.11)**: These test individual multipliers (Manager bonus, upgrade bonuses, event effects, inventory penalty). These can be consolidated into one comprehensive property that tests the complete revenue calculation formula with all factors.

**Expense Calculation Properties (6.1, 6.6)**: Property 6.1 (calculate expenses based on business type and employees) already encompasses 6.6 (add employee salaries to rent). These should be combined into one property.

**Fund Update Properties (7.2, 7.3)**: Both test fund updates for positive and negative profit. These can be combined into one property that tests fund updates for any net profit value.

**Business Sale Properties (9.1, 9.2, 9.3)**: All three test different aspects of the sale operation. Property 9.2 already implies 9.1 (must calculate price to add to funds) and 9.3 (business removal implies data deletion). These can be combined into one comprehensive sale property.

**Data Persistence Properties (11.1, 11.2, 11.3, 11.4)**: Properties 11.3 and 11.4 form a round-trip property (serialize then deserialize). Properties 11.1 and 11.2 test save and load operations. The round-trip property (11.4) subsumes the serialization completeness test (11.3). We can consolidate to: one round-trip property and one immediate persistence property.

**Employee Capacity Properties (2.4, 13.5)**: Both test the same capacity enforcement rule. These are duplicates and should be consolidated.

**Rating Bounds Properties (14.2, 14.3)**: Both test rating changes with bounds (cap at 5, floor at 1). These can be combined into one property that tests rating changes always respect bounds.

**Consolidated Properties**: After reflection, we have approximately 25 unique properties instead of 40+ individual criteria.

### Correctness Properties

Property 1: Business creation with sufficient funds
*For any* business type and player with sufficient funds, creating a business should deduct the correct cost, create the business with default values (100% inventory, 3-star rating, no employees, no upgrades), and return success.
**Validates: Requirements 1.1, 1.7**

Property 2: Business creation with insufficient funds rejected
*For any* business type and player with insufficient funds, attempting to create a business should reject the operation, not modify player funds, not create a business, and return an error.
**Validates: Requirements 1.6**

Property 3: Employee hiring within capacity
*For any* business with available employee capacity and employee type, hiring an employee should add the employee to the business, apply their effects (salary, bonuses), and return success.
**Validates: Requirements 2.1, 2.2, 2.3**

Property 4: Employee hiring beyond capacity rejected
*For any* business at maximum employee capacity, attempting to hire another employee should reject the operation, not modify the business, and return an error.
**Validates: Requirements 2.4, 13.5**

Property 5: Employee firing removes effects
*For any* business with at least one employee, firing an employee should remove the employee from the business, remove their salary from daily expenses, remove their bonuses from calculations, and return success.
**Validates: Requirements 2.5**

Property 6: Daily inventory consumption
*For any* business with any inventory level, processing a day should decrease inventory by exactly 10% of the current level.
**Validates: Requirements 3.1**

Property 7: Inventory purchase increases level
*For any* business and player with at least 5,000₽, purchasing inventory should deduct 5,000₽, increase inventory by 50% (capped at 100%), and return success.
**Validates: Requirements 3.3, 3.4**

Property 8: Inventory purchase with insufficient funds rejected
*For any* business and player with less than 5,000₽, attempting to purchase inventory should reject the operation, not modify funds or inventory, and return an error.
**Validates: Requirements 3.5**

Property 9: Upgrade purchase with sufficient funds
*For any* upgrade type and player with sufficient funds, purchasing an upgrade should deduct the correct cost, add the upgrade to the business, apply its effects, and return success.
**Validates: Requirements 4.1, 4.2, 4.3, 4.4**

Property 10: Upgrade purchase with insufficient funds rejected
*For any* upgrade type and player with insufficient funds, attempting to purchase an upgrade should reject the operation, not modify funds or business, and return an error.
**Validates: Requirements 4.5**

Property 11: Duplicate permanent upgrade rejected
*For any* permanent upgrade already owned by a business, attempting to purchase it again should reject the operation, not modify funds or business, and return an error.
**Validates: Requirements 4.6**

Property 12: Temporary upgrade expiration
*For any* temporary upgrade (e.g., Advertising), after its duration expires, the upgrade's effects should no longer apply to revenue calculations.
**Validates: Requirements 4.7, 8.7**

Property 13: Daily revenue calculation
*For any* business, daily revenue should equal: base_revenue × (rating / 3.0) × employee_multipliers × upgrade_multipliers × event_multipliers × inventory_penalty, where inventory_penalty is 0.5 if inventory < 20%, otherwise 1.0.
**Validates: Requirements 5.1, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 3.2**

Property 14: Daily expenses calculation
*For any* business, daily expenses should equal: base_rent + sum_of_all_employee_salaries.
**Validates: Requirements 6.1, 6.6, 2.6**

Property 15: Net profit calculation and fund update
*For any* business, after processing a day, net profit should equal (daily_revenue - daily_expenses), and player funds should change by exactly the net profit amount (positive or negative).
**Validates: Requirements 7.1, 7.2, 7.3**

Property 16: Low inventory revenue penalty
*For any* business with inventory level below 20%, daily revenue should be reduced by 50% compared to the same business with inventory above 20%.
**Validates: Requirements 3.2**

Property 17: Event probability distribution
*For any* large number of day simulations across multiple businesses, each event type should trigger within its expected probability range (±2% for statistical variance).
**Validates: Requirements 8.1**

Property 18: Business sale calculation
*For any* business, selling it should calculate sale price as 50% of (initial_cost + sum_of_upgrade_costs), add that amount to player funds, permanently delete all business data, and return success.
**Validates: Requirements 9.1, 9.2, 9.3**

Property 19: Daily operations processing
*For any* player with one or more businesses, processing a day should: decrease inventory by 10% for each business, calculate and apply revenue/expenses for each business, process event expirations, trigger new random events, and update player funds with total net profit.
**Validates: Requirements 10.1**

Property 20: Data persistence round-trip
*For any* business with any combination of employees, upgrades, inventory level, rating, and active events, serializing to database then deserializing should produce a business with equivalent state (all fields match).
**Validates: Requirements 11.3, 11.4**

Property 21: Immediate data persistence
*For any* business operation (create, hire, fire, purchase, sell), the database should be updated immediately after the operation completes successfully.
**Validates: Requirements 11.1**

Property 22: Data loading on login
*For any* player with saved businesses, logging in should load all business data from the database and reconstruct all businesses with correct state.
**Validates: Requirements 11.2**

Property 23: API error handling for invalid data
*For any* API endpoint and invalid request data, the endpoint should return HTTP 400 status with a descriptive error message and not modify any data.
**Validates: Requirements 12.9**

Property 24: API authentication enforcement
*For any* API endpoint called without valid authentication, the endpoint should return HTTP 401 status and not process the request.
**Validates: Requirements 12.10**

Property 25: Rating bounds enforcement
*For any* business and any operation that modifies rating (hiring/firing Chef, purchasing Renovation, low inventory penalty, event penalty), the rating should always remain within bounds [1.0, 5.0] inclusive.
**Validates: Requirements 14.2, 14.3, 14.4, 14.5, 14.6**

## Error Handling

### Error Categories

**Insufficient Funds Errors**:
- Business creation: "Insufficient funds. Need {cost}₽, have {current_funds}₽"
- Employee hiring: "Cannot hire employee. Need {salary}₽ for first day"
- Inventory purchase: "Insufficient funds. Need 5,000₽, have {current_funds}₽"
- Upgrade purchase: "Insufficient funds. Need {cost}₽, have {current_funds}₽"
- Event repair: "Cannot pay for repair. Need {cost}₽, have {current_funds}₽"

**Capacity Errors**:
- Employee hiring: "Cannot hire more employees. Maximum capacity: {max_capacity}"
- Duplicate upgrade: "Upgrade already purchased: {upgrade_name}"

**Validation Errors**:
- Invalid business type: "Invalid business type: {type}"
- Invalid employee type: "Invalid employee type: {type}"
- Invalid upgrade type: "Invalid upgrade type: {type}"
- Business not found: "Business not found: {business_id}"
- Employee not found: "Employee not found: {employee_id}"

**Authentication Errors**:
- Unauthenticated: "Authentication required"
- Unauthorized: "You do not own this business"

### Error Handling Strategy

**API Layer**: All endpoints validate input, check authentication, and return appropriate HTTP status codes (400 for validation, 401 for auth, 404 for not found, 500 for server errors).

**Business Logic Layer**: All operations return Result type (success with data or error with message). Operations validate preconditions before modifying state.

**Database Layer**: All database operations wrapped in try-catch blocks. Failed operations rollback transactions and return errors.

**Event Handling**: Events that require player action (e.g., equipment repair) do not automatically resolve. Business continues with penalty until player takes action.

**Fund Depletion**: If player funds go negative due to business losses, businesses continue operating (accumulating debt). Player must sell businesses or wait for payday to recover.

## Testing Strategy

### Dual Testing Approach

The testing strategy employs both unit tests and property-based tests as complementary approaches:

**Unit Tests**: Focus on specific examples, edge cases, and integration points:
- Specific business type creation (Kiosk, Cafe, Restaurant, Restaurant Chain)
- Specific employee type effects (Chef, Cashier, Manager)
- Specific upgrade effects (New Menu, Delivery, Renovation, Advertising)
- Specific event outcomes (Health Inspection fine vs closure, etc.)
- API endpoint responses and error codes
- Achievement unlocking conditions
- Edge cases: inventory at exactly 20%, rating at bounds (1.0, 5.0), capacity limits

**Property-Based Tests**: Verify universal properties across all inputs:
- Business creation with random types and fund amounts
- Employee hiring/firing with random types and business states
- Revenue calculation with random combinations of factors
- Expense calculation with random employee configurations
- Inventory management with random levels and purchases
- Upgrade purchases with random types and business states
- Event triggering and expiration with random timings
- Data persistence round-trips with random business states
- API error handling with random invalid inputs

### Property-Based Testing Configuration

**Library**: Use `hypothesis` for Python (Flask backend)

**Test Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with: `# Feature: business-branch, Property {N}: {property_text}`
- Custom generators for: BusinessType, EmployeeType, UpgradeType, EventType, Business state
- Shrinking enabled to find minimal failing examples

**Example Test Structure**:
```python
from hypothesis import given, strategies as st
import hypothesis.strategies as st

# Feature: business-branch, Property 1: Business creation with sufficient funds
@given(
    business_type=st.sampled_from(BusinessType),
    initial_funds=st.floats(min_value=5_000_000, max_value=10_000_000)
)
def test_business_creation_with_sufficient_funds(business_type, initial_funds):
    # Setup player with initial_funds
    # Create business of business_type
    # Assert: funds decreased by correct cost
    # Assert: business exists with default values
    # Assert: operation returned success
```

### Test Coverage Goals

- 100% coverage of all 25 correctness properties via property-based tests
- 100% coverage of all API endpoints via unit tests
- 100% coverage of all event types and outcomes via unit tests
- Edge case coverage for bounds, limits, and error conditions
- Integration test for complete day processing with multiple businesses

### Testing Execution

**Development**: Run property tests with 100 iterations during development
**CI/CD**: Run property tests with 1000 iterations in continuous integration
**Pre-release**: Run property tests with 10,000 iterations before major releases

This comprehensive testing strategy ensures both specific correctness (unit tests) and general correctness (property tests), providing high confidence in system reliability.

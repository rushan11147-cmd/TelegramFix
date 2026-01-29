# Design Document: Economy Balancing System

## Overview

Система балансировки экономики для игры "Выживи до зарплаты" представляет собой комплексное решение для управления финансовым балансом игрока. Система вводит обязательные ежедневные расходы, корректирует доходы, увеличивает частоту негативных событий и внедряет прогрессивную систему расходов на основе уровня богатства.

Основная цель - превратить достижение зарплаты в реальный вызов, требующий стратегического планирования бюджета и принятия решений.

## Architecture

Система следует модульной архитектуре, аналогичной существующим системам (business_system, side_jobs_system, entertainment_system):

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask Application                        │
│                         (app.py)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   BalanceManager                             │
│              (Main Orchestrator)                             │
└─┬───────────┬───────────┬──────────┬────────────┬──────────┘
  │           │           │          │            │
  ▼           ▼           ▼          ▼            ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│Expense │ │Wealth  │ │Debt    │ │Event   │ │History   │
│Calc    │ │Tier    │ │Tracker │ │Manager │ │Manager   │
└────────┘ └────────┘ └────────┘ └────────┘ └──────────┘
     │          │          │          │            │
     └──────────┴──────────┴──────────┴────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │   Database   │
                  │  (User Data) │
                  └──────────────┘
```

### Key Design Principles

1. **Separation of Concerns**: Каждый компонент отвечает за свою область (расчет расходов, управление долгами, события)
2. **Configuration-Driven**: Все параметры балансировки хранятся в конфигурационном файле
3. **Integration-Friendly**: Система интегрируется с существующими модулями через четкие интерфейсы
4. **Data Persistence**: Вся финансовая история сохраняется для анализа и отображения

## Components and Interfaces

### 1. Configuration Module (balance_config.py)

Централизованное хранилище всех параметров балансировки:

```python
# Daily Expenses
DAILY_EXPENSES = {
    'food': 50,        # Minimum food cost per day
    'transport': 30,   # Minimum transport cost per day
}

# Income Rates (reduced from original)
JOB_INCOME = {
    'delivery': 50,    # Was 80
    'office': 80,      # Was 120
    'freelance': 130,  # Was 200
    'crypto': 180,     # Was 300
}

# Wealth Tiers
WEALTH_TIERS = {
    'poor': {
        'min': 0,
        'max': 3000,
        'multiplier': 1.0
    },
    'middle': {
        'min': 3001,
        'max': 10000,
        'multiplier': 1.5
    },
    'rich': {
        'min': 10001,
        'max': float('inf'),
        'multiplier': 2.0
    }
}

# Negative Events
NEGATIVE_EVENTS = {
    'medical_emergency': {
        'min_cost': 500,
        'max_cost': 1500,
        'name': 'Медицинская помощь',
        'emoji': '🏥'
    },
    'fine': {
        'min_cost': 300,
        'max_cost': 800,
        'name': 'Штраф',
        'emoji': '🚔'
    },
    'equipment_breakdown': {
        'min_cost': 400,
        'max_cost': 1200,
        'name': 'Поломка техники',
        'emoji': '💻'
    },
    'unexpected_bill': {
        'min_cost': 200,
        'max_cost': 600,
        'name': 'Неожиданный счет',
        'emoji': '📄'
    }
}

# Event Probabilities
EVENT_PROBABILITY = {
    'base': 0.25,           # 25% per day
    'debt_3_days': 0.40,    # 40% when in debt 3+ days
}

# Debt Settings
DEBT_SETTINGS = {
    'collector_trigger_days': 7,
    'collector_percentage': 0.20,  # 20% of debt
}
```

### 2. ExpenseCalculator

Отвечает за расчет ежедневных расходов с учетом всех факторов:

```python
class ExpenseCalculator:
    """Calculates daily expenses for player"""
    
    def calculate_daily_expenses(self, user_data: Dict) -> Dict:
        """
        Calculates total daily expenses with breakdown.
        
        Args:
            user_data: Player data including balance, property, wealth tier
            
        Returns:
            {
                'rent': float,
                'food': float,
                'transport': float,
                'base_total': float,
                'tier_multiplier': float,
                'final_total': float
            }
        """
        pass
    
    def calculate_rent(self, user_data: Dict) -> float:
        """
        Calculates daily rent from monthly property rent.
        Formula: monthly_rent / 30
        """
        pass
    
    def get_base_expenses(self) -> Dict:
        """Returns base food and transport costs"""
        pass
```

### 3. WealthTierManager

Управляет классификацией игроков по уровням богатства:

```python
class WealthTierManager:
    """Manages player wealth tier classification"""
    
    def get_wealth_tier(self, balance: float) -> str:
        """
        Determines wealth tier based on current balance.
        
        Args:
            balance: Current player balance
            
        Returns:
            'poor', 'middle', or 'rich'
        """
        pass
    
    def get_expense_multiplier(self, tier: str) -> float:
        """
        Returns expense multiplier for tier.
        
        Args:
            tier: Wealth tier name
            
        Returns:
            Multiplier (1.0, 1.5, or 2.0)
        """
        pass
    
    def check_tier_change(self, user_data: Dict, new_balance: float) -> Optional[str]:
        """
        Checks if player changed wealth tier.
        
        Returns:
            New tier name if changed, None otherwise
        """
        pass
```

### 4. DebtTracker

Отслеживает долги и применяет последствия:

```python
class DebtTracker:
    """Tracks player debt and applies consequences"""
    
    def track_debt(self, user_data: Dict) -> None:
        """
        Updates debt tracking when balance is negative.
        Tracks consecutive days in debt.
        """
        pass
    
    def get_debt_amount(self, balance: float) -> float:
        """Returns absolute debt amount (positive number)"""
        pass
    
    def get_debt_days(self, user_data: Dict) -> int:
        """Returns consecutive days in debt"""
        pass
    
    def should_trigger_collector(self, user_data: Dict) -> bool:
        """Returns True if debt collector event should trigger"""
        pass
    
    def calculate_collector_cost(self, debt_amount: float) -> float:
        """Calculates debt collector cost (20% of debt)"""
        pass
    
    def get_event_probability_modifier(self, debt_days: int) -> float:
        """
        Returns modified event probability based on debt days.
        3+ days: 40%, otherwise: 25%
        """
        pass
```

### 5. NegativeEventManager

Управляет негативными событиями:

```python
class NegativeEventManager:
    """Manages negative random events"""
    
    def should_trigger_event(self, base_probability: float) -> bool:
        """
        Determines if event should trigger based on probability.
        
        Args:
            base_probability: Base probability (0.25 or 0.40)
            
        Returns:
            True if event triggers
        """
        pass
    
    def select_random_event(self) -> Dict:
        """
        Selects random event from pool.
        
        Returns:
            Event configuration with cost range, name, emoji
        """
        pass
    
    def calculate_event_cost(self, event_config: Dict) -> int:
        """
        Calculates random cost within event's range.
        
        Args:
            event_config: Event configuration
            
        Returns:
            Random cost between min_cost and max_cost
        """
        pass
    
    def apply_event(self, user_data: Dict, event: Dict, cost: int) -> None:
        """
        Applies event to player (deducts cost, records history).
        """
        pass
```

### 6. FinancialHistoryManager

Управляет историей финансовых операций:

```python
class FinancialHistoryManager:
    """Manages financial history tracking"""
    
    def record_daily_expenses(self, user_id: str, expense_data: Dict) -> None:
        """Records daily expense breakdown"""
        pass
    
    def record_daily_income(self, user_id: str, income_data: Dict) -> None:
        """Records daily income by source"""
        pass
    
    def record_negative_event(self, user_id: str, event_data: Dict) -> None:
        """Records negative event occurrence"""
        pass
    
    def record_tier_change(self, user_id: str, old_tier: str, new_tier: str) -> None:
        """Records wealth tier change"""
        pass
    
    def get_history(self, user_id: str, days: int = 30) -> Dict:
        """
        Retrieves financial history for last N days.
        
        Returns:
            {
                'expenses': List[Dict],
                'income': List[Dict],
                'events': List[Dict],
                'tier_changes': List[Dict]
            }
        """
        pass
```

### 7. BalanceManager (Main Orchestrator)

Главный координатор всех операций:

```python
class BalanceManager:
    """Main orchestrator for economy balancing system"""
    
    def __init__(self, get_user_func, save_user_func):
        """
        Initialize with database access functions.
        
        Args:
            get_user_func: Function to get user data
            save_user_func: Function to save user data
        """
        self.get_user = get_user_func
        self.save_user = save_user_func
        self.expense_calculator = ExpenseCalculator()
        self.wealth_tier_manager = WealthTierManager()
        self.debt_tracker = DebtTracker()
        self.event_manager = NegativeEventManager()
        self.history_manager = FinancialHistoryManager()
    
    def process_new_day(self, user_id: str) -> Dict:
        """
        Processes all balance operations for new day:
        1. Calculate and deduct daily expenses
        2. Check and update wealth tier
        3. Track debt if balance negative
        4. Trigger negative events
        5. Record history
        
        Returns:
            Summary of operations performed
        """
        pass
    
    def apply_job_income(self, user_id: str, job_type: str) -> Dict:
        """
        Applies reduced job income to player.
        
        Args:
            user_id: Player ID
            job_type: 'delivery', 'office', 'freelance', 'crypto'
            
        Returns:
            Income amount and updated balance
        """
        pass
    
    def get_financial_summary(self, user_id: str) -> Dict:
        """
        Returns current financial status.
        
        Returns:
            {
                'balance': float,
                'wealth_tier': str,
                'debt_amount': float,
                'debt_days': int,
                'last_expenses': Dict,
                'event_probability': float
            }
        """
        pass
```

## Data Models

### User Data Extensions

Система расширяет существующую структуру данных пользователя:

```python
user_data = {
    # Existing fields
    'money': float,
    'property': str,
    'monthly_rent': float,
    
    # New balance system fields
    'balance_data': {
        'wealth_tier': str,              # 'poor', 'middle', 'rich'
        'debt_days': int,                # Consecutive days in debt
        'last_expense_breakdown': {      # Last calculated expenses
            'rent': float,
            'food': float,
            'transport': float,
            'base_total': float,
            'tier_multiplier': float,
            'final_total': float,
            'date': str                  # ISO format
        }
    },
    
    # Financial history (stored in separate collection/table)
    'financial_history': {
        'expenses': [
            {
                'date': str,
                'rent': float,
                'food': float,
                'transport': float,
                'total': float,
                'tier': str
            }
        ],
        'income': [
            {
                'date': str,
                'source': str,           # 'delivery', 'office', etc.
                'amount': float
            }
        ],
        'events': [
            {
                'date': str,
                'event_type': str,
                'cost': int,
                'name': str,
                'emoji': str
            }
        ],
        'tier_changes': [
            {
                'date': str,
                'old_tier': str,
                'new_tier': str,
                'balance': float
            }
        ]
    }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies:
- Properties 2.1-2.4 (specific job income values) can be combined into one property that tests all job types
- Property 2.5 is redundant as it's covered by the combined job income property
- Properties 4.2-4.4 (wealth tier boundaries) are edge cases of property 4.1 and will be handled by the generator
- Properties 4.5-4.7 (multiplier values) can be combined into one property
- Integration properties (8.1-8.7 except 8.5) are covered by other functional properties

### Core Properties

Property 1: Daily expense calculation correctness
*For any* player state with valid property data, calculating daily expenses should produce a breakdown where total equals rent + food + transport, and rent equals monthly_rent / 30, and food >= 50, and transport >= 30
**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 6.1**

Property 2: Negative balance handling
*For any* player state where balance is insufficient for expenses, deducting expenses should result in negative balance and the system should continue to function normally
**Validates: Requirements 1.5, 7.2**

Property 3: Job income rates
*For any* job type in ['delivery', 'office', 'freelance', 'crypto'], the income returned should match the configured reduced rate (50, 80, 130, 180 respectively)
**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

Property 4: Negative event probability
*For any* large number of day simulations (n >= 1000), the frequency of negative events should approach 25% (±5% tolerance) when player is not in debt
**Validates: Requirements 3.1**

Property 5: Event pool membership
*For any* triggered negative event, the event type should be one of ['medical_emergency', 'fine', 'equipment_breakdown', 'unexpected_bill']
**Validates: Requirements 3.2**

Property 6: Event cost deduction
*For any* negative event that triggers, the player's balance should decrease by the event cost immediately
**Validates: Requirements 3.7**

Property 7: Wealth tier classification
*For any* balance value, the wealth tier should be 'poor' if balance <= 3000, 'middle' if 3001 <= balance <= 10000, 'rich' if balance > 10000
**Validates: Requirements 4.1**

Property 8: Expense multiplier application
*For any* player state, the final daily expenses should equal base expenses multiplied by the wealth tier multiplier (1.0, 1.5, or 2.0)
**Validates: Requirements 4.8**

Property 9: Expense to income ratio
*For any* basic job type, the ratio of daily expenses to job income should be between 0.50 and 0.70 for poor tier players
**Validates: Requirements 5.1**

Property 10: Net income calculation
*For any* day with recorded income and expenses, the net income should equal total income minus total expenses
**Validates: Requirements 5.5**

Property 11: Expense breakdown persistence
*For any* calculated daily expenses, all components (rent, food, transport, tier_multiplier) should be stored in the expense record
**Validates: Requirements 6.2**

Property 12: Debt tracking
*For any* player with negative balance, the debt amount should equal the absolute value of the balance, and debt_days should increment each day balance remains negative
**Validates: Requirements 7.1**

Property 13: Debt event probability increase
*For any* player in debt for 3 or more consecutive days, the negative event probability should be 40% instead of 25%
**Validates: Requirements 7.3**

Property 14: Business income preservation
*For any* business income calculation, the amount should not be affected by the job income reduction (business income remains at original rates)
**Validates: Requirements 8.5**

Property 15: Financial history persistence
*For any* financial operation (expense, income, event, tier change), a corresponding record should be created and retrievable from history
**Validates: Requirements 10.1, 10.2, 10.3, 10.4**

Property 16: History retrieval window
*For any* history request with days parameter N, only records from the last N game days should be returned
**Validates: Requirements 10.5**

## Error Handling

### Input Validation

1. **User Data Validation**:
   - Verify user exists before operations
   - Check for required fields (money, property, monthly_rent)
   - Handle missing balance_data gracefully (initialize with defaults)

2. **Configuration Validation**:
   - Validate all config values are positive numbers
   - Ensure wealth tier ranges don't overlap
   - Verify event probabilities are between 0 and 1

### Error Recovery

1. **Database Errors**:
   - Wrap all database operations in try-catch
   - Log errors with context (user_id, operation)
   - Return error result with descriptive message

2. **Calculation Errors**:
   - Handle division by zero (e.g., if monthly_rent is 0)
   - Clamp values to reasonable ranges
   - Use default values if calculation fails

3. **Integration Errors**:
   - If existing system data is missing, use safe defaults
   - Log integration issues for debugging
   - Don't block core functionality

### Error Response Format

```python
{
    'success': False,
    'error': 'Descriptive error message',
    'error_code': 'ERROR_CODE',
    'context': {
        'user_id': str,
        'operation': str
    }
}
```

## Testing Strategy

### Dual Testing Approach

The system will use both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples of expense calculations
- Edge cases (zero balance, maximum debt, tier boundaries)
- Error conditions (missing data, invalid inputs)
- Integration points with existing systems

**Property Tests** focus on:
- Universal properties across all inputs (see Correctness Properties section)
- Comprehensive input coverage through randomization
- Invariants that must hold for all valid states

### Property-Based Testing Configuration

- **Library**: Use `hypothesis` for Python property-based testing
- **Iterations**: Minimum 100 iterations per property test
- **Tagging**: Each property test must reference its design document property
- **Tag Format**: `# Feature: economy-balancing, Property N: [property text]`

### Test Organization

```
tests/
├── unit/
│   ├── test_expense_calculator.py
│   ├── test_wealth_tier_manager.py
│   ├── test_debt_tracker.py
│   ├── test_event_manager.py
│   └── test_balance_manager.py
├── property/
│   ├── test_expense_properties.py
│   ├── test_income_properties.py
│   ├── test_event_properties.py
│   ├── test_tier_properties.py
│   └── test_persistence_properties.py
└── integration/
    ├── test_existing_systems.py
    └── test_daily_cycle.py
```

### Example Property Test

```python
from hypothesis import given, strategies as st
import pytest

# Feature: economy-balancing, Property 1: Daily expense calculation correctness
@given(
    monthly_rent=st.floats(min_value=0, max_value=100000),
    balance=st.floats(min_value=-10000, max_value=1000000)
)
def test_daily_expense_calculation_correctness(monthly_rent, balance):
    """
    For any player state with valid property data, calculating daily 
    expenses should produce a breakdown where total equals 
    rent + food + transport, and rent equals monthly_rent / 30, 
    and food >= 50, and transport >= 30
    """
    user_data = {
        'money': balance,
        'monthly_rent': monthly_rent,
        'property': 'test_property'
    }
    
    calculator = ExpenseCalculator()
    expenses = calculator.calculate_daily_expenses(user_data)
    
    # Check rent calculation
    expected_rent = monthly_rent / 30
    assert abs(expenses['rent'] - expected_rent) < 0.01
    
    # Check minimums
    assert expenses['food'] >= 50
    assert expenses['transport'] >= 30
    
    # Check total
    expected_total = expenses['rent'] + expenses['food'] + expenses['transport']
    assert abs(expenses['base_total'] - expected_total) < 0.01
```

### Integration Testing

Test integration with existing systems:
- Work system (job income application)
- Energy system (energy costs unchanged)
- Property system (rent calculation)
- Business system (income not reduced)
- Side jobs system (income not affected)
- Entertainment system (costs still apply)

### Manual Testing Checklist

- [ ] New day triggers expense deduction
- [ ] Balance can go negative
- [ ] Wealth tier changes when crossing thresholds
- [ ] Negative events trigger at correct frequency
- [ ] Debt collector appears after 7 days
- [ ] Financial history displays correctly
- [ ] All existing features still work

## Integration Points

### With Existing Systems

1. **app.py (Main Application)**:
   - Add BalanceManager initialization
   - Hook into daily cycle processing
   - Add API endpoints for financial summary

2. **Work System**:
   - Modify job income to use new rates
   - Keep energy costs unchanged
   - Apply income through BalanceManager

3. **Property System**:
   - Use monthly_rent for daily rent calculation
   - No changes to property purchase/upgrade

4. **Business System**:
   - Business income bypasses job income reduction
   - Business expenses separate from daily expenses

5. **Side Jobs System**:
   - Side job income not affected by reduction
   - Continues to use original rates

6. **Entertainment System**:
   - Entertainment costs still apply
   - No changes to game mechanics

### API Endpoints

New endpoints to add to app.py:

```python
@app.route('/api/balance/summary')
def get_balance_summary():
    """Returns current financial status"""
    pass

@app.route('/api/balance/history')
def get_financial_history():
    """Returns financial history for last 30 days"""
    pass

@app.route('/api/balance/process_day', methods=['POST'])
def process_daily_balance():
    """Processes daily balance operations (called by daily cycle)"""
    pass
```

### Database Schema Changes

No new tables needed - extends existing user data structure:

```python
# Add to user document/record
user['balance_data'] = {
    'wealth_tier': 'poor',
    'debt_days': 0,
    'last_expense_breakdown': {}
}

user['financial_history'] = {
    'expenses': [],
    'income': [],
    'events': [],
    'tier_changes': []
}
```

## Performance Considerations

1. **Daily Processing**:
   - All calculations are O(1) complexity
   - History limited to 30 days (automatic cleanup)
   - Batch database updates where possible

2. **Memory Usage**:
   - Financial history capped at 30 days per user
   - Old records automatically pruned
   - Minimal memory footprint per user

3. **Database Queries**:
   - Single read/write per user per day
   - History queries indexed by date
   - No complex joins or aggregations

## Future Enhancements

Potential improvements for future iterations:

1. **Dynamic Difficulty**:
   - Adjust parameters based on player success rate
   - Personalized difficulty curves

2. **Seasonal Events**:
   - Holiday expenses (gifts, travel)
   - Seasonal income bonuses

3. **Financial Goals**:
   - Savings targets with rewards
   - Budget challenges

4. **Advanced Analytics**:
   - Spending patterns visualization
   - Income vs expenses charts
   - Wealth progression graphs

5. **Social Features**:
   - Compare financial stats with friends
   - Leaderboards for best budget management

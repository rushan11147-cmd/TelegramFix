# Design Document: Entertainment System

## Overview

The Entertainment System replaces the standalone roulette button with a centralized entertainment menu containing three mini-games: Roulette, Dice, and Crash. The system integrates with the existing game's balance, mood, and luck skill mechanics to provide engaging gambling experiences that affect player state.

### Key Design Decisions

1. **Centralized Menu**: All entertainment games accessible from a single "Развлечения 🎰" button to improve UX and reduce UI clutter
2. **Existing Roulette Integration**: Migrate existing `/api/play_roulette` endpoint to new entertainment system while maintaining backward compatibility
3. **Luck Skill Integration**: Use existing player luck skill to modify game probabilities, making skill progression meaningful
4. **Mood System**: Each game affects mood differently based on outcome magnitude
5. **Statistics Tracking**: Persistent game statistics for player engagement and analytics

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Flask Application                     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Entertainment System Module                │ │
│  │                                                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │ │
│  │  │ Roulette     │  │ Dice Game    │  │ Crash   │ │ │
│  │  │ Game Engine  │  │ Engine       │  │ Engine  │ │ │
│  │  └──────────────┘  └──────────────┘  └─────────┘ │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │      Statistics Manager                      │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │      Balance & Mood Manager                  │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Database Layer                        │ │
│  │  (PostgreSQL/SQLite via existing functions)        │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Player Action** → Frontend sends API request with user_id, game type, bet, and game-specific parameters
2. **Validation** → System validates user_id, balance, bet amount, and parameters
3. **Game Execution** → Appropriate game engine processes the game with luck skill modifiers
4. **State Update** → Balance, mood, and statistics updated atomically
5. **Persistence** → Changes saved to database via existing `save_user_data_safe()`
6. **Response** → JSON response with game result, updated state, and UI feedback

## Components and Interfaces

### 1. Entertainment Manager

**Responsibility**: Orchestrate game execution, validate inputs, manage state updates

```python
class EntertainmentManager:
    def __init__(self, get_user_func, save_user_func):
        self.get_user_data = get_user_func
        self.save_user_data = save_user_func
        self.roulette_engine = RouletteEngine()
        self.dice_engine = DiceEngine()
        self.crash_engine = CrashEngine()
        self.stats_manager = StatisticsManager()
    
    def play_game(self, user_id: str, game_type: str, bet: int, params: dict) -> dict:
        """
        Main entry point for playing any entertainment game
        
        Args:
            user_id: Player identifier
            game_type: 'roulette', 'dice', or 'crash'
            bet: Bet amount in rubles
            params: Game-specific parameters (e.g., dice choice, crash cash_out)
        
        Returns:
            dict with keys: success, result, user_data, message
        """
        pass
    
    def get_statistics(self, user_id: str) -> dict:
        """Get player's entertainment statistics"""
        pass
    
    def _validate_bet(self, user_data: dict, bet: int, min_bet: int, max_bet: int) -> tuple:
        """Validate bet amount against balance and limits"""
        pass
    
    def _update_mood(self, user_data: dict, mood_change: int) -> None:
        """Update mood with clamping to 0-100"""
        pass
    
    def _update_balance(self, user_data: dict, amount: int) -> None:
        """Update balance (positive for wins, negative for losses)"""
        pass
```

### 2. Roulette Engine

**Responsibility**: Execute roulette game logic with three emoji reels

```python
class RouletteEngine:
    EMOJIS = ['🍒', '🍋', '🍊', '🍉', '⭐', '💎', '7️⃣']
    BET_OPTIONS = [100, 500, 1000]
    
    # Probability distribution
    PROBABILITIES = {
        'loss': 0.60,    # 60% - no match
        'x2': 0.25,      # 25% - two matching
        'x5': 0.10,      # 10% - three matching (common)
        'x10': 0.05      # 5% - three matching (rare)
    }
    
    def spin(self, bet: int, luck_level: int) -> dict:
        """
        Execute roulette spin
        
        Args:
            bet: Bet amount (must be in BET_OPTIONS)
            luck_level: Player's luck skill level (1-10)
        
        Returns:
            dict with keys: reels (list of 3 emojis), multiplier, payout, mood_change
        """
        pass
    
    def _generate_reels(self, outcome: str) -> list:
        """Generate three reel results based on outcome"""
        pass
    
    def _determine_outcome(self, luck_level: int) -> str:
        """Determine outcome with luck modifier"""
        pass
```

### 3. Dice Engine

**Responsibility**: Execute dice game with betting on sum ranges

```python
class DiceEngine:
    MIN_BET = 100
    MAX_BET = 1000
    
    CHOICES = {
        'low': {'range': (2, 6), 'payout': 2.5, 'probability': 5/12},      # 5 outcomes: 2,3,4,5,6
        'seven': {'range': (7, 7), 'payout': 6.0, 'probability': 6/36},    # 6 ways to make 7
        'high': {'range': (8, 12), 'payout': 2.5, 'probability': 15/36}    # 15 outcomes: 8-12
    }
    
    LUCK_BONUS_PER_LEVEL = 0.05  # +5% win chance per luck level
    
    def roll(self, bet: int, choice: str, luck_level: int) -> dict:
        """
        Execute dice roll
        
        Args:
            bet: Bet amount (100-1000)
            choice: 'low', 'seven', or 'high'
            luck_level: Player's luck skill level (1-10)
        
        Returns:
            dict with keys: dice1, dice2, sum, won, payout, mood_change
        """
        pass
    
    def _roll_dice(self) -> tuple:
        """Roll two six-sided dice"""
        pass
    
    def _apply_luck_modifier(self, choice: str, dice_sum: int, luck_level: int) -> bool:
        """
        Apply luck skill to potentially change outcome
        
        Luck gives a chance to "nudge" a losing roll into a win
        """
        pass
    
    def _check_win(self, choice: str, dice_sum: int) -> bool:
        """Check if dice sum matches chosen range"""
        pass
```

### 4. Crash Engine

**Responsibility**: Execute crash game with growing multiplier

```python
class CrashEngine:
    MIN_BET = 100
    MAX_BET = 5000
    
    MIN_CRASH = 1.1
    MAX_CRASH = 10.0
    
    MULTIPLIER_INCREMENT = 0.01  # Grows by 0.01 per tick
    TICK_DURATION_MS = 100       # 100ms per tick
    
    def play(self, bet: int, cash_out_multiplier: float, luck_level: int) -> dict:
        """
        Execute crash game
        
        Args:
            bet: Bet amount (100-5000)
            cash_out_multiplier: Multiplier at which player cashed out (or None if crashed)
            luck_level: Player's luck skill level (1-10)
        
        Returns:
            dict with keys: crash_point, cashed_out, multiplier, payout, mood_change
        """
        pass
    
    def _determine_crash_point(self, luck_level: int) -> float:
        """
        Determine crash point with luck modifier
        
        Luck shifts distribution toward higher crash points
        Base: exponential distribution favoring lower values
        Luck: shifts mean upward by 5% per level
        """
        pass
    
    def _calculate_payout(self, bet: int, multiplier: float) -> int:
        """Calculate payout based on cash out multiplier"""
        pass
```

### 5. Statistics Manager

**Responsibility**: Track and calculate game statistics

```python
class StatisticsManager:
    def record_game(self, user_data: dict, game_type: str, bet: int, payout: int, won: bool) -> None:
        """
        Record a game in statistics
        
        Updates user_data['entertainment_stats'] structure:
        {
            'roulette': {'games': 0, 'wins': 0, 'losses': 0, 'total_bet': 0, 'total_won': 0},
            'dice': {...},
            'crash': {...}
        }
        """
        pass
    
    def get_statistics(self, user_data: dict) -> dict:
        """
        Get formatted statistics for all games
        
        Returns:
            dict with per-game stats and totals
        """
        pass
    
    def _calculate_net_profit(self, stats: dict) -> int:
        """Calculate net profit/loss for a game type"""
        pass
```

## Data Models

### User Data Extensions

The entertainment system extends the existing user data structure:

```python
user_data = {
    # ... existing fields ...
    'entertainment_stats': {
        'roulette': {
            'games': 0,
            'wins': 0,
            'losses': 0,
            'total_bet': 0,
            'total_won': 0
        },
        'dice': {
            'games': 0,
            'wins': 0,
            'losses': 0,
            'total_bet': 0,
            'total_won': 0
        },
        'crash': {
            'games': 0,
            'wins': 0,
            'losses': 0,
            'total_bet': 0,
            'total_won': 0
        }
    }
}
```

### API Request/Response Models

**Roulette Request:**
```json
{
    "user_id": "string",
    "bet": 100 | 500 | 1000
}
```

**Roulette Response:**
```json
{
    "success": true,
    "result": {
        "reels": ["🍒", "🍒", "🍒"],
        "multiplier": 5,
        "payout": 500,
        "mood_change": 15
    },
    "user": {
        "money": 1500,
        "mood": 65
    },
    "message": "Выиграл x5! +500₽"
}
```

**Dice Request:**
```json
{
    "user_id": "string",
    "bet": 100-1000,
    "choice": "low" | "seven" | "high"
}
```

**Dice Response:**
```json
{
    "success": true,
    "result": {
        "dice1": 3,
        "dice2": 4,
        "sum": 7,
        "won": true,
        "payout": 600,
        "mood_change": 3
    },
    "user": {
        "money": 1600,
        "mood": 68
    },
    "message": "Выпало 7! Выигрыш x6!"
}
```

**Crash Request:**
```json
{
    "user_id": "string",
    "bet": 100-5000,
    "cash_out_multiplier": 2.5 | null
}
```

**Crash Response:**
```json
{
    "success": true,
    "result": {
        "crash_point": 3.14,
        "cashed_out": true,
        "multiplier": 2.5,
        "payout": 2500,
        "mood_change": 10
    },
    "user": {
        "money": 3500,
        "mood": 78
    },
    "message": "Забрал на x2.5! +2500₽"
}
```

**Statistics Response:**
```json
{
    "success": true,
    "stats": {
        "roulette": {
            "games": 50,
            "wins": 20,
            "losses": 30,
            "total_bet": 25000,
            "total_won": 30000,
            "net_profit": 5000
        },
        "dice": {...},
        "crash": {...},
        "totals": {
            "games": 150,
            "wins": 60,
            "losses": 90,
            "net_profit": -5000
        }
    }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Game Selection Navigation
*For any* game selection from the entertainment menu, the system should open the corresponding game interface in a modal window.
**Validates: Requirements 1.4**

### Property 2: Balance Deduction on Bet
*For any* valid bet in any game, the player's balance should decrease by the bet amount before the game outcome is determined.
**Validates: Requirements 2.4, 7.3**

### Property 3: Roulette Probability Distribution
*For any* large sample of roulette games (n > 1000), the distribution of outcomes should approximate: 60% loss, 25% x2, 10% x5, 5% x10 (within statistical tolerance).
**Validates: Requirements 2.5**

### Property 4: Mood Changes on Game Outcomes
*For any* game outcome across all three games, mood should change according to the specified rules: Roulette (+5 win, -10 loss), Dice (+3 win, -5 loss), Crash (+10 for x5+, -15 loss), and the resulting mood should be clamped to 0-100.
**Validates: Requirements 2.6, 2.7, 3.7, 3.8, 4.7, 4.8, 6.2**

### Property 5: Balance Update Persistence
*For any* game completion, the updated balance should be immediately persisted to the database and reflected in the UI.
**Validates: Requirements 2.8, 7.4, 7.5, 7.6**

### Property 6: Dice Roll Validity
*For any* dice roll, each die should produce a value between 1 and 6 inclusive, and the sum should be between 2 and 12 inclusive.
**Validates: Requirements 3.1**

### Property 7: Dice Bet Validation
*For any* bet amount in the dice game, bets between 100₽ and 1000₽ (inclusive) should be accepted, and bets outside this range should be rejected with an error.
**Validates: Requirements 3.2**

### Property 8: Dice Low Range Payout
*For any* dice game where the player bets on "Низкие" and the sum is between 2-6, the payout should equal bet × 2.5.
**Validates: Requirements 3.4**

### Property 9: Dice Seven Payout
*For any* dice game where the player bets on "Семерка" and the sum is 7, the payout should equal bet × 6.
**Validates: Requirements 3.5**

### Property 10: Dice High Range Payout
*For any* dice game where the player bets on "Высокие" and the sum is between 8-12, the payout should equal bet × 2.5.
**Validates: Requirements 3.6**

### Property 11: Dice Luck Skill Bonus
*For any* dice game, the win probability should increase by 5% per luck skill level compared to base probability.
**Validates: Requirements 3.9**

### Property 12: Crash Bet Validation
*For any* bet amount in the crash game, bets between 100₽ and 5000₽ (inclusive) should be accepted, and bets outside this range should be rejected with an error.
**Validates: Requirements 4.2**

### Property 13: Crash Multiplier Monotonicity
*For any* crash game, the multiplier should increase monotonically from x1.0 until the crash point.
**Validates: Requirements 4.3**

### Property 14: Crash Point Range
*For any* crash game, the crash point should be between x1.1 and x10.0 inclusive.
**Validates: Requirements 4.4**

### Property 15: Crash Cash Out Payout
*For any* crash game where the player cashes out before the crash point, the payout should equal bet × cash_out_multiplier.
**Validates: Requirements 4.5**

### Property 16: Crash Loss on Crash
*For any* crash game where the crash occurs before cash out, the player should lose the bet amount (payout = 0).
**Validates: Requirements 4.6**

### Property 17: Crash Luck Skill Distribution
*For any* large sample of crash games (n > 100) with higher luck skill, the average crash point should be higher than games with lower luck skill.
**Validates: Requirements 4.9**

### Property 18: Luck Skill Retrieval
*For any* player, the entertainment system should correctly retrieve and use their current luck skill level from user data.
**Validates: Requirements 5.1**

### Property 19: Mood Update After Game
*For any* game completion, the player's mood should be updated in user data.
**Validates: Requirements 6.1**

### Property 20: Mood Persistence
*For any* mood change, the new mood value should be immediately persisted to the database.
**Validates: Requirements 6.3**

### Property 21: Mood Display Update
*For any* game completion, the UI should display the updated mood value.
**Validates: Requirements 6.4**

### Property 22: Balance Verification Before Bet
*For any* bet attempt, the system should verify that the player's balance is sufficient before accepting the bet.
**Validates: Requirements 7.1**

### Property 23: Insufficient Balance Rejection
*For any* bet attempt where balance is less than the bet amount, the system should reject the bet and return an error message.
**Validates: Requirements 7.2**

### Property 24: Statistics Recording
*For any* game played, a record should be created with game type, outcome (win/loss), bet amount, and payout, and statistics should be updated immediately in the database.
**Validates: Requirements 8.1, 8.3, 8.5**

### Property 25: Statistics Calculation
*For any* set of game records, the calculated statistics (total wins, total losses, net profit/loss) should accurately reflect the sum of all recorded games.
**Validates: Requirements 8.2**

### Property 26: Statistics Retrieval
*For any* statistics request, the system should return wins, losses, and totals for each game type.
**Validates: Requirements 8.4**

### Property 27: API Error Codes
*For any* invalid API request (malformed data, invalid user_id, etc.), the system should return appropriate HTTP error codes (400 for bad request, 404 for not found, 500 for server error).
**Validates: Requirements 9.5**

### Property 28: API Response Structure
*For any* successful game API call, the response should contain game results, updated balance, and updated mood in JSON format.
**Validates: Requirements 9.6**

### Property 29: API Input Validation
*For any* API call, all input parameters (bet amounts, game choices, user_id) should be validated before processing.
**Validates: Requirements 9.7**

### Property 30: Game Interface Display
*For any* game, the interface should display the game in its own modal window with clear controls.
**Validates: Requirements 10.3**

### Property 31: Balance and Mood Display
*For any* game interface, the current balance and mood should be prominently displayed.
**Validates: Requirements 10.6**

### Property 32: Feedback Messages
*For any* game outcome or error, the system should provide a clear feedback message to the player.
**Validates: Requirements 10.7**

## Error Handling

### Input Validation Errors

1. **Invalid User ID**: Return 400 with message "Invalid user_id"
2. **Insufficient Balance**: Return 400 with message "Недостаточно денег!"
3. **Invalid Bet Amount**: Return 400 with message "Неверная сумма ставки"
4. **Invalid Game Choice**: Return 400 with message "Неверный выбор игры"
5. **Invalid Dice Choice**: Return 400 with message "Выберите: low, seven, или high"

### System Errors

1. **Database Connection Failure**: Return 500 with message "Ошибка базы данных"
2. **User Data Load Failure**: Return 500 with message "Не удалось загрузить данные игрока"
3. **User Data Save Failure**: Return 500 with message "Не удалось сохранить данные"

### Error Response Format

```json
{
    "success": false,
    "error": "Error message in Russian",
    "code": "ERROR_CODE"
}
```

### Logging

All errors should be logged with:
- Timestamp
- User ID (if available)
- Error type
- Error message
- Stack trace (for 500 errors)

## Testing Strategy

### Dual Testing Approach

The entertainment system requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples and edge cases
- API endpoint existence and routing
- Error handling for specific scenarios
- UI component rendering
- Integration between components

**Property-Based Tests** focus on:
- Universal properties across all inputs
- Probability distributions over large samples
- Balance and mood calculations for any valid input
- Input validation boundaries
- Statistical properties of game outcomes

Both testing approaches are complementary and necessary. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across the input space.

### Property-Based Testing Configuration

**Library**: Use `hypothesis` for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each test tagged with: `# Feature: entertainment-system, Property N: [property text]`
- Statistical tests (probability distributions) require 1000+ iterations

**Test Organization**:
```
tests/
├── unit/
│   ├── test_roulette_engine.py
│   ├── test_dice_engine.py
│   ├── test_crash_engine.py
│   ├── test_statistics_manager.py
│   └── test_api_endpoints.py
└── property/
    ├── test_roulette_properties.py
    ├── test_dice_properties.py
    ├── test_crash_properties.py
    ├── test_balance_properties.py
    └── test_mood_properties.py
```

### Example Property Test

```python
from hypothesis import given, strategies as st
import pytest

# Feature: entertainment-system, Property 6: Dice Roll Validity
@given(st.integers(min_value=1, max_value=10))
def test_dice_roll_validity(luck_level):
    """For any dice roll, each die should produce a value between 1 and 6"""
    engine = DiceEngine()
    result = engine.roll(bet=100, choice='low', luck_level=luck_level)
    
    assert 1 <= result['dice1'] <= 6
    assert 1 <= result['dice2'] <= 6
    assert 2 <= result['sum'] <= 12
```

### Unit Test Coverage

**Minimum Coverage Requirements**:
- Roulette Engine: 90%
- Dice Engine: 90%
- Crash Engine: 90%
- Statistics Manager: 85%
- API Endpoints: 80%
- Entertainment Manager: 85%

### Integration Tests

Test complete flows:
1. Player places bet → game executes → balance/mood updated → statistics recorded
2. Player with insufficient balance → bet rejected → no state change
3. Multiple games in sequence → statistics accumulate correctly
4. Luck skill changes → game probabilities adjust accordingly

### Frontend Testing

**Manual Testing Checklist**:
- [ ] Entertainment button replaces roulette button
- [ ] Modal opens with three game options
- [ ] Each game opens in its own modal
- [ ] Balance and mood display correctly
- [ ] Animations play smoothly
- [ ] Error messages display clearly
- [ ] Responsive design works on mobile

**Automated Frontend Tests** (if using testing framework):
- Button click handlers
- Modal open/close behavior
- API call integration
- State updates after game completion

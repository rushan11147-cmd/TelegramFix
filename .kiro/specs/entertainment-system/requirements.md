# Requirements Document: Entertainment System

## Introduction

Система развлечений для игры "Выживи до зарплаты" - это комплексная игровая механика, которая заменяет существующую отдельную кнопку "Рулетка" на централизованное меню развлечений с тремя мини-играми. Система влияет на настроение игрока и использует навык "Удача" для модификации шансов выигрыша.

## Glossary

- **Entertainment_System**: Централизованная система управления мини-играми
- **Player**: Пользователь игры с балансом, навыками, настроением и здоровьем
- **Mood**: Параметр настроения игрока (0-100)
- **Luck_Skill**: Навык "Удача", влияющий на шансы в играх
- **Balance**: Игровой баланс игрока в рублях
- **Bet**: Ставка игрока в конкретной игре
- **Payout**: Выплата при выигрыше
- **Roulette_Game**: Игра с тремя барабанами эмодзи
- **Dice_Game**: Игра с двумя кубиками
- **Crash_Game**: Игра с растущим множителем
- **Game_Statistics**: Статистика игр (выигрыши, проигрыши, суммы)

## Requirements

### Requirement 1: Entertainment Menu

**User Story:** As a player, I want to access all entertainment games from a single menu, so that I can easily choose which game to play.

#### Acceptance Criteria

1. THE Entertainment_System SHALL replace the standalone "Рулетка" button with an "Развлечения 🎰" button
2. WHEN a player clicks the "Развлечения" button, THE Entertainment_System SHALL display a modal window with three game options
3. THE Entertainment_System SHALL display Roulette, Dice, and Crash games in the menu
4. WHEN a player selects a game from the menu, THE Entertainment_System SHALL open that game's interface in a modal window
5. THE Entertainment_System SHALL display the player's current balance and mood in the menu

### Requirement 2: Roulette Game Integration

**User Story:** As a player, I want to play the existing roulette game through the entertainment menu, so that all games are in one place.

#### Acceptance Criteria

1. THE Entertainment_System SHALL integrate the existing Roulette_Game into the entertainment menu
2. THE Roulette_Game SHALL display three reels with emoji symbols
3. THE Roulette_Game SHALL accept bets of 100₽, 500₽, or 1000₽
4. WHEN a player places a bet, THE Roulette_Game SHALL deduct the bet amount from the player's balance
5. THE Roulette_Game SHALL generate results with probabilities: 60% loss, 25% x2 payout, 10% x5 payout, 5% x10 payout
6. WHEN a player wins, THE Roulette_Game SHALL increase mood by 5 points
7. WHEN a player loses, THE Roulette_Game SHALL decrease mood by 10 points
8. THE Roulette_Game SHALL update the player's balance immediately after each spin

### Requirement 3: Dice Game

**User Story:** As a player, I want to play a dice game where I predict the sum of two dice, so that I have more entertainment options.

#### Acceptance Criteria

1. THE Dice_Game SHALL simulate rolling two six-sided dice (1-6 each)
2. THE Dice_Game SHALL accept bets between 100₽ and 1000₽
3. THE Dice_Game SHALL offer three betting options: "Низкие" (2-6), "Семерка" (7), "Высокие" (8-12)
4. WHEN a player bets on "Низкие" and the sum is 2-6, THE Dice_Game SHALL pay out x2.5 the bet
5. WHEN a player bets on "Семерка" and the sum is 7, THE Dice_Game SHALL pay out x6 the bet
6. WHEN a player bets on "Высокие" and the sum is 8-12, THE Dice_Game SHALL pay out x2.5 the bet
7. WHEN a player wins, THE Dice_Game SHALL increase mood by 3 points
8. WHEN a player loses, THE Dice_Game SHALL decrease mood by 5 points
9. THE Dice_Game SHALL apply Luck_Skill bonus: +5% win chance per luck level
10. THE Dice_Game SHALL display animated dice rolling

### Requirement 4: Crash Game

**User Story:** As a player, I want to play a crash game where I can cash out before the multiplier crashes, so that I can test my timing and luck.

#### Acceptance Criteria

1. THE Crash_Game SHALL display a multiplier starting at x1.0
2. THE Crash_Game SHALL accept bets between 100₽ and 5000₽
3. THE Crash_Game SHALL increase the multiplier continuously until crash
4. THE Crash_Game SHALL determine crash point randomly between x1.1 and x10.0
5. WHEN a player clicks "Cash Out" before crash, THE Crash_Game SHALL pay out bet multiplied by current multiplier
6. WHEN the crash occurs before cash out, THE Crash_Game SHALL result in loss of the bet
7. WHEN a player cashes out at x5.0 or higher, THE Crash_Game SHALL increase mood by 10 points
8. WHEN a player loses to crash, THE Crash_Game SHALL decrease mood by 15 points
9. THE Crash_Game SHALL apply Luck_Skill to influence crash point probability
10. THE Crash_Game SHALL display animated multiplier growth

### Requirement 5: Luck Skill Integration

**User Story:** As a player, I want my Luck skill to improve my chances in entertainment games, so that skill progression feels meaningful.

#### Acceptance Criteria

1. THE Entertainment_System SHALL read the player's current Luck_Skill level
2. THE Dice_Game SHALL increase win probability by 5% per Luck_Skill level
3. THE Crash_Game SHALL shift crash point distribution toward higher values based on Luck_Skill
4. THE Entertainment_System SHALL apply Luck_Skill modifiers before calculating game outcomes
5. THE Entertainment_System SHALL display Luck_Skill effects in game tooltips

### Requirement 6: Mood System Integration

**User Story:** As a player, I want entertainment games to affect my mood, so that there are consequences and benefits to gambling.

#### Acceptance Criteria

1. THE Entertainment_System SHALL update the player's mood after each game result
2. WHEN mood changes occur, THE Entertainment_System SHALL ensure mood stays within 0-100 range
3. THE Entertainment_System SHALL persist mood changes to the database immediately
4. THE Entertainment_System SHALL display updated mood value in the UI after each game
5. WHEN mood reaches 0, THE Entertainment_System SHALL still allow playing games

### Requirement 7: Balance Management

**User Story:** As a player, I want my balance to be accurately tracked across all entertainment games, so that I can trust the system.

#### Acceptance Criteria

1. WHEN a player places a bet, THE Entertainment_System SHALL verify sufficient balance exists
2. IF balance is insufficient, THEN THE Entertainment_System SHALL prevent the bet and display an error message
3. THE Entertainment_System SHALL deduct bet amounts before game execution
4. THE Entertainment_System SHALL add winnings to balance immediately after game completion
5. THE Entertainment_System SHALL persist all balance changes to the database
6. THE Entertainment_System SHALL display updated balance in real-time

### Requirement 8: Game Statistics

**User Story:** As a player, I want to see my entertainment game statistics, so that I can track my performance.

#### Acceptance Criteria

1. THE Entertainment_System SHALL record each game played with outcome (win/loss) and amount
2. THE Entertainment_System SHALL calculate total wins, total losses, and net profit/loss per game type
3. THE Entertainment_System SHALL store Game_Statistics in the database
4. WHEN a player requests statistics, THE Entertainment_System SHALL display wins, losses, and totals for each game
5. THE Entertainment_System SHALL update statistics immediately after each game

### Requirement 9: API Endpoints

**User Story:** As a developer, I want RESTful API endpoints for each game, so that the frontend can interact with the backend cleanly.

#### Acceptance Criteria

1. THE Entertainment_System SHALL provide a POST endpoint for Roulette_Game at /api/entertainment/roulette
2. THE Entertainment_System SHALL provide a POST endpoint for Dice_Game at /api/entertainment/dice
3. THE Entertainment_System SHALL provide a POST endpoint for Crash_Game at /api/entertainment/crash
4. THE Entertainment_System SHALL provide a GET endpoint for Game_Statistics at /api/entertainment/stats
5. WHEN an API request is invalid, THE Entertainment_System SHALL return appropriate HTTP error codes (400, 404, 500)
6. THE Entertainment_System SHALL return JSON responses with game results, updated balance, and mood
7. THE Entertainment_System SHALL validate all input parameters (bet amounts, game choices)

### Requirement 10: UI/UX Requirements

**User Story:** As a player, I want an intuitive and visually appealing interface for entertainment games, so that playing is enjoyable.

#### Acceptance Criteria

1. THE Entertainment_System SHALL display the "Развлечения 🎰" button in the main game interface
2. THE Entertainment_System SHALL show a modal window with game selection when the button is clicked
3. THE Entertainment_System SHALL display each game in its own modal window with clear controls
4. THE Dice_Game SHALL animate dice rolling for visual feedback
5. THE Crash_Game SHALL animate multiplier growth smoothly
6. THE Entertainment_System SHALL display current balance and mood prominently in all game interfaces
7. THE Entertainment_System SHALL provide clear feedback messages for wins, losses, and errors
8. THE Entertainment_System SHALL use responsive design for mobile devices (Telegram Mini App)

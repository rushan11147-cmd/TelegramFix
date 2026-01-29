# Requirements Document: Economy Balancing System

## Introduction

Система балансировки экономики для игры "Выживи до зарплаты" предназначена для увеличения сложности и вовлеченности игроков путем введения обязательных ежедневных расходов, корректировки доходов, увеличения частоты негативных событий и внедрения прогрессивной системы расходов. Цель - сделать достижение зарплаты реальным челленджем, требующим планирования бюджета и стратегических решений.

## Glossary

- **Player**: Игрок, управляющий персонажем в игре
- **Balance_System**: Система балансировки экономики
- **Daily_Expenses**: Ежедневные обязательные расходы (аренда, еда, транспорт)
- **Income_Source**: Источник дохода (работа, подработка, бизнес)
- **Negative_Event**: Случайное негативное событие, требующее расходов
- **Progressive_Expenses**: Прогрессивные расходы, увеличивающиеся с ростом богатства
- **Wealth_Tier**: Уровень богатства игрока (бедный, средний, богатый)
- **Energy**: Энергия персонажа (0-100), восстанавливается ежедневно
- **Salary_Day**: День выплаты зарплаты (конец месяца)
- **Game_Day**: Игровой день (24 часа в игре)

## Requirements

### Requirement 1: Daily Mandatory Expenses

**User Story:** Как игрок, я хочу иметь ежедневные обязательные расходы, чтобы игра была более реалистичной и сложной.

#### Acceptance Criteria

1. WHEN a new game day starts, THE Balance_System SHALL calculate and deduct daily expenses from the player's balance
2. THE Balance_System SHALL include rent expenses in daily calculations (proportional to monthly rent divided by 30 days)
3. THE Balance_System SHALL include food expenses in daily calculations (minimum 50₽ per day)
4. THE Balance_System SHALL include transport expenses in daily calculations (minimum 30₽ per day)
5. WHEN the player's balance is insufficient for daily expenses, THE Balance_System SHALL allow negative balance and track debt
6. THE Balance_System SHALL display a breakdown of daily expenses to the player each morning

### Requirement 2: Income Adjustment

**User Story:** Как разработчик игры, я хочу уменьшить доходы от работы, чтобы игроки не могли слишком быстро разбогатеть.

#### Acceptance Criteria

1. THE Balance_System SHALL reduce delivery job income from 80₽ to 50₽
2. THE Balance_System SHALL reduce office job income from 120₽ to 80₽
3. THE Balance_System SHALL reduce freelance job income from 200₽ to 130₽
4. THE Balance_System SHALL reduce crypto job income from 300₽ to 180₽
5. WHEN calculating job income, THE Balance_System SHALL apply the new reduced rates
6. THE Balance_System SHALL maintain existing energy costs for each job type

### Requirement 3: Negative Events System

**User Story:** Как игрок, я хочу сталкиваться с более частыми и значимыми негативными событиями, чтобы игра была более непредсказуемой и сложной.

#### Acceptance Criteria

1. THE Balance_System SHALL increase negative event probability from current rate to 25% per day
2. WHEN a negative event occurs, THE Balance_System SHALL select an event from an expanded event pool
3. THE Balance_System SHALL include medical emergency events costing 500-1500₽
4. THE Balance_System SHALL include fine/penalty events costing 300-800₽
5. THE Balance_System SHALL include equipment breakdown events costing 400-1200₽
6. THE Balance_System SHALL include unexpected bill events costing 200-600₽
7. WHEN a negative event is triggered, THE Balance_System SHALL deduct the cost immediately and notify the player

### Requirement 4: Progressive Expense System

**User Story:** Как игрок, я хочу, чтобы мои расходы росли вместе с доходами, чтобы богатство не делало игру слишком легкой.

#### Acceptance Criteria

1. THE Balance_System SHALL categorize players into wealth tiers based on current balance
2. WHEN player balance is 0-3000₽, THE Balance_System SHALL classify them as "poor" tier
3. WHEN player balance is 3001-10000₽, THE Balance_System SHALL classify them as "middle" tier
4. WHEN player balance exceeds 10000₽, THE Balance_System SHALL classify them as "rich" tier
5. THE Balance_System SHALL apply a 1.0x expense multiplier for poor tier
6. THE Balance_System SHALL apply a 1.5x expense multiplier for middle tier
7. THE Balance_System SHALL apply a 2.0x expense multiplier for rich tier
8. WHEN calculating daily expenses, THE Balance_System SHALL multiply base expenses by the player's wealth tier multiplier

### Requirement 5: Budget Survival Mechanics

**User Story:** Как игрок, я хочу, чтобы выживание до зарплаты было реальным челленджем, требующим планирования.

#### Acceptance Criteria

1. THE Balance_System SHALL ensure daily expenses consume 50-70% of average daily income from basic jobs
2. WHEN a player does not work for 3 consecutive days, THE Balance_System SHALL result in negative balance
3. WHEN a player does not work for 5 consecutive days, THE Balance_System SHALL result in debt exceeding 500₽
4. THE Balance_System SHALL make reaching salary day possible with consistent work and budget management
5. THE Balance_System SHALL track player's daily net income (income minus expenses)

### Requirement 6: Expense Calculation and Display

**User Story:** Как игрок, я хочу видеть детальную информацию о моих расходах, чтобы планировать бюджет.

#### Acceptance Criteria

1. THE Balance_System SHALL calculate total daily expenses before deduction
2. THE Balance_System SHALL store expense breakdown (rent, food, transport, tier multiplier)
3. WHEN displaying expenses, THE Balance_System SHALL show each expense category separately
4. WHEN displaying expenses, THE Balance_System SHALL show the applied wealth tier multiplier
5. THE Balance_System SHALL display total daily expenses and remaining balance after deduction

### Requirement 7: Debt Management

**User Story:** Как игрок, я хочу иметь возможность уйти в долг, но с последствиями, чтобы финансовые ошибки имели значение.

#### Acceptance Criteria

1. WHEN player balance becomes negative, THE Balance_System SHALL track the debt amount
2. THE Balance_System SHALL allow players to continue playing with negative balance
3. WHEN player balance is negative for 3 consecutive days, THE Balance_System SHALL increase negative event probability to 40%
4. WHEN player balance is negative for 7 consecutive days, THE Balance_System SHALL trigger a mandatory "debt collector" event costing 20% of absolute debt value
5. THE Balance_System SHALL display debt amount prominently in the UI when balance is negative

### Requirement 8: Integration with Existing Systems

**User Story:** Как разработчик, я хочу, чтобы система балансировки интегрировалась с существующими игровыми системами, чтобы обеспечить целостность игры.

#### Acceptance Criteria

1. THE Balance_System SHALL integrate with the existing work system (delivery, office, freelance, crypto)
2. THE Balance_System SHALL integrate with the existing energy system
3. THE Balance_System SHALL integrate with the existing events system
4. THE Balance_System SHALL integrate with the existing property system (rent calculation)
5. THE Balance_System SHALL integrate with the existing business system (business income not affected by income reduction)
6. THE Balance_System SHALL integrate with the existing side jobs system
7. THE Balance_System SHALL integrate with the existing entertainment system

### Requirement 9: Configuration and Tuning

**User Story:** Как разработчик, я хочу иметь возможность легко настраивать параметры балансировки, чтобы тестировать и корректировать сложность игры.

#### Acceptance Criteria

1. THE Balance_System SHALL store all balance parameters in a configuration file
2. THE Balance_System SHALL allow modification of daily expense amounts without code changes
3. THE Balance_System SHALL allow modification of income rates without code changes
4. THE Balance_System SHALL allow modification of wealth tier thresholds without code changes
5. THE Balance_System SHALL allow modification of expense multipliers without code changes
6. THE Balance_System SHALL allow modification of negative event probabilities without code changes

### Requirement 10: Data Persistence

**User Story:** Как игрок, я хочу, чтобы моя финансовая история сохранялась, чтобы видеть прогресс и статистику.

#### Acceptance Criteria

1. THE Balance_System SHALL persist daily expense records to the database
2. THE Balance_System SHALL persist daily income records to the database
3. THE Balance_System SHALL persist negative event history to the database
4. THE Balance_System SHALL persist wealth tier changes to the database
5. WHEN a player requests financial history, THE Balance_System SHALL retrieve and display records for the last 30 game days

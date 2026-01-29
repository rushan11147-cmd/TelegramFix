# Requirements Document: Business Branch Feature

## Introduction

Данный документ описывает требования к новой игровой механике "Ветка бизнеса" для Telegram Mini App игры "Выживи до зарплаты". Фича позволяет игрокам открывать и развивать собственный бизнес в сфере общественного питания - от киоска с шаурмой до сети ресторанов. Бизнес становится источником пассивного дохода, но требует активного управления: найма сотрудников, контроля запасов, улучшений и реагирования на случайные события.

## Glossary

- **Business_System**: Система управления бизнесом игрока
- **Business_Type**: Тип бизнеса (киоск, кафе, ресторан, сеть ресторанов)
- **Employee**: Сотрудник бизнеса (повар, кассир, менеджер)
- **Inventory**: Запасы продуктов для бизнеса (0-100%)
- **Rating**: Рейтинг бизнеса (1-5 звезд)
- **Upgrade**: Улучшение бизнеса (новое меню, доставка, ремонт, реклама)
- **Business_Event**: Случайное событие, влияющее на бизнес
- **Daily_Revenue**: Ежедневный доход бизнеса
- **Daily_Expenses**: Ежедневные расходы бизнеса
- **Net_Profit**: Чистая прибыль (доход минус расходы)
- **Game_State**: Состояние основной игры
- **User_Data**: Данные игрока в базе данных

## Requirements

### Requirement 1: Business Creation

**User Story:** As a player, I want to create a business of different types, so that I can start earning passive income.

#### Acceptance Criteria

1. WHEN a player has sufficient funds and requests to create a business, THE Business_System SHALL create a new business of the selected type and deduct the cost from player funds
2. WHEN a player creates a Kiosk business, THE Business_System SHALL deduct 50,000₽ from player funds
3. WHEN a player creates a Cafe business, THE Business_System SHALL deduct 300,000₽ from player funds
4. WHEN a player creates a Restaurant business, THE Business_System SHALL deduct 1,000,000₽ from player funds
5. WHEN a player creates a Restaurant_Chain business, THE Business_System SHALL deduct 5,000,000₽ from player funds
6. WHEN a player has insufficient funds for a business type, THE Business_System SHALL prevent creation and display an error message
7. WHEN a business is created, THE Business_System SHALL initialize it with default values: 100% inventory, 3-star rating, no employees, no upgrades

### Requirement 2: Employee Management

**User Story:** As a player, I want to hire and manage employees, so that I can improve my business performance.

#### Acceptance Criteria

1. WHEN a player hires a Chef employee, THE Business_System SHALL add the employee to the business, deduct 5,000₽ daily expenses, and increase quality by 30%
2. WHEN a player hires a Cashier employee, THE Business_System SHALL add the employee to the business, deduct 3,000₽ daily expenses, and increase service speed by 20%
3. WHEN a player hires a Manager employee, THE Business_System SHALL add the employee to the business, deduct 8,000₽ daily expenses, and increase revenue by 25%
4. WHEN a player attempts to hire more employees than the business type allows, THE Business_System SHALL prevent hiring and display an error message
5. WHEN a player fires an employee, THE Business_System SHALL remove the employee from the business and remove their daily cost and bonuses
6. WHEN calculating daily expenses, THE Business_System SHALL sum all employee salaries

### Requirement 3: Inventory Management

**User Story:** As a player, I want to manage product inventory, so that my business can operate efficiently.

#### Acceptance Criteria

1. WHEN a day passes, THE Business_System SHALL decrease inventory level by 10%
2. WHEN inventory level falls below 20%, THE Business_System SHALL reduce daily revenue by 50%
3. WHEN a player purchases inventory for 5,000₽, THE Business_System SHALL increase inventory level by 50% and deduct 5,000₽ from player funds
4. WHEN inventory level would exceed 100% after purchase, THE Business_System SHALL set inventory level to 100%
5. WHEN a player has insufficient funds to purchase inventory, THE Business_System SHALL prevent purchase and display an error message

### Requirement 4: Business Upgrades

**User Story:** As a player, I want to purchase upgrades for my business, so that I can increase revenue and rating.

#### Acceptance Criteria

1. WHEN a player purchases the New_Menu upgrade for 50,000₽, THE Business_System SHALL add the upgrade to the business, deduct 50,000₽, and increase daily revenue by 30%
2. WHEN a player purchases the Delivery upgrade for 80,000₽, THE Business_System SHALL add the upgrade to the business, deduct 80,000₽, and increase daily revenue by 50%
3. WHEN a player purchases the Renovation upgrade for 100,000₽, THE Business_System SHALL add the upgrade to the business, deduct 100,000₽, and increase rating by 1 star
4. WHEN a player purchases the Advertising upgrade for 30,000₽, THE Business_System SHALL add the upgrade to the business, deduct 30,000₽, increase customer count by 20% for 7 days, and track the expiration
5. WHEN a player has insufficient funds for an upgrade, THE Business_System SHALL prevent purchase and display an error message
6. WHEN a player attempts to purchase an already owned permanent upgrade, THE Business_System SHALL prevent purchase and display an error message
7. WHEN the Advertising upgrade expires after 7 days, THE Business_System SHALL remove the customer count bonus

### Requirement 5: Daily Revenue Calculation

**User Story:** As a player, I want my business to generate daily revenue, so that I can earn passive income.

#### Acceptance Criteria

1. WHEN a day passes, THE Business_System SHALL calculate daily revenue based on business type, rating, employees, upgrades, and inventory level
2. WHEN calculating revenue for a Kiosk, THE Business_System SHALL use a base revenue of 8,000₽ per day
3. WHEN calculating revenue for a Cafe, THE Business_System SHALL use a base revenue of 40,000₽ per day
4. WHEN calculating revenue for a Restaurant, THE Business_System SHALL use a base revenue of 150,000₽ per day
5. WHEN calculating revenue for a Restaurant_Chain, THE Business_System SHALL use a base revenue of 800,000₽ per day
6. WHEN calculating revenue, THE Business_System SHALL multiply base revenue by rating multiplier: (rating / 3.0)
7. WHEN calculating revenue with a Manager employee, THE Business_System SHALL apply a 25% bonus to the result
8. WHEN calculating revenue with New_Menu upgrade, THE Business_System SHALL apply a 30% bonus to the result
9. WHEN calculating revenue with Delivery upgrade, THE Business_System SHALL apply a 50% bonus to the result
10. WHEN calculating revenue with active Advertising upgrade, THE Business_System SHALL apply a 20% bonus to the result
11. WHEN inventory level is below 20%, THE Business_System SHALL apply a 50% penalty to the result

### Requirement 6: Daily Expenses Calculation

**User Story:** As a player, I want to track daily business expenses, so that I can understand my net profit.

#### Acceptance Criteria

1. WHEN a day passes, THE Business_System SHALL calculate daily expenses based on business type and employees
2. WHEN calculating expenses for a Kiosk, THE Business_System SHALL include 2,000₽ base rent
3. WHEN calculating expenses for a Cafe, THE Business_System SHALL include 10,000₽ base rent
4. WHEN calculating expenses for a Restaurant, THE Business_System SHALL include 30,000₽ base rent
5. WHEN calculating expenses for a Restaurant_Chain, THE Business_System SHALL include 150,000₽ base rent
6. WHEN calculating expenses, THE Business_System SHALL add all employee salaries to base rent

### Requirement 7: Net Profit Calculation

**User Story:** As a player, I want to see my net profit, so that I can evaluate business performance.

#### Acceptance Criteria

1. WHEN a day passes, THE Business_System SHALL calculate net profit as daily revenue minus daily expenses
2. WHEN net profit is positive, THE Business_System SHALL add the profit to player funds
3. WHEN net profit is negative, THE Business_System SHALL deduct the loss from player funds
4. WHEN a player views business details, THE Business_System SHALL display current daily revenue, daily expenses, and net profit

### Requirement 8: Business Events

**User Story:** As a player, I want to experience random business events, so that the game remains challenging and unpredictable.

#### Acceptance Criteria

1. WHEN a day passes, THE Business_System SHALL randomly trigger business events with appropriate probabilities
2. WHEN a Health_Inspection event occurs, THE Business_System SHALL either apply a fine (deduct 50,000₽) or temporarily close the business (0 revenue for 2 days)
3. WHEN a Competitor_Opens event occurs, THE Business_System SHALL reduce daily revenue by 20% for 14 days
4. WHEN a Viral_Post event occurs, THE Business_System SHALL increase daily revenue by 50% for 3 days
5. WHEN an Equipment_Breakdown event occurs, THE Business_System SHALL require a repair payment of 20,000₽ and reduce revenue by 30% until repaired
6. WHEN a player pays for equipment repair, THE Business_System SHALL remove the revenue penalty and deduct 20,000₽ from player funds
7. WHEN an event expires, THE Business_System SHALL remove its effects from revenue calculations

### Requirement 9: Business Sale

**User Story:** As a player, I want to sell my business, so that I can recover some of my investment.

#### Acceptance Criteria

1. WHEN a player sells a business, THE Business_System SHALL calculate sale price as 50% of total invested amount (initial cost plus all upgrades)
2. WHEN a player sells a business, THE Business_System SHALL add the sale price to player funds and remove the business from player data
3. WHEN a player confirms business sale, THE Business_System SHALL permanently delete all business data including employees, upgrades, and inventory

### Requirement 10: Game Integration

**User Story:** As a player, I want business mechanics to integrate with the main game, so that it feels like a cohesive experience.

#### Acceptance Criteria

1. WHEN a day passes in the main game, THE Business_System SHALL process all player businesses: update inventory, calculate revenue/expenses, apply event effects, and update player funds
2. WHEN a player views their profile, THE Game_State SHALL display total business count and total daily net profit from all businesses
3. WHEN a player achieves 100,000₽ total net profit from businesses, THE Game_State SHALL unlock the "Businessman" achievement
4. WHEN a player owns a Restaurant_Chain, THE Game_State SHALL unlock the "Tycoon" achievement

### Requirement 11: Data Persistence

**User Story:** As a developer, I want business data to persist in the database, so that player progress is saved.

#### Acceptance Criteria

1. WHEN a business is created, modified, or deleted, THE Business_System SHALL update the User_Data in the database immediately
2. WHEN a player logs in, THE Business_System SHALL load all business data from User_Data
3. WHEN storing business data, THE Business_System SHALL serialize business type, employees, inventory level, rating, upgrades, active events, and creation date
4. WHEN loading business data, THE Business_System SHALL deserialize all fields and reconstruct business state correctly

### Requirement 12: API Endpoints

**User Story:** As a developer, I want RESTful API endpoints for business operations, so that the frontend can interact with the business system.

#### Acceptance Criteria

1. THE Business_System SHALL provide a POST /api/business/create endpoint that accepts business_type and returns created business data or error
2. THE Business_System SHALL provide a POST /api/business/hire endpoint that accepts business_id and employee_type and returns updated business data or error
3. THE Business_System SHALL provide a POST /api/business/fire endpoint that accepts business_id and employee_id and returns updated business data or error
4. THE Business_System SHALL provide a POST /api/business/buy-inventory endpoint that accepts business_id and returns updated business data or error
5. THE Business_System SHALL provide a POST /api/business/upgrade endpoint that accepts business_id and upgrade_type and returns updated business data or error
6. THE Business_System SHALL provide a GET /api/business/list endpoint that returns all player businesses with current stats
7. THE Business_System SHALL provide a POST /api/business/sell endpoint that accepts business_id and returns sale confirmation and updated player funds
8. THE Business_System SHALL provide a POST /api/business/repair endpoint that accepts business_id and returns updated business data after repair
9. WHEN any API endpoint receives invalid data, THE Business_System SHALL return a 400 error with descriptive message
10. WHEN any API endpoint is called by an unauthenticated user, THE Business_System SHALL return a 401 error

### Requirement 13: Employee Capacity Limits

**User Story:** As a player, I want different business types to support different numbers of employees, so that larger businesses feel more substantial.

#### Acceptance Criteria

1. WHEN a Kiosk business is created, THE Business_System SHALL set maximum employee capacity to 2
2. WHEN a Cafe business is created, THE Business_System SHALL set maximum employee capacity to 4
3. WHEN a Restaurant business is created, THE Business_System SHALL set maximum employee capacity to 6
4. WHEN a Restaurant_Chain business is created, THE Business_System SHALL set maximum employee capacity to 10
5. WHEN a player attempts to hire an employee beyond capacity, THE Business_System SHALL prevent hiring and return an error message

### Requirement 14: Rating System

**User Story:** As a player, I want my business rating to affect revenue, so that maintaining quality matters.

#### Acceptance Criteria

1. WHEN a business is created, THE Business_System SHALL initialize rating to 3 stars
2. WHEN a Chef employee is hired, THE Business_System SHALL increase rating by 0.5 stars (capped at 5 stars)
3. WHEN a Chef employee is fired, THE Business_System SHALL decrease rating by 0.5 stars (minimum 1 star)
4. WHEN a Renovation upgrade is purchased, THE Business_System SHALL increase rating by 1 star (capped at 5 stars)
5. WHEN inventory level falls below 20% for 3 consecutive days, THE Business_System SHALL decrease rating by 0.5 stars (minimum 1 star)
6. WHEN a Health_Inspection event results in a fine, THE Business_System SHALL decrease rating by 1 star (minimum 1 star)

### Requirement 15: UI Display

**User Story:** As a player, I want a clear UI for managing my businesses, so that I can easily understand and control them.

#### Acceptance Criteria

1. WHEN a player opens the business section, THE Business_System SHALL display a list of all owned businesses with key stats: type, rating, daily profit, inventory level
2. WHEN a player selects a business, THE Business_System SHALL display detailed view with: employees, upgrades, active events, revenue breakdown, expense breakdown
3. WHEN a player views available actions, THE Business_System SHALL display: hire employee buttons, buy inventory button, purchase upgrade buttons, sell business button
4. WHEN an action is unavailable due to insufficient funds, THE Business_System SHALL disable the button and show required amount
5. WHEN an action is unavailable due to capacity limits, THE Business_System SHALL disable the button and show reason
6. WHEN a business event is active, THE Business_System SHALL display event notification with icon, description, and remaining duration

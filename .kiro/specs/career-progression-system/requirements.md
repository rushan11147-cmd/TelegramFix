# Requirements Document: Career Progression System

## Introduction

The Career Progression System provides players with a structured career path that begins with choosing an initial profession and progresses through multiple levels of advancement. Each profession has unique characteristics, salary structures, and promotion requirements that create meaningful progression and strategic choices throughout the game.

## Glossary

- **Career_System**: The module responsible for managing profession selection, career advancement, and promotion logic
- **Profession**: A career path that a player can choose at game start (Courier, Office Worker, Salesperson, Waiter, Security Guard, or IT Support)
- **Career_Level**: A specific position within a profession's hierarchy (e.g., Courier, Senior Courier, Delivery Manager)
- **Promotion**: The act of advancing from one Career_Level to the next within a Profession
- **Work_Action**: A single instance of performing work that contributes to career progression
- **Base_Salary**: The fixed income amount earned per Work_Action at a given Career_Level
- **Progression_Metrics**: Quantifiable measures used to determine promotion eligibility (work experience, skills, money earned, days survived)
- **Player**: The user playing the game
- **Game_State**: The current state of the player's game including all statistics and progress

## Requirements

### Requirement 1: Initial Profession Selection

**User Story:** As a player, I want to choose my starting profession at the beginning of the game, so that I can start my career journey with a path that matches my preferred playstyle.

#### Acceptance Criteria

1. WHEN a new game starts, THE Career_System SHALL present six profession options before trait selection
2. THE Career_System SHALL provide Courier, Office Worker, Salesperson, Waiter, Security Guard, and IT Support as the six available professions
3. WHEN a player selects a profession, THE Career_System SHALL set the player's initial Career_Level to the entry position of that profession
4. WHEN a player selects a profession, THE Career_System SHALL initialize the player's Base_Salary according to that profession's starting salary
5. THE Career_System SHALL prevent game progression until a profession is selected

### Requirement 2: Profession Characteristics

**User Story:** As a player, I want each profession to have distinct characteristics, so that my choice meaningfully affects my gameplay experience.

#### Acceptance Criteria

1. WHEN a player selects Courier, THE Career_System SHALL set the starting Base_Salary to 150 currency units
2. WHEN a player selects Office Worker, THE Career_System SHALL set the starting Base_Salary to 250 currency units
3. WHEN a player selects Salesperson, THE Career_System SHALL set the starting Base_Salary to 200 currency units
4. WHEN a player selects Waiter, THE Career_System SHALL set the starting Base_Salary to 180 currency units
5. WHEN a player selects Security Guard, THE Career_System SHALL set the starting Base_Salary to 220 currency units
6. WHEN a player selects IT Support, THE Career_System SHALL set the starting Base_Salary to 280 currency units
7. WHEN a player works as a Courier, THE Career_System SHALL apply a progression multiplier of 1.5x to work experience gains
8. WHEN a player works as an Office Worker, THE Career_System SHALL apply a progression multiplier of 1.0x to work experience gains
9. WHEN a player works as a Salesperson, THE Career_System SHALL calculate bonus income based on charisma skill level
10. WHEN a player works as a Waiter, THE Career_System SHALL calculate bonus income based on mood level
11. WHEN a player works as a Security Guard, THE Career_System SHALL reduce energy cost by 10% per work action
12. WHEN a player works as IT Support, THE Career_System SHALL calculate bonus income based on intelligence skill level

### Requirement 3: Career Ladder Structure

**User Story:** As a player, I want each profession to have multiple career levels, so that I have clear advancement goals throughout the game.

#### Acceptance Criteria

1. THE Career_System SHALL define four Career_Levels for the Courier profession: Courier → Senior Courier → Logistics Coordinator → Logistics Director
2. THE Career_System SHALL define four Career_Levels for the Office Worker profession: Office Worker → Senior Specialist → Team Lead → Department Manager
3. THE Career_System SHALL define four Career_Levels for the Salesperson profession: Salesperson → Senior Salesperson → Sales Manager → Regional Director
4. THE Career_System SHALL define four Career_Levels for the Waiter profession: Waiter → Senior Waiter → Restaurant Supervisor → Restaurant Manager
5. THE Career_System SHALL define four Career_Levels for the Security Guard profession: Security Guard → Senior Guard → Security Supervisor → Security Chief
6. THE Career_System SHALL define four Career_Levels for the IT Support profession: IT Support → System Administrator → IT Manager → IT Director
7. WHEN a player is at a Career_Level, THE Career_System SHALL track progress toward the next Career_Level
8. THE Career_System SHALL prevent advancement beyond the highest Career_Level in each profession

### Requirement 4: Promotion Requirements

**User Story:** As a player, I want clear requirements for each promotion, so that I know what goals to work toward for career advancement.

#### Acceptance Criteria

1. WHEN evaluating promotion eligibility, THE Career_System SHALL check if the player has completed the required number of Work_Actions for the target Career_Level
2. WHEN evaluating promotion eligibility, THE Career_System SHALL check if the player's relevant skill levels meet or exceed the target Career_Level requirements
3. WHEN evaluating promotion eligibility, THE Career_System SHALL check if the player's total money earned meets or exceeds the target Career_Level threshold
4. WHEN evaluating promotion eligibility, THE Career_System SHALL check if the player's days survived meets or exceeds the target Career_Level requirement
5. WHEN all promotion requirements are met, THE Career_System SHALL mark the promotion as available
6. THE Career_System SHALL require different skill combinations for different professions:
   - Courier: speed/luck skills
   - Office Worker: intelligence/charisma skills
   - Salesperson: charisma/luck skills
   - Waiter: charisma/speed skills
   - Security Guard: speed/intelligence skills
   - IT Support: intelligence/luck skills

### Requirement 5: Promotion Execution

**User Story:** As a player, I want to receive promotions when I meet the requirements, so that my career advancement is recognized and rewarded.

#### Acceptance Criteria

1. WHEN a player meets all promotion requirements, THE Career_System SHALL allow the player to accept the promotion
2. WHEN a promotion is accepted, THE Career_System SHALL update the player's Career_Level to the next level in the profession hierarchy
3. WHEN a promotion is accepted, THE Career_System SHALL increase the player's Base_Salary according to the new Career_Level
4. WHEN a promotion is accepted, THE Career_System SHALL reset the promotion progress tracking for the new Career_Level
5. WHEN a promotion is accepted, THE Career_System SHALL persist the new career state to the Game_State

### Requirement 6: Salary and Benefits Scaling

**User Story:** As a player, I want higher career levels to provide better rewards, so that career advancement feels meaningful and impactful.

#### Acceptance Criteria

1. WHEN a player is promoted, THE Career_System SHALL increase the Base_Salary by a minimum of 50% compared to the previous Career_Level
2. WHEN a player is at Career_Level 2 or higher, THE Career_System SHALL reduce the energy cost per Work_Action by 5% per level
3. WHEN a player reaches Career_Level 3 or higher, THE Career_System SHALL unlock special ability bonuses specific to the profession
4. THE Career_System SHALL calculate final work income as Base_Salary plus any profession-specific bonuses

### Requirement 7: Career Progress Visualization

**User Story:** As a player, I want to see my career progress visually, so that I can track my advancement and understand how close I am to the next promotion.

#### Acceptance Criteria

1. WHEN displaying career information, THE Career_System SHALL show the player's current Career_Level title
2. WHEN displaying career information, THE Career_System SHALL show a progress indicator for each promotion requirement
3. WHEN displaying career information, THE Career_System SHALL show the percentage completion toward the next promotion
4. WHEN displaying career information, THE Career_System SHALL display the Base_Salary for the current Career_Level
5. WHEN a player is at the maximum Career_Level, THE Career_System SHALL display a completion indicator instead of progress bars

### Requirement 8: Integration with Existing Systems

**User Story:** As a developer, I want the career system to integrate seamlessly with existing game systems, so that it enhances rather than disrupts the current gameplay.

#### Acceptance Criteria

1. WHEN a Work_Action is performed, THE Career_System SHALL update career progression metrics before calculating income
2. WHEN calculating work income, THE Career_System SHALL use the current Career_Level's Base_Salary as the foundation
3. WHEN the skills system updates skill levels, THE Career_System SHALL re-evaluate promotion eligibility
4. WHEN displaying statistics, THE Career_System SHALL provide career information to the statistics display module
5. WHEN displaying leaderboard data, THE Career_System SHALL include Career_Level and profession information in player rankings

### Requirement 9: Career State Persistence

**User Story:** As a player, I want my career progress to be saved, so that I don't lose my advancement when I close and reopen the game.

#### Acceptance Criteria

1. WHEN a player's career state changes, THE Career_System SHALL serialize the career data to the Game_State
2. WHEN a game is loaded, THE Career_System SHALL deserialize and restore the player's profession, Career_Level, and progression metrics
3. WHEN serializing career data, THE Career_System SHALL include profession type, current Career_Level, work experience count, and promotion progress
4. WHEN deserializing career data, THE Career_System SHALL validate that the loaded data is consistent with the career ladder definitions
5. IF career data is corrupted or invalid, THEN THE Career_System SHALL reset the player to the entry level of their profession

### Requirement 10: Career Statistics Tracking

**User Story:** As a player, I want the game to track my career achievements, so that I can see my professional growth over time.

#### Acceptance Criteria

1. THE Career_System SHALL track the total number of promotions received across the game session
2. THE Career_System SHALL track the total Work_Actions completed at each Career_Level
3. THE Career_System SHALL track the total income earned at each Career_Level
4. THE Career_System SHALL track the date/time when each promotion was achieved
5. WHEN displaying career statistics, THE Career_System SHALL present this historical data in a readable format

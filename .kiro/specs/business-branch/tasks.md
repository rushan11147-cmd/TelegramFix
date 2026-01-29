# Implementation Plan: Business Branch Feature

## Overview

This implementation plan breaks down the Business Branch feature into discrete coding tasks. The feature adds business management mechanics to the "Survive Until Payday" game, allowing players to create and manage food service businesses. The implementation follows a bottom-up approach: data models → business logic → API endpoints → frontend integration → testing.

The backend is implemented in Python (Flask), and the frontend in JavaScript. Each task builds incrementally, ensuring testable progress at every step.

## Tasks

- [x] 1. Set up data models and enums
  - Create Python enums for BusinessType, EmployeeType, UpgradeType, EventType, EventOutcome
  - Create data classes for Business, Employee, Upgrade, BusinessEvent
  - Define configuration dictionaries (BUSINESS_CONFIGS, EMPLOYEE_CONFIGS, UPGRADE_CONFIGS, EVENT_CONFIGS)
  - Implement getter methods on Business class (get_max_employees, get_base_revenue, get_base_rent, calculate_total_investment)
  - Implement getter methods on Employee class (get_daily_salary, get_quality_bonus, get_revenue_multiplier)
  - Implement getter methods on Upgrade class (get_cost, get_revenue_multiplier, get_rating_bonus, is_active)
  - Implement getter methods on BusinessEvent class (get_revenue_multiplier, get_immediate_cost, requires_player_action)
  - _Requirements: 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 4.1, 4.2, 4.3, 4.4, 8.2, 8.3, 8.4, 8.5, 13.1, 13.2, 13.3, 13.4_

- [ ]* 1.1 Write property test for data model initialization
  - **Property 1: Business creation with sufficient funds**
  - **Validates: Requirements 1.1, 1.7**

- [ ] 2. Implement Business Repository (data access layer)
  - Create BusinessRepository class with methods: save_business, load_business, load_user_businesses, delete_business
  - Implement update_user_funds and get_user_funds methods
  - Implement JSON serialization for Business objects (serialize employees, upgrades, events, all fields)
  - Implement JSON deserialization for Business objects (reconstruct all fields correctly)
  - Handle database connection and error handling with try-catch blocks
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [ ]* 2.1 Write property test for data persistence round-trip
  - **Property 20: Data persistence round-trip**
  - **Validates: Requirements 11.3, 11.4**

- [ ]* 2.2 Write property test for immediate persistence
  - **Property 21: Immediate data persistence**
  - **Validates: Requirements 11.1**

- [ ]* 2.3 Write property test for data loading
  - **Property 22: Data loading on login**
  - **Validates: Requirements 11.2**

- [ ] 3. Implement Employee Manager
  - Create EmployeeManager class with hire_employee method (validate capacity, create employee, update business)
  - Implement fire_employee method (remove employee, remove effects)
  - Implement get_total_daily_salaries method (sum all employee salaries)
  - Implement calculate_employee_effects method (return revenue_multiplier, quality_bonus, rating_bonus)
  - Add capacity validation logic (check against business max_employees)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 13.5_

- [ ]* 3.1 Write property test for employee hiring within capacity
  - **Property 3: Employee hiring within capacity**
  - **Validates: Requirements 2.1, 2.2, 2.3**

- [ ]* 3.2 Write property test for employee hiring beyond capacity
  - **Property 4: Employee hiring beyond capacity rejected**
  - **Validates: Requirements 2.4, 13.5**

- [ ]* 3.3 Write property test for employee firing
  - **Property 5: Employee firing removes effects**
  - **Validates: Requirements 2.5**

- [ ] 4. Implement Inventory Manager
  - Create InventoryManager class with purchase_inventory method (validate funds, deduct cost, increase inventory, cap at 100%)
  - Implement decrease_daily_inventory method (decrease by 10%)
  - Implement is_low_inventory method (check if < 20%)
  - Implement get_inventory_penalty method (return 0.5 if low, 1.0 otherwise)
  - Implement track_low_inventory_days method (count consecutive low inventory days)
  - Implement apply_rating_penalty_for_low_inventory method (decrease rating by 0.5 if 3+ days)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 14.5_

- [ ]* 4.1 Write property test for daily inventory consumption
  - **Property 6: Daily inventory consumption**
  - **Validates: Requirements 3.1**

- [ ]* 4.2 Write property test for inventory purchase
  - **Property 7: Inventory purchase increases level**
  - **Validates: Requirements 3.3, 3.4**

- [ ]* 4.3 Write property test for inventory purchase with insufficient funds
  - **Property 8: Inventory purchase with insufficient funds rejected**
  - **Validates: Requirements 3.5**

- [ ]* 4.4 Write property test for low inventory revenue penalty
  - **Property 16: Low inventory revenue penalty**
  - **Validates: Requirements 3.2**

- [ ] 5. Implement Upgrade Manager
  - Create UpgradeManager class with purchase_upgrade method (validate funds, check duplicates for permanent upgrades, deduct cost, add upgrade)
  - Implement get_active_upgrades method (filter by is_active, check expiration)
  - Implement process_upgrade_expirations method (mark expired upgrades as inactive)
  - Implement calculate_upgrade_effects method (return revenue_multiplier, rating_bonus)
  - Handle temporary upgrades with expiration tracking (set expires_at for Advertising)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ]* 5.1 Write property test for upgrade purchase
  - **Property 9: Upgrade purchase with sufficient funds**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [ ]* 5.2 Write property test for upgrade purchase with insufficient funds
  - **Property 10: Upgrade purchase with insufficient funds rejected**
  - **Validates: Requirements 4.5**

- [ ]* 5.3 Write property test for duplicate permanent upgrade
  - **Property 11: Duplicate permanent upgrade rejected**
  - **Validates: Requirements 4.6**

- [ ]* 5.4 Write property test for temporary upgrade expiration
  - **Property 12: Temporary upgrade expiration**
  - **Validates: Requirements 4.7, 8.7**

- [ ] 6. Implement Event Manager
  - Create EventManager class with trigger_random_events method (use probabilities from EVENT_CONFIGS, generate random events)
  - Implement get_active_events method (filter by is_resolved and expiration)
  - Implement process_event_expirations method (mark expired events as inactive)
  - Implement resolve_event method (handle player actions like repair payment, mark as resolved)
  - Implement calculate_event_effects method (return revenue_multiplier, immediate_costs, closure_days)
  - Implement apply_event_to_rating method (apply rating penalties from events like health inspection)
  - Handle event outcomes (fine vs closure for health inspection, random selection)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 14.6_

- [ ]* 6.1 Write property test for event probability distribution
  - **Property 17: Event probability distribution**
  - **Validates: Requirements 8.1**

- [ ] 7. Implement Revenue Calculator
  - Create RevenueCalculator class with calculate_daily_revenue method
  - Implement revenue formula: base_revenue × (rating / 3.0) × employee_multipliers × upgrade_multipliers × event_multipliers × inventory_penalty
  - Get employee multipliers from EmployeeManager.calculate_employee_effects
  - Get upgrade multipliers from UpgradeManager.calculate_upgrade_effects
  - Get event multipliers from EventManager.calculate_event_effects
  - Get inventory penalty from InventoryManager.get_inventory_penalty
  - Implement calculate_daily_expenses method: base_rent + employee_salaries
  - Implement calculate_net_profit method: revenue - expenses
  - _Requirements: 5.1, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 6.1, 6.6, 7.1, 3.2_

- [ ]* 7.1 Write property test for daily revenue calculation
  - **Property 13: Daily revenue calculation**
  - **Validates: Requirements 5.1, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 3.2**

- [ ]* 7.2 Write property test for daily expenses calculation
  - **Property 14: Daily expenses calculation**
  - **Validates: Requirements 6.1, 6.6, 2.6**

- [ ]* 7.3 Write property test for net profit and fund update
  - **Property 15: Net profit calculation and fund update**
  - **Validates: Requirements 7.1, 7.2, 7.3**

- [ ] 8. Implement Business Manager (core orchestrator)
  - Create BusinessManager class with create_business method (validate funds, deduct cost, initialize business with defaults, save to DB)
  - Implement get_user_businesses and get_business methods (load from repository)
  - Implement sell_business method (calculate 50% of total investment, add to funds, delete business)
  - Implement process_daily_operations method (for each business: decrease inventory, calculate revenue/expenses, apply event effects, update funds, trigger new events)
  - Integrate all manager classes (EmployeeManager, InventoryManager, UpgradeManager, EventManager, RevenueCalculator)
  - Handle achievement unlocking (Businessman at 100k profit, Tycoon for Restaurant Chain)
  - _Requirements: 1.1, 1.6, 1.7, 9.1, 9.2, 9.3, 10.1, 10.3, 10.4_

- [ ]* 8.1 Write property test for business creation with insufficient funds
  - **Property 2: Business creation with insufficient funds rejected**
  - **Validates: Requirements 1.6**

- [ ]* 8.2 Write property test for business sale
  - **Property 18: Business sale calculation**
  - **Validates: Requirements 9.1, 9.2, 9.3**

- [ ]* 8.3 Write property test for daily operations processing
  - **Property 19: Daily operations processing**
  - **Validates: Requirements 10.1**

- [ ] 9. Checkpoint - Ensure all business logic tests pass
  - Run all property-based tests with 100 iterations
  - Run all unit tests for specific examples
  - Verify all 25 correctness properties pass
  - Ask the user if questions arise

- [x] 10. Implement API endpoints
  - [x] 10.1 Create POST /api/business/create endpoint (accept business_type, call BusinessManager.create_business, return business data or error)
    - Add authentication check (return 401 if not authenticated)
    - Add input validation (return 400 if invalid business_type)
    - _Requirements: 12.1, 12.9, 12.10_
  
  - [x] 10.2 Create POST /api/business/hire endpoint (accept business_id and employee_type, call EmployeeManager.hire_employee, return updated business or error)
    - Add authentication and ownership check
    - Add input validation
    - _Requirements: 12.2, 12.9, 12.10_
  
  - [x] 10.3 Create POST /api/business/fire endpoint (accept business_id and employee_id, call EmployeeManager.fire_employee, return updated business or error)
    - Add authentication and ownership check
    - Add input validation
    - _Requirements: 12.3, 12.9, 12.10_
  
  - [x] 10.4 Create POST /api/business/buy-inventory endpoint (accept business_id, call InventoryManager.purchase_inventory, return updated business or error)
    - Add authentication and ownership check
    - Add input validation
    - _Requirements: 12.4, 12.9, 12.10_
  
  - [x] 10.5 Create POST /api/business/upgrade endpoint (accept business_id and upgrade_type, call UpgradeManager.purchase_upgrade, return updated business or error)
    - Add authentication and ownership check
    - Add input validation
    - _Requirements: 12.5, 12.9, 12.10_
  
  - [x] 10.6 Create GET /api/business/list endpoint (call BusinessManager.get_user_businesses, return all businesses with stats)
    - Add authentication check
    - Calculate current revenue, expenses, net profit for each business
    - _Requirements: 12.6, 12.10_
  
  - [x] 10.7 Create POST /api/business/sell endpoint (accept business_id, call BusinessManager.sell_business, return sale confirmation and updated funds)
    - Add authentication and ownership check
    - Add input validation
    - _Requirements: 12.7, 12.9, 12.10_
  
  - [x] 10.8 Create POST /api/business/repair endpoint (accept business_id, call EventManager.resolve_event with repair action, return updated business)
    - Add authentication and ownership check
    - Add input validation
    - _Requirements: 12.8, 12.9, 12.10_

- [ ]* 10.9 Write unit tests for API endpoints
  - Test each endpoint with valid inputs (return 200 and correct data)
  - Test each endpoint with invalid inputs (return 400 with error message)
  - Test each endpoint without authentication (return 401)
  - Test ownership validation (return 403 if user doesn't own business)
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 12.10_

- [ ]* 10.10 Write property test for API error handling
  - **Property 23: API error handling for invalid data**
  - **Validates: Requirements 12.9**

- [ ]* 10.11 Write property test for API authentication
  - **Property 24: API authentication enforcement**
  - **Validates: Requirements 12.10**

- [x] 11. Integrate with main game day transition
  - Locate the existing day transition logic in the main game code
  - Add call to BusinessManager.process_daily_operations during day transition
  - Ensure business operations happen before other daily calculations
  - Update player funds after business processing
  - _Requirements: 10.1_

- [ ] 12. Implement frontend UI components
  - [ ] 12.1 Create business list view component (display all businesses with type, rating, daily profit, inventory level)
    - Fetch data from GET /api/business/list
    - Display business cards with key stats
    - Add "Create Business" button
    - _Requirements: 15.1_
  
  - [ ] 12.2 Create business detail view component (display employees, upgrades, active events, revenue breakdown, expense breakdown)
    - Fetch detailed business data
    - Display all business information in organized sections
    - _Requirements: 15.2_
  
  - [ ] 12.3 Create action buttons component (hire employee, buy inventory, purchase upgrade, sell business)
    - Add buttons for all available actions
    - Disable buttons when insufficient funds (show required amount)
    - Disable buttons when capacity limits reached (show reason)
    - Call appropriate API endpoints on button click
    - _Requirements: 15.3, 15.4, 15.5_
  
  - [ ] 12.4 Create business creation modal (select business type, show cost, confirm creation)
    - Display all business types with costs and descriptions
    - Validate funds before allowing creation
    - Call POST /api/business/create on confirmation
    - _Requirements: 1.1, 1.6_
  
  - [ ] 12.5 Create event notification component (display active events with icon, description, remaining duration)
    - Show event cards for all active events
    - Display countdown for temporary events
    - Add action buttons for events requiring player action (e.g., repair)
    - _Requirements: 15.6_
  
  - [ ] 12.6 Add business section to main game navigation
    - Add "Business" tab/button to main menu
    - Show total business count and total daily profit in profile
    - _Requirements: 10.2_

- [ ]* 12.7 Write integration tests for frontend-backend interaction
  - Test business creation flow (UI → API → DB → UI update)
  - Test employee hiring flow
  - Test inventory purchase flow
  - Test upgrade purchase flow
  - Test business sale flow
  - Test event resolution flow

- [ ] 13. Implement achievement system integration
  - Add "Businessman" achievement (unlock at 100,000₽ total net profit)
  - Add "Tycoon" achievement (unlock when owning Restaurant Chain)
  - Update achievement checking logic in BusinessManager.process_daily_operations
  - Display achievement notifications in UI
  - _Requirements: 10.3, 10.4_

- [ ] 14. Add rating system logic
  - Implement rating changes in EmployeeManager (Chef hire/fire: ±0.5 stars)
  - Implement rating changes in UpgradeManager (Renovation: +1 star)
  - Implement rating changes in InventoryManager (3+ days low inventory: -0.5 stars)
  - Implement rating changes in EventManager (health inspection fine: -1 star)
  - Ensure rating always stays within [1.0, 5.0] bounds
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_

- [ ]* 14.1 Write property test for rating bounds enforcement
  - **Property 25: Rating bounds enforcement**
  - **Validates: Requirements 14.2, 14.3, 14.4, 14.5, 14.6**

- [ ] 15. Write unit tests for specific examples
  - Test Kiosk creation with exact cost (50,000₽)
  - Test Cafe creation with exact cost (300,000₽)
  - Test Restaurant creation with exact cost (1,000,000₽)
  - Test Restaurant Chain creation with exact cost (5,000,000₽)
  - Test Chef employee effects (5,000₽ salary, +30% quality, +0.5 rating)
  - Test Cashier employee effects (3,000₽ salary, +20% service speed)
  - Test Manager employee effects (8,000₽ salary, +25% revenue)
  - Test New Menu upgrade (50,000₽, +30% revenue)
  - Test Delivery upgrade (80,000₽, +50% revenue)
  - Test Renovation upgrade (100,000₽, +1 star rating)
  - Test Advertising upgrade (30,000₽, +20% revenue for 7 days)
  - Test Health Inspection event (fine or closure outcomes)
  - Test Competitor Opens event (-20% revenue for 14 days)
  - Test Viral Post event (+50% revenue for 3 days)
  - Test Equipment Breakdown event (20,000₽ repair, -30% revenue until fixed)
  - Test Kiosk max employees (2)
  - Test Cafe max employees (4)
  - Test Restaurant max employees (6)
  - Test Restaurant Chain max employees (10)
  - Test Businessman achievement unlock
  - Test Tycoon achievement unlock
  - _Requirements: 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 4.1, 4.2, 4.3, 4.4, 8.2, 8.3, 8.4, 8.5, 8.6, 10.3, 10.4, 13.1, 13.2, 13.3, 13.4, 14.4_

- [ ] 16. Final checkpoint - Comprehensive testing
  - Run all property-based tests with 1000 iterations
  - Run all unit tests
  - Run all integration tests
  - Test complete day cycle with multiple businesses
  - Test edge cases: inventory at 20%, rating at 1.0 and 5.0, capacity limits
  - Verify all 25 correctness properties pass
  - Ensure all tests pass, ask the user if questions arise

- [ ] 17. Code review and optimization
  - Review all code for clarity and maintainability
  - Optimize database queries (batch operations where possible)
  - Add logging for debugging (business operations, event triggers, errors)
  - Add code comments for complex logic (revenue calculation, event probability)
  - Ensure error messages are user-friendly and descriptive

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties (minimum 100 iterations)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end flows
- Checkpoints ensure incremental validation at key milestones
- The implementation follows a bottom-up approach: data → logic → API → UI
- All business logic is testable independently of API and UI layers

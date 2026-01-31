# Tasks: Career Progression System

## Task 1: Create Career System Configuration
- [x] 1.1 Create `career_config.py` with all 6 professions definitions
- [x] 1.2 Define career ladders for each profession (4 levels each)
- [x] 1.3 Define promotion requirements for each level
- [x] 1.4 Define salary scales and bonuses

## Task 2: Implement Core Career Manager
- [x] 2.1 Create `career_system.py` with CareerManager class
- [x] 2.2 Implement `select_profession()` method
- [x] 2.3 Implement `get_career_info()` method
- [x] 2.4 Implement `calculate_work_income()` with profession bonuses
- [x] 2.5 Implement `record_work_action()` to track progress

## Task 3: Implement Promotion Logic
- [x] 3.1 Create PromotionEvaluator class
- [x] 3.2 Implement requirement checking (work actions, skills, money, days)
- [x] 3.3 Implement `check_promotion_eligibility()` method
- [x] 3.4 Implement `promote_player()` method
- [x] 3.5 Add promotion history tracking

## Task 4: Database Integration
- [x] 4.1 Create career_state table migration
- [x] 4.2 Implement CareerState data class
- [x] 4.3 Add database save/load methods
- [x] 4.4 Add career data to user initialization

## Task 5: Flask API Endpoints
- [x] 5.1 Create `/api/select_profession` endpoint
- [x] 5.2 Create `/api/career_info` endpoint
- [x] 5.3 Create `/api/promote` endpoint
- [x] 5.4 Update `/api/work` endpoint to use career system
- [x] 5.5 Update `/api/user` endpoint to include career data

## Task 6: Frontend - Profession Selection Modal
- [x] 6.1 Create profession selection modal HTML
- [x] 6.2 Add profession cards with icons and descriptions
- [x] 6.3 Implement profession selection JavaScript
- [x] 6.4 Show modal after name input, before trait selection
- [x] 6.5 Style profession cards with gradients and effects

## Task 7: Frontend - Career Display
- [x] 7.1 Update job info card to show career level
- [x] 7.2 Create career progress modal
- [x] 7.3 Display promotion requirements with progress bars
- [x] 7.4 Add "Career" button to main interface
- [x] 7.5 Show promotion notification when eligible

## Task 8: Integration with Existing Systems
- [ ] 8.1 Update work() function to use career salary
- [ ] 8.2 Integrate with skills system for requirements
- [ ] 8.3 Update statistics to show career info
- [ ] 8.4 Update leaderboard to show career levels

## Task 9: Testing
- [ ] 9.1 Write unit tests for CareerManager
- [ ] 9.2 Write unit tests for PromotionEvaluator
- [ ] 9.3 Write property-based tests for promotion logic
- [ ] 9.4 Test all 6 professions and 4 levels each
- [ ] 9.5 Test edge cases (max level, invalid profession)

## Task 10: Documentation and Polish
- [ ] 10.1 Add career system to README
- [ ] 10.2 Create career guide for players
- [ ] 10.3 Add tooltips and help text
- [ ] 10.4 Balance testing and adjustments
- [ ] 10.5 Final QA and bug fixes

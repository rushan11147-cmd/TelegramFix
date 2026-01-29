# Implementation Plan: Entertainment System

## Overview

This plan implements a centralized entertainment system with three mini-games (Roulette, Dice, Crash) that replace the standalone roulette button. The implementation follows an incremental approach: core engines → API endpoints → statistics → frontend integration.

## Tasks

- [ ] 1. Create entertainment system module structure
  - Create `entertainment_system.py` file in project root
  - Define base classes and imports
  - Set up module constants (bet limits, probabilities, payouts)
  - _Requirements: 1.1, 2.1, 3.1, 4.1_

- [ ] 2. Implement Roulette Engine
  - [ ] 2.1 Create RouletteEngine class with spin logic
    - Implement emoji reel generation
    - Implement probability-based outcome determination (60% loss, 25% x2, 10% x5, 5% x10)
    - Calculate payouts and mood changes
    - _Requirements: 2.2, 2.3, 2.5, 2.6, 2.7_
  
  - [ ] 2.2 Write property test for roulette probability distribution
    - **Property 3: Roulette Probability Distribution**
    - **Validates: Requirements 2.5**
  
  - [ ] 2.3 Write unit tests for roulette edge cases
    - Test all bet amounts (100, 500, 1000)
    - Test mood changes for wins and losses
    - _Requirements: 2.3, 2.6, 2.7_

- [ ] 3. Implement Dice Engine
  - [ ] 3.1 Create DiceEngine class with roll logic
    - Implement two-dice rolling (1-6 each)
    - Implement three betting choices (low, seven, high)
    - Calculate payouts (x2.5 for low/high, x6 for seven)
    - Implement luck skill bonus (+5% per level)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.9_
  
  - [ ] 3.2 Write property test for dice roll validity
    - **Property 6: Dice Roll Validity**
    - **Validates: Requirements 3.1**
  
  - [ ] 3.3 Write property test for dice bet validation
    - **Property 7: Dice Bet Validation**
    - **Validates: Requirements 3.2**
  
  - [ ] 3.4 Write property tests for dice payouts
    - **Property 8: Dice Low Range Payout**
    - **Property 9: Dice Seven Payout**
    - **Property 10: Dice High Range Payout**
    - **Validates: Requirements 3.4, 3.5, 3.6**
  
  - [ ] 3.5 Write property test for luck skill bonus
    - **Property 11: Dice Luck Skill Bonus**
    - **Validates: Requirements 3.9**

- [ ] 4. Implement Crash Engine
  - [ ] 4.1 Create CrashEngine class with crash logic
    - Implement crash point determination (x1.1 to x10.0)
    - Implement luck skill influence on crash distribution
    - Calculate payouts based on cash out multiplier
    - Handle crash vs cash out scenarios
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6, 4.9_
  
  - [ ] 4.2 Write property test for crash bet validation
    - **Property 12: Crash Bet Validation**
    - **Validates: Requirements 4.2**
  
  - [ ] 4.3 Write property test for crash point range
    - **Property 14: Crash Point Range**
    - **Validates: Requirements 4.4**
  
  - [ ] 4.4 Write property tests for crash payouts
    - **Property 15: Crash Cash Out Payout**
    - **Property 16: Crash Loss on Crash**
    - **Validates: Requirements 4.5, 4.6**
  
  - [ ] 4.5 Write property test for luck skill distribution
    - **Property 17: Crash Luck Skill Distribution**
    - **Validates: Requirements 4.9**

- [ ] 5. Implement Statistics Manager
  - [ ] 5.1 Create StatisticsManager class
    - Implement game recording (game type, outcome, amounts)
    - Implement statistics calculation (wins, losses, net profit)
    - Implement statistics retrieval and formatting
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ] 5.2 Write property tests for statistics tracking
    - **Property 24: Statistics Recording**
    - **Property 25: Statistics Calculation**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.5**

- [ ] 6. Checkpoint - Ensure all game engines work independently
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement Entertainment Manager
  - [ ] 7.1 Create EntertainmentManager class
    - Implement main play_game() method
    - Implement bet validation logic
    - Implement balance update logic with database persistence
    - Implement mood update logic with clamping (0-100)
    - Integrate all three game engines
    - _Requirements: 5.1, 6.1, 6.2, 6.3, 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ] 7.2 Write property tests for balance management
    - **Property 2: Balance Deduction on Bet**
    - **Property 5: Balance Update Persistence**
    - **Property 22: Balance Verification Before Bet**
    - **Property 23: Insufficient Balance Rejection**
    - **Validates: Requirements 2.4, 2.8, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6**
  
  - [ ] 7.3 Write property tests for mood management
    - **Property 4: Mood Changes on Game Outcomes**
    - **Property 19: Mood Update After Game**
    - **Property 20: Mood Persistence**
    - **Validates: Requirements 2.6, 2.7, 3.7, 3.8, 4.7, 4.8, 6.1, 6.2, 6.3**
  
  - [ ] 7.4 Write property test for luck skill retrieval
    - **Property 18: Luck Skill Retrieval**
    - **Validates: Requirements 5.1**

- [ ] 8. Implement API endpoints
  - [ ] 8.1 Create /api/entertainment/roulette endpoint
    - Accept POST requests with user_id and bet
    - Validate inputs and call EntertainmentManager
    - Return JSON response with game result and updated state
    - _Requirements: 9.1, 9.5, 9.6, 9.7_
  
  - [ ] 8.2 Create /api/entertainment/dice endpoint
    - Accept POST requests with user_id, bet, and choice
    - Validate inputs and call EntertainmentManager
    - Return JSON response with dice results and updated state
    - _Requirements: 9.2, 9.5, 9.6, 9.7_
  
  - [ ] 8.3 Create /api/entertainment/crash endpoint
    - Accept POST requests with user_id, bet, and cash_out_multiplier
    - Validate inputs and call EntertainmentManager
    - Return JSON response with crash results and updated state
    - _Requirements: 9.3, 9.5, 9.6, 9.7_
  
  - [ ] 8.4 Create /api/entertainment/stats endpoint
    - Accept GET requests with user_id
    - Return JSON response with game statistics
    - _Requirements: 9.4_
  
  - [ ] 8.5 Write unit tests for API endpoints
    - Test successful requests for all endpoints
    - Test error responses (400, 404, 500)
    - Test input validation
    - _Requirements: 9.5, 9.6, 9.7_
  
  - [ ] 8.6 Write property tests for API validation
    - **Property 27: API Error Codes**
    - **Property 28: API Response Structure**
    - **Property 29: API Input Validation**
    - **Validates: Requirements 9.5, 9.6, 9.7**

- [ ] 9. Migrate existing roulette endpoint
  - [ ] 9.1 Update /api/play_roulette to use new EntertainmentManager
    - Maintain backward compatibility
    - Redirect to new roulette engine
    - Update response format if needed
    - _Requirements: 2.1_
  
  - [ ] 9.2 Write integration tests for roulette migration
    - Test that old endpoint still works
    - Test that behavior matches new endpoint
    - _Requirements: 2.1_

- [ ] 10. Checkpoint - Ensure all backend functionality works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Create entertainment menu frontend
  - [ ] 11.1 Create entertainment modal HTML template
    - Create modal structure with three game buttons
    - Add "Развлечения 🎰" button to main game interface
    - Remove old "Рулетка" button
    - Display balance and mood in menu
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 10.1_
  
  - [ ] 11.2 Add JavaScript for menu navigation
    - Implement modal open/close handlers
    - Implement game selection handlers
    - Update balance and mood display
    - _Requirements: 1.4_

- [ ] 12. Create roulette game frontend
  - [ ] 12.1 Create roulette modal HTML
    - Create three emoji reels display
    - Add bet selection buttons (100₽, 500₽, 1000₽)
    - Add spin button
    - Display balance and mood
    - _Requirements: 2.2, 2.3, 10.6_
  
  - [ ] 12.2 Add JavaScript for roulette game
    - Implement API call to /api/entertainment/roulette
    - Implement reel animation
    - Display game results and feedback messages
    - Update balance and mood after game
    - _Requirements: 2.8, 10.7_

- [ ] 13. Create dice game frontend
  - [ ] 13.1 Create dice modal HTML
    - Create dice display area
    - Add bet amount input (100-1000₽)
    - Add three choice buttons (Низкие, Семерка, Высокие)
    - Add roll button
    - Display balance and mood
    - _Requirements: 3.2, 3.3, 10.6_
  
  - [ ] 13.2 Add JavaScript for dice game
    - Implement API call to /api/entertainment/dice
    - Implement dice rolling animation
    - Display game results and feedback messages
    - Update balance and mood after game
    - _Requirements: 3.10, 10.7_

- [ ] 14. Create crash game frontend
  - [ ] 14.1 Create crash modal HTML
    - Create multiplier display area
    - Add bet amount input (100-5000₽)
    - Add start button and cash out button
    - Display balance and mood
    - _Requirements: 4.1, 4.2, 10.6_
  
  - [ ] 14.2 Add JavaScript for crash game
    - Implement API call to /api/entertainment/crash
    - Implement multiplier animation (growing from x1.0)
    - Handle cash out button click
    - Display game results and feedback messages
    - Update balance and mood after game
    - _Requirements: 4.3, 4.10, 10.7_

- [ ] 15. Create statistics display frontend
  - [ ] 15.1 Add statistics section to entertainment menu
    - Display wins, losses, and net profit for each game
    - Display total statistics across all games
    - Add refresh button
    - _Requirements: 8.4_
  
  - [ ] 15.2 Add JavaScript for statistics
    - Implement API call to /api/entertainment/stats
    - Format and display statistics data
    - Update statistics after each game
    - _Requirements: 8.4_

- [ ] 16. Add CSS styling and animations
  - [ ] 16.1 Style entertainment menu and modals
    - Create consistent modal styling
    - Add button hover effects
    - Ensure responsive design for mobile
    - _Requirements: 10.8_
  
  - [ ] 16.2 Implement game animations
    - Roulette reel spinning animation
    - Dice rolling animation
    - Crash multiplier growth animation
    - Win/loss feedback animations
    - _Requirements: 2.2, 3.10, 4.10_

- [ ] 17. Final integration and testing
  - [ ] 17.1 Test complete user flows
    - Test playing each game from menu
    - Test balance updates across games
    - Test mood updates across games
    - Test statistics accumulation
    - _Requirements: All_
  
  - [ ] 17.2 Write integration tests
    - Test complete game flows (bet → play → update → persist)
    - Test multiple games in sequence
    - Test error handling flows
    - _Requirements: All_

- [ ] 18. Final checkpoint - Ensure everything works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Frontend tasks focus on UI/UX and integration with backend APIs
- The implementation maintains backward compatibility with existing roulette endpoint

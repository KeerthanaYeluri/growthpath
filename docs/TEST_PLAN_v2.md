# GrowthPath v2.0 — Test Plan
# FAANG Mock Interview Simulator

**Aligned with:** PRD v2, Sprint Plan v2
**Test Framework:** pytest (backend), manual + browser-based (frontend POC)
**Coverage Target:** 85%+ backend, critical path E2E for frontend
**Team:** Renu (backend tests), Anand (frontend tests + E2E)

---

## 1. Test Strategy

### Test Pyramid

```
         ┌─────────┐
         │  E2E    │  — 5-10 critical journey tests
         │ (Manual)│  — Full mock interview flow in browser
         ├─────────┤
         │ Integra-│  — 15-20 API integration tests
         │  tion   │  — Multi-endpoint flows
         ├─────────┤
         │  Unit   │  — 80+ unit tests
         │  Tests  │  — Core logic, engines, calculations
         └─────────┘
```

### What We Test vs What We Don't

| Test | Don't Test |
|------|-----------|
| ELO calculation logic | LLM output quality (non-deterministic) |
| Probe tree branching logic | Browser Speech API (vendor) |
| Scoring engine (Thinking + Accuracy) | Tailwind CSS rendering |
| Company profile configurations | Third-party CDN availability |
| Gap map generation | Whisper/Vosk model accuracy |
| Path reordering algorithm | |
| Hiring committee decision logic | |
| API endpoint contracts | |
| Auth + JWT flows | |
| Data persistence + retrieval | |

---

## 2. Unit Tests — By Sprint

### Sprint 1: Foundation (ELO, Company Profiles, Gap Map)

#### 2.1.1 ELO Rating Module (`test_elo.py`)

```
test_starting_elo_junior_returns_1000
test_starting_elo_mid_returns_1200
test_starting_elo_senior_returns_1400
test_starting_elo_staff_returns_1600

test_elo_gain_strong_answer_hard_question
test_elo_gain_average_answer_matching_question
test_elo_loss_weak_answer_easy_question
test_elo_no_negative (ELO never goes below 0)
test_elo_adjustment_range (gains between +5 and +50, losses between -20 and -40)

test_sub_elo_coding_updates_independently
test_sub_elo_system_design_updates_independently
test_sub_elo_behavioral_updates_independently
test_sub_elo_domain_updates_independently

test_targeted_practice_elo_multiplier_0_25x
test_full_mock_elo_multiplier_1x

test_elo_history_records_each_change
test_elo_history_includes_timestamp_and_source
```

#### 2.1.2 Company Profiles (`test_company_profiles.py`)

```
test_google_profile_exists
test_apple_profile_exists
test_google_profile_has_all_5_rounds
test_apple_profile_has_all_5_rounds
test_google_round_weights_sum_to_100
test_apple_round_weights_sum_to_100

test_google_hiring_bar_l3_is_1400
test_google_hiring_bar_l4_is_1600
test_google_hiring_bar_l5_is_1800
test_google_hiring_bar_l6_is_2000
test_apple_hiring_bar_l3_is_1350
test_apple_hiring_bar_l5_is_1750

test_google_persona_prompt_contains_googleyness
test_apple_persona_prompt_contains_design_thinking

test_google_system_design_weight_is_highest
test_apple_behavioral_includes_craftsmanship

test_get_company_profile_invalid_company_returns_error
test_get_hiring_bar_invalid_level_returns_error
```

#### 2.1.3 Gap Map Engine (`test_gap_map.py`)

```
test_gap_map_identifies_strength_areas
test_gap_map_identifies_gap_areas
test_gap_map_identifies_cross_cutting_concerns
test_gap_map_python_backend_dev_has_frontend_gap
test_gap_map_fullstack_has_fewer_gaps
test_gap_map_empty_tech_stack_all_gaps
test_gap_map_returns_role_specific_demands
test_gap_map_google_l5_backend_demands
test_gap_map_apple_l5_frontend_demands
test_gap_map_level_affects_demand_depth (L3 vs L6 demands different things)
```

#### 2.1.4 User Model Extension (`test_user_model.py`)

```
test_register_with_target_company
test_register_with_target_role
test_register_with_target_level
test_register_missing_company_returns_error
test_register_missing_role_returns_error
test_register_invalid_company_returns_error
test_register_invalid_level_returns_error
test_register_stores_all_new_fields
test_profile_returns_company_role_level
```

---

### Sprint 2: Quick Assessment

#### 2.2.1 Quick Assessment Engine (`test_quick_assessment.py`)

```
test_generates_5_to_10_questions
test_questions_are_phone_screen_format
test_questions_tagged_with_archetype_pattern
test_questions_match_target_company_profile
test_questions_match_target_level_difficulty
test_no_duplicate_questions_in_assessment
test_questions_cover_multiple_archetype_patterns

test_start_assessment_creates_session
test_submit_answer_records_response
test_submit_all_answers_completes_assessment
test_cannot_start_second_assessment_while_active
```

#### 2.2.2 Answer Quality Classifier (`test_answer_classifier.py`)

```
test_strong_answer_classified_gte_70_percent
test_average_answer_classified_40_to_69_percent
test_weak_answer_classified_lt_40_percent
test_empty_answer_classified_as_weak
test_keyword_matching_scores_correctly
test_semantic_similarity_contributes_to_score
test_classifier_handles_voice_transcript_noise
test_classifier_handles_code_answers
```

#### 2.2.3 Dual Rating Scorer (`test_dual_rating.py`)

```
test_thinking_process_weight_is_60_percent
test_accuracy_weight_is_40_percent
test_thinking_subscore_clarifying_questions
test_thinking_subscore_multiple_approaches
test_thinking_subscore_tradeoff_awareness
test_thinking_subscore_structured_communication
test_accuracy_subscore_correctness
test_accuracy_subscore_completeness
test_combined_score_calculation
test_perfect_score_equals_max_elo_gain
test_zero_score_equals_max_elo_loss
```

#### 2.2.4 Path Generation from Failures (`test_path_from_failures.py`)

```
test_path_generated_from_weak_patterns
test_weakest_areas_appear_first_in_path
test_strength_areas_appear_later_in_path
test_cross_cutting_concerns_included
test_path_includes_all_gap_map_areas
test_path_length_reasonable_for_level
test_path_content_depth_matches_level
```

---

### Sprint 3: Mock Interview Engine

#### 2.3.1 Mock Interview Structure (`test_mock_engine.py`)

```
test_mock_creates_5_rounds
test_round_1_is_phone_screen
test_round_2_is_system_design
test_round_3_is_behavioral
test_round_4_is_domain_specific
test_round_5_is_bar_raiser

test_total_duration_is_30_minutes
test_round_time_allocation_sums_to_30
test_phone_screen_gets_10_minutes
test_system_design_gets_8_minutes
test_behavioral_gets_5_minutes
test_domain_gets_4_minutes
test_bar_raiser_gets_3_minutes

test_round_transition_auto_advances_on_timeout
test_round_transition_advances_on_completion
test_cannot_go_back_to_previous_round
test_mock_ends_after_round_5

test_enforce_1_mock_per_day
test_second_mock_same_day_rejected
test_targeted_practice_unlimited_per_day
test_mock_resets_at_midnight_user_timezone
```

#### 2.3.2 Question Generation per Round (`test_round_questions.py`)

```
test_phone_screen_generates_coding_questions
test_system_design_generates_architecture_question
test_behavioral_generates_star_questions
test_domain_generates_role_specific_questions
test_bar_raiser_generates_cross_functional_questions

test_questions_match_company_profile_weights
test_questions_match_target_level
test_daily_regeneration_produces_different_questions
test_questions_tagged_with_archetype_patterns
```

#### 2.3.3 Hybrid Answer Mode (`test_answer_mode.py`)

```
test_phone_screen_mode_is_code_editor
test_system_design_mode_is_voice
test_behavioral_mode_is_voice
test_domain_mode_is_hybrid
test_bar_raiser_mode_is_voice
test_hybrid_mode_allows_both_voice_and_text
test_mid_answer_switch_voice_to_text_allowed
test_mid_answer_switch_text_to_voice_allowed
```

#### 2.3.4 Session State Management (`test_session_state.py`)

```
test_session_state_saved_on_each_answer
test_session_resumes_from_last_state_on_disconnect
test_session_preserves_round_number
test_session_preserves_remaining_time
test_session_preserves_answers_so_far
test_completed_session_cannot_be_resumed
```

---

### Sprint 4: AI Interviewer + Probe Trees

#### 2.4.1 AI Interviewer Persona (`test_ai_interviewer.py`)

```
test_google_persona_prompt_loads_correctly
test_apple_persona_prompt_loads_correctly
test_persona_maintains_context_across_questions
test_persona_gives_acknowledgment_before_next_question
test_persona_follows_up_on_vague_answers
test_persona_handles_i_dont_know_gracefully

test_hint_system_delivers_hint_on_request
test_hint_system_applies_score_penalty
test_hint_count_tracked_per_question
test_multiple_hints_increase_penalty

test_guardrail_prevents_answer_leakage
test_guardrail_prevents_direct_answer_in_followup
test_guardrail_allows_hints_without_full_answer
```

#### 2.4.2 Dynamic Probe Trees (`test_probe_trees.py`)

```
test_probe_tree_has_5_levels
test_probe_tree_branches_on_strong_answer
test_probe_tree_branches_on_average_answer
test_probe_tree_branches_on_weak_answer

test_strong_branch_increases_difficulty
test_weak_branch_simplifies_question
test_average_branch_guides_toward_answer

test_probe_depth_1_maps_to_low_score
test_probe_depth_3_maps_to_mid_score
test_probe_depth_5_maps_to_high_score

test_probe_tree_generated_by_ai
test_probe_tree_regenerated_daily
test_different_days_produce_different_trees

test_system_design_probe_depth_up_to_5
test_phone_screen_probe_depth_up_to_2
```

#### 2.4.3 Voice Conversation (`test_voice_conversation.py`)

```
test_vad_detects_silence_after_1_5_seconds
test_ai_waits_for_silence_before_responding
test_transcript_saved_for_full_conversation
test_technical_vocabulary_recognized (kubernetes, postgresql, b-tree)
test_mic_quality_warning_shown_when_poor
test_poor_mic_does_not_affect_score
test_voice_to_text_switch_mid_answer
```

---

### Sprint 5: Scoring, ELO Update, Rubric Reveal

#### 2.5.1 Multi-Dimensional Scoring (`test_scoring_engine.py`)

```
test_per_answer_thinking_60_accuracy_40
test_per_round_weighted_average
test_probe_depth_contributes_to_round_score
test_time_management_bonus_for_on_time
test_time_management_penalty_for_overtime
test_hint_usage_reduces_round_score
test_overall_score_across_5_rounds
```

#### 2.5.2 ELO Update Engine (`test_elo_update.py`)

```
test_elo_increases_after_strong_mock
test_elo_decreases_after_weak_mock
test_sub_elos_update_per_round_type
test_elo_change_recorded_in_history
test_targeted_practice_applies_0_25x_multiplier
test_elo_change_display_shows_delta

test_readiness_label_not_ready_below_1200
test_readiness_label_getting_there_1200_1500
test_readiness_label_almost_ready_1500_1750
test_readiness_label_ready_1750_1900
test_readiness_label_interview_ready_above_1900
```

#### 2.5.3 Rubric Reveal (`test_rubric_reveal.py`)

```
test_rubric_generated_per_question
test_rubric_shows_expected_evaluation_points
test_rubric_marks_covered_points
test_rubric_marks_missed_points
test_rubric_counts_n_of_m_covered
test_missed_rubric_items_link_to_learning_content
test_rubric_available_in_replay_mode
```

#### 2.5.4 Pattern Tracking (`test_pattern_tracking.py`)

```
test_archetype_pattern_mastery_tracked
test_pattern_score_updates_across_mocks
test_weak_patterns_identified_correctly
test_strong_patterns_identified_correctly
test_pattern_mastery_visualization_data_correct
test_learning_path_prioritizes_weak_patterns
```

---

### Sprint 6: Hiring Committee + Path Reordering

#### 2.6.1 Hiring Committee (`test_hiring_committee.py`)

```
test_committee_has_3_interviewers
test_each_interviewer_evaluates_assigned_rounds
test_interviewer_gives_hire_or_no_hire
test_interviewer_quotes_specific_moments
test_interviewer_has_name_and_title

test_majority_vote_2_hire_1_no_hire_is_lean_hire
test_majority_vote_1_hire_2_no_hire_is_lean_no_hire
test_unanimous_hire_is_strong_hire
test_unanimous_no_hire_is_strong_no_hire

test_veto_power_critical_round_no_hire_overrides
test_veto_on_system_design_for_google_is_critical
test_veto_on_behavioral_for_apple_is_critical

test_committee_generates_improvement_recommendations
test_committee_verdict_includes_reasoning
```

#### 2.6.2 Path Reordering (`test_path_reorder.py`)

```
test_weak_areas_move_up_2_to_3_positions
test_strong_areas_stay_or_move_down
test_completed_topics_not_reordered
test_reorder_preserves_all_topics (no topics lost)

test_company_weighting_70_percent
test_general_improvement_30_percent
test_google_prioritizes_system_design_weakness
test_apple_prioritizes_design_thinking_weakness

test_completed_topic_resurfaces_if_pattern_drops_below_50
test_resurface_requires_2_consecutive_low_mocks
test_resurface_only_for_related_patterns

test_user_override_manual_reorder
test_manual_reorder_persists_across_sessions

test_company_change_soft_regeneration
test_company_change_keeps_completed_topics
test_company_change_adds_new_company_gaps
test_company_change_reweights_remaining_path
```

---

### Sprint 7: Content + Review

#### 2.7.1 AI Content Generation (`test_content_generation.py`)

```
test_content_generated_for_4_dimensions
test_content_depth_l3_is_fundamentals
test_content_depth_l5_is_architecture
test_content_depth_l6_is_strategy
test_content_format_is_markdown_with_code
test_content_no_video_references

test_weekly_content_refresh_produces_updates
```

#### 2.7.2 Mock Replay (`test_mock_replay.py`)

```
test_replay_loads_full_transcript
test_replay_shows_scores_per_question
test_replay_shows_rubric_reveals
test_replay_does_not_affect_elo
test_replay_does_not_affect_progress

test_score_comparison_across_attempts
test_score_comparison_shows_trend_arrows
```

#### 2.7.3 Interview Ready Detection (`test_interview_ready.py`)

```
test_interview_ready_when_elo_gte_company_bar
test_not_ready_when_elo_below_bar
test_ready_detection_uses_correct_company_bar
test_ready_detection_uses_correct_level_bar
test_ready_triggers_celebration_flag
test_prep_summary_pdf_generated
```

---

### Sprint 8: Polish + Launch

#### 2.8.1 Rate Cards (`test_rate_cards.py`)

```
test_free_tier_exists
test_pro_tier_exists
test_team_tier_exists
test_enterprise_tier_exists
test_free_tier_limits_3_mocks_per_month
test_rate_cards_endpoint_returns_all_tiers
```

#### 2.8.2 Security (`test_security.py`)

```
test_jwt_required_on_protected_endpoints
test_expired_jwt_rejected
test_invalid_jwt_rejected
test_rate_limiting_on_login_endpoint
test_password_stored_as_bcrypt_hash
test_sql_injection_prevented
test_xss_prevented_in_user_inputs
test_cannot_access_other_users_data
test_cannot_access_other_users_elo
test_cannot_access_other_users_mock_results
```

---

## 3. Integration Tests (`test_integration.py`)

### Critical Flows

```
test_flow_register_to_elo_assignment
  Register with Google/L5/Backend → starting ELO = 1400 → gap map generated

test_flow_quick_assessment_to_path_generation
  Start Quick Assessment → answer 5-10 questions → ELO assigned → learning path generated from failures

test_flow_full_mock_to_scorecard
  Start mock → complete 5 rounds → scorecard generated → ELO updated → rubric reveals available

test_flow_mock_to_committee_to_path_reorder
  Complete mock → committee deliberates → HIRE/NO HIRE → path reorders by weakness

test_flow_learn_then_mock_then_improve
  Complete learning topic → take mock → score higher on that topic → ELO increases

test_flow_targeted_practice_reduced_elo
  Take targeted practice → ELO changes by 0.25x multiplier

test_flow_company_change
  Change target from Google to Apple → path soft-regenerates → new hiring bar displayed

test_flow_interview_ready
  ELO reaches company bar → Interview Ready detected → celebration triggered

test_flow_disconnect_and_resume
  Start mock → disconnect mid-round → reconnect → resume from exact state
```

---

## 4. E2E Tests (Manual / Browser-Based)

### Critical User Journeys

| # | Journey | Steps | Expected Result |
|---|---------|-------|----------------|
| E1 | New User First Experience | Register → Quick Assessment → Results → Dashboard | ELO displayed, gap map visible, learning path generated |
| E2 | Full Mock Interview | Dashboard → Start Mock → 5 rounds → Scorecard → Committee | Complete in 30 min, all rounds work, scorecard shows |
| E3 | Voice Answer | Start mock → Behavioral round → speak answer → transcript appears | Voice recorded, transcript accurate, score assigned |
| E4 | Code Answer | Phone Screen round → write code → submit | Code editor works, code evaluated correctly |
| E5 | Mid-Answer Switch | Domain round → start voice → switch to text for code | Seamless switch, both inputs captured |
| E6 | Probe Tree Depth | System Design → strong answer → harder follow-up → deeper | Follow-ups branch correctly, depth tracked |
| E7 | Hint Usage | Get stuck → request hint → penalty shown | Hint delivered, score reduced, hint count shown |
| E8 | Rubric Reveal | Complete question → view rubric | Evaluation points shown with ✅/❌, links to content |
| E9 | Hiring Committee | Complete mock → view committee | 3 interviewers, HIRE/NO HIRE, quotes from mock |
| E10 | Path Reorder | Complete mock with weak System Design → check path | System Design topics moved up in learning path |
| E11 | ELO Progression | Take 3 mocks → check ELO trend | Graph shows ELO over time, sub-ELOs tracked |
| E12 | Mock Replay | Go to history → replay past mock → review transcript | Full replay with scores, rubric, no ELO change |
| E13 | 1 Mock Per Day Limit | Complete mock → try starting another | "Come back tomorrow" message shown |
| E14 | Targeted Practice Unlimited | Complete mock → do 5 targeted practices | All allowed, ELO changes at 0.25x |
| E15 | Interview Ready | Reach ELO ≥ company bar | Confetti, congratulations, PDF download option |

### Cross-Browser Testing

| Browser | Voice API | Code Editor | WebSocket | Priority |
|---------|-----------|-------------|-----------|----------|
| Chrome (latest) | ✅ Test | ✅ Test | ✅ Test | P0 |
| Edge (latest) | ✅ Test | ✅ Test | ✅ Test | P0 |
| Firefox (latest) | ⚠️ Limited Speech API | ✅ Test | ✅ Test | P1 |
| Safari (latest) | ⚠️ Limited Speech API | ✅ Test | ✅ Test | P2 |

---

## 5. AI-Specific Tests

### AI Interviewer Quality

| Test | Method | Pass Criteria |
|------|--------|--------------|
| Persona consistency | Run 10 mock interviews, check persona stays in character | 9/10 stay in character throughout |
| Guardrail effectiveness | Attempt 20 prompts to extract answers | 0/20 leak answers |
| Follow-up relevance | Rate 50 follow-up probes for relevance | 90%+ rated relevant |
| Hint quality | Rate 20 hints for helpfulness without revealing | 85%+ helpful without revealing |
| Probe tree branching | Submit known-quality answers, verify correct branch | 95%+ correct branching |
| Technical accuracy | Check 50 AI evaluations against expert rubric | 80%+ match expert assessment |

### LLM Fallback Testing

| Scenario | Expected Behavior |
|----------|------------------|
| Claude API available | Use Claude |
| Claude API down, OpenAI available | Fallback to OpenAI |
| Claude + OpenAI down, Gemini available | Fallback to Gemini |
| All LLMs down | Graceful error: "Interview service temporarily unavailable" |
| LLM response timeout (>10s) | Retry once, then show fallback message |
| LLM returns malformed JSON | Parse error handled, retry with structured prompt |

---

## 6. Performance Tests

| Metric | Target | How to Test |
|--------|--------|------------|
| API response time (non-LLM) | < 200ms (p95) | Load test with 100 concurrent requests |
| LLM response time | < 3 seconds | Measure across 50 interview exchanges |
| Voice-to-text latency | < 2 seconds | Time from speech end to transcript display |
| Mock interview state save | < 500ms | Measure on each answer submission |
| Dashboard load time | < 1 second | Measure with ELO + gap map + pattern data |
| ELO calculation | < 50ms | Benchmark with 1000 calculations |
| Path reordering | < 200ms | Benchmark with 30-topic path |

---

## 7. Test Schedule — Per Sprint

| Sprint | Tests Added | Running Total |
|--------|------------|---------------|
| S1 | 35 unit (ELO, company, gap map, user model) | 35 |
| S2 | 30 unit (assessment, classifier, dual rating, path) + 2 integration | 67 |
| S3 | 30 unit (mock engine, round questions, answer mode, session state) + 2 integration | 99 |
| S4 | 25 unit (AI interviewer, probe trees, voice) + 1 integration | 125 |
| S5 | 25 unit (scoring, ELO update, rubric, patterns) + 2 integration | 152 |
| S6 | 25 unit (committee, path reorder) + 2 integration | 179 |
| S7 | 15 unit (content, replay, readiness) + 1 integration | 195 |
| S8 | 15 unit (rate cards, security) + 15 E2E manual | 225 |

**Final count: ~210 automated tests + 15 manual E2E journeys**

---

## 8. Test Infrastructure

### Backend Test Setup

```
interview/
├── backend/
│   ├── tests/
│   │   ├── conftest.py           (fixtures: test user, test session, test DB)
│   │   ├── test_elo.py
│   │   ├── test_company_profiles.py
│   │   ├── test_gap_map.py
│   │   ├── test_user_model.py
│   │   ├── test_quick_assessment.py
│   │   ├── test_answer_classifier.py
│   │   ├── test_dual_rating.py
│   │   ├── test_path_from_failures.py
│   │   ├── test_mock_engine.py
│   │   ├── test_round_questions.py
│   │   ├── test_answer_mode.py
│   │   ├── test_session_state.py
│   │   ├── test_ai_interviewer.py
│   │   ├── test_probe_trees.py
│   │   ├── test_voice_conversation.py
│   │   ├── test_scoring_engine.py
│   │   ├── test_elo_update.py
│   │   ├── test_rubric_reveal.py
│   │   ├── test_pattern_tracking.py
│   │   ├── test_hiring_committee.py
│   │   ├── test_path_reorder.py
│   │   ├── test_content_generation.py
│   │   ├── test_mock_replay.py
│   │   ├── test_interview_ready.py
│   │   ├── test_rate_cards.py
│   │   ├── test_security.py
│   │   └── test_integration.py
│   └── pytest.ini
```

### conftest.py Fixtures

```python
# Key fixtures needed:
@pytest.fixture — test_db (in-memory SQLite for fast tests)
@pytest.fixture — test_client (Flask test client)
@pytest.fixture — test_user (registered user with Google/L5/Backend)
@pytest.fixture — test_user_apple (registered user with Apple/L5/Frontend)
@pytest.fixture — test_elo (initialized ELO for test user)
@pytest.fixture — test_mock_session (mock interview in progress)
@pytest.fixture — test_completed_mock (finished mock with scores)
@pytest.fixture — test_learning_path (generated path with 10 topics)
@pytest.fixture — mock_llm_response (deterministic LLM responses for testing)
```

### Running Tests

```bash
# All tests
cd backend && pytest -v

# Specific sprint tests
pytest tests/test_elo.py tests/test_company_profiles.py tests/test_gap_map.py -v  # Sprint 1

# With coverage
pytest --cov=. --cov-report=html -v

# Fast (skip LLM-dependent tests)
pytest -v -m "not llm"

# Only integration tests
pytest tests/test_integration.py -v
```

### Test Markers

```python
@pytest.mark.unit        # Fast, no external dependencies
@pytest.mark.integration # Multi-component, may use test DB
@pytest.mark.llm         # Requires LLM (mock in CI, real in local)
@pytest.mark.slow        # Takes > 5 seconds
@pytest.mark.voice       # Requires voice/audio infrastructure
```

---

## 9. CI/CD Integration (Future)

```yaml
# .github/workflows/test.yml (for when CI is set up)
on: [push, pull_request]
jobs:
  test:
    steps:
      - run: pip install pytest pytest-cov
      - run: pytest -v -m "not llm and not voice" --cov=. --cov-fail-under=85
```

---

## 10. Definition of Done — Testing

### Per Sprint
- [ ] All unit tests for sprint features written and passing
- [ ] Integration tests for sprint flow written and passing
- [ ] No regressions in previous sprint tests
- [ ] Coverage ≥ 85% for new code

### Pre-Launch (Sprint 8)
- [ ] All 210+ automated tests passing
- [ ] All 15 E2E manual journeys verified on Chrome + Edge
- [ ] AI quality tests completed (persona, guardrail, accuracy)
- [ ] Performance targets met
- [ ] Security tests passing
- [ ] LLM fallback tested
- [ ] Zero critical bugs in happy path

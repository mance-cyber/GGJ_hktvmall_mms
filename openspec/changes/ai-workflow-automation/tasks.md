# Tasks: AI Workflow Automation

## Phase 1: 改價審批流程

### 1. Database & Models

- [x] 1.1 Create database migration for PriceProposal new fields:
  - `source_conversation_id` (VARCHAR, nullable)
  - `source_type` (VARCHAR, default "manual")
  - `assigned_to` (UUID, nullable, FK to users)
  - `due_date` (TIMESTAMP, nullable)
  - `reminder_sent` (BOOLEAN, default false)

- [x] 1.2 Update `backend/app/models/pricing.py` PriceProposal model with new fields

### 2. Workflow Engine Core

- [x] 2.1 Create `backend/app/services/workflow/__init__.py` module structure

- [x] 2.2 Create `backend/app/services/workflow/engine.py` with WorkflowEngine class:
  - Trigger registration
  - Action execution
  - State tracking

- [x] 2.3 Create `backend/app/services/workflow/actions.py` with action executors:
  - `create_pricing_proposal()` action
  - `send_telegram_notification()` action

### 3. Agent Intent Extension

- [x] 3.1 Add new intents to `backend/app/services/agent/intent_classifier.py`:
  - `CREATE_APPROVAL_TASK`
  - `CONFIRM_ACTION`
  - `DECLINE_ACTION`

- [x] 3.2 Update `backend/app/services/agent/agent_service.py` to handle approval workflow:
  - Detect price suggestion context
  - Offer to create approval task
  - Handle user confirmation/decline

- [x] 3.3 Add workflow tool to `backend/app/services/agent/tools/`:
  - `create_approval_task()` tool function

### 4. Telegram Integration

- [x] 4.1 Create approval notification template in Telegram service
  - Implemented in `backend/app/services/workflow/actions.py` (`_send_proposal_notification`)

- [x] 4.2 Add notification trigger when PriceProposal created with source_type="ai_suggestion"
  - Implemented in `handle_pricing_approval_trigger()` with `send_notification=True`

### 5. Frontend Integration

- [x] 5.1 Update `frontend/src/app/pricing-approval/` to display source badge for AI-originated proposals
  - Added `SourceBadge` component with icons for manual/ai_suggestion/auto_alert
  - Updated `PriceProposal` type with new workflow fields

- [x] 5.2 Add conversation link component that navigates to agent page with conversation loaded
  - Added `ConversationLink` component with `/agent?conversation={id}` navigation

### 6. Testing - Phase 1

- [x] 6.1 Write unit tests for WorkflowEngine
  - Created `backend/tests/test_workflow_engine.py`
  - Tests: trigger registration, execution, state tracking, error handling

- [x] 6.2 Write unit tests for Agent approval intent handling
  - Created `backend/tests/test_agent_workflow_intents.py`
  - Tests: intent classification, workflow tools, agent service handling

- [x] 6.3 Write E2E test: conversation → approval task creation
  - Created `backend/tests/e2e/test_workflow_e2e.py`
  - Tests: full flow, source tracking, Telegram notification, API endpoints

---

## Phase 2: 報告排程

### 7. Database & Models

- [x] 7.1 Create `backend/app/models/workflow.py` with:
  - `ScheduledReport` model
  - `ReportExecution` model
  - `AlertWorkflowConfig` model (Phase 3 預備)

- [x] 7.2 Create database migration for scheduled_reports and report_executions tables
  - `20260202_1100_add_scheduled_reports_tables.py`

### 8. Scheduling Service

- [x] 8.1 Create `backend/app/services/workflow/scheduler.py`:
  - Celery Beat task registration
  - Schedule CRUD operations
  - Next run calculation

- [x] 8.2 Create `backend/app/tasks/workflow_tasks.py`:
  - `execute_scheduled_report` Celery task
  - Auto-pause on repeated failures logic

### 9. API Endpoints

- [x] 9.1 Create `backend/app/api/v1/workflow.py` with endpoints:
  - GET `/workflow/schedules` - list schedules
  - POST `/workflow/schedules` - create schedule
  - PATCH `/workflow/schedules/{id}` - update/pause/resume
  - DELETE `/workflow/schedules/{id}` - delete schedule
  - GET `/workflow/executions` - execution history

- [x] 9.2 Create `backend/app/schemas/workflow.py` with Pydantic models

- [x] 9.3 Register workflow router in `backend/app/api/v1/router.py`

### 10. Agent Schedule Intent

- [x] 10.1 Add schedule-related intents to intent classifier:
  - `CREATE_SCHEDULED_REPORT`
  - `PAUSE_SCHEDULED_REPORT`
  - `RESUME_SCHEDULED_REPORT`
  - `DELETE_SCHEDULED_REPORT`
  - `LIST_SCHEDULES`

- [x] 10.2 Add schedule slot extraction to slot manager:
  - Parse frequency (daily/weekly/monthly)
  - Parse time expressions
  - Parse product names
  - Added `ScheduleSlots` dataclass

- [x] 10.3 Implement schedule management in agent service:
  - Created `schedule_tools.py` with 5 tools
  - Create/pause/resume/delete schedule via conversation
  - List active schedules query

### 11. Frontend Schedule Panel

- [x] 11.1 Create `frontend/src/lib/api/workflow.ts` API client
  - Complete API client with all CRUD operations
  - Utility functions for formatting frequency, status, report type

- [x] 11.2 Create `frontend/src/app/agent/components/SchedulePanel.tsx`:
  - List active schedules with ScheduleCard component
  - Pause/resume/delete/trigger buttons
  - Next execution time display with relative formatting
  - Compact mode support for sidebar

- [x] 11.3 Create `frontend/src/app/agent/components/ScheduleEditor.tsx` for editing schedules
  - Dialog-based form for create/edit
  - Support daily/weekly/monthly frequencies
  - Time picker and day selector
  - Form validation

- [x] 11.4 Integrate SchedulePanel into agent page
  - Added collapsible section in desktop sidebar
  - Added collapsible section in mobile sheet
  - Auto-refresh every minute

### 12. Report Delivery

- [x] 12.1 Add Telegram delivery for scheduled reports
  - Added `send_scheduled_report()` method to TelegramNotifier
  - Added `_markdown_to_html()` helper for formatting
  - Improved `_deliver_report()` to use dedicated method
  - Default to Telegram if no channels configured

- [ ] 12.2 Add email delivery option (optional)
  - Placeholder implemented, marked for future enhancement

### 13. Testing - Phase 2

- [x] 13.1 Write unit tests for scheduler service
  - Created `backend/tests/test_scheduler_service.py`
  - Tests: CRUD operations, status management, time calculation, execution tracking

- [x] 13.2 Write unit tests for schedule intent handling
  - Created `backend/tests/test_schedule_intents.py`
  - Tests: intent classification, slot extraction, schedule tools, tool executor integration

- [x] 13.3 Write E2E test: create schedule via conversation → verify Celery task registered
  - Created `backend/tests/e2e/test_schedule_e2e.py`
  - Tests: API endpoints, execution history, Celery task integration, full lifecycle

---

## Phase 3: 告警響應流程

### 14. Alert Workflow Config

- [x] 14.1 Add `AlertWorkflowConfig` model to `backend/app/models/workflow.py`
  - Model pre-created in Phase 2 with fields: name, is_active, trigger_conditions, auto_analyze, auto_create_proposal, notify_channels, quiet_hours_start/end

- [x] 14.2 Create database migration for alert_workflow_configs table
  - Included in `20260202_1100_add_scheduled_reports_tables.py` migration

- [x] 14.3 Add API endpoints for alert workflow config CRUD
  - GET/POST `/workflow/alert-configs` - list and create configs
  - GET/PATCH/DELETE `/workflow/alert-configs/{id}` - CRUD operations
  - POST `/workflow/alert-configs/{id}/toggle` - toggle active status

### 15. Alert Trigger Integration

- [x] 15.1 Create `backend/app/services/workflow/triggers.py`:
  - `AlertTrigger` class with methods: get_active_configs, should_trigger, execute_workflow
  - Threshold checking: price_drop_threshold, price_increase_threshold
  - Quiet hours filtering with timezone support

- [x] 15.2 Integrate trigger with existing PriceAlert creation flow
  - Modified `_check_price_alert()` in `backend/app/tasks/scrape_tasks.py`
  - Triggers `execute_alert_workflow.delay()` after creating PriceAlert

- [x] 15.3 Create `execute_alert_workflow` Celery task
  - Added to `backend/app/tasks/workflow_tasks.py`
  - Async execution with proper event loop handling

### 16. Auto AI Analysis

- [x] 16.1 Implement automatic AI analysis invocation on alert trigger
  - `AlertTrigger._execute_ai_analysis()` method
  - Triggered when `config.auto_analyze == True`

- [x] 16.2 Generate impact assessment and recommendations
  - `_assess_impact()` - high/medium/low/minimal impact levels
  - `_generate_recommendations()` - contextual pricing advice

- [x] 16.3 Store analysis results with alert workflow execution
  - Results stored in `results["analysis_result"]` dict
  - Includes price_change, impact_assessment, recommendations, analyzed_at

### 17. Alert Notifications

- [x] 17.1 Create Telegram notification template with:
  - Alert details (product, prices, change percent)
  - AI analysis summary (impact assessment, first recommendation)
  - Action buttons
  - Added `send_alert_notification()` method to TelegramNotifier

- [x] 17.2 Implement Telegram inline keyboard for action buttons
  - `send_message_with_buttons()` method in telegram.py
  - Buttons: 創建改價任務, 查看詳情, 暫時忽略
  - For proposals: 批准提案, 拒絕提案, 查看詳情

- [x] 17.3 Handle [創建改價任務] button callback
  - Webhook endpoint at POST `/api/v1/telegram/webhook`
  - Callbacks: create_proposal, approve_proposal, reject_proposal, view_alert, view_proposal, ignore_alert

### 18. Auto-Create Proposal Option

- [x] 18.1 Implement auto_create_proposal logic in alert workflow
  - `AlertTrigger._create_price_proposal()` method
  - Triggered when `config.auto_create_proposal == True`
  - Calculates proposed price based on competitor price change

- [x] 18.2 Add notification for auto-created proposals
  - Proposal info included in Telegram notification
  - Different button set for messages with proposals

### 19. Frontend Alert Config

- [ ] 19.1 Create alert workflow configuration UI (optional, can be conversation-only initially)

### 20. Testing - Phase 3

- [x] 20.1 Write unit tests for AlertTrigger
  - Created `backend/tests/test_alert_trigger.py`
  - Tests: condition checking, threshold validation, category filtering

- [x] 20.2 Write unit tests for quiet hours filtering
  - Included in `test_alert_trigger.py` TestQuietHours class
  - Tests: no quiet hours, within quiet hours, overnight quiet hours, time parsing

- [x] 20.3 Write E2E test: price alert → AI analysis → Telegram notification
  - Created `backend/tests/e2e/test_alert_workflow_e2e.py`
  - Tests: full workflow execution, auto proposal, Telegram webhook callbacks, Celery integration

---

## Completion Checklist

- [ ] 21.1 Update CLAUDE.md with new workflow module documentation

- [ ] 21.2 Run full test suite and ensure all tests pass

- [ ] 21.3 Manual QA: test all three workflows end-to-end

---

## Implementation Summary

### Phase 3 Completed Files

**Services:**
- `backend/app/services/workflow/triggers.py` - AlertTrigger class with:
  - Condition checking (price thresholds, category filters)
  - Quiet hours filtering with timezone support
  - AI analysis (impact assessment, recommendations)
  - Auto proposal creation
  - Telegram notification with inline keyboards

**Tasks:**
- `backend/app/tasks/workflow_tasks.py` - Added:
  - `execute_alert_workflow` Celery task
  - `process_single_alert_config` Celery task

- `backend/app/tasks/scrape_tasks.py` - Modified:
  - `_check_price_alert()` now triggers alert workflow

**API:**
- `backend/app/api/v1/workflow.py` - Alert config CRUD endpoints
- `backend/app/api/v1/telegram.py` - Webhook handler for button callbacks

**Telegram:**
- `backend/app/services/telegram.py` - Added:
  - `send_message_with_buttons()` - inline keyboard support
  - `answer_callback_query()` - button click response
  - `edit_message_reply_markup()` - update/remove buttons
  - `send_alert_notification()` - formatted alert with buttons

**Tests:**
- `backend/tests/test_alert_trigger.py` - Unit tests
- `backend/tests/e2e/test_alert_workflow_e2e.py` - E2E tests

## ADDED Requirements

### Requirement: Create Scheduled Report from Conversation
The system SHALL allow users to create scheduled reports through natural language in AI conversations.

#### Scenario: Parse schedule request
- **WHEN** user says "每個禮拜一朝早 9 點出份和牛市場報告"
- **THEN** AI parses: report_type=market, products=["和牛"], schedule_type=weekly, schedule_day=1, schedule_time=09:00

#### Scenario: Confirm schedule creation
- **WHEN** AI successfully parses schedule request
- **THEN** AI confirms: "收到！我會喺每個禮拜一 9:00 自動生成報告"
- **AND** creates ScheduledReport record

#### Scenario: Link schedule to conversation
- **WHEN** ScheduledReport is created from conversation
- **THEN** created_from_conversation is set to the conversation_id

---

### Requirement: Schedule Types
The system SHALL support daily, weekly, and monthly report schedules.

#### Scenario: Daily schedule
- **WHEN** schedule_type is "daily"
- **THEN** report executes every day at schedule_time

#### Scenario: Weekly schedule
- **WHEN** schedule_type is "weekly" AND schedule_day is 1
- **THEN** report executes every Monday at schedule_time

#### Scenario: Monthly schedule
- **WHEN** schedule_type is "monthly" AND schedule_day is 15
- **THEN** report executes on the 15th of each month at schedule_time

---

### Requirement: Report Execution
The system SHALL execute scheduled reports using Celery Beat and track execution history.

#### Scenario: Execute scheduled report
- **WHEN** schedule time arrives
- **THEN** system creates ReportExecution with status "running"
- **AND** invokes ReportGenerator with configured products and report_type

#### Scenario: Store execution result
- **WHEN** report generation completes
- **THEN** ReportExecution is updated with report_markdown and status "success"

#### Scenario: Handle execution failure
- **WHEN** report generation fails
- **THEN** ReportExecution is updated with error_message and status "failed"

---

### Requirement: Report Delivery
The system SHALL deliver generated reports via configured channels.

#### Scenario: Telegram delivery
- **WHEN** report execution completes AND notify_telegram is true
- **THEN** system sends report summary to Telegram
- **AND** attaches PDF if report_pdf_url is available

#### Scenario: Email delivery
- **WHEN** report execution completes AND notify_email is set
- **THEN** system sends report to configured email address

---

### Requirement: Schedule Management
The system SHALL allow users to pause, resume, edit, and delete scheduled reports.

#### Scenario: Pause schedule via conversation
- **WHEN** user says "暫停和牛市場週報"
- **THEN** system sets is_active=false on matching ScheduledReport
- **AND** AI confirms: "已暫停『和牛市場週報』排程"

#### Scenario: Resume schedule via conversation
- **WHEN** user says "恢復和牛市場週報"
- **THEN** system sets is_active=true on matching ScheduledReport

#### Scenario: Delete schedule via conversation
- **WHEN** user says "刪除和牛市場週報"
- **THEN** system soft-deletes the ScheduledReport
- **AND** AI confirms deletion

#### Scenario: Manage via UI
- **WHEN** user opens Schedule Panel in agent page
- **THEN** user can view, pause, resume, edit, and delete schedules

---

### Requirement: Auto-Pause on Repeated Failures
The system SHALL automatically pause schedules that fail repeatedly to prevent resource waste.

#### Scenario: Auto-pause after 3 failures
- **WHEN** a ScheduledReport has 3 consecutive failed executions
- **THEN** system sets is_active=false
- **AND** sends notification to user about auto-pause

#### Scenario: User can re-enable after auto-pause
- **WHEN** user re-enables an auto-paused schedule
- **THEN** failure counter resets to 0

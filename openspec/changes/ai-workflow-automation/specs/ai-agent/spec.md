## ADDED Requirements

### Requirement: Workflow Intent Recognition
The AI agent SHALL recognize user intents related to workflow automation and respond appropriately.

#### Scenario: Recognize create approval intent
- **WHEN** user says "幫我開個審批任務" or similar
- **THEN** AI identifies intent as CREATE_APPROVAL_TASK

#### Scenario: Recognize schedule report intent
- **WHEN** user says "每週一出份報告" or similar
- **THEN** AI identifies intent as CREATE_SCHEDULED_REPORT

#### Scenario: Recognize cancel schedule intent
- **WHEN** user says "取消和牛報告" or similar
- **THEN** AI identifies intent as CANCEL_SCHEDULED_REPORT

#### Scenario: Recognize pause schedule intent
- **WHEN** user says "暫停報告排程" or similar
- **THEN** AI identifies intent as PAUSE_SCHEDULED_REPORT

---

### Requirement: Proactive Workflow Suggestions
The AI agent SHALL proactively suggest workflow actions after completing relevant analyses.

#### Scenario: Suggest approval after price analysis
- **WHEN** AI completes price analysis with a recommendation
- **THEN** AI asks: "想唔想我幫你開個審批任務？"
- **AND** provides quick action buttons [開審批] [唔使]

#### Scenario: Suggest schedule after report generation
- **WHEN** AI generates a report
- **THEN** AI asks: "想唔想定期收到呢類報告？"
- **AND** provides quick action buttons [設定排程] [唔使]

---

### Requirement: Schedule Confirmation Flow
The AI agent SHALL guide users through schedule configuration with clarifying questions if needed.

#### Scenario: Complete schedule info provided
- **WHEN** user provides complete schedule info (type, products, frequency, time)
- **THEN** AI creates schedule without further questions

#### Scenario: Missing schedule details
- **WHEN** user says "幫我定期出報告" without specifying details
- **THEN** AI asks clarifying questions about report type, products, and frequency

#### Scenario: Confirm before creation
- **WHEN** AI has all schedule details
- **THEN** AI summarizes and asks for confirmation before creating

---

### Requirement: Workflow Status Queries
The AI agent SHALL respond to queries about workflow and schedule status.

#### Scenario: List active schedules
- **WHEN** user asks "我有咩排程？"
- **THEN** AI lists all active ScheduledReports for the user

#### Scenario: Check next execution
- **WHEN** user asks "和牛報告幾時出？"
- **THEN** AI responds with next_run_at for matching schedule

#### Scenario: Show execution history
- **WHEN** user asks "上次報告點樣？"
- **THEN** AI shows recent ReportExecution status and summary

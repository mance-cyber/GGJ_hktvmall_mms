## ADDED Requirements

### Requirement: Alert Workflow Configuration
The system SHALL allow users to configure automated response workflows for price alerts.

#### Scenario: Create alert workflow config
- **WHEN** user creates an AlertWorkflowConfig
- **THEN** system stores the configuration with alert_types, threshold_percent, and response actions

#### Scenario: Configure threshold
- **WHEN** user sets threshold_percent to 10
- **THEN** only alerts with change_percent >= 10% trigger the workflow

#### Scenario: Configure quiet hours
- **WHEN** user sets quiet_hours_start=22:00 and quiet_hours_end=08:00
- **THEN** workflow does not execute between 22:00 and 08:00

---

### Requirement: Automatic AI Analysis on Alert
The system SHALL automatically trigger AI analysis when a price alert matches configured workflow rules.

#### Scenario: Trigger analysis on price drop
- **WHEN** PriceAlert is created with alert_type "price_drop"
- **AND** an active AlertWorkflowConfig matches this alert_type
- **AND** change_percent exceeds threshold
- **THEN** system automatically invokes AI analysis for the affected product

#### Scenario: Skip analysis during quiet hours
- **WHEN** alert triggers during configured quiet hours
- **THEN** system queues the analysis for execution after quiet hours end

#### Scenario: Analysis generates insights
- **WHEN** AI analysis completes
- **THEN** result includes impact assessment and recommended response

---

### Requirement: Alert Response Notification
The system SHALL send notifications with AI analysis results when alerts trigger workflows.

#### Scenario: Telegram notification with analysis
- **WHEN** AI analysis completes for an alert
- **AND** notify_telegram is true in config
- **THEN** system sends Telegram message with:
  - Alert details (product, old price, new price, change %)
  - AI analysis summary
  - Action buttons [查看詳情] [創建改價任務]

#### Scenario: Action button creates proposal
- **WHEN** user clicks [創建改價任務] in Telegram
- **THEN** system creates PriceProposal with source_type "auto_alert"

---

### Requirement: Auto-Create Proposal Option
The system SHALL optionally auto-create pricing proposals when alerts trigger, without requiring user confirmation.

#### Scenario: Auto-create enabled
- **WHEN** AlertWorkflowConfig has auto_create_proposal=true
- **AND** alert triggers workflow
- **THEN** system automatically creates PriceProposal with AI-suggested price
- **AND** sends notification informing user of auto-created proposal

#### Scenario: Auto-create disabled (default)
- **WHEN** AlertWorkflowConfig has auto_create_proposal=false
- **THEN** system only sends notification and waits for user action

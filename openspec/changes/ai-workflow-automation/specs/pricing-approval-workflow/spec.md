## ADDED Requirements

### Requirement: Create Approval from AI Suggestion
The system SHALL allow users to create pricing approval tasks directly from AI pricing suggestions within a conversation.

#### Scenario: User confirms approval creation
- **WHEN** AI suggests a price change AND user confirms "創建審批任務"
- **THEN** system creates a PriceProposal with status "pending"
- **AND** the proposal includes source_conversation_id linking to the conversation
- **AND** the proposal includes source_type "ai_suggestion"

#### Scenario: User declines approval creation
- **WHEN** AI suggests a price change AND user declines
- **THEN** no PriceProposal is created
- **AND** the conversation continues normally

---

### Requirement: Approval Task Notification
The system SHALL notify designated approvers when a new pricing approval task is created from an AI conversation.

#### Scenario: Telegram notification sent
- **WHEN** a PriceProposal is created with source_type "ai_suggestion"
- **THEN** system sends Telegram notification to configured approvers
- **AND** notification includes product name, current price, suggested price, and change percentage

#### Scenario: Notification includes conversation link
- **WHEN** Telegram notification is sent for AI-originated proposal
- **THEN** notification includes a link to view the original AI conversation

---

### Requirement: Approval UI Shows Conversation Source
The system SHALL display the originating conversation in the pricing approval UI when a proposal was created from AI.

#### Scenario: Display source badge
- **WHEN** user views a PriceProposal with source_type "ai_suggestion"
- **THEN** the UI displays "來源：AI 對話" badge

#### Scenario: Navigate to source conversation
- **WHEN** user clicks the conversation source link
- **THEN** user is navigated to the AI agent page with that conversation loaded

---

### Requirement: Approval Assignment
The system SHALL support assigning pricing approvals to specific users with optional due dates.

#### Scenario: Assign approver
- **WHEN** creating approval task AND user specifies an approver
- **THEN** PriceProposal.assigned_to is set to that user's ID

#### Scenario: Set due date
- **WHEN** creating approval task AND user specifies a due date
- **THEN** PriceProposal.due_date is set accordingly

#### Scenario: Send reminder before due date
- **WHEN** due_date is approaching (24 hours) AND reminder_sent is false
- **THEN** system sends reminder notification to assigned approver
- **AND** sets reminder_sent to true

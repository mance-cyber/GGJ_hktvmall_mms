## ADDED Requirements

### Requirement: ROI Summary Calculation
The system SHALL calculate and return an ROI summary for a specified time period, including:
- Total value generated (HKD)
- AI pricing contribution (HKD)
- Competitor monitoring value (HKD)
- Risk avoidance value (HKD)
- Overall ROI percentage

#### Scenario: Get monthly ROI summary
- **WHEN** user requests ROI summary with period=month
- **THEN** system calculates values from the last 30 days
- **AND** returns ROISummary object with all metrics

#### Scenario: No data in period
- **WHEN** user requests ROI summary for a period with no executed proposals
- **THEN** system returns ROISummary with zero values
- **AND** roi_percentage is 0

---

### Requirement: ROI Trend Analysis
The system SHALL provide time-series ROI trend data for visualization, supporting daily/weekly/monthly granularity.

#### Scenario: Get 30-day trend with daily granularity
- **WHEN** user requests ROI trends with days=30 and granularity=day
- **THEN** system returns list of ROITrendPoint objects
- **AND** each point contains date, cumulative_value, ai_pricing, monitoring, risk_avoidance

#### Scenario: Sparse data handling
- **WHEN** some days have no data
- **THEN** system fills missing days with zero values
- **AND** maintains continuous date sequence

---

### Requirement: AI Pricing Impact Analysis
The system SHALL analyze and report the impact of executed AI pricing proposals, showing individual proposal contributions.

#### Scenario: Get top 10 pricing impacts
- **WHEN** user requests pricing impact with limit=10
- **THEN** system returns list of PricingProposalImpact objects
- **AND** sorted by impact amount descending
- **AND** includes product_name, old_price, new_price, impact, executed_at

#### Scenario: Calculate impact from executed proposals
- **WHEN** a price proposal has status='executed' and final_price > current_price
- **THEN** impact is calculated as (final_price - current_price) × estimated_quantity
- **AND** estimated_quantity defaults to 10 if no order data available

---

### Requirement: Competitor Monitoring Value
The system SHALL quantify the value derived from competitor price monitoring and alerting.

#### Scenario: Get monthly competitor insights
- **WHEN** user requests competitor insights with period=month
- **THEN** system returns CompetitorInsights object
- **AND** includes price_alerts_triggered, price_drops_detected, price_increases_detected
- **AND** includes avg_response_time_hours and potential_savings

#### Scenario: Calculate potential savings
- **WHEN** calculating competitor monitoring value
- **THEN** potential_savings = COUNT(alerts) × AVG(change_percent) × avg_order_value
- **AND** only includes alerts where alert_type IN ('price_drop', 'price_increase')

---

### Requirement: ROI Dashboard UI
The system SHALL provide a web-based ROI dashboard with visual representation of all ROI metrics.

#### Scenario: Display ROI summary cards
- **WHEN** user navigates to /roi page
- **THEN** 4 KPI cards are displayed: Total Value, AI Contribution, Monitoring Value, ROI%
- **AND** values animate on load using number counter effect

#### Scenario: Display trend chart
- **WHEN** ROI page loads with trend data
- **THEN** Recharts line chart displays cumulative value over time
- **AND** multiple data series can be toggled on/off

#### Scenario: Time range selection
- **WHEN** user selects different time range (today/week/month)
- **THEN** all dashboard components refresh with new period data
- **AND** loading states are shown during data fetch

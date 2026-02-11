# AWS Lightsail 配額提升申請指南

**問題:** "Sorry, your account can not create an instance using this Lightsail plan size."

**原因:** 新 AWS 帳號對較大的 Lightsail 實例有限制

---

## 📝 申請配額提升

### Step 1: 訪問 AWS Support Center

🔗 **鏈接:** https://support.console.aws.amazon.com/support/home

### Step 2: 創建支援案例

1. 點擊 **"Create case"**
2. 選擇 **"Service limit increase"**

### Step 3: 填寫申請表

```yaml
Case classification:
  Limit type: Lightsail

Request 1:
  Region: Asia Pacific (Singapore)
  Limit: Instance count
  New limit value: 5

  Use case description:
    "I am deploying a production web application (GoGoJap - E-commerce
    management system) on Lightsail. I need to create a $40-44/month
    instance (2 vCPU, 4GB RAM) in the Singapore region to serve customers
    in Hong Kong and Southeast Asia.

    The application stack includes:
    - FastAPI backend
    - PostgreSQL database (via RDS)
    - Celery task queue
    - Redis cache

    Current smaller instances ($10-20/month) do not have sufficient
    resources to run this stack reliably. I need the 2 vCPU, 4GB RAM
    instance to ensure stable performance.

    This is a legitimate business use case for a production application.
    Please approve this limit increase. Thank you!"

Contact options:
  Preferred contact language: English
  Contact methods: Web (fastest)
```

### Step 4: 提交並等待

⏱️ **處理時間:**
- Business hours: 通常 12-24 小時
- 最快可能幾小時內批准

### Step 5: 收到批准後

檢查郵件，收到批准通知後就可以創建 $44 套餐了。

---

## 📧 申請範本（複製使用）

```
Subject: Request to increase Lightsail instance limit in Singapore region

Dear AWS Support,

I am deploying a production web application on AWS Lightsail and need to
create a larger instance in the Singapore (ap-southeast-1) region.

Application Details:
- Name: GoGoJap E-commerce Management System
- Stack: FastAPI + PostgreSQL + Redis + Celery
- Target region: Singapore (for Hong Kong customers)
- Required instance: $40-44/month (2 vCPU, 4GB RAM, 80GB SSD)

Current Issue:
I am unable to create this instance size due to account limits. Smaller
instances ($10-20/month) do not have sufficient resources to run the
full application stack reliably.

Request:
Please approve my account to create larger Lightsail instances (up to
2 vCPU, 4GB RAM) in the Singapore region.

This is a legitimate production business application serving e-commerce
customers. I appreciate your prompt assistance.

Thank you,
[Your Name]
```

---

## ⚡ 加快批准的技巧

1. **清楚說明業務用途** - 不是測試，是生產環境
2. **說明技術需求** - 為什麼需要這個配置
3. **提供具體細節** - 應用架構、預期負載
4. **使用商業語氣** - 展現專業性
5. **選擇 Web 聯繫** - 最快的方式

---

## 📊 批准率

**通常情況:**
- ✅ 合理的商業用途：幾乎 100% 批准
- ✅ 新帳號首次申請：通常會批准
- ⏱️ 處理時間：12-24 小時（工作日）

**建議:**
- 白天（美國時間）提交會更快
- 週一至週五提交優於週末

---

## 🔄 同時進行的替代方案

在等待批准期間，可以：
1. 使用 EC2 替代方案（立即可用）
2. 繼續創建 RDS 和 S3（不受影響）
3. 準備部署腳本和配置

---

**創建日期:** 2026-02-10

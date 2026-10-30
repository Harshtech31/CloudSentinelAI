# CloudSentinel AI — AWS Onboarding & IAM Setup Guide

This guide explains how to connect your AWS Account to CloudSentinel AI following the **Principle of Least Privilege**.

---

## ⚠️ Security Recommendation: Create a Dedicated IAM User

> [!WARNING]
> **NEVER use your AWS Root Account or an Admin User for security auditing.**
> Root and Admin credentials possess destructive capabilities that CloudSentinel does not need and will never ask for.

Instead, create a dedicated IAM user with **programmatic access only** and attach CloudSentinel's read-only audit policy.

---

## Step-by-Step IAM Setup

### Step 1: Create the CloudSentinel Audit Policy in AWS
1. Open the [AWS IAM Console — Policies](https://console.aws.amazon.com/iam/home#/policies).
2. Click **Create Policy**.
3. Select the **JSON** tab and paste the contents of [`docs/cloudsentinel_audit_iam_policy.json`](file:///home/harshith/Documents/cloudsentinel-ai(clg)/docs/cloudsentinel_audit_iam_policy.json).
4. Click **Next**.
5. Name the policy: `CloudSentinelAuditReadOnlyPolicy`.
6. Click **Create Policy**.

### Step 2: Create a Dedicated IAM User
1. Navigate to [AWS IAM Console — Users](https://console.aws.amazon.com/iam/home#/users).
2. Click **Create User**.
3. User name: `cloudsentinel-auditor`.
4. Leave **"Provide user access to the AWS Management Console"** unchecked (programmatic CLI access only).
5. Click **Next**.

### Step 3: Attach the Policy
1. In the **Set permissions** screen, select **"Attach policies directly"**.
2. Search for `CloudSentinelAuditReadOnlyPolicy` and check the box.
3. Click **Next**, then **Create User**.

### Step 4: Generate Access Keys
1. Click on the newly created user `cloudsentinel-auditor`.
2. Go to the **Security credentials** tab.
3. Scroll down to **Access keys** and click **Create access key**.
4. Select **Application running outside AWS** (or **Command Line Interface (CLI)**).
5. Click **Next** and **Create access key**.
6. Copy your **Access Key ID** (`AKIA...`) and **Secret Access Key**.

### Step 5: Input into CloudSentinel
Paste the Access Key ID and Secret Access Key into the CloudSentinel Onboarding Wizard, choose your default region (e.g. `us-east-1` or `ap-south-1`), test the connection, and run your first live audit!

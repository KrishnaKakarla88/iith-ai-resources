# Return Fraud and Abuse Prevention Standard

# KARTWAY CUSTOMER OPERATIONS POLICY MANUAL
## SECTION 8: RISK MANAGEMENT AND ACCOUNT INTEGRITY
### SUB-SECTION 8.4: RETURN ABUSE AND FRAUD PREVENTION

---

#### 8.4.1 Return-Rate Thresholds and Automated Flagging

8.4.1.1 **Definition of Return Rate (RR):** Return Rate is calculated as the total monetary value of items returned and refunded divided by the total monetary value of items purchased within a rolling 90-day window, expressed as a percentage.

$$\text{RR} = \left( \frac{\text{Total Refunded Value (90 Days)}}{\text{Total Purchased Value (90 Days)}} \right) \times 100$$

8.4.1.2 **Trigger Thresholds:** The Kartway Account Integrity System (KAIS) automatically applies a "Level 1 Review Flag" to any customer account that meets either of the following mathematical thresholds:
*   **Threshold A (Value-Based):** A Return Rate (RR) equal to or exceeding 42.0% within a rolling 90-day period, provided the account has settled a minimum of five (5) completed transactions during that timeframe.
*   **Threshold B (Volume-Based):** The return of fifteen (15) or more individual physical items within a rolling 90-day period, regardless of total monetary value.

8.4.1.3 **Excepted Product Categories:** Calculations for the thresholds detailed in Clause 8.4.1.2 exclude purchases made within the "Kartway Refurbished Electronics" category and the "Automotive OEM Parts" category. These categories are subject to independent return thresholds of 55.0% and 50.0% respectively, managed under Policy Addendum 8.4-A.

---

#### 8.4.2 Serial Refund Requesters (SRR)

8.4.2.1 **Definition of Serial Refund Requester (SRR):** A customer account is designated as an SRR if it meets any of the following operational behaviors:
*   Initiating a Return Merchandise Authorization (RMA) or "Item Not Received" (INR) claim on three (3) consecutive orders, irrespective of order value.
*   Maintaining a lifetime refund-to-purchase ratio exceeding 50.0% after a minimum of ten (10) lifetime orders.
*   Filing more than two (2) "Empty Box" or "Missing Contents" claims within a 365-day period.

8.4.2.2 **Mandatory System Restrictions for SRR Accounts:** Once an account is classified as an SRR, Customer Operations agents must execute the following protocol in the Admin Console (Version 4.8):
*   **Deactivation of Self-Service Return Labels:** Revoke the customer's access to automated pre-paid return label generation via the Kartway portal.
*   **Mandatory Physical Inspection:** Transition the account's return status to "Manual Warehouse Audit Required." No refund shall be issued until the physical item is received at the Kartway Central Fulfillment Center (CFC-3, located in Joliet, IL) and inspected by a returns technician.
*   **Suspension of Instant Refunds:** The "Refund on First Scan" (RoFS) privilege is permanently revoked for the lifetime of the account.

---

#### 8.4.3 Non-Disclosure and Confidentiality

8.4.3.1 **Strict Prohibition of Disclosure:** Customer Operations agents, Tier 1 support specialists, and external vendor partners are strictly prohibited from disclosing to a customer that their account has been flagged, placed under review, designated as an SRR, or restricted in any manner related to return abuse.

8.4.3.2 **Prohibited Phrases:** Under no circumstances shall an agent use any of the following phrases or variations thereof during live chat, email, or voice interactions:
*   *"Your account has been flagged for high returns."*
*   *"You have exceeded our return threshold."*
*   *"Our risk department is reviewing your account."*
*   *"Your self-service return options have been blocked due to your return history."*

8.4.3.3 **Approved Scripting (Standard Response Protocol):** If a customer inquires about the lack of self-service return options or delayed refunds, the agent must use the following approved response:
> *"To ensure the security of your transactions, your return is currently undergoing a standard manual verification. We are processing this manually to ensure all details are correct. I will gladly initiate this manual request for you now, which will be processed within our standard 3-to-5 business day window."*

8.4.3.4 **Disciplinary Action:** Any violation of this non-disclosure clause constitutes a Class A policy breach. First-time violations will result in a formal written warning and mandatory retraining. A second violation within a 12-month period will result in immediate termination of system access and disciplinary action up to and including termination of employment.

---

#### 8.4.4 Escalation Path for Suspected Fraud

8.4.4.1 **Identification of Suspected Fraud:** Agents must escalate an account immediately if they identify any of the following "Red Flag" activities:
*   Discrepancies in returned item weight exceeding 20% of the manufacturer's shipping weight.
*   Return of an item with a serial number that does not match the outbound shipment record in the Sentry Risk Dashboard.
*   Submission of altered, forged, or photoshopped shipping receipts or drop-off confirmations.

8.4.4.2 **Escalation Routing Protocol:**
*   **Step 1 (Agent Action):** Lock the customer account in the Admin Console using the "Hold Code: H-99 (Under Investigation)." Do not process any pending refunds.
*   **Step 2 (Ticket Creation):** Create an escalation ticket in Jira Service Desk under the project code **[RISK-FRAUD]**.
*   **Step 3 (Data Compilation):** The agent must attach the following evidence to the Jira ticket:
    1.  The outbound tracking number and carrier weight receipt.
    2.  The inbound tracking number and carrier receipt showing return weight.
    3.  A photograph of the returned item and packaging as received by CFC-3 (retrieved via the Warehouse Management System, WMS-6).
*   **Step 4 (Routing):** Assign the ticket to the **Tier 2 Risk Operations Team** (Queue: `ops-risk-tier2`).

8.4.4.3 **Service Level Agreements (SLAs) and Named Contacts:**
*   **Tier 2 Review SLA:** The Tier 2 Risk Operations Team must review and make a determination on the escalated ticket within **four (4) business hours** of submission.
*   **Final Escalation Authority:** If the value of the disputed transaction exceeds $1,500.00 USD, or if the account has active open orders totaling more than $3,000.00 USD, the Tier 2 Specialist must escalate the ticket to the Fraud Investigation Unit (FIU) Lead, **Marcus Vance**, or the Director of Risk Mitigation, **Clara Vance**, for final account termination approval.
*   **Termination SLA:** Accounts approved for termination must be permanently deactivated within **twenty-four (24) hours** of the FIU Lead's sign-off, and a standard "Terms of Service Violation" notification (Template TOS-04) must be dispatched to the registered email address by the system administrator.

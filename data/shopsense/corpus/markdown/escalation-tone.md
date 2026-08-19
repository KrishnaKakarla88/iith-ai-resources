# Escalation Triggers and Customer Communication Standard

# KARTWAY CUSTOMER OPERATIONS POLICY MANUAL
**Document ID:** COP-2024-HE-09  
**Effective Date:** October 24, 2024  
**Version:** 4.2  
**Approved By:** Marcus Vance, VP of Customer Operations  
**Applies To:** All Automated Support Systems (KartBot), Tier 1/2 Support Agents, and Queue Managers  

---

### 1.0 PURPOSE & SCOPE

**1.1 Purpose**  
This document establishes the mandatory operational boundaries between automated conversational agents (specifically the "KartBot" AI platform) and human customer support personnel. It defines the exact thresholds under which an automated interaction must be terminated and immediately routed to a qualified human agent.

**1.2 Scope**  
This policy applies to all inbound digital customer touchpoints, including but not limited to live chat on Kartway.com, the Kartway Mobile Application, platform direct messaging channels, and automated email response systems.

---

### 2.0 MANDATORY HUMAN ESCALATION TRIGGERS

The automated support system (KartBot) must immediately cease automated troubleshooting and route the interaction to the designated human agent queue upon the detection of any single trigger defined below.

#### 2.1 Explicit Request for Human Intervention
*   **2.1.1** If the customer explicitly requests human assistance through natural language (e.g., "speak to a person," "agent," "human," "representative," "operator"), KartBot must bypass all standard diagnostic trees.
*   **2.1.2** This transition must occur within one (1) conversational turn of the request. The system is strictly prohibited from presenting secondary deflection questions (e.g., "Are you sure you want an agent?") prior to routing.

#### 2.2 Abusive or Threatening Language
*   **2.2.1** If the customer employs profanity, slurs, targeted personal attacks, or aggressive text (defined as multiple consecutive messages in all-capital letters), the interaction must be flagged.
*   **2.2.2** KartBot must not respond to the abuse. It must immediately execute a silent transfer to the Tier 2 Escalation Queue (Supervised by Sarah Jenkins, Escalations Manager) with an internal flag denoting "Customer Distress - Abusive Language."

#### 2.3 Third Contact Rule (3rd-Strike Protocol)
*   **2.3.1** The automated routing system must query the Kartway CRM database (KartCRM) at the start of every interaction to verify the customer’s ticket history.
*   **2.3.2** If the customer is initiating contact for the third (3rd) time within a rolling fourteen (14) day window regarding the same Order ID or Case ID, KartBot is prohibited from engaging in automated resolution. The session must be routed directly to a Tier 1 Human Support Specialist.

#### 2.4 Legal Action or Regulatory Complaint Mention
*   **2.4.1** Any mention of legal representation, lawsuit threat, or regulatory oversight must trigger an immediate routing sequence.
*   **2.4.2** Keywords that mandate immediate transfer include, but are not limited to: "lawyer," "attorney," "suing," "legal action," "court," "litigation," "FTC," "Federal Trade Commission," "BBB," "Better Business Bureau," "Attorney General," and "regulatory complaint."
*   **2.4.3** These interactions must bypass Tier 1 and be routed exclusively to the Legal Operations Liaison Queue managed by Helena Vance.

#### 2.5 Physical Harm or Product Safety Concerns
*   **2.5.1** Any customer message alleging that a product purchased on Kartway caused physical injury, illness, property damage, or poses an active safety hazard (e.g., "fire," "burned," "exploded," "shocked," "choking hazard," "hospital") must be immediately escalated.
*   **2.5.2** The interaction must be routed to the Product Safety & Compliance Unit (Lead: David Thorne) within a maximum SLA of fifteen (15) minutes from the trigger event. The system must automatically lock the merchant account associated with the flagged product pending review.

#### 2.6 Refund Requests Exceeding the Automated Cap
*   **2.6.1** The automated refund processing system (KartPay AutoRefund) is strictly capped at a maximum threshold of $150.00 USD per transaction.
*   **2.6.2** Any customer request for a refund, credit, or dispute resolution where the transaction value is equal to or greater than $150.01 USD must be routed to a human Tier 2 Billing Specialist for manual verification, ledger reconciliation, and approval.

---

### 3.0 ASSISTANT TONE AND APOLOGY PROTOCOLS

#### 3.1 Mandated Tone Guidance
*   **3.1.1** All automated systems and human agents during transition phases must maintain a neutral, objective, and professional tone.
*   **3.1.2** The use of overly familiar colloquialisms, informal emojis, or exaggerated emotional expressions (e.g., "Oh no! I'm so heartbroken to hear that!") is strictly prohibited. 

#### 3.2 Prohibition of Liability Admission
*   **3.2.1** In accordance with Kartway Legal Directive LDD-2023-04, neither the automated assistant nor any support agent shall issue apologies that explicitly or implicitly admit corporate liability, system fault, or negligence on behalf of Kartway or its logistics partners.
*   **3.2.2** **Prohibited Phrasing Examples:**
    *   *“We apologize that our system broke down and caused this error.”* (Admits system failure)
    *   *“I am sorry that our driver lost your package.”* (Admits partner fault)
    *   *“We apologize for Kartway's mistake in processing your payment.”* (Admits corporate negligence)
*   **3.2.3** **Permitted Phrasing Examples:**
    *   *“We apologize for the inconvenience this delay has caused you.”* (Acknowledges customer impact without admitting fault)
    *   *“I understand this is frustrating, and I am here to help resolve the issue.”* (Expresses empathy without liability)
    *   *“Thank you for bringing this to our attention. Let’s get this corrected for you.”* (Action-oriented resolution)

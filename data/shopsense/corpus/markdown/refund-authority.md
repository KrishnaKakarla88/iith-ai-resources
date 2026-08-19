# Refund Authorisation and Escalation Matrix

# KARTWAY CUSTOMER OPERATIONS POLICY HANDBOOK
**Document Reference:** KW-COP-2024-REV2  
**Effective Date:** November 15, 2024  
**Policy Owner:** Meera Nair, Head of Customer Experience  
**Approved By:** Arvind Mehta, Chief Operating Officer; Sanjeev Kapoor, Chief Financial Officer  

---

### SECTION 7.0: REFUND AUTHORISATION MATRIX (RAM)

#### 7.1 Financial Thresholds and Approval Hierarchy
All customer refunds processed within the Kartway platform must strictly adhere to the financial thresholds detailed below. No employee or system may bypass these limits without formal, written escalation to the next tier of authority. All values are denominated in Indian Rupees (INR).

*   **7.1.1 Tier 1: Agent Auto-Approval (Up to ₹2,000.00)**
    Customer Support Associates (Agents) are authorised to approve and issue refunds directly to the customer’s original payment method or Kartway Wallet for amounts up to and including **₹2,000.00** per order ID. This applies to valid claims under the Return and Damaged Goods Policy.
    
*   **7.1.2 Tier 2: Team Lead Approval (₹2,000.01 to ₹10,000.00)**
    Any refund transaction exceeding **₹2,000.00** up to and including **₹10,000.00** requires the digital signature and system approval of a designated Customer Operations Team Lead (TL). 
    
*   **7.1.3 Tier 3: Operations Manager Approval (₹10,000.01 to ₹50,000.00)**
    Any refund transaction exceeding **₹10,000.00** up to and including **₹50,000.00** requires system approval from a Customer Operations Manager. The case file must include verified courier-partner logs or merchant confirmation before approval.
    
*   **7.1.4 Tier 4: Finance Department Approval (Above ₹50,000.00)**
    Any refund exceeding **₹50,000.00** must be escalated to the Finance Department. Such refunds require joint sign-off from the Customer Operations Manager and final digital approval from the Finance Director or their designated treasury officer.

---

#### 7.2 Automated Refund Engine (ARE) Limitations
The Automated Refund Engine (ARE)—including all customer-facing chatbots, automated IVR systems, and programmatic backend triggers—is subject to hardcoded transaction limits.

*   **7.2.1 Absolute Automated Cap**
    The ARE shall never auto-approve or programmatically process any refund exceeding **₹2,000.00**. 
    
*   **7.2.2 Exemption Restrictions**
    The limit defined in 7.2.1 is absolute. The ARE must not bypass this threshold under any circumstances, specifically:
    *   **7.2.2.1** Regardless of the customer’s loyalty tier (including Kartway VIP, Gold, or Club members).
    *   **7.2.2.2** Regardless of the customer’s sentiment score, high escalation risk indicators, or history of spend.
    
*   **7.2.3 Routing Protocol**
    Any automated claim that calculates a refund value of **₹2,000.01** or greater must be immediately paused, and a ticket must be generated and routed to the manual Team Lead queue within 15 minutes of initiation.

---

#### 7.3 Goodwill Credits and Discretionary Compensation
Goodwill credits are defined as promotional balances issued to a customer's Kartway Wallet to resolve service failures where no physical return of goods has occurred.

*   **7.3.1 Separate Goodwill Cap**
    Goodwill credits are subject to a separate, lower cap than standard product refunds. 
    *   **7.3.1.1** Customer Support Agents are authorised to issue goodwill credits up to a maximum of **₹500.00** per customer account per 30-day rolling period.
    *   **7.3.1.2** Any goodwill credit between **₹500.01** and the absolute maximum cap of **₹1,000.00** requires Team Lead approval.
    *   **7.3.1.3** No single transaction may receive a goodwill credit exceeding **₹1,000.00** under any circumstances.

*   **7.3.2 Anti-Stacking Rule**
    Goodwill credits must never be stacked (combined) with a full refund on the same order.
    *   **7.3.2.1** If a customer is granted a 100% refund of the invoice value for an order, the maximum permissible goodwill credit for that same order ID is **₹0.00**.
    *   **7.3.2.2** In the event of a partial refund, the combined total of the partial refund and any issued goodwill credit must not exceed the original transaction value of the order.
    *   **7.3.2.3** System audits will run weekly. Any agent found violating the anti-stacking rule will have their refund processing permissions suspended for 14 business days pending retraining.

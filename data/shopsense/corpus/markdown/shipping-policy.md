# Shipping, Delivery and Lost-Parcel Policy

# KARTWAY CUSTOMER OPERATIONS POLICY HANDBOOK
## Section 7: Shipping, Delivery, and Fulfillment Exceptions

---

### 7.1 Delivery Service Level Agreements (SLAs)

Delivery timelines are calculated in business days, starting the day after the order status transitions to "Shipped" in the Kartway Admin Portal (KAP). The day of dispatch is considered Day 0.

#### 7.1.1 Regional Classifications
*   **Metro Areas:** Postcodes designated under Group A (covering metropolitan capital cities and urban centers with populations exceeding 500,000, as defined in Appendix A).
*   **Non-Metro Areas:** All regional, rural, and remote postcodes designated under Group B and Group C.

#### 7.1.2 SLA Matrix by Service Tier

| Service Tier | Metro SLA (Business Days) | Non-Metro SLA (Business Days) | Authorized Carriers |
| :--- | :--- | :--- | :--- |
| **Saver** | 5 Days | 8 Days | VeloPac, MetroCarrier |
| **Standard** | 3 Days | 5 Days | Zenith Express, VeloPac |
| **Expedited** | 2 Days | 4 Days | Zenith Express |
| **Next-Day** | 1 Day (by 18:00 local time) | Not Available | Zenith Express |

---

### 7.2 Delayed Shipment Definition and Compensation Ladder

#### 7.2.1 Definition of a Delayed Shipment
A shipment is legally defined as "Delayed" under Kartway operations when the shipment has not arrived at the designated delivery address by 23:59 local time on the final day of the promised SLA window (as defined in Clause 7.1.2).

#### 7.2.2 Compensation Ladder
Customer Support Agents (CSAs) are authorized to issue automatic compensation to the customer’s Kartway Wallet based on the duration of the delay past the maximum SLA date. 

```
[SLA Deadline Passed]
       │
       ├─► 1 to 2 Business Days Late ──► 50% Shipping Fee Refund + $5.00 Store Credit
       │
       ├─► 3 to 4 Business Days Late ──► 100% Shipping Fee Refund + $15.00 Store Credit
       │
       └─► 5+ Business Days Late ──────► 100% Shipping Fee Refund + $30.00 Store Credit
```

*   **Exception (Free Shipping Promotions):** If the customer received free shipping on their order, they are ineligible for shipping fee refunds. For delays of 3 or more business days, they must be issued a flat $10.00 Kartway Store Credit in lieu of the tiered ladder.

---

### 7.3 Lost-in-Transit (LIT) Declaration Thresholds

#### 7.3.1 Definition of Lost-in-Transit
A package is declared Lost-in-Transit (LIT) when it is deemed permanently unrecoverable by the carrier network or has exceeded the maximum allowable window of tracking inactivity.

#### 7.3.2 Inactivity Thresholds (Consecutive Days)
CSAs must not declare an item LIT or issue a replacement/refund until the following consecutive calendar days of zero tracking updates (no scans) have elapsed:

*   **Saver & Standard Tiers:** 10 consecutive calendar days of tracking inactivity.
*   **Expedited & Next-Day Tiers:** 5 consecutive calendar days of tracking inactivity.

#### 7.3.3 Resolution Action
Immediately upon reaching the thresholds in 7.3.2, the CSA must:
1.  Transition the ticket status to `LIT_RESOLVED` in the KAP.
2.  Issue the customer a choice of either a 100% refund to the original payment method or a priority replacement order dispatched via Expedited tier at Kartway’s expense.

---

### 7.4 Disputed Delivery Protocol (Delivered but Not Received - DNR)

This protocol applies when carrier tracking status displays "Delivered," but the customer disputes receipt of the package.

#### 7.4.1 Immediate Verification Steps
The CSA must open the respective carrier portal (Zenith Express or VeloPac) and extract:
1.  The GPS coordinates of the delivery scan.
2.  The Proof of Delivery (PoD) photograph (if available).

#### 7.4.2 Scenario A: GPS Coordinates Match (Within 50 Meters of Customer Address)
If the GPS coordinates confirm delivery was executed within 50 meters of the customer's specified address:
1.  The CSA must email the customer the **Kartway Letter of Denial (LoD) Form**.
2.  The customer must sign and return this legal declaration within 7 calendar days.
3.  Upon receipt of the signed LoD, the CSA must process a full replacement order. Refunds are not permitted under Scenario A.

#### 7.4.3 Scenario B: GPS Coordinates Mismatch or No GPS/Photo Available
If the GPS coordinates deviate by more than 50 meters from the customer's address, or if the carrier failed to log GPS data and photo evidence:
1.  The CSA must file a **Carrier Investigation Ticket (CIT)**.
2.  The carrier is allocated exactly **48 hours** to locate the parcel or provide physical proof of signature.
3.  If the carrier does not resolve the ticket or locate the package within the 48-hour window, the CSA must immediately issue a full refund or replacement (customer's choice) on Day 3. No LoD is required from the customer.

---

### 7.5 Address-Change and Order-Modification Cutoffs

To maintain warehouse fulfillment velocity, strict cutoffs apply to all post-purchase shipping address modifications.

```
[Order Placed]
       │
       ├─── (0 to 45 Mins) ──► System Status: "Pending" ──────► Self-Service or CSA Edit Allowed
       │
       ├─── (45+ Mins) ──────► System Status: "Processing" ───► Modifications Blocked (Warehouse Lock)
       │
       └─── (Post-Dispatch) ─► System Status: "Shipped" ──────► Zenith Express Intercept Only ($12.50 fee)
```

#### 7.5.1 Pending and Awaiting Processing Status
Customers may modify their delivery address directly via the "My Orders" portal, or CSAs may manually update the address in the Order Management System (OMS), up to **45 minutes** post-order placement. 

#### 7.5.2 Processing Status
Once an order has been in the OMS system for more than 45 minutes, its status transitions to "Processing" (allocated to the fulfillment center floor). At this point, the API locks the order, and absolutely no address modifications can be processed by CSAs or warehouse administrators.

#### 7.5.3 Shipped Status (In-Transit Redirection)
Once an order status changes to "Shipped," modifications are subject to the following carrier constraints:
*   **Zenith Express Shipments:** Customers may request an in-transit redirection. This request must be submitted via a CSA within **4 hours** of receiving the "Shipped" email. A flat redirection fee of **$12.50** is charged to the customer's saved payment method.
*   **VeloPac & MetroCarrier (Saver Tier):** Address redirection is strictly unavailable. If the address is incorrect, the package must complete the delivery attempt cycle and return to the Kartway returns depot as "Undeliverable" before a refund minus a $15.00 restocking fee can be processed.

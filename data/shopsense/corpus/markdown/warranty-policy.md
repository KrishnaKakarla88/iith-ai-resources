# Warranty and Replacement Policy

# KARTWAY CUSTOMER OPERATIONS POLICY MANUAL
**Document ID:** POL-OPS-WAR-2024-V4  
**Effective Date:** October 24, 2024  
**Owner:** Director of Customer Operations, Kartway Retail Group  
**Applies to:** Customer Support Agents, Tier 2 Escalation Specialists, Quality Assurance Division (KQAD)

---

## 1. JURISDICTION: KARTWAY WARRANTY VS. MANUFACTURER WARRANTY

### 1.1 Kartway Direct Sales (First-Party Inventory)
For all items sold directly by "Kartway Retail Group" (indicated on the invoice by seller ID `KRG-01`), Kartway acts as the primary warranty administrator. The customer shall not be directed to the manufacturer. Kartway Quality Assurance Division (KQAD) handles all intake, diagnostics, and fulfillment under the Kartway Standard Warranty (KSW).

### 1.2 Third-Party Marketplace Sales (3P Merchants)
For items purchased from independent merchants on the Kartway Marketplace Platform:
1.2.1 Within the first 30 calendar days from the delivery date, the transaction is governed by the Kartway Return Policy. The merchant must accept the return or exchange.  
1.2.2 From day 31 through the end of the warranty period, the Manufacturer Warranty (MW) takes precedence. The customer must file their claim directly with the manufacturer.  
1.2.3 **The 14-Day Responsiveness Exception:** If the manufacturer fails to respond to the customer's written claim within 14 calendar days, or if the manufacturer has filed for bankruptcy, the customer may invoke the Kartway Marketplace Assurance Guarantee (MAG). Under MAG, Kartway will assume the warranty obligations up to a maximum liability cap of $500.00 per order ID.

---

## 2. WARRANTY COVERAGE PERIODS BY PRODUCT CATEGORY

All warranty coverage periods begin on the exact calendar day the shipment is marked as "Delivered" by the designated carrier.

| Clause | Product Category | Coverage Period | Underwriter / Administrator |
| :--- | :--- | :--- | :--- |
| **2.1** | **Consumer Electronics** (Smartphones, Tablets, Laptops, Gaming Consoles, Wearables) | 365 Calendar Days | Kartway Quality Assurance Division (KQAD) |
| **2.2** | **Major Domestic Appliances** (Refrigerators, Washing Machines, Dishwashers, Ovens) | 730 Calendar Days | ValuShield Insurance Corp (Partner ID: VS-99) |
| **2.3** | **Apparel, Footwear, & Soft Goods** (Clothing, Shoes, Luggage, Bedding) | 90 Calendar Days | Kartway Quality Assurance Division (KQAD) |
| **2.4** | **Home, Furniture, & Garden** (Indoor Furniture, Power Tools, Patio Sets) | 540 Calendar Days | Kartway Quality Assurance Division (KQAD) |
| **2.5** | **Certified Refurbished & Open-Box Items** (All categories, marked as "Grade-A Refurbished") | 180 Calendar Days | Kartway Quality Assurance Division (KQAD) |

---

## 3. WARRANTY VOIDANCE CRITERIA

An active warranty claim must be immediately rejected and closed if any of the following conditions are met during diagnostic inspection by the Apex Repair Hub:

### 3.1 Liquid and Environmental Damage
3.1.1 Activation of any internal Liquid Contact Indicator (LCI) or moisture detection sticker within the device chassis.  
3.1.2 Internal corrosion, mold, or rust inconsistent with normal indoor storage.  
3.1.3 Physical damage resulting from exposure to environmental conditions exceeding the manufacturer's rated IP (Ingress Protection) rating (e.g., exposing an IP67 device to depths greater than 1 meter or durations exceeding 30 minutes).

### 3.2 Unauthorized Modification and Repair
3.2.1 Breach, removal, or tampering of the tamper-evident security seal (e.g., "Void if Broken" stickers over internal chassis screws).  
3.2.2 Installation of non-OEM (Original Equipment Manufacturer) components, including aftermarket batteries, screens, or power units.  
3.2.3 Software modification consisting of rooting, jailbreaking, or flashing unauthorized custom firmware, resulting in a bricked state.

### 3.3 Electrical and Operational Abuse
3.3.1 Evidence of voltage spikes or electrical overstress caused by the use of non-OEM power adapters exceeding the specified input rating (e.g., applying a 24V supply to a 12V system).  
3.3.2 Use of a consumer-grade product within a commercial, industrial, or rental setting, unless the item was explicitly sold under the "Kartway Pro" product line.

---

## 4. REPAIR-VERSUS-REPLACE DECISION RULE

To optimize operations cost, agents must apply the following mathematical rules to determine whether a defective item is routed for repair or direct replacement.

```
                  [ Receive Defective Item ]
                              │
                              ▼
               [ Calculate ERC and Compare to PP ]
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
     ERC >= 60% of PP                    ERC < 60% of PP
            │                                   │
            ▼                                   ▼
  [ Proceed to REPLACEMENT ]              [ Apply Checks ]
                                                │
                          ┌─────────────────────┴─────────────────────┐
                          ▼                                           ▼
                 Meets any condition:                        Meets NO conditions:
                 - Three-Strike Rule                         - Under 3 repair claims
                 - Parts Sourcing Delay > 5 days             - Parts sourced <= 5 days
                          │                                           │
                          ▼                                           ▼
              [ Proceed to REPLACEMENT ]                    [ Proceed to REPAIR ]
```

### 4.1 The Economic Repair Threshold (ERT)
The ERT is set at **60% of the customer's net purchase price** (excluding sales tax, shipping fees, and promotional discounts applied at checkout).
*   **Formula:** `ERC (Estimated Repair Cost) = Parts Cost + Labor Cost ($45.00/hour flat rate)`
*   **Rule 4.1.1:** If `ERC >= 0.60 * Net Purchase Price`, the item is designated as **Unrepairable** and must be routed for **Replacement**.
*   **Rule 4.1.2:** If `ERC < 0.60 * Net Purchase Price`, the item must be routed for **Repair**, subject to the exceptions in Clauses 4.2 and 4.3.

### 4.2 The Three-Strike Rule
Regardless of the ERT calculation, if a single item (tracked by unique Serial Number or IMEI) is sent to the Apex Repair Hub for its third (3rd) distinct warranty repair under the same customer account, the repair path is voided. The item must be flagged as a "Lemon" and routed immediately for a brand-new **Replacement**.

### 4.3 Parts Sourcing Delay Limit
If the specialized parts required for a repair are backordered and cannot be delivered to the Apex Repair Hub within **5 business days** of the item's check-in date, the repair path must be abandoned, and the item must be processed for **Replacement**.

---

## 5. TURNAROUND COMMITMENTS AND SLA SLA

Turnaround time (TAT) measurements begin the business day following receipt of the customer's item at the designated Kartway processing facility.

### 5.1 Repair Path SLA (Turnaround: 12 Business Days)
5.1.1 The Apex Repair Hub has a maximum of **12 business days** to diagnose, repair, quality-test, and dispatch the repaired item back to the customer's registered shipping address.  
5.1.2 Tracking information for the return shipment must be updated in the Kartway Admin Portal (`KAP-01`) within 12 hours of courier pickup.

### 5.2 Replacement Path SLA (Turnaround: 3 Business Days)
5.2.1 Once an item is deemed unrepairable under Section 4, the Kartway Fulfillment Center (specifically facility `KFC-1` in Columbus, OH) has **3 business days** to dispatch an identical replacement unit.  
5.2.2 If the exact SKU is out of stock, the agent must issue a replacement of equal or greater specifications within the same brand line, or proceed to the remedy in Clause 5.3.2.

### 5.3 Breach of SLA Remedies
If Kartway fails to meet the SLAs defined in Clauses 5.1 or 5.2, the customer is automatically entitled to the following remedies:
*   **5.3.1 Delay Compensation:** A non-refundable store credit of **$15.00 per business day of delay**, capped at a maximum of $150.00.
*   **5.3.2 Full Refund Option:** If the delay exceeds **25 business days** from the initial receipt of the item, the customer may cancel the claim and demand a 100% refund returned to the original payment method. The customer shall retain ownership of the original item if it has already been repaired and shipped.

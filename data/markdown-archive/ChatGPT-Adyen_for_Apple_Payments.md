---
title: Adyen for Apple Payments
source: https://chatgpt.com/c/678014c3-e078-8003-af21-a8684ca4e5cd
---

# Adyen for Apple Payments

#### You:
<time datetime="2025-01-09T18:26:12.085Z" title="1/10/2025, 3:26:12 AM">03:26</time>

Can I use my adyen account as a receiving account for revenue from apple in app payments

#### ChatGPT:
<time datetime="2025-01-09T18:27:21.396Z" title="1/10/2025, 3:27:21 AM">03:27</time>

**Short Answer**\
Probably not. Apple generally requires a *traditional* bank account (with valid banking details such as an IBAN, routing number, and swift code) to receive App Store revenue. Most developers cannot directly link an Adyen merchant account as the “payout account” in App Store Connect.

---

## Why Apple Usually Requires a Traditional Bank Account

1. **App Store Payout Mechanism**\
   Apple pays developers through standard bank transfers (e.g., ACH in the U.S., SEPA in Europe). In your App Store Connect account (under **Payments and Financial Reports**), you must add a bank account—not a payment processor or aggregator—using conventional banking details.

2. **Compliance & Verification**\
   Apple verifies the bank account’s ownership to match the legal entity or individual name on the Apple Developer account. Third-party payment platforms (like Adyen, Stripe, Payoneer, etc.) are generally not set up to receive direct transfers as “the account of record” for App Store payouts.

3. **Supported Countries & Currencies**\
   Apple’s developer documentation lists which banks and currencies are supported. In many cases, Apple does not offer direct payouts to non-bank financial institutions, even if they can generate IBAN or routing details.

---

## Can Adyen Ever Serve as a Bank Account?

In very specific use cases—often when using products like **Adyen for Platforms** or similar solutions—Adyen might generate local IBANs or bank account details for merchants. However, there are two big caveats:

1. **Name & Tax Details Must Match**\
   Even if you have a local IBAN from Adyen, Apple will check that the *account holder name* on the IBAN matches the Apple Developer entity. If there is a mismatch, Apple is likely to reject it.

2. **Not Officially Supported**\
   Even if you technically have a “virtual” bank account through Adyen, Apple’s system may still flag it as invalid for payout. Apple does not maintain an official list of “supported payment processors,” so this would be an unconventional setup that may or may not work.

---

## Recommended Best Practice

Because Apple’s policies emphasize direct bank transfers, the common and most reliable approach is:

1. **Connect a Traditional Bank Account**\
   Use a business or personal bank account in the same legal name as your Apple Developer account.

2. **Withdraw Funds to Adyen (If Needed)**\
   Once the funds arrive in your bank account, you can then transfer funds to your Adyen account for further processing, if that’s part of your overall payment ecosystem.

---

### Summary

- **Direct Use of Adyen as Payout Account?** Likely not permitted by Apple.
- **Workaround?** Deposit Apple payments into a normal bank account, then transfer to Adyen if needed.
- **Why Not?** Apple’s payout system is designed for a standard bank, with strict matching of legal names and compliance details.

If in doubt, consult Apple’s [official documentation on banking requirements](https://help.apple.com/app-store-connect/#/devf2ab4cb38) or open a support ticket with Apple and/or Adyen to verify whether they can accommodate unusual banking arrangements.


#### You:
<time datetime="2025-01-09T18:40:00.231Z" title="1/10/2025, 3:40:00 AM">03:40</time>

Can I collect in app revenue without setting up a receiving bank account?

#### ChatGPT:
<time datetime="2025-01-09T18:40:20.786Z" title="1/10/2025, 3:40:20 AM">03:40</time>

**Short Answer**\
No. To receive payout of your in-app purchase revenue from Apple, you must have a valid bank account linked in App Store Connect.

---

## Why You Need a Bank Account

1. **Payout Processing**\
   Apple pays out earnings exclusively via direct bank transfer. Unlike some other platforms that may hold your balance or use alternative payout methods, Apple requires you to specify a bank account (with valid routing/IBAN details) to release your funds.

2. **Verification & Compliance**\
   When you create an Apple Developer account, you agree to the terms where Apple will periodically pay out the revenue you earn. As part of Apple’s compliance process, the legal name associated with your bank account must match the legal name of the individual or business on the developer account.

3. **Mandatory Setup**\
   Even if you accumulate earnings in App Store Connect, Apple typically will not release them until your bank info is complete and verified. In other words, you cannot indefinitely hold an unpaid “balance” with Apple; you must have a valid bank account on file to actually get paid out.

---

## What If I Don’t Want to Use a Traditional Bank Account?

- **Virtual Accounts**\
  Some online payment platforms or virtual bank services issue IBAN or routing details that function like a traditional bank. However, Apple still needs to be able to send an automated clearing house (ACH) or wire transfer. If Apple flags your virtual account as invalid or mismatched in name, it will be rejected.

- **No Official Alternative**\
  Apple does not offer direct payout to platforms like PayPal, Venmo, Payoneer, Adyen, or other payment processors. You may explore whether your processor can provide legitimate local bank details in your name, but there is no guarantee Apple will accept it.

---

## Bottom Line

To collect revenue from in-app purchases, **you do have to set up a valid receiving bank account** in App Store Connect. Apple will not distribute any earnings until that bank account is verified. If you have no such account, you won’t be able to actually receive the funds—even though you might see that you’ve generated revenue in your sales reports.


#### You:
<time datetime="2025-01-09T18:40:22.182Z" title="1/10/2025, 3:40:22 AM">03:40</time>

How long does it take to add a receiving bank account to apple?

#### ChatGPT:
<time datetime="2025-01-09T18:40:53.155Z" title="1/10/2025, 3:40:53 AM">03:40</time>

**Short Answer**\
It typically takes anywhere from a few hours up to a few business days for Apple to process and verify your new bank account information in App Store Connect. Most developers see the verification go through within 1–3 business days, though the exact time can vary depending on your bank and region.

---

## What to Expect During Bank Account Setup

1. **Initial Entry in App Store Connect**
   - You’ll enter your bank details (routing number, IBAN, SWIFT code, etc.).
   - If Apple’s systems can instantly validate those details, you may get immediate confirmation (though this does not always happen).

2. **Verification Process**
   - Apple may perform one or more checks, including matching the bank account owner name to your developer account name.
   - In some regions, Apple may do a small “test deposit” to confirm that the account is active and in your legal name.

3. **Possible Delays**
   - **Banking holidays or weekends** can push verification to the next business day.
   - **Incorrect or partial info** can cause rejections, which means you’ll have to re-enter details.

---

## Tips to Speed Up the Process

1. **Double-Check Banking Details**\
   Ensure your routing number (or IBAN), account number, and account holder name match exactly what your bank has on file—any mismatch is the most common reason for delays or rejections.

2. **Use a Traditional Bank Account**\
   Virtual or online-only accounts sometimes face additional scrutiny. If possible, use a traditional bank account that’s in your name or your company’s legal name (matching your Apple Developer account).

3. **Monitor Your Email and App Store Connect**
   - Apple will usually notify you if the bank details fail verification.
   - If you don’t see any progress after a few business days, check for error messages in **App Store Connect** under **Agreements, Tax, and Banking**.

---

### Bottom Line

Once you add your bank account information to App Store Connect, **plan on 1–3 business days** for Apple to verify and activate it for payouts—though it can be faster if all details match and there are no additional checks needed.


#### You:
<time datetime="2025-01-09T18:54:51.441Z" title="1/10/2025, 3:54:51 AM">03:54</time>

What specific banking details does apple require?

#### ChatGPT:
<time datetime="2025-01-09T18:55:20.162Z" title="1/10/2025, 3:55:20 AM">03:55</time>

Below are the **typical banking details** Apple requires when you add a bank account in App Store Connect. The exact requirements can vary slightly by country, but in general, you’ll be asked to provide:

1. **Account Holder Name**
   - Must match the legal name on your Apple Developer account (individual or business).
   - This is one of the most critical fields—any mismatch can cause verification delays or failures.

2. **Bank Name**
   - The official name of your bank (e.g., “Bank of America,” “HSBC,” “Deutsche Bank,” etc.).

3. **Bank Country**
   - The country where the bank account is registered.

4. **Account Number (and/or IBAN)**
   - Depending on the country, you may be prompted for a standard account number (US) or International Bank Account Number (IBAN) for most non-US accounts.
   - In the United States, you typically provide:
     - **Routing number (ABA)**
     - **Account number**
   - In the EU and many other countries, you provide the **IBAN** and possibly the **BIC/SWIFT**.

5. **BIC/SWIFT Code** (for international transfers)
   - Required in many countries outside the US to facilitate wire transfers.
   - Stands for “Bank Identifier Code” / “Society for Worldwide Interbank Financial Telecommunication.”

6. **Bank Address (Sometimes)**
   - In some regions, Apple may ask for the bank’s full address (street, city, postal code).
   - This is not always required but can be prompted depending on local regulations.

7. **Branch Code or Sort Code (Region-Specific)**
   - For countries like the UK, Australia, or India, you might see a specific “Sort Code,” “BSB,” or “IFSC” requested.

8. **Account Type** (Checking/Savings)—Primarily for US Accounts
   - In the US, Apple sometimes asks whether it’s a Checking or Savings account.

### Important Notes

- **Name Matching**: The account holder’s name must match your Apple Developer account’s legal entity name. If you’re an individual, use your personal name exactly as it appears on your bank statement. If you’re representing a company, it should be the company’s legal name.

- **Verification Process**:
  - Apple may do a **test deposit** in certain regions to confirm your bank account is active and properly linked.
  - If the test deposit or name match fails, you’ll be asked to re-enter your details.

- **Country Variations**:
  - The exact fields can change based on your country. Apple will only show you the relevant fields in **App Store Connect** under **Agreements, Tax, and Banking**.
  - Check [Apple’s official documentation](https://help.apple.com/app-store-connect/#/devf2ab4cb38) or your local bank for guidance on the correct format of your country’s bank details.

### Summary

When setting up your bank account in App Store Connect, you’ll provide standard bank-transfer information such as the **account holder name**, **IBAN or account number**, **routing number**, **SWIFT/BIC code**, **bank name**, and **bank address (if required)**. Ensuring these details match exactly what your bank has on file is crucial for a smooth verification process.

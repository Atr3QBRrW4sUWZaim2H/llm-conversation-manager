---
title: Add subscription to app
source: https://chatgpt.com/c/677f618a-9650-8003-9e64-534ca4cc182b
---

# Add subscription to app

#### You:
<time datetime="2025-01-09T05:41:30.791Z" title="1/9/2025, 2:41:30 PM">14:41</time>

i have a free ios app. what are the steps to start charging people a subscription for a set of features hat I'm about to launch

#### ChatGPT:
<time datetime="2025-01-09T05:43:22.915Z" title="1/9/2025, 2:43:22 PM">14:43</time>

Below is an overview of the high-level steps you’ll need to follow to offer subscriptions in your (currently free) iOS app. Note that these steps assume you already have an Apple Developer account and have familiarity with Xcode and App Store Connect.

---

## 1. Determine Your Subscription Model and Strategy

1. **Define the features to be paywalled**: Clearly identify which new or premium features will be accessible only to subscribers.
2. **Choose a subscription structure**: You can offer:
   - **Auto-renewable subscriptions** (most common for ongoing services).
   - **Non-renewing subscriptions** (less common, but sometimes used for fixed-term access).
3. **Decide on pricing**: Figure out what subscription price tiers you want to set (e.g., monthly, yearly) and whether you’ll provide free trials or introductory pricing.

**Tip**: For existing free users who might feel blindsided by a subscription wall, consider offering a grace period, grandfathering some features, or a free trial for a smooth transition.

---

## 2. Set Up Subscriptions in App Store Connect

1. **Go to “My Apps”** in [App Store Connect](https://appstoreconnect.apple.com/).
2. Select your **app**, then navigate to **Features > In-App Purchases** (or “Subscriptions” if you see that tab).
3. **Create a new subscription group** if you don’t already have one. (All auto-renewable subscriptions must belong to at least one group.)
4. **Add a new subscription** within that group:
   - Provide a **Reference Name** and **Product ID** (e.g., `com.yourapp.subscription.premium`).
   - **Select the subscription type** (e.g., auto-renewable).
   - **Set pricing and duration** (monthly, yearly, etc.).
   - Optionally configure **free trials** or **introductory offers**.
5. **Configure localizations**: Provide subscription display name and description for each language.
6. **Save** and **submit** for review (although the final review happens when you submit your app version).

---

## 3. Implement the Subscription Logic in Your App

1. **Integrate StoreKit** (Apple’s framework for handling in-app purchases):
   - Use the [`StoreKit`](https://developer.apple.com/documentation/storekit) APIs to fetch product information, initiate purchases, and handle subscription statuses.
2. **Fetch available products**: On app launch or at the appropriate moment, request available products from the App Store using your **product identifiers**.
3. **Display purchase UI**: Provide a clear explanation of what subscribing will unlock. Apple guidelines require transparency and a “Buy” or “Subscribe” button.
4. **Handle subscription purchases**:
   - Call `SKPaymentQueue.default().add(payment)` once a user chooses to subscribe.
   - Implement a transaction observer to listen for updates in `paymentQueue(_:updatedTransactions:)`.
5. **Verify receipts** (important for subscription validation):
   - You can do receipt validation **either on-device** or **server-side** (Apple strongly recommends server-side validation).
   - Keep track of the expiration date and subscription status.
6. **Lock/Unlock features** based on subscription status:
   - If a user’s subscription is active, unlock premium features.
   - Otherwise, show a paywall or subscription prompt.

---

## 4. Comply with Apple’s Guidelines

1. **In-App Purchases Only**: For digital content or services used within the app, Apple requires using IAP. (Don’t redirect people to a website for payment, as that violates guidelines.)
2. **Clear Pricing and Terms**: You must clearly show:
   - Subscription price and duration.
   - Auto-renewal disclaimers (if using auto-renewable subscriptions).
   - Link to your privacy policy and terms of service.
3. **Allow cancellation**: Apple’s subscription model requires you to show or guide users how to cancel if they want to (this is typically handled by Apple in iOS Settings, but you should mention it in your support documentation).

---

## 5. Test Your Subscriptions

1. **Use Sandbox**: In App Store Connect, create Sandbox test users under **Users and Access** → **Sandbox**.
2. **Run test transactions** with your sandbox accounts in a debug or TestFlight build:
   - Verify purchase flow, receipt validation, and subscription state changes.
3. **Check edge cases**: Renewal, expiration, free trial transitions, and network failures.

---

## 6. Update Your App and Submit for Review

1. **Implement the subscription UI/UX** in your app’s code and confirm everything is working properly in a sandbox environment.
2. **Bump the version number** in Xcode (e.g., to 2.0 if you’re launching premium for the first time).
3. **Archive and upload** the build to App Store Connect.
4. **Submit your app for review**. Apple will review:
   - The new subscription in-app purchase metadata.
   - The updated build of your app.

**Tip**: Make sure your in-app subscription listing is “Ready to Submit” or “Submitted” to review at the same time you submit your app build.

---

## 7. Post-Launch Considerations

1. **Monitor subscription metrics**: Track subscriber count, churn, renewals, and revenue in App Store Connect and/or your own analytics.
2. **Marketing**: Encourage free users to upgrade by highlighting premium features and their benefits within the app.
3. **Support**: Prepare FAQs regarding billing, cancellation, refunds, and subscription management to handle user support requests.

---

### Key Points to Remember

- **User Communication**: Be transparent about why you’re charging a subscription and what value you’re offering.
- **Maintain App Quality**: Even with some features going behind a paywall, your free users should still find the app usable or enticing enough to consider upgrading.
- **Adhere to Apple Guidelines**: Violations can lead to rejections during the app review process, so double-check that your paywall and subscription flows follow Apple’s rules, especially around auto-renewing subscriptions.

---

By carefully planning your subscription model, configuring it in App Store Connect, implementing the purchase logic (including proper receipt validation), and submitting for review in a compliant way, you’ll be able to transition from a free model to a subscription-based one for your premium features. Good luck!


#### You:
<time datetime="2025-01-09T05:48:59.484Z" title="1/9/2025, 2:48:59 PM">14:48</time>

2. Set Up Subscriptions in App Store Connect

    Go to “My Apps” in App Store Connect.
    Select your app, then navigate to Features > In-App Purchases (or “Subscriptions” if you see that tab).
    Create a new subscription group if you don’t already have one. (All auto-renewable subscriptions must belong to at least one group.)
    Add a new subscription within that group:
        Provide a Reference Name and Product ID (e.g., com.yourapp.subscription.premium).
        Select the subscription type (e.g., auto-renewable).
        Set pricing and duration (monthly, yearly, etc.).
        Optionally configure free trials or introductory offers.
    Configure localizations: Provide subscription display name and description for each language.
    Save and submit for review (although the final review happens when you submit your app version).

tell me more about this step. how do i connect my bank account? does apple withhold taxes? do i need to prorate or denomenate earnings over the course of a month?

#### ChatGPT:
<time datetime="2025-01-09T05:52:20.297Z" title="1/9/2025, 2:52:20 PM">14:52</time>

When you add in-app subscriptions, you’re indeed charging users directly through the App Store, but you also need to ensure you’re set up to receive payments from Apple. Below are details on how to connect your bank account, what taxes Apple may or may not handle, and how payments get reported or “prorated” over time.

---

## 1. Connecting Your Bank Account

### a. Go to Agreements, Tax, and Banking

1. **Log into App Store Connect.**
2. Click **Agreements, Tax, and Banking** on the main dashboard (left-side navigation).

### b. Accept Developer Agreements

Before you can sell apps or subscriptions, you must:

1. **Accept** the latest **Apple Developer Program License Agreement** and any relevant schedule for paid apps.
2. Under **Contracts**, look for **Paid Applications** (this contract handles subscription payments), and click **Set Up** if you haven’t already.

### c. Provide Banking Information

1. In **Bank Accounts**, add a new bank account:
   - **Bank Name, Routing Number**, Account Number, and so on.
   - Ensure the account can accept ACH/Wire transfers (depending on your region).
2. **Verify** the deposit process (in some regions, you might need to confirm micro-deposits).

Once added, you should see your bank account appear as **Active**. Apple will deposit your monthly earnings into this account.

---

## 2. Taxes and Apple’s Withholding

Apple generally does not withhold income taxes for you (especially if you’re in the U.S.). However, there are a few nuances:

1. **Apple’s Commission**:
   - Apple takes a commission (usually 30%, which can drop to 15% under certain conditions like the App Store Small Business Program or after the first year of a subscription).

2. **Sales Tax / VAT / GST**:
   - For many regions (e.g., EU countries, some U.S. states), Apple **collects and remits** sales tax (VAT/GST) directly.
   - You’ll see this as a deduction in your payment reports, but you **do not** have to handle remitting those taxes to local authorities yourself (Apple does).
   - In some countries, you may still be responsible for self-reporting certain taxes, so check local regulations.

3. **Income Tax Withholding**:
   - Typically, Apple does **not** withhold income taxes on your behalf.
   - You’ll need to report your app revenue to your local tax authority as required.
   - In some cases (especially outside the U.S.), if you’re part of the U.S. tax treaty process, you might fill out a **W-8 form** so that Apple does not withhold U.S. taxes.

4. **Forms and Documentation**:
   - In **Agreements, Tax, and Banking**, Apple will prompt you to fill out or upload necessary tax forms (e.g., W-9 for U.S. developers, W-8BEN for non-U.S., etc.).
   - This ensures compliance and clarifies your tax status with Apple.

---

## 3. Payment Timing and Reporting

### a. Payment Schedule

Apple pays out on a **monthly** cycle, generally about **30-45 days** after the end of the month in which you earned the revenue. For example:

- Revenue from January typically gets paid at the end of February or the first week of March.

### b. Payment Thresholds and Holds

- Apple may hold your payment until you reach a minimum **payment threshold** (depending on your region).
- If there are unresolved issues with your account (e.g., negative balance, bank account verification pending, etc.), this can delay payment.

### c. Financial Reports

Under **Payments and Financial Reports** in App Store Connect:

1. You can **view monthly statements**, which detail how much was earned from each app/subscription, Apple’s commission, taxes, and the **final payout**.
2. You’ll see itemized lines for:
   - Net revenue after Apple’s cut.
   - **Taxes** (like VAT) if applicable.
   - Your **final payout** amount.

---

## 4. Do You Need to Prorate or Break Down Earnings?

For auto-renewable subscriptions:

- **Apple Manages Renewal Dates**: Each subscriber has a specific billing/renewal date. Apple bills them on that day and collects the fees.
- **Monthly Statement**: Apple aggregates all subscription revenue for the month and then pays you the lump sum.
- **Partial Months**: If a user subscribes mid-month or upgrades/downgrades, Apple automatically handles any pro-rated charges/credits to the user. You simply see the net revenue in your monthly payout.
- **No Manual Proration**: You don’t have to manually calculate or distribute earnings for partial months. Apple’s system ensures that the correct charge is applied to each user’s subscription, and you receive the correct share (minus Apple’s commission and any taxes they collect/remit).

**In short:** You don’t need to manually prorate or break down daily earnings. Apple’s subscription infrastructure handles the user’s billing cycle, and you see the net result in your monthly report.

---

## 5. Practical Next Steps

1. **Complete Agreements, Tax, and Banking Setup**:
   - If you haven’t done so, make sure to **accept the Paid Apps contract** in App Store Connect and enter your bank and tax information.
2. **Configure Subscription Pricing**:
   - Set your monthly/yearly subscription tiers in App Store Connect.
   - Decide whether to offer free trials or promo pricing.
3. **Test Transactions** (with Sandbox accounts) to verify:
   - The user flow for purchasing a subscription.
   - That your app properly unlocks features.
   - That you receive correct data from Apple (via receipts, subscription status, etc.).
4. **Review Financial Reports**:
   - Once your app is live and you start getting subscribers, check **Payments and Financial Reports** to confirm everything matches your expectations.

---

### Final Tips

- **Keep Records**: Apple provides monthly statements, but you may also want to maintain your own revenue logs for accounting and tax filing.
- **Consult a Tax Professional**: Depending on your location, you may need specific guidance on how to handle subscription revenue, especially if you’re operating in multiple countries.
- **Stay Updated on Apple Policies**: Terms and rules around commissions, taxes, and developer agreements can change, so always keep an eye on official Apple announcements.

---

By following these steps—particularly setting up **Agreements, Tax, and Banking**—you’ll ensure you receive monthly payouts correctly. Apple’s system will handle the billing, renewal, and any tax withholdings for certain regions. You’ll just need to manage your own corporate or personal income taxes as required by your local government.

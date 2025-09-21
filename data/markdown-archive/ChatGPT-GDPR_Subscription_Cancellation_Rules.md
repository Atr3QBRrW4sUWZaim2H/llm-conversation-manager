---
title: GDPR Subscription Cancellation Rules
source: https://chatgpt.com/c/67929ad3-87ec-8003-9034-5eb0e2d9e9af
---

# GDPR Subscription Cancellation Rules

#### You:
<time datetime="2025-01-23T19:38:59.958Z" title="1/24/2025, 4:38:59 AM">04:38</time>

if people are paying a subscription for my ios app, and then they send me a gdpr sanitize request, can i cancel their subscription for them? does apple allow this?

#### ChatGPT:
<time datetime="2025-01-23T19:39:15.130Z" title="1/24/2025, 4:39:15 AM">04:39</time>

Under Apple’s guidelines, developers **do not** have direct control over cancelling an individual’s subscription on their behalf. That is entirely handled by Apple and the user. If someone pays for a subscription through an iOS app, the user themselves must typically manage (cancel/renew) that subscription in the App Store’s “Subscriptions” settings.

---

## Why You Can’t Cancel for the User

1. **User’s Relationship with Apple**: The user’s subscription is technically an agreement with Apple (via in-app purchases). Developers have no built-in mechanism to forcibly cancel a user’s subscription because Apple controls the payment/subscription flow.
2. **Privacy & Security**: Apple isolates financial and account control on the user’s end to protect user privacy and prevent unauthorized cancellations.
3. **Policy Constraints**: Apple’s App Store Review Guidelines specify that subscription management is a user-driven process.

---

## GDPR Angle

Under the GDPR, if you receive a data deletion (or “right to be forgotten”) request, you must remove or anonymize **all of the personal data** you control about the user. However, fulfilling this request **does not** automatically revoke their commercial relationship with Apple. You can comply with GDPR by:

1. **Removing Personal Data From Your Servers**: Delete or anonymize all personal information you control.
2. **Informing the User on Subscription Management**: Provide a clear path or instructions for the user to manage or cancel the subscription through:
   - The **App Store** on their device.
   - Contacting Apple directly (for unusual situations).

The user’s subscription will continue to exist—and they may keep getting charged—until they cancel it via Apple’s system.

---

## Best Practices

1. **In-App Instructions**: Offer a help screen or FAQ explaining how to cancel subscriptions. A quick link to “Manage Subscriptions” in iOS settings can reduce confusion.
2. **Data Deletion & Feature Access**: After you sanitize the user’s data for GDPR, you might restrict their access to your app’s features (e.g., no more personalized content). But the billing won’t stop until they unsubscribe through Apple.
3. **User Support**: Should the user have trouble cancelling, direct them to Apple Support. You cannot process the cancellation directly, but you can guide them to the correct Apple path.

---

### In Summary

- **You cannot directly cancel a user’s subscription** in response to a GDPR data deletion request.
- **Your obligation** under GDPR is to remove or anonymize the user’s personal data from your own systems.
- **The user must manage the subscription** within the App Store or contact Apple for assistance.

This setup ensures Apple remains the intermediary for billing, protecting both user privacy and your app’s compliance with the platform’s guidelines.

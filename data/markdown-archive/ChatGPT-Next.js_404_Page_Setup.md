---
title: Next.js 404 Page Setup
source: https://chatgpt.com/c/6783420a-dd70-8003-9b09-995d11a9c098
---

# Next.js 404 Page Setup

#### You:
<time datetime="2025-01-12T04:16:11.198Z" title="1/12/2025, 1:16:11 PM">13:16</time>

<!DOCTYPE html><html class="h-full"><head><meta charSet="utf-8"/><meta name="viewport" content="width=device-width"/><title>404: This page could not be found</title><meta name="next-head-count" content="3"/><link rel="preload" href="/_next/static/media/a34f9d1faa5f3315-s.p.woff2" as="font" type="font/woff2" crossorigin="anonymous" data-next-font="size-adjust"/><link rel="preload" href="/_next/static/css/1a6da92cd81ab158.css" as="style"/><link rel="stylesheet" href="/_next/static/css/1a6da92cd81ab158.css" data-n-g=""/><noscript data-n-css=""></noscript><script defer="" nomodule="" src="/_next/static/chunks/polyfills-42372ed130431b0a.js"></script><script src="/_next/static/chunks/webpack-5e3ffe9897f64986.js" defer=""></script><script src="/_next/static/chunks/framework-95e32d7d538f2386.js" defer=""></script><script src="/_next/static/chunks/main-440d5d3a927320ce.js" defer=""></script><script src="/_next/static/chunks/pages/_app-67361d677e702111.js" defer=""></script><script src="/_next/static/chunks/pages/_error-3436fc32a9da8d8e.js" defer=""></script><script src="/_next/static/gTbRIVFq7UEJXX8yJ_3nt/_buildManifest.js" defer=""></script><script src="/_next/static/gTbRIVFq7UEJXX8yJ_3nt/_ssgManifest.js" defer=""></script><style id="__jsx-3064908113">body{--font-inter:'__Inter_179fbf', '__Inter_Fallback_179fbf'}</style></head><body class="h-full bg-white text-black dark:bg-[--main-dark-color] dark:text-white transition-colors"><div id="__next"><div style="font-family:system-ui,&quot;Segoe UI&quot;,Roboto,Helvetica,Arial,sans-serif,&quot;Apple Color Emoji&quot;,&quot;Segoe UI Emoji&quot;;height:100vh;text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center"><div style="line-height:48px"><style>body{color:#000;background:#fff;margin:0}.next-error-h1{border-right:1px solid rgba(0,0,0,.3)}@media (prefers-color-scheme:dark){body{color:#fff;background:#000}.next-error-h1{border-right:1px solid rgba(255,255,255,.3)}}</style><h1 class="next-error-h1" style="display:inline-block;margin:0 20px 0 0;padding-right:23px;font-size:24px;font-weight:500;vertical-align:top">404</h1><div style="display:inline-block"><h2 style="font-size:14px;font-weight:400;line-height:28px">This page could not be found<!-- -->.</h2></div></div></div><div id="_rht_toaster" style="position:fixed;z-index:9999;top:16px;left:16px;right:16px;bottom:16px;pointer-events:none"></div></div><script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{"statusCode":404,"_sentryTraceData":"af5af3ff623640ec8edc3069a43fd892-8f8f3541c078f770-0","_sentryBaggage":"sentry-environment=vercel-production,sentry-release=7480dfc1b1ad5cae784c0b5cccb0f433c71b5291,sentry-public_key=e1b189841c384830b9c321a7f0672f9d,sentry-trace_id=af5af3ff623640ec8edc3069a43fd892,sentry-sample_rate=0.01,sentry-transaction=%2F_error,sentry-sampled=false"}},"page":"/_error","query":{"_nextBubbleNoFallback":"1"},"buildId":"gTbRIVFq7UEJXX8yJ_3nt","isFallback":false,"isExperimentalCompile":false,"gip":true,"scriptLoader":[]}</script></body></html>


#### ChatGPT:
<time datetime="2025-01-12T04:16:51.386Z" title="1/12/2025, 1:16:51 PM">13:16</time>

It looks like you’ve come across a standard **Next.js 404 page**. In a Next.js project, if a user tries to visit a route that the application can’t match, Next.js automatically serves up this fallback 404 page. Here’s some background and a few tips on how you can work with or customize the 404 experience:

---

## Why You’re Seeing This 404 Page

- **File-based routing**: Next.js determines which page to serve based on your `/pages` directory (or `/app` folder if you’re using the newer App Router in Next.js 13+). If the user navigates to a path that doesn’t match any file in your routing structure, Next.js serves the default 404 page.
- **Missing page or route**: Sometimes a missing or incorrectly named file (e.g., `about.js` instead of `[...slug].js`) results in a 404.
- **Deployment routing issues**: If you’ve set up rewrites or redirects in your `next.config.js` or in a hosting environment, a misconfiguration can also trigger this 404.

---

## Customizing the 404 Page

One of Next.js’s strengths is how easy it is to create a custom 404 page:

- **In the Pages Router** (Next.js versions < 13 or if you haven’t adopted the App Router):
  1. Create a file at `/pages/404.js`.
  2. Export a React component from that file.
  3. Next.js will use that component as the official 404 page for your app.

- **In the App Router** (Next.js 13+):
  1. Create a file named `not-found.js` in your relevant route folder (for example, `app/not-found.js` if you want a global 404).
  2. Next.js will use that component whenever a route is not found.

### Example `404.js` (Pages Router)

```jsx
function Custom404() {
  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Oops! Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
    </div>
  );
}

export default Custom404;
```

### Example `not-found.js` (App Router)

```jsx
export default function NotFound() {
  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>404</h1>
      <p>This page could not be found.</p>
    </div>
  );
}
```

---

## Helpful Tips & Best Practices

1. **SEO Considerations**
   - Having a descriptive 404 page with helpful navigation or suggestions can improve user experience and help search engines understand your site structure.
   - Include links back to key areas of your site so visitors can recover if they end up on a 404.

2. **Custom Error Boundaries**
   - While 404 pages are for missing routes, errors within your app (like JavaScript exceptions) often display a different Next.js error screen during development. Consider implementing [React Error Boundaries](https://react.dev/docs/error-boundaries.html) for production to gracefully handle unexpected errors.

3. **Sentry or Other Error Tracking**
   - Tools such as [Sentry](https://sentry.io/) can be integrated to track both client- and server-side errors, including 404s. This can help you identify broken links and missing routes.

4. **Dynamic Routing & Fallback**
   - With Next.js, you can create dynamic routes (like `[slug].js` in Pages Router or `[slug]/page.tsx` in the App Router). When using [Incremental Static Regeneration (ISR)](https://nextjs.org/docs/basic-features/data-fetching/incremental-static-regeneration) or a `fallback` configuration, some missing pages might generate 404s until the content is dynamically generated.

5. **Handling Redirects**
   - If you’ve recently removed or reorganized pages, remember to set up [redirects](https://nextjs.org/docs/api-reference/next.config.js/redirects) in `next.config.js` so old links don’t just lead to 404s.

---

## Summary

Seeing this HTML snippet basically means you’ve hit a route in your Next.js app that doesn’t exist (or a fallback Next.js 404 page is being rendered). If you want to customize what your users see when they land on a not-found page, just add a dedicated `404.js` (for the Pages Router) or `not-found.js` (for the App Router).

Whether you’re exploring front-end frameworks, serverless deployments, or advanced concepts like Incremental Static Regeneration, Next.js has a flexible routing system that makes handling 404s and other errors straightforward.

If you have further questions about customizing or debugging 404 issues—such as SEO considerations, tracking not-found pages, or implementing advanced routing—feel free to ask!

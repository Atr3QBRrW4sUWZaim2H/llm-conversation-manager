---
title: PWA macOS Process Merging
source: https://chatgpt.com/c/6785cda0-6960-8003-a834-67e034fffb35
---

# PWA macOS Process Merging

#### You:
<time datetime="2025-01-14T02:36:16.806Z" title="1/14/2025, 11:36:16 AM">11:36</time>


Skip to content
Navigation Menu

    filips123

    PWAsForFirefox

Code
Issues 65
Pull requests 1
Discussions
Actions
Projects 1
Wiki

All PWAs in the same profile are merged with the first PWA that was opened (macOS-only) #81
Open
filips123 opened this issue Nov 9, 2021 · 3 comments
Comments
@filips123
Owner
filips123 commented Nov 9, 2021
Description

All PWAs are merged with the first PWA that was opened. This only applies to macOS.

When some PWA is already running, all newly launched PWAs will merge with it and remain merged until all of them are closed. This will cause the app menu to display all PWAs as part of the first PWA that was launched, with its icon and desktop actions (if any).

Users can prevent this by installing each PWA into a different profile.
Steps to Reproduce

    Install at least two different PWAs into the same profile.
    Launch the first PWA.
    See that it has the correct icon.
    Launch another PWA without closing the first one.
    See that is merged with the first one and has the wrong icon.

Possible Solution

Apple only allows a process to be associated with a single application at all times. Perhaps this could be solved by using an IPC link between a host process and the main Firefox runtime process, the same way the Firefox parent process handles its content processes. This is just a wild theory though and has to be investigated further. See this comment for more.
@filips123 filips123 added the bug label Nov 9, 2021
@filips123 filips123 mentioned this issue Nov 9, 2021
Implement System Integration on macOS #33
Closed
@filips123 filips123 added this to PWAsForFirefox Dec 26, 2021
@filips123 filips123 moved this to On Hold in PWAsForFirefox Dec 26, 2021
@filips123 filips123 mentioned this issue Jun 22, 2022
reopening a PWA after closing all windows opens new tab page #42
Closed
filips123 added a commit that referenced this issue Jul 31, 2022
@filips123
Fix reopening web app after closing all windows on macOS (fixes #42)
434189f
@filips123 filips123 mentioned this issue Sep 17, 2022
Install new app in new profile by default #216
Closed
@dmose
dmose commented Nov 7, 2022

From the comment linked to in the issue description:

    Maybe. Gecko uses IPC links internally to render websites in its content processes, but display them in the window of the parent process. Here is a brief explanation from back in 2013 when it was first implemented. I think we might also be able to use the same IPC protocol between our host process and the main Firefox runtime, but there is not much public documentation on how exactly this works. I think we would have to find a gecko engineer who can tell us if a gecko is ready for such a setup or how much work it would be to make it possible.

Since that comment was written by @TitanNano, I believe the IPC documentation has gotten substantially better. If that doesn't have what you need, reach out to me on chat.mozilla.org (I'm dmosedale@mozilla.com there), and I can perhaps find a gecko engineer who knows more...
@julian-klode
julian-klode commented Aug 16, 2023

I also see this on GNOME on Ubuntu on Wayland, I moved two apps into the default profile and then the app I open second is grouped with the app I open first.
@filips123 filips123 mentioned this issue Aug 16, 2023
All PWAs in the same profile are merged with the first PWA that was opened (Linux Wayland-only) #80
Closed
@filips123
Owner Author
filips123 commented Aug 16, 2023

@julian-klode I reopened and created a comment in #80 because that is the issue for this problem on Linux.

@dmose Sorry for quite the late reply and thanks for that. I don't know much about macOS development and Gecko internals (and neither have a good setup for testing that, except quite a slow VM), so I'm afraid I won't be able to do this. However, if anyone else can try to implement this, I will try to help where I can.

One other possible problem is that I won't want to fork Firefox, as maintaining the infrastructure to build and ship all updates to users would be too hard, and it would also make it harder to use alternative Firefox-based browsers. So, if possible, the required changes to Firefox should be upstreamed, or the IPC should be somehow called from this project's own code (maybe from the Rust part or UserChromeJS).

Another relevant issue is #42. I created a workaround that only works with separate profiles, so when/if this issue is fixed, a fix for that one should also be reworked.
@wbywfjptrgmuMJxByvFD
Add a comment
Comment

Add your comment here...
Remember, contributions to this repository should follow its contributing guidelines and security policy.
Show your support for filips123 by sponsoring them.
Assignees
No one assigned
Labels
bug
Projects
PWAsForFirefox
Status: On Hold
Milestone
No milestone
Development

No branches or pull requests

You’re not receiving notifications from this thread.
3 participants
@dmose
@julian-klode
@filips123
Footer
© 2025 GitHub, Inc.
Footer navigation

    Terms
    Privacy
    Security
    Status
    Docs
    Contact



#### ChatGPT:
<time datetime="2025-01-14T02:37:01.335Z" title="1/14/2025, 11:37:01 AM">11:37</time>

Below is a **summary** and some **contextual commentary** around the GitHub conversation you shared, with added notes on relevant terminologies and insights for those interested in how PWAs, user profiles, and multi-process architecture (like Gecko’s IPC) can be made to work together—especially if you’re coming from a background in broader software development, parallel processing, or even HPC.

---

## **What the Issue Describes**

1. **Problem**:
   - On macOS (and later found on GNOME/Wayland as well), when you install multiple Progressive Web Apps (PWAs) via the same Firefox profile, they merge into the same application instance.
   - Visually, this means the operating system’s app switcher (or the dock on macOS) shows only one application icon, rather than separate icons for each PWA.

2. **Key Takeaway**:
   - **Why?** Apple (macOS) and some Linux desktop environments often associate a single process with a single app identity. So if you open a new PWA in the same profile, it reuses the same underlying Firefox process.

3. **Current Workaround**:
   - Install each PWA in a **separate Firefox profile**. This way, each app can (in theory) spawn from a different profile directory, thus having a unique identifier and process context.

4. **Proposed Ideas**:
   - **IPC (Inter-Process Communication)**:
     - The developer references how Gecko (the Firefox rendering engine) uses IPC internally to render content in separate processes. They propose some form of bridging or adapting that IPC model for PWAs, enabling each installed web app to appear as its own application identity.
   - **Upstreaming Changes to Firefox**:
     - Since forking Firefox and maintaining a custom build is not feasible long-term (for security updates, distribution, and broader usage with derivatives like LibreWolf, Waterfox, etc.), a better solution would be to push these changes upstream to Mozilla or to leverage an existing stable API/IPC.

5. **Related Issues**:
   - \#42: Addresses how reopening a PWA after closing all windows can inadvertently open a new tab. There’s a partial fix that also depends on how profiles are handled.

---

## **Why This Matters (and Broader Lessons)**

1. **PWAs and Desktop Integration**:
   - PWAs are typically web apps bundled in a way that makes them act like native desktop apps (e.g., icons, separate windows, etc.).
   - On platforms like Windows, each PWA can easily appear as a standalone process because the OS supports it well. On macOS and some Linux DEs (Wayland, GNOME, etc.), it’s trickier due to how process-app associations work.

2. **Firefox Multiprocess (Electrolysis/e10s)**:
   - Firefox famously introduced multi-process architecture (codenamed “Electrolysis” or **e10s**) to separate web content from the browser’s main process for security and performance.
   - This is done via an IPC mechanism. Each “content process” is controlled by the parent process.
   - The conversation hints at possibly hooking into that same mechanism so that each PWA can run in a separate “container” or “content process” but still be recognized by the OS as a separate application.

3. **Profiles as ‘Sandboxing’**:
   - If you’re familiar with HPC or containerization, you can think of profiles in a slightly analogous way to “sandboxing” or “namespacing.” Each profile has its own settings, cookies, local storage, and now (potentially) its own application identity.
   - The advantage is that a profile physically separates disk artifacts (like local databases, config files, caches), so it’s somewhat like a lightweight container for your app.

4. **Potential HPC Angle (if you’re curious)**:
   - While HPC often deals with large-scale data processing, the underlying concept of **process separation and concurrency** is relevant in smaller-scale multi-process architectures too. The solution folks are discussing here is about isolating processes so that each PWA runs independently.
   - If you’ve ever used container orchestration (like Docker or Kubernetes) for HPC tasks, the principle is similar: the environment is isolated to avoid conflicts. In the PWA realm, separate Firefox profiles are the quick fix. A deeper OS-level or browser-level fix might be akin to re-engineering how the browser spawns new processes under the hood.

---

## **Key Terms & Concepts to Explore Further**

1. **IPC (Inter-Process Communication)**:
   - Mechanisms: Pipes, sockets, shared memory, etc.
   - In Firefox’s context, a custom protocol is used to communicate between the parent process and content processes.

2. **Electrolysis (e10s)**:
   - Mozilla’s multi-process architecture introduced around Firefox 48 (2016).

3. **PWAs**:
   - Key attributes: Service Workers, Web App Manifest, offline capability, etc.
   - Desktop integration can be trickier for cross-platform consistency (Windows vs. macOS vs. Linux variants).

4. **Profiles in Firefox**:
   - Each profile stores extensions, cookies, local storage, and can even isolate entire sets of browsing data.
   - Using a dedicated profile per app ensures it launches in a separate process context, but is less user-friendly than having them all in one profile.

5. **Wayland vs. X11 on Linux**:
   - On Wayland, some window-handling intricacies differ from older X11. This leads to additional complexity in how a “window” or “app” is recognized.

---

## **Conclusion**

- The GitHub issue you shared is essentially about **how to give each installed PWA on macOS (and potentially on Wayland) its own unique process and identity** so that the operating system recognizes them as distinct apps.
- **Short-Term Fix**: Use separate Firefox profiles.
- **Long-Term Fix**: Possibly integrate or adapt Firefox’s existing multiprocess approach with an IPC solution that “fakes” multiple app identities. But this would ideally need upstream buy-in from Mozilla to avoid maintaining a fork.
- For developers and enthusiasts—especially those interested in parallel processing or HPC—the conversation about multi-process architecture parallels how tasks or containers are isolated in other domains. The difference is we’re applying it to the user-facing PWA environment rather than large-scale computational tasks.

Hopefully, this gives you a clearer, high-level view of the discussion and some interesting directions to explore, whether you are looking into macOS system internals, Wayland behaviors, or multi-process design patterns in general.


#### You:
<time datetime="2025-01-16T00:23:06.228Z" title="1/16/2025, 9:23:06 AM">09:23</time>

it looks like one of my PWAs are running out of space. how can  i increase the allocated space?

#### ChatGPT:
<time datetime="2025-01-16T00:24:06.596Z" title="1/16/2025, 9:24:06 AM">09:24</time>

Below is some **context and practical guidance** on how to increase storage for a PWA in Firefox. Since you’ve expressed interest in deeper, technical topics (like concurrency or containerization in HPC), I’ll also include a quick background on how PWAs store data and how that might align with broader multi-process or sandboxed environments.

---

## **1. How PWAs Store Data**

A PWA typically caches site resources and stores application-specific data using the following mechanisms:

- **Cache Storage (via Service Workers)**
- **IndexedDB**
- **LocalStorage or SessionStorage** (less commonly used for large storage)

In Firefox (as well as other browsers), these data stores are subject to **quota limits**. Typically, the browser calculates a maximum storage quota per site/pwa, which can vary depending on system free space, the user’s history with that domain, and whether the user has granted “persistent” or “temporary” storage permissions.

---

## **2. Why the Quota Gets Exceeded**

1. **Large offline data**: PWAs with extensive offline capabilities (for instance, offline HPC-related data, large data sets, or media files) can quickly fill up the default quota.
2. **Single Profile**: If you’re using a single Firefox profile for multiple PWAs (e.g., using the same “Default” profile), they can collectively bump up against global limits for storage.

---

## **3. Potential Ways to Increase or Manage PWA Storage in Firefox**

### **A. Requesting ‘Persistent’ Storage Programmatically**

If you’re the developer of the PWA, you can leverage the [Storage Manager API](https://developer.mozilla.org/en-US/docs/Web/API/StorageManager) to request persistent storage, which can help ensure that data isn’t evicted.

```javascript
if (navigator.storage && navigator.storage.persist) {
  navigator.storage.persist().then(persistent => {
    if (persistent) {
      console.log("Storage will not be cleared except by explicit user action");
    } else {
      console.log("Storage may be cleared by the UA under storage pressure.");
    }
  });
}
```

> **Note**: This doesn’t *force* the browser to grant you more space outright, but it does prevent data eviction under storage pressure. Firefox often allows more space for domains that have been granted persistent storage.

### **B. Using Separate Firefox Profiles for Each PWA**

As discussed in the GitHub thread, installing each PWA into its own Firefox profile helps in two ways:

1. Each profile has its own quota calculation.
2. PWAs are less likely to conflict or merge under a single Firefox process identity (useful especially on macOS or Wayland).

**How to do it**:

- Open Firefox’s **Profile Manager** (for instance, run `firefox --ProfileManager` from a terminal).
- Create a new profile, launch Firefox with that profile, and then install the PWA from that new instance.

### **C. Checking or Adjusting IndexedDB/Local Storage Limits (about:config)**

Firefox’s dynamic storage allocation doesn’t have a simple GUI slider to “just increase storage,” but you can look under **`about:config`** for advanced settings related to:

- `dom.indexedDB.enabled`
- `dom.storageManager.enabled`
- `dom.quotaManager.enabled`

In most modern Firefox versions, these are enabled by default, but you can verify.

> **Caution**: Tweaking internal quotas via `about:config` (like `dom.indexedDB.warningQuota`) can be tricky and sometimes not well-documented. Changes may affect stability or introduce unknown behaviors.

### **D. Managing Offline Data via Firefox Settings**

In recent versions of Firefox:

1. Go to **Settings** (Preferences) → **Privacy & Security** → **Cookies and Site Data** → **Manage Data**.
2. Here, you’ll see sites (including installed PWAs) that are storing data.
3. While you can’t directly “expand” their quota here, you can clear unused data from other sites to free up global space.

---

## **4. If You’re Working with Large or HPC-Style Datasets**

For very large offline data sets (e.g., HPC or scientific data in a PWA-like environment):

1. **Hybrid Approach**: Store frequently accessed small data in IndexedDB (client-side), but keep large data sets on a server or in a local server-like database.
2. **Local Node Server**: If you truly need gigabytes of local data for HPC tasks, you might consider running a minimal Node.js or Python server on the same machine, letting your “PWA” talk to it via `localhost`.
3. **Containerization**: Think of each PWA as a container that can be spun up with its own data environment, akin to Docker containers. This analogy can help conceptually if you’re used to HPC or parallel computing: each container (or profile) has its own namespace, dependencies, and stored data.

---

## **5. Bottom Line**

- **Short-Term “User-Level” Fix**: Either use separate profiles or carefully purge unused data from other sites to free up quota.
- **Deeper “Developer-Level” Fix**: Request [persistent storage](https://developer.mozilla.org/en-US/docs/Web/API/StorageManager/persist) and reduce data usage by adopting best practices for offline caching.
- **Advanced Tweaks**: (For power users) Adjust `about:config` settings, but proceed with caution.

---

### **In Summary**

Increasing allocated space for a PWA isn’t as simple as clicking “Add more GB” in Firefox, because **browser-based storage** is governed by dynamic quotas and user permissions. By requesting persistent storage, managing separate profiles, or employing an architecture that stores large data sets outside the browser, you can usually mitigate issues around running out of space.

If your PWA is tied to bigger HPC or data-science workflows, you might find parallels between containerizing apps for HPC and isolating PWAs in separate Firefox profiles—both ensure that each environment has its own resources and avoids interfering with one another.

*Hopefully this helps you get more breathing room for your PWA data and offers a broader technical context that aligns with your interests in multi-process or HPC-like concepts!*

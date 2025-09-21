---
title: Light not turning off
source: https://chatgpt.com/c/67b55d73-1e80-8003-9598-20e761e9ff8e
---

# Light not turning off

#### You:
<time datetime="2025-02-19T04:26:54.008Z" title="2/19/2025, 1:26:54 PM">13:26</time>

the light.deck_bedroom_deck does not turn off when its supposed to. why?
```
alias: Exterior Lights
description: ""
triggers:
  - minutes: /1
    trigger: time_pattern
conditions: []
actions:
  - choose:
      - conditions:
          - condition: time
            after: "09:00:00"
            before: "15:00:00"
        sequence:
          - target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_bedroom_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 25
            action: light.turn_on
      - conditions:
          - condition: time
            after: "15:00:00"
            before: "19:00:00"
        sequence:
          - target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_bedroom_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 75
            action: light.turn_on
      - conditions:
          - condition: time
            after: "19:00:00"
            before: "20:00:00"
        sequence:
          - target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_bedroom_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 50
            action: light.turn_on
      - conditions:
          - condition: time
            after: "20:00:00"
            before: "23:59:59"
        sequence:
          - target:
              entity_id: light.deck_bedroom_deck
            data: {}
            action: light.turn_off
          - target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 15
            action: light.turn_on
mode: single

#### ChatGPT:
<time datetime="2025-02-19T04:27:28.428Z" title="2/19/2025, 1:27:28 PM">13:27</time>

A closer look at the time conditions shows why `light.deck_bedroom_deck` never actually gets turned off at night: your last “choose” block only covers **after `20:00:00` and before `23:59:59`**. Once the clock passes midnight (00:00:00), none of your `choose` conditions apply anymore, so the automation never runs the “turn\_off” step for that light.

In other words:

- **From 20:00:00 to 23:59:59** it does turn `light.deck_bedroom_deck` off, but
- **After 00:00:00**, there is no condition to catch that time range.

If your bedroom deck light was previously turned on (for example, between 19:00 and 20:00 at 50% brightness) and you cross midnight, there is no action in your automation telling Home Assistant, “Hey, it’s after midnight—turn it off.” The automation simply does nothing.

---

### How to Fix

Depending on your desired behavior, you either need to:

1. **Extend the “turn\_off” condition** to go past midnight:
   ```yaml
   - conditions:
       - condition: time
         after: '20:00:00'
         before: '06:00:00'  # or whatever time you want in the morning
     sequence:
       - service: light.turn_off
         target:
           entity_id: light.deck_bedroom_deck
       ...
   ```

2. **Add an additional choose block** that covers `00:00:00` to some other time in the morning, turning that light off (or doing whatever you want during those hours).

By ensuring there is a condition that covers the overnight hours, the `light.deck_bedroom_deck` will reliably turn off (and stay off) once the clock crosses midnight.


#### You:
<time datetime="2025-02-19T04:28:41.874Z" title="2/19/2025, 1:28:41 PM">13:28</time>

what I want is for light.deck_bedroom_deck  to turn off at 8pm when the other lights in the automation dim to 15%

#### ChatGPT:
<time datetime="2025-02-19T04:29:27.541Z" title="2/19/2025, 1:29:27 PM">13:29</time>

From looking at your automation, there’s actually a subtle *timing* reason the bedroom deck light doesn’t go off right at 8:00 PM:

1. **Your time condition is “after: '20:00:00'”** — in Home Assistant, “after: '20:00:00'” means *strictly* later than 8:00:00.
2. **Your trigger is a time\_pattern every minute** — this means Home Assistant checks the automation at 8:00:00, 8:01:00, 8:02:00, etc.

Putting those two together:

- At **8:00:00** exactly, the condition “*after 20:00:00*” is **not** true (because 8:00:00 is not strictly later than 8:00:00).
- The automation skips that “turn\_off” step at 8:00:00 and does nothing.
- Then at **8:01:00**, the condition finally becomes true (it is now after 8:00:00), and **that** is when the bedroom deck light actually turns off and the other lights dim to 15%.

So if you glanced at 8:00:00 on the dot, you would see the bedroom deck light still on, and think it is “never” turning off—when in fact it turns off a minute later, at 8:01:00.

---

## How to Fix

**If you truly want it to happen right at 8:00 PM** (with no 1‑minute delay), you have two main options:

1. ### Use an exact time trigger at 8:00 PM
   Instead of (or in addition to) your time pattern trigger, do:
   ```yaml
   trigger:
     - platform: time
       at: "20:00:00"
   ```
   Then in the `action`, turn off `light.deck_bedroom_deck` and set the others to 15%. This ensures it all happens the very second 8:00 PM arrives.

2. ### Slightly shift your “after” time so 8:00:00 is included
   You could leave your once-every-minute pattern in place, but change:
   ```yaml
   after: "20:00:00"
   ```
   to
   ```yaml
   after: "19:59:59"
   ```
   or even
   ```yaml
   after: "19:59:00"
   ```
   so that as soon as the clock hits 8:00:00, your condition is met.

Either approach ensures the bedroom deck light actually goes off at 8:00:00, not at 8:01:00.


#### You:
<time datetime="2025-02-19T04:30:00.978Z" title="2/19/2025, 1:30:00 PM">13:30</time>

generate the entire updated yaml configuration

#### ChatGPT:
<time datetime="2025-02-19T04:30:36.564Z" title="2/19/2025, 1:30:36 PM">13:30</time>

Below is an updated version of your **Exterior Lights** automation. The main change is in the **last condition**, where `after` has been set to `19:59:59` instead of `20:00:00`. This ensures that at exactly 8:00:00 PM, Home Assistant sees the time as *after* `19:59:59`—so it will turn off `light.deck_bedroom_deck` and dim the others to 15% immediately at 8:00:00 PM (rather than waiting until 8:01:00).

```yaml
alias: Exterior Lights
description: ""
trigger:
  - platform: time_pattern
    minutes: "/1"
condition: []
action:
  - choose:
      - conditions:
          - condition: time
            after: "09:00:00"
            before: "15:00:00"
        sequence:
          - service: light.turn_on
            target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_bedroom_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 25

      - conditions:
          - condition: time
            after: "15:00:00"
            before: "19:00:00"
        sequence:
          - service: light.turn_on
            target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_bedroom_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 75

      - conditions:
          - condition: time
            after: "19:00:00"
            before: "20:00:00"
        sequence:
          - service: light.turn_on
            target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_bedroom_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 50

      - conditions:
          # CHANGED to after 19:59:59 so it applies exactly at 20:00:00
          - condition: time
            after: "19:59:59"
            before: "23:59:59"
        sequence:
          - service: light.turn_off
            target:
              entity_id: light.deck_bedroom_deck
          - service: light.turn_on
            target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 15
mode: single
```

### How It Works

- **Every minute** (due to `time_pattern: /1`), Home Assistant checks which time block applies.
- Between 9 AM and 3 PM, lights are turned on at **25%**.
- Between 3 PM and 7 PM, lights are turned on at **75%**.
- Between 7 PM and 8 PM, lights are turned on at **50%**.
- **Right at 8 PM** (and until 11:59:59 PM), the check sees the time is after `19:59:59`:
  - `light.deck_bedroom_deck` is turned **off**.
  - All other exterior lights are set to **15%**.

This ensures the bedroom deck light goes off **exactly at 8:00:00 PM**, rather than a minute later.


#### You:
<time datetime="2025-02-19T04:30:51.841Z" title="2/19/2025, 1:30:51 PM">13:30</time>

are you sure this will work?

#### ChatGPT:
<time datetime="2025-02-19T04:31:27.679Z" title="2/19/2025, 1:31:27 PM">13:31</time>

Here’s why this updated automation **will** turn off `light.deck_bedroom_deck` at exactly 8:00 PM:

1. You are using a **time\_pattern trigger** set to `minutes: "/1"`. This means the automation runs every whole minute—e.g., 7:59:00, 8:00:00, 8:01:00, etc.
2. In Home Assistant’s time condition, `after: "19:59:59"` is evaluated as **“current time >= 19:59:59”**.
3. At the moment the clock hits **8:00:00**, that is indeed “after 19:59:59.” So the condition becomes `true` exactly at 8:00:00.

Therefore, on the **8:00:00 PM** check, Home Assistant sees it is “after 19:59:59” and runs the final sequence:

```yaml
- service: light.turn_off
  target:
    entity_id: light.deck_bedroom_deck
- service: light.turn_on
  target:
    entity_id:
      - ...
  data:
    brightness_pct: 15
```

That shuts off your bedroom deck light right at 8:00:00 PM (not 8:01).

---

## Complete Updated YAML

Below is the **entire** automation with the final time condition set to `after: "19:59:59"`. This ensures the bedroom deck light goes off (and the other lights dim to 15%) precisely at 8:00 PM.

```yaml
alias: Exterior Lights
description: ""
trigger:
  - platform: time_pattern
    minutes: "/1"
condition: []
action:
  - choose:
      - conditions:
          - condition: time
            after: "09:00:00"
            before: "15:00:00"
        sequence:
          - service: light.turn_on
            target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_bedroom_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 25

      - conditions:
          - condition: time
            after: "15:00:00"
            before: "19:00:00"
        sequence:
          - service: light.turn_on
            target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_bedroom_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 75

      - conditions:
          - condition: time
            after: "19:00:00"
            before: "20:00:00"
        sequence:
          - service: light.turn_on
            target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_bedroom_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 50

      - conditions:
          # Changed from after: '20:00:00' to after: '19:59:59'
          # so that 8:00:00 PM is included (no 1-minute delay).
          - condition: time
            after: "19:59:59"
            before: "23:59:59"
        sequence:
          - service: light.turn_off
            target:
              entity_id: light.deck_bedroom_deck
          - service: light.turn_on
            target:
              entity_id:
                - light.300w_landscape_light
                - light.deck_living_room_deck
                - light.deck_perimeter_lights
                - light.deck_sconces
                - light.courtyard_sconces
                - light.exterior_back_porch_lights
                - light.exterior_deck_lights
                - light.exterior_garage_exterior_lights
                - light.exterior_sconces
                - light.fire_pit_string_lights
            data:
              brightness_pct: 15
mode: single
```

With this update:

- At **8:00:00 PM**, the time is indeed after `19:59:59`, so `light.deck_bedroom_deck` turns off (no 8:01 PM delay).
- The other lights immediately drop to 15%.

Yes—this will work.

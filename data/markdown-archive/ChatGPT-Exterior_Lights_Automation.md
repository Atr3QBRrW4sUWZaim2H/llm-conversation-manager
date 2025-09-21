---
title: Exterior Lights Automation
source: https://chatgpt.com/c/67b3f4f8-c2dc-8003-b97e-3412680fa84c
---

# Exterior Lights Automation

#### You:
<time datetime="2025-02-18T02:48:24.953Z" title="2/18/2025, 11:48:24 AM">11:48</time>

what does this automation do?
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
<time datetime="2025-02-18T02:48:35.981Z" title="2/18/2025, 11:48:35 AM">11:48</time>

This automation (in YAML format for Home Assistant) checks every minute (via the `time_pattern` trigger with `minutes: /1`) and then sets various exterior lights to different brightness levels (or turns them off) based on the time of day. Specifically:

1. **Time Range 09:00–15:00**
   - All listed lights turn **on** at **25%** brightness.

2. **Time Range 15:00–19:00**
   - All listed lights turn **on** at **75%** brightness.

3. **Time Range 19:00–20:00**
   - All listed lights turn **on** at **50%** brightness.

4. **Time Range 20:00–23:59:59**
   - The `light.deck_bedroom_deck` is turned **off**.
   - The remaining lights are turned **on** at **15%** brightness.

### Why it checks every minute

The trigger’s `time_pattern` with `minutes: /1` means it fires once each minute. On each trigger, the automation evaluates its set of `choose` conditions and then executes the appropriate action for the current time window. You can think of this as a safeguard: if for some reason the lights are out of sync with the intended brightness, they will be corrected within a minute.

### Key Home Assistant concepts highlighted

1. **Trigger (time\_pattern)** – This type of trigger runs based on matching a time pattern. Here, the pattern is `minutes: /1`, so it effectively runs every minute.
2. **Choose Action** – The `choose:` block in Home Assistant allows branching logic. Each “choice” has a condition (in this case, a time condition) and a sequence of actions. If the first condition isn’t met, it goes to the next one, and so on.
3. **Time Condition** – The `condition: time` checks if the current time is between two specified points (e.g., `after: "09:00:00"` and `before: "15:00:00"`).
4. **Light Control** – `light.turn_on` with `brightness_pct` sets the brightness level as a percentage. In Home Assistant, you can also specify `brightness` in raw integer values (`0–255`) or use `brightness_step_pct` to increase or decrease brightness by a certain percentage.
5. **Entity Targeting** – Multiple entities can be targeted together, as shown with the list of exterior lights. This saves writing multiple lines for the same action.

### Potential enhancements or related ideas

- **Transitions**: You could add a `transition:` parameter (in seconds) to gradually fade lights in or out rather than switching instantly at a new brightness level.
- **Color Temperature or RGB**: If these lights support color temperature or RGB, you might also see parameters like `color_temp` or `rgb_color` in a similar action.
- **Adaptive Lighting**: Some users integrate with an adaptive lighting system that automatically adjusts brightness or color temperature based on local sunrise, sunset, and circadian rhythms.
- **Scheduler or UI**: Instead of editing YAML, many users like to have a visual scheduler or advanced scheduling add-ons that let you set time-based triggers in a more calendar-like interface.

Overall, this automation ensures that your exterior lights are always at the right brightness (or turned off) at specific times throughout the day. This can be handy for saving energy, matching the aesthetic of your outdoor space, and integrating seamlessly with other home automations.


#### You:
<time datetime="2025-02-18T02:49:04.709Z" title="2/18/2025, 11:49:04 AM">11:49</time>

this makes the light.deck_bedroom_deck turn on and off intermittently. do you know why?

#### ChatGPT:
<time datetime="2025-02-18T02:49:33.746Z" title="2/18/2025, 11:49:33 AM">11:49</time>

From a quick look, the most likely reason for the **light.deck\_bedroom\_deck** turning on/off intermittently is that this automation runs **every minute** (due to `minutes: /1`) and re-applies the time-based conditions over and over.

Here’s what’s happening step-by-step:

1. **Automation Fires Every Minute**
   - The `time_pattern` trigger (`minutes: /1`) means Home Assistant re-checks this automation **once per minute**, 24/7.

2. **Conditions for Different Times**
   - Between 19:00:00 and 20:00:00, the bedroom deck is set to **50% brightness** (`light.turn_on`).
   - Right at/after 20:00:00 and before 23:59:59, the same deck light is **turned off**.

3. **“Fighting” Any Manual Changes**
   - If, for example, you manually turn the deck bedroom light on at 20:05, the next time the automation checks (which is up to a minute later), it sees the time is still > 20:00:00 and forces the light off again.
   - From your perspective, it seems to come on (your manual action) and then almost immediately go off again, giving that “intermittent” on/off behavior.

### Why “time\_pattern: /1” causes it

- Each minute, Home Assistant sees if the current time is within one of those time slots. It then **immediately enforces** the action you’ve defined for that slot.
- You probably only want the brightness to change once at 20:00, not *continuously* from 20:00 to 23:59:59. But because it’s checking every minute, it will “correct” the state anytime it finds it not matching your automation’s instruction.

### How to fix or refine it

1. **Use a single “time” or “sun” trigger** instead of a repeating pattern.

   - For example, create multiple triggers—one at 09:00, another at 15:00, 19:00, 20:00—so the automation only runs at those **exact times** to set brightness/off. It won’t “enforce” it every minute.

   ```yaml
   trigger:
     - platform: time
       at: "09:00:00"
     - platform: time
       at: "15:00:00"
     - platform: time
       at: "19:00:00"
     - platform: time
       at: "20:00:00"
   ```

2. **Add a condition to stop if the light was manually changed**
   - If you want your manual overrides to stick, you can store a helper (`input_boolean`) or use [*Context-based filtering*](https://www.home-assistant.io/blog/2021/05/05/release-20215/#new-automation-condition-based-on-trigger-context) to ignore changes that come from the UI or from another automation.

3. **Use a shorter or different time window** if the goal is to correct accidental changes.
   - For example, checking every 30 minutes or once an hour might cut down on the flicker effect.

### Big picture

- As soon as the clock hits 20:00, the deck bedroom light is off. Any attempt to override that between 20:00 and 23:59:59 will be undone within the next minute.
- Moving to a time-based trigger that only fires **once** at those key times is a simpler, more common approach. Then you won’t see that on/off toggling caused by this “every minute” enforcement.

Hopefully that helps clarify why the bedroom deck light appears to “flicker” or come on and off in the evening—it’s the combination of the frequent time trigger and strict time-based conditions.

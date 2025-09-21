---
title: Basement Lights Minimum Brightness
source: https://chatgpt.com/c/67b3f43b-8594-8003-b165-a0061015cc43
---

# Basement Lights Minimum Brightness

#### You:
<time datetime="2025-02-18T02:45:15.691Z" title="2/18/2025, 11:45:15 AM">11:45</time>

what does this automation do?
```
alias: Set Minimum Brightness for Basement Bathroom Lights
description: ""
triggers:
  - entity_id: light.basement_bathroom_lights
    to: "on"
    trigger: state
conditions: []
actions:
  - choose:
      - conditions:
          - condition: template
            value_template: >
              {{ state_attr('light.basement_bathroom_lights', 'brightness') |
              int < 26 }}
        sequence:
          - target:
              entity_id: light.basement_bathroom_lights
            data:
              brightness_pct: 10
            action: light.turn_on
mode: single

#### ChatGPT:
<time datetime="2025-02-18T02:45:41.027Z" title="2/18/2025, 11:45:41 AM">11:45</time>

This Home Assistant automation ensures that your basement bathroom lights never turn on below a certain brightness level. Specifically:

1. **Trigger**
   - It runs whenever `light.basement_bathroom_lights` changes to the “on” state.

2. **Condition**
   - It checks if the current brightness attribute (`state_attr('light.basement_bathroom_lights', 'brightness')`) is less than 26.
   - In Home Assistant, the brightness attribute usually runs on a 0–255 scale, so 26 corresponds to just over 10% brightness.

3. **Action**
   - If the brightness is below 26, it calls `light.turn_on` and sets the `brightness_pct` to 10, ensuring the light is at least at 10% brightness.

Put simply, anytime you turn on the basement bathroom lights at a very low brightness (under \~10%), this automation boosts them to 10%. It’s a handy way to prevent the lights from turning on too dim to be useful.

**Key Takeaways and Related Concepts**

- **Home Assistant Automations**: They consist of **triggers** (what causes the automation to run), **conditions** (requirements that must be met), and **actions** (what the automation does in response).
- **Brightness Scale**: In Home Assistant, `brightness` often ranges from 0–255, while `brightness_pct` is a percentage of that range (0–100%).
- **Template Conditions**: The condition here uses a Jinja2 template (`value_template`) to compare the current brightness to a fixed integer (26).

If you’re exploring more advanced automations, you could:

- Dynamically set the minimum brightness based on time of day or ambient light.
- Use other triggers or conditions (like motion sensors, door sensors, etc.) to refine the logic.

This automation is a straightforward example of ensuring lights don’t come on too dim—especially helpful in spaces like bathrooms where you want a consistent minimum level of illumination.


#### You:
<time datetime="2025-02-18T02:47:13.825Z" title="2/18/2025, 11:47:13 AM">11:47</time>

i'd like to replace this automation with one that dims the lights to 10% 30 mins after the last time the switch was touched

#### ChatGPT:
<time datetime="2025-02-18T02:47:33.128Z" title="2/18/2025, 11:47:33 AM">11:47</time>

Below is an example **Home Assistant** automation that dims the basement bathroom lights to 10% **30 minutes after the last time the switch (or light) was changed**. The key is to use **`mode: restart`** so that each time the switch/light is toggled, the 30‑minute “inactivity timer” restarts.

```yaml
alias: Dim Basement Bathroom Lights After 30 Mins
description: "Dims the lights to 10% if they remain on 30 minutes after last toggle."
mode: restart
trigger:
  # Any change to the light's state (on/off/brightness) will restart this automation
  - platform: state
    entity_id: light.basement_bathroom_lights

condition: []
action:
  # 1) Wait 30 minutes after the last change
  - delay: "00:30:00"

  # 2) Ensure the light is still on after that delay
  - condition: state
    entity_id: light.basement_bathroom_lights
    state: "on"

  # 3) If on, dim to 10%
  - service: light.turn_on
    target:
      entity_id: light.basement_bathroom_lights
    data:
      brightness_pct: 10
```

### How It Works

1. **Trigger**
   - The automation triggers whenever `light.basement_bathroom_lights` changes state.
   - This includes turning on, turning off, or changing brightness.

2. **Mode: restart**
   - The `mode: restart` ensures that if the light is toggled again within those 30 minutes, it cancels the current wait timer and starts over. This effectively tracks the “last time the switch was touched.”

3. **Delay + Condition**
   - After a 30‑minute delay, we check if the lights are still on. If so, we dim them to 10%. If the user turned them off, the condition fails and nothing happens.

This approach cleanly meets your requirement to **wait 30 minutes after the last switch/light interaction** before dimming. If you ever want to expand on this, you could add more conditions (e.g., only dim during certain hours) or integrate a motion sensor to skip dimming if someone is still in the bathroom.


#### You:
<time datetime="2025-02-18T02:51:20.845Z" title="2/18/2025, 11:51:20 AM">11:51</time>

update this automation to use light.garage_main_lights and to turn the lights off after 15 mins

#### ChatGPT:
<time datetime="2025-02-18T02:51:33.802Z" title="2/18/2025, 11:51:33 AM">11:51</time>

Below is a revised **Home Assistant** automation that monitors `light.garage_main_lights` and turns them off **15 minutes after the last time they were toggled**. We use `mode: restart` so the timer resets every time the light state changes (e.g., turned on/off or brightness adjusted).

```yaml
alias: Turn Off Garage Main Lights After 15 Mins
description: "Turns off the garage main lights if they remain on 15 minutes after the last toggle."
mode: restart
trigger:
  - platform: state
    entity_id: light.garage_main_lights

condition: []

action:
  # Wait 15 minutes after the last state change
  - delay: "00:15:00"

  # Check if the light is still on
  - condition: state
    entity_id: light.garage_main_lights
    state: "on"

  # Turn it off if it remains on
  - service: light.turn_off
    target:
      entity_id: light.garage_main_lights
```

### How It Works

1. **Trigger**
   - Runs whenever `light.garage_main_lights` changes state (on/off/brightness).

2. **Mode: restart**
   - Each time the light changes, the 15-minute delay restarts from zero.

3. **Delay + Condition**
   - After 15 minutes of inactivity, the automation checks if the light is still on.
   - If it’s still on, it calls `light.turn_off`.

This ensures your **garage main lights** are turned off automatically if left on for 15 minutes without any further interaction.

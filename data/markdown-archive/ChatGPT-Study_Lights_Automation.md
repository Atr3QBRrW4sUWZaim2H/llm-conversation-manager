---
title: Study Lights Automation
source: https://chatgpt.com/c/67b61b6c-106c-8003-a385-8c3ea7c217e8
---

# Study Lights Automation

#### You:
<time datetime="2025-02-19T17:58:49.658Z" title="2/20/2025, 2:58:49 AM">02:58</time>

replace this home assistant automation with one that turns the overhead lights to 1% on motion and the study_desk_lamps_2 to 50% brightness. turns these lights off after 10 mins of no motion. between sunset and sunrise, only the study_desk_lamps_2 should be turned on, and it should be turned on to 5% brightness.
```
alias: Study Lights
description: >
  Turns study overhead lights and desk lamps on when motion is detected.  After
  10 minutes with no motion, turns overhead lights off and dims desk lamps.
triggers:
  - entity_id: binary_sensor.study_motion_sensor_motion
    to: "on"
    id: motion_detected
    trigger: state
  - entity_id: binary_sensor.study_motion_sensor_motion
    to: "off"
    for: "00:10:00"
    id: no_motion
    trigger: state
conditions: []
actions:
  - choose:
      - conditions:
          - condition: trigger
            id: motion_detected
          - condition: sun
            after: sunset
        sequence:
          - target:
              entity_id: light.study_overhead_lights
            data:
              brightness_pct: 1
            action: light.turn_on
          - target:
              entity_id:
                - light.study_desk_lamps_2
                - light.den_tv_backlight
            data: {}
            action: light.turn_on
      - conditions:
          - condition: trigger
            id: motion_detected
        sequence:
          - target:
              entity_id:
                - light.study_overhead_lights
                - light.study_desk_lamps_2
                - light.den_tv_backlight
            data: {}
            action: light.turn_on
      - conditions:
          - condition: trigger
            id: no_motion
        sequence:
          - target:
              entity_id:
                - light.study_overhead_lights
                - light.den_tv_backlight
            data: {}
            action: light.turn_off
          - target:
              entity_id: light.study_desk_lamps_2
            data:
              brightness_pct: 10
            action: light.turn_on
    default: []
mode: single

#### ChatGPT:
<time datetime="2025-02-19T17:59:09.356Z" title="2/20/2025, 2:59:09 AM">02:59</time>

Below is an example of how you can implement a single automation that meets your requirements:

1. **If motion is detected during the day** (sunrise → sunset),
   - Turn the overhead lights on at **1%**.
   - Turn the desk lamps on at **50%**.

2. **If motion is detected at night** (sunset → sunrise),
   - Do **not** turn on the overhead lights.
   - Turn the desk lamps on at **5%**.

3. **When no motion is detected for 10 minutes**,
   - Turn off both the overhead lights and the desk lamps.

```yaml
alias: Study Lights
description: >
  Turns study lights on at different brightness levels based on time of day
  when motion is detected, and turns them off after 10 minutes of no motion.
mode: single
trigger:
  - platform: state
    entity_id: binary_sensor.study_motion_sensor_motion
    to: 'on'
    id: motion_detected
  - platform: state
    entity_id: binary_sensor.study_motion_sensor_motion
    to: 'off'
    for: '00:10:00'
    id: no_motion

condition: []

action:
  - choose:
      # When motion is detected during the day (sunrise → sunset)
      - conditions:
          - condition: trigger
            id: motion_detected
          - condition: sun
            after: sunrise
            before: sunset
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.study_overhead_lights
            data:
              brightness_pct: 1
          - service: light.turn_on
            target:
              entity_id: light.study_desk_lamps_2
            data:
              brightness_pct: 50

      # When motion is detected at night (sunset → sunrise)
      - conditions:
          - condition: trigger
            id: motion_detected
          - condition: sun
            after: sunset
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.study_desk_lamps_2
            data:
              brightness_pct: 5

      # After 10 minutes with no motion
      - conditions:
          - condition: trigger
            id: no_motion
        sequence:
          - service: light.turn_off
            target:
              entity_id:
                - light.study_overhead_lights
                - light.study_desk_lamps_2

    default: []
```

### Explanation

1. **Triggers**:
   - `motion_detected`: Fires when `binary_sensor.study_motion_sensor_motion` changes to `on`.
   - `no_motion`: Fires when `binary_sensor.study_motion_sensor_motion` changes to `off` **and** remains off for 10 minutes (`for: '00:10:00'`).

2. **Choose Action**:
   - **Daytime motion** (`sunrise` → `sunset`): Overhead at 1%, Desk Lamps at 50%.
   - **Nighttime motion** (`sunset` → `sunrise`): Only Desk Lamps at 5%.
   - **No motion for 10 minutes**: Turn both lights off.

Feel free to modify brightness levels, times, or entity IDs as needed. This single automation will handle your different brightness requirements based on time of day, and also ensure the lights turn off after inactivity.


#### You:
<time datetime="2025-02-19T18:01:07.559Z" title="2/20/2025, 3:01:07 AM">03:01</time>

don't run this automation if either of the lights are already on. otherwise it resets any manual changes i've made to the lights' brightness

#### ChatGPT:
<time datetime="2025-02-19T18:01:20.889Z" title="2/20/2025, 3:01:20 AM">03:01</time>

Below is an updated version of the automation. The main change is adding **state conditions** so that **if either light is already on**, the “turn on” actions will be skipped. In other words, this prevents the automation from resetting brightness or overriding any manual changes when motion is detected.

```yaml
alias: Study Lights
description: >
  Turn study overhead lights and desk lamps on at different brightness levels 
  based on time of day when motion is detected, unless either is already on, 
  then turn them off after 10 minutes of no motion.
mode: single
trigger:
  - platform: state
    entity_id: binary_sensor.study_motion_sensor_motion
    to: 'on'
    id: motion_detected
  - platform: state
    entity_id: binary_sensor.study_motion_sensor_motion
    to: 'off'
    for: '00:10:00'
    id: no_motion

condition: []

action:
  - choose:
      # 1) Motion detected during the day
      - conditions:
          - condition: trigger
            id: motion_detected
          - condition: sun
            after: sunrise
            before: sunset
          # Don't run if either light is already on:
          - condition: state
            entity_id: light.study_overhead_lights
            state: 'off'
          - condition: state
            entity_id: light.study_desk_lamps_2
            state: 'off'
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.study_overhead_lights
            data:
              brightness_pct: 1
          - service: light.turn_on
            target:
              entity_id: light.study_desk_lamps_2
            data:
              brightness_pct: 50

      # 2) Motion detected at night
      - conditions:
          - condition: trigger
            id: motion_detected
          - condition: sun
            after: sunset
          # Don't run if either light is already on:
          - condition: state
            entity_id: light.study_overhead_lights
            state: 'off'
          - condition: state
            entity_id: light.study_desk_lamps_2
            state: 'off'
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.study_desk_lamps_2
            data:
              brightness_pct: 5

      # 3) No motion for 10 minutes
      - conditions:
          - condition: trigger
            id: no_motion
        sequence:
          - service: light.turn_off
            target:
              entity_id:
                - light.study_overhead_lights
                - light.study_desk_lamps_2

    default: []
```

### How It Works

1. **Triggers**:
   - **`motion_detected`**: When the sensor goes to `on`.
   - **`no_motion`**: When the sensor has been `off` for 10 minutes.

2. **Choose**:
   - **Daytime motion**: Only run if it’s between sunrise and sunset **and** both lights are `off`.
     - Overhead → **1%**
     - Desk lamps → **50%**
   - **Nighttime motion**: Only run if it’s after sunset **and** both lights are `off`.
     - Desk lamps → **5%**
     - (No overhead lights at night.)
   - **No motion**: Turn off both lights after 10 minutes of inactivity.

By adding the conditions that each light must be `off` for the “turn\_on” actions to run, this automation will **not** override lights that were already on (e.g., if you set them to a different brightness manually).

Feel free to tweak brightness levels or times to suit your preferences!


#### You:
<time datetime="2025-02-19T18:03:29.017Z" title="2/20/2025, 3:03:29 AM">03:03</time>

add light.study_tv_backlight_2 to this automation. it should follow the same rules as study_desk_lamps_2

#### ChatGPT:
<time datetime="2025-02-19T18:03:53.015Z" title="2/20/2025, 3:03:53 AM">03:03</time>

Below is an updated version of the automation including **`light.study_tv_backlight_2`**. It follows the same rules as **`light.study_desk_lamps_2`**—turning on at 50% (daytime) or 5% (nighttime), and turning off after 10 minutes of no motion. It also checks that **all three** lights (`study_overhead_lights`, `study_desk_lamps_2`, and `study_tv_backlight_2`) are off before turning them on, ensuring you don’t overwrite any manual settings.

```yaml
alias: Study Lights
description: >
  Turn study overhead lights, desk lamps, and TV backlight on at different 
  brightness levels based on time of day when motion is detected, unless 
  any is already on, then turn them off after 10 minutes of no motion.
mode: single
trigger:
  - platform: state
    entity_id: binary_sensor.study_motion_sensor_motion
    to: 'on'
    id: motion_detected
  - platform: state
    entity_id: binary_sensor.study_motion_sensor_motion
    to: 'off'
    for: '00:10:00'
    id: no_motion

condition: []

action:
  - choose:
      # 1) Motion detected during the day
      - conditions:
          - condition: trigger
            id: motion_detected
          - condition: sun
            after: sunrise
            before: sunset
          # Don't run if ANY of these lights is already on
          - condition: state
            entity_id: light.study_overhead_lights
            state: 'off'
          - condition: state
            entity_id: light.study_desk_lamps_2
            state: 'off'
          - condition: state
            entity_id: light.study_tv_backlight_2
            state: 'off'
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.study_overhead_lights
            data:
              brightness_pct: 1
          - service: light.turn_on
            target:
              entity_id:
                - light.study_desk_lamps_2
                - light.study_tv_backlight_2
            data:
              brightness_pct: 50

      # 2) Motion detected at night
      - conditions:
          - condition: trigger
            id: motion_detected
          - condition: sun
            after: sunset
          # Don't run if ANY of these lights is already on
          - condition: state
            entity_id: light.study_overhead_lights
            state: 'off'
          - condition: state
            entity_id: light.study_desk_lamps_2
            state: 'off'
          - condition: state
            entity_id: light.study_tv_backlight_2
            state: 'off'
        sequence:
          - service: light.turn_on
            target:
              entity_id:
                - light.study_desk_lamps_2
                - light.study_tv_backlight_2
            data:
              brightness_pct: 5

      # 3) No motion for 10 minutes
      - conditions:
          - condition: trigger
            id: no_motion
        sequence:
          - service: light.turn_off
            target:
              entity_id:
                - light.study_overhead_lights
                - light.study_desk_lamps_2
                - light.study_tv_backlight_2

    default: []
```

### What Changed

1. **Added `light.study_tv_backlight_2`** to the actions where `study_desk_lamps_2` is used.
2. **Added conditions** so the “turn on” sequences only run if **all** the relevant lights (`study_overhead_lights`, `study_desk_lamps_2`, and `study_tv_backlight_2`) are **off**. This prevents overwriting manual settings if you’ve already turned the lights on.
3. **Turn off** all three lights after 10 minutes of no motion.

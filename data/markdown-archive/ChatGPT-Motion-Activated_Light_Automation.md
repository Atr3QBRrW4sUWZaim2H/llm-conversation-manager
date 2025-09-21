---
title: Motion-Activated Light Automation
source: https://chatgpt.com/c/67b4181e-9650-8003-96f3-f34b57eee6af
---

# Motion-Activated Light Automation

#### You:
<time datetime="2025-02-18T05:18:22.771Z" title="2/18/2025, 2:18:22 PM">14:18</time>

home assistant automation that turns the light on when there is motion
- lights:
light.study_overhead_lights
- motion:
binary_sensor.study_motion_sensor_motion

#### ChatGPT:
<time datetime="2025-02-18T05:18:32.816Z" title="2/18/2025, 2:18:32 PM">14:18</time>

Below is a simple Home Assistant automation in YAML that will turn on your **Study Overhead Lights** whenever your **Study Motion Sensor** detects motion.

```yaml
alias: "Turn On Study Lights on Motion"
description: "Turns the study overhead lights on when motion is detected."
trigger:
  - platform: state
    entity_id: binary_sensor.study_motion_sensor_motion
    to: "on"
condition: []
action:
  - service: light.turn_on
    target:
      entity_id: light.study_overhead_lights
mode: single
```

### Explanation

1. **trigger**: Uses a [state trigger](https://www.home-assistant.io/docs/automation/trigger/#state-trigger) on `binary_sensor.study_motion_sensor_motion`. When it changes state to `on` (motion detected), it triggers the automation.
2. **condition**: There are no additional conditions in this example, so it will always run once motion is detected.
3. **action**: Calls the `light.turn_on` service to turn on `light.study_overhead_lights`.

If you’d like to refine this further (for example, only trigger during certain times of the day or if the lights are currently off), you can add [conditions](https://www.home-assistant.io/docs/scripts/conditions/) to achieve that. But this basic version should get you started with detecting motion and turning on the lights.

---

If you’re exploring deeper into **motion-based automations**, you might be interested in:

- **Adding a delay** to automatically turn lights off after no motion is detected.
- Using **templating** in Home Assistant for more complex conditional rules (e.g., time-based or brightness-based conditions).
- Integrating sensors like **ambient light sensors** to prevent lights from turning on if there is already enough daylight in the room.

Feel free to let me know if you’d like to explore any of those advanced topics!


#### You:
<time datetime="2025-02-18T05:20:07.537Z" title="2/18/2025, 2:20:07 PM">14:20</time>

also control light.study_desk_lamps_2

#### ChatGPT:
<time datetime="2025-02-18T05:20:18.864Z" title="2/18/2025, 2:20:18 PM">14:20</time>

Below is an updated Home Assistant automation in YAML that turns **both** your overhead lights and desk lamp on whenever motion is detected by your study motion sensor:

```yaml
alias: "Turn On Study Lights on Motion"
description: "Turns on the study overhead lights and desk lamps when motion is detected."
trigger:
  - platform: state
    entity_id: binary_sensor.study_motion_sensor_motion
    to: "on"
condition: []
action:
  - service: light.turn_on
    target:
      entity_id:
        - light.study_overhead_lights
        - light.study_desk_lamps_2
mode: single
```

### How It Works

- **Trigger**: Listens for the `binary_sensor.study_motion_sensor_motion` to change its state to `on`.
- **Action**: Executes `light.turn_on` for both `light.study_overhead_lights` and `light.study_desk_lamps_2` so they illuminate in unison.
- **No condition**: As soon as the motion sensor is `on`, the lights turn on, with no time or other restrictions.

---

### Suggestions for Further Customization

- **Time-based Conditions**: You can add a [condition](https://www.home-assistant.io/docs/scripts/conditions/) to only turn the lights on if it’s after sunset or before sunrise (or during specific hours).
- **Brightness or Color**: You can configure brightness and color by adding parameters under `data:` in the `action` section if your lights support it.
- **Turn Lights Off Automatically**: Use a second automation or extend this one with a `for` option or separate trigger when `binary_sensor.study_motion_sensor_motion` returns to `off`, along with a time delay, to automatically turn lights off after no motion is detected.

Feel free to let me know if you’d like more details on these enhancements!


#### You:
<time datetime="2025-02-18T05:22:08.598Z" title="2/18/2025, 2:22:08 PM">14:22</time>

after 10 minutes of no motion turn study_overhead_lights off and dim study_desk_lamps_2 to 10%

#### ChatGPT:
<time datetime="2025-02-18T05:22:16.862Z" title="2/18/2025, 2:22:16 PM">14:22</time>

Below is an example automation in Home Assistant YAML that waits for 10 minutes of **no motion** before turning off the **study overhead lights** and dimming the **desk lamps** to 10%.

```yaml
alias: "Dim and Turn Off Study Lights After No Motion"
description: "After 10 minutes of no motion, overhead lights turn off, desk lamps go to 10%."
trigger:
  - platform: state
    entity_id: binary_sensor.study_motion_sensor_motion
    to: "off"
    for: "00:10:00"
condition: []
action:
  - service: light.turn_off
    target:
      entity_id: light.study_overhead_lights
  - service: light.turn_on
    target:
      entity_id: light.study_desk_lamps_2
    data:
      brightness_pct: 10
mode: single
```

## How It Works

1. **Trigger**: The automation listens for your motion sensor to switch to the “off” state (no motion), and stays that way for 10 minutes (`for: "00:10:00"`).
2. **Action**:
   - **Turn Off Overhead Lights**: Calls `light.turn_off` on `light.study_overhead_lights`.
   - **Dim Desk Lamps**: Calls `light.turn_on` on `light.study_desk_lamps_2` with `brightness_pct: 10`, which sets them to 10% brightness.

### Tips & Ideas

- Combine this with your **motion-based “lights on” automation** for a complete motion-driven lighting setup.
- If you want the lights to turn back up to 100% when motion resumes, you can customize your motion “lights on” automation to set a brightness value, or you can simply keep it at the default brightness if that is your preference.
- You can adjust the `for: "00:10:00"` duration to any time window you like.
- If you have other conditions (e.g., only dim or turn off lights if it’s a certain time of day), add a [condition block](https://www.home-assistant.io/docs/scripts/conditions/) before the action.

Feel free to let me know if you want to explore more advanced automations!


#### You:
<time datetime="2025-02-18T05:22:23.540Z" title="2/18/2025, 2:22:23 PM">14:22</time>

combine both into a single config

#### ChatGPT:
<time datetime="2025-02-18T05:22:36.574Z" title="2/18/2025, 2:22:36 PM">14:22</time>

Below is an example of a **single** Home Assistant automation that does both:

1. **Turns on** your overhead lights and desk lamps **when motion is detected**.
2. **After 10 minutes of no motion**, turns **off** the overhead lights and **dims** the desk lamps to 10%.

```yaml
alias: "Study Motion Lighting Control"
description: >
  Turns study overhead lights and desk lamps on when motion is detected.
  After 10 minutes with no motion, turns overhead lights off and dims desk lamps.
mode: single
trigger:
  - platform: state
    entity_id: binary_sensor.study_motion_sensor_motion
    to: "on"
    id: "motion_detected"
  - platform: state
    entity_id: binary_sensor.study_motion_sensor_motion
    to: "off"
    for: "00:10:00"  # 10 minutes
    id: "no_motion"
condition: []
action:
  - choose:
      - conditions:
          - condition: trigger
            id: "motion_detected"
        sequence:
          - service: light.turn_on
            target:
              entity_id:
                - light.study_overhead_lights
                - light.study_desk_lamps_2
      - conditions:
          - condition: trigger
            id: "no_motion"
        sequence:
          - service: light.turn_off
            target:
              entity_id: light.study_overhead_lights
          - service: light.turn_on
            target:
              entity_id: light.study_desk_lamps_2
            data:
              brightness_pct: 10
    default: []
```

### How It Works

1. **Multiple Triggers**:
   - **Trigger 1:** When the motion sensor goes to **`on`** (`id: "motion_detected"`).
   - **Trigger 2:** When the sensor has been **`off`** (no motion) for 10 minutes (`id: "no_motion"`).
2. **Choose Action**:
   - If the automation was triggered by `motion_detected`, it **turns on** the overhead lights and desk lamps.
   - If triggered by `no_motion`, it **turns off** the overhead lights and **dims** the desk lamps to 10%.
3. **mode: single**: Ensures only one execution of this automation runs at a time. Depending on your needs, you could also use `mode: restart` or `queued`.

---

## Additional Notes

- You can adjust the `for: "00:10:00"` to any duration you prefer.
- If you find you want the desk lamps completely off, just replace the `light.turn_on` service with `light.turn_off` in the second sequence (or remove the second step entirely).
- Consider adding [conditions](https://www.home-assistant.io/docs/scripts/conditions/) (e.g., time-of-day, presence of daylight) if you want finer control.

Feel free to let me know if you have any other questions or if you’d like to explore more advanced configurations!


#### You:
<time datetime="2025-02-19T02:56:08.560Z" title="2/19/2025, 11:56:08 AM">11:56</time>

update this automation to turn the study lights to 1% brightness after sunset:
````
alias: Study Lights
description: >
  Turns study overhead lights and desk lamps on when motion is detected. After
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
        sequence:
          - target:
              entity_id:
                - light.study_overhead_lights
                - light.study_desk_lamps_2
                - light.den_tv_backlight
            action: light.turn_on
            data: {}
      - conditions:
          - condition: trigger
            id: no_motion
        sequence:
          - target:
              entity_id:
                - light.study_overhead_lights
                - light.den_tv_backlight
            action: light.turn_off
            data: {}
          - target:
              entity_id: light.study_desk_lamps_2
            data:
              brightness_pct: 10
            action: light.turn_on
    default: []
mode: single



#### ChatGPT:
<time datetime="2025-02-19T02:57:11.852Z" title="2/19/2025, 11:57:11 AM">11:57</time>

Below is an updated version of your automation that:

1. **Turns on the lights** (overhead, desk lamps, TV backlight) when motion is detected.
2. **After sunset**, the **overhead lights** will turn on at **1% brightness** instead of full brightness.
3. **After 10 minutes of no motion**, overhead lights and TV backlight turn off, while desk lamps dim to 10% brightness.

> **Note**: This approach uses Home Assistant’s built-in [Sun integration](https://www.home-assistant.io/integrations/sun/) (make sure `sun:` is enabled in your `configuration.yaml`).

```yaml
alias: Study Lights
description: >
  Turns study overhead lights and desk lamps on when motion is detected. 
  After 10 minutes with no motion, turns overhead lights off and dims desk lamps.
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
      # 1) MOTION DETECTED AND AFTER SUNSET => Overhead Lights @ 1%, Other Lights On
      - conditions:
          - condition: trigger
            id: motion_detected
          - condition: sun
            after: sunset
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
                - light.den_tv_backlight
            data: {}
      
      # 2) MOTION DETECTED (ANY OTHER TIME) => All Lights On (Default/Full Brightness)
      - conditions:
          - condition: trigger
            id: motion_detected
        sequence:
          - service: light.turn_on
            target:
              entity_id:
                - light.study_overhead_lights
                - light.study_desk_lamps_2
                - light.den_tv_backlight
            data: {}
      
      # 3) NO MOTION AFTER 10 MIN => Overhead Lights & TV Off, Desk Lamps @ 10%
      - conditions:
          - condition: trigger
            id: no_motion
        sequence:
          - service: light.turn_off
            target:
              entity_id:
                - light.study_overhead_lights
                - light.den_tv_backlight
            data: {}
          - service: light.turn_on
            target:
              entity_id: light.study_desk_lamps_2
            data:
              brightness_pct: 10
    default: []
mode: single
```

### How It Works

1. **Triggers**:
   - **`motion_detected`**: When the motion sensor goes `on`.
   - **`no_motion`**: When the sensor remains `off` for 10 minutes.

2. **Choose Conditions**:
   1. **If motion is detected and it’s after sunset**: Overhead lights turn on at **1%** brightness, while the desk lamps and TV backlight come on at default brightness.
   2. **If motion is detected and it’s **not** after sunset**: All lights turn on at their default brightness.
   3. **If no motion for 10 minutes**: Turn off overhead lights and TV backlight, and dim the desk lamps to **10%** brightness.

3. **Sun Integration**:
   - The `condition: sun` with `after: sunset` requires the `sun:` platform to be enabled in your Home Assistant configuration (usually by default).
   - This condition ensures that the brightness change to 1% only applies when it’s actually dark outside.

You can further customize brightness levels, add color temperature data if your bulbs support it, or restrict these actions to specific times of day. If you have any other questions, feel free to let me know!

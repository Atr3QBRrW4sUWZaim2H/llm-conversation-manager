---
title: PS Audio Integration Tips
source: https://chatgpt.com/c/679e6c78-515c-8003-a228-4e0e63cad3b5
---

# PS Audio Integration Tips

#### You:
<time datetime="2025-02-01T18:48:24.518Z" title="2/2/2025, 3:48:24 AM">03:48</time>


# Loads default set of integrations. Do not remove.
default_config:

# Load frontend themes from the themes folder
frontend:
  themes: !include_dir_merge_named themes

automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

rest:
  # -------------------------
  # Zone 0
  # -------------------------
  - resource: "http://192.168.1.37/zones.cgi?zone=0"
    scan_interval: 10
    device:
      identifiers: "ps_audio_p5_00:1F:F6:00:24:AD"
      manufacturer: "PS Audio"
      model: "PerfectWave P5"
      name: "PS Audio PerfectWave P5"
    switch:
      - name: "P5 Zone 0"
        unique_id: "ps_audio_p5_zone_0"
        command_on: "http://192.168.1.37/zones.cgi?zone=0"
        command_off: "http://192.168.1.37/zones.cgi?zone=0"
        verify_state: true
        value_template: >-
          {% if 'Success! 1' in value %}
            on
          {% elif 'Success! 0' in value %}
            off
          {% else %}
            unknown
          {% endif %}
        state_on: "on"
        state_off: "off"

  # -------------------------
  # Zone 1
  # -------------------------
  - resource: "http://192.168.1.37/zones.cgi?zone=1"
    scan_interval: 10
    device:
      identifiers: "ps_audio_p5_00:1F:F6:00:24:AD"  # Same device ID
      manufacturer: "PS Audio"
      model: "PerfectWave P5"
      name: "PS Audio PerfectWave P5"
    switch:
      - name: "P5 Zone 1"
        unique_id: "ps_audio_p5_zone_1"
        command_on: "http://192.168.1.37/zones.cgi?zone=1"
        command_off: "http://192.168.1.37/zones.cgi?zone=1"
        verify_state: true
        value_template: >-
          {% if 'Success! 1' in value %}
            on
          {% elif 'Success! 0' in value %}
            off
          {% else %}
            unknown
          {% endif %}
        state_on: "on"
        state_off: "off"

  # -------------------------
  # Zone 2
  # -------------------------
  - resource: "http://192.168.1.37/zones.cgi?zone=2"
    scan_interval: 10
    device:
      identifiers: "ps_audio_p5_00:1F:F6:00:24:AD"
      manufacturer: "PS Audio"
      model: "PerfectWave P5"
      name: "PS Audio PerfectWave P5"
    switch:
      - name: "P5 Zone 2"
        unique_id: "ps_audio_p5_zone_2"
        command_on: "http://192.168.1.37/zones.cgi?zone=2"
        command_off: "http://192.168.1.37/zones.cgi?zone=2"
        verify_state: true
        value_template: >-
          {% if 'Success! 1' in value %}
            on
          {% elif 'Success! 0' in value %}
            off
          {% else %}
            unknown
          {% endif %}
        state_on: "on"
        state_off: "off"

  # -------------------------
  # Zone 3
  # -------------------------
  - resource: "http://192.168.1.37/zones.cgi?zone=3"
    scan_interval: 10
    device:
      identifiers: "ps_audio_p5_00:1F:F6:00:24:AD"
      manufacturer: "PS Audio"
      model: "PerfectWave P5"
      name: "PS Audio PerfectWave P5"
    switch:
      - name: "P5 Zone 3"
        unique_id: "ps_audio_p5_zone_3"
        command_on: "http://192.168.1.37/zones.cgi?zone=3"
        command_off: "http://192.168.1.37/zones.cgi?zone=3"
        verify_state: true
        value_template: >-
          {% if 'Success! 1' in value %}
            on
          {% elif 'Success! 0' in value %}
            off
          {% else %}
            unknown
          {% endif %}
        state_on: "on"
        state_off: "off"

  # -------------------------
  # Zone 4
  # -------------------------
  - resource: "http://192.168.1.37/zones.cgi?zone=4"
    scan_interval: 10
    device:
      identifiers: "ps_audio_p5_00:1F:F6:00:24:AD"
      manufacturer: "PS Audio"
      model: "PerfectWave P5"
      name: "PS Audio PerfectWave P5"
    switch:
      - name: "P5 Zone 4"
        unique_id: "ps_audio_p5_zone_4"
        command_on: "http://192.168.1.37/zones.cgi?zone=4"
        command_off: "http://192.168.1.37/zones.cgi?zone=4"
        verify_state: true
        value_template: >-
          {% if 'Success! 1' in value %}
            on
          {% elif 'Success! 0' in value %}
            off
          {% else %}
            unknown
          {% endif %}
        state_on: "on"
        state_off: "off"

#### ChatGPT:
<time datetime="2025-02-01T18:49:01.126Z" title="2/2/2025, 3:49:01 AM">03:49</time>

Below is a brief overview and some suggestions for enhancing this configuration for controlling your PS Audio PerfectWave P5 via Home Assistant. Since you’ve shown interest in audio equipment, Home Assistant automations, and related high-end gear, I’ll also touch on how you might integrate these switches into more advanced use cases (e.g., scene control, home theater automation, etc.).

---

## How the Current Configuration Works

1. **Basic REST Switch Setup**:
   - Each of the five zones (0 through 4) is set up as a separate REST switch.
   - Home Assistant calls `http://192.168.1.37/zones.cgi?zone=N` (where `N` is the zone number) when you turn the zone on or off.
   - The device responds with either `Success! 1` or `Success! 0`, which the `value_template` checks to determine if the state is `on` or `off`.

2. **Shared Device Information**:
   - All zones use the same device identifiers: `ps_audio_p5_00:1F:F6:00:24:AD`.
   - This means they’ll all appear under a single device in Home Assistant, with each zone as a separate switch entity.

3. **Unique IDs**:
   - Each switch has a distinct `unique_id`, ensuring that Home Assistant tracks them as separate entities (e.g., `ps_audio_p5_zone_0`, `ps_audio_p5_zone_1`, etc.).

4. **Scan Interval**:
   - The `scan_interval: 10` ensures Home Assistant polls the P5 every 10 seconds for updated zone states.
   - If you want more frequent or less frequent updates, adjust this number.

Overall, the configuration is straightforward and should work as expected for toggling each zone on the P5 on/off.

---

## Potential Enhancements

### 1. Use of `rest_command` for Cleaner YAML

- **Why**: Right now, each REST switch has the same pattern for `command_on` and `command_off` that only changes the `zone` parameter. You can avoid repeating the full URL multiple times by using the [rest\_command integration](https://www.home-assistant.io/integrations/rest_command/) and referencing it within your switches. This can make the code more maintainable if your endpoint or IP changes.
- **Example**:
  ```yaml
  rest_command:
    p5_zone_toggle:
      url: "http://192.168.1.37/zones.cgi?zone={{ zone_id }}"

  # Then, in your switch:
  switch:
    - platform: template
      switches:
        p5_zone_0:
          value_template: "{{ states('sensor.p5_zone_0_state') }}"
          turn_on:
            service: rest_command.p5_zone_toggle
            data:
              zone_id: 0
          turn_off:
            service: rest_command.p5_zone_toggle
            data:
              zone_id: 0
  ```
  You’d pair that with a sensor to read back the state from the device—though you can keep your existing REST approach for reading states if preferred.

### 2. Adding Read-Only Sensors for Power Data

- Many PS Audio devices can provide current draw, wattage, or voltage measurements on each zone. If the P5 exposes that via its API or a similar HTTP endpoint, you might consider adding some additional `sensor:` entries.
- This could be particularly interesting for your hi-fi or home theater setup—seeing real-time power usage can help you monitor or automate certain conditions (for example, a high current draw might indicate your amplifier is on, triggering certain lighting or scene changes).

### 3. Customizing Names, Icons, and Device Classes

- Home Assistant allows you to specify `friendly_name` and `icon`. This can be nice to keep your UI polished. For example:
  ```yaml
  switch:
    - name: "Amplifier (P5 Zone 0)"
      icon: mdi:amplifier
      ...
  ```
  That way, in the Lovelace UI or the Home Assistant app, you’ll see a relevant icon for your audio gear.

### 4. Leveraging Scenes and Automations

- Now that each zone is a switch, you can incorporate them into:
  - **Scenes**: You might create a “Movie Night” scene that turns on certain zones, sets overhead lights to 20%, lowers the projector screen, etc.
  - **Automations**: For instance, if your hi-fi preamp or media player powers on, you could detect that (via [HDMI-CEC](https://www.home-assistant.io/integrations/hdmi_cec), IP control, or another integration) and then automatically toggle specific P5 zones to power amps or source components.

### 5. Conditional or Triggered Polling

- If you only need real-time updates when toggling the switch in the UI, you could reduce or remove `scan_interval` to lighten network traffic.
- Another pattern is to call an update service within an automation after issuing a power toggle command. That way, you’re not polling too often, but you still get an immediate refresh of the state.

---

## Summary

- **Your current YAML** is well-structured for basic on/off control of each zone on the PS Audio PerfectWave P5.
- **Consider using `rest_command`** for a more streamlined approach that can cut down on repeated URL definitions.
- **Look into additional read-only sensors** (if your P5 exposes power metrics) to expand your insight and automation capabilities.
- **Automations & Scenes** can make controlling your high-end audio gear part of a more immersive system (e.g., powering up specific zones when switching on your tube amp, or shutting everything down in a single “Good Night” routine).

Given your interest in advanced setups—especially around high-end audio gear—these tips could help you harness more of the PS Audio P5’s network capabilities and tie it all together in Home Assistant for a polished, automated listening environment. If you have further questions or decide to expand your Home Assistant configuration to gather power usage stats or integrate other hi-fi components, feel free to share more details!


#### You:
<time datetime="2025-02-01T18:49:13.636Z" title="2/2/2025, 3:49:13 AM">03:49</time>

refactor to 1. Use of rest_command for Cleaner YAML

#### ChatGPT:
<time datetime="2025-02-01T18:50:18.309Z" title="2/2/2025, 3:50:18 AM">03:50</time>

Below is one example of how you can refactor your PS Audio P5 configuration to use a single `rest_command` for cleaner, more maintainable YAML. This approach separates:

1. A single `rest_command` to send the on/off command to each zone.
2. A set of `rest` sensors (one per zone) that read the current state from the P5.
3. A set of template switches (one per zone) that tie it all together in the UI.

> **Note**: This method does *not* attach each switch directly to a single “device” in Home Assistant (meaning you won’t see them grouped under a single device with manufacturer/model in the UI). Instead, you’ll see them as separate entities. If preserving the device grouping is critical, you can explore more advanced methods, but this refactoring demonstrates how to avoid repeating the same URL/config multiple times by leveraging `rest_command`.

---

## 1. `rest_command` Configuration

Define a single command in your main `configuration.yaml` (or in a file you include) to handle toggling any zone by passing in a `zone_id` parameter:

```yaml
rest_command:
  p5_zone_toggle:
    url: "http://192.168.1.37/zones.cgi?zone={{ zone_id }}"
    # Optionally specify method/payload if needed, e.g.:
    # method: POST
    # content_type: "application/x-www-form-urlencoded"
    # payload: "zone={{ zone_id }}"
```

This single command now covers the on/off “toggle” endpoint for all zones.

---

## 2. `rest` Sensors for Each Zone

Next, set up a `rest` sensor for each zone to read its current state. Home Assistant will call these endpoints every `scan_interval` seconds to keep the switch states in sync:

```yaml
sensor:
  - platform: rest
    name: "P5 Zone 0 State"
    resource: "http://192.168.1.37/zones.cgi?zone=0"
    scan_interval: 10
    value_template: >-
      {% if 'Success! 1' in value %}
        on
      {% elif 'Success! 0' in value %}
        off
      {% else %}
        unknown
      {% endif %}

  - platform: rest
    name: "P5 Zone 1 State"
    resource: "http://192.168.1.37/zones.cgi?zone=1"
    scan_interval: 10
    value_template: >-
      {% if 'Success! 1' in value %}
        on
      {% elif 'Success! 0' in value %}
        off
      {% else %}
        unknown
      {% endif %}

  - platform: rest
    name: "P5 Zone 2 State"
    resource: "http://192.168.1.37/zones.cgi?zone=2"
    scan_interval: 10
    value_template: >-
      {% if 'Success! 1' in value %}
        on
      {% elif 'Success! 0' in value %}
        off
      {% else %}
        unknown
      {% endif %}

  - platform: rest
    name: "P5 Zone 3 State"
    resource: "http://192.168.1.37/zones.cgi?zone=3"
    scan_interval: 10
    value_template: >-
      {% if 'Success! 1' in value %}
        on
      {% elif 'Success! 0' in value %}
        off
      {% else %}
        unknown
      {% endif %}

  - platform: rest
    name: "P5 Zone 4 State"
    resource: "http://192.168.1.37/zones.cgi?zone=4"
    scan_interval: 10
    value_template: >-
      {% if 'Success! 1' in value %}
        on
      {% elif 'Success! 0' in value %}
        off
      {% else %}
        unknown
      {% endif %}
```

Each sensor’s `value_template` checks if the zone is “Success! 1” (on) or “Success! 0” (off).

---

## 3. Template Switches for Each Zone

Finally, create template switches that:

- Look at the corresponding sensor for their current `value_template`.
- Call the `rest_command.p5_zone_toggle` service to turn on/off (passing the relevant `zone_id`).

```yaml
switch:
  - platform: template
    switches:

      p5_zone_0:
        friendly_name: "P5 Zone 0"
        value_template: "{{ is_state('sensor.p5_zone_0_state', 'on') }}"
        turn_on:
          service: rest_command.p5_zone_toggle
          data:
            zone_id: 0
        turn_off:
          service: rest_command.p5_zone_toggle
          data:
            zone_id: 0
        icon_template: "mdi:power"

      p5_zone_1:
        friendly_name: "P5 Zone 1"
        value_template: "{{ is_state('sensor.p5_zone_1_state', 'on') }}"
        turn_on:
          service: rest_command.p5_zone_toggle
          data:
            zone_id: 1
        turn_off:
          service: rest_command.p5_zone_toggle
          data:
            zone_id: 1
        icon_template: "mdi:power"

      p5_zone_2:
        friendly_name: "P5 Zone 2"
        value_template: "{{ is_state('sensor.p5_zone_2_state', 'on') }}"
        turn_on:
          service: rest_command.p5_zone_toggle
          data:
            zone_id: 2
        turn_off:
          service: rest_command.p5_zone_toggle
          data:
            zone_id: 2
        icon_template: "mdi:power"

      p5_zone_3:
        friendly_name: "P5 Zone 3"
        value_template: "{{ is_state('sensor.p5_zone_3_state', 'on') }}"
        turn_on:
          service: rest_command.p5_zone_toggle
          data:
            zone_id: 3
        turn_off:
          service: rest_command.p5_zone_toggle
          data:
            zone_id: 3
        icon_template: "mdi:power"

      p5_zone_4:
        friendly_name: "P5 Zone 4"
        value_template: "{{ is_state('sensor.p5_zone_4_state', 'on') }}"
        turn_on:
          service: rest_command.p5_zone_toggle
          data:
            zone_id: 4
        turn_off:
          service: rest_command.p5_zone_toggle
          data:
            zone_id: 4
        icon_template: "mdi:power"
```

---

## How It Works

- **When you toggle a zone** in the Home Assistant UI:
  1. The template switch calls `rest_command.p5_zone_toggle`, appending the right `zone_id` (0–4) to the URL (`http://192.168.1.37/zones.cgi?zone=...`).
  2. The P5 toggles that zone (since the same endpoint is used for on/off).
  3. On the next sensor update (every 10 seconds by default), the sensor grabs the new state (`Success! 1` or `Success! 0`).
  4. The template switch’s `value_template` compares the sensor value to `on` or `off` and updates the switch’s state in Home Assistant.

- **To see immediate feedback**: If you want the switch state to refresh more quickly, you can lower `scan_interval` in the `rest` sensors, or call a manual `homeassistant.update_entity` on the sensor(s) right after toggling the switch.

---

## Customizations and Next Steps

1. **Device Grouping**: If you want to see these switches grouped under a single “device” with manufacturer/model info, you can either:
   - Continue using a RESTful Switch platform (like your initial approach) but refactor the command using `rest_command` in the `command_template` fields, or
   - Use advanced YAML or a custom integration to set device info for template entities.

2. **Power Monitoring**: If your P5 provides power usage data (current draw, voltage, etc.) via HTTP endpoints, add more `rest` sensors for deeper insight and potential automations (e.g., watch wattage to trigger other actions).

3. **Scenes & Automations**: Now that each zone is a simple switch, you can add them to Scenes or Automations (e.g., “Movie Night” scene to power on multiple amplifiers, subwoofers, and set lighting).

---

**That’s it!** You’ve now refactored your config to use one `rest_command` for all P5 zones, significantly cutting down on repetitive code. You’ll have five `rest` sensors (one per zone) to track their states and five template switches that call the single toggle command. Enjoy the streamlined YAML and keep exploring ways to integrate your PS Audio P5 with the rest of your Home Assistant smart home setup.

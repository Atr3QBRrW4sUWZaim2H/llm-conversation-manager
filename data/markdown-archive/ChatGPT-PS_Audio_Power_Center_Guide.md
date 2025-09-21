---
title: PS Audio Power Center Guide
source: https://chatgpt.com/c/679e621c-8428-8003-95f8-41b19a8a14a8
---

# PS Audio Power Center Guide

#### You:
<time datetime="2025-02-01T18:04:12.715Z" title="2/2/2025, 3:04:12 AM">03:04</time>


PS Audio Power Center - Control Panel
System Status
Configuration
Network
Unit: POWERPLANT
System Power:

Zone Power:


Zone Details: No Zone Selected

For additional help, please contact your custom installer or www.psaudio.com.
 
Copyright © 2010 PS Audio

#### ChatGPT:
<time datetime="2025-02-01T18:04:31.372Z" title="2/2/2025, 3:04:31 AM">03:04</time>

Below is a brief overview of what you’re seeing on the PS Audio Power Center (often referred to as a Power Plant or Power Regenerator) control panel and some context on how it fits into a high-performance audio setup. I’ll also weave in some related key concepts—like power regeneration, clean power delivery, and system zoning—that may be useful if you’re expanding your knowledge on audiophile power management.

---

## Understanding the Control Panel Readout

1. **System Status**\
   This typically provides a high-level overview of the Power Plant’s operating condition (e.g., incoming voltage, outgoing voltage, total harmonic distortion (THD) readings, and overall load). The “System Power” line often shows whether the entire unit is on and supplying regenerated power.

2. **Zone Power**\
   Many PS Audio power products allow you to configure different “Zones.” A zone is simply a group of outlets that share certain power settings or turn-on/turn-off timings.
   - *For instance, you might have Zone A dedicated to your main amplifier, Zone B for source components like a DAC or streamer, and Zone C for auxiliary gear.*
   - Each zone can often be powered on independently or set to sequences to avoid large current draws all at once.

3. **Zone Details**\
   If the control panel says “No Zone Selected,” it might mean you haven’t clicked or tapped on a particular zone to see specifics. Selecting a zone typically reveals details like the current power draw (in watts), on/off status, or any auto-shutdown triggers you’ve set.

4. **Configuration**\
   This area is where you’d set up how each zone behaves, such as:
   - Power on delays (to prevent all devices from turning on at once).
   - Naming each zone according to the equipment connected.
   - Fine-tuning voltage or multi-wave settings (if supported by your specific Power Plant model).

5. **Network**\
   If your PS Audio device has network connectivity (many models do), the “Network” section is where you’d configure Ethernet or Wi-Fi settings. This can include IP address, firmware updates, and remote-control features via a web browser or control app.

---

## Why Power Regeneration Matters in Audio

PS Audio’s Power Plants (and similar regenerators) are more than just power conditioners. While typical *power conditioners* filter noise from the mains, a *power regenerator* actually takes the incoming AC power, converts it to DC, and then reconstructs a new, ultra-low-noise AC sine wave. Here’s why that helps:

- **Cleaner Power:** Reducing harmonic distortion (THD) means your amplifiers, DACs, and other gear receive more stable voltage with fewer artifacts.
- **Voltage Stability:** If your home’s voltage fluctuates (e.g., 110V to 125V swings), a regenerator outputs a constant voltage (commonly set around 120V in the US).
- **Lower Noise Floor:** Cleaner power often translates to greater dynamic range and a lower noise floor, which can improve clarity and detail in audio playback.

These qualities can be especially relevant if you’re into high-resolution or reference-level audio, where every gain in SNR (signal-to-noise ratio) can be perceived in the overall system performance.

---

## Key Concepts & Terminologies

- **THD (Total Harmonic Distortion):** This measures how much the AC waveform is distorted relative to a pure sine wave. Lower is better for audio.
- **Regenerator vs. Conditioner:** Regenerators rebuild AC power from the ground up; conditioners typically just filter noise and may offer surge protection.
- **Power Sequencing:** Staggering the turn-on times of gear to avoid tripping breakers or creating voltage dips.
- **Zones:** Grouped outlets that can be individually controlled for different components.
- **Ground Loop:** Unwanted hum/buzz often caused by multiple paths to ground in an audio system. Proper power management can reduce ground loop noise.

---

## Practical Tips

1. **Zone Assignments:** Label your zones to match the equipment plugged in. For instance, “Amps,” “Front End,” “Digital Source,” “Analog Source.” This keeps things organized when you’re checking status remotely or making changes.

2. **Set Startup Delays:** Large power amplifiers can draw heavy current on startup. Delaying them by a few seconds after DACs or preamps are powered on can help manage inrush current.

3. **Check Firmware Updates:** If your Power Center is network-enabled, periodically check the “Network” page for firmware updates. PS Audio often refines the performance and adds features over time.

4. **Monitor Incoming/Outgoing Voltage & THD:** If you’re curious, you can watch how the Power Plant is reducing distortion. It’s educational and can help diagnose if you have particularly dirty mains.

5. **System Synergy:** If you’re expanding your knowledge in the Hi-Fi domain, note how clean power interacts with downstream gear—especially sensitive components like DACs or turntable preamps.

---

## Further Resources

- **PS Audio Website:** [www.psaudio.com](https://www.psaudio.com/) – Official documentation, troubleshooting guides, and community forums.
- **Custom Installer/Dealer:** If you have advanced integration (home automation, triggers, or multi-room setups), a certified installer can help program and fine-tune your zones.
- **Audiophile Forums:** Places like the PS Audio forums, Audiogon, or Head-Fi can provide user experiences and tips on fine-tuning your power setup.

---

### Final Thoughts

The screen you provided is essentially the device’s status dashboard. Each section—System Power, Zone Power, Configuration, Network—lets you manage how your equipment receives power and how you monitor the quality of that power. In high-end audio systems, attention to AC power quality can yield audible improvements, which is why Power Plants and regenerators are so popular among serious listeners.

If you have more questions about setting up specific zones, optimizing settings for your components, or you want to delve deeper into power-related terminologies (like multi-wave, sine-wave, crest factor, etc.), feel free to ask! There’s a whole world of knowledge around power management that ties in well with your existing audio interests.


#### You:
<time datetime="2025-02-01T18:04:53.519Z" title="2/2/2025, 3:04:53 AM">03:04</time>

on this screen i can push a button and it will turn on my powerplant. how can i send the "turn on" signal to the powerplant programmatically

#### ChatGPT:
<time datetime="2025-02-01T18:05:12.425Z" title="2/2/2025, 3:05:12 AM">03:05</time>

Programmatically controlling a PS Audio Power Plant (e.g., turning the unit on or off) typically requires sending the same kind of command that the web interface or front-panel control sends. Depending on your Power Plant model and the firmware it’s running, there are a few common methods:

---

## 1. Using the Device’s Network / Web Interface (HTTP Requests)

Most modern PS Audio units with network connectivity provide a built-in web interface you can access by typing its IP address into a browser. If you can turn the Power Plant on/off by pressing a button on that web page, you can often replicate the same action programmatically by sending the same HTTP request the web UI sends.

### Steps to Explore:

1. **Find the Power Plant’s IP Address**
   - Check the “Network” settings on the Power Plant screen.
   - Or look at your router’s DHCP client list to see which IP address was assigned to the device.

2. **Inspect the Web Interface**
   - Open the Power Plant’s web page in Chrome/Firefox.
   - Use “Developer Tools” (e.g., in Chrome, press **F12** or **Ctrl+Shift+I**) to view the **Network** tab.
   - Press the **Power On** button in the UI and observe any HTTP requests triggered. You should see a POST or GET request with a specific endpoint (URL) and parameters.

3. **Replicate the Request**
   - Use a tool like **cURL**, **Postman**, or even your own code (Python, Node.js, etc.) to send the exact same request.
   - If an authentication token or session ID is required, you’ll need to include that in your request header or cookie.

4. **Automate It**
   - Incorporate that HTTP request into your home automation system or custom script so that it can be triggered on demand.

> **Note:** Some PS Audio devices require a login or session cookie. Make sure you handle that properly if the device’s firmware enforces authentication.

---

## 2. Using IP Control / Telnet / SSH (If Supported)

Certain models (especially those aimed at custom installers) may support direct IP control via Telnet or SSH commands. If your Power Plant supports this:

1. **Enable IP Control**: On the Power Plant’s network settings page, see if there’s an option for “Telnet” or “SSH” or something referencing direct IP control.
2. **Command Set**: Consult the user manual or integrator guides to find a list of valid text commands (e.g., “POWER ON” or “OUTLET1 ON”).
3. **Send Commands**: Use a Telnet client (e.g., PuTTY or a custom script) to connect to the Power Plant’s IP on the correct port (23 for Telnet, 22 for SSH). Then issue the appropriate command to turn on the device or specific zones.

---

## 3. Using a 12V Trigger (Hardware Control)

If your system doesn’t provide an accessible network/HTTP API, or if you prefer hardware-level control:

1. **12V Trigger Port**: Many Power Plants have a 12V trigger input. You can send a 12V “turn on” signal from another device—like a preamp, AV receiver, or home automation controller—to power on the regenerator automatically.
2. **Wiring**: Use a standard 3.5mm mono cable, where the tip is +12V and the sleeve is ground.
3. **Programming**: If your preamp or system controller can send out a 12V trigger when you power on your system, the Power Plant will turn on as soon as it sees that voltage.

---

## 4. Integration with Automation Systems (Control4, Crestron, etc.)

For users with a custom-installed environment:

1. **Check for PS Audio Drivers**: Many integrators have built device drivers (often available in their respective driver stores) for Crestron, Control4, Savant, etc.
2. **Setup**: Install the driver, input the Power Plant’s IP address, and you’ll get control over power on/off, zone management, and more directly from your automation system’s GUI or programming interface.

---

## Additional Notes

- **Firmware Version**: Different firmware versions may alter how the network interface or commands work. If you’re not seeing an easy method, consider updating the Power Plant firmware or consulting the release notes.
- **Documentation**: PS Audio often provides integrator notes and documentation on their site. Search for “PS Audio” + your Power Plant model + “Integrator’s Guide” or “Network Control” to see if there’s an official PDF with instructions.
- **Security**: If you expose any controls externally (e.g., port forwarding from your router), be mindful of security. Ideally, keep control on your local network or behind a secure VPN.

---

### Bottom Line

**The most straightforward method** for many users is to sniff the HTTP request that the Power Plant’s built-in web page sends (via browser Dev Tools) and replicate it in code. This technique doesn’t require special drivers or complex configuration—just basic web request knowledge. Alternatively, if the device supports a standard integrator protocol (Telnet/SSH or 12V trigger), you can use that for a more direct approach.

If you have more specifics about your exact Power Plant model, or your preferred programming environment (e.g., Python scripts, Node-RED flows, or control system macros), let me know—I can offer more targeted guidance!


#### You:
<time datetime="2025-02-01T18:07:55.716Z" title="2/2/2025, 3:07:55 AM">03:07</time>


Disable Cache
219 requests
48.40 kB / 67.28 kB transferred
Finish: 20.08 s
	
GET
	http://192.168.1.37/zones.cgi?zone=0
Status
200
OK
VersionHTTP/1.1
Transferred98 B (10 B size)
Referrer Policystrict-origin-when-cross-origin
Request PriorityHighest
DNS ResolutionSystem

	
Cache-Control
	no-cache
Connection
	close
Content-Type
	text/html
	
Accept
	*/*
Accept-Encoding
	gzip, deflate
Accept-Language
	en-US,en;q=0.5
Connection
	keep-alive
DNT
	1
Host
	192.168.1.37
Priority
	u=0
Referer
	http://192.168.1.37/index.htm
Sec-GPC
	1
User-Agent
	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0






---






Disable Cache
317 requests
70.45 kB / 97.85 kB transferred
Finish: 36.37 s
	
GET
	http://192.168.1.37/zones.cgi?zone=0
Status
200
OK
VersionHTTP/1.1
Transferred98 B (10 B size)
Referrer Policystrict-origin-when-cross-origin
Request PriorityHighest
DNS ResolutionSystem

	
Cache-Control
	no-cache
Connection
	close
Content-Type
	text/html
	
Accept
	*/*
Accept-Encoding
	gzip, deflate
Accept-Language
	en-US,en;q=0.5
Connection
	keep-alive
DNT
	1
Host
	192.168.1.37
Priority
	u=0
Referer
	http://192.168.1.37/index.htm
Sec-GPC
	1
User-Agent
	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0




#### ChatGPT:
<time datetime="2025-02-01T18:08:17.870Z" title="2/2/2025, 3:08:17 AM">03:08</time>

It looks like you’re capturing the **status request** to `zones.cgi?zone=0` rather than the **command** that actually toggles the unit on or off. In many web interfaces, there’s one endpoint that retrieves the current state and another (or the same endpoint with extra parameters) that issues commands (e.g., “turn on”).

When you open Developer Tools and click the “Power On” (or “Power Off”) button in the UI, the request responsible for toggling the power may be:

- A **different** `GET` or `POST` request with extra parameters (e.g., `zones.cgi?zone=0&power=1` or `zones.cgi?zone=0&cmd=on`).
- Or possibly a **JavaScript** call that happens in the background which you’re not currently seeing in the Network tab.

Below are some tips to find the actual toggle request and replicate it programmatically.

---

## 1. Confirm the Actual Toggle Request

1. **Reload Developer Tools**
   - In your browser (Firefox or Chrome), open the Network tab in Developer Tools.
   - Make sure “Preserve log” is checked so you don’t lose any network events when the page navigates or refreshes.

2. **Click the “On” or “Off” Button**
   - Perform the exact action on the control panel page that turns the Power Plant on/off.
   - Watch the Network tab to see if a **new** request shows up immediately after you click.

3. **Compare Requests**
   - The request you currently see, `GET zones.cgi?zone=0`, could simply be polling or retrieving status.
   - Look for something with additional parameters or a different endpoint, for example:
     - `zones.cgi?zone=0&cmd=1`
     - `zones.cgi?zone=0&power=on`
     - `zones.cgi?command=zone_on`
   - Sometimes the UI might do a **POST** request with form data or JSON body. If so, you’ll see a `Request Method: POST` in the Dev Tools.

---

## 2. Inspect the HTML / JavaScript Code

If you can’t see any obvious extra request in the Network panel:

1. **View Page Source** or **Inspect the JavaScript**
   - Right-click the page and choose “View Source” (or open the `.js` files you see under the Sources tab).
   - Look for JavaScript functions that might look like `function setZone(zone, value)` or `function powerToggle(...)`.
2. **Check Form Submissions**
   - If there’s an HTML form around the power button, it might be submitting a hidden input or special parameter.
3. **Search for “cgi”**
   - Many times, the code that toggles the power will be calling `zones.cgi` with a parameter like `&power=1` or `&turn_on=true`.

---

## 3. Replicate the Command Programmatically

Once you identify the correct request:

1. **Use cURL or Python**
   - A typical command might be:
     ```bash
     curl "http://192.168.1.37/zones.cgi?zone=0&power=1"
     ```
     or in Python:
     ```python
     import requests

     r = requests.get("http://192.168.1.37/zones.cgi?zone=0&power=1")
     print(r.text)
     ```
   - If it’s a **POST** request, you’d do something like:
     ```bash
     curl -X POST "http://192.168.1.37/zones.cgi" \
       -d "zone=0&power=on"
     ```
2. **Include Any Required Headers or Cookies**
   - If the web interface requires a session token or Basic Auth, replicate that in your request.
   - You can see the exact headers in Developer Tools under the “Headers” tab for the toggle request.

---

## 4. Validate the Response

After you send the toggle request via a script:

- Check the Power Plant physically (or in the web UI) to see if it turned on/off.
- Look at the response text (HTML or JSON) to confirm success. Sometimes the device returns a short HTML snippet that says “OK” or “DONE.”

---

### If You Still Only See `zones.cgi?zone=0`

- That might be just a **status poll**, and the real toggle command could be embedded in JavaScript or handled in some other hidden way.
- Some devices poll the same CGI endpoint with different query parameters—**pay close attention** to any differences in the URL or to the `Query String Parameters` in Dev Tools.

---

## 5. Alternative Paths

If the device truly **doesn’t expose** a straightforward HTTP command for power on/off, you could investigate:

- **Telnet / SSH Commands**: Some PS Audio units (especially older ones) might support Telnet with a limited set of ASCII commands.
- **12V Trigger**: Using a hardware trigger from a preamp or home automation controller (less likely what you want for direct software control, but an option).
- **Automation Driver**: If you use Control4, Crestron, or similar, see if there is a PS Audio or third-party driver that can handle the request logic behind the scenes.

---

### Summary

**The key** is to capture or figure out the **exact** request that changes the Power Plant’s state (turn on/off). The logs you showed (`GET /zones.cgi?zone=0`) are almost certainly just the status checks. You need to watch for what happens in the Network tab *right when* you click the “On” or “Off” button. Once you find the correct request, you can replicate it from your code or script.


#### You:
<time datetime="2025-02-01T19:19:51.385Z" title="2/2/2025, 4:19:51 AM">04:19</time>

it looks like simply making a GET request to that URL toggles the power on and off

make a home assistant entity to turn this switch off and on

#### ChatGPT:
<time datetime="2025-02-01T19:20:03.636Z" title="2/2/2025, 4:20:03 AM">04:20</time>

Below is one straightforward way to add a **Home Assistant** switch entity that toggles your PS Audio PowerPlant via an HTTP GET request. Because you mentioned that **just calling the same URL toggles power on/off**, we have to handle the fact that there isn’t a separate endpoint for “on” vs. “off.”

However, Home Assistant expects distinct actions for turning something on vs. turning it off—and a method to check state. We can work around this with a **template switch** that calls a REST command to toggle power and polls a separate status request to figure out if the device is currently on or off.

---

## 1. Check if You Can Poll a Status

First, see if the PowerPlant returns any *parsable* status text. Sometimes the same `zones.cgi?zone=0` or a different request might include something like `"POWER=1"` or `"POWER=0"` in the response, or some other indicator to show it’s on or off. This is important so Home Assistant can accurately reflect the current state (rather than always assuming it succeeded).

If the response is purely toggling without any extra status info, you have two main options:

1. **Use a second endpoint** (if available) that gives definitive on/off data.
2. **Accept that Home Assistant might not always be fully synced** with the PowerPlant’s true state (since we only have a toggle command).

For this example, let’s assume:

- **Toggling**: `GET http://192.168.1.37/zones.cgi?zone=0` toggles power.
- **Status**: `GET http://192.168.1.37/zones.cgi?zone=0` (the same or a similar request) returns text like `POWER=1` (or something that indicates on/off).

If you **don’t** have a reliable status in the response, skip the `binary_sensor` part and just accept a “stateless” toggle switch.

---

## 2. Define a REST Command for the Toggle

In your `configuration.yaml`, or a package YAML file, create a `rest_command`:

```yaml
rest_command:
  ps_audio_power_toggle:
    url: "http://192.168.1.37/zones.cgi?zone=0"
    method: GET
```

This defines a single REST command in Home Assistant that, when called, sends a GET request to `http://192.168.1.37/zones.cgi?zone=0`. That’s our “toggle” call.

---

## 3. (Optional) Create a REST Sensor or Binary Sensor for State

If the device’s response to `zones.cgi?zone=0` (or a different endpoint) shows whether it’s currently on or off, you can have a sensor track that. For example:

```yaml
binary_sensor:
  - platform: rest
    name: "PS Audio Status"
    resource: "http://192.168.1.37/zones.cgi?zone=0"
    scan_interval: 10
    value_template: >-
      {% if "POWER=1" in value %}
        on
      {% else %}
        off
      {% endif %}
```

- `scan_interval: 10` means Home Assistant will poll this endpoint every 10 seconds.
- `value_template` checks if the returned text includes `"POWER=1"`. If yes, it’s on; otherwise off.
- Adjust this template based on the **actual** response string you see. You might need to `{{ if "on" in value }}` or `POWER=ON` or something else.

---

## 4. Make a Template Switch to Tie Them Together

Finally, we combine the REST command (toggle) and the binary sensor (status) into a switch that Home Assistant can show in the UI:

```yaml
switch:
  - platform: template
    switches:
      ps_audio_powerplant:
        friendly_name: "PS Audio PowerPlant"
        value_template: "{{ is_state('binary_sensor.ps_audio_status', 'on') }}"
        turn_on:
          - service: rest_command.ps_audio_power_toggle
        turn_off:
          - service: rest_command.ps_audio_power_toggle
```

Here’s what’s happening:

- **`value_template`**: The switch checks the state of our `binary_sensor.ps_audio_status`. If that sensor is “on,” Home Assistant will show the switch as ON.
- **`turn_on` / `turn_off`**: Both call the same `rest_command.ps_audio_power_toggle`, because the device only has a toggle endpoint.
- Home Assistant will call `turn_on` if you click the switch from OFF to ON, and call `turn_off` if you click it from ON to OFF. Because the endpoint just toggles, the net effect is “on” if it was off, and “off” if it was on.

---

### If You Don’t Have a Real Status Endpoint

If the device doesn’t provide any reliable info about whether it’s actually on or off, you can omit the `binary_sensor` and simplify to a **command line switch** or **template switch** with no state check. For instance:

```yaml
switch:
  - platform: command_line
    switches:
      ps_audio_powerplant:
        command_on: 'curl "http://192.168.1.37/zones.cgi?zone=0"'
        command_off: 'curl "http://192.168.1.37/zones.cgi?zone=0"'
        friendly_name: "PS Audio PowerPlant"
```

But note: Home Assistant will assume it’s on if you press ON, and off if you press OFF, regardless of the actual device state—so they can drift out of sync.

---

## 5. Restart Home Assistant and Test

1. Save your changes to `configuration.yaml` (or your separate YAML files), then check your config in Home Assistant:
   ```bash
   ha core check
   ```
2. If there are no errors, restart:
   ```bash
   ha core restart
   ```
3. After Home Assistant comes back, look for the “PS Audio PowerPlant” switch in the **States** or **Devices** & **Entities** list.
4. Click it in the UI to see if it toggles your PowerPlant. If you’ve set up the **binary sensor**, watch to see if the state updates properly within \~10 seconds or so.

---

## Tips & Considerations

- **Polling Interval**: The default for the REST sensor is 30 seconds. You can lower `scan_interval` to 5 or 10 seconds if you want faster updates (but be mindful of network spam).
- **Security**: If your PowerPlant is behind your local network, that’s typically okay. If you open this to the internet (port forwarding), it can be a security risk.
- **Troubleshooting**:
  - Check Home Assistant logs for template or rest command errors.
  - Try the `curl` command manually in a terminal to confirm it really toggles the device.
  - If the device requires any special headers or cookies, add them under `headers:` in the `rest_command`.

---

### Conclusion

With the above setup, you’ll have a working switch entity in Home Assistant that sends a toggle request to your PS Audio device. If the device returns enough information to distinguish on/off states, you can keep your UI in sync via a REST binary sensor. Otherwise, you’ll at least have basic toggling control, albeit with no guaranteed knowledge of the actual power state.

Enjoy integrating your PowerPlant into Home Assistant! If you need further refinements—like reading THD measurements or voltage data from the unit’s status page—similar REST sensors can be configured to parse those values and display them in Home Assistant, too.


#### You:
<time datetime="2025-02-01T19:23:30.071Z" title="2/2/2025, 4:23:30 AM">04:23</time>


http://192.168.1.37/zones.cgi?zone=0 this toggles the power

http://192.168.1.37/zones.cgi this returns "Success! 1" if power is on and "Success! 0" if power is off

update the script 

#### ChatGPT:
<time datetime="2025-02-01T19:23:46.592Z" title="2/2/2025, 4:23:46 AM">04:23</time>

Below is a complete **Home Assistant** snippet illustrating how to:

1. **Poll** the device state from `http://192.168.1.37/zones.cgi`—which returns `"Success! 1"` if power is on and `"Success! 0"` if power is off.
2. **Toggle** the power (on/off) via `http://192.168.1.37/zones.cgi?zone=0`.

It includes the **binary sensor** for state and a **template switch** that uses a REST command to toggle.

```yaml
# 1) REST command to toggle power
rest_command:
  ps_audio_toggle:
    url: "http://192.168.1.37/zones.cgi?zone=0"
    method: GET

# 2) Binary sensor to read current status
binary_sensor:
  - platform: rest
    name: "PS Audio Status"
    resource: "http://192.168.1.37/zones.cgi"
    scan_interval: 10
    value_template: >-
      {% if "Success! 1" in value %}
        on
      {% else %}
        off
      {% endif %}

# 3) Template switch that:
#    - Reads 'binary_sensor.ps_audio_status' for current on/off state
#    - Calls ps_audio_toggle for turn_on and turn_off
switch:
  - platform: template
    switches:
      ps_audio_powerplant:
        friendly_name: "PS Audio PowerPlant"
        value_template: "{{ is_state('binary_sensor.ps_audio_status', 'on') }}"
        turn_on:
          service: rest_command.ps_audio_toggle
        turn_off:
          service: rest_command.ps_audio_toggle
```

### How It Works

- **Binary Sensor**:
  - Home Assistant polls `zones.cgi` every `scan_interval` seconds (in this example, every 10s).
  - If the response contains `Success! 1`, we set the sensor to `on`; otherwise `off`.

- **Switch**:
  - The switch’s **`value_template`** references the binary sensor’s state. If that sensor is `on`, the switch is displayed as ON in the UI.
  - **`turn_on`** and **`turn_off`** both call `rest_command.ps_audio_toggle`, because we only have a toggle endpoint.

This means that when you click the switch in Home Assistant, it sends a GET request to `http://192.168.1.37/zones.cgi?zone=0` (thus toggling the power). A few seconds later, the binary sensor re-polls `zones.cgi` to confirm whether it’s now `on` (`Success! 1`) or `off` (`Success! 0`), updating the switch state accordingly.


#### You:
<time datetime="2025-02-01T19:27:48.197Z" title="2/2/2025, 4:27:48 AM">04:27</time>

why is the template switch needed?


#### ChatGPT:
<time datetime="2025-02-01T19:27:53.992Z" title="2/2/2025, 4:27:53 AM">04:27</time>

A **template switch** is needed because:

- **Home Assistant’s built-in REST Switch** expects distinct URLs or payloads for `turn_on` vs. `turn_off`, as well as a direct endpoint that indicates on/off state. In your case, you have:
  - A **single toggle endpoint** (`zones.cgi?zone=0`) rather than separate URLs (like `/on` or `/off`).
  - Another **endpoint** (`zones.cgi`) that returns `"Success! 1"` or `"Success! 0"` for the state.

- By contrast, a **template switch** gives you the flexibility to:
  1. Use the **binary sensor** to determine true on/off status by parsing `"Success! 1"` vs. `"Success! 0"`.
  2. Call the **same toggle endpoint** for both `turn_on` and `turn_off`.

In essence, the template switch merges these two aspects (toggle command + status checking) into a single switch entity in Home Assistant. This allows the UI to display a proper “on/off” state while still calling the single toggle URL in the background. If you tried to do this with just one built-in integration, you would typically need separate “on” and “off” commands, which you don’t have here.


#### You:
<time datetime="2025-02-01T19:28:16.107Z" title="2/2/2025, 4:28:16 AM">04:28</time>

should i disable the first switch then?

#### ChatGPT:
<time datetime="2025-02-01T19:28:19.931Z" title="2/2/2025, 4:28:19 AM">04:28</time>

If you have a **template switch** set up as shown (where it references the binary sensor for the “on/off” state and calls the toggle endpoint), there’s typically no need for the original REST-based switch entity (the “first switch”). In fact, having both could cause confusion or out-of-sync states in the UI.

Usually you’d remove or comment out any earlier switch configuration, **unless** you want to keep it around for testing or alternate control. In most scenarios, the single template switch (backed by the binary sensor) is the cleaner, more consistent solution.


#### You:
<time datetime="2025-02-01T19:28:39.160Z" title="2/2/2025, 4:28:39 AM">04:28</time>

is thi ssufficient then?
```
binary_sensor:
  - platform: rest
    name: "PS Audio Status"
    unique_id: "sensor_ps_audio_powerplant_001ff60024ad"
    resource: "http://192.168.1.37/zones.cgi"
    scan_interval: 10
    value_template: >-
      {% if "Success! 1" in value %}
        on
      {% else %}
        off
      {% endif %}

# 3) Template switch that:
#    - Reads 'binary_sensor.ps_audio_status' for current on/off state
#    - Calls ps_audio_toggle for turn_on and turn_off
switch:
  - platform: template
    switches:
      ps_audio_powerplant:
        friendly_name: "PS Audio PowerPlant"
        unique_id: "switch_ps_audio_powerplant_001ff60024ad"
        value_template: "{{ is_state('binary_sensor.ps_audio_status', 'on') }}"
        turn_on:
          service: rest_command.ps_audio_toggle
        turn_off:
          service: rest_command.ps_audio_toggle

#### ChatGPT:
<time datetime="2025-02-01T19:28:45.047Z" title="2/2/2025, 4:28:45 AM">04:28</time>

Almost—one more piece is needed. You also need to include the **`rest_command`** definition for `ps_audio_toggle` somewhere in your Home Assistant configuration, because your switch calls that service when turned on or off. Without it, Home Assistant won’t know how to send the toggle request.

So your final setup should look like this (all together, or split appropriately in your config):

```yaml
rest_command:
  ps_audio_toggle:
    url: "http://192.168.1.37/zones.cgi?zone=0"
    method: GET

binary_sensor:
  - platform: rest
    name: "PS Audio Status"
    unique_id: "sensor_ps_audio_powerplant_001ff60024ad"
    resource: "http://192.168.1.37/zones.cgi"
    scan_interval: 10
    value_template: >-
      {% if "Success! 1" in value %}
        on
      {% else %}
        off
      {% endif %}

switch:
  - platform: template
    switches:
      ps_audio_powerplant:
        friendly_name: "PS Audio PowerPlant"
        unique_id: "switch_ps_audio_powerplant_001ff60024ad"
        value_template: "{{ is_state('binary_sensor.ps_audio_status', 'on') }}"
        turn_on:
          service: rest_command.ps_audio_toggle
        turn_off:
          service: rest_command.ps_audio_toggle
```

With that **rest\_command** in place, this config should be sufficient for Home Assistant to:

1. **Poll** the device state (on/off) every 10 seconds.
2. **Reflect** that state in the template switch.
3. **Toggle** power on or off using the single toggle endpoint.


#### You:
<time datetime="2025-02-01T19:29:06.324Z" title="2/2/2025, 4:29:06 AM">04:29</time>

any other simplifications to make?

#### ChatGPT:
<time datetime="2025-02-01T19:29:26.829Z" title="2/2/2025, 4:29:26 AM">04:29</time>

Your current setup is already quite minimal and clear. You have:

- One **rest\_command** for toggling power.
- One **binary\_sensor** that polls the device’s true on/off state.
- One **template switch** that ties those two together into a user-friendly Home Assistant entity.

That approach is typically the **cleanest** for a single “toggle” endpoint and a separate status check.

### Possible Simplifications

1. **Combine Into a Single Command-Line Switch**
   - You can theoretically use a [command\_line switch](https://www.home-assistant.io/integrations/command_line/#switch) that calls the same toggle URL for both `command_on` and `command_off`, and then uses `command_state` to poll the status.
   - **However,** because the endpoint is just “toggle,” you can accidentally get out of sync. For instance, if the device is already on and you call `command_on`, the device will turn off. This creates a confusing user experience unless you’re very careful about always matching your actions to the device’s actual state.

2. **Remove Unused Keys**
   - If you want to shave off a line, you could remove `method: GET` from the rest\_command, since GET is usually the default. But that’s purely stylistic and doesn’t affect functionality.

3. **Hide or Omit `unique_id`**
   - If you don’t need each entity to have a unique ID for UI customization, you can omit `unique_id`. This is personal preference—some people find it helpful for renaming in the UI or easily disabling the entity.

Other than those minor things, you’re already at the simplest robust solution for an **endpoint that only toggles** and another endpoint that **reports on/off**. The template switch pattern is common in Home Assistant for exactly this scenario. Unless you have specific reasons to unify or reduce lines, your current config is both concise and reliable.

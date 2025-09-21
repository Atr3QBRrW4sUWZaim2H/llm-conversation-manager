---
title: Ubuntu TV Display Issue
source: https://chatgpt.com/c/6788134a-c1c0-8003-81b2-5f4f911394d8
---

# Ubuntu TV Display Issue

#### You:
<time datetime="2025-01-15T19:58:56.118Z" title="1/16/2025, 4:58:56 AM">04:58</time>

my ubuntu desktop is connected to my tv and there is no signal. i can see a desktop when i use remote desktop and I can see the bios during POST. help me show a gui desktop on my tv

#### ChatGPT:
<time datetime="2025-01-15T19:59:08.140Z" title="1/16/2025, 4:59:08 AM">04:59</time>

Below are a few troubleshooting steps and methods you can try to get your Ubuntu desktop’s GUI displaying on your TV. Since you can see the BIOS splash screen and use remote desktop, but not see the Ubuntu GUI on the TV directly, it’s often a graphics configuration or resolution issue.

---

## 1. Double-check physical connections


#### You:
<time datetime="2025-01-15T19:59:38.212Z" title="1/16/2025, 4:59:38 AM">04:59</time>

ashwin@ubuntu-server:~/.hqplayer$ xrandr
Can't open display 
ashwin@ubuntu-server:~/.hqplayer$ xrandr --output HDMI-1 --mode 1920x1080 --rate 60
Can't open display 
ashwin@ubuntu-server:~/.hqplayer$ 

#### ChatGPT:
<time datetime="2025-01-15T20:00:33.413Z" title="1/16/2025, 5:00:33 AM">05:00</time>

When you see errors like “Can't open display” while running `xrandr`, it usually means one of two things:

1. **No local X session** is running on the machine (i.e., you’re in a headless or server-like configuration without a desktop manager).
2. **You’re not connected to (or haven’t specified) the correct DISPLAY** environment variable while running commands via SSH/remote shell.

Below is a checklist and set of steps to figure out why your HDMI output is black even though you see the BIOS splash and can remote into Ubuntu.

---

## 1. Confirm that a local GUI session is actually running

1. **Are you on Ubuntu Desktop or Ubuntu Server?**
   - If this is truly Ubuntu Server, there may not be a local desktop manager (like GDM or LightDM) running. In that case, you’ll need to install and/or enable one in order to have a local GUI on the TV.

2. **Check if a display manager is running.**
   - On Ubuntu, you can check with:
     ```bash
     systemctl status gdm
     # or
     systemctl status lightdm
     ```
   - If you see “not found” or it’s inactive, then the system is not running a graphical login manager. You can install or enable one, for example:
     ```bash
     sudo apt-get update
     sudo apt-get install gdm3
     sudo systemctl enable gdm
     sudo systemctl start gdm
     ```
   - Afterward, confirm that the system boots into a graphical login screen on the attached monitor/TV.

---

## 2. Make sure you run `xrandr` inside (or pointing to) an active X session

- **The “Can't open display” error** means that the `xrandr` command can’t find the X server. If you’re SSHing in (or on a text console TTY), you must point `xrandr` to a running X server.
- **If your desktop environment is on display `:0`,** you can force `xrandr` to use that display by setting `DISPLAY` before running the command:
  ```bash
  export DISPLAY=:0
  xrandr --output HDMI-1 --mode 1920x1080 --rate 60
  ```
  Or prepend it:
  ```bash
  DISPLAY=:0 xrandr --output HDMI-1 --mode 1920x1080 --rate 60
  ```
- **If no display manager is running on the local machine**, there is no X server on `:0`. That would explain why `xrandr` fails.

---

## 3. Check your GPU drivers and monitor detection

1. **Check dmesg for HDMI detection**\
   Sometimes the OS may not detect the connected TV if there are driver or cable issues:
   ```bash
   dmesg | grep -i hdmi
   ```
   Look for messages about the HDMI port being connected or any errors.

2. **Check that your GPU drivers are loaded**
   - If you’re using NVIDIA, try:
     ```bash
     ubuntu-drivers devices
     ```
     and see if a recommended driver is available and install it if needed:
     ```bash
     sudo apt-get install nvidia-driver-<version>
     ```
   - Then reboot to ensure the new driver loads.

3. **Verify the monitor is recognized**
   - Once you have a running X server, check:
     ```bash
     DISPLAY=:0 xrandr -q
     ```
     and ensure you see an output like `HDMI-1 connected`.

---

## 4. Check GRUB or kernel parameters (in some cases)

- Sometimes Ubuntu is set with `nomodeset` in the kernel parameters (in `/etc/default/grub`) which can prevent the usual driver from picking up the display. Look for a line like:
  ```
  GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nomodeset"
  ```
  Removing `nomodeset` (if it’s not needed) and then running:
  ```bash
  sudo update-grub
  sudo reboot
  ```
  might allow the system to properly set the resolution on the HDMI port.

---

## 5. If you only see BIOS/POST on the TV but no Ubuntu splash

- **BIOS/POST is often output directly by the GPU firmware**, independent of the OS drivers. Once Ubuntu starts, the X (or Wayland) drivers need to detect the display and set up the signal.
- If you do not have a desktop manager installed, or if the GPU driver is misconfigured, Ubuntu will effectively stop sending any video signal after the BIOS handoff.

---

## Summary of what to do next

1. **Ensure you have a desktop environment and display manager installed** (if you intend to use a true GUI on the TV).
2. **Ensure that the display manager is enabled and running** so that you actually have an X session on the HDMI port.
3. **From a remote SSH shell, set `DISPLAY=:0`** (or whichever display your GUI is using) before running `xrandr`.
4. **Confirm the system recognizes the HDMI connection** by checking `dmesg` or `xrandr` output.
5. **Install the correct GPU driver** if you haven’t already, and remove any unneeded `nomodeset` kernel parameters.

Once you do all of the above and reboot, you should be able to get a proper GUI signal on your TV (assuming hardware connections are fine and the TV supports the resolution/refresh rate).


#### You:
<time datetime="2025-01-15T20:01:24.270Z" title="1/16/2025, 5:01:24 AM">05:01</time>

ashwin@ubuntu-server:~/.hqplayer$ systemctl status gdm
● gdm.service - GNOME Display Manager
     Loaded: loaded (/usr/lib/systemd/system/gdm.service; static)
     Active: active (running) since Wed 2025-01-15 10:47:07 PST; 1h 14min ago
   Main PID: 2484 (gdm3)
      Tasks: 4 (limit: 76048)
     Memory: 6.8M (peak: 78.0M)
        CPU: 412ms
     CGroup: /system.slice/gdm.service
             └─2484 /usr/sbin/gdm3

Jan 15 10:47:07 ubuntu-server systemd[1]: Starting gdm.service - GNOME Display Manager...
Jan 15 10:47:07 ubuntu-server systemd[1]: Started gdm.service - GNOME Display Manager.
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: gkr-pam: no password is available for user
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: pam_unix(gdm-autologin:session): session opened for user ashwin(uid=1000) by ashwin(uid=0)
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: gkr-pam: couldn't unlock the login keyring.
Jan 15 10:47:10 ubuntu-server gdm3[2635]: Timed out for waiting the udev queue being empty.
ashwin@ubuntu-server:~/.hqplayer$ '

#### ChatGPT:
<time datetime="2025-01-15T20:02:46.396Z" title="1/16/2025, 5:02:46 AM">05:02</time>

Let’s summarize the situation so far:

1. You have Ubuntu “Server” (or at least a system originally installed as server) but **GDM** (GNOME Display Manager) is installed and running.
2. You see a normal BIOS/POST screen on your TV (so the TV and HDMI cable are connected physically, and the firmware/boot output is working).
3. Once Ubuntu starts, the TV shows **no signal**.
4. Over SSH, attempting `xrandr` gives “Can’t open display,” meaning no visible X/Wayland session is found or accessible through your SSH shell.

Below is a methodical way to troubleshoot why your TV remains dark even though GDM is running.

---

## 1. Verify an actual (X or Wayland) graphical session is running

Even if GDM is running, it may be failing to create an active display (for example, a GPU driver issue or a misconfiguration can prevent Xorg/Wayland from starting properly). Let’s check a few things:

1. **Check for an Xorg or Wayland process:**

   ```bash
   ps aux | grep -E "Xorg|wayland|gnome-shell"
   ```

   - If `Xorg` or `gnome-shell` are running, it means a session might be up.
   - If you only see `gdm3` (and no Xorg or Wayland process), then GDM might be failing to start a graphical session.

2. **Check loginctl for active sessions**:

   ```bash
   loginctl
   ```

   Look for a session that is `seat0` and belongs to your user (or GDM). For example, you might see something like:

   ```
   SESSION  UID  USER   SEAT  TTY  
       c1   1000 ashwin seat0 tty2
   ```

   If there is no session on seat0 or it’s “inactive,” GDM may not have launched a session on the local display.

3. **Check the Xorg log or GDM logs for errors**:

   - If using Xorg, look in:
     ```
     /var/log/Xorg.0.log
     /var/log/Xorg.1.log
     ```
     or in newer Ubuntu releases, logs might be under:
     ```
     /var/lib/gdm3/.local/share/xorg/Xorg.0.log
     ```
   - If GDM is using Wayland, you might look in the journal:
     ```bash
     journalctl -b 0 -u gdm -u gdm3
     ```
     or:
     ```bash
     journalctl -b | grep -E "(Xorg|gdm|gnome-shell)"
     ```

   Look for lines like “No screens found,” “Failed to create screen,” or EDID/monitor detection errors.

---

## 2. Confirm that your GPU is recognized and has proper drivers

If the underlying GPU driver is missing or misconfigured, Xorg (or Wayland) won’t be able to set a mode on your HDMI port.

1. **Check what GPU is in your system**:
   ```bash
   sudo lspci -k | grep -EA3 "VGA|3D|Display"
   ```
   See if it’s Intel, AMD, or NVIDIA (or something else).

2. **Install drivers if needed**:
   - For **Intel** or **AMD**, usually the open-source drivers included with the kernel just work.
   - For **NVIDIA**, you may need to install the proprietary driver:
     ```bash
     sudo ubuntu-drivers devices
     sudo apt-get install nvidia-driver-<version>
     ```
   - Reboot after installing or updating drivers.

3. **Check for kernel parameters**:
   - If `/etc/default/grub` contains `nomodeset`, remove it unless you have a specific reason for using it. Then:
     ```bash
     sudo update-grub
     sudo reboot
     ```
   - `nomodeset` often causes the system to use a very basic fallback driver that doesn’t support normal modes on HDMI.

---

## 3. Ensure GDM is actually trying to use your HDMI output

Sometimes, if you have more than one GPU or if Xorg is configured incorrectly, GDM might be launching on a “virtual display” instead of the physical HDMI port.

1. **Check `xrandr` while specifying DISPLAY**\
   Since you’re connecting via SSH, you must explicitly point to the local display environment. If GDM is on display `:0`, try:
   ```bash
   export DISPLAY=:0
   xrandr -q
   ```
   or
   ```bash
   DISPLAY=:0 xrandr -q
   ```
   - If you still see “Can't open display :0,” it means no running X server is actually bound to `:0` or you don’t have permission.

2. **If Wayland is enabled** (the default on newer Ubuntu):
   - `xrandr` won’t work in a pure Wayland session; you might get an error about not being able to open display.
   - You can force GDM to use Xorg by editing `/etc/gdm3/custom.conf` and uncommenting or adding:
     ```
     WaylandEnable=false
     ```
   - Then `sudo systemctl restart gdm` (or reboot).

---

## 4. Look for EDID / resolution problems

Some TVs don’t always provide correct EDID data or might not like the default refresh rate. This can cause a black screen if Ubuntu tries a resolution or refresh rate the TV doesn’t support.

1. **Try lower resolutions or different refresh rates**\
   Once you can run `xrandr -q` or a Wayland equivalent, try modes like `1920x1080@30`, `1280x720@60`, etc., to see if it lights up the TV.

2. **Check `dmesg` for HDMI detection**
   ```bash
   dmesg | grep -i hdmi
   ```
   If you see messages about “HDMI disconnected” or EDID read errors, that might indicate a


#### You:
<time datetime="2025-01-15T20:05:27.048Z" title="1/16/2025, 5:05:27 AM">05:05</time>

i have 2 gpus. the 4090 is for ml workloads only and does not display anything. i am using my onboard amd gpu to display the tv.

---
ashwin@ubuntu-server:~/.hqplayer$ systemctl status gdm
● gdm.service - GNOME Display Manager
     Loaded: loaded (/usr/lib/systemd/system/gdm.service; static)
     Active: active (running) since Wed 2025-01-15 10:47:07 PST; 1h 14min ago
   Main PID: 2484 (gdm3)
      Tasks: 4 (limit: 76048)
     Memory: 6.8M (peak: 78.0M)
        CPU: 412ms
     CGroup: /system.slice/gdm.service
             └─2484 /usr/sbin/gdm3

Jan 15 10:47:07 ubuntu-server systemd[1]: Starting gdm.service - GNOME Display Manager...
Jan 15 10:47:07 ubuntu-server systemd[1]: Started gdm.service - GNOME Display Manager.
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: gkr-pam: no password is available for user
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: pam_unix(gdm-autologin:session): session opened for user ashwin(uid=1000) by ashwin(uid=0)
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: gkr-pam: couldn't unlock the login keyring.
Jan 15 10:47:10 ubuntu-server gdm3[2635]: Timed out for waiting the udev queue being empty.
ashwin@ubuntu-server:~/.hqplayer$ ps aux | grep -E "Xorg|wayland|gnome-shell"
root        2655  0.0  0.1 25417960 74268 tty2   Sl+  10:47   0:01 /usr/lib/xorg/Xorg vt2 -displayfd 3 -auth /run/user/1000/gdm/Xauthority -nolisten tcp -background none -noreset -keeptty -novtswitch -verbose 3
ashwin      2900  0.0  0.3 4000396 228256 ?      Ssl  10:47   0:01 /usr/bin/gnome-shell
ashwin      2970  0.0  0.0 655984 19944 ?        Sl   10:47   0:00 /usr/libexec/gnome-shell-calendar-server
ashwin      2988  0.0  0.0 2671280 25152 ?       Sl   10:47   0:00 /usr/bin/gjs -m /usr/share/gnome-shell/org.gnome.Shell.Notifications
ashwin      4143  0.0  0.0 2802348 25128 ?       Sl   10:47   0:00 /usr/bin/gjs -m /usr/share/gnome-shell/org.gnome.ScreenSaver
ashwin     22481  0.0  0.0  17944  2048 pts/0    S+   12:02   0:00 grep --color=auto -E Xorg|wayland|gnome-shell
ashwin@ubuntu-server:~/.hqplayer$ loginctl
SESSION  UID USER   SEAT  TTY  STATE  IDLE SINCE       
      1 1000 ashwin seat0 tty2 active yes  1h 10min ago
     11 1000 ashwin -     -    active no   -           
      3 1000 ashwin -     -    active no   -           
      5 1000 ashwin -     -    active no   -           

4 sessions listed.
ashwin@ubuntu-server:~/.hqplayer$ journalctl -b 0 -u gdm -u gdm3
Jan 15 10:47:07 ubuntu-server systemd[1]: Starting gdm.service - GNOME Display Manager...
Jan 15 10:47:07 ubuntu-server systemd[1]: Started gdm.service - GNOME Display Manager.
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: gkr-pam: no password is available for user
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: pam_unix(gdm-autologin:session): session opened for user ashwin(uid=1000) by ashwin(uid=0)
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: gkr-pam: couldn't unlock the login keyring.
Jan 15 10:47:10 ubuntu-server gdm3[2635]: Timed out for waiting the udev queue being empty.
ashwin@ubuntu-server:~/.hqplayer$ journalctl -b | grep -E "(Xorg|gdm|gnome-shell)"
Jan 15 10:47:07 ubuntu-server systemd[1]: Starting gdm.service - GNOME Display Manager...
Jan 15 10:47:07 ubuntu-server systemd[1]: Started gdm.service - GNOME Display Manager.
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: gkr-pam: no password is available for user
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: pam_unix(gdm-autologin:session): session opened for user ashwin(uid=1000) by ashwin(uid=0)
Jan 15 10:47:07 ubuntu-server gdm-autologin][2509]: gkr-pam: couldn't unlock the login keyring.
Jan 15 10:47:10 ubuntu-server gdm3[2635]: Timed out for waiting the udev queue being empty.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) Log file renamed from "/var/log/Xorg.pid-2655.log" to "/var/log/Xorg.0.log"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: X.Org X Server 1.21.1.11
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: X Protocol Version 11, Revision 0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: Current Operating System: Linux ubuntu-server 6.8.0-51-generic #52-Ubuntu SMP PREEMPT_DYNAMIC Thu Dec  5 13:09:44 UTC 2024 x86_64
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: Kernel command line: BOOT_IMAGE=/boot/vmlinuz-6.8.0-51-generic root=UUID=0c98e29f-3996-4891-b397-5e03e8f31509 ro quiet splash vt.handoff=7
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: xorg-server 2:21.1.12-1ubuntu1.1 (For technical support please see http://www.ubuntu.com/support)
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: Current version of pixman: 0.42.2
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         Before reporting problems, check http://wiki.x.org
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         to make sure that you have the latest version.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: Markers: (--) probed, (**) from config file, (==) default setting,
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         (++) from command line, (!!) notice, (II) informational,
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         (WW) warning, (EE) error, (NI) not implemented, (??) unknown.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) Log file: "/var/log/Xorg.0.log", Time: Wed Jan 15 10:47:10 2025
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) Using config file: "/etc/X11/xorg.conf"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) Using system config directory "/usr/share/X11/xorg.conf.d"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) ServerLayout "layout"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) |-->Screen "Screen0" (0)
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) |   |-->Monitor "Monitor0"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) |   |-->Device "AMD_GPU"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) |   |-->GPUDevice "NVIDIA_GPU"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Allowing byte-swapped clients
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) Automatically adding devices
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) Automatically enabling devices
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) Automatically adding GPU devices
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) Automatically binding GPU devices
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) Max clients allowed: 256, resource mask: 0x1fffff
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (WW) The directory "/usr/share/fonts/X11/cyrillic" does not exist.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         Entry deleted from font path.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (WW) The directory "/usr/share/fonts/X11/100dpi/" does not exist.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         Entry deleted from font path.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (WW) The directory "/usr/share/fonts/X11/75dpi/" does not exist.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         Entry deleted from font path.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (WW) The directory "/usr/share/fonts/X11/100dpi" does not exist.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         Entry deleted from font path.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (WW) The directory "/usr/share/fonts/X11/75dpi" does not exist.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         Entry deleted from font path.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) FontPath set to:
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         /usr/share/fonts/X11/misc,
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         /usr/share/fonts/X11/Type1,
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         built-ins
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) ModulePath set to "/usr/lib/xorg/modules"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) The server relies on udev to provide the list of input devices.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         If no devices become available, reconfigure udev or disable AutoAddDevices.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Loader magic: 0x5a968ceeb020
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Module ABI versions:
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         X.Org ANSI C Emulation: 0.4
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         X.Org Video Driver: 25.2
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         X.Org XInput driver : 24.4
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         X.Org Server Extension : 10.0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (++) using VT number 2
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: took control of session /org/freedesktop/login1/session/_31
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) xfree86: Adding drm device (/dev/dri/card0)
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Platform probe for /sys/devices/pci0000:00/0000:00:01.1/0000:01:00.0/drm/card0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: got fd for /dev/dri/card0 226:0 fd 14 paused 0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) xfree86: Adding drm device (/dev/dri/card1)
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Platform probe for /sys/devices/pci0000:00/0000:00:08.1/0000:0d:00.0/drm/card1
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: got fd for /dev/dri/card1 226:1 fd 15 paused 0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) OutputClass "nvidia" ModulePath extended to "/usr/lib/x86_64-linux-gnu/nvidia/xorg,/usr/lib/xorg/modules"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) PCI: (1@0:0:0) 10de:2684:10de:16f4 rev 161, Mem @ 0xfb000000/16777216, 0xf000000000/34359738368, 0xf800000000/33554432, I/O @ 0x0000f000/128, BIOS @ 0x????????/524288
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) PCI:*(13@0:0:0) 1002:164e:1043:8877 rev 201, Mem @ 0xf810000000/268435456, 0xf820000000/2097152, 0xfca00000/524288, I/O @ 0x0000e000/256
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) LoadModule: "glx"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Loading /usr/lib/xorg/modules/extensions/libglx.so
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Module glx: vendor="X.Org Foundation"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         compiled for 1.21.1.11, module version = 1.0.0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         ABI class: X.Org Server Extension, version 10.0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) LoadModule: "nvidia"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Loading /usr/lib/x86_64-linux-gnu/nvidia/xorg/nvidia_drv.so
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Module nvidia: vendor="NVIDIA Corporation"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         compiled for 1.6.99.901, module version = 1.0.0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         Module class: X.Org Video Driver
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA dlloader X Driver  565.57.01  Thu Oct 10 12:05:50 UTC 2024
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA Unified Driver for all Supported NVIDIA GPUs
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: releasing fd for 226:0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Loading sub module "fb"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) LoadModule: "fb"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Module "fb" already built-in
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Loading sub module "wfb"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) LoadModule: "wfb"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Loading /usr/lib/xorg/modules/libwfb.so
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Module wfb: vendor="X.Org Foundation"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         compiled for 1.21.1.11, module version = 1.0.0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         ABI class: X.Org ANSI C Emulation, version 0.4
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) NVIDIA(0): Depth 24, (--) framebuffer bpp 32
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) NVIDIA(0): RGB weight 888
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) NVIDIA(0): Default visual is TrueColor
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) NVIDIA(0): Using gamma correction (1.0, 1.0, 1.0)
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "AllowNVIDIAGpuScreens"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Applying OutputClass "nvidia" options to /dev/dri/card0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) NVIDIA(0): Option "AllowEmptyInitialConfiguration"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) NVIDIA(0): Enabling 2D acceleration
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Loading sub module "glxserver_nvidia"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) LoadModule: "glxserver_nvidia"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Loading /usr/lib/x86_64-linux-gnu/nvidia/xorg/libglxserver_nvidia.so
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Module glxserver_nvidia: vendor="NVIDIA Corporation"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         compiled for 1.6.99.901, module version = 1.0.0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]:         Module class: X.Org Server Extension
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA GLX Module  565.57.01  Thu Oct 10 12:09:28 UTC 2024
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA: The X server supports PRIME Render Offload.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0): Valid display device(s) on GPU-0 at PCI:1:0:0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0):     DFP-0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0):     DFP-1
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0):     DFP-2
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0):     DFP-3
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0):     DFP-4
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0):     DFP-5
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0):     DFP-6
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0): NVIDIA GPU NVIDIA GeForce RTX 4090 (AD102-A) at PCI:1:0:0
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0):     (GPU-0)
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0): Memory: 25153536 kBytes
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0): VideoBIOS: 95.02.47.00.01
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0): Detected PCI Express Link width: 16X
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: disconnected
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: Internal TMDS
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: 165.0 MHz maximum pixel clock
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: disconnected
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: Internal DisplayPort
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: 2670.0 MHz maximum pixel clock
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: disconnected
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: Internal TMDS
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: 165.0 MHz maximum pixel clock
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: disconnected
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: Internal DisplayPort
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: 2670.0 MHz maximum pixel clock
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: disconnected
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: Internal TMDS
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: 165.0 MHz maximum pixel clock
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: disconnected
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: Internal DisplayPort
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: 2670.0 MHz maximum pixel clock
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: disconnected
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: Internal TMDS
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: 165.0 MHz maximum pixel clock
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) NVIDIA(0):
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) NVIDIA(0): No modes were requested; the default mode "nvidia-auto-select"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) NVIDIA(0):     will be used as the requested mode.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) NVIDIA(0):
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0): No enabled display devices found; starting anyway because
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(0):     AllowEmptyInitialConfiguration is enabled
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0): Validated MetaModes:
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0):     "NULL"
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0): Virtual screen size determined to be 640 x 480
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (WW) NVIDIA(0): Unable to get display device for DPI computation.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) NVIDIA(0): DPI set to (75, 75); computed from built-in default
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA: Reserving 24576.00 MB of virtual memory for indirect memory
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA:     access.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0): ACPI: failed to connect to the ACPI event daemon; the daemon
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0):     may not be running or the "AcpidSocketPath" X
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0):     configuration option may not be set correctly.  When the
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0):     ACPI event daemon is available, the NVIDIA X driver will
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0):     try to use it to receive ACPI event notifications.  For
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0):     details, please see the "ConnectToAcpid" and
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0):     "AcpidSocketPath" X configuration options in Appendix B: X
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0):     Config Options in the README.
Jan 15 10:47:10 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0): Setting mode "NULL"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) NVIDIA(0): Disabling shared memory pixmaps
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) NVIDIA(0): Backing store enabled
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (==) NVIDIA(0): Silken mouse enabled
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) NVIDIA(0): DPMS enabled
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Loading sub module "dri2"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) LoadModule: "dri2"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Module "dri2" already built-in
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0): [DRI2] Setup complete
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) NVIDIA(0): [DRI2]   VDPAU driver: nvidia
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension Generic Event Extension
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension SHAPE
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension MIT-SHM
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension XInputExtension
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension XTEST
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension BIG-REQUESTS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension SYNC
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension XKEYBOARD
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension XC-MISC
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension SECURITY
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension XFIXES
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension RENDER
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension RANDR
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension COMPOSITE
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension DAMAGE
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension MIT-SCREEN-SAVER
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension DOUBLE-BUFFER
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension RECORD
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension DPMS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension Present
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension DRI3
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension X-Resource
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension XVideo
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension XVideo-MotionCompensation
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension SELinux
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) SELinux: Disabled on system
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension GLX
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension GLX
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Indirect GLX disabled.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) GLX: Another vendor is already registered for screen 0
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension XFree86-VidModeExtension
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension XFree86-DGA
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension XFree86-DRI
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension DRI2
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension NV-GLX
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Initializing extension NV-CONTROL
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: The XKEYBOARD keymap compiler (xkbcomp) reports:
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86CameraAccessEnable
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86CameraAccessDisable
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86CameraAccessToggle
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86NextElement
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86PreviousElement
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86AutopilotEngageToggle
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86MarkWaypoint
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86Sos
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86NavChart
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86FishingChart
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86SingleRangeRadar
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86DualRangeRadar
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86RadarOverlay
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86TraditionalSonar
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86ClearvuSonar
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86SidevuSonar
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: > Warning:          Could not resolve keysym XF86NavInfo
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2699]: Errors from xkbcomp are not fatal to the X server
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device Power Button (/dev/input/event1)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Power Button: Applying InputClass "libinput keyboard catchall"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) LoadModule: "libinput"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Loading /usr/lib/xorg/modules/input/libinput_drv.so
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Module libinput: vendor="X.Org Foundation"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]:         compiled for 1.21.1.11, module version = 1.4.0
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]:         Module class: X.Org XInput Driver
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]:         ABI class: X.Org XInput driver, version 24.4
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Using input driver 'libinput' for 'Power Button'
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: got fd for /dev/input/event1 13:65 fd 43 paused 0
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Power Button: always reports core events
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "Device" "/dev/input/event1"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event1  - Power Button: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event1  - Power Button: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event1  - Power Button: device removed
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "config_info" "udev:/sys/devices/LNXSYSTM:00/LNXPWRBN:00/input/input1/event1"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) XINPUT: Adding extended input device "Power Button" (type: KEYBOARD, id 6)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_model" "pc105"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_layout" "us"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event1  - Power Button: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event1  - Power Button: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device Video Bus (/dev/input/event2)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Video Bus: Applying InputClass "libinput keyboard catchall"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Using input driver 'libinput' for 'Video Bus'
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: got fd for /dev/input/event2 13:66 fd 46 paused 0
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Video Bus: always reports core events
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "Device" "/dev/input/event2"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event2  - Video Bus: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event2  - Video Bus: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event2  - Video Bus: device removed
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "config_info" "udev:/sys/devices/LNXSYSTM:00/LNXSYBUS:00/PNP0A08:00/device:20/LNXVIDEO:00/input/input2/event2"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) XINPUT: Adding extended input device "Video Bus" (type: KEYBOARD, id 7)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_model" "pc105"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_layout" "us"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event2  - Video Bus: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event2  - Video Bus: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device Power Button (/dev/input/event0)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Power Button: Applying InputClass "libinput keyboard catchall"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Using input driver 'libinput' for 'Power Button'
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: got fd for /dev/input/event0 13:64 fd 47 paused 0
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Power Button: always reports core events
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "Device" "/dev/input/event0"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event0  - Power Button: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event0  - Power Button: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event0  - Power Button: device removed
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "config_info" "udev:/sys/devices/LNXSYSTM:00/LNXSYBUS:00/PNP0C0C:00/input/input0/event0"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) XINPUT: Adding extended input device "Power Button" (type: KEYBOARD, id 8)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_model" "pc105"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_layout" "us"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event0  - Power Button: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event0  - Power Button: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device HDA NVidia HDMI/DP,pcm=3 (/dev/input/event9)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) No input driver specified, ignoring this device.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) This device may have been added with another device file.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device HDA NVidia HDMI/DP,pcm=7 (/dev/input/event10)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) No input driver specified, ignoring this device.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) This device may have been added with another device file.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device HDA NVidia HDMI/DP,pcm=8 (/dev/input/event11)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) No input driver specified, ignoring this device.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) This device may have been added with another device file.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device HDA NVidia HDMI/DP,pcm=9 (/dev/input/event12)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) No input driver specified, ignoring this device.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) This device may have been added with another device file.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device HD-Audio Generic HDMI/DP,pcm=3 (/dev/input/event7)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) No input driver specified, ignoring this device.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) This device may have been added with another device file.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device HD-Audio Generic HDMI/DP,pcm=7 (/dev/input/event8)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) No input driver specified, ignoring this device.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) This device may have been added with another device file.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device Logitech K400 Plus (/dev/input/event4)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Logitech K400 Plus: Applying InputClass "libinput pointer catchall"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Logitech K400 Plus: Applying InputClass "libinput keyboard catchall"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Using input driver 'libinput' for 'Logitech K400 Plus'
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: got fd for /dev/input/event4 13:68 fd 48 paused 0
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Logitech K400 Plus: always reports core events
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "Device" "/dev/input/event4"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event4  - Logitech K400 Plus: is tagged by udev as: Keyboard Mouse
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event4  - Logitech K400 Plus: device is a pointer
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event4  - Logitech K400 Plus: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event4  - Logitech K400 Plus: device removed
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) libinput: Logitech K400 Plus: Step value 0 was provided, libinput Fallback acceleration function is used.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) libinput: Logitech K400 Plus: Step value 0 was provided, libinput Fallback acceleration function is used.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) libinput: Logitech K400 Plus: Step value 0 was provided, libinput Fallback acceleration function is used.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) libinput: Logitech K400 Plus: needs a virtual subdevice
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "config_info" "udev:/sys/devices/pci0000:00/0000:00:08.1/0000:0d:00.3/usb3/3-1/3-1.1/3-1.1.2/3-1.1.2:1.2/0003:046D:C52B.0007/0003:046D:404D.0008/input/input14/event4"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) XINPUT: Adding extended input device "Logitech K400 Plus" (type: MOUSE, id 9)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "AccelerationScheme" "none"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Logitech K400 Plus: (accel) selected scheme none/0
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Logitech K400 Plus: (accel) acceleration factor: 2.000
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Logitech K400 Plus: (accel) acceleration threshold: 4
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event4  - Logitech K400 Plus: is tagged by udev as: Keyboard Mouse
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event4  - Logitech K400 Plus: device is a pointer
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event4  - Logitech K400 Plus: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device Logitech K400 Plus (/dev/input/mouse0)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) No input driver specified, ignoring this device.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) This device may have been added with another device file.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device Yubico YubiKey OTP+FIDO+CCID (/dev/input/event3)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Yubico YubiKey OTP+FIDO+CCID: Applying InputClass "libinput keyboard catchall"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Using input driver 'libinput' for 'Yubico YubiKey OTP+FIDO+CCID'
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: got fd for /dev/input/event3 13:67 fd 49 paused 0
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Yubico YubiKey OTP+FIDO+CCID: always reports core events
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "Device" "/dev/input/event3"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event3  - Yubico YubiKey OTP+FIDO+CCID: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event3  - Yubico YubiKey OTP+FIDO+CCID: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event3  - Yubico YubiKey OTP+FIDO+CCID: device removed
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "config_info" "udev:/sys/devices/pci0000:00/0000:00:08.1/0000:0d:00.3/usb3/3-1/3-1.1/3-1.1.3/3-1.1.3:1.0/0003:1050:0407.0009/input/input13/event3"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) XINPUT: Adding extended input device "Yubico YubiKey OTP+FIDO+CCID" (type: KEYBOARD, id 10)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_model" "pc105"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_layout" "us"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event3  - Yubico YubiKey OTP+FIDO+CCID: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event3  - Yubico YubiKey OTP+FIDO+CCID: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device Asus WMI hotkeys (/dev/input/event6)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Asus WMI hotkeys: Applying InputClass "libinput keyboard catchall"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Using input driver 'libinput' for 'Asus WMI hotkeys'
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: got fd for /dev/input/event6 13:70 fd 50 paused 0
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Asus WMI hotkeys: always reports core events
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "Device" "/dev/input/event6"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event6  - Asus WMI hotkeys: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event6  - Asus WMI hotkeys: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event6  - Asus WMI hotkeys: device removed
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "config_info" "udev:/sys/devices/platform/asus-nb-wmi/input/input16/event6"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) XINPUT: Adding extended input device "Asus WMI hotkeys" (type: KEYBOARD, id 11)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_model" "pc105"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_layout" "us"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event6  - Asus WMI hotkeys: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event6  - Asus WMI hotkeys: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) config/udev: Adding input device Eee PC WMI hotkeys (/dev/input/event5)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Eee PC WMI hotkeys: Applying InputClass "libinput keyboard catchall"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Using input driver 'libinput' for 'Eee PC WMI hotkeys'
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: got fd for /dev/input/event5 13:69 fd 51 paused 0
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Eee PC WMI hotkeys: always reports core events
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "Device" "/dev/input/event5"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event5  - Eee PC WMI hotkeys: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event5  - Eee PC WMI hotkeys: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event5  - Eee PC WMI hotkeys: device removed
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "config_info" "udev:/sys/devices/platform/eeepc-wmi/input/input15/event5"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) XINPUT: Adding extended input device "Eee PC WMI hotkeys" (type: KEYBOARD, id 12)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_model" "pc105"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_layout" "us"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event5  - Eee PC WMI hotkeys: is tagged by udev as: Keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) event5  - Eee PC WMI hotkeys: device is a keyboard
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Logitech K400 Plus: Applying InputClass "libinput pointer catchall"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Logitech K400 Plus: Applying InputClass "libinput keyboard catchall"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) Using input driver 'libinput' for 'Logitech K400 Plus'
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) systemd-logind: returning pre-existing fd for /dev/input/event4 13:68
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Logitech K400 Plus: always reports core events
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "Device" "/dev/input/event4"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) libinput: Logitech K400 Plus: is a virtual subdevice
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) libinput: Logitech K400 Plus: Step value 0 was provided, libinput Fallback acceleration function is used.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) libinput: Logitech K400 Plus: Step value 0 was provided, libinput Fallback acceleration function is used.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) libinput: Logitech K400 Plus: Step value 0 was provided, libinput Fallback acceleration function is used.
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "config_info" "udev:/sys/devices/pci0000:00/0000:00:08.1/0000:0d:00.3/usb3/3-1/3-1.1/3-1.1.2/3-1.1.2:1.2/0003:046D:C52B.0007/0003:046D:404D.0008/input/input14/event4"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (II) XINPUT: Adding extended input device "Logitech K400 Plus" (type: KEYBOARD, id 13)
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_model" "pc105"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (**) Option "xkb_layout" "us"
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2707]: rm: cannot remove '/var/log/prime-supported.log': Permission denied
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2706]: /usr/bin/prime-supported: 35: cannot create /var/log/prime-supported.log: Permission denied
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2739]: Could not find provider with name
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: Internal DisplayPort
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: 2670.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: disconnected
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: Internal TMDS
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: 165.0 MHz maximum pixel clock
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2746]: warning: output  not found; ignoring
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2747]: warning: output  not found; ignoring
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2748]: /etc/gdm3/Xsession: Beginning session setup...
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2764]: localuser:ashwin being added to access control list
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2767]: dbus-update-activation-environment: setting DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2767]: dbus-update-activation-environment: setting DISPLAY=:0
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2767]: dbus-update-activation-environment: setting XAUTHORITY=/run/user/1000/gdm/Xauthority
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2767]: dbus-update-activation-environment: setting XDG_CURRENT_DESKTOP=ubuntu:GNOME
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2771]: /etc/X11/Xsession.d/30x11-common_xresources: line 16: has_option: command not found
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2774]: localuser:ashwin being added to access control list
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2800]: dbus-update-activation-environment: setting GTK_MODULES=gail:atk-bridge
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2809]: dbus-update-activation-environment: setting QT_ACCESSIBILITY=1
Jan 15 10:47:11 ubuntu-server /usr/libexec/gdm-x-session[2811]: /etc/X11/Xsession.d/90x11-common_ssh-agent: line 9: has_option: command not found
Jan 15 10:47:11 ubuntu-server gnome-shell[2900]: Running GNOME Shell (using mutter 46.2) as a X11 window and compositing manager
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: disconnected
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: Internal TMDS
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-0: 165.0 MHz maximum pixel clock
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: disconnected
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: Internal DisplayPort
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-1: 2670.0 MHz maximum pixel clock
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: disconnected
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: Internal TMDS
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-2: 165.0 MHz maximum pixel clock
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: disconnected
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: Internal DisplayPort
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-3: 2670.0 MHz maximum pixel clock
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: disconnected
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: Internal TMDS
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-4: 165.0 MHz maximum pixel clock
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: disconnected
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: Internal DisplayPort
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-5: 2670.0 MHz maximum pixel clock
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: disconnected
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: Internal TMDS
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0): DFP-6: 165.0 MHz maximum pixel clock
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2655]: (--) NVIDIA(GPU-0):
Jan 15 10:47:12 ubuntu-server at-spi-bus-launcher[2838]: dbus-daemon[2838]: Activating service name='org.a11y.atspi.Registry' requested by ':1.1' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[1615]: [system] Activating via systemd: service name='org.freedesktop.ColorManager' unit='colord.service' requested by ':1.47' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server gnome-shell[2900]: Unset XDG_SESSION_ID, getCurrentSessionProxy() called outside a user session. Asking logind directly.
Jan 15 10:47:12 ubuntu-server gnome-shell[2900]: Will monitor session 1
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating service name='org.gnome.Shell.Screencast' requested by ':1.37' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating service name='org.gnome.Shell.CalendarServer' requested by ':1.37' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating via systemd: service name='org.gnome.evolution.dataserver.Sources5' unit='evolution-source-registry.service' requested by ':1.42' (uid=1000 pid=2970 comm="/usr/libexec/gnome-shell-calendar-server" label="unconfined")
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: The XKEYBOARD keymap compiler (xkbcomp) reports:
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86CameraAccessEnable
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86CameraAccessDisable
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86CameraAccessToggle
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86NextElement
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86PreviousElement
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86AutopilotEngageToggle
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86MarkWaypoint
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86Sos
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86NavChart
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86FishingChart
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86SingleRangeRadar
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86DualRangeRadar
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86RadarOverlay
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86TraditionalSonar
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86ClearvuSonar
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86SidevuSonar
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: > Warning:          Could not resolve keysym XF86NavInfo
Jan 15 10:47:12 ubuntu-server /usr/libexec/gdm-x-session[2977]: Errors from xkbcomp are not fatal to the X server
Jan 15 10:47:12 ubuntu-server dbus-daemon[1615]: [system] Activating via systemd: service name='org.freedesktop.PackageKit' unit='packagekit.service' requested by ':1.47' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[1615]: [system] Activating via systemd: service name='org.freedesktop.UPower' unit='upower.service' requested by ':1.47' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating service name='org.gnome.Shell.Notifications' requested by ':1.37' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server gnome-shell[2900]: Gio.UnixInputStream has been moved to a separate platform-specific library. Please update your code to use GioUnix.InputStream instead.
Jan 15 10:47:12 ubuntu-server gnome-shell[2900]: Error looking up permission: GDBus.Error:org.freedesktop.portal.Error.NotFound: No entry for geolocation
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating via systemd: service name='org.gtk.vfs.UDisks2VolumeMonitor' unit='gvfs-udisks2-volume-monitor.service' requested by ':1.37' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating via systemd: service name='org.gnome.evolution.dataserver.Calendar8' unit='evolution-calendar-factory.service' requested by ':1.42' (uid=1000 pid=2970 comm="/usr/libexec/gnome-shell-calendar-server" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating via systemd: service name='org.gtk.vfs.GPhoto2VolumeMonitor' unit='gvfs-gphoto2-volume-monitor.service' requested by ':1.37' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating via systemd: service name='org.gtk.vfs.GoaVolumeMonitor' unit='gvfs-goa-volume-monitor.service' requested by ':1.37' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating via systemd: service name='org.gtk.vfs.AfcVolumeMonitor' unit='gvfs-afc-volume-monitor.service' requested by ':1.37' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating via systemd: service name='org.gtk.vfs.MTPVolumeMonitor' unit='gvfs-mtp-volume-monitor.service' requested by ':1.37' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server polkitd[1628]: Registered Authentication Agent for unix-session:1 (system bus name :1.47 [/usr/bin/gnome-shell], object path /org/freedesktop/PolicyKit1/AuthenticationAgent, locale en_US.UTF-8)
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating via systemd: service name='ca.desrt.dconf' unit='dconf.service' requested by ':1.37' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating via systemd: service name='org.freedesktop.FileManager1' unit='thunar.service' requested by ':1.37' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[2585]: [session uid=1000 pid=2585] Activating via systemd: service name='org.gtk.vfs.Metadata' unit='gvfs-metadata.service' requested by ':1.37' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:12 ubuntu-server dbus-daemon[1615]: [system] Activating via systemd: service name='org.freedesktop.GeoClue2' unit='geoclue.service' requested by ':1.47' (uid=1000 pid=2900 comm="/usr/bin/gnome-shell" label="unconfined")
Jan 15 10:47:13 ubuntu-server gnome-shell[2900]: GFileInfo created without standard::icon
Jan 15 10:47:13 ubuntu-server gnome-shell[2900]: file ../../../gio/gfileinfo.c: line 1765 (g_file_info_get_icon): should not be reached
Jan 15 10:47:13 ubuntu-server gnome-shell[2900]: GFileInfo created without standard::icon
Jan 15 10:47:13 ubuntu-server gnome-shell[2900]: file ../../../gio/gfileinfo.c: line 1765 (g_file_info_get_icon): should not be reached
Jan 15 10:47:13 ubuntu-server gnome-shell[2900]: GFileInfo created without standard::icon
Jan 15 10:47:13 ubuntu-server gnome-shell[2900]: file ../../../gio/gfileinfo.c: line 1765 (g_file_info_get_icon): should not be reached
Jan 15 10:47:13 ubuntu-server gnome-shell[2900]: GFileInfo created without standard::icon
Jan 15 10:47:13 ubuntu-server gnome-shell[2900]: file ../../../gio/gfileinfo.c: line 1765 (g_file_info_get_icon): should not be reached
Jan 15 10:52:11 ubuntu-server gnome-shell[2900]: error: Unable to lock: Lock was blocked by an app
Jan 15 11:03:14 ubuntu-server gnome-shell[2900]: Window manager warning: Buggy client sent a _NET_ACTIVE_WINDOW message with a timestamp of 0 for 0x1800003
ashwin@ubuntu-server:~/.hqplayer$ 

#### ChatGPT:
<time datetime="2025-01-15T20:07:00.510Z" title="1/16/2025, 5:07:00 AM">05:07</time>

From the logs, the key issue is that your X session is coming up on the NVIDIA 4090 (GPU-0) with a “fake” (NULL) display—even though you want to use the AMD GPU’s HDMI output as your display to the TV. You can see many entries about “NVIDIA(0)” and “AllowEmptyInitialConfiguration,” while the AMD GPU (card1) isn’t being used for any actual display output. That explains why the TV stays dark when plugged into the AMD GPU port.

Below are the most likely reasons and how to fix them.

---

## 1. Why is NVIDIA being used instead of AMD?

### a) An xorg.conf or .conf snippet is forcing NVIDIA as primary

Your logs show:

```
(==) Using config file: "/etc/X11/xorg.conf"
...
(**) |-->Device "AMD_GPU"
(**) |-->GPUDevice "NVIDIA_GPU"
...
(**) NVIDIA(0): Depth 24
...
(--) NVIDIA(0): No enabled display devices found; starting anyway because
(--) NVIDIA(0):     AllowEmptyInitialConfiguration is enabled
```

Xorg is finding a configuration that sets up one “Screen0” (the main screen) on the NVIDIA GPU, with the AMD card also mentioned but never actually bound to an output. The “AllowEmptyInitialConfiguration” line means Xorg is happily starting the server on the NVIDIA GPU even if there’s nothing physically connected. Meanwhile, the AMD GPU is basically ignored for the desktop session.

### b) BIOS or firmware is enumerating the 4090 first

On many motherboards, the dedicated PCIe GPU will appear as the primary GPU to the OS unless you force “IGD” or “Onboard GPU” as the primary in the BIOS. But in your logs, we also see references to an explicit xorg.conf that sets the Nvidia GPU as seat0. Even if the AMD GPU is physically wired to your TV, Xorg is ignoring it because the config says to use NVIDIA.

---

## 2. How to force your AMD GPU to become the primary display

You want GDM (GNOME Display Manager) and the GNOME session to appear on the AMD GPU’s output (the TV). There are a few ways:

### Option A: Remove or rename any existing custom `xorg.conf`

If you have a file `/etc/X11/xorg.conf` (or a custom snippet in `/etc/X11/xorg.conf.d/*.conf`) that references “NVIDIA” as the main device, you can move it out of the way:

```bash
sudo mv /etc/X11/xorg.conf /etc/X11/xorg.conf.bak
sudo mv /etc/X11/xorg.conf.d/20-nvidia.conf /etc/X11/xorg.conf.d/20-nvidia.conf.bak   # if it exists
```

Then reboot. Without a custom config, Xorg will auto-detect that your AMD GPU has the connected HDMI. Typically that means your AMD GPU becomes the active display and the TV should light up.

### Option B: Edit `xorg.conf` to make AMD the primary screen

If for some reason you *do* need a custom xorg.conf (for example, for multi-GPU or for special GPU offloading), you can manually configure the AMD GPU as the “Device” for Screen0. For example, in `/etc/X11/xorg.conf` you might see something like:

```ini
Section "Device"
    Identifier "AMD_GPU"
    Driver     "amdgpu"
    BusID      "PCI:13:0:0"
    # ...
EndSection

Section "Device"
    Identifier "NVIDIA_GPU"
    Driver     "nvidia"
    BusID      "PCI:1:0:0"
    # ...
EndSection

Section "Screen"
    Identifier "Screen0"
    Device     "AMD_GPU"     # <--- Make the AMD GPU the primary device for the screen
    Monitor    "Monitor0"
EndSection
```

Then remove `GPUDevice "NVIDIA_GPU"` references from the Screen section or ensure it’s not auto-bound. Also remove `AllowEmptyInitialConfiguration` from the NVIDIA device section so it doesn’t grab screen0.

### Option C: Check your BIOS primary GPU setting

Some motherboards let you pick which GPU is “initial” in the firmware. If the NVIDIA card is enumerated first, it can lead to confusion for Xorg. Usually, though, Xorg on a modern Ubuntu system can handle multiple GPUs. The real culprit is likely that xorg.conf is overriding auto-detection, not just the BIOS.

---

## 3. Verifying that the AMD GPU is now driving the display

1. **After removing or fixing the xorg.conf**, reboot and watch the boot process:
   - If your AMD GPU is truly recognized for output, you’ll see the Ubuntu splash on the TV (assuming the BIOS hands off properly).

2. **Check with xrandr** from an SSH session (or TTY) *after* your desktop has loaded:
   ```bash
   export DISPLAY=:0
   xrandr -q
   ```
   You should see a line like `HDMI-A-0 connected 1920x1080+0+0 ...` or something similar (the exact naming depends on your AMD GPU). If it says “connected,” that means the AMD GPU is in use.

3. **Confirm the NVIDIA GPU is idle**:
   - If you do `nvidia-smi`, you should see no X processes using the 4090, confirming it’s not driving the display.
   - You can still use the 4090 for compute/ML workloads (CUDA, etc.), even if it’s not the active display.

---

## 4. Summary of steps to fix

1. **Rename or remove `/etc/X11/xorg.conf`** (and any relevant `.conf` in `/etc/X11/xorg.conf.d/`) so that Xorg can auto-detect the AMD GPU as the display adapter.
2. **Reboot**.
3. **Check** that the TV now shows the Ubuntu login screen or desktop.
4. If you need a custom config for any reason, **edit** the file so that the AMD GPU is `Device "AMD_GPU"` in the primary `Screen` section, and remove `AllowEmptyInitialConfiguration` from the NVIDIA device.

Once Xorg is free to pick whichever GPU has an active HDMI connection, your AMD GPU output should drive the TV properly. Then the 4090 can remain installed purely for CUDA/ML without interfering with your display.


#### You:
<time datetime="2025-01-15T20:09:36.906Z" title="1/16/2025, 5:09:36 AM">05:09</time>

great i see a desktop now.

#### ChatGPT:
<time datetime="2025-01-15T20:09:41.808Z" title="1/16/2025, 5:09:41 AM">05:09</time>

Awesome! Glad you got the desktop showing up on the TV. If you have any more questions or run into other issues, feel free to let me know. Enjoy your newly working setup!

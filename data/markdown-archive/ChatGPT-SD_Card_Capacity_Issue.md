---
title: SD Card Capacity Issue
source: https://chatgpt.com/c/6789ad9e-2210-8003-93aa-85d11d4260e7
---

# SD Card Capacity Issue

#### You:
<time datetime="2025-01-17T01:08:46.584Z" title="1/17/2025, 10:08:46 AM">10:08</time>

i have an sd card that's 128gb but is showing on my computer at 32gb. how can i troubleshoot

#### ChatGPT:
<time datetime="2025-01-17T01:09:20.688Z" title="1/17/2025, 10:09:20 AM">10:09</time>

Below is a systematic approach to troubleshooting why a 128GB SD card might only appear as 32GB on your computer. Along the way, I'll highlight some key concepts in storage media, partitioning, and file systems—topics that might appeal to your interest in computer hardware and software.

---

## 1. Confirm the SD Card’s Authenticity

**Why:** Some SD cards sold online are counterfeit or mislabeled. They may be physically marked as 128GB, but in reality, the storage is lower (often 8GB, 16GB, or 32GB).

**How to check:**

- **h2testw (Windows):** Writes and reads data across the entire capacity of the card to verify actual storage.
- **F3 (Linux/macOS):** Same principle—verifies the entire storage space.

If these tests fail or show errors after \~32GB, it’s likely the card is fake.

---

## 2. Check for Partition Issues

**Why:** Sometimes the card is partitioned in such a way that only one partition (32GB) is recognized. This can happen after formatting in certain cameras, gaming consoles, or single-board computers (e.g., Raspberry Pi).

**How to check on Windows:**

1. **Disk Management:** Right-click the Windows Start button → “Disk Management.”
2. Look for “unallocated” space on the SD card. If you see a small partition of \~32GB and the rest is unallocated, your OS is reading only that first partition.

**On Linux:**

1. Use `lsblk` or `fdisk -l` to see partitions.
2. If you see multiple partitions or leftover space not assigned to any partition, you can fix it with tools like `parted` or `gparted`.

---

## 3. Reformat the Card to Its Full Capacity

> **Important:** Reformatting erases all data, so back up anything important first.

**On Windows (using Disk Management):**

1. Open **Disk Management**.
2. Locate your SD card in the drive list (be extra sure it’s the correct one).
3. Right-click the partitions on the SD card → **Delete Volume** until it’s all unallocated.
4. Right-click the unallocated space → **New Simple Volume**.
5. Follow the wizard, and when it asks for a file system, choose **exFAT** (recommended for SD cards larger than 32GB).

**Using `diskpart` (command-line) on Windows:**

1. Open **Command Prompt** or **PowerShell** as Administrator.
2. Type `diskpart`.
3. Type `list disk` to identify your SD card.
4. Type `select disk X` (where X is the correct disk number for your SD card—verify carefully).
5. Type `clean` to remove existing partitions.
6. Type `create partition primary`.
7. Type `format fs=exfat quick` (for capacity >32GB).
8. Type `assign` to give the SD card a drive letter.

**On Linux:**

1. Install `gparted` or use `parted` in the terminal.
2. Identify the SD card, typically something like `/dev/sdb`.
3. Remove old partitions and create a new GPT or MBR partition table (GPT is usually recommended for large drives).
4. Format the main partition to **exFAT** (for larger SD cards).

---

## 4. Verify Hardware/Device Compatibility

- **Older devices** (e.g., older cameras, MP3 players, or embedded systems) might only support **FAT32** and read up to 32GB.
- **SDHC vs. SDXC**: Some devices only support SDHC (up to 32GB). For 128GB, you typically need a device that supports SDXC.

---

## 5. Run a Final Capacity Test

After formatting, re-run a tool like **h2testw** or **F3**. This ensures the card is now fully accessible at its expected capacity (128GB). If it still caps out at 32GB or fails during the test, it’s likely counterfeit or physically damaged.

---

## 6. Consider That the Card May Be Defective

- Sometimes genuine cards go bad.
- If repeated attempts to format or partition the card fail, or the card reverts to 32GB after a full format, contact the manufacturer (SanDisk, Samsung, Kingston, etc.) if it’s under warranty.

---

### Key Takeaways

- **Counterfeit vs. Genuine**: Testing with tools like h2testw or F3 is essential to confirm the actual capacity.
- **Partitioning**: Sometimes leftover partitions from other devices can limit recognized space. Deleting all partitions and formatting can fix this.
- **File Systems**: Larger than 32GB typically require **exFAT** (or NTFS, though exFAT is more common for removable flash media).
- **Device Compatibility**: Older devices or firmware may read a 128GB card as 32GB if they only support SDHC/FAT32.

By following these steps—verifying authenticity, checking partitions, reformatting using exFAT, ensuring hardware compatibility, and testing capacity again—you’ll either restore the card to its full 128GB or determine that it’s defective/fake.

---

I hope this helps you troubleshoot effectively. If you’re also curious about broader storage concepts (like how partition tables work, or the difference between MBR and GPT) or if you’re dabbling in embedded systems where SD card partitioning is crucial, let me know, and I can expand on those topics!


#### You:
<time datetime="2025-01-17T01:10:05.675Z" title="1/17/2025, 10:10:05 AM">10:10</time>

Welcome to Ubuntu 24.04.1 LTS (GNU/Linux 6.8.0-51-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

Expanded Security Maintenance for Applications is enabled.

1 update can be applied immediately.
To see these additional updates run: apt list --upgradable

Last login: Wed Jan 15 19:49:49 2025 from 192.168.1.201
ashwin@ubuntu-server:~$ lsblk
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0         7:0    0     4K  1 loop /snap/bare/5
loop1         7:1    0  73.9M  1 loop /snap/core22/1722
loop3         7:3    0 274.8M  1 loop /snap/firefox/5561
loop4         7:4    0 505.1M  1 loop /snap/gnome-42-2204/176
loop5         7:5    0  91.7M  1 loop /snap/gtk-common-themes/1535
loop6         7:6    0  44.3M  1 loop /snap/snapd/23258
loop7         7:7    0  44.4M  1 loop /snap/snapd/23545
loop8         7:8    0 150.6M  1 loop /snap/thunderbird/609
loop9         7:9    0 274.4M  1 loop /snap/firefox/5600
sda           8:0    0   3.6T  0 disk 
└─sda1        8:1    0   3.6T  0 part /media/ashwin/photo
sdb           8:16   0   3.6T  0 disk 
└─sdb1        8:17   0   3.6T  0 part /media/ashwin/video
sdc           8:32   1     0B  0 disk 
sdd           8:48   1  30.6M  0 disk 
nvme1n1     259:0    0   3.6T  0 disk 
└─nvme1n1p1 259:2    0   3.6T  0 part /media/ashwin/music
nvme0n1     259:1    0   1.8T  0 disk 
├─nvme0n1p1 259:3    0   5.8G  0 part /media/ashwin/dev
├─nvme0n1p2 259:4    0     1G  0 part /boot/efi
├─nvme0n1p3 259:5    0   300K  0 part 
└─nvme0n1p4 259:6    0   1.8T  0 part /
ashwin@ubuntu-server:~$ fdisk -l
fdisk: cannot open /dev/loop0: Permission denied
fdisk: cannot open /dev/loop1: Permission denied
fdisk: cannot open /dev/loop3: Permission denied
fdisk: cannot open /dev/loop4: Permission denied
fdisk: cannot open /dev/loop5: Permission denied
fdisk: cannot open /dev/loop6: Permission denied
fdisk: cannot open /dev/loop7: Permission denied
fdisk: cannot open /dev/nvme1n1: Permission denied
fdisk: cannot open /dev/nvme0n1: Permission denied
fdisk: cannot open /dev/sda: Permission denied
fdisk: cannot open /dev/sdb: Permission denied
fdisk: cannot open /dev/loop8: Permission denied
fdisk: cannot open /dev/loop9: Permission denied
fdisk: cannot open /dev/sdd: Permission denied
ashwin@ubuntu-server:~$ sudo fdisk -l
[sudo] password for ashwin: 
Disk /dev/loop0: 4 KiB, 4096 bytes, 8 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/loop1: 73.87 MiB, 77459456 bytes, 151288 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/loop3: 274.84 MiB, 288194560 bytes, 562880 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/loop4: 505.09 MiB, 529625088 bytes, 1034424 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/loop5: 91.69 MiB, 96141312 bytes, 187776 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/loop6: 44.3 MiB, 46448640 bytes, 90720 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/loop7: 44.44 MiB, 46596096 bytes, 91008 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/nvme1n1: 3.64 TiB, 4000787030016 bytes, 7814037168 sectors
Disk model: Samsung SSD 990 PRO 4TB                 
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: 4B346409-E415-4525-BDD0-671292F37DAA

Device         Start        End    Sectors  Size Type
/dev/nvme1n1p1    34 7814035455 7814035422  3.6T Linux filesystem


Disk /dev/nvme0n1: 1.82 TiB, 2000398934016 bytes, 3907029168 sectors
Disk model: Samsung SSD 990 PRO 2TB                 
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: EED3DE8A-ACD3-4541-BA15-9014C007D874

Device            Start        End    Sectors  Size Type
/dev/nvme0n1p1     2048   12113919   12111872  5.8G Linux filesystem
/dev/nvme0n1p2 12115968   14317567    2201600    1G EFI System
/dev/nvme0n1p3 12115264   12115863        600  300K Microsoft basic data
/dev/nvme0n1p4 14317568 3907028991 3892711424  1.8T Linux filesystem

Partition table entries are not in disk order.


Disk /dev/sda: 3.64 TiB, 4000787030016 bytes, 7814037168 sectors
Disk model: CT4000MX500SSD1 
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: gpt
Disk identifier: 4A7798F1-F20F-47E0-9CBE-2F425CDF633D

Device     Start        End    Sectors  Size Type
/dev/sda1     34 7814035455 7814035422  3.6T Linux filesystem

Partition 1 does not start on physical sector boundary.


Disk /dev/sdb: 3.64 TiB, 4000787030016 bytes, 7814037168 sectors
Disk model: CT4000MX500SSD1 
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: gpt
Disk identifier: E5AA20D9-F45E-45D6-9BC6-6D0FA30580ED

Device     Start        End    Sectors  Size Type
/dev/sdb1     34 7814035455 7814035422  3.6T Linux filesystem

Partition 1 does not start on physical sector boundary.


Disk /dev/loop8: 150.59 MiB, 157908992 bytes, 308416 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/loop9: 274.45 MiB, 287776768 bytes, 562064 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/sdd: 30.61 MiB, 32096256 bytes, 62688 sectors
Disk model: Micro SD/M2     
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
ashwin@ubuntu-server:~$ 

#### ChatGPT:
<time datetime="2025-01-17T01:10:24.706Z" title="1/17/2025, 10:10:24 AM">10:10</time>

From the output of `lsblk` and `fdisk -l`, it looks like your SD card (likely **/dev/sdd**) is only being recognized as roughly **30MB**—far below the 128GB you expect. Below are some steps you can take to figure out what’s going on and hopefully fix it.

---

## 1. Verify That **/dev/sdd** Is Indeed the SD Card

- **Physical Check**: If you have multiple USB/SD devices connected, confirm that **sdd** is the correct one by unplugging/re-plugging and re-checking with `dmesg` or `lsblk`.
- **Card Reader**: A flaky or older reader could cause incorrect capacity reporting.

After ensuring **/dev/sdd** is your 128GB card, proceed.

---

## 2. Check dmesg Logs for Errors

Immediately after inserting the SD card, run:

```bash
dmesg | tail -n 30
```

Look for lines mentioning **sdd** or similar. Sometimes the kernel logs will indicate read errors, I/O issues, or unusual partition table warnings.

---

## 3. Consider a Counterfeit or Damaged Card

When an SD card’s actual capacity drastically differs from its labeled capacity (e.g., 128GB labeled, but \~30MB recognized), it can be:

1. **Counterfeit**: The controller was modified to report 128GB, but physically it’s only 32MB or 32GB. Tools like **F3** or **h2testw** can help confirm.
2. **Damaged Controller**: If the internal controller is failing, it might be defaulting to a “safe” minimal capacity.

### How to Test Actual Capacity

- **F3** (Linux/macOS):
  ```bash
  sudo apt-get install f3
  f3probe --destructive /dev/sdd
  ```
  This will attempt to write/read the entire device to see if it’s truly 128GB.
- **h2testw** (Windows): Similar approach, if you have a Windows machine around.

If the test quickly fails or never sees more than \~30MB, the SD card is almost certainly fake or defective.

---

## 4. Wipe and Recreate the Partition Table

If you still suspect a partition or filesystem issue (even though 30MB is suspiciously small), you can try to **completely wipe** the card and rebuild the partition table. (Be absolutely sure you’re selecting the correct device so as not to overwrite another drive!)

### Using `parted`

1. **Install parted** (if not installed):
   ```bash
   sudo apt-get update
   sudo apt-get install parted
   ```
2. **Wipe old partition table**:
   ```bash
   sudo parted /dev/sdd mklabel gpt
   ```
   (GPT is recommended for drives larger than 2TB, but using it on smaller storage is fine too. If there’s a fundamental capacity error, parted might complain here.)
3. **Create a new partition**:
   ```bash
   sudo parted -a optimal /dev/sdd mkpart primary 0% 100%
   ```
4. **Format** (assuming exFAT for 128GB):
   ```bash
   sudo mkfs.exfat /dev/sdd1
   ```
5. **Double-check**:
   ```bash
   sudo parted /dev/sdd print
   lsblk
   ```

If parted or mkfs.exfat fails with size-related errors, that’s another sign the card isn’t truly 128GB.

---

## 5. Try a Different USB Port / Different System

- **Different Port or Reader**: Sometimes USB hubs or older built-in card readers cause capacity misreads.
- **Another PC**: If multiple systems see the same “\~30MB,” that cements it’s the card itself at fault.

---

## 6. Conclusion: Likely Counterfeit or Dead

When a card labeled “128GB” only shows up as \~30MB:

- **Best-Case**: The partition table is corrupt. A wipe/reformat might restore full capacity.
- **Worst-Case**: The SD card is counterfeit or physically damaged. Testing tools (F3/h2testw) are the definitive way to confirm.

If it still reports \~30MB after all these steps, it’s either a counterfeit card or its internal controller is irreparably damaged. In that scenario, the only real fix is to **replace** it.

---

### Quick Reference

1. **Identify** the correct device (`lsblk`, `dmesg`).
2. **Check** logs (`dmesg | tail`).
3. **Test** authenticity (`f3probe`, `h2testw`).
4. **Wipe** partition table (`sudo parted mklabel gpt`) and format (`mkfs.exfat`).
5. **Verify** on another system or card reader.
6. **Replace** if still stuck at 30MB.

If you’re diving deeper into how storage controllers can be “spoofed,” or want to understand the differences between MBR and GPT partition schemes (plus how the OS interprets them), let me know. There’s a lot more behind the scenes in how Linux enumerates block devices, especially if you’re tinkering in hardware or embedded systems!


#### You:
<time datetime="2025-01-17T01:10:58.265Z" title="1/17/2025, 10:10:58 AM">10:10</time>

ashwin@ubuntu-server:~$ dmesg | tail -n 30
dmesg: read kernel buffer failed: Operation not permitted
ashwin@ubuntu-server:~$ sudo dmesg | tail -n 30
[103937.024929] scsi host6: usb-storage 3-1.1.4.2:1.0
[103938.064847] scsi 6:0:0:0: Direct-Access     Generic- SD/MMC           1.00 PQ: 0 ANSI: 6
[103938.066171] scsi 6:0:0:1: Direct-Access     Generic- Micro SD/M2      1.08 PQ: 0 ANSI: 6
[103938.066368] sd 6:0:0:0: Attached scsi generic sg2 type 0
[103938.066496] sd 6:0:0:1: Attached scsi generic sg3 type 0
[103938.067159] sd 6:0:0:0: [sdc] Media removed, stopped polling
[103938.067461] sd 6:0:0:0: [sdc] Attached SCSI removable disk
[103938.397291] sd 6:0:0:1: [sdd] 62688 512-byte logical blocks: (32.1 MB/30.6 MiB)
[103938.399545] sd 6:0:0:1: [sdd] Write Protect is off
[103938.399548] sd 6:0:0:1: [sdd] Mode Sense: 23 00 00 00
[103938.401667] sd 6:0:0:1: [sdd] Write cache: disabled, read cache: disabled, doesn't support DPO or FUA
[103938.415942] sd 6:0:0:1: [sdd] Attached SCSI removable disk
[103943.459612] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103943.459871] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103943.460096] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103947.524872] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103947.525139] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103947.525391] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103947.758515] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103947.758714] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103947.758863] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103948.560838] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103948.561090] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103948.561312] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103949.090907] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103949.091156] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103949.091375] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103967.356651] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103967.356910] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
[103967.357134] [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
ashwin@ubuntu-server:~$ sudo apt-get update
sudo apt-get install parted
Get:1 file:/var/cuda-repo-ubuntu2404-12-6-local  InRelease [1,572 B]
Get:1 file:/var/cuda-repo-ubuntu2404-12-6-local  InRelease [1,572 B]
Hit:2 https://nvidia.github.io/libnvidia-container/stable/deb/amd64  InRelease
Hit:3 https://download.docker.com/linux/ubuntu noble InRelease                                                                                                                                                              
Hit:4 https://deb.nodesource.com/node_22.x nodistro InRelease                                                                                                                                                               
Hit:5 http://repository.netdata.cloud/repos/stable/ubuntu noble/ InRelease                                                                                                                                                  
Err:2 https://nvidia.github.io/libnvidia-container/stable/deb/amd64  InRelease                                                                                                                                              
  The following signatures couldn't be verified because the public key is not available: NO_PUBKEY DDCAE044F796ECB0
Hit:6 https://repo.radeon.com/amdgpu/6.2.4/ubuntu noble InRelease                                                                                                                                                           
Hit:7 https://packages.microsoft.com/ubuntu/24.04/prod noble InRelease                                                                                                                                                      
Get:8 https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64  InRelease [1,581 B]                                                                                                                       
Get:9 https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64  InRelease [1,581 B]                                                                                                                       
Hit:10 https://repo.radeon.com/rocm/apt/6.2.4 noble InRelease                                                                                                                                                               
Hit:11 http://repository.netdata.cloud/repos/repoconfig/ubuntu noble/ InRelease                                                                                                                                             
Get:12 http://security.ubuntu.com/ubuntu noble-security InRelease [126 kB]                                                                                                                       
Get:13 https://pkgs.tailscale.com/stable/ubuntu noble InRelease                                                                                                                      
Get:14 https://esm.ubuntu.com/apps/ubuntu noble-apps-security InRelease [7,547 B]                                                                                                      
Get:15 https://esm.ubuntu.com/apps/ubuntu noble-apps-updates InRelease [7,468 B]                                                                                     
Hit:16 https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu noble InRelease                                                                             
Get:17 http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages [586 kB]                                                        
Get:18 https://esm.ubuntu.com/infra/ubuntu noble-infra-security InRelease [7,462 B]                                                                   
Hit:19 https://ppa.launchpadcontent.net/ubuntuhandbook1/darktable/ubuntu noble InRelease                                                                             
Get:20 https://esm.ubuntu.com/infra/ubuntu noble-infra-updates InRelease [7,461 B]                                                                                   
Hit:21 http://us.archive.ubuntu.com/ubuntu noble InRelease                                                                                                                         
Get:23 https://esm.ubuntu.com/apps/ubuntu noble-apps-security/main i386 Packages [17.0 kB]                                
Get:24 https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64  Packages [1,926 kB]                                              
Get:25 https://esm.ubuntu.com/apps/ubuntu noble-apps-security/main amd64 Packages [26.2 kB]                                                         
Get:26 http://us.archive.ubuntu.com/ubuntu noble-updates InRelease [126 kB]                                                             
Get:27 http://security.ubuntu.com/ubuntu noble-security/main i386 Packages [232 kB]                                                                
Get:28 http://security.ubuntu.com/ubuntu noble-security/main amd64 Components [7,240 B]                                                                       
Get:29 http://security.ubuntu.com/ubuntu noble-security/restricted amd64 Components [212 B]                                                                   
Get:30 http://security.ubuntu.com/ubuntu noble-security/universe i386 Packages [503 kB]                                                   
Get:31 https://ppa.launchpadcontent.net/xtradeb/apps/ubuntu noble InRelease [24.1 kB]                                                                         
Get:32 https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64  Packages [330 kB]                                                 
Get:33 http://security.ubuntu.com/ubuntu noble-security/universe amd64 Packages [800 kB]                                                                       
Get:34 http://security.ubuntu.com/ubuntu noble-security/universe amd64 Components [52.0 kB]                       
Get:35 http://security.ubuntu.com/ubuntu noble-security/multiverse amd64 Components [208 B]                                                      
Get:36 https://ppa.launchpadcontent.net/xtradeb/apps/ubuntu noble/main i386 Packages [9,448 B]                                
Get:37 http://us.archive.ubuntu.com/ubuntu noble-backports InRelease [126 kB]               
Get:38 https://ppa.launchpadcontent.net/xtradeb/apps/ubuntu noble/main amd64 Packages [38.6 kB]
Get:39 http://us.archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages [774 kB]      
Ign:22 https://developer.download.nvidia.com/devtools/repos/ubuntu2404/amd64  InRelease
Get:40 http://us.archive.ubuntu.com/ubuntu noble-updates/main i386 Packages [376 kB]
Get:41 http://us.archive.ubuntu.com/ubuntu noble-updates/main amd64 Components [151 kB]
Get:42 http://us.archive.ubuntu.com/ubuntu noble-updates/restricted amd64 Components [212 B]
Get:43 http://us.archive.ubuntu.com/ubuntu noble-updates/universe amd64 Packages [974 kB]
Get:44 http://us.archive.ubuntu.com/ubuntu noble-updates/universe i386 Packages [597 kB]
Get:45 http://us.archive.ubuntu.com/ubuntu noble-updates/universe amd64 Components [309 kB]
Hit:46 https://developer.download.nvidia.com/devtools/repos/ubuntu2404/amd64  Release 
Get:47 http://us.archive.ubuntu.com/ubuntu noble-updates/multiverse amd64 Components [940 B]
Get:49 http://us.archive.ubuntu.com/ubuntu noble-backports/main amd64 Components [208 B]
Get:50 http://us.archive.ubuntu.com/ubuntu noble-backports/restricted amd64 Components [212 B]
Get:51 http://us.archive.ubuntu.com/ubuntu noble-backports/universe amd64 Components [11.7 kB]
Get:52 http://us.archive.ubuntu.com/ubuntu noble-backports/multiverse amd64 Components [212 B]
Fetched 8,167 kB in 3s (3,156 kB/s)                                      
Reading package lists... Done
W: An error occurred during the signature verification. The repository is not updated and the previous index files will be used. GPG error: https://nvidia.github.io/libnvidia-container/stable/deb/amd64  InRelease: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY DDCAE044F796ECB0
N: Skipping acquire of configured file 'main/binary-i386/Packages' as repository 'https://deb.nodesource.com/node_22.x nodistro InRelease' doesn't support architecture 'i386'
W: https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/InRelease: Key is stored in legacy trusted.gpg keyring (/etc/apt/trusted.gpg), see the DEPRECATION section in apt-key(8) for details.
W: https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/InRelease: Key is stored in legacy trusted.gpg keyring (/etc/apt/trusted.gpg), see the DEPRECATION section in apt-key(8) for details.
W: https://developer.download.nvidia.com/devtools/repos/ubuntu2404/amd64/Release.gpg: Key is stored in legacy trusted.gpg keyring (/etc/apt/trusted.gpg), see the DEPRECATION section in apt-key(8) for details.
W: Failed to fetch https://nvidia.github.io/libnvidia-container/stable/deb/amd64/InRelease  The following signatures couldn't be verified because the public key is not available: NO_PUBKEY DDCAE044F796ECB0
W: Some index files failed to download. They have been ignored, or old ones used instead.
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
parted is already the newest version (3.6-4build1).
parted set to manually installed.
The following package was automatically installed and is no longer required:
  python3-netifaces
Use 'sudo apt autoremove' to remove it.
0 upgraded, 0 newly installed, 0 to remove and 11 not upgraded.
ashwin@ubuntu-server:~$ 

#### ChatGPT:
<time datetime="2025-01-17T01:11:30.802Z" title="1/17/2025, 10:11:30 AM">10:11</time>

From your latest output, two main things stand out:

1. **The system is only detecting your SD card at \~30MB** (sdd reports 62688 blocks × 512 bytes = 32.1 MB/30.6 MiB).
2. **There are unrelated NVIDIA DRM errors** in the logs (about “Failed to grab modeset ownership”), plus a **GPG key warning** regarding an NVIDIA repository.

Let’s address these separately.

---

## Part 1: SD Card Showing 30MB Instead of 128GB

### 1. Confirm It’s Really /dev/sdd

- Physically disconnect/reconnect the SD card reader and re-run:
  ```bash
  lsblk
  dmesg | tail -n 30
  ```
  Make sure `/dev/sdd` consistently appears when you plug in the same card/reader.
- If you have multiple USB or card readers, confirm you’re looking at the correct device.

### 2. Test with Parted (to Wipe Partition Table)

Even though it’s reporting 30MB, you can attempt to remove any corrupt partition info:

```bash
# Be absolutely sure /dev/sdd is your SD card!
sudo parted /dev/sdd mklabel gpt
sudo parted -a optimal /dev/sdd mkpart primary 0% 100%
sudo mkfs.exfat /dev/sdd1
```

- If **parted** complains that the size is out of range (e.g., it sees only 30MB total), then the kernel truly believes it’s only 30MB in hardware terms.
- After you try creating a GPT label and a partition, re-check with:
  ```bash
  sudo parted /dev/sdd print
  lsblk
  ```

### 3. Run an SD Card Authenticity Test

Because the difference (128GB label vs. 30MB detected) is huge, it’s highly likely the card is either:

- **Counterfeit** (controller hacked to report “128GB,” but physically a fraction of that), or
- **Defective** (controller/flash has failed, causing it to default to a minimal capacity).

On Ubuntu, install **f3** to test actual capacity:

```bash
sudo apt-get install f3
# Destructive test (it will overwrite data, so back up anything important first):
sudo f3probe --destructive /dev/sdd
```

- If `f3probe` only sees \~30MB, or it fails around the 30MB mark, that confirms the card’s hardware is not 128GB.

### 4. Try Another Reader or System

- Some old USB card readers can misread larger capacity cards.
- Plug the card into a different PC or a USB 3.0+ card reader.
- If multiple systems still see \~30MB, then it’s definitely the card.

**Bottom line**: If parted/f3 all confirm 30MB, the card is almost certainly **fake or damaged beyond recovery**. At that point, replacement is the only reliable fix.

---

## Part 2: NVIDIA DRM Errors

You have repeated log messages like:

```
[drm:nv_drm_master_set [nvidia_drm]] *ERROR* ... Failed to grab modeset ownership
```

This typically means:

- The NVIDIA DRM driver is trying to take control of the display (or a virtual console), but something else (e.g., the open-source `nouveau` driver, or another display server) has it.
- If you’re running headless or using third-party GPU drivers, this might just be harmless “noise” in the logs.

### Quick Checks

- **Verify you’re using the proprietary NVIDIA driver** (not nouveau).
- **Update or reinstall** your NVIDIA drivers if you have display issues.
- If this is a headless server, you could ignore these unless it’s causing real problems—or you could remove (or blacklist) the conflicting drivers.

---

## Part 3: GPG Key Warning (NVIDIA Repository)

You’re seeing:

```
The following signatures couldn't be verified because the public key is not available: NO_PUBKEY DDCAE044F796ECB0
```

This happens when Ubuntu tries to update from the **NVIDIA** repository, but your system doesn’t have the correct GPG key to verify packages.

### How to Fix

1. Visit [the official NVIDIA instructions](https://nvidia.github.io/libnvidia-container) or [libnvidia-container GitHub page](https://github.com/NVIDIA/libnvidia-container) for updated key details.
2. Typically, you run something like:
   ```bash
   curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
       sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
   ```
3. Then update the corresponding `.list` file in `/etc/apt/sources.list.d/` so it references that keyring file, for example:
   ```
   deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/deb/amd64 /
   ```
4. Run:
   ```bash
   sudo apt-get update
   ```
   again and the GPG error should go away.

Or, if you no longer need that NVIDIA container repo, just **remove** or **comment out** that repository from `/etc/apt/sources.list.d/...`.

---

## Summary and Next Steps

1. **SD Card**:
   - Try wiping with `parted`/`mkfs.exfat`.
   - If it still shows up as 30MB, do an **F3** test to confirm it’s not genuine.
   - Check with another card reader or machine. If it’s consistently 30MB, time to replace.

2. **NVIDIA DRM**:
   - Likely harmless if you’re not actively using the GPU for display.
   - Consider updating drivers or disabling conflicting drivers if it’s causing issues.

3. **NVIDIA Repo GPG Key**:
   - Either add the missing GPG key to your system or remove that repo if it’s not needed.

If you have more questions on how block devices are recognized in Linux, the difference between MBR/GPT partition tables, or how GPU drivers interact with DRM in a headless setup, feel free to ask!


#### You:
<time datetime="2025-01-17T01:12:25.245Z" title="1/17/2025, 10:12:25 AM">10:12</time>

ashwin@ubuntu-server:~$ lsblk
dmesg | tail -n 30
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0         7:0    0     4K  1 loop /snap/bare/5
loop1         7:1    0  73.9M  1 loop /snap/core22/1722
loop3         7:3    0 274.8M  1 loop /snap/firefox/5561
loop4         7:4    0 505.1M  1 loop /snap/gnome-42-2204/176
loop5         7:5    0  91.7M  1 loop /snap/gtk-common-themes/1535
loop6         7:6    0  44.3M  1 loop /snap/snapd/23258
loop7         7:7    0  44.4M  1 loop /snap/snapd/23545
loop8         7:8    0 150.6M  1 loop /snap/thunderbird/609
loop9         7:9    0 274.4M  1 loop /snap/firefox/5600
sda           8:0    0   3.6T  0 disk 
└─sda1        8:1    0   3.6T  0 part /media/ashwin/photo
sdb           8:16   0   3.6T  0 disk 
└─sdb1        8:17   0   3.6T  0 part /media/ashwin/video
sdc           8:32   1     0B  0 disk 
sdd           8:48   1  30.6M  0 disk 
nvme1n1     259:0    0   3.6T  0 disk 
└─nvme1n1p1 259:2    0   3.6T  0 part /media/ashwin/music
nvme0n1     259:1    0   1.8T  0 disk 
├─nvme0n1p1 259:3    0   5.8G  0 part /media/ashwin/dev
├─nvme0n1p2 259:4    0     1G  0 part /boot/efi
├─nvme0n1p3 259:5    0   300K  0 part 
└─nvme0n1p4 259:6    0   1.8T  0 part /
dmesg: read kernel buffer failed: Operation not permitted
ashwin@ubuntu-server:~$ dmesg | tail -n 30
dmesg: read kernel buffer failed: Operation not permitted
ashwin@ubuntu-server:~$ lsblk
dmesg | tail -n 30
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0         7:0    0     4K  1 loop /snap/bare/5
loop1         7:1    0  73.9M  1 loop /snap/core22/1722
loop3         7:3    0 274.8M  1 loop /snap/firefox/5561
loop4         7:4    0 505.1M  1 loop /snap/gnome-42-2204/176
loop5         7:5    0  91.7M  1 loop /snap/gtk-common-themes/1535
loop6         7:6    0  44.3M  1 loop /snap/snapd/23258
loop7         7:7    0  44.4M  1 loop /snap/snapd/23545
loop8         7:8    0 150.6M  1 loop /snap/thunderbird/609
loop9         7:9    0 274.4M  1 loop /snap/firefox/5600
sda           8:0    0   3.6T  0 disk 
└─sda1        8:1    0   3.6T  0 part /media/ashwin/photo
sdb           8:16   0   3.6T  0 disk 
└─sdb1        8:17   0   3.6T  0 part /media/ashwin/video
nvme1n1     259:0    0   3.6T  0 disk 
└─nvme1n1p1 259:2    0   3.6T  0 part /media/ashwin/music
nvme0n1     259:1    0   1.8T  0 disk 
├─nvme0n1p1 259:3    0   5.8G  0 part /media/ashwin/dev
├─nvme0n1p2 259:4    0     1G  0 part /boot/efi
├─nvme0n1p3 259:5    0   300K  0 part 
└─nvme0n1p4 259:6    0   1.8T  0 part /
dmesg: read kernel buffer failed: Operation not permitted
ashwin@ubuntu-server:~$ lsblk
dmesg | tail -n 30
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0         7:0    0     4K  1 loop /snap/bare/5
loop1         7:1    0  73.9M  1 loop /snap/core22/1722
loop3         7:3    0 274.8M  1 loop /snap/firefox/5561
loop4         7:4    0 505.1M  1 loop /snap/gnome-42-2204/176
loop5         7:5    0  91.7M  1 loop /snap/gtk-common-themes/1535
loop6         7:6    0  44.3M  1 loop /snap/snapd/23258
loop7         7:7    0  44.4M  1 loop /snap/snapd/23545
loop8         7:8    0 150.6M  1 loop /snap/thunderbird/609
loop9         7:9    0 274.4M  1 loop /snap/firefox/5600
sda           8:0    0   3.6T  0 disk 
└─sda1        8:1    0   3.6T  0 part /media/ashwin/photo
sdb           8:16   0   3.6T  0 disk 
└─sdb1        8:17   0   3.6T  0 part /media/ashwin/video
sdc           8:32   1     0B  0 disk 
sdd           8:48   1  30.6M  0 disk 
nvme1n1     259:0    0   3.6T  0 disk 
└─nvme1n1p1 259:2    0   3.6T  0 part /media/ashwin/music
nvme0n1     259:1    0   1.8T  0 disk 
├─nvme0n1p1 259:3    0   5.8G  0 part /media/ashwin/dev
├─nvme0n1p2 259:4    0     1G  0 part /boot/efi
├─nvme0n1p3 259:5    0   300K  0 part 
└─nvme0n1p4 259:6    0   1.8T  0 part /
dmesg: read kernel buffer failed: Operation not permitted
ashwin@ubuntu-server:~$ 

#### ChatGPT:
<time datetime="2025-01-17T01:12:48.861Z" title="1/17/2025, 10:12:48 AM">10:12</time>

It looks like you’re running into two main issues here:

1. **Your SD card is only showing 30.6 MB** instead of the expected 128 GB.
2. **You’re getting “Operation not permitted”** whenever you try to read the kernel ring buffer using `dmesg` as a non-root user.

Below are some explanations and troubleshooting steps for both.

---

## 1. SD Card Shows as 30.6 MB

From your `lsblk` output:

```
sdd           8:48   1  30.6M  0 disk
```

That drive is only reporting around 30 MB. If you’re certain this is supposed to be a 128 GB SD card, you’re most likely dealing with:

- **A counterfeit card** (unfortunately common online).
- **A physically damaged card** whose controller now only reports a small capacity.
- **Corrupted partition info** (although partition corruption alone rarely drops capacity to 30 MB—it’s usually a sign of a broken or fake card).

### Steps to Verify / Attempt Recovery

1. **Try a Different Reader or Machine**
   - Sometimes older or faulty USB SD readers misreport capacity.
   - If multiple systems also see only 30 MB, that points to a hardware/controller issue with the card.

2. **Wipe the Partition Table** (if recognized at all)
   ```bash
   sudo parted /dev/sdd mklabel gpt
   sudo parted -a optimal /dev/sdd mkpart primary 0% 100%
   sudo mkfs.exfat /dev/sdd1
   ```
   - If parted complains about out-of-range sizes, or it refuses to create partitions beyond 30 MB, that means the OS genuinely sees only 30 MB of storage.

3. **Use F3 or h2testw to Confirm Real Capacity**
   - On Ubuntu:
     ```bash
     sudo apt-get install f3
     sudo f3probe --destructive /dev/sdd
     ```
     This will write and read data across the reported capacity. If it’s truly limited to 30 MB, the test will fail (or never find more than \~30 MB).

4. **Replace the Card If All Else Fails**
   - If `f3probe` shows only 30 MB, and parted can’t repartition the card to 128 GB, it’s most likely irreparably defective or fake.

---

## 2. “Operation not permitted” When Running `dmesg`

On modern Ubuntu systems, unprivileged users often cannot read the raw kernel ring buffer (`dmesg`) by default. Instead, you get:

```
dmesg: read kernel buffer failed: Operation not permitted
```

This is a security measure to prevent non-privileged processes from reading sensitive kernel messages.

### How to Work Around This

1. **Run dmesg as root**:
   ```bash
   sudo dmesg | tail -n 30
   ```
   That should work without the “Operation not permitted” error.

2. **Use journalctl** (on most modern Ubuntu systems with systemd):
   ```bash
   sudo journalctl -k -n 30
   ```
   This shows the last 30 lines of the kernel messages. Again, you’ll need sudo to see them.

If you need non-sudo access to dmesg, you can adjust system settings (e.g., `/proc/sys/kernel/dmesg_restrict`), but that is generally not recommended unless you’re sure about the security implications.

---

## Summary

- **SD Card**: Your OS is only detecting 30 MB, which strongly indicates a counterfeit or broken SD card. Try repartitioning with parted and test with `f3probe`. If it consistently fails to show more than 30 MB, the card is unusable.
- **dmesg Permission**: Use `sudo dmesg` or `journalctl -k` if you need to see kernel logs. The “Operation not permitted” is normal for non-root users on Ubuntu.

Hopefully, these steps clarify both issues. Feel free to ask if you have any follow-up questions on partitioning, SD card authenticity testing, or adjusting system permissions for kernel logs.


#### You:
<time datetime="2025-01-17T01:13:29.714Z" title="1/17/2025, 10:13:29 AM">10:13</time>

ashwin@ubuntu-server:~$ lsblk
dmesg | tail -n 30
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0         7:0    0     4K  1 loop /snap/bare/5
loop1         7:1    0  73.9M  1 loop /snap/core22/1722
loop3         7:3    0 274.8M  1 loop /snap/firefox/5561
loop4         7:4    0 505.1M  1 loop /snap/gnome-42-2204/176
loop5         7:5    0  91.7M  1 loop /snap/gtk-common-themes/1535
loop6         7:6    0  44.3M  1 loop /snap/snapd/23258
loop7         7:7    0  44.4M  1 loop /snap/snapd/23545
loop8         7:8    0 150.6M  1 loop /snap/thunderbird/609
loop9         7:9    0 274.4M  1 loop /snap/firefox/5600
sda           8:0    0   3.6T  0 disk 
└─sda1        8:1    0   3.6T  0 part /media/ashwin/photo
sdb           8:16   0   3.6T  0 disk 
└─sdb1        8:17   0   3.6T  0 part /media/ashwin/video
sdc           8:32   1     0B  0 disk 
sdd           8:48   1  30.6M  0 disk 
nvme1n1     259:0    0   3.6T  0 disk 
└─nvme1n1p1 259:2    0   3.6T  0 part /media/ashwin/music
nvme0n1     259:1    0   1.8T  0 disk 
├─nvme0n1p1 259:3    0   5.8G  0 part /media/ashwin/dev
├─nvme0n1p2 259:4    0     1G  0 part /boot/efi
├─nvme0n1p3 259:5    0   300K  0 part 
└─nvme0n1p4 259:6    0   1.8T  0 part /
dmesg: read kernel buffer failed: Operation not permitted
ashwin@ubuntu-server:~$ dmesg | tail -n 30
dmesg: read kernel buffer failed: Operation not permitted
ashwin@ubuntu-server:~$ lsblk
dmesg | tail -n 30
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0         7:0    0     4K  1 loop /snap/bare/5
loop1         7:1    0  73.9M  1 loop /snap/core22/1722
loop3         7:3    0 274.8M  1 loop /snap/firefox/5561
loop4         7:4    0 505.1M  1 loop /snap/gnome-42-2204/176
loop5         7:5    0  91.7M  1 loop /snap/gtk-common-themes/1535
loop6         7:6    0  44.3M  1 loop /snap/snapd/23258
loop7         7:7    0  44.4M  1 loop /snap/snapd/23545
loop8         7:8    0 150.6M  1 loop /snap/thunderbird/609
loop9         7:9    0 274.4M  1 loop /snap/firefox/5600
sda           8:0    0   3.6T  0 disk 
└─sda1        8:1    0   3.6T  0 part /media/ashwin/photo
sdb           8:16   0   3.6T  0 disk 
└─sdb1        8:17   0   3.6T  0 part /media/ashwin/video
nvme1n1     259:0    0   3.6T  0 disk 
└─nvme1n1p1 259:2    0   3.6T  0 part /media/ashwin/music
nvme0n1     259:1    0   1.8T  0 disk 
├─nvme0n1p1 259:3    0   5.8G  0 part /media/ashwin/dev
├─nvme0n1p2 259:4    0     1G  0 part /boot/efi
├─nvme0n1p3 259:5    0   300K  0 part 
└─nvme0n1p4 259:6    0   1.8T  0 part /
dmesg: read kernel buffer failed: Operation not permitted
ashwin@ubuntu-server:~$ lsblk
dmesg | tail -n 30
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0         7:0    0     4K  1 loop /snap/bare/5
loop1         7:1    0  73.9M  1 loop /snap/core22/1722
loop3         7:3    0 274.8M  1 loop /snap/firefox/5561
loop4         7:4    0 505.1M  1 loop /snap/gnome-42-2204/176
loop5         7:5    0  91.7M  1 loop /snap/gtk-common-themes/1535
loop6         7:6    0  44.3M  1 loop /snap/snapd/23258
loop7         7:7    0  44.4M  1 loop /snap/snapd/23545
loop8         7:8    0 150.6M  1 loop /snap/thunderbird/609
loop9         7:9    0 274.4M  1 loop /snap/firefox/5600
sda           8:0    0   3.6T  0 disk 
└─sda1        8:1    0   3.6T  0 part /media/ashwin/photo
sdb           8:16   0   3.6T  0 disk 
└─sdb1        8:17   0   3.6T  0 part /media/ashwin/video
sdc           8:32   1     0B  0 disk 
sdd           8:48   1  30.6M  0 disk 
nvme1n1     259:0    0   3.6T  0 disk 
└─nvme1n1p1 259:2    0   3.6T  0 part /media/ashwin/music
nvme0n1     259:1    0   1.8T  0 disk 
├─nvme0n1p1 259:3    0   5.8G  0 part /media/ashwin/dev
├─nvme0n1p2 259:4    0     1G  0 part /boot/efi
├─nvme0n1p3 259:5    0   300K  0 part 
└─nvme0n1p4 259:6    0   1.8T  0 part /
dmesg: read kernel buffer failed: Operation not permitted
ashwin@ubuntu-server:~$ sudo parted /dev/sdd mklabel gpt
sudo parted -a optimal /dev/sdd mkpart primary 0% 100%
sudo mkfs.exfat /dev/sdd1
Information: You may need to update /etc/fstab.

Error: /dev/sdd: unrecognised disk label                                  
sudo: mkfs.exfat: command not found                                       
ashwin@ubuntu-server:~$ sudo apt-get install f3
sudo f3probe --destructive /dev/sdd
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following package was automatically installed and is no longer required:
  python3-netifaces
Use 'sudo apt autoremove' to remove it.
The following NEW packages will be installed:
  f3
0 upgraded, 1 newly installed, 0 to remove and 11 not upgraded.
Need to get 51.4 kB of archives.
After this operation, 187 kB of additional disk space will be used.
Get:1 http://us.archive.ubuntu.com/ubuntu noble/universe amd64 f3 amd64 8.0-2build2 [51.4 kB]
Fetched 51.4 kB in 1s (75.6 kB/s)
Selecting previously unselected package f3.
(Reading database ... 311371 files and directories currently installed.)
Preparing to unpack .../f3_8.0-2build2_amd64.deb ...
Unpacking f3 (8.0-2build2) ...
Setting up f3 (8.0-2build2) ...
Processing triggers for man-db (2.12.0-4build2) ...
F3 probe 8.0
Copyright (C) 2010 Digirati Internet LTDA.
This is free software; see the source for copying conditions.

WARNING: Probing normally takes from a few seconds to 15 minutes, but
         it can take longer. Please be patient.

Bad news: The device `/dev/sdd' is damaged

Device geometry:
                 *Usable* size: 0.00 Byte (0 blocks)
                Announced size: 30.61 MB (62688 blocks)
                        Module: 32.00 MB (2^25 Bytes)
        Approximate cache size: 0.00 Byte (0 blocks), need-reset=no
           Physical block size: 512.00 Byte (2^9 Bytes)

Probe time: 253.5ms
ashwin@ubuntu-server:~$ sudo journalctl -k -n 30
Jan 16 17:01:30 ubuntu-server kernel: [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
Jan 16 17:01:30 ubuntu-server kernel: [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
Jan 16 17:01:30 ubuntu-server kernel: [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
Jan 16 17:01:30 ubuntu-server kernel: [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
Jan 16 17:01:30 ubuntu-server kernel: [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
Jan 16 17:01:48 ubuntu-server kernel: [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
Jan 16 17:01:48 ubuntu-server kernel: [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
Jan 16 17:01:48 ubuntu-server kernel: [drm:nv_drm_master_set [nvidia_drm]] *ERROR* [nvidia-drm] [GPU ID 0x00000100] Failed to grab modeset ownership
Jan 16 17:11:46 ubuntu-server kernel: usb 3-1.1.4.2: USB disconnect, device number 12
Jan 16 17:11:46 ubuntu-server kernel: sd 6:0:0:1: [sdd] Test Unit Ready failed: Result: hostbyte=DID_NO_CONNECT driverbyte=DRIVER_OK
Jan 16 17:11:46 ubuntu-server kernel: sdd: detected capacity change from 62688 to 0
Jan 16 17:12:09 ubuntu-server kernel: usb 3-1.1.4.2: new high-speed USB device number 13 using xhci_hcd
Jan 16 17:12:09 ubuntu-server kernel: usb 3-1.1.4.2: New USB device found, idVendor=058f, idProduct=8468, bcdDevice= 1.00
Jan 16 17:12:09 ubuntu-server kernel: usb 3-1.1.4.2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
Jan 16 17:12:09 ubuntu-server kernel: usb 3-1.1.4.2: Product: Mass Storage Device
Jan 16 17:12:09 ubuntu-server kernel: usb 3-1.1.4.2: Manufacturer: Generic
Jan 16 17:12:09 ubuntu-server kernel: usb 3-1.1.4.2: SerialNumber: 158F84688461
Jan 16 17:12:09 ubuntu-server kernel: usb-storage 3-1.1.4.2:1.0: USB Mass Storage device detected
Jan 16 17:12:09 ubuntu-server kernel: scsi host6: usb-storage 3-1.1.4.2:1.0
Jan 16 17:12:10 ubuntu-server kernel: scsi 6:0:0:0: Direct-Access     Generic- SD/MMC           1.00 PQ: 0 ANSI: 6
Jan 16 17:12:10 ubuntu-server kernel: scsi 6:0:0:1: Direct-Access     Generic- Micro SD/M2      1.08 PQ: 0 ANSI: 6
Jan 16 17:12:10 ubuntu-server kernel: sd 6:0:0:0: Attached scsi generic sg2 type 0
Jan 16 17:12:10 ubuntu-server kernel: sd 6:0:0:1: Attached scsi generic sg3 type 0
Jan 16 17:12:10 ubuntu-server kernel: sd 6:0:0:0: [sdc] Media removed, stopped polling
Jan 16 17:12:10 ubuntu-server kernel: sd 6:0:0:0: [sdc] Attached SCSI removable disk
Jan 16 17:12:10 ubuntu-server kernel: sd 6:0:0:1: [sdd] 62688 512-byte logical blocks: (32.1 MB/30.6 MiB)
Jan 16 17:12:10 ubuntu-server kernel: sd 6:0:0:1: [sdd] Write Protect is off
Jan 16 17:12:10 ubuntu-server kernel: sd 6:0:0:1: [sdd] Mode Sense: 23 00 00 00
Jan 16 17:12:10 ubuntu-server kernel: sd 6:0:0:1: [sdd] Write cache: disabled, read cache: disabled, doesn't support DPO or FUA
Jan 16 17:12:10 ubuntu-server kernel: sd 6:0:0:1: [sdd] Attached SCSI removable disk
ashwin@ubuntu-server:~$ 

#### ChatGPT:
<time datetime="2025-01-17T01:13:53.107Z" title="1/17/2025, 10:13:53 AM">10:13</time>

Based on your latest output, here’s what we can conclude:

1. **Your SD card is irreparably damaged or counterfeit.**
   - The `f3probe` tool reports:
     ```bash
     Bad news: The device `/dev/sdd' is damaged
     Device geometry:
       *Usable* size: 0.00 Byte (0 blocks)
       Announced size: 30.61 MB (62688 blocks)
     ```
     This means the kernel can only see (and F3 can only probe) around 30 MB—far from the 128 GB you expected.

2. **Parted is unable to create a valid partition table** because the underlying device geometry itself is invalid or severely broken:
   ```bash
   Error: /dev/sdd: unrecognised disk label
   ```
   Even if you force mklabel gpt, parted cannot fix a hardware-level issue.

3. **mkfs.exfat is missing** on your system.

   - Even if the card were working, you’d need to install exFAT utilities:
     ```bash
     sudo apt-get install exfatprogs
     ```
     (In older Ubuntu versions, the package was called `exfat-utils`).

   However, given the F3 results, you won’t be able to format it to 128 GB anyway.

4. **Likely counterfeit or physically failing**:
   - A **counterfeit** SD card might show a “fake” capacity label (128 GB), but in reality it’s only 30 MB–32 MB.
   - A genuine card with a **failing controller** can also appear with a drastically reduced size.

5. **NVIDIA DRM messages** are unrelated to the SD card issue. They’re a separate quirk, often seen if the proprietary NVIDIA driver can’t take over the display (headless or conflicting driver scenario). Unless you’re experiencing GPU issues, they’re mostly harmless logs.

---

## What to Do Next

- **Test on another system or with another USB card reader** to rule out a quirky card reader.
- **Return or replace** the card. If it’s under warranty or recently purchased, contact the seller/manufacturer.
- **If it’s counterfeit**, there’s unfortunately no fix. You’ll need to get a legitimate 128 GB card from a reputable source.

Given all the evidence from `f3probe`, the system genuinely sees only 30 MB of flash. No amount of reformatting or partition-table changes will restore it to 128 GB. Your best bet is to replace the card.

---
title: Ubuntu Server Backup Guide
source: https://chatgpt.com/c/678d54b8-5fc8-8003-8a18-53d7ce636c32
---

# Ubuntu Server Backup Guide

#### You:
<time datetime="2025-01-19T19:38:32.771Z" title="1/20/2025, 4:38:32 AM">04:38</time>

i have a ubuntu server. how should I back it up? I use it mainly for development

#### ChatGPT:
<time datetime="2025-01-19T19:39:09.406Z" title="1/20/2025, 4:39:09 AM">04:39</time>

Below is an overview of practical approaches to backing up a Ubuntu development server, along with thoughts on tools, strategies, and considerations to ensure a reliable and restorable setup.

---

## 1. Identify What to Back Up

1. **User Data and Code**
   - Your home directory (`/home/username`), where personal files and source code typically live.
   - Development project directories (e.g., if you store them under `/srv`, `/opt`, or a specific path).
   - Git repositories (though these can also be mirrored to platforms like GitHub, GitLab, etc.).

2. **System Configuration**
   - Critical config files in `/etc` (e.g., Nginx/Apache configs, database configs, SSH settings).
   - Environment configuration files for languages and tools (e.g., `/etc/profile.d/`, or environment variable files).
   - Package lists to reproduce your environment quickly. On Ubuntu, you can export your package list with:
     ```bash
     dpkg --get-selections > ~/package-list.txt
     ```
     and restore with:
     ```bash
     sudo dpkg --set-selections < package-list.txt
     sudo apt-get dselect-upgrade
     ```

3. **Databases** (if applicable)
   - MySQL/PostgreSQL dumps, especially if you have local databases used for development or testing.
   - For large or frequently changing databases, schedule regular backups with tools like `mysqldump` or `pg_dump`.

---

## 2. Backup Approaches & Tools

There are several ways to back up a Ubuntu system. You can pick one (or combine them) based on your development workflow, storage availability, and desired ease of restore.

### A. **File-Based Backups with `tar` or `rsync`**

- **Tar Archives**
  - Create compressed archives of important directories.
  - Example:
    ```bash
    tar -cvpzf backup-$(date +%F).tar.gz \
      --exclude=/proc \
      --exclude=/tmp \
      --exclude=/mnt \
      --exclude=/dev \
      --exclude=/sys \
      --exclude=/run \
      /  # or specific dirs like /home, /etc
    ```
  - Good for one-off backups, simple to restore. However, large, full archives can be time- and space-consuming.

- **Rsync**
  - Incremental syncs, can mirror directories to external storage, another server, or a local mount point:
    ```bash
    rsync -aAXH /source/path /backup/destination
    ```
  - Well-suited for scripts run via cron or systemd timers to automate daily/weekly backups.

### B. **Snapshot-Based Tools (LVM, Btrfs, ZFS)**

- If your Ubuntu server uses **LVM** or **ZFS** for the filesystem, you can take point-in-time snapshots:
  - **ZFS** allows quick snapshots and incremental sends (`zfs send` / `zfs receive`).
  - **Btrfs** supports subvolume snapshots and incremental backups.
  - **LVM** snapshots can be leveraged for consistent backups of live systems.
- Snapshots are fast to create and revert from, but you need to plan partitioning/file system layout.

### C. **Versioned Backup Utilities**

- **BorgBackup**
  - Deduplicating, encrypted, and incremental. Great for efficient remote backups.
- **Restic**
  - Similar advantages to Borg (encryption, deduplication) and can store data in many backends (AWS S3, Backblaze B2, etc.).
- **Duplicity**
  - Creates encrypted incremental backups; works well with a variety of cloud services.

These tools are well-suited for developers as they allow versioned backups (you can restore specific snapshots in time) and integrate easily with continuous integration or daily scripts.

### D. **Disk/VM Snapshots (Cloud or Virtual Environment)**

- If your Ubuntu server is running in a virtual machine or cloud environment (e.g., AWS EC2, DigitalOcean Droplet, VMware, VirtualBox), you can often leverage built-in snapshot capabilities:
  - **AWS**: Create EBS snapshots regularly.
  - **DigitalOcean**: Droplet snapshots or auto backups.
  - **VMware/VirtualBox**: VM snapshots for full-state backups.
- Snapshots here can be a quick “entire-server” safety net but may be slower to restore if you only need a single file.

---

## 3. Automating the Backup Process

### Use Cron or Systemd Timers

- Schedule backups (daily, weekly) so you don’t have to remember. For example, a cron job using `rsync` to external storage:
  ```bash
  crontab -e
  # Every day at 2 AM
  0 2 * * * /usr/bin/rsync -aAX /home /etc /var/www /backup/$(date +\%F)
  ```
- Combine versioned backups with housekeeping scripts (removing older backups periodically to manage disk space).

### Testing Restores

- A backup is only as good as your restore process. Practice restoring (whether from a tar archive, a restic snapshot, or a VM snapshot) to a test environment to confirm you can fully recover.

---

## 4. Consider Secure, Off-Site Storage

- **Why Off-Site?**
  - If your development server is compromised or physically damaged, local backups could be affected. Using a separate location or a cloud-based bucket (e.g., AWS S3, Backblaze, Azure Blob) adds resilience.
- **Encryption**
  - For sensitive data (e.g., code bases, configuration files with API keys), always encrypt backups. Tools like Borg, Restic, and Duplicity support encryption natively.
- **Cloud Buckets**
  - Borg + rclone, or Restic with S3, is a popular combination to push backups off-site in an automated fashion.

---

## 5. Additional Tips for Development Environments

1. **Leverage Git**
   - Storing your code in remote Git repositories (GitHub, GitLab, Bitbucket, etc.) is a form of version control and backup in itself.
   - Keep secrets (API keys, credentials) out of Git or store them encrypted.

2. **Docker/Container Images**
   - If your environment uses containers, back up:
     - Docker volumes containing persistent data
     - Docker Compose or Kubernetes configurations
   - Rebuilding your environment from Dockerfiles or Compose files is often faster than restoring from a full system backup.

3. **Infrastructure as Code**
   - Tools like Ansible, Terraform, or Packer can define your server setup. This makes re-provisioning a server straightforward, so your backups only need to focus on data rather than the entire OS.

---

## Sample Simple Backup Workflow

Below is a sample workflow that combines a few best practices for a development-focused Ubuntu server:

1. **Version Control Your Code**
   - Make sure all critical code is pushed to a remote repository.

2. **Daily Incremental Backup** (using Borg or Restic)
   - Create a script (`backup.sh`) that runs:
     ```bash
     #!/bin/bash
     # Example with Restic
     export RESTIC_REPOSITORY="s3:https://s3.your-cloud.com/your-bucket"
     export RESTIC_PASSWORD="your-strong-password"

     restic backup /home/youruser /etc /var/lib/mysql --exclude-file=/path/to/excludes.txt
     restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
     ```
   - Schedule it via cron (`crontab -e`) to run nightly.

3. **Off-Site Storage**
   - Using a cloud provider or a second server to store backups.

4. **Regular Restore Tests**
   - Spin up a local VM or a test directory to confirm you can restore from your backups:
     ```bash
     restic restore latest --target /restore/test
     ```

By combining these steps, you’ll have a robust setup for safeguarding your work, system configs, and data.

---

## Conclusion

For a development-focused Ubuntu server, you should:

1. Identify your critical directories (code, configs, databases).
2. Use an automated, versioned backup tool (e.g., Restic, Borg, Duplicity) or reliable file-sync tool (e.g., rsync) for daily or weekly backups.
3. Store backups off-site (encrypted) to protect against physical or security incidents.
4. Include environment replication steps (e.g., package lists, Dockerfiles) so you can quickly spin up a fresh server in case of disaster.
5. Test your restore process regularly.

This approach ensures your development setup, including all your projects and configurations, is safe and can be restored quickly, letting you focus on coding rather than disaster recovery.

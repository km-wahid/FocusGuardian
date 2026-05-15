# FocusGuardian - macOS Website Blocker

A production-ready, local website blocker for macOS that runs in the background and redirects blocked websites to a motivational reminder page.

## 🎯 Features

- **System-wide blocking** across all browsers
- **Local HTTP server** serving motivational quotes and Quranic reminders
- **Background daemon** that survives terminal closure
- **LaunchAgent integration** for automatic startup on login
- **Safe hosts file modification** with automatic backups
- **Easy CLI management** for enabling/disabling/reloading
- **Beginner-friendly** code with comprehensive comments
- **Production-grade** architecture and safety features

## 📋 Project Structure

```
blocked/
├── blocker.py              # Main application (hosts file management)
├── local_server.py         # HTTP server for reminder page
├── blocked_sites.txt       # List of domains to block
├── quotes.json             # Motivational & Quranic quotes
├── reminder_page/
│   └── index.html          # Reminder page UI
├── focusguardian.plist     # macOS LaunchAgent configuration
├── hosts.backup            # Auto-created backup of original hosts file
└── logs/
    ├── focusguardian.out   # Server output logs
    └── focusguardian.err   # Error logs
```

## 🚀 Quick Start

### 1. Install

```bash
# Clone or navigate to project directory
cd /Users/khalidmuhammad/Desktop/blocked

# Make scripts executable (already done)
chmod +x blocker.py local_server.py
```

### 2. Configure Blocked Sites

Edit `blocked_sites.txt` to add domains you want to block:

```txt
facebook.com
instagram.com
reddit.com
# Add more sites...
```

### 3. Test the Blocker

```bash
# View currently blocked sites
python3 blocker.py status

# Enable blocking
sudo python3 blocker.py enable

# Disable blocking
sudo python3 blocker.py disable
```

### 4. Start Local Server

In another terminal:

```bash
python3 local_server.py
```

Visit `http://localhost:8080` in your browser - you should see the reminder page.

### 5. Install LaunchAgent (Automatic Startup)

```bash
# Copy plist to LaunchAgents directory
cp focusguardian.plist ~/Library/LaunchAgents/

# Load it
launchctl load ~/Library/LaunchAgents/focusguardian.plist

# Verify it's loaded
launchctl list | grep focusguardian
```

## 🎮 CLI Commands

### Enable Blocking
```bash
sudo python3 blocker.py enable
```
Activates website blocking and updates the hosts file.

### Disable Blocking
```bash
sudo python3 blocker.py disable
```
Deactivates website blocking without modifying hosts file.

### Show Status
```bash
python3 blocker.py status
```
Displays all currently blocked websites.

### Reload Blocked Sites
```bash
sudo python3 blocker.py reload
```
Reloads `blocked_sites.txt` and updates hosts file.

### Restore Original Hosts
```bash
sudo python3 blocker.py restore
```
Restores the original hosts file from backup.

## 📝 Configuration Files

### blocked_sites.txt
Simple text file with one domain per line:
- Comments start with `#`
- The blocker automatically adds `www.` variants
- Example:
  ```txt
  # Social Media
  facebook.com
  instagram.com
  
  # Add your sites below
  example.com
  ```

### quotes.json
JSON file with motivational and Quranic quotes:
```json
{
  "motivational": [
    "Success is not final...",
    "Focus on being productive..."
  ],
  "quranic": [
    "Indeed, with hardship comes ease...",
    "Verily, in the remembrance of Allah..."
  ]
}
```

### focusguardian.plist
macOS LaunchAgent configuration:
- Automatically runs `blocker.py enable` on login
- Restarts automatically if the process crashes
- Logs output to `/tmp/focusguardian.out`
- Logs errors to `/tmp/focusguardian.err`

## 🔧 How It Works

### Hosts File Modification (blocker.py)

1. **Backup Original**: Creates a backup of `/etc/hosts` on first run
2. **Read Blocked Sites**: Loads domains from `blocked_sites.txt`
3. **Add Entries**: Adds entries like `127.0.0.1 facebook.com` to redirect blocked sites to localhost
4. **Include Variants**: Automatically adds `www.` variants for each domain
5. **Preserve Content**: Maintains all existing hosts file entries

Example hosts file entries created:
```
127.0.0.1 facebook.com
127.0.0.1 www.facebook.com
127.0.0.1 instagram.com
127.0.0.1 www.instagram.com
```

### Local Server (local_server.py)

1. **Runs on localhost:8080**: Acts as a reminder page server
2. **Displays Quotes**: Shows random motivational or Quranic quotes
3. **Prevents Repeats**: Avoids showing the same quote consecutively
4. **Responsive Design**: Works on desktop, tablet, and mobile
5. **Real-time Clock**: Displays current time on reminder page

When a user tries to access a blocked site:
1. The hosts file redirects the request to `127.0.0.1` (localhost)
2. The local server (running on port 8080) intercepts the request
3. A reminder page is displayed with a motivational quote
4. The user is prompted to refocus

### Background Execution

The `focusguardian.plist` file configures macOS to:
- Automatically start the blocker on login
- Keep it running in the background
- Restart it automatically if it crashes
- Log all output for debugging

## 🔐 Safety Features

### Backup & Recovery
```bash
# Automatic backup created before first modification
/Users/khalidmuhammad/Desktop/blocked/hosts.backup

# Restore anytime with:
sudo python3 blocker.py restore
```

### Validation
- Domain format validation before adding to hosts file
- Invalid domains are logged but not added
- Duplicate prevention ensures clean hosts file

### Logging
All operations are logged to `/tmp/focusguardian.out`:
```bash
# View logs
tail -f /tmp/focusguardian.out
```

### Graceful Error Handling
- Permission errors are caught and reported
- File I/O errors don't corrupt the hosts file
- Server startup errors provide helpful debugging info

## 🐛 Troubleshooting

### "Permission Denied" Error
The blocker needs `sudo` to modify `/etc/hosts`:
```bash
sudo python3 blocker.py enable
```

### Server Port Already in Use
Another process is using port 8080:
```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>
```

### Websites Still Accessible
1. Check if blocking is enabled: `python3 blocker.py status`
2. Check if server is running: `curl http://localhost:8080`
3. Flush DNS cache: `sudo dscacheutil -flushcache`
4. Check hosts file permissions: `ls -l /etc/hosts`

### LaunchAgent Not Starting
```bash
# Verify plist is properly formatted
plutil -lint ~/Library/LaunchAgents/focusguardian.plist

# Check if loaded
launchctl list | grep focusguardian

# View logs
cat /tmp/focusguardian.out
cat /tmp/focusguardian.err
```

## 📊 Logs

### Output Logs
```bash
# View real-time output
tail -f /tmp/focusguardian.out
```

### Error Logs
```bash
# View error output
tail -f /tmp/focusguardian.err
```

## 🛠 Advanced Usage

### Custom Reminder Page
Edit `reminder_page/index.html` to customize the appearance.

### Add Dynamic Quotes
Add more quotes to `quotes.json` in either category.

### Monitor Active Sessions
```bash
# Check if server is running
ps aux | grep "local_server.py"

# Check if blocker is loaded
launchctl list | grep focusguardian
```

### Disable LaunchAgent
```bash
# Unload the LaunchAgent
launchctl unload ~/Library/LaunchAgents/focusguardian.plist

# Remove it
rm ~/Library/LaunchAgents/focusguardian.plist
```

## 🔄 Workflow Example

```bash
# 1. Configure sites to block
nano /Users/khalidmuhammad/Desktop/blocked/blocked_sites.txt

# 2. Test locally first
sudo python3 blocker.py enable
python3 local_server.py

# 3. Test in browser
open http://localhost:8080
# Try visiting a blocked site

# 4. Install for automatic startup
cp focusguardian.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/focusguardian.plist

# 5. Verify it's running
launchctl list | grep focusguardian

# 6. Check logs
tail /tmp/focusguardian.out
```

## 📋 Code Architecture

### blocker.py
- **read_blocked_sites()**: Loads domains from text file
- **validate_domain()**: Ensures domain format is valid
- **update_hosts_file()**: Modifies /etc/hosts with blocking entries
- **restore_hosts_file()**: Restores from backup
- **Modular CLI**: Commands for enable/disable/reload/restore/status

### local_server.py
- **load_quotes()**: Reads quotes.json into memory
- **get_random_quote()**: Selects random quote with no-repeat logic
- **ReminderRequestHandler**: Custom HTTP handler for all requests
- **start_server()**: Runs HTTP server on localhost:8080

### reminder_page/index.html
- Responsive design with CSS Grid/Flexbox
- Real-time clock using JavaScript
- Smooth animations and modern UI
- Mobile-friendly layout

## ⚖️ How Hosts File Blocking Works

The hosts file maps domain names to IP addresses. By adding:
```
127.0.0.1 facebook.com
```

Any request to `facebook.com` is redirected to your local machine (`127.0.0.1`), where the local server intercepts it and serves the reminder page.

This works at the **OS level**, so it affects:
- ✅ Chrome, Safari, Firefox, Edge
- ✅ Any application making DNS requests
- ✅ VPNs and proxies (in most cases)

## 📚 Learning Resources

This project demonstrates:
- Python file I/O and error handling
- HTTP server implementation
- macOS system administration
- Process management and logging
- Command-line interface design
- JSON data handling
- Shell integration with LaunchAgent

## 🤝 Contributing

Feel free to:
- Add more Quranic reminders
- Improve the reminder page design
- Add new CLI commands
- Enhance error handling

## 📄 License

This project is provided as-is for personal focus and productivity use.

## 🙏 Inspiration

> "The greatest wealth is health, and the greatest health is mental focus."

Stay focused. Stay productive. 🚀

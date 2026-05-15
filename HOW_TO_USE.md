# 🚀 FocusGuardian - Complete Usage Guide

## Overview


 blocks distracting websites on macOS by modifying your `/etc/hosts` file. When you try to visit a blocked site, it redirects you to a local reminder page with motivational quotes.

---

## 📋 Prerequisites
- **macOS** (tested on Big Sur and above)
- **Python 3.6+** (usually pre-installed)
- **Terminal access**
- **Sudo password** (for enabling/disabling blocking)

---

## 🎯 Quick Start (5 minutes)

### Step 1: Open Terminal
```bash
# Navigate to project folder
cd /Users/khalidmuhammad/Desktop/blocked
```

### Step 2: View What's Blocked
```bash
# See all 24 blocked websites
cat blocked_sites.txt
```

**Output example:**
```
facebook.com
www.facebook.com
instagram.com
www.instagram.com
youtube.com
www.youtube.com
reddit.com
...
```

### Step 3: Test Without Blocking (First Time!)
```bash
# Start the reminder page server
python3 local_server.py
```

**Terminal output:**
```
Starting FocusGuardian server on http://localhost:8080...
Server running. Press Ctrl+C to stop.
```

✅ **Keep this terminal window OPEN**

### Step 4: Open Another Terminal Window
**While the first terminal is running the server:**

```bash
# Open NEW terminal (Command + T in Terminal)
cd /Users/khalidmuhammad/Desktop/blocked
```

### Step 5: Enable Blocking (ONE COMMAND)
```bash
sudo python3 blocker.py enable
```

**What happens:**
- Terminal asks for your password
- Creates backup of `/etc/hosts` (safe!)
- Adds blocking entries
- Takes effect immediately

**Password prompt:**
```
Password: [TYPE YOUR PASSWORD - won't show]
```

### Step 6: Test It!
Open your browser and try visiting:
- `youtube.com` → Shows reminder page ✨
- `reddit.com` → Shows different quote
- `facebook.com` → Another quote
- `google.com` → Works normally (not blocked)

**What you'll see:**
```
╔════════════════════════════════════════════╗
║      🎯 FOCUSGUARDIAN - FOCUS TIME 🎯     ║
╚════════════════════════════════════════════╝

"The only way to do great work is to love 
what you do." - Steve Jobs

⏰ Current Time: 19:04:57

✨ Quick Tips:
• Take a 5-minute break
• Do some stretching
• Drink water
• Check your goals
```

### Step 7: Try Different Sites
Refresh youtube.com multiple times:
- 1st visit: Shows quote A
- 2nd visit: Shows quote B  
- 3rd visit: Shows quote C
- Each time = NEW random quote! 🎲

---

## 🛑 Stopping/Disabling

### Option A: Disable Blocking (Keep Server Running)
**In a new terminal:**
```bash
cd /Users/khalidmuhammad/Desktop/blocked
sudo python3 blocker.py disable
```

- Blocked sites work normally again
- Server still runs on localhost:8080
- Can re-enable anytime

### Option B: Stop Web Server
**In the terminal running the server:**
```bash
# Press Ctrl+C
^C
```

Or in a new terminal:
```bash
ps aux | grep local_server
# Find the PID number, then:
kill -9 [PID_NUMBER]
```

### Option C: Disable + Stop Everything
```bash
sudo python3 blocker.py disable    # Step 1: Disable blocking
# Then press Ctrl+C in server terminal  # Step 2: Stop server
```

---

## 📊 Check Status Anytime

### See if Blocking is Active
```bash
python3 blocker.py status
```

**Output if ACTIVE:**
```
FocusGuardian Status:
  Blocking: ENABLED ✅
  Total blocked sites: 24
  Blocked domains: facebook.com, instagram.com, youtube.com, ...
```

**Output if DISABLED:**
```
FocusGuardian Status:
  Blocking: DISABLED ❌
  Total blocked sites: 24
  (Blocking not active)
```

---

## 🎨 How It Works (Behind the Scenes)

### The Blocking Process
```
1. You type: youtube.com
   ↓
2. macOS checks /etc/hosts file first (before the internet)
   ↓
3. Finds: "127.0.0.1  youtube.com"
   ↓
4. Routes to localhost (127.0.0.1)
   ↓
5. Local server (port 8080) responds with reminder page
   ↓
6. You see motivational quote instead of YouTube
```

### Why This Works
- ✅ Works across ALL browsers (Chrome, Safari, Firefox, Edge)
- ✅ Works across ALL applications
- ✅ Blocks at OS level (before internet connection)
- ✅ Survives most VPNs
- ✅ No additional software needed

---

## ⚙️ Advanced: Modify Blocked Sites

### Add New Sites to Block

**Step 1: Edit the file**
```bash
# Open with your text editor
nano blocked_sites.txt
```

**Step 2: Add sites (one per line)**
```
Add these lines:
pinterest.com
www.pinterest.com
```

**Step 3: Save and exit**
```
Press: Ctrl+O (save)
Press: Enter (confirm)
Press: Ctrl+X (exit)
```

**Step 4: Reload blocking**
```bash
sudo python3 blocker.py reload
```

Done! New sites are blocked immediately.

### Remove Sites from Block

**Step 1: Edit the file**
```bash
nano blocked_sites.txt
```

**Step 2: Delete lines you don't want**
```
DELETE these:
pinterest.com
www.pinterest.com
```

**Step 3: Save and reload**
```bash
Ctrl+O → Enter → Ctrl+X
sudo python3 blocker.py reload
```

---

## 🔄 Full Command Reference

| Command | What It Does | Needs Sudo? |
|---------|-------------|-----------|
| `python3 blocker.py enable` | Start blocking websites | ✅ YES |
| `python3 blocker.py disable` | Stop blocking | ✅ YES |
| `python3 blocker.py reload` | Reload after editing blocked_sites.txt | ✅ YES |
| `python3 blocker.py status` | Check if blocking is active | ❌ NO |
| `python3 blocker.py restore` | Restore original /etc/hosts file | ✅ YES |
| `python3 local_server.py` | Start reminder page server | ❌ NO |

---

## 🐛 Troubleshooting

### Problem: "Port 8080 already in use"
**Solution:**
```bash
# Find what's using port 8080
lsof -i :8080

# Kill the process
kill -9 [PID_NUMBER]

# Start server again
python3 local_server.py
```

### Problem: "Permission denied" or "must run with sudo"
**Solution:** Make sure to use `sudo` for blocking commands
```bash
sudo python3 blocker.py enable
# ^ don't forget the sudo!
```

### Problem: Sites still not blocked after enable
**Solution:**
1. Wait 5 seconds for system to update
2. Try a different site
3. Check status: `python3 blocker.py status`
4. Try full stop/start:
   ```bash
   sudo python3 blocker.py disable
   sudo python3 blocker.py enable
   ```

### Problem: Can't see the reminder page
**Solution:**
1. Make sure server is running: `python3 local_server.py`
2. Check: `curl http://localhost:8080`
3. Try in browser: `http://localhost:8080`

### Problem: Want to unblock everything
**Solution:**
```bash
# Option 1: Disable (keeps ability to re-enable)
sudo python3 blocker.py disable

# Option 2: Complete restore (removes all traces)
sudo python3 blocker.py restore
```

---

## 📁 Project Files Explained

| File | Purpose |
|------|---------|
| `blocker.py` | Main app - handles blocking/unblocking |
| `local_server.py` | Web server - serves reminder pages |
| `blocked_sites.txt` | List of sites to block (edit this to customize) |
| `quotes.json` | Motivational quotes shown on reminder page |
| `reminder_page/index.html` | Beautiful reminder page design |
| `focusguardian.plist` | (Advanced) For auto-start on login |

---

## 🎯 Typical Workflow

### Monday Morning: Start Focusing
```bash
cd /Users/khalidmuhammad/Desktop/blocked
python3 local_server.py &        # Start server (background)
sudo python3 blocker.py enable   # Enable blocking
```

### During Work: Check What's Blocked
```bash
python3 blocker.py status
```

### End of Day: Stop Everything
```bash
sudo python3 blocker.py disable
```

### Customize Blocked Sites
```bash
nano blocked_sites.txt           # Edit sites
sudo python3 blocker.py reload   # Apply changes
```

---

## ✨ Tips & Tricks

✅ **Pro Tip #1: Background Server**
Keep the server running even after you close terminal:
```bash
# Instead of: python3 local_server.py
# Use this:
nohup python3 local_server.py > /tmp/focusguardian.log &
```

✅ **Pro Tip #2: Quick Toggle**
Create aliases for faster commands:
```bash
# Add to ~/.zshrc or ~/.bash_profile
alias focuson="sudo python3 ~/Desktop/blocked/blocker.py enable"
alias focusoff="sudo python3 ~/Desktop/blocked/blocker.py disable"
alias focusstatus="python3 ~/Desktop/blocked/blocker.py status"
```

Then just use:
```bash
focuson      # Enable
focusoff     # Disable  
focusstatus  # Check status
```

✅ **Pro Tip #3: View Current Hosts File**
```bash
# See what entries FocusGuardian added
grep "FocusGuardian" /etc/hosts

# See all blocked sites
grep "127.0.0.1" /etc/hosts | grep -v "#"
```

---

## 🔐 Safety & Backups

### Automatic Backups Created
When you run `sudo python3 blocker.py enable`, the system creates 3 backups:
1. **Initial backup** - First time you enable
2. **Dated backup** - Each day you enable
3. **Pre-restore backup** - Before disabling

**Location:** `/etc/hosts.focusguardian.backup*`

### If Something Goes Wrong
```bash
# Restore from backup
sudo python3 blocker.py restore

# This puts your /etc/hosts back to original
```

---

## 📚 Need More Help?

- **Check README.md** - Detailed project documentation
- **View quotes.json** - Edit or add your own quotes
- **Edit blocked_sites.txt** - Customize which sites to block
- **Modify reminder_page/index.html** - Customize the reminder page design

---

## 🎉 You're All Set!

You now know how to:
- ✅ Start the server
- ✅ Enable/disable blocking
- ✅ Test it in your browser
- ✅ Add/remove blocked sites
- ✅ Check status
- ✅ Fix common problems

**Happy focusing! 🚀**

---

*Last updated: May 15, 2026*

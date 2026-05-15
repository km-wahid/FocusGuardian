#!/usr/bin/env python3
"""
FocusGuardian - macOS Website Blocker
A production-ready website blocker that runs locally and redirects blocked sites to reminders.

Main application entry point for managing blocking functionality.
"""

import sys
import os
import json
import logging
import shutil
import tempfile
from pathlib import Path
import argparse
import time
import subprocess
from datetime import datetime

# Configure logging
log_dir = Path("/tmp")
log_file = log_dir / "focusguardian.out"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_DIR = Path("/Users/khalidmuhammad/Desktop/blocked")
BLOCKED_SITES_FILE = PROJECT_DIR / "blocked_sites.txt"
HOSTS_FILE = Path("/etc/hosts")
HOSTS_BACKUP = PROJECT_DIR / "hosts.backup"
HOSTS_BACKUP_DATED = PROJECT_DIR / "hosts.backup.pre-blocker"
QUOTES_FILE = PROJECT_DIR / "quotes.json"

# FocusGuardian markers for hosts file
BLOCKER_START_MARKER = "# ===== FocusGuardian Blocked Sites START ====="
BLOCKER_END_MARKER = "# ===== FocusGuardian Blocked Sites END ====="


def read_blocked_sites():
    """
    Read blocked websites from blocked_sites.txt.
    
    Parses the configuration file, skipping:
    - Empty lines
    - Comments (lines starting with #)
    
    Returns:
        list: List of domain names to block (sorted, unique)
    """
    if not BLOCKED_SITES_FILE.exists():
        logger.warning(f"Blocked sites file not found: {BLOCKED_SITES_FILE}")
        return []
    
    try:
        with open(BLOCKED_SITES_FILE, 'r') as f:
            # Filter out empty lines and comments, strip whitespace
            sites = [
                line.strip() 
                for line in f 
                if line.strip() and not line.strip().startswith('#')
            ]
        
        # Remove duplicates and sort for consistency
        sites = sorted(list(set(sites)))
        logger.info(f"Loaded {len(sites)} blocked sites")
        return sites
    except Exception as e:
        logger.error(f"Error reading blocked sites: {e}")
        return []


def validate_domain(domain):
    """
    Validate domain name format with comprehensive checks.
    
    Validates:
    - Not empty
    - Length <= 255 characters (DNS limit)
    - No invalid characters
    - Proper domain format
    
    Args:
        domain (str): Domain name to validate
    
    Returns:
        bool: True if domain is valid, False otherwise
    """
    # Check for empty or None
    if not domain or not isinstance(domain, str):
        return False
    
    domain = domain.strip()
    
    # Check length (DNS standard)
    if len(domain) > 255 or len(domain) < 3:
        return False
    
    # Invalid characters that should not appear in domains
    invalid_chars = ['@', '#', '$', '%', '&', '*', ' ', '\t', '\n', '/', '\\', '?', '=']
    for char in invalid_chars:
        if char in domain:
            return False
    
    # Must not start or end with a dot
    if domain.startswith('.') or domain.endswith('.'):
        return False
    
    # Must not have consecutive dots
    if '..' in domain:
        return False
    
    # Domain must have at least one dot (e.g., example.com, not just 'example')
    # Exception: localhost
    if domain != 'localhost' and '.' not in domain:
        return False
    
    return True


def create_backup():
    """
    Create a backup of the original hosts file before modification.
    
    Performs:
    - Checks if backup already exists
    - Creates dated backup if original exists
    - Logs backup location
    
    Returns:
        bool: True if backup created or already exists, False on error
    """
    try:
        if not HOSTS_FILE.exists():
            logger.warning(f"Hosts file not found at {HOSTS_FILE}")
            return False
        
        # Create initial backup if it doesn't exist
        if not HOSTS_BACKUP.exists():
            logger.info(f"Creating initial backup: {HOSTS_BACKUP}")
            shutil.copy2(HOSTS_FILE, HOSTS_BACKUP)
            logger.info("Initial backup created successfully")
        
        # Also create a dated backup for version history
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dated_backup = PROJECT_DIR / f"hosts.backup.{timestamp}"
        if not dated_backup.exists():
            shutil.copy2(HOSTS_FILE, dated_backup)
            logger.info(f"Created dated backup: {dated_backup}")
        
        return True
    
    except PermissionError:
        logger.error("Permission denied when creating backup. Try running with sudo.")
        return False
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False


def update_hosts_file(block=True):
    """
    Update /etc/hosts file to redirect blocked domains to 127.0.0.1.
    
    This function:
    1. Creates backup before modification
    2. Reads current hosts file
    3. Removes old FocusGuardian entries (idempotent)
    4. Adds new blocking entries with markers
    5. Validates each domain before adding
    6. Adds both domain and www.domain variants
    7. Writes safely to temporary file first
    
    Args:
        block (bool): If True, add blocking entries; if False, remove them
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create backup first
        if not create_backup():
            logger.error("Failed to create backup. Aborting hosts file modification.")
            return False
        
        # Read current hosts file
        if HOSTS_FILE.exists():
            with open(HOSTS_FILE, 'r') as f:
                content = f.read()
        else:
            logger.warning(f"Hosts file not found at {HOSTS_FILE}, creating new one")
            content = ""
        
        # Parse hosts file into lines
        lines = content.split('\n')
        
        # Remove old FocusGuardian entries and preserve everything else
        filtered_lines = []
        in_blocker_section = False
        
        for line in lines:
            # Skip FocusGuardian sections
            if BLOCKER_START_MARKER in line:
                in_blocker_section = True
                continue
            if BLOCKER_END_MARKER in line:
                in_blocker_section = False
                continue
            if in_blocker_section:
                continue
            
            # Keep all non-blocker lines
            filtered_lines.append(line)
        
        # If blocking is enabled, add new entries
        if block:
            logger.info("Adding blocking entries to hosts file...")
            blocked_sites = read_blocked_sites()
            
            if not blocked_sites:
                logger.warning("No blocked sites found. Nothing to add.")
                return True
            
            # Build new blocking section
            new_entries = [BLOCKER_START_MARKER]
            blocked_count = 0
            
            for site in blocked_sites:
                if not validate_domain(site):
                    logger.warning(f"Invalid domain, skipping: {site}")
                    continue
                
                # Add main domain
                entry = f"127.0.0.1 {site}"
                new_entries.append(entry)
                blocked_count += 1
                
                # Add www variant if it doesn't already include www
                if not site.startswith('www.'):
                    www_entry = f"127.0.0.1 www.{site}"
                    new_entries.append(www_entry)
                    blocked_count += 1
            
            new_entries.append(BLOCKER_END_MARKER)
            
            # Combine old lines with new blocking section
            filtered_lines.extend(new_entries)
            logger.info(f"Added {blocked_count} blocking entries for {len(blocked_sites)} domains")
        else:
            logger.info("Removing blocking entries from hosts file...")
        
        # Write to temporary file first (atomic operation safety)
        updated_content = '\n'.join(filtered_lines)
        
        # Use temporary file to ensure atomic write
        temp_fd, temp_path = tempfile.mkstemp(dir=PROJECT_DIR)
        try:
            with os.fdopen(temp_fd, 'w') as temp_file:
                temp_file.write(updated_content)
            
            # Test write by reading the temp file
            with open(temp_path, 'r') as test_file:
                test_content = test_file.read()
            
            if test_content != updated_content:
                logger.error("Temporary file write verification failed")
                os.unlink(temp_path)
                return False
            
            # Safe to write to actual hosts file
            logger.info("Writing to /etc/hosts...")
            shutil.copy2(temp_path, HOSTS_FILE)
            os.chmod(HOSTS_FILE, 0o644)
            
            logger.info("Successfully updated hosts file")
            return True
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except PermissionError:
        logger.error("Permission denied. This command requires sudo privileges.")
        logger.error("Try running: sudo python3 blocker.py " + ("enable" if block else "disable"))
        return False
    except Exception as e:
        logger.error(f"Error updating hosts file: {e}")
        return False


def restore_hosts_file():
    """
    Restore the original hosts file from backup.
    
    Steps:
    1. Checks if backup exists
    2. Creates dated backup of current state
    3. Restores from original backup
    4. Verifies restore was successful
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not HOSTS_BACKUP.exists():
            logger.error(f"Backup file not found: {HOSTS_BACKUP}")
            logger.error("Cannot restore without a backup. The original hosts file may have been deleted.")
            return False
        
        # Create backup of current state before restoring
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_restore_backup = PROJECT_DIR / f"hosts.backup.before-restore.{timestamp}"
        try:
            shutil.copy2(HOSTS_FILE, pre_restore_backup)
            logger.info(f"Created backup before restore: {pre_restore_backup}")
        except Exception as e:
            logger.warning(f"Could not create pre-restore backup: {e}")
        
        # Verify backup is readable
        with open(HOSTS_BACKUP, 'r') as f:
            backup_content = f.read()
        
        if not backup_content:
            logger.error("Backup file is empty or unreadable")
            return False
        
        # Restore the backup
        logger.info("Restoring hosts file from backup...")
        shutil.copy2(HOSTS_BACKUP, HOSTS_FILE)
        os.chmod(HOSTS_FILE, 0o644)
        
        # Verify restore
        with open(HOSTS_FILE, 'r') as f:
            restored_content = f.read()
        
        if restored_content != backup_content:
            logger.error("Restore verification failed: contents don't match")
            return False
        
        logger.info("Hosts file restored successfully")
        return True
    
    except PermissionError:
        logger.error("Permission denied. This command requires sudo privileges.")
        logger.error("Try running: sudo python3 blocker.py restore")
        return False
    except Exception as e:
        logger.error(f"Error restoring hosts file: {e}")
        return False


def start_blocking():
    """
    Start website blocking by adding entries to hosts file.
    
    Process:
    1. Create backup if needed
    2. Validate all blocked sites
    3. Update hosts file with blocking entries
    4. Verify the operation
    """
    logger.info("="*60)
    logger.info("FocusGuardian: Starting website blocker")
    logger.info("="*60)
    
    if check_blocker_status():
        logger.info("⚠️  Blocker is already active")
        return
    
    if update_hosts_file(block=True):
        logger.info("✅ Website blocking enabled successfully")
        logger.info(f"📍 Backup location: {HOSTS_BACKUP}")
        logger.info(f"📝 Blocked sites: {len(read_blocked_sites())} domains")
    else:
        logger.error("❌ Failed to enable website blocking")


def stop_blocking():
    """
    Stop website blocking by removing entries from hosts file.
    
    Process:
    1. Remove FocusGuardian section from hosts file
    2. Preserve all other entries
    3. Verify the operation
    """
    logger.info("="*60)
    logger.info("FocusGuardian: Stopping website blocker")
    logger.info("="*60)
    
    if not check_blocker_status():
        logger.info("⚠️  Blocker is already inactive")
        return
    
    if update_hosts_file(block=False):
        logger.info("✅ Website blocking disabled successfully")
    else:
        logger.error("❌ Failed to disable website blocking")


def show_blocked_sites():
    """
    Display currently blocked websites with detailed information.
    
    Shows:
    - Number of blocked domains
    - List of blocked sites
    - Current blocker status
    """
    sites = read_blocked_sites()
    
    print("\n" + "="*60)
    print("FocusGuardian - Blocked Websites Status")
    print("="*60)
    
    if not sites:
        print("  ⚠️  No blocked sites configured")
        print("\n  Edit blocked_sites.txt to add sites")
    else:
        print(f"\n  📍 Total Sites: {len(sites)}\n")
        
        # Group by category
        social_media = [s for s in sites if any(x in s for x in ['facebook', 'instagram', 'twitter', 'reddit', 'tiktok', 'snapchat'])]
        streaming = [s for s in sites if any(x in s for x in ['netflix', 'hulu', 'disney', 'youtube'])]
        news = [s for s in sites if any(x in s for x in ['cnn', 'bbc', 'news'])]
        other = [s for s in sites if s not in social_media and s not in streaming and s not in news]
        
        if social_media:
            print("  🔗 Social Media:")
            for site in social_media:
                print(f"     • {site}")
        
        if streaming:
            print("\n  🎬 Streaming:")
            for site in streaming:
                print(f"     • {site}")
        
        if news:
            print("\n  📰 News:")
            for site in news:
                print(f"     • {site}")
        
        if other:
            print("\n  ⚙️  Other:")
            for site in other:
                print(f"     • {site}")
    
    print("\n" + "="*60)
    print("  Commands:")
    print("    • sudo python3 blocker.py enable   - Start blocking")
    print("    • sudo python3 blocker.py disable  - Stop blocking")
    print("    • sudo python3 blocker.py reload   - Reload sites")
    print("    • sudo python3 blocker.py restore  - Restore original")
    print("="*60 + "\n")


def check_blocker_status():
    """
    Check if blocking is currently active.
    
    Returns:
        bool: True if blocking is active (FocusGuardian section in hosts file)
    """
    try:
        if not HOSTS_FILE.exists():
            return False
        
        with open(HOSTS_FILE, 'r') as f:
            content = f.read()
        
        return BLOCKER_START_MARKER in content
    except Exception as e:
        logger.error(f"Error checking blocker status: {e}")
        return False


def reload_blocked_sites():
    """
    Reload blocked sites list from blocked_sites.txt and update hosts file.
    
    Useful when you've edited blocked_sites.txt and want changes to take effect immediately.
    """
    logger.info("="*60)
    logger.info("FocusGuardian: Reloading blocked sites")
    logger.info("="*60)
    
    sites = read_blocked_sites()
    logger.info(f"Loaded {len(sites)} sites from configuration")
    
    if check_blocker_status():
        if update_hosts_file(block=True):
            logger.info("✅ Blocked sites reloaded successfully")
        else:
            logger.error("❌ Failed to reload blocked sites")
    else:
        logger.warning("⚠️  Blocker is currently inactive. No changes made.")
        logger.info("    Run 'sudo python3 blocker.py enable' to activate blocking")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="FocusGuardian - macOS Website Blocker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Enable blocking (requires sudo)
  sudo python3 blocker.py enable
  
  # Disable blocking (requires sudo)
  sudo python3 blocker.py disable
  
  # Show blocked websites
  python3 blocker.py status
  
  # Reload blocked sites (after editing blocked_sites.txt)
  sudo python3 blocker.py reload
  
  # Restore original hosts file
  sudo python3 blocker.py restore

REQUIREMENTS:
  • Use 'sudo' for enable, disable, and restore commands
  • Edit blocked_sites.txt to customize blocked websites
  • Edit quotes.json to customize reminder quotes

TROUBLESHOOTING:
  • If "Permission Denied", use sudo
  • View logs: tail -f /tmp/focusguardian.out
  • Check status: sudo python3 blocker.py status
        """
    )
    
    parser.add_argument(
        'action',
        choices=['enable', 'disable', 'status', 'reload', 'restore'],
        help='Action to perform'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Adjust logging level if verbose
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
    
    logger.info(f"FocusGuardian v1.0 - Action: {args.action}")
    
    try:
        if args.action == 'enable':
            # Check for sudo
            if os.geteuid() != 0:
                print("❌ Error: 'enable' requires sudo privileges")
                print("   Try: sudo python3 blocker.py enable")
                sys.exit(1)
            start_blocking()
        
        elif args.action == 'disable':
            # Check for sudo
            if os.geteuid() != 0:
                print("❌ Error: 'disable' requires sudo privileges")
                print("   Try: sudo python3 blocker.py disable")
                sys.exit(1)
            stop_blocking()
        
        elif args.action == 'status':
            show_blocked_sites()
            if check_blocker_status():
                print("✅ Status: BLOCKING ACTIVE\n")
            else:
                print("⏸️  Status: BLOCKING INACTIVE\n")
        
        elif args.action == 'reload':
            # Check for sudo
            if os.geteuid() != 0:
                print("❌ Error: 'reload' requires sudo privileges")
                print("   Try: sudo python3 blocker.py reload")
                sys.exit(1)
            reload_blocked_sites()
        
        elif args.action == 'restore':
            # Check for sudo
            if os.geteuid() != 0:
                print("❌ Error: 'restore' requires sudo privileges")
                print("   Try: sudo python3 blocker.py restore")
                sys.exit(1)
            restore_hosts_file()
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error executing action '{args.action}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

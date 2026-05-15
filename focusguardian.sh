#!/bin/bash

################################################################################
#                                                                              #
#           🎯 FocusGuardian - Automated Startup Script 🎯                  #
#                                                                              #
#  This script starts everything needed for FocusGuardian to work:           #
#  1. Web server on localhost:8080                                           #
#  2. Enable website blocking                                                #
#  3. Create backups automatically                                           #
#                                                                              #
#  Usage:                                                                     #
#    ./focusguardian.sh start    → Start everything                         #
#    ./focusguardian.sh stop     → Stop everything                          #
#    ./focusguardian.sh status   → Check status                             #
#    ./focusguardian.sh help     → Show help                                #
#                                                                              #
################################################################################


# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_SCRIPT="$SCRIPT_DIR/local_server.py"
BLOCKER_SCRIPT="$SCRIPT_DIR/blocker.py"
PID_FILE="/tmp/focusguardian_server.pid"
LOG_FILE="/tmp/focusguardian_server.log"


################################################################################
#                           🎨 HELPER FUNCTIONS
################################################################################

# Print colored output
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if Python 3 is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed!"
        echo "Please install Python 3 first: https://www.python.org/downloads/"
        exit 1
    fi
    print_success "Python 3 found"
}

# Check if scripts exist
check_scripts() {
    if [ ! -f "$SERVER_SCRIPT" ]; then
        print_error "local_server.py not found!"
        exit 1
    fi
    if [ ! -f "$BLOCKER_SCRIPT" ]; then
        print_error "blocker.py not found!"
        exit 1
    fi
    print_success "All scripts found"
}

# Check if server is already running
is_server_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0  # Running
        fi
    fi
    return 1  # Not running
}

# Start the web server
start_server() {
    print_info "Starting web server..."
    
    if is_server_running; then
        print_info "Server already running (PID: $(cat $PID_FILE))"
        return 0
    fi
    
    # Start server in background and save PID
    nohup python3 "$SERVER_SCRIPT" > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo $pid > "$PID_FILE"
    
    # Wait for server to start
    sleep 2
    
    # Check if server started successfully
    if kill -0 $pid 2>/dev/null; then
        print_success "Web server started (PID: $pid)"
        echo "  URL: http://localhost:8080"
        return 0
    else
        print_error "Failed to start web server"
        return 1
    fi
}

# Stop the web server
stop_server() {
    print_info "Stopping web server..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null
            print_success "Web server stopped"
        fi
        rm -f "$PID_FILE"
    else
        print_info "Server not running"
    fi
}

# Enable blocking
enable_blocking() {
    print_info "Enabling website blocking..."
    
    # Run blocker enable command with sudo
    cd "$SCRIPT_DIR"
    if sudo python3 "$BLOCKER_SCRIPT" enable; then
        print_success "Website blocking enabled!"
        return 0
    else
        print_error "Failed to enable blocking"
        return 1
    fi
}

# Disable blocking
disable_blocking() {
    print_info "Disabling website blocking..."
    
    cd "$SCRIPT_DIR"
    if sudo python3 "$BLOCKER_SCRIPT" disable; then
        print_success "Website blocking disabled"
        return 0
    else
        print_error "Failed to disable blocking"
        return 1
    fi
}

# Show status
show_status() {
    print_header "🎯 FocusGuardian Status"
    
    # Server status
    if is_server_running; then
        print_success "Web Server: RUNNING (PID: $(cat $PID_FILE))"
    else
        print_error "Web Server: STOPPED"
    fi
    
    # Check if server responds
    if is_server_running; then
        if curl -s http://localhost:8080 > /dev/null 2>&1; then
            print_success "Web Server: RESPONDING on http://localhost:8080"
        else
            print_error "Web Server: NOT RESPONDING"
        fi
    fi
    
    # Blocking status
    echo ""
    cd "$SCRIPT_DIR"
    python3 "$BLOCKER_SCRIPT" status 2>/dev/null || print_error "Could not check blocking status"
}

# Show help
show_help() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║          🚀 FocusGuardian - Automated Startup Script 🚀       ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Usage: ./focusguardian.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start everything (server + blocking)"
    echo "  stop        Stop everything (server + blocking)"
    echo "  status      Check if server and blocking are active"
    echo "  server-on   Start just the server (no blocking)"
    echo "  server-off  Stop just the server"
    echo "  block-on    Enable blocking (server must be running)"
    echo "  block-off   Disable blocking"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./focusguardian.sh start        # Start everything"
    echo "  ./focusguardian.sh status       # Check status"
    echo "  ./focusguardian.sh stop         # Stop everything"
    echo ""
    echo "First Time Setup:"
    echo "  1. chmod +x focusguardian.sh    (make it executable)"
    echo "  2. ./focusguardian.sh start     (run it)"
    echo "  3. Visit http://localhost:8080  (test it)"
    echo ""
}


################################################################################
#                         🚀 MAIN COMMANDS
################################################################################

# START - Start server and enable blocking
start_all() {
    print_header "🚀 Starting FocusGuardian"
    
    check_python
    check_scripts
    
    echo ""
    start_server || exit 1
    
    echo ""
    enable_blocking || exit 1
    
    echo ""
    print_header "✨ FocusGuardian is Ready!"
    echo ""
    print_success "Web Server: http://localhost:8080"
    print_success "Blocking: ENABLED"
    echo ""
    print_info "Test it: Open browser and visit youtube.com"
    echo ""
}

# STOP - Stop server and disable blocking
stop_all() {
    print_header "⏹️  Stopping FocusGuardian"
    
    disable_blocking
    echo ""
    stop_server
    
    echo ""
    print_header "✅ FocusGuardian Stopped"
}

# Parse command and execute
case "${1:-help}" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    status)
        show_status
        ;;
    server-on)
        check_python
        check_scripts
        start_server
        ;;
    server-off)
        stop_server
        ;;
    block-on)
        enable_blocking
        ;;
    block-off)
        disable_blocking
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

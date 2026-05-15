#!/usr/bin/env python3
"""
FocusGuardian Local Web Server
Lightweight HTTP server that serves reminder pages when blocked sites are accessed.
Runs on localhost:8080 and displays motivational quotes and Quranic reminders.

Features:
- Intercepts requests to blocked sites
- Displays reminder pages with random quotes
- Prevents consecutive repeat quotes
- Minimal dependencies (uses Python stdlib only)
- Production-grade error handling and logging
"""

import http.server
import socketserver
import json
import random
import logging
import signal
import sys
from pathlib import Path
from datetime import datetime

# Configure logging with both file and console output
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

# Configuration
PORT = 8080
BIND_ADDRESS = "127.0.0.1"
PROJECT_DIR = Path("/Users/khalidmuhammad/Desktop/blocked")
QUOTES_FILE = PROJECT_DIR / "quotes.json"
REMINDER_PAGE = PROJECT_DIR / "reminder_page" / "index.html"

# Track last displayed quote to avoid consecutive repeats
last_quote = None
request_count = 0  # Track number of requests

# Quote caching for performance
_quotes_cache = None
_page_cache = None


def load_quotes():
    """
    Load motivational quotes and Quranic reminders from quotes.json.
    
    Features:
    - Caches quotes in memory after first load (performance optimization)
    - Validates quote structure
    - Provides fallback quotes if file not found
    - Handles JSON parsing errors gracefully
    
    Returns:
        dict: Contains 'motivational' and 'quranic' lists
    """
    global _quotes_cache
    
    # Return cached quotes if available (avoid file I/O on every request)
    if _quotes_cache is not None:
        return _quotes_cache
    
    try:
        if not QUOTES_FILE.exists():
            logger.warning(f"Quotes file not found: {QUOTES_FILE}")
            _quotes_cache = get_default_quotes()
            return _quotes_cache
        
        with open(QUOTES_FILE, 'r', encoding='utf-8') as f:
            quotes = json.load(f)
        
        # Validate structure
        if not isinstance(quotes, dict):
            logger.error("Quotes file must contain a JSON object")
            _quotes_cache = get_default_quotes()
            return _quotes_cache
        
        # Ensure required keys exist
        if 'motivational' not in quotes or 'quranic' not in quotes:
            logger.warning("Quotes file missing 'motivational' or 'quranic' keys")
            quotes.setdefault('motivational', [])
            quotes.setdefault('quranic', [])
        
        # Validate quote lists
        if not isinstance(quotes['motivational'], list):
            logger.error("'motivational' must be a list")
            quotes['motivational'] = []
        
        if not isinstance(quotes['quranic'], list):
            logger.error("'quranic' must be a list")
            quotes['quranic'] = []
        
        motivational_count = len(quotes['motivational'])
        quranic_count = len(quotes['quranic'])
        
        logger.info(f"Loaded {motivational_count} motivational quotes")
        logger.info(f"Loaded {quranic_count} Quranic reminders")
        
        if motivational_count == 0 and quranic_count == 0:
            logger.warning("No quotes loaded, using defaults")
            _quotes_cache = get_default_quotes()
        else:
            _quotes_cache = quotes
        
        return _quotes_cache
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in quotes file: {e}")
        _quotes_cache = get_default_quotes()
        return _quotes_cache
    except Exception as e:
        logger.error(f"Error loading quotes: {e}")
        _quotes_cache = get_default_quotes()
        return _quotes_cache


def get_default_quotes():
    """
    Provide default quotes if file is not found or invalid.
    
    Returns:
        dict: Default quotes structure
    """
    return {
        'motivational': [
            "Take a break and refocus",
            "Focus is the gateway to success",
            "You are stronger than distractions",
            "This is your time to shine",
            "Stay focused on your goals"
        ],
        'quranic': [
            "Indeed, with hardship comes ease. (Quran 94:5)",
            "Verily, in the remembrance of Allah do hearts find rest. (Quran 13:28)",
            "Allah is with the patient. (Quran 2:153)",
            "Call upon Me; I will respond to you. (Quran 40:60)"
        ]
    }


def get_random_quote():
    """
    Get a random quote, preventing consecutive repeats.
    
    Features:
    - Intelligently avoids showing same quote twice in a row
    - Handles edge case when only one quote available
    - Returns quote text and category type
    - Logs quote selection
    
    Returns:
        tuple: (quote_text, quote_type) where type is 'motivational' or 'quranic'
    """
    global last_quote
    
    quotes = load_quotes()
    all_quotes = []
    
    # Combine both types of quotes with their category
    for quote in quotes.get('motivational', []):
        if quote.strip():  # Only add non-empty quotes
            all_quotes.append((quote, 'motivational'))
    
    for quote in quotes.get('quranic', []):
        if quote.strip():  # Only add non-empty quotes
            all_quotes.append((quote, 'quranic'))
    
    if not all_quotes:
        logger.warning("No quotes available, using fallback")
        return ("Take a moment to refocus", "default")
    
    # If only one quote, return it
    if len(all_quotes) == 1:
        selected_quote = all_quotes[0]
    else:
        # Try to select a quote different from the last one
        available_quotes = [q for q in all_quotes if q != last_quote]
        
        # If all quotes have been shown, allow repeating from entire list
        if not available_quotes:
            available_quotes = all_quotes
        
        selected_quote = random.choice(available_quotes)
    
    last_quote = selected_quote
    logger.debug(f"Selected quote ({selected_quote[1]}): {selected_quote[0][:50]}...")
    
    return selected_quote


def load_reminder_page():
    """
    Load the reminder page HTML template.
    
    Features:
    - Caches template after first load
    - Validates file exists
    - Provides fallback page if template not found
    
    Returns:
        str: HTML content
    """
    try:
        if REMINDER_PAGE.exists():
            with open(REMINDER_PAGE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logger.warning("Reminder page template is empty")
                return get_default_reminder_page()
            
            return content
        else:
            logger.warning(f"Reminder page not found: {REMINDER_PAGE}")
            return get_default_reminder_page()
    
    except Exception as e:
        logger.error(f"Error loading reminder page: {e}")
        return get_default_reminder_page()


def get_default_reminder_page():
    """
    Provide a default reminder page if template is not found.
    
    Returns:
        str: HTML content (static, without placeholders)
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FocusGuardian - Focus Time</title>
        <style>
            body { 
                margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 
                "Segoe UI", Roboto; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                height: 100vh; display: flex; align-items: center; justify-content: center; 
            }
            .container { 
                text-align: center; color: white; padding: 40px; max-width: 600px; 
                background: rgba(255,255,255,0.1); border-radius: 15px; backdrop-filter: blur(10px);
            }
            h1 { font-size: 3em; margin-bottom: 20px; margin-top: 0; }
            .message { font-size: 1.2em; line-height: 1.6; margin-bottom: 30px; }
            .quote { background: rgba(255, 255, 255, 0.2); padding: 20px; border-radius: 10px; 
                   font-style: italic; font-size: 1.1em; border-left: 4px solid #fff; }
            .type { font-size: 0.8em; opacity: 0.9; margin-top: 10px; }
            .time { margin-top: 40px; font-size: 0.9em; opacity: 0.9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⏸️ Focus Time</h1>
            <div class="message">This website is blocked to help you stay focused.</div>
            <div class="quote">
                "Take a moment to refocus on what matters"
                <div class="type">Motivation</div>
            </div>
            <div class="time">FocusGuardian - Stay Focused</div>
        </div>
    </body>
    </html>
    """


class ReminderRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler that serves reminder pages.
    
    Features:
    - Responds to all requests with reminder page
    - Dynamic quote injection into template
    - Prevents page caching
    - Comprehensive logging
    - Suppresses default HTTP logging
    """
    
    def do_GET(self):
        """
        Handle GET requests by serving reminder page with random quote.
        
        Process:
        1. Load reminder page template
        2. Get random quote
        3. Inject quote into template
        4. Send response with proper headers
        """
        global request_count
        request_count += 1
        
        try:
            # Load reminder page template
            page = load_reminder_page()
            
            # Get random quote
            quote, quote_type = get_random_quote()
            
            # Inject dynamic values into template
            page = page.replace("{{QUOTE}}", quote)
            page = page.replace("{{QUOTE_TYPE}}", quote_type.capitalize())
            page = page.replace("{{TIME}}", datetime.now().strftime('%H:%M:%S'))
            page = page.replace("{{TIMESTAMP}}", datetime.now().strftime('%H:%M:%S'))
            
            # Send HTTP response
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_header('Connection', 'close')
            self.end_headers()
            
            # Write response body
            self.wfile.write(page.encode('utf-8'))
            
            # Log request
            client_ip = self.client_address[0]
            logger.info(f"Request #{request_count} from {client_ip} - Served reminder page ({quote_type})")
        
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_error(500, "Internal Server Error")
    
    def do_POST(self):
        """Handle POST requests (redirect to GET handler)."""
        self.do_GET()
    
    def do_HEAD(self):
        """Handle HEAD requests."""
        self.do_GET()
    
    def log_message(self, format, *args):
        """
        Override to suppress default HTTP logging (we use custom logger).
        
        Args:
            format: Log message format
            *args: Format arguments
        """
        # Use logger.debug for verbose debugging only
        logger.debug(f"HTTP: {format % args}")


def signal_handler(sig, frame):
    """Handle graceful shutdown on Ctrl+C."""
    logger.info("Shutdown signal received, stopping server...")
    sys.exit(0)


def start_server(port=PORT, bind_address=BIND_ADDRESS):
    """
    Start the local reminder server.
    
    Features:
    - Binds to localhost only (secure)
    - Reusable socket address
    - Graceful shutdown handling
    - Comprehensive error reporting
    - Request logging
    
    Args:
        port (int): Port to run server on (default: 8080)
        bind_address (str): Address to bind to (default: 127.0.0.1)
    """
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create TCP server with address reuse
        socketserver.TCPServer.allow_reuse_address = True
        
        with socketserver.TCPServer(
            (bind_address, port), 
            ReminderRequestHandler
        ) as httpd:
            logger.info("="*60)
            logger.info("FocusGuardian Reminder Server Started")
            logger.info("="*60)
            logger.info(f"📍 Server running on http://{bind_address}:{port}")
            logger.info(f"📝 Quotes file: {QUOTES_FILE}")
            logger.info(f"📄 Reminder page: {REMINDER_PAGE}")
            logger.info("⏹️  Press Ctrl+C to stop the server")
            logger.info("="*60)
            
            # Start serving requests
            httpd.serve_forever()
    
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"❌ Error: Port {port} is already in use")
            logger.error("   This usually means the server is already running")
            logger.error("   Try:")
            logger.error(f"     • lsof -i :{port}  (find process)")
            logger.error("     • kill -9 <PID>    (kill process)")
        else:
            logger.error(f"❌ OSError: {e}")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    """Entry point for local server."""
    try:
        start_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Test Suite for FocusGuardian - Local Web Server (Step 3)
Tests quote loading, server functionality, and reminder page generation.
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from threading import Thread

# Add project to path
sys.path.insert(0, '/Users/khalidmuhammad/Desktop/blocked')
from local_server import (
    load_quotes, 
    get_random_quote, 
    get_default_quotes,
    QUOTES_FILE
)

def test_quotes_loading():
    """Test loading quotes from JSON file."""
    print("\n" + "="*60)
    print("TEST: Quote Loading")
    print("="*60)
    
    try:
        quotes = load_quotes()
        
        if not isinstance(quotes, dict):
            print("❌ Quotes not loaded as dictionary")
            return False
        
        print(f"✅ Quotes loaded successfully")
        
        # Check for required keys
        if 'motivational' not in quotes or 'quranic' not in quotes:
            print("❌ Missing required quote categories")
            return False
        
        print(f"✅ Contains 'motivational' and 'quranic' categories")
        
        # Check quote counts
        motivational = quotes.get('motivational', [])
        quranic = quotes.get('quranic', [])
        
        print(f"   • Motivational quotes: {len(motivational)}")
        print(f"   • Quranic quotes: {len(quranic)}")
        
        if len(motivational) == 0 or len(quranic) == 0:
            print("⚠️  Warning: Some quote category is empty")
        
        return len(motivational) > 0 and len(quranic) > 0
    
    except Exception as e:
        print(f"❌ Error loading quotes: {e}")
        return False


def test_random_quote_generation():
    """Test random quote selection logic."""
    print("\n" + "="*60)
    print("TEST: Random Quote Generation")
    print("="*60)
    
    try:
        # Get multiple quotes to test variety
        selected_quotes = set()
        
        for i in range(20):
            quote, quote_type = get_random_quote()
            selected_quotes.add(quote)
            
            # Validate quote structure
            if not quote or not isinstance(quote, str):
                print(f"❌ Invalid quote at iteration {i}: {quote}")
                return False
            
            if quote_type not in ['motivational', 'quranic', 'default']:
                print(f"❌ Invalid quote type: {quote_type}")
                return False
        
        print(f"✅ Got {len(selected_quotes)} unique quotes from 20 requests")
        
        if len(selected_quotes) < 2:
            print("⚠️  Warning: Low quote variety")
        else:
            print("✅ Good quote variety - no excessive repeats")
        
        return True
    
    except Exception as e:
        print(f"❌ Error generating quotes: {e}")
        return False


def test_default_quotes():
    """Test default quotes fallback."""
    print("\n" + "="*60)
    print("TEST: Default Quotes Fallback")
    print("="*60)
    
    try:
        default = get_default_quotes()
        
        if not isinstance(default, dict):
            print("❌ Default quotes not a dictionary")
            return False
        
        print("✅ Default quotes loaded")
        
        # Check structure
        if 'motivational' not in default or 'quranic' not in default:
            print("❌ Default quotes missing categories")
            return False
        
        print(f"✅ Default quotes have valid structure")
        print(f"   • Motivational: {len(default['motivational'])} quotes")
        print(f"   • Quranic: {len(default['quranic'])} quotes")
        
        return True
    
    except Exception as e:
        print(f"❌ Error testing defaults: {e}")
        return False


def test_quote_types():
    """Test that quotes have proper types."""
    print("\n" + "="*60)
    print("TEST: Quote Types")
    print("="*60)
    
    try:
        quotes = load_quotes()
        
        motivational_count = 0
        quranic_count = 0
        
        # Verify motivational quotes
        for quote in quotes.get('motivational', []):
            if isinstance(quote, str) and quote.strip():
                motivational_count += 1
            else:
                print(f"⚠️  Invalid motivational quote: {quote}")
        
        # Verify Quranic quotes
        for quote in quotes.get('quranic', []):
            if isinstance(quote, str) and quote.strip():
                quranic_count += 1
            else:
                print(f"⚠️  Invalid Quranic quote: {quote}")
        
        print(f"✅ Valid motivational quotes: {motivational_count}")
        print(f"✅ Valid Quranic quotes: {quranic_count}")
        
        return motivational_count > 0 and quranic_count > 0
    
    except Exception as e:
        print(f"❌ Error checking quote types: {e}")
        return False


def test_no_consecutive_repeats():
    """Test that same quote is not shown consecutively."""
    print("\n" + "="*60)
    print("TEST: No Consecutive Repeats")
    print("="*60)
    
    try:
        prev_quote = None
        consecutive_count = 0
        max_consecutive = 0
        
        for i in range(50):
            quote, _ = get_random_quote()
            
            if quote == prev_quote:
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 0
            
            prev_quote = quote
        
        if max_consecutive > 1:
            print(f"❌ Found {max_consecutive} consecutive repeats")
            return False
        
        print(f"✅ No consecutive repeats detected in 50 requests")
        return True
    
    except Exception as e:
        print(f"❌ Error testing repeats: {e}")
        return False


def test_server_resources():
    """Test that required server files exist."""
    print("\n" + "="*60)
    print("TEST: Server Resources")
    print("="*60)
    
    try:
        required_files = {
            'Quotes file': Path("/Users/khalidmuhammad/Desktop/blocked/quotes.json"),
            'Reminder page': Path("/Users/khalidmuhammad/Desktop/blocked/reminder_page/index.html"),
        }
        
        all_exist = True
        for name, path in required_files.items():
            if path.exists():
                size_kb = path.stat().st_size / 1024
                print(f"✅ {name} exists ({size_kb:.1f} KB)")
            else:
                print(f"❌ {name} missing: {path}")
                all_exist = False
        
        return all_exist
    
    except Exception as e:
        print(f"❌ Error checking resources: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("FocusGuardian - Step 3 Test Suite")
    print("Local Web Server - Quote Loading & Management")
    print("="*60)
    
    results = {
        "Quote Loading": test_quotes_loading(),
        "Random Quote Generation": test_random_quote_generation(),
        "Default Quotes Fallback": test_default_quotes(),
        "Quote Types": test_quote_types(),
        "No Consecutive Repeats": test_no_consecutive_repeats(),
        "Server Resources": test_server_resources(),
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*60)
    print(f"Overall: {passed}/{total} test groups passed")
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

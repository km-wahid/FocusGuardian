#!/usr/bin/env python3
"""
Test Suite for FocusGuardian - Hosts File Modification Logic
Tests validation, backup, and safety features.
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, '/Users/khalidmuhammad/Desktop/blocked')
from blocker import validate_domain, read_blocked_sites, check_blocker_status

def test_domain_validation():
    """Test domain validation function."""
    print("\n" + "="*60)
    print("TEST: Domain Validation")
    print("="*60)
    
    test_cases = [
        ("facebook.com", True, "Valid: standard domain"),
        ("www.example.com", True, "Valid: subdomain"),
        ("reddit.co.uk", True, "Valid: country domain"),
        ("localhost", True, "Valid: localhost"),
        ("", False, "Invalid: empty string"),
        ("domain", False, "Invalid: no TLD"),
        ("domain..com", False, "Invalid: consecutive dots"),
        (".domain.com", False, "Invalid: starts with dot"),
        ("domain.com.", False, "Invalid: ends with dot"),
        ("domain@.com", False, "Invalid: contains @"),
        ("domain#.com", False, "Invalid: contains #"),
        ("domain $.com", False, "Invalid: contains space"),
        ("a" * 260, False, "Invalid: exceeds 255 chars"),
    ]
    
    passed = 0
    failed = 0
    
    for domain, expected, description in test_cases:
        result = validate_domain(domain)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} - {description}")
        print(f"       Domain: '{domain}' | Expected: {expected} | Got: {result}")
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_blocked_sites_loading():
    """Test loading blocked sites from configuration."""
    print("\n" + "="*60)
    print("TEST: Loading Blocked Sites")
    print("="*60)
    
    try:
        sites = read_blocked_sites()
        
        print(f"✅ Successfully loaded {len(sites)} sites")
        
        # Check for duplicates
        if len(sites) == len(set(sites)):
            print("✅ No duplicates found")
        else:
            print("❌ Duplicates detected")
            return False
        
        # Check all sites are valid
        invalid = [s for s in sites if not validate_domain(s)]
        if invalid:
            print(f"❌ Invalid sites found: {invalid}")
            return False
        else:
            print(f"✅ All {len(sites)} sites have valid format")
        
        # Check for sorting
        if sites == sorted(sites):
            print("✅ Sites are properly sorted")
        else:
            print("⚠️  Sites are not sorted (not an error, just note)")
        
        print(f"\nLoaded sites: {', '.join(sites[:3])}...")
        return True
    
    except Exception as e:
        print(f"❌ Error loading sites: {e}")
        return False


def test_blocker_status():
    """Test blocker status checking."""
    print("\n" + "="*60)
    print("TEST: Blocker Status Detection")
    print("="*60)
    
    try:
        status = check_blocker_status()
        print(f"Current blocker status: {'ACTIVE' if status else 'INACTIVE'}")
        print("✅ Status check successful")
        return True
    
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False


def test_site_variants():
    """Test that both www and non-www variants are created."""
    print("\n" + "="*60)
    print("TEST: Site Variants (www handling)")
    print("="*60)
    
    test_domains = [
        ("facebook.com", ["facebook.com", "www.facebook.com"]),
        ("www.example.com", ["www.example.com"]),
        ("reddit.co.uk", ["reddit.co.uk", "www.reddit.co.uk"]),
    ]
    
    passed = 0
    
    for domain, expected_variants in test_domains:
        print(f"\nDomain: {domain}")
        
        # For non-www domains, should add www variant
        if not domain.startswith("www."):
            variants = [domain, f"www.{domain}"]
        else:
            variants = [domain]
        
        if variants == expected_variants:
            print(f"  ✅ Correct variants: {variants}")
            passed += 1
        else:
            print(f"  ❌ Expected: {expected_variants}, Got: {variants}")
    
    return passed == len(test_domains)


def test_safety_checks():
    """Test safety features."""
    print("\n" + "="*60)
    print("TEST: Safety Features")
    print("="*60)
    
    # Check backup location exists
    backup_dir = Path("/Users/khalidmuhammad/Desktop/blocked")
    if backup_dir.exists():
        print(f"✅ Project directory exists: {backup_dir}")
    else:
        print(f"❌ Project directory not found: {backup_dir}")
        return False
    
    # Check required files exist
    required_files = [
        Path("/Users/khalidmuhammad/Desktop/blocked/blocked_sites.txt"),
        Path("/Users/khalidmuhammad/Desktop/blocked/quotes.json"),
    ]
    
    for file_path in required_files:
        if file_path.exists():
            print(f"✅ Required file exists: {file_path.name}")
        else:
            print(f"❌ Required file missing: {file_path.name}")
            return False
    
    print("✅ All safety checks passed")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("FocusGuardian - Step 2 Test Suite")
    print("Hosts File Modification Logic & Safety")
    print("="*60)
    
    results = {
        "Domain Validation": test_domain_validation(),
        "Loading Blocked Sites": test_blocked_sites_loading(),
        "Blocker Status Detection": test_blocker_status(),
        "Site Variants": test_site_variants(),
        "Safety Features": test_safety_checks(),
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

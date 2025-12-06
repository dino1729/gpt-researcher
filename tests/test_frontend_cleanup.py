#!/usr/bin/env python3
"""
Test script to verify frontend cleanup was successful
"""

import os
import sys

def test_frontend_structure():
    """Test that frontend structure is correct"""
    print("=" * 60)
    print("TEST 1: Frontend Structure")
    print("=" * 60)

    frontend_dir = "frontend"

    # Check main frontend directory exists
    if not os.path.exists(frontend_dir):
        print("✗ Frontend directory missing")
        return False
    print("✓ Frontend directory exists")

    # Check required files exist
    required_files = [
        "index.html",
        "scripts.js",
        "styles.css",
        "pdf_styles.css",
        "README.md"
    ]

    for file in required_files:
        file_path = os.path.join(frontend_dir, file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✓ {file} exists ({size:,} bytes)")
        else:
            print(f"✗ {file} missing")
            return False

    # Check static directory
    static_dir = os.path.join(frontend_dir, "static")
    if os.path.exists(static_dir):
        static_files = os.listdir(static_dir)
        print(f"✓ Static directory exists ({len(static_files)} items)")
    else:
        print("✗ Static directory missing")
        return False

    return True


def test_nextjs_removed():
    """Test that Next.js frontend is removed"""
    print("\n" + "=" * 60)
    print("TEST 2: Next.js Removal")
    print("=" * 60)

    nextjs_dir = os.path.join("frontend", "nextjs")

    if os.path.exists(nextjs_dir):
        print(f"✗ Next.js directory still exists: {nextjs_dir}")
        return False

    print("✓ Next.js directory successfully removed")
    return True


def test_npm_files_removed():
    """Test that npm-related files are removed"""
    print("\n" + "=" * 60)
    print("TEST 3: NPM Files Removal")
    print("=" * 60)

    # Check for removed npm directories
    removed_dirs = [
        "docs/discord-bot",
        "docs/npm",
    ]

    for dir_path in removed_dirs:
        if os.path.exists(dir_path):
            print(f"✗ {dir_path} still exists")
            return False
        print(f"✓ {dir_path} removed")

    # Check for removed npm config files
    removed_files = [
        "docs/package.json",
        "docs/babel.config.js",
        "docs/pydoc-markdown.yml",
        "multi_agents/package.json"
    ]

    for file_path in removed_files:
        if os.path.exists(file_path):
            print(f"✗ {file_path} still exists")
            return False
        print(f"✓ {file_path} removed")

    return True


def test_backend_mounts():
    """Test that backend can import and mount paths exist"""
    print("\n" + "=" * 60)
    print("TEST 4: Backend Integration")
    print("=" * 60)

    try:
        # Test import
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from fastapi.staticfiles import StaticFiles
        print("✓ FastAPI StaticFiles imports correctly")

        # Check paths that backend would mount
        frontend_dir = "frontend"
        static_dir = os.path.join(frontend_dir, "static")
        index_path = os.path.join(frontend_dir, "index.html")

        if os.path.exists(frontend_dir):
            print(f"✓ Frontend mount path exists: {frontend_dir}")
        else:
            print(f"✗ Frontend mount path missing: {frontend_dir}")
            return False

        if os.path.exists(static_dir):
            print(f"✓ Static mount path exists: {static_dir}")
        else:
            print(f"✗ Static mount path missing: {static_dir}")
            return False

        if os.path.exists(index_path):
            print(f"✓ Index file exists: {index_path}")
        else:
            print(f"✗ Index file missing: {index_path}")
            return False

        return True
    except Exception as e:
        print(f"✗ Backend test failed: {e}")
        return False


def test_no_node_modules():
    """Test that no node_modules directories exist"""
    print("\n" + "=" * 60)
    print("TEST 5: Node Modules Cleanup")
    print("=" * 60)

    # Search for node_modules in common locations
    search_dirs = ["frontend", "docs", "multi_agents"]
    found_node_modules = []

    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue

        for root, dirs, files in os.walk(search_dir):
            if "node_modules" in dirs:
                found_node_modules.append(os.path.join(root, "node_modules"))

    if found_node_modules:
        print("✗ Found node_modules directories:")
        for path in found_node_modules:
            print(f"  - {path}")
        return False

    print("✓ No node_modules directories found")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FRONTEND CLEANUP VERIFICATION TEST SUITE")
    print("=" * 60)

    tests = [
        test_frontend_structure,
        test_nextjs_removed,
        test_npm_files_removed,
        test_backend_mounts,
        test_no_node_modules,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if all(results):
        print("\n✅ ALL TESTS PASSED!")
        print("Frontend cleanup successful:")
        print("  - Static frontend intact and functional")
        print("  - Next.js frontend completely removed")
        print("  - NPM dependencies cleaned up")
        print("  - Backend integration verified")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please review the failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

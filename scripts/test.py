#!/usr/bin/env python3
"""
Test runner script for PDF Knowledge Extractor.
"""

import sys
import unittest
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Add tests to path
tests_path = Path(__file__).parent.parent / "tests"
sys.path.insert(0, str(tests_path))


def run_tests(test_pattern=None, verbose=True):
    """Run unit tests.
    
    Args:
        test_pattern: Pattern to match test files (default: all tests)
        verbose: Whether to run in verbose mode
    """
    # Change to tests directory
    os.chdir(tests_path)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    
    if test_pattern:
        # Run specific test pattern
        suite = loader.discover('.', pattern=test_pattern)
    else:
        # Run all tests
        suite = loader.discover('.', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


def run_core_tests():
    """Run only core module tests."""
    loader = unittest.TestLoader()
    suite = loader.discover('test_core', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_utils_tests():
    """Run only utils module tests."""
    return run_tests('test_utils/test_*.py')


def run_gui_tests():
    """Run only GUI module tests."""
    return run_tests('test_gui/test_*.py')


def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run tests for PDF Knowledge Extractor')
    parser.add_argument(
        '--module',
        choices=['core', 'utils', 'gui', 'all'],
        default='all',
        help='Which module to test'
    )
    parser.add_argument(
        '--pattern',
        help='Test file pattern to match'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Run in quiet mode'
    )
    
    args = parser.parse_args()
    
    print("PDF Knowledge Extractor - Test Runner")
    print("=" * 40)
    
    success = True
    
    if args.module == 'all':
        print("Running all tests...")
        success = run_tests(args.pattern, not args.quiet)
    elif args.module == 'core':
        print("Running core module tests...")
        success = run_core_tests()
    elif args.module == 'utils':
        print("Running utils module tests...")
        success = run_utils_tests()
    elif args.module == 'gui':
        print("Running GUI module tests...")
        success = run_gui_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Development helper script for PDF Knowledge Extractor.
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SourceChangeHandler(FileSystemEventHandler):
    """Handle source code changes for auto-reload."""
    
    def __init__(self, callback):
        """Initialize handler.
        
        Args:
            callback: Function to call when files change
        """
        self.callback = callback
        self.last_modified = 0
        
    def on_modified(self, event):
        """Handle file modification."""
        if event.is_directory:
            return
            
        # Only react to Python files
        if not event.src_path.endswith('.py'):
            return
            
        # Debounce rapid changes
        current_time = time.time()
        if current_time - self.last_modified < 1.0:
            return
            
        self.last_modified = current_time
        print(f"📝 Source changed: {event.src_path}")
        self.callback()


class DevServer:
    """Development server for PDF Knowledge Extractor."""
    
    def __init__(self):
        """Initialize development server."""
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"
        self.process = None
        self.observer = None
        
    def run_app(self):
        """Run the application."""
        main_script = self.src_dir / "main.py"
        
        if not main_script.exists():
            print("❌ Main script not found")
            return
            
        # Kill existing process
        if self.process:
            self.process.terminate()
            self.process.wait()
            
        print("🚀 Starting application...")
        
        # Start new process
        self.process = subprocess.Popen([
            sys.executable, str(main_script)
        ], cwd=self.project_root)
        
    def run_tests(self):
        """Run tests."""
        test_script = self.project_root / "scripts" / "test.py"
        
        if not test_script.exists():
            print("❌ Test script not found")
            return
            
        print("🧪 Running tests...")
        
        try:
            result = subprocess.run([
                sys.executable, str(test_script), "--quiet"
            ], cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Tests passed")
            else:
                print("❌ Tests failed")
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            
    def start_file_watcher(self):
        """Start file system watcher."""
        print("👀 Starting file watcher...")
        
        handler = SourceChangeHandler(self.on_source_change)
        self.observer = Observer()
        self.observer.schedule(handler, str(self.src_dir), recursive=True)
        self.observer.start()
        
    def on_source_change(self):
        """Handle source code changes."""
        print("🔄 Reloading application...")
        self.run_app()
        
    def start_dev_mode(self):
        """Start development mode with auto-reload."""
        print("PDF Knowledge Extractor - Development Mode")
        print("=" * 45)
        print("🔧 Starting development server...")
        print("   - Auto-reload on source changes")
        print("   - Press Ctrl+C to stop")
        print()
        
        # Start file watcher
        self.start_file_watcher()
        
        # Initial app start
        self.run_app()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Stopping development server...")
            self.stop()
            
    def stop(self):
        """Stop the development server."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            
        if self.observer:
            self.observer.stop()
            self.observer.join()


def setup_dev_environment():
    """Setup development environment."""
    print("🔧 Setting up development environment...")
    
    project_root = Path(__file__).parent.parent
    
    # Install development dependencies
    dev_requirements = [
        "watchdog",  # File watching
        "black",     # Code formatting
        "flake8",    # Linting
        "pytest",    # Testing framework
    ]
    
    for package in dev_requirements:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True)
            
    print("✅ Development environment ready")


def format_code():
    """Format code with black."""
    print("🎨 Formatting code with black...")
    
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    
    try:
        subprocess.run([
            sys.executable, "-m", "black", str(src_dir)
        ], check=True)
        print("✅ Code formatted")
    except subprocess.CalledProcessError as e:
        print(f"❌ Formatting failed: {e}")
    except FileNotFoundError:
        print("❌ Black not installed. Run: pip install black")


def lint_code():
    """Lint code with flake8."""
    print("🔍 Linting code with flake8...")
    
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "flake8", str(src_dir),
            "--max-line-length=88",
            "--extend-ignore=E203,W503"
        ], cwd=project_root)
        
        if result.returncode == 0:
            print("✅ No linting issues found")
        else:
            print("❌ Linting issues found")
    except subprocess.CalledProcessError as e:
        print(f"❌ Linting failed: {e}")
    except FileNotFoundError:
        print("❌ Flake8 not installed. Run: pip install flake8")


def main():
    """Main development script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Development tools for PDF Knowledge Extractor')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Dev server
    dev_parser = subparsers.add_parser('serve', help='Start development server with auto-reload')
    
    # Setup
    setup_parser = subparsers.add_parser('setup', help='Setup development environment')
    
    # Code quality
    format_parser = subparsers.add_parser('format', help='Format code with black')
    lint_parser = subparsers.add_parser('lint', help='Lint code with flake8')
    
    # Testing
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--watch', action='store_true', help='Watch for changes and re-run tests')
    
    args = parser.parse_args()
    
    if args.command == 'serve':
        server = DevServer()
        server.start_dev_mode()
    elif args.command == 'setup':
        setup_dev_environment()
    elif args.command == 'format':
        format_code()
    elif args.command == 'lint':
        lint_code()
    elif args.command == 'test':
        if args.watch:
            # Watch mode for tests
            def run_tests_callback():
                server = DevServer()
                server.run_tests()
                
            handler = SourceChangeHandler(run_tests_callback)
            observer = Observer()
            observer.schedule(handler, str(Path(__file__).parent.parent / "src"), recursive=True)
            observer.schedule(handler, str(Path(__file__).parent.parent / "tests"), recursive=True)
            observer.start()
            
            print("🧪 Test watcher started. Press Ctrl+C to stop.")
            run_tests_callback()  # Initial run
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                observer.join()
        else:
            server = DevServer()
            server.run_tests()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
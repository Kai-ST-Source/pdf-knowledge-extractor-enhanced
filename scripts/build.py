#!/usr/bin/env python3
"""
Build script for PDF Knowledge Extractor.
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path


class BuildManager:
    """Manage the build process."""
    
    def __init__(self):
        """Initialize build manager."""
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
    def clean(self):
        """Clean build artifacts."""
        print("🧹 Cleaning build artifacts...")
        
        # Remove dist and build directories
        for directory in [self.dist_dir, self.build_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"   Removed {directory}")
        
        # Remove __pycache__ directories
        for pycache in self.project_root.rglob("__pycache__"):
            shutil.rmtree(pycache)
            
        # Remove .pyc files
        for pyc_file in self.project_root.rglob("*.pyc"):
            pyc_file.unlink()
            
        print("✅ Clean completed")
        
    def install_dependencies(self):
        """Install project dependencies."""
        print("📦 Installing dependencies...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
            
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, cwd=self.project_root)
            print("✅ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
            
    def run_tests(self):
        """Run unit tests."""
        print("🧪 Running tests...")
        
        test_script = self.project_root / "scripts" / "test.py"
        if not test_script.exists():
            print("❌ Test script not found")
            return False
            
        try:
            result = subprocess.run([
                sys.executable, str(test_script), "--quiet"
            ], cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ All tests passed")
                return True
            else:
                print("❌ Some tests failed")
                return False
        except subprocess.CalledProcessError as e:
            print(f"❌ Test execution failed: {e}")
            return False
            
    def build_executable(self):
        """Build executable using PyInstaller."""
        print("🔨 Building executable...")
        
        # Ensure PyInstaller is available
        try:
            import PyInstaller
        except ImportError:
            print("❌ PyInstaller not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            
        # Main script path
        main_script = self.src_dir / "main.py"
        if not main_script.exists():
            print("❌ Main script not found")
            return False
            
        # Build command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--name", "PDF Knowledge Extractor",
            "--onedir",
            "--windowed" if sys.platform == "darwin" else "--console",
            "--add-data", f"{self.project_root / 'config.json'}:.",
            "--hidden-import", "tkinter",
            "--hidden-import", "PIL._tkinter_finder",
            str(main_script)
        ]
        
        # Add icon
        icon_path = self.project_root / "docs" / "icon.icns"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])
        else:
            print("⚠️  App icon not found. Run 'python3 scripts/create_icon.py' to create it.")
        
        try:
            subprocess.run(cmd, check=True, cwd=self.project_root)
            print("✅ Executable built successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            return False
            
    def create_macos_app(self):
        """Create macOS application bundle."""
        if sys.platform != "darwin":
            print("⚠️  macOS app creation only available on macOS")
            return True
            
        print("🍎 Creating macOS application bundle...")
        
        app_name = "PDF Knowledge Extractor"
        dist_app = self.dist_dir / f"{app_name}.app"
        
        if not dist_app.exists():
            print("❌ Built app not found")
            return False
            
        # Copy to Applications if requested
        try:
            applications_dir = Path("/Applications")
            target_app = applications_dir / f"{app_name}.app"
            
            if target_app.exists():
                shutil.rmtree(target_app)
                
            shutil.copytree(dist_app, target_app)
            print(f"✅ App installed to {target_app}")
            return True
        except Exception as e:
            print(f"❌ Failed to install app: {e}")
            return False
            
    def package_release(self):
        """Package release artifacts."""
        print("📦 Packaging release...")
        
        # Create release directory
        release_dir = self.project_root / "release"
        release_dir.mkdir(exist_ok=True)
        
        # Package based on platform
        if sys.platform == "darwin":
            # Create DMG for macOS
            app_name = "PDF Knowledge Extractor"
            dist_app = self.dist_dir / f"{app_name}.app"
            
            if dist_app.exists():
                dmg_name = f"{app_name.replace(' ', '_')}_macOS.dmg"
                dmg_path = release_dir / dmg_name
                
                try:
                    # Simple DMG creation (requires hdiutil)
                    temp_dmg = release_dir / "temp.dmg"
                    
                    subprocess.run([
                        "hdiutil", "create", "-volname", app_name,
                        "-srcfolder", str(dist_app),
                        "-ov", "-format", "UDZO",
                        str(dmg_path)
                    ], check=True)
                    
                    print(f"✅ DMG created: {dmg_path}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ DMG creation failed: {e}")
                    # Fallback: create ZIP
                    shutil.make_archive(
                        str(release_dir / app_name.replace(' ', '_')),
                        'zip',
                        self.dist_dir,
                        f"{app_name}.app"
                    )
                    print(f"✅ ZIP created as fallback")
        else:
            # Create ZIP for other platforms
            shutil.make_archive(
                str(release_dir / "PDF_Knowledge_Extractor"),
                'zip',
                self.dist_dir
            )
            print("✅ ZIP package created")
            
        return True


def main():
    """Main build function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build PDF Knowledge Extractor')
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build artifacts before building'
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip running tests'
    )
    parser.add_argument(
        '--skip-deps',
        action='store_true',
        help='Skip installing dependencies'
    )
    parser.add_argument(
        '--install-app',
        action='store_true',
        help='Install app to /Applications (macOS only)'
    )
    parser.add_argument(
        '--package',
        action='store_true',
        help='Package release artifacts'
    )
    
    args = parser.parse_args()
    
    builder = BuildManager()
    
    print("PDF Knowledge Extractor - Build Script")
    print("=" * 40)
    
    # Clean if requested
    if args.clean:
        builder.clean()
        
    # Install dependencies
    if not args.skip_deps:
        if not builder.install_dependencies():
            sys.exit(1)
            
    # Run tests
    if not args.skip_tests:
        if not builder.run_tests():
            print("❌ Tests failed, stopping build")
            sys.exit(1)
            
    # Build executable
    if not builder.build_executable():
        sys.exit(1)
        
    # Install app if requested
    if args.install_app:
        if not builder.create_macos_app():
            sys.exit(1)
            
    # Package release
    if args.package:
        if not builder.package_release():
            sys.exit(1)
            
    print("\n🎉 Build completed successfully!")


if __name__ == '__main__':
    main()
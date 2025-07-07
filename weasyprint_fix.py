#!/usr/bin/env python3
"""
WeasyPrint Fix Utility
This script helps diagnose and fix WeasyPrint issues on servers.
"""

import os
import sys
import subprocess
import platform

def check_system_info():
    """Check system information"""
    print("=== System Information ===")
    print(f"Platform: {platform.platform()}")
    print(f"Python Version: {sys.version}")
    print(f"Architecture: {platform.architecture()}")
    print()

def check_weasyprint_installation():
    """Check WeasyPrint installation"""
    print("=== WeasyPrint Installation Check ===")
    try:
        import weasyprint
        print(f"WeasyPrint Version: {weasyprint.__version__}")
        print("✓ WeasyPrint is installed")
    except ImportError as e:
        print(f"✗ WeasyPrint not installed: {e}")
        return False
    except Exception as e:
        print(f"✗ WeasyPrint error: {e}")
        return False
    return True

def check_system_libraries():
    """Check for required system libraries"""
    print("=== System Libraries Check ===")
    
    # Common library paths
    lib_paths = [
        '/usr/lib',
        '/usr/lib64',
        '/usr/local/lib',
        '/usr/local/lib64',
        '/opt/alt/python313/lib64',
    ]
    
    required_libs = [
        'libpango-1.0.so.0',
        'libcairo.so.2',
        'libgdk_pixbuf-2.0.so.0',
        'libgobject-2.0.so.0',
        'libglib-2.0.so.0',
    ]
    
    for lib in required_libs:
        found = False
        for path in lib_paths:
            lib_path = os.path.join(path, lib)
            if os.path.exists(lib_path):
                print(f"✓ {lib} found at {lib_path}")
                found = True
                break
        if not found:
            print(f"✗ {lib} not found")
    
    print()

def test_weasyprint_generation():
    """Test WeasyPrint PDF generation"""
    print("=== WeasyPrint PDF Generation Test ===")
    
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Simple HTML test
        html_content = """
        <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; }
                    h1 { color: blue; }
                </style>
            </head>
            <body>
                <h1>Test PDF Generation</h1>
                <p>This is a test of WeasyPrint PDF generation.</p>
            </body>
        </html>
        """
        
        # Try to generate PDF
        font_config = FontConfiguration()
        html = HTML(string=html_content)
        css = CSS(string='', font_config=font_config)
        
        pdf_bytes = html.write_pdf(stylesheets=[css], font_config=font_config)
        
        if pdf_bytes:
            print("✓ WeasyPrint PDF generation successful")
            print(f"  Generated {len(pdf_bytes)} bytes")
            return True
        else:
            print("✗ WeasyPrint PDF generation failed - no output")
            return False
            
    except Exception as e:
        print(f"✗ WeasyPrint PDF generation failed: {e}")
        return False

def suggest_fixes():
    """Suggest fixes for common WeasyPrint issues"""
    print("=== Suggested Fixes ===")
    
    print("1. Install system dependencies:")
    print("   Ubuntu/Debian:")
    print("   sudo apt-get install libpango1.0-dev libcairo2-dev libgdk-pixbuf2.0-dev")
    print()
    print("   CentOS/RHEL:")
    print("   sudo yum install pango-devel cairo-devel gdk-pixbuf2-devel")
    print()
    print("   cPanel/Shared Hosting:")
    print("   Contact your hosting provider to install the required libraries")
    print()
    
    print("2. Alternative: Use ReportLab instead of WeasyPrint")
    print("   - ReportLab is more reliable on shared hosting")
    print("   - No system dependencies required")
    print("   - Already implemented in the application")
    print()
    
    print("3. Environment variables to try:")
    print("   export LD_LIBRARY_PATH=/usr/lib64:/usr/lib:$LD_LIBRARY_PATH")
    print("   export PKG_CONFIG_PATH=/usr/lib64/pkgconfig:/usr/lib/pkgconfig:$PKG_CONFIG_PATH")
    print()

def main():
    """Main function"""
    print("WeasyPrint Diagnostic Tool")
    print("=" * 50)
    print()
    
    check_system_info()
    
    if not check_weasyprint_installation():
        print("WeasyPrint is not properly installed.")
        suggest_fixes()
        return
    
    check_system_libraries()
    
    if not test_weasyprint_generation():
        print("WeasyPrint PDF generation is failing.")
        suggest_fixes()
        return
    
    print("✓ WeasyPrint appears to be working correctly!")

if __name__ == "__main__":
    main() 
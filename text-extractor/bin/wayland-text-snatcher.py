#!/usr/bin/env python3
import os
import sys
import signal
import subprocess
import tempfile
from PIL import Image
import pytesseract

class TextExtractor:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle termination signals"""
        self.running = False
        print("\nShutting down gracefully...")
        sys.exit(0)
        
    def check_dependencies(self):
        """Verify required tools are installed"""
        required = ['grim', 'slurp', 'wl-copy', 'tesseract']
        missing = []
        
        for tool in required:
            try:
                subprocess.run(['which', tool], check=True, 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                missing.append(tool)
                
        if missing:
            print(f"Missing required tools: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
            
    def capture_region(self):
        """Capture screen region using grim/slurp"""
        try:
            # Get selection coordinates
            slurp = subprocess.run(['slurp'], capture_output=True, text=True)
            if slurp.returncode != 0:
                return None
                
            # Take screenshot
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                subprocess.run(['grim', '-g', slurp.stdout.strip(), tmp.name], check=True)
                return tmp.name
                
        except subprocess.CalledProcessError as e:
            print(f"Capture failed: {e}", file=sys.stderr)
            return None
            
    def extract_text(self, image_path):
        """Perform OCR on captured image"""
        try:
            with Image.open(image_path) as img:
                text = pytesseract.image_to_string(img)
                return text.strip()
        except Exception as e:
            print(f"OCR failed: {e}", file=sys.stderr)
            return None
            
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            subprocess.run(['wl-copy'], input=text.encode('utf-8'), check=True)
            print("✓ Text copied to clipboard!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Clipboard error: {e}", file=sys.stderr)
            return False
            
    def cleanup(self, file_path):
        """Remove temporary files"""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Cleanup error: {e}", file=sys.stderr)
            
    def perform_ocr_operation(self):
        """Complete OCR workflow"""
        screenshot_path = None
        try:
            screenshot_path = self.capture_region()
            if not screenshot_path:
                return False
                
            text = self.extract_text(screenshot_path)
            if not text:
                return False
                
            return self.copy_to_clipboard(text)
        finally:
            self.cleanup(screenshot_path)
            
    def run(self, immediate=False):
        """Main execution"""
        self.check_dependencies()
        
        if immediate:
            return self.perform_ocr_operation()
        else:
            print("Ready for OCR (Configure system hotkey to run with --capture flag)")
            while self.running:
                try:
                    input()  # Keep alive waiting for signals
                except (EOFError, KeyboardInterrupt):
                    break

if __name__ == '__main__':
    if os.getenv('XDG_SESSION_TYPE') != 'wayland':
        print("Error: This requires a Wayland session", file=sys.stderr)
        sys.exit(1)
        
    extractor = TextExtractor()
    
    # Handle --capture flag
    if '--capture' in sys.argv:
        sys.exit(0 if extractor.run(immediate=True) else 1)
    else:
        extractor.run()

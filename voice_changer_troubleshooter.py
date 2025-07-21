#!/usr/bin/env python3
"""
Voice Changer Troubleshooter
Comprehensive troubleshooting for voice changer after killing all instances
"""

import os
import sys
import json
import time
import subprocess
import psutil
import requests
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceChangerTroubleshooter:
    """Troubleshoots voice changer issues"""
    
    def __init__(self):
        self.voice_changer_dir = Path("voice-changer")
        self.server_dir = self.voice_changer_dir / "server"
        self.logs_dir = self.voice_changer_dir / "logs"
        self.tmp_dir = self.voice_changer_dir / "tmp_dir"
        
        # Voice changer ports
        self.ports = [8080, 8081, 8082, 8083]
        
        # Process names to check
        self.process_names = [
            "python", "vcclient", "voice-changer", "MMVCServerSIO"
        ]
    
    def check_system_status(self):
        """Check overall system status"""
        print("🔍 Checking system status...")
        
        # Check running processes
        running_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                for process_name in self.process_names:
                    if process_name.lower() in proc.info['name'].lower():
                        running_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        print(f"📊 Running voice changer processes: {len(running_processes)}")
        for proc in running_processes:
            print(f"   PID {proc['pid']}: {proc['name']}")
        
        # Check port usage
        print("\n🌐 Checking port usage...")
        for port in self.ports:
            try:
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                if str(port) in result.stdout:
                    print(f"   Port {port}: IN USE")
                else:
                    print(f"   Port {port}: AVAILABLE")
            except Exception as e:
                print(f"   Port {port}: ERROR - {e}")
        
        return len(running_processes) == 0
    
    def clean_temporary_files(self):
        """Clean temporary files and logs"""
        print("\n🧹 Cleaning temporary files...")
        
        # Clean tmp directory
        if self.tmp_dir.exists():
            try:
                for file in self.tmp_dir.glob("*"):
                    if file.is_file():
                        file.unlink()
                        print(f"   Deleted: {file}")
            except Exception as e:
                print(f"   Error cleaning tmp_dir: {e}")
        
        # Clean logs
        if self.logs_dir.exists():
            try:
                for file in self.logs_dir.glob("*.log"):
                    if file.stat().st_size > 10 * 1024 * 1024:  # Larger than 10MB
                        file.unlink()
                        print(f"   Deleted large log: {file}")
            except Exception as e:
                print(f"   Error cleaning logs: {e}")
        
        # Clean server logs
        server_logs = self.server_dir / "logs"
        if server_logs.exists():
            try:
                for file in server_logs.glob("*.log"):
                    if file.stat().st_size > 10 * 1024 * 1024:  # Larger than 10MB
                        file.unlink()
                        print(f"   Deleted large server log: {file}")
            except Exception as e:
                print(f"   Error cleaning server logs: {e}")
    
    def check_voice_changer_installation(self):
        """Check voice changer installation"""
        print("\n📦 Checking voice changer installation...")
        
        # Check directories
        required_dirs = [
            self.voice_changer_dir,
            self.server_dir,
            self.server_dir / "voice_changer",
            self.server_dir / "model_dir"
        ]
        
        for dir_path in required_dirs:
            if dir_path.exists():
                print(f"   ✅ {dir_path.name}: EXISTS")
            else:
                print(f"   ❌ {dir_path.name}: MISSING")
        
        # Check key files
        key_files = [
            self.server_dir / "requirements.txt",
            self.server_dir / "MMVCServerSIO.py",
            self.server_dir / "const.py"
        ]
        
        for file_path in key_files:
            if file_path.exists():
                print(f"   ✅ {file_path.name}: EXISTS")
            else:
                print(f"   ❌ {file_path.name}: MISSING")
    
    def check_python_dependencies(self):
        """Check Python dependencies"""
        print("\n🐍 Checking Python dependencies...")
        
        required_packages = [
            "torch", "torchaudio", "onnxruntime", "numpy", "scipy",
            "librosa", "soundfile", "websockets", "fastapi", "uvicorn"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✅ {package}: INSTALLED")
            except ImportError:
                print(f"   ❌ {package}: MISSING")
    
    def start_voice_changer_server(self):
        """Start the voice changer server"""
        print("\n🚀 Starting voice changer server...")
        
        if not self.server_dir.exists():
            print("❌ Server directory not found")
            return False
        
        try:
            # Change to server directory
            os.chdir(self.server_dir)
            
            # Check if requirements are installed
            print("   Installing/updating requirements...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         capture_output=True, text=True)
            
            # Start the server
            print("   Starting MMVCServerSIO...")
            server_process = subprocess.Popen([
                sys.executable, "MMVCServerSIO.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if process is still running
            if server_process.poll() is None:
                print("   ✅ Server started successfully")
                return server_process
            else:
                stdout, stderr = server_process.communicate()
                print(f"   ❌ Server failed to start")
                print(f"   STDOUT: {stdout}")
                print(f"   STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error starting server: {e}")
            return False
    
    def test_server_connection(self, timeout=10):
        """Test server connection"""
        print("\n🔗 Testing server connection...")
        
        for port in self.ports:
            try:
                response = requests.get(f"http://localhost:{port}/", timeout=timeout)
                if response.status_code == 200:
                    print(f"   ✅ Port {port}: SERVER RESPONDING")
                    return port
                else:
                    print(f"   ⚠️ Port {port}: HTTP {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"   ❌ Port {port}: NO RESPONSE")
        
        return None
    
    def check_voice_changer_client(self):
        """Check voice changer client"""
        print("\n🎤 Checking voice changer client...")
        
        client_dir = self.voice_changer_dir / "client"
        if not client_dir.exists():
            print("   ❌ Client directory not found")
            return False
        
        # Check for client files
        client_files = list(client_dir.glob("*.html"))
        if client_files:
            print(f"   ✅ Found {len(client_files)} client files")
            for file in client_files[:3]:  # Show first 3
                print(f"      - {file.name}")
            return True
        else:
            print("   ❌ No client files found")
            return False
    
    def create_startup_script(self):
        """Create a startup script for voice changer"""
        print("\n📝 Creating startup script...")
        
        startup_script = '''@echo off
echo Starting Voice Changer Server...
cd voice-changer\\server

echo Installing requirements...
python -m pip install -r requirements.txt

echo Starting server...
python MMVCServerSIO.py

pause
'''
        
        script_path = Path("start_voice_changer.bat")
        with open(script_path, 'w') as f:
            f.write(startup_script)
        
        print(f"   ✅ Created: {script_path}")
        return script_path
    
    def create_troubleshooting_report(self):
        """Create a troubleshooting report"""
        print("\n📄 Creating troubleshooting report...")
        
        report = f"""
# Voice Changer Troubleshooting Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## System Status
- Voice Changer Directory: {'EXISTS' if self.voice_changer_dir.exists() else 'MISSING'}
- Server Directory: {'EXISTS' if self.server_dir.exists() else 'MISSING'}
- Logs Directory: {'EXISTS' if self.logs_dir.exists() else 'MISSING'}

## Process Status
- Running Processes: {len([p for p in psutil.process_iter() if any(name in p.name().lower() for name in self.process_names)])}

## Port Status
"""
        
        for port in self.ports:
            try:
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                if str(port) in result.stdout:
                    report += f"- Port {port}: IN USE\n"
                else:
                    report += f"- Port {port}: AVAILABLE\n"
            except:
                report += f"- Port {port}: UNKNOWN\n"
        
        report += """
## Recommendations
1. Run the startup script: start_voice_changer.bat
2. Check the logs in voice-changer/logs/
3. Ensure no other applications are using ports 8080-8083
4. Restart the system if issues persist

## Support
- Check voice-changer/README.md for documentation
- Look for error messages in the logs
- Ensure all Python dependencies are installed
"""
        
        report_path = Path("voice_changer_troubleshooting_report.md")
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"   ✅ Created: {report_path}")
        return report_path
    
    def run_complete_troubleshooting(self):
        """Run complete troubleshooting process"""
        print("🎯 Voice Changer Troubleshooting")
        print("=" * 50)
        
        # Step 1: Check system status
        system_clean = self.check_system_status()
        
        # Step 2: Clean temporary files
        self.clean_temporary_files()
        
        # Step 3: Check installation
        self.check_voice_changer_installation()
        
        # Step 4: Check dependencies
        self.check_python_dependencies()
        
        # Step 5: Check client
        client_ok = self.check_voice_changer_client()
        
        # Step 6: Create startup script
        startup_script = self.create_startup_script()
        
        # Step 7: Create report
        report = self.create_troubleshooting_report()
        
        print("\n" + "=" * 50)
        print("🎉 Troubleshooting Complete!")
        print("\nNext Steps:")
        print("1. Run the startup script:")
        print(f"   {startup_script}")
        print("2. Check the troubleshooting report:")
        print(f"   {report}")
        print("3. If the server starts, open your browser to:")
        print("   http://localhost:8080")
        print("\nIf you encounter issues:")
        print("- Check the logs in voice-changer/logs/")
        print("- Ensure no other applications are using the ports")
        print("- Restart your system if problems persist")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice Changer Troubleshooter")
    parser.add_argument("--start-server", action="store_true", help="Start the voice changer server")
    parser.add_argument("--test-connection", action="store_true", help="Test server connection")
    parser.add_argument("--clean", action="store_true", help="Clean temporary files only")
    
    args = parser.parse_args()
    
    troubleshooter = VoiceChangerTroubleshooter()
    
    if args.clean:
        # Just clean files
        troubleshooter.clean_temporary_files()
        print("✅ Cleaning complete")
        
    elif args.start_server:
        # Start server
        server_process = troubleshooter.start_voice_changer_server()
        if server_process:
            print("✅ Server started successfully")
            print("Open http://localhost:8080 in your browser")
        else:
            print("❌ Failed to start server")
            
    elif args.test_connection:
        # Test connection
        port = troubleshooter.test_server_connection()
        if port:
            print(f"✅ Server responding on port {port}")
        else:
            print("❌ No server responding")
            
    else:
        # Run complete troubleshooting
        troubleshooter.run_complete_troubleshooting()

if __name__ == "__main__":
    main() 
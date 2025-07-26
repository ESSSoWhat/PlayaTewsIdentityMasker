#!/usr/bin/env python3
"""
Quick status check for the PlayaTewsIdentityMasker app
"""

import time
import psutil
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_processes():
    """Check for running Python processes"""
    logger.info("🔍 Checking for running Python processes...")
    
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'PlayaTewsIdentityMasker' in cmdline or 'main.py' in cmdline:
                    python_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return python_processes

def main():
    """Check app status"""
    logger.info("🚀 Checking PlayaTewsIdentityMasker App Status...")
    
    # Check for running processes
    processes = check_python_processes()
    
    if processes:
        logger.info(f"✅ Found {len(processes)} running Python process(es):")
        for proc in processes:
            logger.info(f"   PID: {proc['pid']} | Name: {proc['name']}")
            logger.info(f"   Command: {proc['cmdline'][:100]}...")
        logger.info("🎉 App appears to be running successfully!")
    else:
        logger.warning("⚠️  No PlayaTewsIdentityMasker processes found running")
        logger.info("💡 Try running: python main.py run PlayaTewsIdentityMaskerOptimized")
    
    # Check system resources
    logger.info("\n📊 System Resources:")
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    logger.info(f"   CPU Usage: {cpu_percent:.1f}%")
    logger.info(f"   Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)")
    
    logger.info("\n✨ Status check completed!")

if __name__ == "__main__":
    main() 
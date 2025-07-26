#!/usr/bin/env python3
"""
Simple test to check backend component creation and activation
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_simple_backend():
    """Simple test of backend creation"""
    print("Testing simple backend creation...")
    
    try:
        from apps.PlayaTewsIdentityMasker import backend
        print("✅ Backend module imported")
        
        # Create minimal backend infrastructure
        settings_dirpath = Path("settings")
        settings_dirpath.mkdir(exist_ok=True)
        
        backend_db = backend.BackendDB(settings_dirpath / 'states.dat')
        backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)
        reemit_frame_signal = backend.BackendSignal()
        
        print("✅ Backend infrastructure created")
        
        # Create a simple backend connection
        bc_out = backend.BackendConnection()
        
        # Try to create a simple backend component
        from apps.PlayaTewsIdentityMasker.backend.FileSource import FileSource
        
        file_source = FileSource(
            weak_heap=backend_weak_heap, 
            reemit_frame_signal=reemit_frame_signal, 
            bc_out=bc_out, 
            backend_db=backend_db
        )
        
        print("✅ FileSource backend created")
        print(f"  - Initial state: {'Started' if file_source.is_started() else 'Stopped'}")
        
        # Try to start it
        if file_source.is_stopped():
            print("  - Attempting to start...")
            file_source.start()
            
            # Process messages
            backend_db.process_messages()
            file_source.process_messages()
            
            print(f"  - State after start: {'Started' if file_source.is_started() else 'Stopped'}")
            print(f"  - Is starting: {file_source.is_starting()}")
            print(f"  - Is stopping: {file_source.is_stopping()}")
            print(f"  - Is busy: {file_source.is_busy()}")
        
        print("✅ Simple backend test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_backend() 
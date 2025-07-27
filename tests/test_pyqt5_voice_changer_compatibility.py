#!/usr/bin/env python3
"""
PyQt5 Voice Changer Compatibility Test
Verifies that the voice changer works correctly with PyQt5
"""

import sys
import os
from pathlib import Path

def test_pyqt5_imports():
    """Test that PyQt5 imports work correctly"""
    print("🔍 Testing PyQt5 imports...")
    
    try:
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
        from PyQt5.QtCore import Qt, pyqtSignal
        from PyQt5.QtGui import QFont, QPalette, QColor
        print("✅ Core PyQt5 imports successful")
        return True
    except ImportError as e:
        print(f"❌ PyQt5 import failed: {e}")
        return False

def test_voice_changer_imports():
    """Test voice changer component imports"""
    print("\n🎤 Testing voice changer imports...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from apps.PlayaTewsIdentityMasker.ui.QVoiceChanger import QVoiceChanger
        print("✅ QVoiceChanger UI import successful")
        
        from apps.PlayaTewsIdentityMasker.backend.VoiceChanger import VoiceChanger
        print("✅ VoiceChanger backend import successful")
        
        return True
    except ImportError as e:
        print(f"❌ Voice changer import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Voice changer error: {e}")
        return False

def test_pyqt5_enum_usage():
    """Test PyQt5 enum usage patterns"""
    print("\n🔢 Testing PyQt5 enum usage...")
    
    try:
        from PyQt5.QtCore import Qt
        
        # Test direct enum access (PyQt5 style)
        alignment_center = Qt.AlignCenter
        alignment_left = Qt.AlignLeft
        checked_state = Qt.Checked
        horizontal_orientation = Qt.Horizontal
        
        print("✅ PyQt5 enum access working correctly")
        print(f"   - AlignCenter: {alignment_center}")
        print(f"   - AlignLeft: {alignment_left}")
        print(f"   - Checked: {checked_state}")
        print(f"   - Horizontal: {horizontal_orientation}")
        
        # Verify PyQt6-style enums are NOT available
        try:
            alignment_flag = Qt.AlignmentFlag
            print("⚠️  PyQt6-style AlignmentFlag detected (unexpected)")
            return False
        except AttributeError:
            print("✅ PyQt6-style enums correctly absent")
        
        return True
    except Exception as e:
        print(f"❌ Enum usage test failed: {e}")
        return False

def test_widget_creation():
    """Test basic widget creation with PyQt5"""
    print("\n🎨 Testing widget creation...")
    
    try:
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                                     QSlider, QComboBox, QPushButton)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        # Create test widget
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Test label with PyQt5 alignment
        label = QLabel("Test Voice Changer")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)  # PyQt5 style enum
        
        # Test slider with PyQt5 orientation
        slider = QSlider()
        slider.setOrientation(Qt.Horizontal)  # PyQt5 style enum
        slider.setRange(0, 100)
        
        # Test combo box
        combo = QComboBox()
        combo.addItem("None")
        combo.addItem("Pitch Shift")
        combo.addItem("Robot Effect")
        
        # Test button
        button = QPushButton("Apply Effect")
        
        # Add to layout
        layout.addWidget(label)
        layout.addWidget(slider)
        layout.addWidget(combo)
        layout.addWidget(button)
        widget.setLayout(layout)
        
        print("✅ Widget creation successful")
        print("✅ PyQt5 enum usage in widgets working")
        return True
        
    except Exception as e:
        print(f"❌ Widget creation failed: {e}")
        return False

def test_signal_slot_compatibility():
    """Test signal/slot connections"""
    print("\n📡 Testing signal/slot connections...")
    
    try:
        from PyQt5.QtWidgets import QPushButton, QSlider
        from PyQt5.QtCore import QObject, pyqtSignal
        
        class TestSignals(QObject):
            test_signal = pyqtSignal(int)
            
            def __init__(self):
                super().__init__()
                self.signal_received = False
                self.received_value = None
            
            def on_signal(self, value):
                self.signal_received = True
                self.received_value = value
        
        # Test signal/slot connection
        test_obj = TestSignals()
        test_obj.test_signal.connect(test_obj.on_signal)
        test_obj.test_signal.emit(42)
        
        if test_obj.signal_received and test_obj.received_value == 42:
            print("✅ Signal/slot connections working")
            return True
        else:
            print("❌ Signal/slot test failed")
            return False
            
    except Exception as e:
        print(f"❌ Signal/slot test error: {e}")
        return False

def test_voice_effects_enum():
    """Test voice effects enumeration"""
    print("\n🎭 Testing voice effects enumeration...")
    
    try:
        from apps.PlayaTewsIdentityMasker.backend.VoiceChanger import VoiceEffectType
        
        effects = [
            VoiceEffectType.NONE,
            VoiceEffectType.PITCH_SHIFT,
            VoiceEffectType.FORMANT_SHIFT,
            VoiceEffectType.ROBOT,
            VoiceEffectType.HELIUM,
            VoiceEffectType.DEEP,
            VoiceEffectType.ECHO,
            VoiceEffectType.REVERB,
            VoiceEffectType.CHORUS,
            VoiceEffectType.DISTORTION,
            VoiceEffectType.AUTOTUNE
        ]
        
        print(f"✅ Voice effects enumeration working ({len(effects)} effects)")
        for effect in effects:
            print(f"   - {effect.name}: {effect.value}")
            
        return True
        
    except Exception as e:
        print(f"❌ Voice effects enum test failed: {e}")
        return False

def test_requirements_consistency():
    """Test that requirements files specify PyQt5"""
    print("\n📋 Testing requirements consistency...")
    
    req_files = [
        'requirements-unified.txt',
        'requirements_minimal.txt'
    ]
    
    pyqt5_found = 0
    pyqt6_found = 0
    
    for req_file in req_files:
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                content = f.read()
                if 'PyQt5' in content and 'PyQt5>=' in content:
                    pyqt5_found += 1
                    print(f"✅ {req_file}: PyQt5 specified")
                elif 'PyQt6' in content and 'PyQt6>=' in content:
                    pyqt6_found += 1
                    print(f"⚠️  {req_file}: PyQt6 specified (should be PyQt5)")
    
    if pyqt5_found > 0 and pyqt6_found == 0:
        print("✅ Requirements files consistent with PyQt5")
        return True
    else:
        print("❌ Requirements files inconsistent")
        return False

def run_compatibility_summary():
    """Run all compatibility tests and provide summary"""
    print("🧪 PyQt5 Voice Changer Compatibility Test Suite")
    print("=" * 60)
    
    tests = [
        ("PyQt5 Core Imports", test_pyqt5_imports),
        ("Voice Changer Imports", test_voice_changer_imports),
        ("PyQt5 Enum Usage", test_pyqt5_enum_usage),
        ("Widget Creation", test_widget_creation),
        ("Signal/Slot Connections", test_signal_slot_compatibility),
        ("Voice Effects Enum", test_voice_effects_enum),
        ("Requirements Consistency", test_requirements_consistency)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed / (passed + failed) * 100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Voice changer is fully compatible with PyQt5")
        print("✅ Ready for deployment in PyQt5 environment")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        print("❌ Additional work needed for full PyQt5 compatibility")
        return False

if __name__ == '__main__':
    success = run_compatibility_summary()
    sys.exit(0 if success else 1)
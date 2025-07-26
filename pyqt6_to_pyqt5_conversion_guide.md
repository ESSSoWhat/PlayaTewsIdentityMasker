# PyQt6 to PyQt5 Conversion Guide for Voice Changer

## 🔄 CONVERSION STRATEGY

Instead of migrating the existing PyQt5 components to PyQt6, this guide provides **PyQt5 alternatives** for the PyQt6 voice changer implementation, ensuring compatibility with the existing PyQt5 ecosystem.

## Current PyQt6 Components Requiring Conversion

### 1. **Voice Changer UI** (`QVoiceChanger.py`)
- **Current**: Uses PyQt6 imports and enums
- **Target**: Convert to PyQt5 equivalents
- **Complexity**: Medium (enum changes required)

### 2. **Core Framework** (`xlib/qt/__init__.py`)
- **Current**: PyQt6 foundation
- **Target**: PyQt5 foundation with compatibility layer
- **Complexity**: High (affects entire framework)

### 3. **Requirements** (`requirements-unified.txt`)
- **Current**: PyQt6>=6.4.0,<6.7.0
- **Target**: PyQt5>=5.15.0,<5.16.0
- **Complexity**: Low (simple replacement)

## PyQt6 → PyQt5 API Conversion Reference

### Import Statement Changes

#### ✅ Direct Replacements (No Code Changes)
```python
# These imports work identically in both PyQt5 and PyQt6
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

# ↓ CONVERT TO ↓

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
```

#### ⚠️ Enum Access Changes Required
```python
# PyQt6 (Current - PROBLEMATIC):
title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

# PyQt5 (Target - COMPATIBLE):
title_label.setAlignment(Qt.AlignCenter)
```

### Complete Enum Conversion Table

| PyQt6 Enum | PyQt5 Enum | Usage Context |
|------------|------------|---------------|
| `Qt.AlignmentFlag.AlignCenter` | `Qt.AlignCenter` | Widget alignment |
| `Qt.AlignmentFlag.AlignLeft` | `Qt.AlignLeft` | Widget alignment |
| `Qt.AlignmentFlag.AlignRight` | `Qt.AlignRight` | Widget alignment |
| `Qt.AlignmentFlag.AlignTop` | `Qt.AlignTop` | Widget alignment |
| `Qt.AlignmentFlag.AlignBottom` | `Qt.AlignBottom` | Widget alignment |
| `Qt.CheckState.Checked` | `Qt.Checked` | Checkbox states |
| `Qt.CheckState.Unchecked` | `Qt.Unchecked` | Checkbox states |
| `Qt.MouseButton.LeftButton` | `Qt.LeftButton` | Mouse events |
| `Qt.MouseButton.RightButton` | `Qt.RightButton` | Mouse events |
| `Qt.Key.Key_Enter` | `Qt.Key_Enter` | Keyboard events |
| `Qt.Orientation.Horizontal` | `Qt.Horizontal` | Slider orientation |
| `Qt.Orientation.Vertical` | `Qt.Vertical` | Slider orientation |

## Detailed File Conversion Plans

### 1. Requirements File Update

#### File: `requirements-unified.txt`
```diff
# GUI Framework (Updated from PyQt5 to PyQt6)
- PyQt6>=6.4.0,<6.7.0
+ PyQt5>=5.15.0,<5.16.0
```

**Rationale**: PyQt5 5.15.x is the latest stable version with excellent compatibility

### 2. Core Framework Conversion

#### File: `xlib/qt/__init__.py`
```python
# BEFORE (PyQt6):
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

AlignLeft = Qt.AlignmentFlag.AlignLeft
AlignCenter = Qt.AlignmentFlag.AlignCenter
# ... other enum aliases

# AFTER (PyQt5):
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# PyQt5 doesn't need enum aliases - direct access works
AlignLeft = Qt.AlignLeft
AlignCenter = Qt.AlignCenter
# ... direct enum access
```

### 3. Voice Changer UI Conversion

#### File: `apps/PlayaTewsIdentityMasker/ui/QVoiceChanger.py`
```python
# BEFORE (PyQt6):
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QSlider, QComboBox, QCheckBox, QSpinBox,
                             QDoubleSpinBox, QPushButton, QTabWidget, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

# AFTER (PyQt5):
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QSlider, QComboBox, QCheckBox, QSpinBox,
                             QDoubleSpinBox, QPushButton, QTabWidget, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
```

#### Enum Usage Updates:
```python
# BEFORE (PyQt6):
title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
checkbox.setCheckState(Qt.CheckState.Checked)
slider.setOrientation(Qt.Orientation.Horizontal)

# AFTER (PyQt5):
title_label.setAlignment(Qt.AlignCenter)
checkbox.setCheckState(Qt.Checked)
slider.setOrientation(Qt.Horizontal)
```

### 4. Build Script Updates

#### File: `build_desktop.py`
```python
# BEFORE (PyQt6):
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    ...
]

# AFTER (PyQt5):
hiddenimports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    ...
]
```

## Widget-Specific Considerations

### QTabWidget (Voice Changer UI)
```python
# PyQt6 and PyQt5 - Identical API
tab_widget = QTabWidget()
tab_widget.addTab(widget, "Tab Name")
# No changes needed
```

### QSlider (Effect Parameters)
```python
# PyQt6:
slider.setOrientation(Qt.Orientation.Horizontal)
slider.setRange(0, 100)

# PyQt5:
slider.setOrientation(Qt.Horizontal)  # Simplified enum access
slider.setRange(0, 100)  # No change
```

### QComboBox (Effect Selection)
```python
# PyQt6 and PyQt5 - Identical API
combo.addItem("Effect Name")
combo.setCurrentText("Default")
# No changes needed
```

### Signal/Slot Connections
```python
# PyQt6 and PyQt5 - Identical API
button.clicked.connect(self.on_button_clicked)
slider.valueChanged.connect(self.on_value_changed)
# No changes needed
```

## Migration Implementation Strategy

### Phase 1: Requirements and Core Framework (Day 1)
1. **Update requirements-unified.txt** to PyQt5
2. **Convert xlib/qt/__init__.py** to PyQt5 imports
3. **Remove PyQt6 enum aliases** (use direct access)
4. **Update build scripts** for PyQt5

### Phase 2: Voice Changer Conversion (Day 2)
1. **Convert QVoiceChanger.py imports** to PyQt5
2. **Update enum usage** throughout voice changer code
3. **Test widget functionality** with PyQt5
4. **Verify signal/slot connections**

### Phase 3: Integration Testing (Day 3)
1. **Test voice changer** with existing PyQt5 components
2. **Verify OBS-style UI integration**
3. **Test enhanced stream output compatibility**
4. **Performance validation**

## Compatibility Benefits

### ✅ Advantages of PyQt5 Conversion
1. **Ecosystem Consistency**: All components use same Qt version
2. **Stability**: PyQt5 is mature and well-tested
3. **Library Support**: More third-party libraries support PyQt5
4. **Deployment**: Simpler packaging with single Qt version

### ⚠️ Considerations
1. **Enum Syntax**: Simpler in PyQt5 (no nested flags)
2. **Feature Parity**: PyQt5 has all needed features for voice changer
3. **Performance**: Minimal difference for voice changer use case
4. **Future Proofing**: PyQt5 still actively maintained

## Testing Strategy

### Unit Tests
```python
def test_pyqt5_voice_changer_imports():
    """Test PyQt5 voice changer imports work correctly"""
    from PyQt5.QtWidgets import QWidget
    from apps.PlayaTewsIdentityMasker.ui.QVoiceChanger import QVoiceChanger
    # Should work without errors

def test_enum_usage():
    """Test PyQt5 enum usage in voice changer"""
    from PyQt5.QtCore import Qt
    # Test direct enum access
    assert hasattr(Qt, 'AlignCenter')
    assert not hasattr(Qt, 'AlignmentFlag')  # PyQt6 style
```

### Integration Tests
- Test voice changer within PyQt5 application
- Verify all widgets render correctly
- Test effect parameter controls
- Validate audio processing integration

## Risk Assessment

### 🟢 Low Risk Areas
- **Widget APIs**: Nearly identical between PyQt5/PyQt6
- **Signal/Slot**: Same syntax and behavior
- **Layout Management**: No changes needed
- **Event Handling**: Compatible APIs

### 🟡 Medium Risk Areas
- **Enum Access**: Requires systematic changes
- **Import Statements**: Must be consistent across all files
- **Build Scripts**: Need coordinated updates

### 🔴 High Risk Areas
- **Core Framework**: Changes affect entire application
- **Third-party Dependencies**: May have PyQt version preferences

## Alternative Approach: Compatibility Layer

If full conversion is risky, create a compatibility layer:

```python
# File: xlib/qt/compat.py
"""PyQt5/PyQt6 Compatibility Layer"""

try:
    # Try PyQt6 first
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtWidgets import *
    QT_VERSION = 6
    
    # Create PyQt5-style aliases
    Qt.AlignCenter = Qt.AlignmentFlag.AlignCenter
    Qt.AlignLeft = Qt.AlignmentFlag.AlignLeft
    Qt.Checked = Qt.CheckState.Checked
    # ... other aliases
    
except ImportError:
    # Fall back to PyQt5
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    QT_VERSION = 5
    # PyQt5 enums already in correct format
```

## Conclusion

Converting the PyQt6 voice changer to PyQt5 is **straightforward** with the main effort being:

1. **Import statement changes** (mechanical)
2. **Enum syntax updates** (systematic) 
3. **Requirements file updates** (trivial)

The voice changer functionality will remain **100% identical** since the core Qt APIs are the same between versions. This conversion ensures **full compatibility** with the existing PyQt5 ecosystem while maintaining all voice changing capabilities.
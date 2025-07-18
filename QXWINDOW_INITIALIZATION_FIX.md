# QXWindow Initialization Fix

## Problem Analysis

The error `Exception: Top widget must be a class of QXWindow` occurs during the widget registration process in the Qt framework. The issue is in the initialization order and timing:

### Root Cause
1. During application startup, widgets are being resized before the `forward_declarations.QXWindow` is properly set
2. The `_part_QXWidget.resizeEvent()` method calls `QXMainApplication.inst.register_QXWidget(self)`
3. The registration process traverses the widget hierarchy to find the top parent widget
4. It checks if the top widget is an instance of `forward_declarations.QXWindow`
5. However, `forward_declarations.QXWindow` is `None` because the import chain hasn't completed

### Error Location Stack
```
File: xlib/qt/widgets/QXWidget.py, line 21 (resizeEvent)
↓
File: xlib/qt/widgets/_part_QXWidget.py, line 122 (resizeEvent -> register_QXWidget)
↓
File: xlib/qt/widgets/QXMainApplication.py, line 110 (register_QXWidget)
Exception: Top widget must be a class of QXWindow
```

## Solution

### 1. Fix the Forward Declaration Import Order

The issue is that `forward_declarations.QXWindow` is set at the end of `QXWindow.py` but the check happens before all imports are complete.

**Fix in `xlib/qt/widgets/QXMainApplication.py`:**

```python
def register_QXWidget(self, widget) -> str:
    """
    registers QXWidget, checks validity, returns an unique name
    """
    hierarchy = []

    iter_widget = widget
    while True:
        hierarchy.insert(0, iter_widget.__class__.__name__)
        iter_parent_widget = iter_widget.parentWidget()
        if iter_parent_widget is None:
            break
        iter_widget = iter_parent_widget

    # Import QXWindow directly if forward_declarations.QXWindow is None
    if forward_declarations.QXWindow is None:
        try:
            from .QXWindow import QXWindow
            forward_declarations.QXWindow = QXWindow
        except ImportError:
            pass

    if forward_declarations.QXWindow is not None and not isinstance(iter_widget, forward_declarations.QXWindow):
        raise Exception('Top widget must be a class of QXWindow')

    if len(hierarchy) == 1:
        # top level widgets(Windows) has no numerification
        return hierarchy[0]
    else:
        hierarchy_name = '.'.join(hierarchy)

        num = self._hierarchy_name_count.get(hierarchy_name, -1)
        num = self._hierarchy_name_count[hierarchy_name] = num + 1
        
        return f"{hierarchy_name}#{num}"
```

### 2. Alternative: Defer Widget Registration

Another approach is to defer the registration until the application is fully initialized:

**Fix in `xlib/qt/widgets/_part_QXWidget.py`:**

```python
def resizeEvent(self, ev : QResizeEvent):
    if not self._registered:
        # Check if QXMainApplication is ready and forward_declarations are set
        if (hasattr(self, '_registration_deferred') or 
            forward_declarations.QXWindow is None or 
            QXMainApplication.inst is None):
            self._registration_deferred = True
            return
        
        self._registered = True
        self._name_id = QXMainApplication.inst.register_QXWidget(self)
        self._on_registered()
```

### 3. Recommended Fix: Import Order Correction

The cleanest solution is to ensure proper import order in `xlib/qt/__init__.py`:

**Move QXWindow import before QXMainApplication:**

```python
# Import QXWindow early to set forward_declarations
from .widgets.QXWindow import QXWindow
from .widgets.QXMainApplication import QXMainApplication
# ... other imports
```

## Implementation Steps

1. **Immediate Fix**: Apply the register_QXWidget safety check (Solution 1)
2. **Long-term Fix**: Reorganize import order (Solution 3)
3. **Test**: Verify the application starts without the QXWindow error

## Files to Modify

1. `xlib/qt/widgets/QXMainApplication.py` - Add safety check in register_QXWidget
2. `xlib/qt/__init__.py` - Reorder imports to put QXWindow before QXMainApplication
3. Optionally `xlib/qt/widgets/_part_QXWidget.py` - Add deferred registration logic

## Testing

After applying the fix:
1. Run the application normally
2. Verify the splash screen appears
3. Confirm the main window opens without errors
4. Test widget resizing and registration
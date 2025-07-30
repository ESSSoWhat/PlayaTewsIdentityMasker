#!/usr/bin/env python3
"""
Accessibility Manager for PlayaTewsIdentityMasker
Screen reader support, keyboard navigation, and accessibility features
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class AccessibilityLevel(Enum):
    """Accessibility support levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"

class NavigationMode(Enum):
    """Keyboard navigation modes"""
    TAB = "tab"
    ARROW = "arrow"
    HOTKEY = "hotkey"

class AccessibilityManager:
    """Main accessibility manager for the application"""
    
    def __init__(self):
        self.enabled = True
        self.screen_reader_support = True
        self.keyboard_navigation = True
        self.high_contrast_mode = False
        self.large_text_mode = False
        self.voice_feedback = False
        
        # Navigation state
        self.current_focus_index = 0
        self.focusable_elements = []
        self.navigation_mode = NavigationMode.TAB
        
        # Screen reader support
        self.screen_reader_queue = []
        self.screen_reader_thread = None
        self.screen_reader_running = False
        
        # Keyboard shortcuts
        self.keyboard_shortcuts = self._initialize_keyboard_shortcuts()
        
        # Voice feedback
        self.voice_feedback_enabled = False
        self.voice_feedback_thread = None
        
        # Accessibility settings
        self.settings = self._load_accessibility_settings()
        
        logger.info("♿ Accessibility Manager initialized")
    
    def _initialize_keyboard_shortcuts(self) -> Dict[str, Dict[str, Any]]:
        """Initialize keyboard shortcuts for accessibility"""
        return {
            'F1': {
                'action': 'help',
                'description': 'Show accessibility help',
                'category': 'navigation'
            },
            'F2': {
                'action': 'toggle_screen_reader',
                'description': 'Toggle screen reader',
                'category': 'screen_reader'
            },
            'F3': {
                'action': 'toggle_high_contrast',
                'description': 'Toggle high contrast mode',
                'category': 'visual'
            },
            'F4': {
                'action': 'toggle_large_text',
                'description': 'Toggle large text mode',
                'category': 'visual'
            },
            'F5': {
                'action': 'toggle_voice_feedback',
                'description': 'Toggle voice feedback',
                'category': 'audio'
            },
            'Tab': {
                'action': 'next_focus',
                'description': 'Move to next focusable element',
                'category': 'navigation'
            },
            'Shift+Tab': {
                'action': 'previous_focus',
                'description': 'Move to previous focusable element',
                'category': 'navigation'
            },
            'Enter': {
                'action': 'activate',
                'description': 'Activate current element',
                'category': 'navigation'
            },
            'Space': {
                'action': 'toggle',
                'description': 'Toggle current element',
                'category': 'navigation'
            },
            'Escape': {
                'action': 'cancel',
                'description': 'Cancel current operation',
                'category': 'navigation'
            },
            'Ctrl+M': {
                'action': 'focus_menu',
                'description': 'Focus main menu',
                'category': 'navigation'
            },
            'Ctrl+S': {
                'action': 'focus_settings',
                'description': 'Focus settings panel',
                'category': 'navigation'
            },
            'Ctrl+P': {
                'action': 'focus_preview',
                'description': 'Focus preview area',
                'category': 'navigation'
            }
        }
    
    def _load_accessibility_settings(self) -> Dict[str, Any]:
        """Load accessibility settings from file"""
        settings_file = Path("settings/accessibility.json")
        default_settings = {
            'enabled': True,
            'screen_reader_support': True,
            'keyboard_navigation': True,
            'high_contrast_mode': False,
            'large_text_mode': False,
            'voice_feedback': False,
            'navigation_mode': 'tab',
            'announce_focus_changes': True,
            'announce_state_changes': True,
            'announce_errors': True,
            'keyboard_shortcuts_enabled': True,
            'focus_indicator_style': 'outline',
            'focus_indicator_color': '#0078d4',
            'focus_indicator_width': '2px',
            'high_contrast_colors': {
                'background': '#000000',
                'foreground': '#ffffff',
                'accent': '#ffff00'
            },
            'large_text_scale': 1.5,
            'voice_feedback_rate': 1.0,
            'voice_feedback_volume': 0.8
        }
        
        try:
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
                    logger.info("♿ Accessibility settings loaded")
            else:
                # Create default settings file
                settings_file.parent.mkdir(parents=True, exist_ok=True)
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(default_settings, f, indent=2)
                logger.info("♿ Default accessibility settings created")
        except Exception as e:
            logger.error(f"❌ Error loading accessibility settings: {e}")
        
        return default_settings
    
    def save_accessibility_settings(self):
        """Save accessibility settings to file"""
        try:
            settings_file = Path("settings/accessibility.json")
            settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            logger.info("♿ Accessibility settings saved")
        except Exception as e:
            logger.error(f"❌ Error saving accessibility settings: {e}")
    
    def start_screen_reader(self):
        """Start screen reader functionality"""
        if not self.screen_reader_support or self.screen_reader_running:
            return
        
        self.screen_reader_running = True
        self.screen_reader_thread = threading.Thread(target=self._screen_reader_worker, daemon=True)
        self.screen_reader_thread.start()
        logger.info("♿ Screen reader started")
    
    def stop_screen_reader(self):
        """Stop screen reader functionality"""
        self.screen_reader_running = False
        if self.screen_reader_thread:
            self.screen_reader_thread.join(timeout=1.0)
        logger.info("♿ Screen reader stopped")
    
    def _screen_reader_worker(self):
        """Screen reader worker thread"""
        while self.screen_reader_running:
            if self.screen_reader_queue:
                message = self.screen_reader_queue.pop(0)
                self._announce_message(message)
            time.sleep(0.1)
    
    def announce(self, message: str, priority: str = "normal"):
        """Announce message to screen reader"""
        if not self.screen_reader_support or not self.enabled:
            return
        
        announcement = {
            'message': message,
            'priority': priority,
            'timestamp': time.time()
        }
        
        self.screen_reader_queue.append(announcement)
        
        # Also log for debugging
        logger.info(f"♿ Announcement: {message}")
    
    def _announce_message(self, announcement: Dict[str, Any]):
        """Actually announce the message (platform-specific)"""
        message = announcement['message']
        priority = announcement['priority']
        
        # For now, just log the announcement
        # In a real implementation, this would interface with screen reader APIs
        if priority == "high":
            logger.info(f"🔊 HIGH PRIORITY: {message}")
        else:
            logger.info(f"🔊 {message}")
    
    def register_focusable_element(self, element_id: str, element_type: str, 
                                 description: str, position: tuple = None):
        """Register a focusable element for keyboard navigation"""
        element = {
            'id': element_id,
            'type': element_type,
            'description': description,
            'position': position,
            'focused': False
        }
        
        self.focusable_elements.append(element)
        logger.debug(f"♿ Registered focusable element: {element_id}")
    
    def unregister_focusable_element(self, element_id: str):
        """Unregister a focusable element"""
        self.focusable_elements = [e for e in self.focusable_elements if e['id'] != element_id]
        logger.debug(f"♿ Unregistered focusable element: {element_id}")
    
    def set_focus(self, element_id: str):
        """Set focus to a specific element"""
        for i, element in enumerate(self.focusable_elements):
            if element['id'] == element_id:
                # Clear previous focus
                for elem in self.focusable_elements:
                    elem['focused'] = False
                
                # Set new focus
                element['focused'] = True
                self.current_focus_index = i
                
                # Announce focus change
                if self.settings.get('announce_focus_changes', True):
                    self.announce(f"Focused on {element['description']}")
                
                logger.debug(f"♿ Focus set to: {element_id}")
                return True
        
        logger.warning(f"⚠️ Element not found for focus: {element_id}")
        return False
    
    def next_focus(self):
        """Move focus to next element"""
        if not self.focusable_elements:
            return
        
        self.current_focus_index = (self.current_focus_index + 1) % len(self.focusable_elements)
        element = self.focusable_elements[self.current_focus_index]
        
        # Clear previous focus
        for elem in self.focusable_elements:
            elem['focused'] = False
        
        # Set new focus
        element['focused'] = True
        
        # Announce focus change
        if self.settings.get('announce_focus_changes', True):
            self.announce(f"Focused on {element['description']}")
        
        logger.debug(f"♿ Focus moved to: {element['id']}")
    
    def previous_focus(self):
        """Move focus to previous element"""
        if not self.focusable_elements:
            return
        
        self.current_focus_index = (self.current_focus_index - 1) % len(self.focusable_elements)
        element = self.focusable_elements[self.current_focus_index]
        
        # Clear previous focus
        for elem in self.focusable_elements:
            elem['focused'] = False
        
        # Set new focus
        element['focused'] = True
        
        # Announce focus change
        if self.settings.get('announce_focus_changes', True):
            self.announce(f"Focused on {element['description']}")
        
        logger.debug(f"♿ Focus moved to: {element['id']}")
    
    def toggle_high_contrast_mode(self):
        """Toggle high contrast mode"""
        self.high_contrast_mode = not self.high_contrast_mode
        self.settings['high_contrast_mode'] = self.high_contrast_mode
        
        if self.high_contrast_mode:
            self.announce("High contrast mode enabled")
            logger.info("♿ High contrast mode enabled")
        else:
            self.announce("High contrast mode disabled")
            logger.info("♿ High contrast mode disabled")
        
        self.save_accessibility_settings()
    
    def toggle_large_text_mode(self):
        """Toggle large text mode"""
        self.large_text_mode = not self.large_text_mode
        self.settings['large_text_mode'] = self.large_text_mode
        
        if self.large_text_mode:
            self.announce("Large text mode enabled")
            logger.info("♿ Large text mode enabled")
        else:
            self.announce("Large text mode disabled")
            logger.info("♿ Large text mode disabled")
        
        self.save_accessibility_settings()
    
    def toggle_voice_feedback(self):
        """Toggle voice feedback"""
        self.voice_feedback = not self.voice_feedback
        self.settings['voice_feedback'] = self.voice_feedback
        
        if self.voice_feedback:
            self.announce("Voice feedback enabled")
            logger.info("♿ Voice feedback enabled")
        else:
            self.announce("Voice feedback disabled")
            logger.info("♿ Voice feedback disabled")
        
        self.save_accessibility_settings()
    
    def handle_keyboard_event(self, key: str, modifiers: List[str] = None) -> bool:
        """Handle keyboard events for accessibility"""
        if not self.keyboard_navigation or not self.enabled:
            return False
        
        modifiers = modifiers or []
        key_combination = '+'.join(modifiers + [key])
        
        # Check for registered shortcuts
        if key_combination in self.keyboard_shortcuts:
            shortcut = self.keyboard_shortcuts[key_combination]
            action = shortcut['action']
            
            # Execute the action
            if action == 'next_focus':
                self.next_focus()
                return True
            elif action == 'previous_focus':
                self.previous_focus()
                return True
            elif action == 'toggle_high_contrast':
                self.toggle_high_contrast_mode()
                return True
            elif action == 'toggle_large_text':
                self.toggle_large_text_mode()
                return True
            elif action == 'toggle_voice_feedback':
                self.toggle_voice_feedback()
                return True
            elif action == 'help':
                self.show_accessibility_help()
                return True
        
        return False
    
    def show_accessibility_help(self):
        """Show accessibility help information"""
        help_text = """
Accessibility Help:

Keyboard Navigation:
- Tab: Move to next element
- Shift+Tab: Move to previous element
- Enter: Activate element
- Space: Toggle element
- Escape: Cancel operation

Function Keys:
- F1: Show this help
- F2: Toggle screen reader
- F3: Toggle high contrast mode
- F4: Toggle large text mode
- F5: Toggle voice feedback

Shortcuts:
- Ctrl+M: Focus main menu
- Ctrl+S: Focus settings
- Ctrl+P: Focus preview

For more help, visit the accessibility settings.
        """
        
        self.announce("Showing accessibility help")
        logger.info("♿ Accessibility help displayed")
        print(help_text)
    
    def get_accessibility_status(self) -> Dict[str, Any]:
        """Get current accessibility status"""
        return {
            'enabled': self.enabled,
            'screen_reader_support': self.screen_reader_support,
            'keyboard_navigation': self.keyboard_navigation,
            'high_contrast_mode': self.high_contrast_mode,
            'large_text_mode': self.large_text_mode,
            'voice_feedback': self.voice_feedback,
            'focusable_elements_count': len(self.focusable_elements),
            'current_focus_index': self.current_focus_index,
            'navigation_mode': self.navigation_mode.value,
            'settings': self.settings
        }
    
    def announce_state_change(self, component: str, new_state: str):
        """Announce state changes for accessibility"""
        if not self.settings.get('announce_state_changes', True):
            return
        
        message = f"{component} {new_state}"
        self.announce(message)
        logger.debug(f"♿ State change announced: {message}")
    
    def announce_error(self, error_message: str):
        """Announce errors for accessibility"""
        if not self.settings.get('announce_errors', True):
            return
        
        message = f"Error: {error_message}"
        self.announce(message, priority="high")
        logger.error(f"♿ Error announced: {error_message}")
    
    def cleanup(self):
        """Cleanup accessibility resources"""
        self.stop_screen_reader()
        self.save_accessibility_settings()
        logger.info("♿ Accessibility manager cleaned up")

# Global accessibility manager instance
_accessibility_manager = None

def get_accessibility_manager() -> AccessibilityManager:
    """Get global accessibility manager instance"""
    global _accessibility_manager
    if _accessibility_manager is None:
        _accessibility_manager = AccessibilityManager()
    return _accessibility_manager

def announce(message: str, priority: str = "normal"):
    """Convenience function for announcements"""
    get_accessibility_manager().announce(message, priority)

def register_focusable_element(element_id: str, element_type: str, description: str, position: tuple = None):
    """Convenience function for registering focusable elements"""
    get_accessibility_manager().register_focusable_element(element_id, element_type, description, position)

def set_focus(element_id: str):
    """Convenience function for setting focus"""
    return get_accessibility_manager().set_focus(element_id) 
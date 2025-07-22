from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QSlider, QComboBox, QCheckBox, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from .widgets.QComboBoxCSWDynamicSingleSwitch import QComboBoxCSWDynamicSingleSwitch
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber
from .widgets.QDoubleSpinBoxCSWNumber import QDoubleSpinBoxCSWNumber


class QCompactVoiceChanger(QWidget):
    """
    Compact voice changer widget for bottom left panel integration
    """
    def __init__(self, cs_voice_changer):
        super().__init__()
        
        self.cs_voice_changer = cs_voice_changer
        
        # Create main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create title
        title_label = QLabel("🎤 Voice Changer")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
        main_layout.addWidget(title_label)
        
        # Enable/Disable control
        try:
            self.q_enabled = QCheckBoxCSWFlag(self.cs_voice_changer.enabled)
            self.q_enabled.setText("Enable Voice Changer")
            self.q_enabled.setStyleSheet("""
                QCheckBox {
                    color: #ffffff;
                    font-size: 10px;
                    font-weight: bold;
                }
            """)
            main_layout.addWidget(self.q_enabled)
        except Exception as e:
            print(f"Warning: Could not create voice changer enabled control: {e}")
            # Create a simple checkbox as fallback
            self.q_enabled = QCheckBox("Enable Voice Changer")
            self.q_enabled.setStyleSheet("""
                QCheckBox {
                    color: #ffffff;
                    font-size: 10px;
                    font-weight: bold;
                }
            """)
            main_layout.addWidget(self.q_enabled)
        
        # Effect type selection
        effect_label = QLabel("Effect:")
        effect_label.setStyleSheet("color: #cccccc; font-size: 9px; margin-top: 5px;")
        main_layout.addWidget(effect_label)
        
        try:
            self.q_effect_type = QComboBoxCSWDynamicSingleSwitch(
                self.cs_voice_changer.effect_type, 
                reflect_state_widgets=[effect_label]
            )
            self.q_effect_type.setStyleSheet("""
                QComboBox {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #ffffff;
                    font-size: 9px;
                    padding: 2px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid #ffffff;
                }
            """)
            main_layout.addWidget(self.q_effect_type)
        except Exception as e:
            print(f"Warning: Could not create voice changer effect control: {e}")
            # Create a simple combobox as fallback
            self.q_effect_type = QComboBox()
            self.q_effect_type.addItems([
                "None", "Pitch Up", "Pitch Down", "Robot", "Helium", 
                "Deep Voice", "Echo", "Reverb", "Chorus", "Distortion", "Autotune"
            ])
            self.q_effect_type.setStyleSheet("""
                QComboBox {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 3px;
                    color: #ffffff;
                    font-size: 9px;
                    padding: 2px;
                }
            """)
            main_layout.addWidget(self.q_effect_type)
        
        # Quick presets (compact grid)
        presets_label = QLabel("Quick Presets:")
        presets_label.setStyleSheet("color: #cccccc; font-size: 9px; margin-top: 5px;")
        main_layout.addWidget(presets_label)
        
        presets_layout = QHBoxLayout()
        
        # Create compact preset buttons
        presets = [
            ("Male", "Deep Voice"),
            ("Female", "Pitch Up"),
            ("Robot", "Robot"),
            ("Echo", "Echo")
        ]
        
        for preset_name, effect_name in presets:
            btn = QPushButton(preset_name)
            btn.setMaximumWidth(40)
            btn.setMaximumHeight(20)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 2px;
                    font-size: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn.clicked.connect(lambda checked, name=effect_name: self._apply_preset(name))
            presets_layout.addWidget(btn)
        
        main_layout.addLayout(presets_layout)
        
        # Effect parameters (collapsible)
        self.params_group = QGroupBox("Parameters")
        self.params_group.setMaximumHeight(80)
        self.params_group.setStyleSheet("""
            QGroupBox {
                color: #cccccc;
                font-size: 9px;
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 3px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 5px;
                padding: 0 3px 0 3px;
            }
        """)
        
        params_layout = QVBoxLayout()
        
        # Pitch shift slider
        pitch_label = QLabel("Pitch:")
        pitch_label.setStyleSheet("color: #cccccc; font-size: 8px;")
        params_layout.addWidget(pitch_label)
        
        try:
            self.q_pitch_shift = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.pitch_shift)
            self.q_pitch_shift.setRange(-12.0, 12.0)
            self.q_pitch_shift.setSingleStep(0.5)
            self.q_pitch_shift.setDecimals(1)
            self.q_pitch_shift.setStyleSheet("""
                QDoubleSpinBox {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 2px;
                    color: #ffffff;
                    font-size: 8px;
                    padding: 1px;
                }
            """)
            params_layout.addWidget(self.q_pitch_shift)
        except Exception as e:
            print(f"Warning: Could not create voice changer pitch control: {e}")
            # Create a simple slider as fallback
            self.q_pitch_shift = QSlider(Qt.Horizontal)
            self.q_pitch_shift.setRange(-12, 12)
            self.q_pitch_shift.setValue(0)
            self.q_pitch_shift.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #404040;
                    height: 4px;
                    background: #2d2d2d;
                    border-radius: 2px;
                }
                QSlider::handle:horizontal {
                    background: #3498db;
                    border: 1px solid #2980b9;
                    width: 8px;
                    margin: -2px 0;
                    border-radius: 4px;
                }
            """)
            params_layout.addWidget(self.q_pitch_shift)
        
        self.params_group.setLayout(params_layout)
        main_layout.addWidget(self.params_group)
        
        # Set up styling
        self._setup_styling()

    def _apply_preset(self, effect_name):
        """Apply a voice effect preset"""
        effect_mapping = {
            "Deep Voice": ("effect_type", 5),  # DEEP
            "Pitch Up": ("effect_type", 1),    # PITCH_SHIFT
            "Robot": ("effect_type", 3),       # ROBOT
            "Echo": ("effect_type", 6),        # ECHO
            "Reverb": ("effect_type", 7),      # REVERB
            "Chorus": ("effect_type", 8),      # CHORUS
            "Distortion": ("effect_type", 9),  # DISTORTION
            "Autotune": ("effect_type", 10),   # AUTOTUNE
            "Male": ("effect_type", 11),       # MALE_VOICE
            "Female": ("effect_type", 12),     # FEMALE_VOICE
            "Child": ("effect_type", 13),      # CHILD_VOICE
            "Elderly": ("effect_type", 14),    # ELDERLY_VOICE
            "British": ("effect_type", 15),    # BRITISH_ACCENT
            "Southern": ("effect_type", 16),   # SOUTHERN_ACCENT
        }
        
        if effect_name in effect_mapping:
            param_name, value = effect_mapping[effect_name]
            
            # Try to use control sheet if available
            if hasattr(self.cs_voice_changer, param_name):
                try:
                    getattr(self.cs_voice_changer, param_name).set_number(value)
                    
                    # Set additional parameters for specific effects
                    if effect_name == "Deep Voice" and hasattr(self.cs_voice_changer, 'pitch_shift'):
                        self.cs_voice_changer.pitch_shift.set_number(-3.0)
                    elif effect_name == "Pitch Up" and hasattr(self.cs_voice_changer, 'pitch_shift'):
                        self.cs_voice_changer.pitch_shift.set_number(3.0)
                    elif effect_name == "Robot" and hasattr(self.cs_voice_changer, 'robot_rate'):
                        self.cs_voice_changer.robot_rate.set_number(0.1)
                    elif effect_name == "Echo" and hasattr(self.cs_voice_changer, 'echo_delay'):
                        self.cs_voice_changer.echo_delay.set_number(0.3)
                        if hasattr(self.cs_voice_changer, 'echo_decay'):
                            self.cs_voice_changer.echo_decay.set_number(0.5)
                    
                    print(f"🎤 Voice effect applied: {effect_name}")
                    return
                except Exception as e:
                    print(f"Warning: Could not apply voice effect via control sheet: {e}")
            
            # Fallback: try to update the UI controls directly
            try:
                if param_name == "effect_type" and hasattr(self, 'q_effect_type'):
                    if isinstance(self.q_effect_type, QComboBox):
                        # Find the effect in the combobox
                        effect_text = effect_name.replace("_", " ").title()
                        index = self.q_effect_type.findText(effect_text)
                        if index >= 0:
                            self.q_effect_type.setCurrentIndex(index)
                        else:
                            # Try alternative names
                            alt_names = {
                                "Deep Voice": "Deep",
                                "Pitch Up": "Pitch Shift",
                                "Robot": "Robot",
                                "Echo": "Echo"
                            }
                            if effect_name in alt_names:
                                index = self.q_effect_type.findText(alt_names[effect_name])
                                if index >= 0:
                                    self.q_effect_type.setCurrentIndex(index)
                    
                    # Update pitch slider if available
                    if effect_name == "Deep Voice" and hasattr(self, 'q_pitch_shift'):
                        if isinstance(self.q_pitch_shift, QSlider):
                            self.q_pitch_shift.setValue(-3)
                        elif hasattr(self.q_pitch_shift, 'setValue'):
                            self.q_pitch_shift.setValue(-3.0)
                    elif effect_name == "Pitch Up" and hasattr(self, 'q_pitch_shift'):
                        if isinstance(self.q_pitch_shift, QSlider):
                            self.q_pitch_shift.setValue(3)
                        elif hasattr(self.q_pitch_shift, 'setValue'):
                            self.q_pitch_shift.setValue(3.0)
                    
                    print(f"🎤 Voice effect applied (UI fallback): {effect_name}")
                else:
                    print(f"🎤 Voice effect not applied: {effect_name} (parameter {param_name} not found)")
            except Exception as e:
                print(f"Warning: Could not apply voice effect via UI fallback: {e}")
                print(f"🎤 Voice effect not applied: {effect_name}")

    def _setup_styling(self):
        """Setup the widget styling"""
        self.setStyleSheet("""
            QCompactVoiceChanger {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        # Set maximum height to keep it compact
        self.setMaximumHeight(200) 
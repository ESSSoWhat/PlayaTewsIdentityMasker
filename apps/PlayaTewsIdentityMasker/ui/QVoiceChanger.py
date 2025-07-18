from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QSlider, QComboBox, QCheckBox, QSpinBox,
                             QDoubleSpinBox, QPushButton, QTabWidget, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from .widgets.QComboBoxCSWDynamicSingleSwitch import QComboBoxCSWDynamicSingleSwitch
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber
from .widgets.QDoubleSpinBoxCSWNumber import QDoubleSpinBoxCSWNumber


class QVoiceChanger(QWidget):
    def __init__(self, cs_voice_changer):
        super().__init__()
        
        self.cs_voice_changer = cs_voice_changer
        
        # Create main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create title
        title_label = QLabel("Voice Changer")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create tab widget for different effect categories
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_main_tab()
        self._create_effects_tab()
        self._create_devices_tab()
        
        # Set up styling
        self._setup_styling()

    def _create_main_tab(self):
        """Create the main control tab"""
        main_tab = QWidget()
        layout = QVBoxLayout()
        main_tab.setLayout(layout)
        
        # Enable/Disable control
        enable_group = QGroupBox("Voice Changer Control")
        enable_layout = QVBoxLayout()
        enable_group.setLayout(enable_layout)
        
        self.q_enabled = QCheckBoxCSWFlag(self.cs_voice_changer.enabled)
        enable_layout.addWidget(self.q_enabled)
        layout.addWidget(enable_group)
        
        # Effect type selection
        effect_group = QGroupBox("Effect Type")
        effect_layout = QVBoxLayout()
        effect_group.setLayout(effect_layout)
        
        effect_label = QLabel("Select Effect:")
        effect_layout.addWidget(effect_label)
        
        self.q_effect_type = QComboBoxCSWDynamicSingleSwitch(
            self.cs_voice_changer.effect_type, 
            reflect_state_widgets=[effect_label]
        )
        effect_layout.addWidget(self.q_effect_type)
        layout.addWidget(effect_group)
        
        # Quick presets
        presets_group = QGroupBox("Quick Presets")
        presets_layout = QGridLayout()
        presets_group.setLayout(presets_layout)
        
        # Create preset buttons
        presets = [
            ("Helium", lambda: self._apply_preset("helium")),
            ("Deep Voice", lambda: self._apply_preset("deep")),
            ("Robot", lambda: self._apply_preset("robot")),
            ("Echo", lambda: self._apply_preset("echo")),
            ("Reverb", lambda: self._apply_preset("reverb")),
            ("Chorus", lambda: self._apply_preset("chorus")),
            ("Distortion", lambda: self._apply_preset("distortion")),
            ("Autotune", lambda: self._apply_preset("autotune"))
        ]
        
        for i, (name, callback) in enumerate(presets):
            btn = QPushButton(name)
            btn.clicked.connect(callback)
            presets_layout.addWidget(btn, i // 4, i % 4)
        
        layout.addWidget(presets_group)
        layout.addStretch()
        
        self.tab_widget.addTab(main_tab, "Main")

    def _create_effects_tab(self):
        """Create the effects parameters tab"""
        effects_tab = QWidget()
        layout = QVBoxLayout()
        effects_tab.setLayout(layout)
        
        # Pitch and Formant controls
        pitch_group = QGroupBox("Pitch & Formant")
        pitch_layout = QGridLayout()
        pitch_group.setLayout(pitch_layout)
        
        # Pitch shift
        pitch_label = QLabel("Pitch Shift (semitones):")
        self.q_pitch_shift = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.pitch_shift)
        pitch_layout.addWidget(pitch_label, 0, 0)
        pitch_layout.addWidget(self.q_pitch_shift, 0, 1)
        
        # Formant shift
        formant_label = QLabel("Formant Shift:")
        self.q_formant_shift = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.formant_shift)
        pitch_layout.addWidget(formant_label, 1, 0)
        pitch_layout.addWidget(self.q_formant_shift, 1, 1)
        
        layout.addWidget(pitch_group)
        
        # Robot effect controls
        robot_group = QGroupBox("Robot Effect")
        robot_layout = QGridLayout()
        robot_group.setLayout(robot_layout)
        
        robot_rate_label = QLabel("Modulation Rate (Hz):")
        self.q_robot_rate = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.robot_rate)
        robot_layout.addWidget(robot_rate_label, 0, 0)
        robot_layout.addWidget(self.q_robot_rate, 0, 1)
        
        layout.addWidget(robot_group)
        
        # Echo effect controls
        echo_group = QGroupBox("Echo Effect")
        echo_layout = QGridLayout()
        echo_group.setLayout(echo_layout)
        
        echo_delay_label = QLabel("Delay (seconds):")
        self.q_echo_delay = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.echo_delay)
        echo_layout.addWidget(echo_delay_label, 0, 0)
        echo_layout.addWidget(self.q_echo_delay, 0, 1)
        
        echo_decay_label = QLabel("Decay:")
        self.q_echo_decay = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.echo_decay)
        echo_layout.addWidget(echo_decay_label, 1, 0)
        echo_layout.addWidget(self.q_echo_decay, 1, 1)
        
        layout.addWidget(echo_group)
        
        # Reverb effect controls
        reverb_group = QGroupBox("Reverb Effect")
        reverb_layout = QGridLayout()
        reverb_group.setLayout(reverb_layout)
        
        reverb_room_label = QLabel("Room Size:")
        self.q_reverb_room_size = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.reverb_room_size)
        reverb_layout.addWidget(reverb_room_label, 0, 0)
        reverb_layout.addWidget(self.q_reverb_room_size, 0, 1)
        
        reverb_damping_label = QLabel("Damping:")
        self.q_reverb_damping = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.reverb_damping)
        reverb_layout.addWidget(reverb_damping_label, 1, 0)
        reverb_layout.addWidget(self.q_reverb_damping, 1, 1)
        
        layout.addWidget(reverb_group)
        
        # Chorus effect controls
        chorus_group = QGroupBox("Chorus Effect")
        chorus_layout = QGridLayout()
        chorus_group.setLayout(chorus_layout)
        
        chorus_rate_label = QLabel("Rate (Hz):")
        self.q_chorus_rate = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.chorus_rate)
        chorus_layout.addWidget(chorus_rate_label, 0, 0)
        chorus_layout.addWidget(self.q_chorus_rate, 0, 1)
        
        chorus_depth_label = QLabel("Depth (seconds):")
        self.q_chorus_depth = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.chorus_depth)
        chorus_layout.addWidget(chorus_depth_label, 1, 0)
        chorus_layout.addWidget(self.q_chorus_depth, 1, 1)
        
        layout.addWidget(chorus_group)
        
        # Distortion effect controls
        distortion_group = QGroupBox("Distortion Effect")
        distortion_layout = QGridLayout()
        distortion_group.setLayout(distortion_layout)
        
        distortion_amount_label = QLabel("Amount:")
        self.q_distortion_amount = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.distortion_amount)
        distortion_layout.addWidget(distortion_amount_label, 0, 0)
        distortion_layout.addWidget(self.q_distortion_amount, 0, 1)
        
        layout.addWidget(distortion_group)
        
        # Autotune effect controls
        autotune_group = QGroupBox("Autotune Effect")
        autotune_layout = QGridLayout()
        autotune_group.setLayout(autotune_layout)
        
        autotune_sensitivity_label = QLabel("Sensitivity:")
        self.q_autotune_sensitivity = QDoubleSpinBoxCSWNumber(self.cs_voice_changer.autotune_sensitivity)
        autotune_layout.addWidget(autotune_sensitivity_label, 0, 0)
        autotune_layout.addWidget(self.q_autotune_sensitivity, 0, 1)
        
        layout.addWidget(autotune_group)
        layout.addStretch()
        
        self.tab_widget.addTab(effects_tab, "Effects")

    def _create_devices_tab(self):
        """Create the devices configuration tab"""
        devices_tab = QWidget()
        layout = QVBoxLayout()
        devices_tab.setLayout(layout)
        
        # Input device selection
        input_group = QGroupBox("Input Device")
        input_layout = QVBoxLayout()
        input_group.setLayout(input_layout)
        
        input_label = QLabel("Microphone:")
        input_layout.addWidget(input_label)
        
        self.q_input_device = QComboBoxCSWDynamicSingleSwitch(
            self.cs_voice_changer.input_device,
            reflect_state_widgets=[input_label]
        )
        input_layout.addWidget(self.q_input_device)
        layout.addWidget(input_group)
        
        # Output device selection
        output_group = QGroupBox("Output Device")
        output_layout = QVBoxLayout()
        output_group.setLayout(output_layout)
        
        output_label = QLabel("Speakers/Headphones:")
        output_layout.addWidget(output_label)
        
        self.q_output_device = QComboBoxCSWDynamicSingleSwitch(
            self.cs_voice_changer.output_device,
            reflect_state_widgets=[output_label]
        )
        output_layout.addWidget(self.q_output_device)
        layout.addWidget(output_group)
        
        # Audio settings info
        info_group = QGroupBox("Audio Settings")
        info_layout = QVBoxLayout()
        info_group.setLayout(info_layout)
        
        info_text = """
        <b>Audio Configuration:</b><br>
        • Sample Rate: 44.1 kHz<br>
        • Buffer Size: 1024 samples<br>
        • Channels: Mono<br>
        • Format: 32-bit Float<br><br>
        <b>Tips:</b><br>
        • Use headphones to avoid feedback<br>
        • Adjust input volume in system settings<br>
        • Test effects with different voice types<br>
        • Combine effects for unique sounds
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(devices_tab, "Devices")

    def _apply_preset(self, preset_name):
        """Apply a preset configuration"""
        presets = {
            "helium": {
                "effect_type": 1,  # PITCH_SHIFT
                "pitch_shift": 4.0
            },
            "deep": {
                "effect_type": 1,  # PITCH_SHIFT
                "pitch_shift": -4.0
            },
            "robot": {
                "effect_type": 3,  # ROBOT
                "robot_rate": 0.5
            },
            "echo": {
                "effect_type": 6,  # ECHO
                "echo_delay": 0.3,
                "echo_decay": 0.5
            },
            "reverb": {
                "effect_type": 7,  # REVERB
                "reverb_room_size": 0.8,
                "reverb_damping": 0.5
            },
            "chorus": {
                "effect_type": 8,  # CHORUS
                "chorus_rate": 1.5,
                "chorus_depth": 0.002
            },
            "distortion": {
                "effect_type": 9,  # DISTORTION
                "distortion_amount": 0.3
            },
            "autotune": {
                "effect_type": 10,  # AUTOTUNE
                "autotune_sensitivity": 0.1
            }
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            
            # Apply effect type first
            if "effect_type" in preset:
                self.cs_voice_changer.effect_type.select(preset["effect_type"])
            
            # Apply other parameters
            for param, value in preset.items():
                if param != "effect_type":
                    getattr(self.cs_voice_changer, param).set_number(value)

    def _setup_styling(self):
        """Set up the widget styling"""
        # Set dark theme colors
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 10pt;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            
            QComboBox {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            
            QSpinBox, QDoubleSpinBox {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }
            
            QCheckBox {
                spacing: 5px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            
            QCheckBox::indicator:unchecked {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 2px;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
                border-radius: 2px;
            }
            
            QTabWidget::pane {
                border: 1px solid #666666;
                background-color: #2b2b2b;
            }
            
            QTabBar::tab {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #0078d4;
                border-color: #0078d4;
            }
            
            QTabBar::tab:hover {
                background-color: #5a5a5a;
            }
        """)
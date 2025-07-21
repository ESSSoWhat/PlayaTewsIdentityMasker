# Universal DFM Folder System

## Overview
This is a standardized folder structure for managing all DFM (DeepFaceLab Model) files in a consistent and organized manner. The system provides a centralized location for all DFM models with automated management tools.

## 🚀 Quick Start

### 1. Setup (Already Complete)
The universal DFM system has been set up and populated with your existing models.

### 2. Basic Usage
```bash
# Navigate to the universal_dfm directory
cd universal_dfm

# List all models
python dfm_manager.py list

# List models in a specific category
python dfm_manager.py list --category prebuilt

# Get information about a specific model
python dfm_manager.py info --model-name "kevin_hart_model"

# Add a new model
python dfm_manager.py add --model-path "path/to/new_model.dfm" --category custom

# Move a model between categories
python dfm_manager.py move --model-name "model_name" --from-category prebuilt --to-category active
```

### 3. Using the Batch File (Windows)
```bash
# Easy access with the batch file
manage_dfm.bat list
manage_dfm.bat info --model-name "kevin_hart_model"
```

## 📁 Folder Structure
```
universal_dfm/
├── models/
│   ├── active/      # Currently active models for face swapping
│   ├── archived/    # Archived/old models (backup)
│   ├── custom/      # User-created models
│   └── prebuilt/    # Pre-built/imported models (32 models)
├── temp/
│   ├── extraction/  # Temporary extraction files
│   ├── training/    # Temporary training files
│   └── conversion/  # Temporary conversion files
├── backups/
│   ├── models/      # Model backups
│   └── configs/     # Configuration backups
├── logs/
│   ├── extraction/  # Extraction logs
│   ├── training/    # Training logs
│   └── conversion/  # Conversion logs
├── config/
│   ├── models/      # Model-specific configs
│   ├── settings/    # System settings
│   ├── main_config.json      # Main system configuration
│   └── model_registry.json   # Model registry
├── dfm_manager.py   # Main management script
├── manage_dfm.bat   # Windows batch file
└── README.md        # This file
```

## 📊 Current Models
The system currently contains **32 prebuilt models**:

### Prebuilt Models (32 total)
- Albica_Johns
- Amber_Song  
- Ava_de_Addario
- Bryan_Greynolds
- David_Kovalniy
- Dean_Wiesel
- Dilraba_Dilmurat
- Emily_Winston
- Ewon_Spice
- Irina_Arty
- Jackie_Chan
- Jesse_Stat_320
- Joker
- Keanu_Reeves
- Keanu_Reeves_320
- kevin_hart_model
- Kim_Jarrey
- Liu_Lice
- Matilda_Bobbie
- Meggie_Merkel
- Millie_Park
- Mr_Bean
- Natalie_Fatman
- Natasha_Former
- Nicola_Badge
- Rob_Doe
- Silwan_Stillwone
- Tim_Chrys
- Tim_Norland
- Tina_Shift
- Yohanna_Coralson
- Zahar_Lupin

## 🛠️ Management Commands

### List Models
```bash
# List all models
python dfm_manager.py list

# List models in specific category
python dfm_manager.py list --category prebuilt
python dfm_manager.py list --category custom
python dfm_manager.py list --category active
python dfm_manager.py list --category archived
```

### Add Models
```bash
# Add a new model to custom category
python dfm_manager.py add --model-path "path/to/model.dfm" --category custom

# Add a model to active category
python dfm_manager.py add --model-path "path/to/model.dfm" --category active
```

### Move Models
```bash
# Move a model from prebuilt to active
python dfm_manager.py move --model-name "kevin_hart_model" --from-category prebuilt --to-category active

# Move a model to archived
python dfm_manager.py move --model-name "old_model" --from-category active --to-category archived
```

### Get Model Information
```bash
# Get detailed info about a model
python dfm_manager.py info --model-name "kevin_hart_model"
```

### Remove Models
```bash
# Remove a model from a category
python dfm_manager.py remove --model-name "model_name" --category custom
```

## 🔧 Configuration Files

### main_config.json
Main system configuration including paths and settings.

### model_registry.json
Registry of all models with metadata and categorization.

### default_settings.json
Default settings for extraction, training, and conversion.

## 📋 Best Practices

1. **Model Organization**
   - Use `prebuilt` for imported/standard models
   - Use `custom` for your own trained models
   - Use `active` for models currently in use
   - Use `archived` for old/unused models

2. **Regular Maintenance**
   - Clean temp files periodically
   - Check logs for issues
   - Backup important models

3. **Naming Conventions**
   - Use descriptive model names
   - Include version numbers if applicable
   - Avoid special characters in names

## 🔄 Integration with DeepFaceLab

The universal DFM system is designed to work seamlessly with your existing DeepFaceLab workflow:

1. **Model Access**: All models are centrally located and easily accessible
2. **Consistent Paths**: Use the same model paths across all applications
3. **Backup Management**: Automatic backups prevent data loss
4. **Logging**: Comprehensive logging for troubleshooting

## 🚨 Troubleshooting

### Common Issues

1. **Model not found**
   - Check if the model exists in the specified category
   - Use `python dfm_manager.py list` to see all models

2. **Registry issues**
   - Run `python populate_registry.py` to rebuild the registry

3. **Permission errors**
   - Ensure you have write permissions to the universal_dfm directory

### Getting Help
- Check the logs in the `logs/` directory
- Verify model files exist in the correct categories
- Use the info command to check model details

## 📈 Future Enhancements

- Web interface for model management
- Automatic model validation
- Integration with DeepFaceLab GUI
- Cloud backup support
- Model performance metrics

---

**Created**: 2025-07-20  
**Version**: 1.0  
**Total Models**: 32  
**Status**: ✅ Active and Ready 
#!/usr/bin/env python3
"""
Kevin Hart Model Fix Script
Specifically targets the protobuf parsing error for kevin_hart_model.dfm
"""

import os
import sys
import shutil
import time
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KevinHartModelFixer:
    """Specific fixer for Kevin Hart model issues"""
    
    def __init__(self):
        self.dfm_models_dir = Path("dfm_models")
        self.kevin_hart_model = self.dfm_models_dir / "kevin_hart_model.dfm"
        self.backup_dir = self.dfm_models_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def diagnose_issue(self):
        """Diagnose the specific Kevin Hart model issue"""
        logger.info("🔍 Diagnosing Kevin Hart model issue...")
        
        if not self.kevin_hart_model.exists():
            logger.error(f"❌ Model file not found: {self.kevin_hart_model}")
            return False
        
        # Check file size
        file_size = self.kevin_hart_model.stat().st_size
        logger.info(f"📁 File size: {file_size:,} bytes")
        
        if file_size < 1024 * 1024:  # Less than 1MB
            logger.error("❌ File is too small - likely corrupted or incomplete")
            return False
        
        # Try to read file header
        try:
            with open(self.kevin_hart_model, 'rb') as f:
                header = f.read(100)
            
            if b'ONNX' in header:
                logger.info("✅ ONNX header found in file")
            else:
                logger.warning("⚠️ ONNX header not found - file may be corrupted")
            
            # Check for protobuf magic bytes
            if header.startswith(b'\x08'):
                logger.info("✅ Protobuf format detected")
            else:
                logger.warning("⚠️ Protobuf format not detected")
                
        except Exception as e:
            logger.error(f"❌ Error reading file: {e}")
            return False
        
        return True
    
    def create_backup(self):
        """Create backup of the original model"""
        timestamp = int(time.time())
        backup_path = self.backup_dir / f"kevin_hart_model_backup_{timestamp}.dfm"
        
        try:
            shutil.copy2(self.kevin_hart_model, backup_path)
            logger.info(f"✅ Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"❌ Failed to create backup: {e}")
            return None
    
    def attempt_fix_1_onnx_optimization(self):
        """Fix attempt 1: ONNX optimization"""
        logger.info("🔧 Attempting ONNX optimization fix...")
        
        try:
            import onnx
            import onnxruntime as ort
            
            # Load the model
            onnx_model = onnx.load(str(self.kevin_hart_model))
            
            # Try to optimize
            from onnxruntime.transformers import optimizer
            opt_model = optimizer.optimize_model(str(self.kevin_hart_model))
            
            # Save optimized version
            optimized_path = self.dfm_models_dir / "kevin_hart_model_optimized.onnx"
            opt_model.save_model_to_file(str(optimized_path))
            
            # Test the optimized model
            test_session = ort.InferenceSession(str(optimized_path))
            logger.info("✅ ONNX optimization successful!")
            
            # Replace original with optimized
            shutil.move(str(optimized_path), str(self.kevin_hart_model))
            return True
            
        except ImportError as e:
            logger.warning(f"⚠️ ONNX optimization not available: {e}")
            return False
        except Exception as e:
            logger.warning(f"⚠️ ONNX optimization failed: {e}")
            return False
    
    def attempt_fix_2_protobuf_repair(self):
        """Fix attempt 2: Protobuf repair"""
        logger.info("🔧 Attempting protobuf repair...")
        
        try:
            # Read the file
            with open(self.kevin_hart_model, 'rb') as f:
                data = f.read()
            
            # Look for ONNX header
            onnx_start = data.find(b'ONNX')
            if onnx_start >= 0:
                logger.info(f"Found ONNX header at position {onnx_start}")
                
                # Extract from ONNX header onwards
                onnx_data = data[onnx_start:]
                
                # Try to parse as ONNX
                import onnx
                try:
                    onnx_model = onnx.load_from_string(onnx_data)
                    logger.info("✅ Protobuf repair successful!")
                    
                    # Save repaired model
                    onnx.save(onnx_model, str(self.kevin_hart_model))
                    return True
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse repaired protobuf: {e}")
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Protobuf repair failed: {e}")
            return False
    
    def attempt_fix_3_download_replacement(self):
        """Fix attempt 3: Download replacement model"""
        logger.info("🔧 Attempting to download replacement model...")
        
        # Known good Kevin Hart model URLs (if available)
        replacement_urls = [
            "https://github.com/iperov/DeepFaceLive/releases/download/KEVIN_HART/kevin_hart_model.dfm",
            # Add other known good URLs here
        ]
        
        try:
            import requests
            
            for url in replacement_urls:
                try:
                    logger.info(f"Trying to download from: {url}")
                    
                    response = requests.get(url, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    # Save to temporary file
                    temp_path = self.dfm_models_dir / "kevin_hart_model_temp.dfm"
                    with open(temp_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Validate the downloaded file
                    if self.validate_downloaded_model(temp_path):
                        # Replace original
                        shutil.move(str(temp_path), str(self.kevin_hart_model))
                        logger.info("✅ Replacement model downloaded and validated!")
                        return True
                    else:
                        temp_path.unlink()  # Delete invalid file
                        
                except Exception as e:
                    logger.warning(f"⚠️ Download from {url} failed: {e}")
                    continue
            
            return False
            
        except ImportError:
            logger.warning("⚠️ Requests library not available for download")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Download replacement failed: {e}")
            return False
    
    def validate_downloaded_model(self, model_path: Path) -> bool:
        """Validate a downloaded model file"""
        try:
            import onnx
            import onnxruntime as ort
            
            # Check file size
            if model_path.stat().st_size < 10 * 1024 * 1024:  # Less than 10MB
                return False
            
            # Try to load with ONNX
            onnx_model = onnx.load(str(model_path))
            onnx.checker.check_model(onnx_model)
            
            # Try to create ONNX Runtime session
            sess = ort.InferenceSession(str(model_path))
            
            # Check for required inputs
            inputs = sess.get_inputs()
            input_names = [inp.name for inp in inputs]
            
            if 'in_face' not in input_names:
                return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Model validation failed: {e}")
            return False
    
    def test_model(self):
        """Test if the model works after fixes"""
        logger.info("🧪 Testing model after fixes...")
        
        try:
            import onnxruntime as ort
            
            # Try to create inference session
            sess = ort.InferenceSession(str(self.kevin_hart_model))
            
            # Check inputs
            inputs = sess.get_inputs()
            logger.info(f"✅ Model loaded successfully!")
            logger.info(f"   Inputs: {[inp.name for inp in inputs]}")
            
            # Check outputs
            outputs = sess.get_outputs()
            logger.info(f"   Outputs: {[out.name for out in outputs]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Model test failed: {e}")
            return False
    
    def run_complete_fix(self):
        """Run the complete fix process"""
        logger.info("🚀 Starting Kevin Hart model fix process...")
        
        # Step 1: Diagnose
        if not self.diagnose_issue():
            logger.error("❌ Diagnosis failed - cannot proceed")
            return False
        
        # Step 2: Create backup
        backup_path = self.create_backup()
        if not backup_path:
            logger.error("❌ Backup creation failed - cannot proceed")
            return False
        
        # Step 3: Try fixes in order
        fixes = [
            ("ONNX Optimization", self.attempt_fix_1_onnx_optimization),
            ("Protobuf Repair", self.attempt_fix_2_protobuf_repair),
            ("Download Replacement", self.attempt_fix_3_download_replacement)
        ]
        
        for fix_name, fix_func in fixes:
            logger.info(f"🔧 Trying {fix_name}...")
            if fix_func():
                logger.info(f"✅ {fix_name} succeeded!")
                
                # Test the fixed model
                if self.test_model():
                    logger.info("🎉 Model successfully fixed and tested!")
                    return True
                else:
                    logger.warning(f"⚠️ {fix_name} succeeded but model test failed")
            else:
                logger.warning(f"⚠️ {fix_name} failed")
        
        logger.error("❌ All fix attempts failed")
        logger.info(f"💾 Original model backed up to: {backup_path}")
        return False

def main():
    """Main function"""
    fixer = KevinHartModelFixer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--diagnose":
        # Just diagnose
        fixer.diagnose_issue()
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Just test
        fixer.test_model()
    else:
        # Run complete fix
        success = fixer.run_complete_fix()
        if success:
            print("\n🎉 Kevin Hart model successfully fixed!")
            print("You can now use the model in DeepFaceLive.")
        else:
            print("\n❌ Fix failed. Check the logs for details.")
            print("You may need to manually download a replacement model.")

if __name__ == "__main__":
    main() 
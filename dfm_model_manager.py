#!/usr/bin/env python3
"""
DFM Model Manager
Handles placeholder files, downloads real models, and manages the DFM model collection
"""

import os
import sys
import json
import shutil
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DFMModelManager:
    """Manages DFM models including placeholder handling and downloads"""
    
    def __init__(self, dfm_models_dir: str = "dfm_models"):
        self.dfm_models_dir = Path(dfm_models_dir)
        self.backup_dir = self.dfm_models_dir / "backups"
        self.temp_dir = self.dfm_models_dir / "temp"
        
        # Create necessary directories
        self.backup_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Known model URLs (from DeepFaceLive releases)
        self.model_urls = {
            "kevin_hart_model": {
                "url": "https://github.com/iperov/DeepFaceLive/releases/download/KEVIN_HART/kevin_hart_model.dfm",
                "size_mb": 150,  # Approximate size
                "description": "Kevin Hart face swap model"
            },
            "tom_cruise_model": {
                "url": "https://github.com/iperov/DeepFaceLive/releases/download/TOM_CRUISE/tom_cruise_model.dfm",
                "size_mb": 150,
                "description": "Tom Cruise face swap model"
            },
            "leonardo_dicaprio_model": {
                "url": "https://github.com/iperov/DeepFaceLive/releases/download/LEONARDO_DICAPRIO/leonardo_dicaprio_model.dfm",
                "size_mb": 150,
                "description": "Leonardo DiCaprio face swap model"
            }
        }
    
    def analyze_model_file(self, model_path: Path) -> Dict:
        """Analyze a model file to determine its type and status"""
        result = {
            'path': str(model_path),
            'exists': False,
            'size': 0,
            'type': 'unknown',
            'is_valid': False,
            'is_placeholder': False,
            'needs_download': False,
            'errors': [],
            'warnings': []
        }
        
        if not model_path.exists():
            result['errors'].append("File does not exist")
            return result
        
        result['exists'] = True
        result['size'] = model_path.stat().st_size
        
        try:
            # Try to read as JSON first (placeholder check)
            with open(model_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if content.strip().startswith('{'):
                try:
                    json_data = json.loads(content)
                    if 'is_placeholder' in json_data and json_data['is_placeholder']:
                        result['type'] = 'placeholder'
                        result['is_placeholder'] = True
                        result['needs_download'] = True
                        result['warnings'].append("This is a placeholder file, not a real model")
                        return result
                except json.JSONDecodeError:
                    pass
            
            # Try to read as binary (real model check)
            with open(model_path, 'rb') as f:
                header = f.read(100)
            
            # Check for ONNX header
            if b'ONNX' in header:
                result['type'] = 'onnx'
                # Validate ONNX model
                onnx_validation = self._validate_onnx_model(model_path)
                result.update(onnx_validation)
            else:
                result['type'] = 'unknown'
                result['errors'].append("Not a valid ONNX model")
                
        except Exception as e:
            result['errors'].append(f"Analysis failed: {str(e)}")
        
        return result
    
    def _validate_onnx_model(self, model_path: Path) -> Dict:
        """Validate ONNX model structure"""
        result = {
            'onnx_valid': False,
            'onnx_errors': [],
            'input_info': None,
            'output_info': None
        }
        
        try:
            import onnx
            import onnxruntime as ort
            
            # Load ONNX model
            onnx_model = onnx.load(str(model_path))
            onnx.checker.check_model(onnx_model)
            
            # Get model info
            inputs = onnx_model.graph.input
            outputs = onnx_model.graph.output
            
            result['onnx_valid'] = True
            result['input_info'] = [{'name': inp.name, 'shape': [d.dim_value for d in inp.type.tensor_type.shape.dim]} for inp in inputs]
            result['output_info'] = [{'name': out.name, 'shape': [d.dim_value for d in out.type.tensor_type.shape.dim]} for out in outputs]
            
            # Check for required inputs (DFM models should have 'in_face' input)
            input_names = [inp.name for inp in inputs]
            if 'in_face' not in input_names:
                result['onnx_errors'].append("Missing required input 'in_face'")
            
            # Try to create ONNX Runtime session
            try:
                sess = ort.InferenceSession(str(model_path))
                result['ort_session_created'] = True
            except Exception as e:
                result['ort_session_created'] = False
                result['onnx_errors'].append(f"ONNX Runtime session creation failed: {str(e)}")
            
        except ImportError as e:
            result['onnx_errors'].append(f"ONNX libraries not available: {str(e)}")
        except Exception as e:
            result['onnx_errors'].append(f"ONNX validation failed: {str(e)}")
        
        return result
    
    def download_model(self, model_name: str, force: bool = False) -> bool:
        """Download a model from the known URLs"""
        if model_name not in self.model_urls:
            logger.error(f"❌ Unknown model: {model_name}")
            return False
        
        model_info = self.model_urls[model_name]
        model_path = self.dfm_models_dir / f"{model_name}.dfm"
        
        # Check if model already exists and is valid
        if not force and model_path.exists():
            analysis = self.analyze_model_file(model_path)
            if analysis['is_valid'] and not analysis['is_placeholder']:
                logger.info(f"✅ Model {model_name} already exists and is valid")
                return True
        
        # Create backup if file exists
        if model_path.exists():
            backup_path = self.backup_dir / f"{model_name}_backup_{int(time.time())}.dfm"
            shutil.copy2(model_path, backup_path)
            logger.info(f"💾 Created backup: {backup_path}")
        
        # Download the model
        try:
            import requests
            
            url = model_info['url']
            logger.info(f"📥 Downloading {model_name} from: {url}")
            logger.info(f"📊 Expected size: ~{model_info['size_mb']}MB")
            
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Get total size for progress tracking
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress
            temp_path = self.temp_dir / f"{model_name}_temp.dfm"
            downloaded_size = 0
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Show progress
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            logger.info(f"📥 Download progress: {progress:.1f}% ({downloaded_size/1024/1024:.1f}MB)")
            
            # Validate downloaded file
            if self._validate_downloaded_model(temp_path, model_info):
                # Move to final location
                shutil.move(str(temp_path), str(model_path))
                logger.info(f"✅ Successfully downloaded {model_name}")
                return True
            else:
                temp_path.unlink()  # Delete invalid file
                logger.error(f"❌ Downloaded file validation failed for {model_name}")
                return False
                
        except ImportError:
            logger.error("❌ Requests library not available. Install with: pip install requests")
            return False
        except Exception as e:
            logger.error(f"❌ Download failed for {model_name}: {str(e)}")
            return False
    
    def _validate_downloaded_model(self, model_path: Path, model_info: Dict) -> bool:
        """Validate a downloaded model file"""
        try:
            # Check file size (should be reasonable)
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            expected_size_mb = model_info['size_mb']
            
            if file_size_mb < expected_size_mb * 0.5:  # Less than 50% of expected
                logger.warning(f"⚠️ Downloaded file seems too small: {file_size_mb:.1f}MB (expected ~{expected_size_mb}MB)")
                return False
            
            # Try to validate as ONNX model
            analysis = self.analyze_model_file(model_path)
            if analysis['is_valid'] and not analysis['is_placeholder']:
                return True
            
            logger.warning(f"⚠️ Downloaded file is not a valid ONNX model")
            return False
            
        except Exception as e:
            logger.error(f"❌ Model validation failed: {str(e)}")
            return False
    
    def convert_placeholder_to_real_model(self, model_name: str) -> bool:
        """Convert a placeholder file to a real model by downloading"""
        model_path = self.dfm_models_dir / f"{model_name}.dfm"
        
        if not model_path.exists():
            logger.error(f"❌ Model file not found: {model_path}")
            return False
        
        # Analyze the file
        analysis = self.analyze_model_file(model_path)
        
        if not analysis['is_placeholder']:
            logger.info(f"✅ {model_name} is already a real model")
            return True
        
        logger.info(f"🔄 Converting placeholder {model_name} to real model...")
        
        # Extract model name from placeholder
        try:
            with open(model_path, 'r') as f:
                placeholder_data = json.load(f)
            
            actual_model_name = placeholder_data.get('model_name', model_name)
            logger.info(f"📝 Placeholder indicates model: {actual_model_name}")
            
            # Download the real model
            return self.download_model(actual_model_name, force=True)
            
        except Exception as e:
            logger.error(f"❌ Failed to read placeholder data: {str(e)}")
            return False
    
    def scan_all_models(self) -> Dict:
        """Scan all models in the directory"""
        results = {
            'total_models': 0,
            'valid_models': 0,
            'placeholder_models': 0,
            'corrupted_models': 0,
            'model_details': []
        }
        
        if not self.dfm_models_dir.exists():
            logger.error(f"❌ DFM models directory does not exist: {self.dfm_models_dir}")
            return results
        
        # Find all DFM files
        dfm_files = list(self.dfm_models_dir.glob("*.dfm"))
        results['total_models'] = len(dfm_files)
        
        logger.info(f"🔍 Found {len(dfm_files)} DFM model files")
        
        for model_file in dfm_files:
            model_name = model_file.stem
            logger.info(f"📋 Analyzing: {model_name}")
            
            analysis = self.analyze_model_file(model_file)
            results['model_details'].append(analysis)
            
            if analysis['is_valid']:
                results['valid_models'] += 1
            elif analysis['is_placeholder']:
                results['placeholder_models'] += 1
            else:
                results['corrupted_models'] += 1
        
        return results
    
    def auto_fix_all_placeholders(self) -> Dict:
        """Automatically convert all placeholder models to real models"""
        scan_results = self.scan_all_models()
        fix_results = {
            'attempted_conversions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'conversion_details': []
        }
        
        for model_detail in scan_results['model_details']:
            if model_detail['is_placeholder']:
                model_name = Path(model_detail['path']).stem
                fix_results['attempted_conversions'] += 1
                
                logger.info(f"🔄 Converting placeholder: {model_name}")
                if self.convert_placeholder_to_real_model(model_name):
                    fix_results['successful_conversions'] += 1
                    fix_results['conversion_details'].append({
                        'model': model_name,
                        'status': 'success'
                    })
                else:
                    fix_results['failed_conversions'] += 1
                    fix_results['conversion_details'].append({
                        'model': model_name,
                        'status': 'failed'
                    })
        
        return fix_results
    
    def generate_report(self, scan_results: Dict, fix_results: Dict = None) -> str:
        """Generate a detailed report"""
        report = []
        report.append("=" * 60)
        report.append("DFM MODEL ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append("SUMMARY:")
        report.append(f"  Total Models: {scan_results['total_models']}")
        report.append(f"  Valid Models: {scan_results['valid_models']}")
        report.append(f"  Placeholder Models: {scan_results['placeholder_models']}")
        report.append(f"  Corrupted Models: {scan_results['corrupted_models']}")
        report.append("")
        
        if fix_results:
            report.append("CONVERSION RESULTS:")
            report.append(f"  Attempted Conversions: {fix_results['attempted_conversions']}")
            report.append(f"  Successful Conversions: {fix_results['successful_conversions']}")
            report.append(f"  Failed Conversions: {fix_results['failed_conversions']}")
            report.append("")
        
        # Detailed model information
        report.append("DETAILED MODEL INFORMATION:")
        report.append("-" * 40)
        
        for model_detail in scan_results['model_details']:
            model_name = Path(model_detail['path']).name
            
            if model_detail['is_valid']:
                status = "✅ VALID"
            elif model_detail['is_placeholder']:
                status = "📝 PLACEHOLDER"
            else:
                status = "❌ CORRUPTED"
            
            report.append(f"{model_name}: {status}")
            report.append(f"  Size: {model_detail['size']:,} bytes")
            report.append(f"  Type: {model_detail['type']}")
            
            if model_detail['is_placeholder']:
                report.append(f"  🔄 Needs conversion to real model")
            elif not model_detail['is_valid']:
                for error in model_detail['errors']:
                    report.append(f"  Error: {error}")
            
            report.append("")
        
        return "\n".join(report)

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DFM Model Manager")
    parser.add_argument("--models-dir", default="dfm_models", help="Directory containing DFM models")
    parser.add_argument("--model", help="Analyze specific model file")
    parser.add_argument("--scan", action="store_true", help="Scan all models")
    parser.add_argument("--fix-placeholders", action="store_true", help="Convert placeholder models to real models")
    parser.add_argument("--download", help="Download specific model")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    
    args = parser.parse_args()
    
    manager = DFMModelManager(args.models_dir)
    
    if args.model:
        # Analyze specific model
        model_path = Path(args.model)
        if not model_path.is_absolute():
            model_path = manager.dfm_models_dir / model_path
        
        logger.info(f"🔍 Analyzing specific model: {model_path}")
        result = manager.analyze_model_file(model_path)
        
        print(f"\nModel: {model_path}")
        print(f"Type: {result['type']}")
        print(f"Valid: {result['is_valid']}")
        print(f"Placeholder: {result['is_placeholder']}")
        print(f"Size: {result['size']:,} bytes")
        
        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['warnings']:
            print("Warnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if result['is_placeholder']:
            print("\n🔄 This is a placeholder file. To convert to real model:")
            print(f"  python dfm_model_manager.py --download {model_path.stem}")
    
    elif args.download:
        # Download specific model
        logger.info(f"📥 Downloading model: {args.download}")
        if manager.download_model(args.download):
            print(f"✅ Successfully downloaded {args.download}")
        else:
            print(f"❌ Failed to download {args.download}")
    
    elif args.scan or args.fix_placeholders:
        # Scan all models
        logger.info("🔍 Scanning all DFM models...")
        scan_results = manager.scan_all_models()
        
        if args.fix_placeholders:
            logger.info("🔄 Converting placeholder models to real models...")
            fix_results = manager.auto_fix_all_placeholders()
        else:
            fix_results = None
        
        if args.report:
            report = manager.generate_report(scan_results, fix_results)
            print(report)
            
            # Save report to file
            report_file = manager.dfm_models_dir / "model_analysis_report.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            logger.info(f"📄 Report saved to: {report_file}")
        else:
            # Simple summary
            print(f"\nScan Results:")
            print(f"  Total: {scan_results['total_models']}")
            print(f"  Valid: {scan_results['valid_models']}")
            print(f"  Placeholders: {scan_results['placeholder_models']}")
            print(f"  Corrupted: {scan_results['corrupted_models']}")
            
            if fix_results:
                print(f"\nConversion Results:")
                print(f"  Attempted: {fix_results['attempted_conversions']}")
                print(f"  Successful: {fix_results['successful_conversions']}")
                print(f"  Failed: {fix_results['failed_conversions']}")
    
    else:
        # Default: scan and show summary
        logger.info("🔍 Scanning all DFM models...")
        scan_results = manager.scan_all_models()
        
        print(f"\nDFM Model Scan Results:")
        print(f"  Total Models: {scan_results['total_models']}")
        print(f"  Valid Models: {scan_results['valid_models']}")
        print(f"  Placeholder Models: {scan_results['placeholder_models']}")
        print(f"  Corrupted Models: {scan_results['corrupted_models']}")
        
        if scan_results['placeholder_models'] > 0:
            print(f"\nTo convert placeholder models to real models, run:")
            print(f"  python dfm_model_manager.py --fix-placeholders --report")

if __name__ == "__main__":
    main() 
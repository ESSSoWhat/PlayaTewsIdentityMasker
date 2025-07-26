#!/usr/bin/env python3
"""
DFM Model Validator and Repair Utility
Diagnoses and fixes corrupted DFM model files that cause ONNX Runtime protobuf errors
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DFMModelValidator:
    """Validates and repairs DFM model files"""
    
    def __init__(self, dfm_models_dir: str = "dfm_models"):
        self.dfm_models_dir = Path(dfm_models_dir)
        self.backup_dir = self.dfm_models_dir / "backups"
        self.repair_dir = self.dfm_models_dir / "repair"
        
        # Create necessary directories
        self.backup_dir.mkdir(exist_ok=True)
        self.repair_dir.mkdir(exist_ok=True)
        
        # Known good model hashes (for verification)
        self.known_hashes = {
            # Add known good model hashes here if available
        }
    
    def validate_model(self, model_path: Path) -> Dict:
        """Validate a single DFM model file"""
        result = {
            'model_path': str(model_path),
            'exists': False,
            'size': 0,
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'file_hash': None,
            'can_repair': False
        }
        
        try:
            # Check if file exists
            if not model_path.exists():
                result['errors'].append("Model file does not exist")
                return result
            
            result['exists'] = True
            result['size'] = model_path.stat().st_size
            
            # Check file size (DFM models are typically 50MB+)
            if result['size'] < 10 * 1024 * 1024:  # Less than 10MB
                result['warnings'].append("File size seems too small for a DFM model")
            
            # Calculate file hash
            result['file_hash'] = self._calculate_file_hash(model_path)
            
            # Try to load with ONNX Runtime
            onnx_validation = self._validate_onnx_model(model_path)
            result.update(onnx_validation)
            
            # Check if we can repair it
            result['can_repair'] = self._can_repair_model(model_path, result)
            
        except Exception as e:
            result['errors'].append(f"Validation failed: {str(e)}")
        
        return result
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _validate_onnx_model(self, model_path: Path) -> Dict:
        """Validate ONNX model structure"""
        result = {
            'onnx_valid': False,
            'onnx_errors': [],
            'input_info': None,
            'output_info': None
        }
        
        try:
            # Try to import ONNX
            import onnx
            import onnxruntime as ort
            
            # Load ONNX model
            onnx_model = onnx.load(str(model_path))
            
            # Validate ONNX model
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
    
    def _can_repair_model(self, model_path: Path, validation_result: Dict) -> bool:
        """Determine if model can be repaired"""
        # Can repair if:
        # 1. File exists and has reasonable size
        # 2. ONNX validation failed but file structure seems intact
        # 3. Not completely corrupted
        
        if not validation_result['exists']:
            return False
        
        if validation_result['size'] < 1024:  # Less than 1KB
            return False
        
        # If ONNX validation failed but file exists and has size, we might be able to repair
        if not validation_result['onnx_valid'] and validation_result['size'] > 1024 * 1024:
            return True
        
        return False
    
    def repair_model(self, model_path: Path, validation_result: Dict) -> bool:
        """Attempt to repair a corrupted DFM model"""
        try:
            logger.info(f"Attempting to repair model: {model_path}")
            
            # Create backup
            backup_path = self.backup_dir / f"{model_path.stem}_backup_{int(time.time())}.dfm"
            shutil.copy2(model_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            
            # Try different repair strategies
            repair_strategies = [
                self._repair_strategy_1_onnx_optimize,
                self._repair_strategy_2_protobuf_fix,
                self._repair_strategy_3_rebuild_model
            ]
            
            for i, strategy in enumerate(repair_strategies, 1):
                logger.info(f"Trying repair strategy {i}...")
                if strategy(model_path, validation_result):
                    logger.info(f"Repair strategy {i} succeeded!")
                    return True
            
            logger.error("All repair strategies failed")
            return False
            
        except Exception as e:
            logger.error(f"Repair failed: {str(e)}")
            return False
    
    def _repair_strategy_1_onnx_optimize(self, model_path: Path, validation_result: Dict) -> bool:
        """Strategy 1: Try ONNX optimization"""
        try:
            import onnx
            import onnxruntime as ort
            
            # Load and optimize the model
            onnx_model = onnx.load(str(model_path))
            
            # Try to optimize the model
            from onnxruntime.transformers import optimizer
            opt_model = optimizer.optimize_model(str(model_path))
            
            # Save optimized model
            optimized_path = self.repair_dir / f"{model_path.stem}_optimized.onnx"
            opt_model.save_model_to_file(str(optimized_path))
            
            # Test if optimized model works
            test_result = self._validate_onnx_model(optimized_path)
            if test_result['onnx_valid']:
                # Replace original with optimized
                shutil.move(str(optimized_path), str(model_path))
                return True
                
        except Exception as e:
            logger.debug(f"ONNX optimization strategy failed: {str(e)}")
        
        return False
    
    def _repair_strategy_2_protobuf_fix(self, model_path: Path, validation_result: Dict) -> bool:
        """Strategy 2: Try protobuf repair"""
        try:
            # Read file and try to fix common protobuf issues
            with open(model_path, 'rb') as f:
                data = f.read()
            
            # Check for common protobuf corruption patterns
            if b'ONNX' in data[:100]:  # ONNX header present
                # Try to extract valid protobuf data
                onnx_start = data.find(b'ONNX')
                if onnx_start >= 0:
                    # Try to create a new file with just the ONNX data
                    fixed_path = self.repair_dir / f"{model_path.stem}_fixed.onnx"
                    with open(fixed_path, 'wb') as f:
                        f.write(data[onnx_start:])
                    
                    # Test if fixed model works
                    test_result = self._validate_onnx_model(fixed_path)
                    if test_result['onnx_valid']:
                        shutil.move(str(fixed_path), str(model_path))
                        return True
                        
        except Exception as e:
            logger.debug(f"Protobuf fix strategy failed: {str(e)}")
        
        return False
    
    def _repair_strategy_3_rebuild_model(self, model_path: Path, validation_result: Dict) -> bool:
        """Strategy 3: Try to rebuild from scratch (if we have source)"""
        try:
            # This would require access to the original training data
            # For now, just log that this strategy is not available
            logger.info("Rebuild strategy requires original training data - not available")
            return False
            
        except Exception as e:
            logger.debug(f"Rebuild strategy failed: {str(e)}")
        
        return False
    
    def scan_all_models(self) -> Dict:
        """Scan and validate all DFM models in the directory"""
        results = {
            'total_models': 0,
            'valid_models': 0,
            'corrupted_models': 0,
            'repairable_models': 0,
            'model_details': []
        }
        
        if not self.dfm_models_dir.exists():
            logger.error(f"DFM models directory does not exist: {self.dfm_models_dir}")
            return results
        
        # Find all DFM files
        dfm_files = list(self.dfm_models_dir.glob("*.dfm"))
        results['total_models'] = len(dfm_files)
        
        logger.info(f"Found {len(dfm_files)} DFM model files")
        
        for model_file in dfm_files:
            logger.info(f"Validating: {model_file.name}")
            validation_result = self.validate_model(model_file)
            results['model_details'].append(validation_result)
            
            if validation_result['is_valid']:
                results['valid_models'] += 1
            else:
                results['corrupted_models'] += 1
                if validation_result['can_repair']:
                    results['repairable_models'] += 1
        
        return results
    
    def auto_repair_all(self) -> Dict:
        """Automatically repair all repairable models"""
        scan_results = self.scan_all_models()
        repair_results = {
            'attempted_repairs': 0,
            'successful_repairs': 0,
            'failed_repairs': 0,
            'repair_details': []
        }
        
        for model_detail in scan_results['model_details']:
            if model_detail['can_repair'] and not model_detail['is_valid']:
                model_path = Path(model_detail['model_path'])
                repair_results['attempted_repairs'] += 1
                
                logger.info(f"Auto-repairing: {model_path.name}")
                if self.repair_model(model_path, model_detail):
                    repair_results['successful_repairs'] += 1
                    repair_results['repair_details'].append({
                        'model': model_path.name,
                        'status': 'success'
                    })
                else:
                    repair_results['failed_repairs'] += 1
                    repair_results['repair_details'].append({
                        'model': model_path.name,
                        'status': 'failed'
                    })
        
        return repair_results
    
    def generate_report(self, scan_results: Dict, repair_results: Dict = None) -> str:
        """Generate a detailed report"""
        report = []
        report.append("=" * 60)
        report.append("DFM MODEL VALIDATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append("SUMMARY:")
        report.append(f"  Total Models: {scan_results['total_models']}")
        report.append(f"  Valid Models: {scan_results['valid_models']}")
        report.append(f"  Corrupted Models: {scan_results['corrupted_models']}")
        report.append(f"  Repairable Models: {scan_results['repairable_models']}")
        report.append("")
        
        if repair_results:
            report.append("REPAIR RESULTS:")
            report.append(f"  Attempted Repairs: {repair_results['attempted_repairs']}")
            report.append(f"  Successful Repairs: {repair_results['successful_repairs']}")
            report.append(f"  Failed Repairs: {repair_results['failed_repairs']}")
            report.append("")
        
        # Detailed model information
        report.append("DETAILED MODEL INFORMATION:")
        report.append("-" * 40)
        
        for model_detail in scan_results['model_details']:
            model_name = Path(model_detail['model_path']).name
            status = "✅ VALID" if model_detail['is_valid'] else "❌ CORRUPTED"
            report.append(f"{model_name}: {status}")
            
            if not model_detail['is_valid']:
                for error in model_detail['errors']:
                    report.append(f"  Error: {error}")
                for warning in model_detail['warnings']:
                    report.append(f"  Warning: {warning}")
                
                if model_detail['can_repair']:
                    report.append(f"  🔧 Repairable: Yes")
                else:
                    report.append(f"  🔧 Repairable: No")
            
            report.append("")
        
        return "\n".join(report)

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DFM Model Validator and Repair Utility")
    parser.add_argument("--models-dir", default="dfm_models", help="Directory containing DFM models")
    parser.add_argument("--model", help="Validate specific model file")
    parser.add_argument("--scan", action="store_true", help="Scan all models")
    parser.add_argument("--repair", action="store_true", help="Auto-repair corrupted models")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    
    args = parser.parse_args()
    
    validator = DFMModelValidator(args.models_dir)
    
    if args.model:
        # Validate specific model
        model_path = Path(args.model)
        if not model_path.is_absolute():
            model_path = validator.dfm_models_dir / model_path
        
        logger.info(f"Validating specific model: {model_path}")
        result = validator.validate_model(model_path)
        
        print(f"\nModel: {model_path}")
        print(f"Valid: {result['is_valid']}")
        print(f"Size: {result['size']} bytes")
        print(f"Can Repair: {result['can_repair']}")
        
        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['warnings']:
            print("Warnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if args.repair and result['can_repair'] and not result['is_valid']:
            print("\nAttempting repair...")
            if validator.repair_model(model_path, result):
                print("✅ Repair successful!")
            else:
                print("❌ Repair failed!")
    
    elif args.scan or args.repair:
        # Scan all models
        logger.info("Scanning all DFM models...")
        scan_results = validator.scan_all_models()
        
        if args.repair:
            logger.info("Auto-repairing corrupted models...")
            repair_results = validator.auto_repair_all()
        else:
            repair_results = None
        
        if args.report:
            report = validator.generate_report(scan_results, repair_results)
            print(report)
            
            # Save report to file
            report_file = validator.dfm_models_dir / "validation_report.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to: {report_file}")
        else:
            # Simple summary
            print(f"\nScan Results:")
            print(f"  Total: {scan_results['total_models']}")
            print(f"  Valid: {scan_results['valid_models']}")
            print(f"  Corrupted: {scan_results['corrupted_models']}")
            print(f"  Repairable: {scan_results['repairable_models']}")
            
            if repair_results:
                print(f"\nRepair Results:")
                print(f"  Attempted: {repair_results['attempted_repairs']}")
                print(f"  Successful: {repair_results['successful_repairs']}")
                print(f"  Failed: {repair_results['failed_repairs']}")
    
    else:
        # Default: scan and show summary
        logger.info("Scanning all DFM models...")
        scan_results = validator.scan_all_models()
        
        print(f"\nDFM Model Scan Results:")
        print(f"  Total Models: {scan_results['total_models']}")
        print(f"  Valid Models: {scan_results['valid_models']}")
        print(f"  Corrupted Models: {scan_results['corrupted_models']}")
        print(f"  Repairable Models: {scan_results['repairable_models']}")
        
        if scan_results['corrupted_models'] > 0:
            print(f"\nTo repair corrupted models, run:")
            print(f"  python dfm_model_validator.py --repair --report")

if __name__ == "__main__":
    main() 
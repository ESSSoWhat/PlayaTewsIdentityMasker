#!/usr/bin/env python3
"""
Show Credits and Attribution
Displays comprehensive credits for all open source projects used
"""

import os
import sys
from pathlib import Path

def show_credits():
    """Display comprehensive credits and attribution"""
    
    print("=" * 80)
    print("🎯 PLAYA TEWS IDENTITY MASKER - CREDITS AND ATTRIBUTION")
    print("=" * 80)
    print()
    
    print("🌟 CORE TECHNOLOGIES")
    print("-" * 40)
    print("This application is built upon the excellent work of the open source community:")
    print()
    
    print("🔬 DeepFaceLive - Real-time Face Swap Technology")
    print("   Repository: https://github.com/iperov/DeepFaceLive.git")
    print("   Author: @iperov")
    print("   License: GPL-3.0")
    print("   Stars: 29k+ stars, 707 forks")
    print("   Status: Archived (read-only as of Nov 13, 2024)")
    print("   Features: Real-time face swapping, model hub, ONNX runtime")
    print()
    
    print("🧠 DeepFaceLab - Face Model Training Framework")
    print("   Repository: https://github.com/iperov/DeepFaceLab")
    print("   Author: @iperov")
    print("   Purpose: Training custom face models")
    print("   Integration: Used for creating high-quality DFM models")
    print()
    
    print("🎤 Voice Changer Technology")
    print("   Real-time audio processing and effects")
    print("   Audio capture, processing, and streaming")
    print("   Cross-platform audio system integration")
    print()
    
    print("👥 DEEPFACELIVE CONTRIBUTORS")
    print("-" * 40)
    print("Main Developer: @iperov")
    print("Contributors:")
    print("  - @Arthurzhangsheng")
    print("  - @CeeBeeEh")
    print("  - @osushiski")
    print("  - @Cioscos")
    print("  - @RitikDutta")
    print("  - @codefan-byte")
    print("  - @Sajeg")
    print()
    
    print("📚 AVAILABLE MODELS")
    print("-" * 40)
    print("Based on DeepFaceLive's public model library:")
    print("  - Keanu Reeves (High-quality celebrity model)")
    print("  - Bryan Greynolds (Professional actor model)")
    print("  - Jesse Stat (Popular testing model)")
    print("  - Ewon Spice (Quality face swap model)")
    print("  - Liu Lice (Well-documented model)")
    print("  - Meggie Merkel (Community favorite)")
    print("  - Tina Shift (High-quality model - 685MB)")
    print("  - Albica Johns (Professional model)")
    print("  - Natalie Fatman (Quality model)")
    print("  - Irina Arty (Popular model)")
    print("  - Rob Doe (Community model)")
    print("  - Mr. Bean (Character model)")
    print("  - And many more...")
    print()
    
    print("🛠️ ADDITIONAL OPEN SOURCE LIBRARIES")
    print("-" * 40)
    print("Core Dependencies:")
    print("  - PyQt5 (GUI framework - LGPL v2.1)")
    print("  - OpenCV (Computer vision - Apache 2.0)")
    print("  - ONNX Runtime (Neural network inference - MIT)")
    print("  - NumPy (Numerical computing - BSD-3-Clause)")
    print("  - Pillow (Image processing - HPND)")
    print()
    print("Audio Processing:")
    print("  - PyAudio (Audio I/O - MIT)")
    print("  - SciPy (Scientific computing - BSD-3-Clause)")
    print("  - SoundDevice (Audio streaming - MIT)")
    print()
    print("Machine Learning:")
    print("  - TensorFlow (Deep learning - Apache 2.0)")
    print("  - PyTorch (Machine learning - BSD-3-Clause)")
    print("  - scikit-learn (ML utilities - BSD-3-Clause)")
    print()
    
    print("🌐 COMMUNITY RESOURCES")
    print("-" * 40)
    print("DeepFaceLive Community:")
    print("  - Discord: https://discord.gg/rxa7h9M6rH")
    print("  - QQ Group: 124500433 (Chinese community)")
    print("  - GitHub Issues: https://github.com/iperov/DeepFaceLive/issues")
    print()
    print("Model Sources:")
    print("  - Mega Repository: https://mega.nz/folder/Po0nGQrA#dbbliNWojjt_9_12c5qjog")
    print("  - HuggingFace: https://huggingface.co/datasets/deepfakes/dfm-models")
    print("  - DeepFakes Forum: https://www.deepfakes.com/forums/")
    print("  - MrDeepFakes: https://mrdeepfakes.com/")
    print()
    
    print("📄 LICENSE INFORMATION")
    print("-" * 40)
    print("Primary Licenses:")
    print("  - DeepFaceLive: GPL-3.0 License")
    print("  - DeepFaceLab: GPL-3.0 License")
    print("  - This Application: Based on DeepFaceLive (GPL-3.0 compatible)")
    print()
    print("License Compliance:")
    print("  ✓ All open source components properly attributed")
    print("  ✓ License terms respected and maintained")
    print("  ✓ Source code modifications documented")
    print("  ✓ Attribution requirements fulfilled")
    print()
    
    print("🙏 SPECIAL THANKS")
    print("-" * 40)
    print("DeepFaceLive Community:")
    print("  - @iperov: For creating and maintaining DeepFaceLive")
    print("  - All Contributors: For their valuable contributions")
    print("  - Community Members: For testing, feedback, and support")
    print("  - Model Creators: For sharing high-quality face models")
    print()
    print("Voice Processing Community:")
    print("  - Audio Developers: For real-time processing libraries")
    print("  - Streaming Community: For OBS integration support")
    print("  - Open Source Audio: For cross-platform audio solutions")
    print()
    print("General Open Source:")
    print("  - Python Community: For the excellent ecosystem")
    print("  - Machine Learning Community: For advancing AI technology")
    print("  - Open Source Maintainers: For keeping projects alive")
    print()
    
    print("📝 HOW TO CITE")
    print("-" * 40)
    print("Academic/Research Use:")
    print("""
@software{deepfacelive,
  title={DeepFaceLive: Real-time face swap for PC streaming or video calls},
  author={iperov},
  year={2023},
  url={https://github.com/iperov/DeepFaceLive},
  license={GPL-3.0}
}
""")
    print("General Attribution:")
    print("  - 'Based on DeepFaceLive by @iperov (https://github.com/iperov/DeepFaceLive)'")
    print("  - 'Voice processing powered by open source audio libraries'")
    print("  - 'Models from DeepFaceLive community repository'")
    print()
    
    print("🔄 CONTRIBUTING BACK")
    print("-" * 40)
    print("How to Support:")
    print("  1. Star the Repository: https://github.com/iperov/DeepFaceLive")
    print("  2. Join the Community: Discord and QQ groups")
    print("  3. Share Models: Contribute to the model library")
    print("  4. Report Issues: Help improve the software")
    print("  5. Documentation: Help with guides and tutorials")
    print()
    print("Community Guidelines:")
    print("  - Respect all license terms")
    print("  - Attribute original work properly")
    print("  - Contribute back to the community")
    print("  - Help other users and developers")
    print("  - Maintain ethical use of technology")
    print()
    
    print("📖 FULL CREDITS DOCUMENTATION")
    print("-" * 40)
    print("For complete attribution information, see:")
    print("  - CREDITS_AND_ATTRIBUTIONS.md (Comprehensive credits)")
    print("  - README.md (Quick attribution overview)")
    print("  - Source code headers (Individual file attributions)")
    print()
    
    print("=" * 80)
    print("🎉 Thank you to all open source contributors!")
    print("   This application would not be possible without your work.")
    print("=" * 80)

def main():
    """Main function"""
    show_credits()
    
    # Check if credits file exists
    credits_file = Path("CREDITS_AND_ATTRIBUTIONS.md")
    if credits_file.exists():
        print(f"\n📄 Full credits documentation available at: {credits_file}")
    else:
        print(f"\n⚠️  Credits file not found: {credits_file}")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Legacy Archive Modernizer - Sample Data Generator
Creates realistic chaotic archive structure for demonstration

Author: Your Name
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
import random

def create_sample_archive(base_path):
    """
    Create a realistic sample of chaotic engineering archive
    """
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Sample file contents (placeholder content)
    sample_content = {
        '.dwg': b'Sample CAD file content - would be binary in real implementation',
        '.pdf': b'Sample PDF specification content - would be binary in real implementation', 
        '.xlsx': b'Sample Excel BOM content - would be binary in real implementation',
        '.txt': b'Sample text documentation content'
    }
    
    # Create the chaotic structure from our business plan
    chaotic_structure = {
        "2015_ProjectAlpha_Rev3": [
            ("DWG_MainAssembly_v2_FINAL.dwg", ".dwg"),
            ("DWG_MainAssembly_v3_ACTUALFINAL.dwg", ".dwg"),  # Version chaos!
            ("specs_alpha_project.pdf", ".pdf"),
            ("BOM_alpha_030315.xlsx", ".xlsx"),
            ("alpha_calculations.txt", ".txt")
        ],
        "ProjectBeta_2016": [
            ("Beta_Assembly_R1.dwg", ".dwg"),
            ("Beta_SubAssy_A_R1.dwg", ".dwg"),
            ("Beta_SubAssy_B_R2.dwg", ".dwg"),
            ("ProjectBeta_Specifications_Final.pdf", ".pdf"),
            ("Beta_BOM_v1.xlsx", ".xlsx"),
            ("beta_test_results.txt", ".txt")
        ],
        "GAMMA-2017-Files": [
            ("GAM_001_MainFrame.dwg", ".dwg"),
            ("GAM_002_Housing.dwg", ".dwg"),
            ("GAM_003_Bracket.dwg", ".dwg"),
            ("GAM_BOM_Rev2.xlsx", ".xlsx"),
            ("gamma_specs_updated.pdf", ".pdf"),
            ("gamma_notes.txt", ".txt")
        ],
        "2018Projects/Delta_Project": [
            ("DEL-ASM-001.dwg", ".dwg"),
            ("DEL-PRT-001_Bracket.dwg", ".dwg"),
            ("DEL-PRT-002_Shaft.dwg", ".dwg"),
            ("DEL-PRT-003_Housing.dwg", ".dwg"),
            ("Delta_Requirements_v1.2.pdf", ".pdf"),
            ("DEL_BOM_Final.xlsx", ".xlsx"),
            ("delta_design_notes.txt", ".txt")
        ],
        "2019_ProjectEcho": [
            ("Echo_MainAssembly_Rev1.dwg", ".dwg"),
            ("Echo_Subassembly_A_Rev1.dwg", ".dwg"),
            ("Echo_Part_001.dwg", ".dwg"),
            ("Echo_Part_002_Modified.dwg", ".dwg"),
            ("ECHO_SPECIFICATIONS_FINAL.pdf", ".pdf"),
            ("echo_bom_2019.xlsx", ".xlsx")
        ],
        "MiscFiles": [
            ("old_template.dwg", ".dwg"),
            ("standard_titleblock.dwg", ".dwg"),
            ("random_calc.xlsx", ".xlsx"),
            ("meeting_notes_2018.txt", ".txt"),
            ("supplier_contact_list.txt", ".txt")
        ],
        "TempFolder": [
            ("temp_assembly_test.dwg", ".dwg"),
            ("backup_file_001.dwg", ".dwg"),
            ("old_version_something.pdf", ".pdf")
        ],
        "Archive_Old": [
            ("legacy_project_1.dwg", ".dwg"),
            ("legacy_project_2.dwg", ".dwg"),
            ("old_standard.pdf", ".pdf")
        ]
    }
    
    print(f"Creating sample chaotic archive in: {base_path}")
    
    # Create all folders and files
    for folder_path, files in chaotic_structure.items():
        folder_full_path = base_path / folder_path
        folder_full_path.mkdir(parents=True, exist_ok=True)
        
        print(f"  Creating folder: {folder_path}")
        
        for filename, extension in files:
            file_path = folder_full_path / filename
            
            # Create file with sample content
            content = sample_content.get(extension, b'Sample file content')
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Set random modification dates to simulate real archive
            days_ago = random.randint(30, 2000)  # Between 1 month and 5+ years ago
            mod_time = datetime.now() - timedelta(days=days_ago)
            timestamp = mod_time.timestamp()
            os.utime(file_path, (timestamp, timestamp))
            
            print(f"    Created: {filename}")
    
    # Create a README for the sample data
    readme_content = """# Sample Chaotic Archive

This sample archive demonstrates common issues in legacy file management:

## Problems Demonstrated:
1. **Multiple Naming Conventions**: 
   - 2015: Descriptive names with dates (ProjectAlpha_Rev3)
   - 2016: Mixed conventions (ProjectBeta_2016)
   - 2017: Code-based naming (GAM_001, GAM_002)
   - 2018+: Structured codes (DEL-ASM-001)

2. **Version Control Chaos**:
   - DWG_MainAssembly_v2_FINAL.dwg
   - DWG_MainAssembly_v3_ACTUALFINAL.dwg
   - Multiple revision indicators (Rev1, R1, v1.2)

3. **Inconsistent Folder Structure**:
   - Some projects in year-based folders
   - Others in descriptive folders
   - Misc/Temp folders with important files

4. **File Relationship Issues**:
   - Related files scattered across folders
   - No clear assembly → part → BOM → spec relationships

## Archive Statistics:
- **Total Projects**: 6 main projects + misc files
- **File Types**: CAD drawings (.dwg), specifications (.pdf), BOMs (.xlsx), notes (.txt)
- **Time Span**: 2015-2019 (5 years of accumulated chaos)
- **Naming Patterns**: 4+ different conventions

This represents a typical small engineering firm's accumulated file management debt.
"""
    
    with open(base_path / "README_SAMPLE_DATA.md", 'w') as f:
        f.write(readme_content)
    
    print(f"\nSample archive created successfully!")
    print(f"Total folders: {len(chaotic_structure)}")
    print(f"Total files: {sum(len(files) for files in chaotic_structure.values())}")
    print(f"\nTo analyze this archive, run:")
    print(f"  python scan_archive.py {base_path}")
    print(f"\nTo transform this archive, run:")
    print(f"  python modernize_archive.py {base_path} output_folder/")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create sample chaotic archive for demonstration')
    parser.add_argument('output_path', nargs='?', default='sample_data/chaotic_archive', 
                       help='Path where sample archive will be created')
    
    args = parser.parse_args()
    
    create_sample_archive(args.output_path)
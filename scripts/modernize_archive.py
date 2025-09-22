#!/usr/bin/env python3
"""
Legacy Archive Modernizer - Transformation Engine
Systematically transforms legacy archives while preserving relationships

Based on real-world enterprise migration experience.
Author: Your Name
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArchiveTransformer:
    """
    Comprehensive archive transformation engine that applies systematic
    naming conventions while preserving all file relationships.
    """
    
    def __init__(self, source_path, target_path, transformation_rules=None):
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        self.transformation_rules = transformation_rules or self._default_rules()
        self.transformation_log = []
        self.project_counter = 1
        self.project_mappings = {}
        
    def _default_rules(self):
        """
        Default transformation rules for engineering archives
        """
        return {
            'project_prefix': 'P',
            'project_digits': 3,
            'revision_format': 'R{number}',
            'folder_structure': {
                'drawings': 'Drawings',
                'documentation': 'Documentation', 
                'bom': 'BOM',
                'standards': 'Standards'
            },
            'file_type_mapping': {
                '.dwg': 'drawings',
                '.pdf': 'documentation',
                '.xlsx': 'bom',
                '.xls': 'bom',
                '.doc': 'documentation',
                '.docx': 'documentation'
            },
            'naming_convention': '{project_id}-{type_code}-{sequence}_{description}_{revision}.{ext}'
        }
    
    def transform_archive(self):
        """
        Main transformation pipeline
        """
        logger.info(f"Starting transformation: {self.source_path} -> {self.target_path}")
        
        # Phase 1: Analyze source structure
        projects = self._discover_projects()
        
        # Phase 2: Create target structure
        self._create_target_structure()
        
        # Phase 3: Transform each project
        for project in projects:
            self._transform_project(project)
        
        # Phase 4: Generate transformation report
        return self._generate_transformation_report()
    
    def _discover_projects(self):
        """
        Discover and group files by project
        """
        logger.info("Discovering project structure...")
        
        projects = {}
        
        for root, dirs, files in os.walk(self.source_path):
            if not files:
                continue
                
            folder_path = Path(root)
            relative_path = folder_path.relative_to(self.source_path)
            
            # Determine project identity from folder structure
            project_id = self._identify_project_from_path(relative_path)
            
            if project_id not in projects:
                projects[project_id] = {
                    'original_name': project_id,
                    'files': [],
                    'source_folders': set(),
                    'year': self._extract_year_from_path(relative_path)
                }
            
            # Add files to project
            for file in files:
                file_path = folder_path / file
                file_info = {
                    'source_path': file_path,
                    'filename': file,
                    'extension': file_path.suffix.lower(),
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                    'relative_path': relative_path
                }
                projects[project_id]['files'].append(file_info)
                projects[project_id]['source_folders'].add(str(relative_path))
        
        logger.info(f"Discovered {len(projects)} projects")
        return projects
    
    def _identify_project_from_path(self, relative_path):
        """
        Extract project identifier from path structure
        """
        path_str = str(relative_path)
        
        # Pattern 1: Direct project folder (ProjectAlpha, ProjectBeta, etc.)
        if 'project' in path_str.lower():
            match = re.search(r'project[_\s]*([a-zA-Z]+)', path_str, re.IGNORECASE)
            if match:
                return match.group(1).title()
        
        # Pattern 2: Year-based grouping
        if re.search(r'20\d{2}', path_str):
            year = re.search(r'(20\d{2})', path_str).group(1)
            # Look for project name after year
            remaining = re.sub(r'20\d{2}[_\s]*', '', path_str, flags=re.IGNORECASE)
            if remaining:
                project_name = re.split(r'[_\s/\\]+', remaining)[0]
                return f"{project_name}_{year}"
            return f"Project_{year}"
        
        # Pattern 3: Code-based (GAM, DEL, etc.)
        code_match = re.search(r'([A-Z]{2,4})[-_]', path_str)
        if code_match:
            return code_match.group(1)
        
        # Pattern 4: First meaningful folder name
        parts = [p for p in relative_path.parts if p and not p.startswith('.')]
        if parts:
            return parts[0].replace(' ', '_').title()
        
        return "Unknown_Project"
    
    def _extract_year_from_path(self, relative_path):
        """
        Extract year from path or filename for chronological organization
        """
        path_str = str(relative_path)
        year_match = re.search(r'(20\d{2})', path_str)
        if year_match:
            return int(year_match.group(1))
        return 2020  # Default fallback year
    
    def _create_target_structure(self):
        """
        Create standardized target directory structure
        """
        logger.info("Creating target directory structure...")
        
        self.target_path.mkdir(parents=True, exist_ok=True)
        
        # Create main structure
        (self.target_path / "Projects").mkdir(exist_ok=True)
        (self.target_path / "Standards").mkdir(exist_ok=True)
        (self.target_path / "Standards" / "Templates").mkdir(exist_ok=True)
        (self.target_path / "Migration_Reports").mkdir(exist_ok=True)
    
    def _transform_project(self, project_data):
        """
        Transform a single project with all its files
        """
        original_name = project_data['original_name']
        project_year = project_data['year']
        
        # Generate new project ID
        new_project_id = f"{self.transformation_rules['project_prefix']}{self.project_counter:0{self.transformation_rules['project_digits']}d}"
        
        # Create descriptive project folder name
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', original_name)
        project_folder_name = f"{new_project_id}_{clean_name}_{project_year}"
        
        # Store mapping for cross-references
        self.project_mappings[original_name] = {
            'new_id': new_project_id,
            'folder_name': project_folder_name,
            'original_name': original_name
        }
        
        logger.info(f"Transforming project: {original_name} -> {project_folder_name}")
        
        # Create project directory structure
        project_base = self.target_path / "Projects" / project_folder_name
        project_base.mkdir(exist_ok=True)
        
        # Create subdirectories for different file types
        for subdir in self.transformation_rules['folder_structure'].values():
            (project_base / subdir).mkdir(exist_ok=True)
        
        # Transform and organize files
        file_counters = {'ASM': 1, 'PRT': 1, 'SPEC': 1, 'BOM': 1, 'MISC': 1}
        
        for file_info in project_data['files']:
            self._transform_file(file_info, new_project_id, project_base, file_counters)
        
        self.project_counter += 1
    
    def _transform_file(self, file_info, project_id, project_base, file_counters):
        """
        Transform a single file with new naming convention
        """
        source_path = file_info['source_path']
        original_filename = file_info['filename']
        extension = file_info['extension']
        
        # Determine file type and target folder
        file_category = self.transformation_rules['file_type_mapping'].get(extension, 'misc')
        target_folder = project_base / self.transformation_rules['folder_structure'].get(file_category, 'Misc')
        
        # Determine file type code
        type_code = self._determine_type_code(original_filename, extension)
        
        # Extract revision information
        revision = self._extract_revision(original_filename)
        
        # Generate clean description
        description = self._generate_description(original_filename, type_code)
        
        # Generate new filename
        sequence = f"{file_counters[type_code]:03d}"
        new_filename = self.transformation_rules['naming_convention'].format(
            project_id=project_id,
            type_code=type_code,
            sequence=sequence,
            description=description,
            revision=revision,
            ext=extension[1:]  # Remove leading dot
        )
        
        # Ensure filename is filesystem-safe
        new_filename = re.sub(r'[<>:"/\\|?*]', '_', new_filename)
        
        target_path = target_folder / new_filename
        
        # Copy file with transformation logging
        try:
            shutil.copy2(source_path, target_path)
            
            # Log transformation
            self.transformation_log.append({
                'timestamp': datetime.now().isoformat(),
                'source_path': str(source_path),
                'target_path': str(target_path),
                'original_filename': original_filename,
                'new_filename': new_filename,
                'project_id': project_id,
                'file_size': file_info['size'],
                'status': 'SUCCESS'
            })
            
            file_counters[type_code] += 1
            
        except Exception as e:
            logger.error(f"Failed to transform {original_filename}: {e}")
            self.transformation_log.append({
                'timestamp': datetime.now().isoformat(),
                'source_path': str(source_path),
                'original_filename': original_filename,
                'error': str(e),
                'status': 'FAILED'
            })
    
    def _determine_type_code(self, filename, extension):
        """
        Determine standardized type code based on filename and extension
        """
        filename_lower = filename.lower()
        
        # CAD file type determination
        if extension == '.dwg':
            if any(word in filename_lower for word in ['assembly', 'asm', 'main']):
                return 'ASM'
            else:
                return 'PRT'
        
        # Document type determination
        elif extension == '.pdf':
            if any(word in filename_lower for word in ['spec', 'requirement', 'standard']):
                return 'SPEC'
            else:
                return 'DOC'
        
        # Spreadsheet type determination
        elif extension in ['.xlsx', '.xls']:
            if any(word in filename_lower for word in ['bom', 'bill', 'material']):
                return 'BOM'
            else:
                return 'DATA'
        
        return 'MISC'
    
    def _extract_revision(self, filename):
        """
        Extract and standardize revision information
        """
        # Look for various revision patterns
        patterns = [
            r'[rR]ev\s*(\d+)',
            r'[rR](\d+)',
            r'[vV]\s*(\d+)',
            r'Rev\s*([A-Z])',
            r'_(\d+)(?=\.[^.]*$)'  # Number before extension
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                rev_value = match.group(1)
                if rev_value.isdigit():
                    return f"R{rev_value}"
                else:
                    return f"R{ord(rev_value.upper()) - ord('A') + 1}"
        
        return "R1"  # Default revision
    
    def _generate_description(self, filename, type_code):
        """
        Generate clean, descriptive name from original filename
        """
        # Remove common prefixes and suffixes
        clean_name = filename
        
        # Remove extension
        clean_name = re.sub(r'\.[^.]*, '', clean_name)
        
        # Remove version/revision indicators
        clean_name = re.sub(r'[vV]?\d+|[rR]ev?\d*|final|FINAL|actualfinal', '', clean_name, flags=re.IGNORECASE)
        
        # Remove project codes and type indicators
        clean_name = re.sub(r'^[A-Z]{2,4}[-_]', '', clean_name)
        clean_name = re.sub(r'dwg|pdf|xlsx?|assembly|asm|part|prt', '', clean_name, flags=re.IGNORECASE)
        
        # Clean up separators and spaces
        clean_name = re.sub(r'[-_\s]+', '_', clean_name)
        clean_name = clean_name.strip('_')
        
        # If nothing meaningful left, use type-based default
        if not clean_name or len(clean_name) < 3:
            defaults = {
                'ASM': 'MainAssembly',
                'PRT': 'Component',
                'SPEC': 'Specification',
                'BOM': 'BillOfMaterials',
                'DOC': 'Document',
                'DATA': 'DataSheet'
            }
            clean_name = defaults.get(type_code, 'File')
        
        # Capitalize properly
        clean_name = ''.join(word.capitalize() for word in clean_name.split('_'))
        
        return clean_name[:30]  # Limit length
    
    def _generate_transformation_report(self):
        """
        Generate comprehensive transformation report
        """
        logger.info("Generating transformation report...")
        
        # Calculate statistics
        total_files = len(self.transformation_log)
        successful_files = len([log for log in self.transformation_log if log['status'] == 'SUCCESS'])
        failed_files = total_files - successful_files
        total_size = sum(log.get('file_size', 0) for log in self.transformation_log if log['status'] == 'SUCCESS')
        
        # Create report
        report = {
            'transformation_summary': {
                'timestamp': datetime.now().isoformat(),
                'source_path': str(self.source_path),
                'target_path': str(self.target_path),
                'total_projects': len(self.project_mappings),
                'total_files_processed': total_files,
                'successful_transformations': successful_files,
                'failed_transformations': failed_files,
                'success_rate': round((successful_files / total_files * 100), 2) if total_files > 0 else 0,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            },
            'project_mappings': self.project_mappings,
            'transformation_rules': self.transformation_rules,
            'detailed_log': self.transformation_log
        }
        
        # Save report to target directory
        report_path = self.target_path / "Migration_Reports" / "transformation_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Create summary report
        summary_path = self.target_path / "Migration_Reports" / "transformation_summary.txt"
        with open(summary_path, 'w') as f:
            f.write("ARCHIVE TRANSFORMATION SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Transformation completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source: {self.source_path}\n")
            f.write(f"Target: {self.target_path}\n\n")
            f.write(f"Projects processed: {len(self.project_mappings)}\n")
            f.write(f"Files transformed: {successful_files}/{total_files}\n")
            f.write(f"Success rate: {report['transformation_summary']['success_rate']}%\n")
            f.write(f"Total size: {report['transformation_summary']['total_size_mb']} MB\n\n")
            
            f.write("PROJECT MAPPINGS:\n")
            f.write("-" * 30 + "\n")
            for original, mapping in self.project_mappings.items():
                f.write(f"{original} -> {mapping['folder_name']}\n")
            
            if failed_files > 0:
                f.write(f"\nFAILED TRANSFORMATIONS ({failed_files}):\n")
                f.write("-" * 30 + "\n")
                for log in self.transformation_log:
                    if log['status'] == 'FAILED':
                        f.write(f"{log['original_filename']}: {log.get('error', 'Unknown error')}\n")
        
        logger.info(f"Transformation complete. Success rate: {report['transformation_summary']['success_rate']}%")
        return report

def main():
    """
    Command-line interface for archive transformation
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Transform legacy file archive to modern structure')
    parser.add_argument('source_path', help='Path to source archive directory')
    parser.add_argument('target_path', help='Path to target directory for transformed archive')
    parser.add_argument('--rules', '-r', help='JSON file with custom transformation rules')
    parser.add_argument('--dry-run', action='store_true', help='Analyze only, do not copy files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate paths
    if not os.path.exists(args.source_path):
        logger.error(f"Source path does not exist: {args.source_path}")
        return 1
    
    if os.path.exists(args.target_path) and os.listdir(args.target_path):
        response = input(f"Target directory {args.target_path} is not empty. Continue? (y/n): ")
        if response.lower() != 'y':
            return 1
    
    # Load custom rules if provided
    transformation_rules = None
    if args.rules:
        with open(args.rules, 'r') as f:
            transformation_rules = json.load(f)
    
    # Create transformer and run
    transformer = ArchiveTransformer(args.source_path, args.target_path, transformation_rules)
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be copied")
        # In a real implementation, you'd analyze without copying
        projects = transformer._discover_projects()
        print(f"\nWould transform {len(projects)} projects:")
        for project_name, project_data in projects.items():
            print(f"  {project_name}: {len(project_data['files'])} files")
    else:
        report = transformer.transform_archive()
        print(f"\nTransformation complete!")
        print(f"Success rate: {report['transformation_summary']['success_rate']}%")
        print(f"Report saved to: {args.target_path}/Migration_Reports/")
    
    return 0

if __name__ == "__main__":
    exit(main())
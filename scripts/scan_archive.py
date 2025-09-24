#!/usr/bin/env python3
"""
Legacy Archive Modernizer - Archive Analysis Engine
Discovers patterns, relationships, and issues in legacy file archives

Based on real-world enterprise migration experience.
Author: Ryan Hendrix
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArchiveAnalyzer:
    """
    Comprehensive archive analysis engine that discovers patterns,
    relationships, and issues in legacy file structures.
    """
    
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.files_data = []
        self.naming_patterns = defaultdict(list)
        self.file_relationships = defaultdict(list)
        self.version_conflicts = []
        self.orphaned_files = []
        
    def analyze_archive(self):
        """
        Main analysis pipeline - discovers all patterns and issues
        """
        logger.info(f"Starting analysis of archive: {self.root_path}")
        
        # Phase 1: Discover all files and basic metadata
        self._discover_files()
        
        # Phase 2: Identify naming conventions and patterns
        self._identify_naming_patterns()
        
        # Phase 3: Map file relationships
        self._map_file_relationships()
        
        # Phase 4: Detect version control issues
        self._detect_version_conflicts()
        
        # Phase 5: Identify orphaned files
        self._identify_orphaned_files()
        
        # Phase 6: Generate comprehensive report
        return self._generate_analysis_report()
    
    def _discover_files(self):
        """
        Recursively discover all files and extract metadata
        """
        logger.info("Discovering files and extracting metadata...")
        
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.root_path)
                
                file_info = {
                    'full_path': str(file_path),
                    'relative_path': str(relative_path),
                    'filename': file,
                    'extension': file_path.suffix.lower(),
                    'size_bytes': file_path.stat().st_size,
                    'modified_date': datetime.fromtimestamp(file_path.stat().st_mtime),
                    'folder_depth': len(relative_path.parts) - 1,
                    'parent_folder': relative_path.parent.name,
                    'project_path': str(relative_path.parts[0]) if relative_path.parts else '',
                }
                
                self.files_data.append(file_info)
        
        logger.info(f"Discovered {len(self.files_data)} files")
    
    def _identify_naming_patterns(self):
        """
        Identify different naming conventions used across the archive
        """
        logger.info("Identifying naming patterns...")
        
        # Define regex patterns for common naming conventions
        patterns = {
            'descriptive_with_version': r'^[A-Za-z_]+.*[vV]?\d+.*\.(dwg|pdf|xlsx?)$',
            'project_code_sequential': r'^[A-Z]{2,4}[-_]\d{3}[-_].*\.(dwg|pdf|xlsx?)$',
            'structured_code': r'^[A-Z]\d{3}[-_][A-Z]{3}[-_]\d{3}.*\.(dwg|pdf|xlsx?)$',
            'date_based': r'.*\d{6}.*\.(dwg|pdf|xlsx?)$',
            'revision_controlled': r'.*[rR]ev?\d+.*\.(dwg|pdf|xlsx?)$',
            'final_versions': r'.*[fF][iI][nN][aA][lL].*\.(dwg|pdf|xlsx?)$',
        }
        
        for file_info in self.files_data:
            filename = file_info['filename']
            for pattern_name, pattern_regex in patterns.items():
                if re.match(pattern_regex, filename, re.IGNORECASE):
                    self.naming_patterns[pattern_name].append(file_info)
                    break
            else:
                self.naming_patterns['unclassified'].append(file_info)
    
    def _map_file_relationships(self):
        """
        Identify relationships between files (assemblies, parts, BOMs, specs)
        """
        logger.info("Mapping file relationships...")
        
        # Group files by likely project associations
        project_groups = defaultdict(list)
        
        for file_info in self.files_data:
            # Extract potential project identifier
            project_id = self._extract_project_identifier(file_info['filename'])
            if project_id:
                project_groups[project_id].append(file_info)
        
        # Within each project, identify file type relationships
        for project_id, files in project_groups.items():
            dwg_files = [f for f in files if f['extension'] == '.dwg']
            pdf_files = [f for f in files if f['extension'] == '.pdf']
            excel_files = [f for f in files if f['extension'] in ['.xlsx', '.xls']]
            
            self.file_relationships[project_id] = {
                'drawings': dwg_files,
                'specifications': pdf_files,
                'boms': excel_files,
                'total_files': len(files)
            }
    
    def _extract_project_identifier(self, filename):
        """
        Extract project identifier from filename using various patterns
        """
        # Pattern 1: Project name at start (Alpha, Beta, Gamma, etc.)
        match = re.match(r'^([A-Za-z]+)', filename)
        if match and len(match.group(1)) >= 3:
            return match.group(1).upper()
        
        # Pattern 2: Project code (GAM, DEL, etc.)
        match = re.match(r'^([A-Z]{2,4})[-_]', filename)
        if match:
            return match.group(1)
        
        # Pattern 3: Year-based grouping
        match = re.search(r'(20\d{2})', filename)
        if match:
            return f"YEAR_{match.group(1)}"
        
        return None
    
    def _detect_version_conflicts(self):
        """
        Identify files with conflicting versions or naming
        """
        logger.info("Detecting version conflicts...")
        
        # Group similar filenames and look for version conflicts
        base_names = defaultdict(list)
        
        for file_info in self.files_data:
            # Remove common version indicators to find base name
            base_name = re.sub(r'[vV]?\d+|[rR]ev?\d+|final|FINAL|actualfinal', '', 
                             file_info['filename'], flags=re.IGNORECASE)
            base_name = re.sub(r'[-_\s]+', '_', base_name).strip('_')
            
            base_names[base_name].append(file_info)
        
        # Identify groups with multiple versions
        for base_name, files in base_names.items():
            if len(files) > 1:
                # Sort by modification date to identify latest
                files_sorted = sorted(files, key=lambda x: x['modified_date'], reverse=True)
                self.version_conflicts.append({
                    'base_name': base_name,
                    'files': files_sorted,
                    'conflict_count': len(files),
                    'latest_file': files_sorted[0]['filename'],
                    'oldest_file': files_sorted[-1]['filename']
                })
    
    def _identify_orphaned_files(self):
        """
        Identify files that don't appear to belong to any project
        """
        logger.info("Identifying orphaned files...")
        
        # Files in "misc", "temp", or similar folders
        misc_keywords = ['misc', 'temp', 'old', 'backup', 'archive', 'delete']
        
        for file_info in self.files_data:
            folder_path = str(file_info['relative_path']).lower()
            
            # Check if file is in a "misc" type folder
            if any(keyword in folder_path for keyword in misc_keywords):
                self.orphaned_files.append(file_info)
                continue
            
            # Check if file has no clear project association
            project_id = self._extract_project_identifier(file_info['filename'])
            if not project_id and file_info['folder_depth'] > 0:
                self.orphaned_files.append(file_info)
    
    def _generate_analysis_report(self):
        """
        Generate comprehensive analysis report
        """
        logger.info("Generating analysis report...")
        
        # Calculate summary statistics
        total_files = len(self.files_data)
        total_size_mb = sum(f['size_bytes'] for f in self.files_data) / (1024 * 1024)
        
        # Extension analysis
        extensions = Counter(f['extension'] for f in self.files_data)
        
        # Date range analysis
        dates = [f['modified_date'] for f in self.files_data]
        date_range = {
            'earliest': min(dates),
            'latest': max(dates),
            'span_years': (max(dates) - min(dates)).days / 365.25
        }
        
        # Pattern distribution
        pattern_distribution = {name: len(files) for name, files in self.naming_patterns.items()}
        
        report = {
            'summary': {
                'total_files': total_files,
                'total_size_mb': round(total_size_mb, 2),
                'unique_projects': len(self.file_relationships),
                'version_conflicts': len(self.version_conflicts),
                'orphaned_files': len(self.orphaned_files),
                'date_range': date_range
            },
            'file_types': dict(extensions.most_common()),
            'naming_patterns': pattern_distribution,
            'project_breakdown': {
                pid: {
                    'total_files': data['total_files'],
                    'drawings': len(data['drawings']),
                    'specifications': len(data['specifications']),
                    'boms': len(data['boms'])
                }
                for pid, data in self.file_relationships.items()
            },
            'issues': {
                'version_conflicts': len(self.version_conflicts),
                'orphaned_files': len(self.orphaned_files),
                'unclassified_files': len(self.naming_patterns.get('unclassified', []))
            },
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self):
        """
        Generate actionable recommendations based on analysis
        """
        recommendations = []
        
        # Version conflict recommendations
        if self.version_conflicts:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Version Control',
                'issue': f"{len(self.version_conflicts)} sets of conflicting file versions detected",
                'recommendation': "Implement systematic version control with clear latest-version identification",
                'estimated_time_saved': f"{len(self.version_conflicts) * 10} minutes per search"
            })
        
        # Naming convention recommendations
        pattern_count = len([p for p in self.naming_patterns.keys() if self.naming_patterns[p]])
        if pattern_count > 3:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Standardization',
                'issue': f"{pattern_count} different naming conventions in use",
                'recommendation': "Standardize on single naming convention across all projects",
                'estimated_time_saved': "50% reduction in file search time"
            })
        
        # Orphaned files recommendations
        if self.orphaned_files:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Organization',
                'issue': f"{len(self.orphaned_files)} orphaned files in misc/temp folders",
                'recommendation': "Archive or categorize orphaned files to reduce clutter",
                'estimated_storage_saved': f"{sum(f['size_bytes'] for f in self.orphaned_files) / (1024*1024):.1f} MB"
            })
        
        return recommendations

def main():
    """
    Command-line interface for archive analysis
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze legacy file archive structure')
    parser.add_argument('archive_path', help='Path to archive directory to analyze')
    parser.add_argument('--output', '-o', help='Output file for analysis report (JSON format)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input path
    if not os.path.exists(args.archive_path):
        logger.error(f"Archive path does not exist: {args.archive_path}")
        return 1
    
    # Run analysis
    analyzer = ArchiveAnalyzer(args.archive_path)
    report = analyzer.analyze_archive()
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Analysis report saved to: {args.output}")
    else:
        print("\n" + "="*50)
        print("ARCHIVE ANALYSIS REPORT")
        print("="*50)
        print(f"Total Files: {report['summary']['total_files']}")
        print(f"Total Size: {report['summary']['total_size_mb']} MB")
        print(f"Projects Identified: {report['summary']['unique_projects']}")
        print(f"Version Conflicts: {report['summary']['version_conflicts']}")
        print(f"Orphaned Files: {report['summary']['orphaned_files']}")
        print("\nFile Types:")
        for ext, count in report['file_types'].items():
            print(f"  {ext}: {count} files")
        
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
    
    return 0

if __name__ == "__main__":
    exit(main())

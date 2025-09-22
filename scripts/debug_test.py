#!/usr/bin/env python3
"""
Debug script to isolate the transformation issue
"""

import sys
from pathlib import Path

def test_sample_creation():
    """Test sample data creation"""
    print("Testing sample data creation...")
    
    try:
        import create_sample_data
        sample_path = Path("debug_test_output/chaotic_archive")
        create_sample_data.create_sample_archive(sample_path)
        print(f"SUCCESS: Sample data created successfully at: {sample_path}")
        return sample_path
    except Exception as e:
        print(f"ERROR: Sample creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_analysis(sample_path):
    """Test archive analysis"""
    print(f"\nTesting archive analysis on: {sample_path}")
    
    try:
        import scan_archive
        analyzer = scan_archive.ArchiveAnalyzer(sample_path)
        report = analyzer.analyze_archive()
        print(f"SUCCESS: Analysis completed. Found {report['summary']['total_files']} files")
        return report
    except Exception as e:
        print(f"ERROR: Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_discovery(sample_path):
    """Test project discovery in isolation"""
    print(f"\nTesting project discovery on: {sample_path}")
    
    try:
        import modernize_archive
        transformer = modernize_archive.ArchiveTransformer(sample_path, "debug_test_output/output")
        projects = transformer._discover_projects()
        
        print(f"SUCCESS: Discovery completed. Found {len(projects)} projects:")
        for project_name, project_data in projects.items():
            print(f"   Project: {project_name}")
            print(f"   Type: {type(project_data)}")
            print(f"   Keys: {list(project_data.keys()) if isinstance(project_data, dict) else 'Not a dict!'}")
            print(f"   Files: {len(project_data.get('files', []))}")
            print()
        
        return projects
    except Exception as e:
        print(f"ERROR: Discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_single_project_transform(sample_path):
    """Test transforming a single project"""
    print(f"\nTesting single project transformation...")
    
    try:
        import modernize_archive
        transformer = modernize_archive.ArchiveTransformer(sample_path, "debug_test_output/output")
        projects = transformer._discover_projects()
        
        if not projects:
            print(" WARNIGN: No projects found to transform")
            return False
        
        # Get first project
        first_project_name = list(projects.keys())[0]
        first_project_data = projects[first_project_name]
        
        print(f"Transforming project: {first_project_name}")
        print(f"Project data type: {type(first_project_data)}")
        print(f"Project data: {first_project_data}")
        
        # Create target structure first
        transformer._create_target_structure()
        
        # Try to transform just one project
        transformer._transform_project(first_project_data)
        print("SUCCESS: Single project transformation successful")
        return True
        
    except Exception as e:
        print(f"ERROR: Single project transformation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run debug tests"""
    print("Legacy Archive Modernizer - Debug Tests")
    print("=" * 50)
    
    # Test 1: Sample creation
    sample_path = test_sample_creation()
    if not sample_path:
        return 1
    
    # Test 2: Analysis
    analysis_report = test_analysis(sample_path)
    if not analysis_report:
        return 1
    
    # Test 3: Project discovery
    projects = test_discovery(sample_path)
    if not projects:
        return 1
    
    # Test 4: Single project transformation
    success = test_single_project_transform(sample_path)
    if not success:
        return 1
    
    print("\nSUCCESS: All debug tests passed!")
    return 0

if __name__ == "__main__":
    exit(main())
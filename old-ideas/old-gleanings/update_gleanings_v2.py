#!/usr/bin/env python3
"""
Smart Gleanings Update - Version 2

Enhanced update script that uses the state management system for:
- Incremental processing (only modified files)
- User state preservation (hidden/deleted items)
- Performance optimization
- Backward compatibility with existing workflow
"""

import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime

def run_script(script_name, description, args=None):
    """Run a Python script and handle errors."""
    print(f"\nRunning {description}...")
    
    cmd = [sys.executable, script_name]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"SUCCESS: {description} completed successfully")
        if result.stdout.strip():
            # Only show relevant output, filter out verbose logs
            lines = result.stdout.strip().split('\n')
            important_lines = [line for line in lines if any(marker in line for marker in ['SUCCESS:', 'STATS:', 'Processed:', 'New:', 'Total:', 'Active:', 'Extraction complete'])]
            if important_lines:
                print('\n'.join(important_lines))
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR in {description}:")
        print(e.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='Smart gleanings update with state management')
    parser.add_argument('--force-all', action='store_true',
                       help='Process all files, not just modified ones')
    parser.add_argument('--skip-analysis', action='store_true',
                       help='Skip generating analysis report')
    parser.add_argument('--migrate', action='store_true',
                       help='Migrate from legacy format first')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    
    print("Smart Gleanings Update v2")
    print("=" * 40)
    
    # Change to script directory
    import os
    original_cwd = os.getcwd()
    os.chdir(script_dir)
    
    try:
        # Step 1: Migrate legacy data if requested
        if args.migrate:
            if not run_script("extract_new.py", "Migrating legacy data", ["--migrate"]):
                return
        
        # Step 2: Incremental extraction
        extract_args = []
        if args.force_all:
            extract_args.append("--force-all")
        
        if not run_script("extract_new.py", "Smart extraction (incremental processing)", extract_args):
            return
        
        # Step 3: Generate state-aware index
        if not run_script("generate_index_v2.py", "Generating state-aware index"):
            return
        
        # Step 4: Generate analysis (optional)
        if not args.skip_analysis:
            if not run_script("analyze_gleanings.py", "Creating analysis report"):
                print("WARNING: Analysis generation failed, but continuing...")
        
        print("\nSmart gleanings update completed!")
        print("\nGenerated files:")
        print("gleanings_state.json - Enhanced data with user state")
        print("Gleanings Index.md - State-aware browsable index")
        if not args.skip_analysis:
            print("Gleanings Analysis.md - Patterns and insights report")
        
        print("\nNext steps:")
        print("• Use `uv run manage_gleanings.py` for interactive management")
        print("• Run with --force-all to reprocess all files")
        print("• Use `uv run extract_new.py --stats` to see current statistics")
        
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

if __name__ == '__main__':
    main()
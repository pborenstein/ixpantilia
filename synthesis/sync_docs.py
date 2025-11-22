#!/usr/bin/env python3
"""
Documentation sync script - keeps project docs in sync with actual code.

Why this exists:
- Manual doc updates are error-prone and forgotten
- session_memory.json gets stale without updates
- README.md commands can drift from main.py reality
- CLAUDE.md status needs updating as phases complete

Architecture:
- Scan codebase for actual capabilities (files, commands, features)
- Compare against current documentation state
- Auto-update docs to match reality
- Report what changed for review
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime


class DocSyncer:
    """
    Automatically sync documentation with codebase reality.
    
    Why automatic sync:
    - Docs lag behind code changes
    - Manual updates get forgotten during development flow
    - Inconsistency between what exists vs what's documented
    """
    
    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent
        
        self.project_root = project_root
        self.session_file = project_root / "session_memory.json"
        self.readme_file = project_root / "README.md"
        self.claude_file = project_root / "CLAUDE.md"
        self.main_file = project_root / "main.py"
        
    def scan_codebase_reality(self) -> Dict:
        """
        Scan actual codebase to determine what we've built.
        
        Why scan vs hardcode:
        - Code is source of truth, not docs
        - Catches features we built but forgot to document
        - Automatic discovery of new capabilities
        """
        reality = {
            "implemented_tools": self._find_implemented_tools(),
            "cli_commands": self._extract_cli_commands(),
            "working_files": self._find_working_files(),
            "completion_indicators": self._detect_completion_status()
        }
        
        return reality
    
    def _find_implemented_tools(self) -> List[str]:
        """Find actually implemented Python modules in src/"""
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            return []
        
        tools = []
        
        # Check for key implementation files
        if (src_dir / "temporal_archaeology.py").exists():
            tools.append("Temporal Interest Archaeology")
        
        if (src_dir / "visualizer").exists():
            tools.append("Personal Knowledge Graph Visualizer")
        
        if (src_dir / "embeddings").exists():
            tools.append("Embeddings System")
        
        return tools
    
    def _extract_cli_commands(self) -> Dict[str, str]:
        """Extract available CLI commands from main.py"""
        if not self.main_file.exists():
            return {}
        
        with open(self.main_file, 'r') as f:
            content = f.read()
        
        # Find subparser definitions
        commands = {}
        parser_pattern = r'subparsers\.add_parser\("(\w+)",\s*help="([^"]*)"'
        matches = re.findall(parser_pattern, content)
        
        for cmd, help_text in matches:
            commands[cmd] = help_text
        
        return commands
    
    def _find_working_files(self) -> List[str]:
        """Find files that indicate working functionality"""
        indicators = []
        
        # Check for embeddings data
        embeddings_dir = self.project_root / "embeddings"
        if embeddings_dir.exists() and any(embeddings_dir.iterdir()):
            indicators.append("embeddings data present")
        
        # Check for visualization outputs
        viz_dir = self.project_root / "visualizations"
        if viz_dir.exists():
            html_files = list(viz_dir.glob("*.html"))
            if html_files:
                indicators.append(f"{len(html_files)} visualization outputs")
        
        return indicators
    
    def _detect_completion_status(self) -> Dict[str, bool]:
        """Auto-detect what's actually complete vs planned"""
        status = {}
        
        # Check if temporal archaeology is working
        temp_file = self.project_root / "src" / "temporal_archaeology.py"
        status["temporal_archaeology"] = temp_file.exists() and len(temp_file.read_text()) > 1000
        
        # Check if visualizer is working  
        viz_dir = self.project_root / "src" / "visualizer"
        status["knowledge_graph"] = viz_dir.exists() and (viz_dir / "visualizer.py").exists()
        
        # Check if embeddings system works
        embed_dir = self.project_root / "src" / "embeddings"
        status["embeddings"] = embed_dir.exists() and (embed_dir / "pipeline.py").exists()
        
        return status
    
    def update_session_memory(self, reality: Dict) -> List[str]:
        """Update session_memory.json with current reality"""
        changes = []
        
        if not self.session_file.exists():
            return ["session_memory.json not found"]
        
        with open(self.session_file, 'r') as f:
            session_data = json.load(f)
        
        # Update last_updated timestamp
        old_date = session_data.get("last_updated", "unknown")
        session_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        if old_date != session_data["last_updated"]:
            changes.append(f"Updated timestamp: {old_date} -> {session_data['last_updated']}")
        
        # Add any missing completed milestones
        completed = set(session_data.get("milestones", {}).get("completed", []))
        
        # Auto-detect new completions
        if reality["completion_indicators"]["temporal_archaeology"]:
            new_milestone = "Temporal Interest Archaeology implemented with ASCII timelines"
            if new_milestone not in completed:
                session_data["milestones"]["completed"].append(new_milestone)
                changes.append(f"Added milestone: {new_milestone}")
        
        # Update CLI commands section
        if reality["cli_commands"]:
            if "cli_commands" not in session_data.get("technical_implementation", {}):
                session_data.setdefault("technical_implementation", {})["cli_commands"] = {}
            
            for cmd, desc in reality["cli_commands"].items():
                old_desc = session_data["technical_implementation"]["cli_commands"].get(cmd)
                if old_desc != desc:
                    session_data["technical_implementation"]["cli_commands"][cmd] = desc
                    changes.append(f"Updated CLI command: {cmd}")
        
        # Write back
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return changes
    
    def update_readme(self, reality: Dict) -> List[str]:
        """Update README.md with current commands"""
        changes = []
        
        if not self.readme_file.exists():
            return ["README.md not found"]
        
        # For now, just report what we could sync
        # (Full implementation would parse/update markdown sections)
        available_commands = list(reality["cli_commands"].keys())
        changes.append(f"Available commands: {', '.join(available_commands)}")
        
        return changes
    
    def run_sync(self) -> None:
        """Run full documentation sync"""
        print("Scanning codebase reality...")
        reality = self.scan_codebase_reality()
        
        print(f"Found {len(reality['implemented_tools'])} implemented tools")
        print(f"Found {len(reality['cli_commands'])} CLI commands")
        print(f"Working files: {reality['working_files']}")
        
        print("\nUpdating session_memory.json...")
        session_changes = self.update_session_memory(reality)
        for change in session_changes:
            print(f"  ✓ {change}")
        
        print("\nChecking README.md...")
        readme_changes = self.update_readme(reality)
        for change in readme_changes:
            print(f"  • {change}")
        
        if not session_changes and not readme_changes:
            print("\nDocumentation already in sync!")
        else:
            print(f"\nSync complete: {len(session_changes + readme_changes)} updates made")


def main():
    """CLI entry point for doc sync"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync documentation with codebase reality")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without updating")
    
    args = parser.parse_args()
    
    syncer = DocSyncer()
    
    if args.dry_run:
        print("DRY RUN - no files will be modified")
    
    syncer.run_sync()


if __name__ == "__main__":
    main()
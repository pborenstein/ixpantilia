#!/usr/bin/env python3
"""
ASCII Art Formatter

Simple tool to fix ragged right edges in ASCII art boxes.
Detects ASCII art blocks and ensures consistent width alignment.
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple


# Box drawing characters used in ASCII art
BOX_CHARS = set('┌┐└┘│─├┤┬┴┼')


def is_ascii_art_line(line: str) -> bool:
    """Check if a line contains ASCII art box-drawing characters."""
    return any(char in BOX_CHARS for char in line)


def is_box_corner_line(line: str) -> bool:
    """Check if line contains box corner characters (starts/ends a box)."""
    stripped = line.strip()
    return any(char in '┌┐└┘' for char in stripped)


def is_simple_flow_line(line: str) -> bool:
    """Check if line is a simple flow connector (not part of a box)."""
    stripped = line.strip()
    # Simple vertical connectors or arrows that aren't part of boxes
    if stripped in ['│', '▼', '│▼'] or stripped.startswith('│ ') and stripped.endswith(' │'):
        return False  # These might be part of boxes
    # Single vertical line or arrow without box context
    if stripped == '│' or stripped == '▼' or '──▶' in stripped:
        return True
    # Isolated text with arrows (not in a box)
    if '──▶' in stripped and '│' not in stripped:
        return True
    return False


def find_box_blocks(lines: List[str]) -> List[Tuple[int, int]]:
    """
    Find actual ASCII art BOX blocks (not flow diagrams).
    Only includes blocks that have corner characters (┌┐└┘).
    """
    blocks = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for a box start (line with corner characters)
        if is_box_corner_line(line) or (line.startswith('┌') or '┌' in line):
            start = i
            
            # Find the end of this box
            box_end = start
            for j in range(start + 1, len(lines)):
                next_line = lines[j].strip()
                
                if not next_line:  # Empty line might be end of block
                    break
                if not is_ascii_art_line(next_line):  # Non-ASCII line ends block
                    break
                if is_simple_flow_line(next_line):  # Flow line ends box
                    break
                
                box_end = j
                
                # If we hit a bottom corner, this box is complete
                if next_line.startswith('└') or next_line.endswith('┘'):
                    break
            
            # Only add if we have a substantial box (more than just one line)
            if box_end > start:
                blocks.append((start, box_end))
            
            i = box_end + 1
        else:
            i += 1
    
    return blocks


def find_ascii_blocks(lines: List[str]) -> List[Tuple[int, int]]:
    """
    Find ASCII art blocks in the text.
    Now focuses on actual boxes, not flow diagrams.
    Returns list of (start_line, end_line) tuples.
    """
    return find_box_blocks(lines)


def get_line_type(line: str) -> str:
    """Determine the type of ASCII art line."""
    stripped = line.strip()
    if not stripped:
        return 'empty'
    
    if stripped.startswith('┌') and stripped.endswith('┐'):
        return 'top'
    elif stripped.startswith('└') and stripped.endswith('┘'):
        return 'bottom'
    elif stripped.startswith('│') and stripped.endswith('│'):
        # Check if it's a separator line (contains only ─ and spaces)
        content = stripped[1:-1].strip()
        if all(c in '─ ' for c in content):
            return 'separator'
        else:
            return 'content'
    else:
        return 'other'


def calculate_block_width(lines: List[str], start: int, end: int) -> int:
    """Calculate the optimal width for an ASCII art block."""
    max_content_width = 0
    
    for i in range(start, end + 1):
        line = lines[i].strip()
        if not line:
            continue
            
        line_type = get_line_type(line)
        
        if line_type == 'content':
            # For content lines, measure the actual content
            if len(line) >= 2 and line[0] == '│' and line[-1] == '│':
                content = line[1:-1]
                content_width = len(content)
                max_content_width = max(max_content_width, content_width)
        elif line_type in ['top', 'bottom', 'separator']:
            # For border/separator lines, use the total width minus borders
            if len(line) >= 2:
                inner_width = len(line) - 2
                max_content_width = max(max_content_width, inner_width)
    
    # Add padding - ensure at least some minimum width
    return max(max_content_width, 20)


def format_ascii_line(line: str, target_width: int) -> str:
    """Format a single ASCII art line to the target width."""
    stripped = line.strip()
    if not stripped:
        return line  # Keep empty lines as-is
    
    line_type = get_line_type(stripped)
    
    if line_type == 'top':
        return '┌' + '─' * target_width + '┐'
    elif line_type == 'bottom':
        return '└' + '─' * target_width + '┘'
    elif line_type == 'separator':
        return '│ ' + '─' * (target_width - 2) + ' │'
    elif line_type == 'content':
        if len(stripped) >= 2 and stripped[0] == '│' and stripped[-1] == '│':
            content = stripped[1:-1]
            # Left-align content and pad to width
            padded_content = content.ljust(target_width)
            return '│' + padded_content + '│'
        else:
            return line  # Keep malformed lines as-is
    else:
        return line  # Keep other lines as-is


def format_ascii_block(lines: List[str], start: int, end: int) -> List[str]:
    """Format an entire ASCII art block."""
    target_width = calculate_block_width(lines, start, end)
    formatted_lines = []
    
    for i in range(start, end + 1):
        original_line = lines[i]
        if original_line.strip():  # Only format non-empty lines
            formatted_line = format_ascii_line(original_line, target_width)
            # Preserve original indentation
            indent = len(original_line) - len(original_line.lstrip())
            formatted_lines.append(' ' * indent + formatted_line)
        else:
            formatted_lines.append(original_line)  # Keep empty lines
    
    return formatted_lines


def format_file(file_path: Path, backup: bool = True) -> None:
    """Format ASCII art in a file."""
    if not file_path.exists():
        print(f"Error: File {file_path} not found")
        return
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remove trailing newlines from lines but remember original endings
    original_lines = lines[:]
    lines = [line.rstrip('\n\r') for line in lines]
    
    # Find ASCII blocks
    blocks = find_ascii_blocks(lines)
    
    if not blocks:
        print(f"No ASCII art blocks found in {file_path}")
        return
    
    print(f"Found {len(blocks)} ASCII art blocks in {file_path}")
    
    # Create backup if requested
    if backup:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(original_lines)
        print(f"Backup created: {backup_path}")
    
    # Format each block (in reverse order to preserve line numbers)
    for start, end in reversed(blocks):
        print(f"Formatting block at lines {start+1}-{end+1}")
        formatted_block = format_ascii_block(lines, start, end)
        
        # Replace the block
        lines[start:end+1] = formatted_block
    
    # Write the formatted file
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
    
    print(f"Formatted ASCII art in {file_path}")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python ascii_formatter.py <file_path>")
        print("Example: python ascii_formatter.py EMBEDDINGS_SEARCH.md")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    format_file(file_path)


if __name__ == '__main__':
    main()
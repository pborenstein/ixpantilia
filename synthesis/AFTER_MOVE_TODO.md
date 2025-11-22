# Post-Move TODO

**When:** After moving to ~/projects/obsidian-projects/synthesis

## Required Path Fixes

### 1. Hardcoded Vault Name in Obsidian URIs

**Files affected:** main.py (lines 115, 134, 390, 415)

**Problem:**
```python
"obsidian_uri": f"obsidian://vault/amoxtli/{quote(path_no_ext)}"
```

**Fix needed:**
Extract vault name from vault_root parameter or make it configurable:
```python
vault_name = vault_root.resolve().name  # Auto-detect from path
"obsidian_uri": f"obsidian://vault/{vault_name}/{quote(path_no_ext)}"
```

### 2. Hardcoded File Path Prefix

**Files affected:** main.py (lines 117, 392)

**Problem:**
```python
"file_path": f"~/Obsidian/amoxtli/{rel_path}"
```

**Fix needed:**
Use actual vault_root from parameter:
```python
"file_path": str(vault_root / rel_path)
```

### 3. Default Vault Path Assumptions

**Files affected:**
- main.py:425 - `Path("../../")`
- src/visualizer/simple_viz.py:92 - `Path("../../")`
- simple_canvas.py:156 - `Path("../../")`

**Current behavior:** Assumes tool lives at `.tools/synthesis/` inside vault

**After move:** These defaults will fail

**Fix options:**

**Option A - Make explicit (recommended):**
Always require vault path:
```bash
uv run main.py --vault ~/Obsidian/amoxtli search "query"
```

**Option B - Config file:**
Add vault_path to synthesis_config.json:
```json
{
  "default_model": "all-MiniLM-L6-v2",
  "vault_path": "~/Obsidian/amoxtli"
}
```

**Option C - Environment variable:**
```bash
export OBSIDIAN_VAULT=~/Obsidian/amoxtli
```

## Recommendation

Implement **Option B** (config file) + **Option A** (CLI override).

Add to ConfigManager:
- `get_vault_path()` - returns configured vault or raises error
- `set_vault_path(path)` - stores vault location
- CLI `--vault` overrides config

This way after move:
```bash
# One-time setup
uv run main.py set-vault ~/Obsidian/amoxtli

# Then all commands just work
uv run main.py search "query"
uv run main.py archaeology "AI"
```

## Testing After Move

1. Move project to ~/projects/obsidian-projects/synthesis
2. Try running without --vault flag (should fail or warn)
3. Test with explicit --vault flag
4. Implement vault path config
5. Test all commands work after config set

---

*Created: 2025-10-13*
*Context: Moving from .tools/synthesis/ to standalone project location*

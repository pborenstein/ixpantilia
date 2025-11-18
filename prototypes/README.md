# Phase 0 Prototypes

This directory contains test scripts for Phase 0: Discovery & Validation.

**Important**: These scripts are meant to be run on **your machine with internet access**, not in the VM.

## Current Task: 0.1 - Test Synthesis Performance

### What You Need to Do

1. **Pull the latest changes** from this repo on your machine (with internet)

2. **Update the script path** if needed:
   - Edit `test_synthesis_performance.py`
   - Change `SYNTHESIS_PATH` to point to your actual Synthesis installation
   - Could be: `old-ideas/synthesis/` (in this repo)
   - Or: `~/.obsidian/vaults/main/.tools/synthesis` (in your vault)

3. **Run the test**:
   ```bash
   cd /path/to/ixpantilia
   python prototypes/test_synthesis_performance.py
   ```

4. **Copy the output** and report back via commit message, issue, or however we're communicating

### What the Script Tests

- ✅ Available models (downloads on first run if needed)
- ✅ Vault statistics (file count, indexed directories)
- ✅ Cold start search performance
- ✅ Warm start search performance (3 queries)
- ✅ Different model performance
- ✅ Archaeology feature (temporal analysis)

### What I Need From You

After running the script, please report:

1. **Full output** of the script
2. **Are daily notes indexed?** (look in stats output)
3. **What's the average warm search time?** (should be < 1s, ideally < 500ms)
4. **Did models download successfully?** (on first run)
5. **How many files are indexed?** (does it match your vault?)

### Next Steps

After you report the results, I'll:
- Analyze the performance data
- Document findings in `docs/phase0-results.md`
- Move to Task 0.2 (subprocess integration prototype)
- Continue through Phase 0 tasks

---

## Communication Pattern

1. I create scripts and push to repo
2. You pull and run on your machine (with internet/vault access)
3. You report results back
4. I analyze and create next script
5. Repeat until Phase 0 is complete

This way we work around the VM's internet limitations while still being able to test the actual system.

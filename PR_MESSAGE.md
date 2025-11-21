# Extraction Shakedown: Format Flexibility & Filesystem Robustness

## Summary

Real-world extraction testing on production vault (742 daily notes, 766 gleanings) revealed critical format gaps and filesystem edge cases. This PR implements comprehensive fixes that achieve **100% gleaning coverage** (up from 90%) and handles macOS case-insensitive filesystem quirks.

**Impact**: Extraction now follows Postel's Law ("be liberal in your input, conservative in your output"), supporting 5 different gleaning formats instead of just 1.

## Problems Fixed

### 1. Case-Insensitive Filesystem Duplicates (macOS APFS) 🔧

**Problem**: On macOS with case-insensitive APFS, both `Daily/**/*.md` and `daily/**/*.md` glob patterns matched the same files, causing confusing duplicate output.

**Solution**:
- Added `seen_paths` set using `Path.resolve()` for deduplication based on absolute paths
- Removed lowercase patterns entirely (user only has `Daily/`, not `daily/`)
- Each file now processed exactly once with clean output

**Test coverage**: Added `test_find_daily_notes_no_duplicates_on_case_insensitive_fs()`

### 2. Missing 'hidden' Status in CLI 🔧

**Problem**: System internals supported three statuses (active/inactive/hidden), but CLI only exposed active/inactive.

**Solution**:
- Added 'hidden' to CLI `temoa gleaning mark` command choices
- Updated help text to explain all three statuses:
  - **active**: Normal gleaning, included in search
  - **inactive**: Dead link, auto-restores if link comes back
  - **hidden**: Manually hidden, never checked by maintenance

### 3. Multiple Gleaning Formats Not Supported (10% Data Loss) 🚨

**Problem**: Extraction only handled single rigid format `- [Title](URL) - Description`, missing 77 gleanings (10% loss).

**Solution**: Implemented comprehensive pattern matching for **5 format types**:

1. **Markdown link**: `- [Title](URL)`
2. **Markdown link with timestamp**: `- [Title](URL)  [14:30]`
3. **Naked URL with bullet**: `- https://example.com` (fetches title from web)
4. **Naked URL bare**: `https://example.com` (no bullet, fetches title)
5. **Multi-line descriptions**: ALL consecutive `>` lines captured, paragraph breaks preserved

**Title fetching**: For naked URLs, fetch page `<title>` tag via HTTP (only first 8KB read). Falls back to domain name if fetch fails. Adds ~1.5s per URL but eliminates data loss.

**Result**: 766/766 gleanings extracted (100% coverage, 0% loss)

### 4. Dry Run Fetching Titles Wastefully 🔧

**Problem**: `--dry-run` made HTTP requests to fetch titles, then discarded them.

**Solution**:
- Added `dry_run` parameter to `extract_from_note()`
- Skip title fetching during dry run, use placeholders instead
- Instant dry run preview, no wasted bandwidth

### 5. Lowercase Patterns Causing User Confusion 🔧

**Problem**: Even though deduplication worked, output showed both `daily/` and `Daily/` paths, confusing users.

**Solution**:
- Removed lowercase patterns (`daily/**/*.md`, `journal/**/*.md`)
- Only search capital-case patterns (`Daily/**/*.md`, `Journal/**/*.md`)
- Clean output showing actual directory names only

## Enhancement: Diagnostic Tool 🎁

Added `scripts/analyze_gleaning_formats.py` - pre-extraction analysis tool:

**Features**:
- Scans vault for all gleaning formats
- Shows examples of each format found
- Reports coverage statistics
- Estimates extraction time for naked URLs

**Example output**:
```
FORMAT BREAKDOWN:
  ✓ Markdown links ([Title](URL)):        689 (SUPPORTED)
  ✓ Naked URLs with bullet (- https://):   50 (SUPPORTED - fetches title)
  ✓ Naked URLs bare (https://):            27 (SUPPORTED - fetches title)

FEATURE USAGE:
  ✓ Timestamps [HH:MM]:                    234 (SUPPORTED)
  ✓ Multi-line descriptions (>2 lines):    45 (FULLY SUPPORTED)

📌 NOTE: 77 naked URLs will have titles fetched from web
   Extraction will take ~115 seconds longer (fetching titles)
```

## Production Results

**Before fixes**:
```
Total gleanings found: 689
Missing gleanings: 77 (10% loss)
Confusing duplicate output showing daily/ and Daily/
```

**After fixes**:
```
Total gleanings found: 766
New gleanings created: 739
Duplicates skipped: 27
Files processed: 374
Coverage: 100% (0% loss)
Clean output, no duplicate processing messages
```

## Design Decisions

**DEC-021: Postel's Law for Gleanings**
- Accept 5 different gleaning formats
- Normalize to consistent output format
- Preserve all information (titles, URLs, descriptions, timestamps)
- Trade-off: More complex extraction logic, but 0% data loss

**DEC-022: Title Fetching for Naked URLs**
- Fetch page titles from web for naked URLs
- ~1.5s per URL acceptable for completeness
- Fallback to domain name if fetch fails
- Trade-off: Extraction slower, but search results much more useful

**DEC-023: Case-Sensitive Pattern Matching**
- Only search `Daily/` and `Journal/` (capital-case)
- Clearer UX for 99% case (most Obsidian vaults use capital-case)
- Users with lowercase directories can easily customize patterns

## Testing

**Test coverage added**:
- `test_find_daily_notes_no_duplicates_on_case_insensitive_fs()` - Verifies deduplication
- `test_extract_gleanings_no_duplicate_processing()` - Verifies no double-extraction

**All 19 gleaning tests passing**:
- Status management (active/inactive/hidden)
- Frontmatter parsing
- Status persistence
- File deduplication
- Extraction without duplicates

## Documentation Updates

- ✅ **docs/IMPLEMENTATION.md**: Added "Extraction Shakedown" section to Phase 2.5
- ✅ **docs/CHRONICLES.md**: Added Entry 10 with detailed problem analysis
- ✅ **docs/GLEANINGS.md**: Updated with all 5 format examples
- ✅ **scripts/analyze_gleaning_formats.py**: Reflects current support status

## Commits

- `c356fdb`: fix: resolve case-insensitive filesystem duplicate extraction bug
- `c356fdb`: feat: add 'hidden' status support to CLI
- `6db212d`: feat: support multiple gleaning formats and naked URLs
- `aa903e5`: docs: update GLEANINGS.md with multiple format support
- `493143c`: fix: update diagnostic script to reflect current format support
- `ead20e3`: fix: skip title fetching during dry run
- `ef105f4`: fix: remove lowercase daily/journal patterns (user preference)

## Lessons Learned

**Real-world testing is irreplaceable**:
- VM testing (Linux) didn't catch macOS filesystem issues
- Test data had single format; production vault had 5 formats
- User mental models differ from developer assumptions

**Flexibility beats perfection**:
- Supporting 5 formats instead of 1 = 10% more data captured
- Title fetching overhead (~2 min) acceptable for completeness
- "Be liberal in your input" = better UX than forcing format changes

**Diagnostic tools accelerate debugging**:
- `analyze_gleaning_formats.py` made format gaps immediately visible
- Users can self-diagnose before filing bug reports
- Transparency builds trust

**User feedback is gold**:
- "daily is BAD BAD BAD" → Remove confusing patterns
- "Dry run shouldn't fetch" → Optimize preview performance
- "Any URL is a gleaning" → Expand pattern matching

## Next Steps

✅ **Extraction proven robust** on production vault with 100% coverage
🚀 **Ready for deployment** to always-on machine
📱 **Next**: Validate behavioral hypothesis (vault-first habit formation via mobile)

---

**Status**: Phase 2.5 - Mobile Validation (ongoing)
**Extraction**: Ready for production use
**Test Coverage**: 19/19 gleaning tests passing

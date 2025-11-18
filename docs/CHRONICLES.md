# CHRONICLES.md - Project Lore & Design Discussions

> **Purpose**: This document captures key discussions, design decisions, and historical context for the Ixpantilia project. Unlike IMPLEMENTATION.md (which tracks *what* to build) or CLAUDE.md (which explains *how* to build), Chronicles explains *why* we're building it this way.

**Created**: 2025-11-18
**Format**: Chronological entries with discussion summaries
**Audience**: Future developers, decision-makers, and your future self

---

## Entry 1: The Central Problem of AI (2025-11-18)

### The Question

> "I have a bunch of documents and I want to know what is in them. The canonical 'query my documents' problem. If there were a silver bullet, I would probably know about it. What is the deal with this problem, and am I reinventing the axle?"

This is **the** question. If you're reading this wondering whether Ixpantilia is necessary, start here.

---

### Why There's No Silver Bullet

The "query my documents" problem is fundamentally hard because it's **not one problem—it's many problems disguised as one**.

#### Different Query Types Need Different Approaches

| Query Type | Example | Best Approach | Why Others Fail |
|------------|---------|---------------|-----------------|
| **Lookup** | "What did I save about React hooks?" | Full-text search (grep) | Semantic search over-complicates, LLMs hallucinate |
| **Conceptual** | "What do I know about state management?" | Semantic search (embeddings) | Full-text misses synonyms, LLMs too slow |
| **Synthesis** | "How do these ideas connect?" | RAG with LLM | Search can't generate, embeddings can't synthesize |
| **Temporal** | "What was I interested in last March?" | Archaeology/analytics | Standard search ignores time dimension |

**No single approach wins at all of these.** That's not a technology gap—it's a fundamental trade-off.

#### The Fundamental Trade-offs

1. **Recall vs. Precision**
   - Cast a wide net → get irrelevant results
   - Be specific → miss important connections
   - No algorithm solves both perfectly

2. **Speed vs. Quality**
   - Fast search → simpler models → misses nuance
   - Deep analysis → slow → unusable on mobile
   - Can't have both without caching/pre-computation

3. **Context Window Limits**
   - LLMs can't hold your entire vault
   - Must retrieve → rank → assemble context
   - Retrieval quality determines output quality
   - Wrong chunks = wrong answers

4. **Exact Match vs. Semantic Match**
   - Keyword search: finds "React" but not "user interface libraries"
   - Semantic search: finds concepts but might miss the exact phrase you saved
   - Both are needed for different tasks

---

### Comparison of Existing Solutions

Why isn't someone else already solving this? **They are, but not for *your* use case.**

| Solution | What It Does Well | Why It Doesn't Solve Ixpantilia's Problem | Cost/Complexity |
|----------|-------------------|------------------------------------------|-----------------|
| **Obsidian Native Search** | Fast keyword search, works offline | Not semantic, doesn't rank by relevance, desktop-only UI, no mobile optimization | Free, built-in |
| **Obsidian Copilot** | Chat with vault, semantic search, good LLM integration | Requires OpenAI API (not local), complex 6000-char chunking, chat-focused not search-focused, heavy dependencies | ~$20/mo for API, plugin setup |
| **Perplexity/ChatGPT** | Great at synthesis, up-to-date info, natural language | Searches the *internet*, not your vault, no access to private notes, hallucination risk | $20/mo, requires internet |
| **Vector DBs (Pinecone, Weaviate)** | Scalable semantic search, production-ready, good for large datasets | Requires restructuring vault into DB, complex setup/maintenance, not Obsidian-aware, overkill for personal use | $70+/mo or self-host complexity |
| **NotebookLM** | Excellent RAG, source citations, audio summaries | Not local (cloud-based), not mobile-optimized, not real-time with vault changes, Google data policies | Free (for now), privacy trade-off |
| **Elasticsearch** | Enterprise search, scales well, good ranking | Massive overkill for personal vault, not semantic by default (need plugins), complex config, resource-heavy | Self-host: high complexity |
| **mem0.ai** | Personal memory layer, good for LLM context | Cloud-based, not Obsidian-native, requires API integration | Freemium, $10+/mo |
| **Recall (recall.wiki)** | Summarizes bookmarks, semantic search of saved links | Cloud storage, browser-focused not note-focused, doesn't integrate with Obsidian workflow | Free tier limited |

**Key Insight**: Most solutions optimize for one of:
- **Enterprise scale** (you have 1 vault, not 1000 databases)
- **Cloud convenience** (you want privacy and local processing)
- **Chat interface** (you want search results, not conversations)
- **General web content** (you have curated, structured knowledge)

**None optimize for**: *"Search my personal vault from my phone in <2s while preserving privacy."*

---

### What Ixpantilia Actually Is

**Ixpantilia is NOT a new search algorithm.** It's a **workflow wrapper** that:

1. **Makes existing tech (Synthesis) accessible from mobile** → removes friction
2. **Puts your vault first** → habit formation (check before Googling)
3. **Stays local** → privacy, no API costs, works offline
4. **Obsidian-native** → works with existing notes, no migration

#### Analogy

You're not inventing a new search engine. You're building a **speed dial for your brain's external hard drive**.

#### The Real Problem Being Solved

It's not *"How do I search documents?"*

It's: **"I save things but never see them again. How do I make my past research useful for my present research?"**

This is a **retrieval behavior problem**, not a search technology problem.

---

### Why Gleanings Are Different

Most RAG solutions assume you have **unstructured documents**. You have **pre-structured knowledge artifacts**:

- **Already filtered**: You decided these links were important (curation done)
- **Timestamped**: Temporal context preserved (when you were interested)
- **Atomic**: One link per note (perfect granularity for embeddings)
- **Personal**: Your knowledge graph, not generic web content

**This is a huge advantage.** Gleanings are already in the ideal format for semantic search.

---

### What We're NOT Trying to Solve

These are explicitly **out of scope** (learned from old-gleanings failure):

| Anti-Goal | Why We're Avoiding It | Cost of Attempting |
|-----------|----------------------|-------------------|
| ❌ Answering questions with perfect accuracy | That's AGI-complete | Infinite development time |
| ❌ Replacing Google | Internet search is a different problem space | Wasted effort on wrong problem |
| ❌ Organizing knowledge into categories | old-gleanings proved this fails (2,771 lines of complexity) | User frustration, abandonment |
| ❌ Building a new embedding model | sentence-transformers is fine for personal use | Months of ML training, no ROI |
| ❌ Multi-user collaboration | Personal vault is single-user by design | Auth, sync, conflict resolution complexity |
| ❌ Real-time sync | Batch re-indexing is sufficient | Watcher overhead, race conditions |

**Lesson from old-gleanings**: Over-engineering kills adoption. Keep Ixpantilia simple.

---

### The Ixpantilia Hypothesis

Our core bet:

> **"If I can search my vault from my phone in <2 seconds, I'll check it before Googling. Over time, this habit makes past research compound."**

This is **not** a technology hypothesis. It's a **behavioral hypothesis**.

#### Success Looks Like

- **Week 1**: "This is fast and convenient"
- **Month 1**: "I check my vault before Googling sometimes"
- **Month 3**: "I check my vault *first* most of the time"
- **Month 6**: "I'm rediscovering forgotten gleanings regularly"
- **Year 1**: "My research builds on itself instead of restarting"

#### Failure Looks Like

- Vault search takes >3 seconds → I don't use it → habit never forms
- Results aren't relevant → I lose trust → I stop checking
- Mobile UI is clunky → friction too high → back to Google

**The technology must be invisible.** Speed and relevance are the only metrics that matter for habit formation.

---

### Key Insights for Future Reference

1. **There is no silver bullet** because "query my documents" is 4+ different problems requiring different approaches.

2. **RAG ≠ Search**
   - RAG generates answers (can hallucinate)
   - Search returns what you actually have (trustworthy)
   - Both are needed for different tasks

3. **Ixpantilia's niche is underserved**: Mobile-first, local, Obsidian-native semantic search with <2s response time.

4. **Behavioral change is the hard part**, not the technology. Synthesis already works. Making it accessible and habitual is the innovation.

5. **Pre-structured knowledge (gleanings) is an advantage** over generic RAG, which must chunk arbitrary documents.

6. **Phase 0 validation is critical**: If Synthesis is slow, if obsidian:// URIs don't work on mobile, if subprocess overhead is high → the hypothesis fails. Measure first.

---

## Decision Log

### DEC-001: Why Subprocess Instead of Library Import?

**Date**: 2025-11-18
**Context**: How should Ixpantilia call Synthesis?
**Options Considered**:
1. Import Synthesis as Python module → tight coupling
2. Keep Synthesis as separate service → deployment complexity
3. **Subprocess call via CLI** → clean separation ✓

**Decision**: Subprocess call
**Rationale**:
- Clean interface via JSON (well-defined contract)
- Synthesis changes don't break Ixpantilia (loose coupling)
- Overhead ~50-100ms acceptable for non-interactive use
- Simpler deployment (one codebase, one process)

**Trade-offs Accepted**: Slightly higher latency, but worth it for maintainability

---

### DEC-002: Why No Chunking?

**Date**: 2025-11-18
**Context**: Obsidian Copilot uses 6000-char chunks. Should Ixpantilia chunk documents?
**Decision**: No chunking initially
**Rationale**:
- Gleanings are already small (<500 chars typically)
- Atomic units (one link per note)
- Synthesis handles short documents well
- Reduces implementation complexity

**Re-evaluate if**: Gleanings grow to include long summaries (>2000 chars)

---

### DEC-003: Why No Caching Initially?

**Date**: 2025-11-18
**Context**: Should we cache Synthesis search results?
**Decision**: No caching in Phase 1
**Rationale**:
- Measure Synthesis performance first (Phase 0)
- Avoid premature optimization
- Cache invalidation adds complexity
- Server has more RAM than mobile (less constrained)

**Add caching if**: Search takes >500ms consistently AND same queries repeat often

**Caching strategy if needed**: Simple in-memory LRU cache with 15-minute TTL

---

## Future Topics to Chronicle

Questions to answer in future entries:

- How did Phase 0 performance testing go?
- Did obsidian:// URIs work reliably on mobile?
- What gleaning formats were found in the wild?
- How many gleanings were actually extracted?
- Did the <2s response time hypothesis hold?
- What was the actual adoption curve?
- Which features got used vs. ignored?

---

## Meta: How to Use This Document

**When starting a new session:**
1. Read the latest entry to understand recent discussions
2. Check Decision Log before proposing architectural changes
3. Add new entries when major design questions arise

**When making a design decision:**
1. Summarize the context and options
2. Document the decision and rationale
3. Note trade-offs accepted
4. Add to Decision Log with unique ID (DEC-XXX)

**When questioning a decision:**
1. Read the original rationale in Decision Log
2. Check if context has changed
3. If reversing decision, document why in new entry

---

**Remember**: This document explains *why*. IMPLEMENTATION.md explains *what*. CLAUDE.md explains *how*.

If you're wondering "why are we doing it this way?", the answer should be here.

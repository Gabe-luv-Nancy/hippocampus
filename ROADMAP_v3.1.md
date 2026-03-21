# Hippocampus Photon v3.1 Roadmap

> **Status**: Planned  
> **Target**: Post v3.0.0  
> **Last Updated**: 2026-03-21

---

## New Features

### 1. Micro-Macro Workflow Memory (P0)

**Problem**: Users often express complex needs with brief instructions.

Examples:
- User says "发文件" (send file) → AI should know to send via Feishu in MD format
- User says "帮我整理" (organize for me) → AI should know user's preferred organization method

**Core Concept**:
- **Micro**: Short user command (e.g., "发文件")
- **Macro**: Complete action workflow behind it (e.g., "send via Feishu, MD format")

**Data Structure**:
```yaml
micro_macro_workflows:
  - micro: "发文件"
    macro:
      channel: "feishu"
      format: "md"
      action: "send_file"
    keywords: ["发", "文件", "过来"]
    usage_count: 5
    last_used: "2026-03-21"
    
  - micro: "帮我整理"
    macro:
      tool: "organize"
      pattern: "by_date"
      destination: "workspace"
    keywords: ["整理", "归类"]
    usage_count: 3
```

**Matching Mechanism**:
```python
def match_micro_macro(user_input: str) -> Optional[MacroWorkflow]:
    # 1. Exact match on micro
    # 2. Fuzzy match on keywords
    # 3. Semantic similarity matching
    # 4. Fallback to asking user
```

**Implementation**:
- New command: `/photon learn-workflow <micro> → <macro>`
- Store in `assets/hippocampus/micro_macro/`
- Index by keywords for fast lookup

---

### 2. Achievement/Reward Incentive System (P1)

**Problem**: When user gives lots of affirmation (e.g., multiple praises), AI should:
- Remember characteristics of current working mode
- Recognize this as a successful pattern
- Reuse in future workflows

**Quantifying "User Affirmation"**:
```yaml
positive_signals:
  praise_keywords: ["好", "不错", "棒", "完美", "厉害", "谢谢", "👍", "✨"]
  strong_affirmation: ["完全正确", "就是", "非常好", "正是如此"]
  
thresholds:
  light_positive: 2  # Simple record
  medium_positive: 4  # Record + analyze
  strong_positive: 6  # Extract pattern + mark for reuse
```

**Achievement Storage**:
```yaml
achievements:
  - timestamp: "2026-03-21 17:30"
    session_context: "Solving Hippocampus version issue"
    user_affirmation_level: 6
    successful_patterns:
      - "Quickly locate root cause"
      - "Execute step by step"
      - "Proactive progress reporting"
    reusable_aspects:
      working_mode: "step-by-step confirmation"
      communication_style: "concise and proactive"
```

**Reuse Mechanism**:
- When encountering similar tasks, retrieve historical success patterns
- Suggest using previously effective communication/execution methods
- User can mark "this pattern worked well"

---

### 3. Integration with Existing Architecture

| New Feature | Existing Component | Integration |
|-------------|-------------------|-------------|
| Micro-Macro | Monograph | New `workflow.md` type |
| Achievement | Chronicle | New `achievement.md` type |
| Both | Index | Shared keyword index |

---

## Priority

| Priority | Feature | Reason |
|----------|---------|--------|
| P0 | Micro-Macro Workflow | Direct user benefit |
| P1 | Achievement Quantization | System enhancement |
| P2 | Pattern Reuse Recommendation | Future enhancement |

---

## Implementation Notes

### For Micro-Macro
1. Create `micro_macro/` directory under assets
2. Store workflows as YAML files
3. Add keyword index for fast matching
4. Add `/photon learn-workflow` command

### For Achievement System
1. Create `achievements/` directory under assets
2. Track positive signals from user messages
3. Generate achievement records after threshold
4. Add `/photon achievements` command to view history

### Compatibility
- v3.1 is backward compatible with v3.0
- New features are additive only
- Existing commands unchanged
- Old data remains accessible

---

## Out of Scope for v3.1

- AI-generated workflow suggestions (needs LLM integration)
- Automatic pattern recognition (future ML feature)
- Cross-session workflow learning (needs more infrastructure)
- Social/sharing features (not aligned with philosophy)

# Recent Changes

## 2026-01-24: Switched to All-Claude Architecture

### What Changed
All AI agents now use **Claude Sonnet 4.5** instead of mixing Claude and OpenAI:

- ✅ **Architect Agent**: `anthropic:claude-sonnet-4-5` (was already Claude)
- ✅ **Builder Agent**: `anthropic:claude-sonnet-4-5` (changed from `openai:gpt-4o`)
- ✅ **Genesis Agent**: `anthropic:claude-opus-4-5` (was already Claude)

### Why This Change?

1. **No Rate Limits**: Claude has higher rate limits than OpenAI's free tier
2. **Better Consistency**: All agents use the same AI family
3. **Simpler Setup**: Only need `ANTHROPIC_API_KEY` (OpenAI key optional)
4. **Cost Effective**: Claude's pricing is competitive and you have AWS credits

### Files Updated

- [agents/builder_agent.py](agents/builder_agent.py) - Line 320
- [genesis/genesis_engine.py](genesis/genesis_engine.py) - Line 310

### How to Use

Just run the demo - it will automatically use Claude for all operations:

```bash
python3 examples/genesis_demo.py
```

No configuration changes needed - your existing `ANTHROPIC_API_KEY` in `.env` works for all agents now!

### Performance Notes

Claude Sonnet 4.5 provides:
- **Faster responses** than GPT-4o in many cases
- **Better code generation** with fewer iterations
- **Higher context window** (200k tokens)
- **Built-in prompt caching** to reduce costs

You should see the self-healing loop complete successfully without hitting rate limits.

---

**Previous setup**: Architect (Claude) → Builder (OpenAI) → QA
**Current setup**: Architect (Claude) → Builder (Claude) → QA ✅

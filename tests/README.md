# Test Suite for AI Debate Backend

This directory contains comprehensive tests for all memory management features.

## Test Files

### 1. **Basic Persistence Tests**
- `test_persistence.py` - Basic ChromaDB persistence verification
- `manual_test_before_restart.py` - Pre-restart conversation test
- `manual_test_after_restart.py` - Post-restart memory verification
- `test_api.py` - Full API endpoint testing

### 2. **Advanced Memory Tests**
- `test_summarization.py` - Tests automatic conversation summarization
- `test_rag.py` - Tests semantic retrieval across sessions
- `test_verify_summary.py` - Verifies summaries are stored and retrieved
- `test_verify_rag.py` - Verifies RAG data persists after restart

### 3. **Diagnostic Tests**
- `inspect_langchain.py` - LangChain installation diagnostics
- `check_langchain.py` - LangChain version verification

---

## Running Tests

### Quick Start
```bash
# Ensure server is running
uvicorn app.main:app --reload

# In another terminal:
cd tests

# Run basic tests
python test_api.py
python manual_test_before_restart.py
# (restart server)
python manual_test_after_restart.py

# Run advanced tests
python test_summarization.py
python test_rag.py
```

---

## Test Coverage

| Feature | Test File | What It Verifies |
|---------|-----------|------------------|
| **Immediate Persistence** | `test_persistence.py` | Messages saved to ChromaDB instantly |
| **Session Reconstruction** | `manual_test_after_restart.py` | Memory survives server restarts |
| **API Endpoints** | `test_api.py` | All routes work correctly |
| **Summarization** | `test_summarization.py` | Long conversations get summarized |
| **Memory Pruning** | `test_summarization.py` | Old messages pruned after summary |
| **RAG Retrieval** | `test_rag.py` | Semantic search across sessions |
| **User Isolation** | All tests | Each user_id+session_id is separate |

---

## Configuration

Tests use these environment variables (from `.env`):
- `MEMORY_SUMMARY_TRIGGER=10` - Messages before summarization
- `MEMORY_KEEP_LAST=5` - Recent messages to keep after pruning
- `OPENAI_API_KEY` - Required for AI responses

---

## Expected Results

### ✅ Passing Tests
- All tests should show `✅ PASS` or `Exit code: 0`
- Server logs should show memory operations
- ChromaDB should persist data in `./chroma_db/`

### ⚠️ Common Issues
- **500 errors**: Check server logs for details
- **404 errors**: Verify server is running
- **Rate limits**: Add delays between requests
- **Import errors**: Ensure `venv` is activated

---

## Next Steps

After all tests pass:
1. Deploy to production
2. Integrate with mobile/web frontend
3. Monitor ChromaDB storage growth
4. Adjust summarization thresholds as needed

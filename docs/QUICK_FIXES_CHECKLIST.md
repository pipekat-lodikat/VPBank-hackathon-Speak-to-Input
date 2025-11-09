# Quick Wins Checklist - VPBank Voice Agent

Quick fixes that can be done in **1-2 days** with **high impact** on code quality and production readiness.

---

## Priority 1: Security Fixes (3-4 hours)

### [ ] 1. Remove Hardcoded Production URL
**File:** `frontend/src/config/api.ts` (line 17)  
**Current:**
```typescript
return 'https://lie-confidential-substance-anna.trycloudflare.com';
```
**Fix:**
```typescript
// Use environment variable or empty for production
return import.meta.env.VITE_PROD_API_URL || '';
```
**Time:** 15 minutes

### [ ] 2. Remove Actual API Key from .env.example
**File:** `.env.example` (line 40)  
**Current:**
```
BROWSER_USE_API_KEY=bu_DPDJlDjgOTllFTImbQ40sKcyvzSIejx7BYHfG59uDEw
```
**Fix:**
```
BROWSER_USE_API_KEY=your_browser_use_api_key_here
```
**Time:** 5 minutes

### [ ] 3. Clean up AWS Key Logging
**File:** `src/auth_service.py` (line 31)  
**Current:**
```python
logger.info(f"🔐 Using AUTH credentials: {auth_access_key[:8]}...")
```
**Fix:**
```python
logger.info("🔐 Using separate AUTH credentials")
# Don't log any part of the key
```
**Time:** 5 minutes

---

## Priority 2: Configuration & Deployment (2-3 hours)

### [ ] 4. Fix Docker Compose Voice Bot Health Check
**File:** `docker-compose.yml` (line 62)  
**Current:**
```yaml
test: ["CMD", "curl", "-f", "http://localhost:7860/"]
```
**Fix:**
```yaml
test: ["CMD", "curl", "-f", "http://localhost:7860/health"]
```
**Time:** 2 minutes

### [ ] 5. Add Service Health Check Condition to Frontend
**File:** `docker-compose.yml` (line 82-83)  
**Current:**
```yaml
depends_on:
  - voice-bot
```
**Fix:**
```yaml
depends_on:
  voice-bot:
    condition: service_healthy
```
**Time:** 2 minutes

### [ ] 6. Update .env.example with Missing Variables
**File:** `.env.example`  
**Add:**
```
# Service Configuration
HOST=0.0.0.0
PORT=7860
LOG_LEVEL=INFO

# WebRTC Configuration (optional)
STUN_SERVER=stun:stun.l.google.com:19302
TURN_SERVER=turn:openrelay.metered.ca:80
TURN_USERNAME=openrelayproject
TURN_CREDENTIAL=openrelayproject
```
**Time:** 10 minutes

### [ ] 7. Update .env.example with Empty DynamoDB Credentials
**File:** `.env.example` (lines 36-38)  
**Current:**
```
DYNAMODB_ACCESS_KEY_ID=
DYNAMODB_SECRET_ACCESS_KEY=
```
**Fix:**
```
# Use separate credentials for DynamoDB (optional - uses main credentials if not set)
DYNAMODB_ACCESS_KEY_ID=your_dynamodb_access_key_here
DYNAMODB_SECRET_ACCESS_KEY=your_dynamodb_secret_key_here
```
**Time:** 5 minutes

### [ ] 8. Make Vite Proxy Configurable
**File:** `frontend/vite.config.ts` (line 18)  
**Current:**
```typescript
target: 'http://127.0.0.1:7860',
```
**Fix:**
```typescript
target: process.env.VITE_BACKEND_URL || 'http://127.0.0.1:7860',
```
**Time:** 5 minutes

---

## Priority 3: Code Cleanup (2-3 hours)

### [ ] 9. Remove Backup & Unused Dockerfile Files
**Files to delete:**
- `Dockerfile.backup.20251109_180921`
- `Dockerfile.browser`
- `Dockerfile.frontend`
- `Dockerfile.voice`
- `.cleanup_backup_20251109_190943/` directory

**Commands:**
```bash
git rm Dockerfile.backup.20251109_180921
git rm Dockerfile.browser
git rm Dockerfile.frontend
git rm Dockerfile.voice
git rm -r .cleanup_backup_20251109_190943/
git commit -m "chore: remove backup and unused dockerfile variants"
```
**Time:** 10 minutes

### [ ] 10. Add Missing Module __init__.py Files
**Files to create (empty is fine):**
```bash
touch src/monitoring/__init__.py
touch src/verification/__init__.py
touch src/security/__init__.py
touch src/cost/__init__.py
touch src/prompts/__init__.py
touch src/llm_evaluator/__init__.py
```
**Time:** 5 minutes

### [ ] 11. Add Type Annotation to Untyped Variable
**File:** `frontend/src/pages/ChatPage.tsx` (line 40)  
**Current:**
```typescript
public connected = false;
```
**Fix:**
```typescript
public connected: boolean = false;
```
**Time:** 5 minutes

### [ ] 12. Create Frontend Utils Directory
**Create file:** `frontend/src/utils/logger.ts`
```typescript
export const logger = {
  debug: (msg: string) => {
    if (import.meta.env.DEV) console.debug(`[DEBUG] ${msg}`);
  },
  info: (msg: string) => {
    console.log(`[INFO] ${msg}`);
  },
  warn: (msg: string) => {
    console.warn(`[WARN] ${msg}`);
  },
  error: (msg: string, err?: Error) => {
    console.error(`[ERROR] ${msg}`, err);
  },
};
```

**Replace console.log in ChatPage.tsx:**
```typescript
// Instead of:
console.log("🎙️ [DEBUG] Starting WebRTC connection...");

// Use:
import { logger } from '../utils/logger';
logger.debug("Starting WebRTC connection");
```
**Time:** 1-2 hours

---

## Priority 4: Documentation (1-2 hours)

### [ ] 13. Add JSDoc Comments to Key Functions
**Files:** `src/voice_bot.py`, `src/browser_agent.py`

**Example for voice_bot.py (line 113):**
```python
async def push_to_browser_service(
    user_message: str, 
    ws_connections: set, 
    session_id: str, 
    processing_flag: dict
) -> None:
    """
    Send request to Browser Agent Service via HTTP API.
    
    Implements exponential backoff retry logic and WebSocket notification on completion.
    
    Args:
        user_message: Full conversation context from user
        ws_connections: Set of active WebSocket connections for notifications
        session_id: Current session ID for tracking
        processing_flag: Dict to track processing state (dict['active'], dict['task_id'])
        
    Returns:
        None (updates WebSocket connections with results)
        
    Raises:
        asyncio.TimeoutError: If Browser Service doesn't respond within 5 minutes
    """
```
**Time:** 2-3 hours

### [ ] 14. Add Comments to Complex Regex Patterns
**File:** `src/voice_bot.py` (lines 169-173)
```python
# Remove JSON code blocks (browser agent returns formatted JSON)
final_message = re.sub(r'```json\s*\{[^}]*\}\s*```', '', final_message, flags=re.DOTALL)
# Remove other markdown code blocks
final_message = re.sub(r'```[^`]*```', '', final_message, flags=re.DOTALL)
# Remove raw JSON objects (fallback for unformatted responses)
final_message = re.sub(r'\{[^}]*\}', '', final_message)
```
**Time:** 15 minutes

---

## Summary Table

| # | Task | File | Time | Priority |
|---|------|------|------|----------|
| 1 | Remove hardcoded tunnel URL | frontend/src/config/api.ts | 15m | CRITICAL |
| 2 | Remove API key from .env.example | .env.example | 5m | CRITICAL |
| 3 | Clean up AWS key logging | src/auth_service.py | 5m | CRITICAL |
| 4 | Fix voice-bot health check | docker-compose.yml | 2m | HIGH |
| 5 | Add health check condition | docker-compose.yml | 2m | HIGH |
| 6 | Add missing env vars | .env.example | 10m | HIGH |
| 7 | Document DynamoDB creds | .env.example | 5m | HIGH |
| 8 | Make proxy configurable | frontend/vite.config.ts | 5m | HIGH |
| 9 | Remove backup files | Various | 10m | MEDIUM |
| 10 | Add __init__.py files | src/ | 5m | MEDIUM |
| 11 | Add type annotation | frontend/src/pages/ChatPage.tsx | 5m | MEDIUM |
| 12 | Create logger utility | frontend/src/utils/ | 1-2h | MEDIUM |
| 13 | Add JSDoc comments | src/voice_bot.py, browser_agent.py | 2-3h | LOW |
| 14 | Comment complex regexes | src/voice_bot.py | 15m | LOW |

**Total Time:** ~6-8 hours spread across 2 days  
**Impact:** Immediate improvement in security, deployment reliability, and code maintainability

---

## Implementation Order

**Day 1 - Morning (3-4 hours):**
1. Complete tasks 1-8 (Security, Config, Vite proxy)
2. Delete backup files (task 9)
3. Add __init__.py files (task 10)

**Day 1 - Afternoon (1-2 hours):**
4. Create logger utility (task 12) 
5. Replace console.log in ChatPage

**Day 2 - Morning (2-3 hours):**
6. Add JSDoc comments (task 13)
7. Add regex comments (task 14)
8. Minor cleanup

---

## Testing After Changes

```bash
# Docker
docker-compose build
docker-compose up
# Verify health checks pass

# Frontend
cd frontend
npm run dev
# Check browser console for logger output

# Backend
# Run voice-bot health check
curl http://localhost:7860/health

# Run browser agent health check
curl http://localhost:7863/api/health
```

---

## Git Workflow

```bash
# Create feature branch
git checkout -b chore/codebase-quality-improvements

# Make changes
# Commit with descriptive messages
git commit -m "chore: remove hardcoded production URL from api config"
git commit -m "chore: remove credentials from .env.example"
git commit -m "fix: correct docker-compose health check paths"

# Create Pull Request
git push origin chore/codebase-quality-improvements
```

---

## Next Steps After Quick Wins

1. Create `src/config.py` for centralized configuration
2. Create `src/exceptions.py` for custom exceptions
3. Create `frontend/src/utils/api.ts` for API client wrapper
4. Add pytest tests for critical functions
5. Document architecture in ADRs


# Troubleshooting Guide

## AWS Transcribe Timeout Errors

### Error Message:
```
ERROR | AWSTranscribeSTTService Exception from AWS: Your request timed out because no new audio was received for 15 seconds.
```

### Explanation:
This is **NORMAL BEHAVIOR**, not an error. AWS Transcribe automatically closes the WebSocket connection after 15 seconds of silence to save costs.

### What happens:
1. User stops speaking
2. After 15 seconds of no audio, AWS Transcribe closes connection
3. Connection automatically re-establishes when user speaks again
4. No action needed

### Why this happens:
- AWS Transcribe charges per second of audio processed
- Auto-closing prevents unnecessary charges during silence
- This is a cost-optimization feature, not a bug

### Solution:
**No fix needed.** This is expected behavior. The error log can be safely ignored.

If you want to suppress these logs, you can filter them in your log viewer or adjust logging levels.

---

## Other Common Issues

### WebRTC Connection Timeout
**Symptom:** "Timeout establishing the connection to the remote peer"

**Cause:** No audio being sent from browser or network issues

**Solution:**
1. Check microphone permissions in browser
2. Ensure HTTPS is used (required for WebRTC)
3. Check firewall/network settings

### Token Expired Errors
**Symptom:** "Access Token has expired"

**Cause:** Cognito authentication token expired (default: 1 hour)

**Solution:** User needs to log in again

### Mixed Content Errors
**Symptom:** "Mixed Content: The page at 'https://...' was loaded over HTTPS, but requested an insecure resource"

**Cause:** Frontend (HTTPS) trying to call backend (HTTP)

**Solution:** Ensure both frontend and backend use HTTPS in production

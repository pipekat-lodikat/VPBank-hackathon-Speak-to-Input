# WebRTC Debug Instructions - Enhanced Logging

## Overview
The frontend has been updated with comprehensive WebRTC debug logging. This guide will help you test and diagnose the connection timeout issue.

## Test Preparation

### 1. Clear Browser Cache
**Chrome/Edge:**
1. Press `Ctrl+Shift+Delete` (Windows/Linux) or `Cmd+Shift+Delete` (Mac)
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh page with `Ctrl+F5` or `Cmd+Shift+R`

**Firefox:**
1. Press `Ctrl+Shift+Delete`
2. Select "Cache"
3. Click "Clear Now"
4. Refresh page with `Ctrl+F5`

### 2. Open Browser DevTools Console
1. Press `F12` or `Ctrl+Shift+I` (Windows/Linux) / `Cmd+Option+I` (Mac)
2. Click the **Console** tab
3. Keep DevTools open during the entire test

### 3. Access Production URL
```
https://d359aaha3l67dn.cloudfront.net
```

## What to Look For

### Expected Success Flow (with new debug logs):

```
🎙️ [DEBUG] Starting WebRTC connection...
🔧 [DEBUG] Creating new RTCPeerConnection
🎤 [DEBUG] Requesting microphone access with constraints: {audio: true, video: false}
✅ [DEBUG] Microphone access granted
🎙️ [DEBUG] Local audio track: {id: "...", enabled: true, readyState: "live", muted: false}
➕ [DEBUG] Adding audio track to peer connection

🔗 [DEBUG] Connecting to WebRTC endpoint: http://...
📤 [DEBUG] Sending WebRTC offer SDP: {type: "offer", sdpLength: 2500, ...}

📊 [DEBUG] Connection monitor: {
  connectionState: "new",
  iceConnectionState: "new",
  iceGatheringState: "gathering",
  signalingState: "have-local-offer"
}

🧊 [DEBUG] ICE candidate generated: {
  type: "host",
  protocol: "udp",
  address: "192.168.x.x",
  port: 54321,
  candidate: "candidate:..."
}

🧊 [DEBUG] ICE candidate generated: {
  type: "srflx",         ← IMPORTANT: STUN candidate
  protocol: "udp",
  address: "1.2.3.4",    ← Your public IP
  port: 54321,
  candidate: "candidate:..."
}

🧊 [DEBUG] ICE candidate generated: {
  type: "relay",         ← IMPORTANT: TURN candidate
  protocol: "udp",
  address: "openrelay.metered.ca",
  port: 80,
  candidate: "candidate:..."
}

🧊 [DEBUG] ICE gathering complete

📥 [DEBUG] Response status: 200 OK
✅ [DEBUG] Received WebRTC answer: {
  type: "answer",
  sdpLength: 2800,
  hasIceCandidates: true
}
✅ [DEBUG] Remote description set successfully

📊 [DEBUG] Connection monitor: {
  connectionState: "connecting",
  iceConnectionState: "checking",
  iceGatheringState: "complete",
  signalingState: "stable"
}

🧊 [DEBUG] ICE connection state: connected    ← SUCCESS!
🔄 [DEBUG] Connection state changed: connected

📊 [DEBUG] Connection monitor: {
  connectionState: "connected",               ← SUCCESS!
  iceConnectionState: "connected",
  iceGatheringState: "complete",
  signalingState: "stable"
}

🔊 [DEBUG] Remote audio track received
📊 [DEBUG] Audio level: 15.3% (frames: 120)
```

## Critical Checks

### 1. ICE Candidates
**What to Check:**
- Do you see `type: "host"` candidates? (Should always appear)
- Do you see `type: "srflx"` candidates? (STUN server working)
- Do you see `type: "relay"` candidates? (TURN server working)

**If NO "srflx" candidates:**
- STUN server (stun.l.google.com:19302) is blocked or unreachable
- Check firewall/network settings for UDP port 3478

**If NO "relay" candidates:**
- TURN server (turn:openrelay.metered.ca:80) is blocked or unreachable
- Backend may need different TURN server configuration

### 2. Connection State Transitions
**Expected Sequence:**
```
connectionState: "new" → "connecting" → "connected" ✅
iceConnectionState: "new" → "checking" → "connected" ✅
```

**If stuck at "connecting" or "checking":**
- ICE negotiation is failing
- Candidates not being exchanged properly
- Network/firewall blocking WebRTC media ports

**If goes to "failed" or "disconnected":**
- All candidate pairs failed
- Need to check which candidates were generated
- May need alternative TURN server

### 3. Connection Monitor (Every 2 seconds)
The connection monitor logs every 2 seconds. Watch for:
```
📊 [DEBUG] Connection monitor: {...}
```

If `connectionState` stays at "connecting" for >15 seconds → TIMEOUT IMMINENT

### 4. Audio Levels
After connection succeeds, you should see:
```
📊 [DEBUG] Audio level: X% (frames: N)
```

**Test:** Speak into microphone → audio level should increase to 30-80%
- If always 0%, microphone is muted or not capturing
- If connection times out before this, WebRTC never established

## Common Failure Patterns

### Pattern 1: No STUN candidates (srflx)
```
🧊 [DEBUG] ICE candidate generated: {type: "host", ...}
🧊 [DEBUG] ICE gathering complete
❌ No "srflx" candidate found!
```
**Fix:** UDP port 3478 blocked by firewall or STUN server unreachable

### Pattern 2: No TURN candidates (relay)
```
🧊 [DEBUG] ICE candidate generated: {type: "host", ...}
🧊 [DEBUG] ICE candidate generated: {type: "srflx", ...}
🧊 [DEBUG] ICE gathering complete
❌ No "relay" candidate found!
```
**Fix:** TURN server configuration issue or blocked

### Pattern 3: Timeout after 14 seconds
```
📊 [DEBUG] Connection monitor: {connectionState: "connecting", ...}
📊 [DEBUG] Connection monitor: {connectionState: "connecting", ...}
⏰ Timeout establishing the connection to the remote peer
🧊 [DEBUG] ICE connection state: closed
```
**Fix:** ICE candidates generated but connection negotiation failed

## What to Report Back

Please copy and paste from the console:

1. **ALL ICE candidates** (lines starting with `🧊 [DEBUG] ICE candidate generated:`)
2. **Connection monitor logs** (lines starting with `📊 [DEBUG] Connection monitor:`)
3. **Any error messages** (lines starting with `❌`)
4. **Final connection state** before timeout

Example of what to share:
```
🧊 [DEBUG] ICE candidate generated: {type: "host", protocol: "udp", address: "192.168.1.100", port: 54321}
🧊 [DEBUG] ICE candidate generated: {type: "srflx", protocol: "udp", address: "1.2.3.4", port: 54321}
🧊 [DEBUG] ICE gathering complete
📊 [DEBUG] Connection monitor: {connectionState: "connecting", iceConnectionState: "checking", ...}
📊 [DEBUG] Connection monitor: {connectionState: "connecting", iceConnectionState: "checking", ...}
⏰ Timeout establishing the connection to the remote peer
```

## Backend Configuration (For Reference)

The backend is configured with:
- **STUN Server:** `stun:stun.l.google.com:19302`
- **TURN Server:** `turn:openrelay.metered.ca:80`
- **TURN Username:** `openrelayproject`
- **TURN Credential:** `openrelayproject`

These are passed to `SmallWebRTCConnection` in the backend (voice_bot.py:897).

## Additional Diagnostic Tools

### Chrome: chrome://webrtc-internals
1. Open new tab
2. Navigate to `chrome://webrtc-internals`
3. Start connection in main tab
4. Watch WebRTC stats in internals tab
5. Look for "RTCPeerConnection" section
6. Check "Stats graphs" for detailed metrics

### Firefox: about:webrtc
1. Open new tab
2. Navigate to `about:webrtc`
3. Start connection in main tab
4. View detailed WebRTC connection info
5. Check "Connection Log" for debug details

## Next Steps

After testing, please share:
1. Which ICE candidate types were generated (host/srflx/relay)
2. Where the connection state gets stuck
3. The console logs from the test
4. Any error messages

This will help us identify whether:
- STUN server is working
- TURN server is working
- ICE negotiation is completing
- Network/firewall is blocking connections

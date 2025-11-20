# Browser DevTools Console Debugging Guide

## How to Open DevTools Console

### Google Chrome / Microsoft Edge
1. Press `F12` or `Ctrl+Shift+I` (Windows/Linux) / `Cmd+Option+I` (Mac)
2. Click the **Console** tab
3. Leave the DevTools window open while using the application

### Mozilla Firefox
1. Press `F12` or `Ctrl+Shift+K` (Windows/Linux) / `Cmd+Option+K` (Mac)
2. Click the **Console** tab
3. Leave the DevTools window open while using the application

### Safari
1. Enable Developer Menu: Safari > Preferences > Advanced > Check "Show Develop menu"
2. Press `Cmd+Option+C` or Develop > Show JavaScript Console
3. Leave the Console window open while using the application

---

## What to Look For: Debug Logs Checklist

Once the console is open, click the **Start** button to initiate the voice connection. You should see a sequence of debug logs:

### ✅ Expected Success Flow:

```
🎙️ [DEBUG] Starting WebRTC connection...
🔧 [DEBUG] Creating new RTCPeerConnection
🎤 [DEBUG] Requesting microphone access with constraints: {audio: true, video: false}
✅ [DEBUG] Microphone access granted
🎙️ [DEBUG] Local audio track: {id: "...", label: "...", enabled: true, readyState: "live", muted: false}
➕ [DEBUG] Adding audio track to peer connection
🔗 Connecting to WebRTC endpoint: http://...
📤 Sending WebRTC offer...
📥 Response status: 200 OK
✅ Received WebRTC answer: answer
✅ Remote description set successfully
🔄 [DEBUG] Connection state changed: connecting
🧊 [DEBUG] ICE candidate generated: host
🧊 [DEBUG] ICE candidate generated: srflx
🧊 [DEBUG] ICE gathering complete
🔄 [DEBUG] Connection state changed: connected
🔊 [DEBUG] Remote audio track received
📊 [DEBUG] Setting up audio analysis for track: {id: "...", enabled: true, readyState: "live"}
✅ [DEBUG] Audio analyser connected, starting animation
📊 [DEBUG] Audio level: 15.3% (frames: 120)  # Should update every 2 seconds
```

### ❌ Common Error Patterns:

#### 1. **Microphone Permission Denied**
```
🎙️ [DEBUG] Starting WebRTC connection...
🔧 [DEBUG] Creating new RTCPeerConnection
🎤 [DEBUG] Requesting microphone access with constraints: {audio: true, video: false}
❌ Error: NotAllowedError: Permission denied
```
**Fix:** Click the microphone icon in browser address bar and allow microphone access

#### 2. **No Audio Track**
```
✅ [DEBUG] Microphone access granted
❌ [DEBUG] No audio track found in local stream!
```
**Fix:** Check if another application is using the microphone, close it and retry

#### 3. **Muted or Disabled Track**
```
🎙️ [DEBUG] Local audio track: {enabled: false, readyState: "live", muted: true}
⚠️ [DEBUG] Audio track muted
```
**Fix:** Check system microphone settings and unmute

#### 4. **WebRTC Connection Timeout**
```
🔄 [DEBUG] Connection state changed: connecting
⏰ Timeout establishing the connection to the remote peer. Closing.
🔄 [DEBUG] Connection state changed: closed
```
**Fix:** Firewall/network issue - check UDP ports 3478 and 49152-65535

#### 5. **Zero Audio Levels (Silent Microphone)**
```
✅ [DEBUG] Audio analyser connected, starting animation
📊 [DEBUG] Audio level: 0.0% (frames: 120)  # Always 0%
📊 [DEBUG] Audio level: 0.0% (frames: 120)
```
**Fix:**
- Microphone is muted at hardware/OS level
- Wrong microphone selected in Settings
- Microphone privacy settings blocking access

---

## Detailed Debugging Steps

### Step 1: Verify Microphone Permissions

**Chrome:**
1. Click the 🔒 padlock or ⓘ icon in address bar
2. Check if "Microphone" is set to "Allow"
3. If "Block", change to "Allow" and refresh page

**Firefox:**
1. Click the 🔒 padlock in address bar
2. Look for "Use the Microphone" permission
3. Ensure it's "Allowed"

**Edge/Safari:**
- Similar to Chrome - check address bar permissions

### Step 2: Check Browser Console for Errors

Look for these specific error messages:

| Error Message | Meaning | Solution |
|--------------|---------|----------|
| `NotAllowedError` | Microphone permission denied | Allow in browser settings |
| `NotFoundError` | No microphone detected | Check hardware connection |
| `NotReadableError` | Microphone in use by another app | Close other apps using mic |
| `OverconstrainedError` | Selected device doesn't exist | Choose different device in Settings |
| `AbortError` | Microphone access interrupted | Refresh page and try again |

### Step 3: Verify Audio Levels

After connection succeeds, you should see:
```
📊 [DEBUG] Audio level: 15.3% (frames: 120)
```

**Try speaking into the microphone:**
- Audio levels should increase to 30-80%
- If always 0%, microphone is not capturing audio
- If always 100%, check for feedback loop

### Step 4: Check ICE Connection

```
🧊 [DEBUG] ICE candidate generated: host
🧊 [DEBUG] ICE candidate generated: srflx  ✅ Good - can connect through NAT
🧊 [DEBUG] ICE gathering complete
🔄 [DEBUG] Connection state changed: connected  ✅ Success!
```

If you DON'T see `srflx` candidate or connection fails:
- Network firewall blocking UDP
- STUN server (stun.l.google.com:19302) unreachable
- Try different network (mobile hotspot, VPN off)

### Step 5: Monitor for Disconnections

Watch for:
```
⚠️ [DEBUG] Audio track muted  # Hardware mute pressed
❌ [DEBUG] Audio track ended  # Device disconnected
🔄 [DEBUG] Connection state changed: disconnected  # Network issue
```

---

## Testing Checklist

Use this checklist when debugging:

- [ ] Open Browser DevTools Console (F12)
- [ ] Click "Start" button to initiate connection
- [ ] Verify `✅ [DEBUG] Microphone access granted` appears
- [ ] Verify `🎙️ [DEBUG] Local audio track: {enabled: true, readyState: "live"}` shows
- [ ] Verify `🔄 [DEBUG] Connection state changed: connected` appears
- [ ] Verify `📊 [DEBUG] Audio level: X%` updates every 2 seconds
- [ ] **Speak into microphone** and verify audio level increases
- [ ] If audio level stays at 0%, check system microphone settings
- [ ] If connection fails, check network/firewall settings
- [ ] If errors appear, read error message carefully and follow solutions above

---

## Exporting Console Logs

If you need to share logs for support:

### Chrome/Edge/Firefox:
1. Right-click in console
2. Select "Save as..." or "Export to file"
3. Save as `.txt` or `.log` file

### Or:
1. Select all console text (Ctrl+A)
2. Copy (Ctrl+C)
3. Paste into text file

---

## Additional WebRTC Diagnostic Tools

### Chrome: chrome://webrtc-internals
1. Open new tab
2. Navigate to `chrome://webrtc-internals`
3. This shows detailed WebRTC connection stats
4. Look for "RTCPeerConnection" section
5. Check "Stats graphs" for audio/video metrics

### Firefox: about:webrtc
1. Open new tab
2. Navigate to `about:webrtc`
3. View detailed WebRTC connection info
4. Check "Connection Log" for debug details

---

## Summary of Debug Log Meanings

| Icon | Log Type | Meaning |
|------|----------|---------|
| 🎙️ | Connection | WebRTC/microphone setup |
| 🔧 | Config | Creating peer connection |
| 🎤 | Permission | Requesting microphone access |
| ✅ | Success | Operation completed successfully |
| ➕ | Track | Adding media track |
| 🔗 | Network | Connecting to server |
| 📤 | Send | Sending data to server |
| 📥 | Receive | Receiving data from server |
| 🔄 | State | Connection state change |
| 🧊 | ICE | ICE candidate/gathering |
| 🔊 | Audio | Remote audio received |
| 📊 | Analysis | Audio analysis/levels |
| ⚠️ | Warning | Non-critical issue |
| ❌ | Error | Critical failure |
| 🔇 | Mute | Audio track muted/ended |

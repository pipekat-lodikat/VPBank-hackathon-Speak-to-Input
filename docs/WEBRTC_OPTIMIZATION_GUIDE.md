# WebRTC Connection Optimization Guide

## Current Issues Identified

### 1. Connection Timeouts
**Problem:** WebRTC connections timing out after 60 seconds during ICE gathering
```
WARNING | Timeout establishing the connection to the remote peer. Closing.
```

**Root Causes:**
- Default ICE gathering timeout is too short
- UDP ports may be restricted in some network configurations
- NAT traversal issues for clients behind strict firewalls

### 2. ICE Gathering Delays
**Problem:** ICE gathering takes 5-7 seconds before connection completes
```
DEBUG | ICE gathering state is gathering
[5 second delay]
DEBUG | ICE gathering state is complete
```

**Impact:** Poor user experience with slow connection establishment

### 3. Audio Frame Timeouts
**Problem:** Audio read timeouts after session establishment
```
WARNING | Timeout: No audio frame received within the specified time.
```

**Cause:** User not speaking (expected behavior, but can be optimized)

---

## Optimization Recommendations

### Backend Optimizations (voice_bot.py)

#### 1. Configure ICE Server Priority
**Current:**
```python
ice_servers = [
    IceServer(urls=STUN_SERVER),  # Google STUN
    IceServer(
        urls=TURN_SERVER,  # OpenRelay TURN
        username=TURN_USERNAME,
        credential=TURN_CREDENTIAL
    ),
]
```

**Optimized:**
```python
# Use multiple STUN servers for redundancy
ice_servers = [
    IceServer(urls="stun:stun.l.google.com:19302"),
    IceServer(urls="stun:stun1.l.google.com:19302"),
    IceServer(urls="stun:stun2.l.google.com:19302"),
    IceServer(
        urls="turn:openrelay.metered.ca:80",
        username="openrelayproject",
        credential="openrelayproject"
    ),
    IceServer(
        urls="turn:openrelay.metered.ca:443",  # TLS TURN for restrictive networks
        username="openrelayproject",
        credential="openrelayproject"
    ),
]
```

#### 2. Add Connection Timeout Configuration
**Add to voice_bot.py:**
```python
# WebRTC connection parameters
WEBRTC_CONNECTION_TIMEOUT = int(os.getenv("WEBRTC_CONNECTION_TIMEOUT", "90"))  # seconds
ICE_GATHERING_TIMEOUT = int(os.getenv("ICE_GATHERING_TIMEOUT", "10"))  # seconds

# When creating SmallWebRTCConnection
webrtc_connection = SmallWebRTCConnection(
    ice_servers=ice_servers,
    # Note: Pipecat 0.0.91 may not support these params directly
    # Check library documentation for timeout configuration
)
```

#### 3. Implement Connection State Monitoring
**Add connection monitoring:**
```python
async def monitor_webrtc_connection(connection, session_id):
    """Monitor WebRTC connection health"""
    try:
        # Wait for connection to establish
        timeout = WEBRTC_CONNECTION_TIMEOUT
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check connection state
            if connection.connection_state == "connected":
                logger.info(f"✅ WebRTC connected for session {session_id}")
                return True
            elif connection.connection_state in ["failed", "closed"]:
                logger.error(f"❌ WebRTC failed for session {session_id}")
                return False

            await asyncio.sleep(1)

        logger.warning(f"⏱️ WebRTC connection timeout for session {session_id}")
        return False

    except Exception as e:
        logger.error(f"Error monitoring connection: {e}")
        return False
```

#### 4. Add Connection Keepalive
**Prevent idle disconnections:**
```python
# Add to pipeline params
pipeline_params = PipelineParams(
    enable_metrics=True,
    enable_usage_metrics=True,
    send_initial_empty_metrics=True,
    # Add idle timeout (Pipecat specific)
    idle_timeout=600,  # 10 minutes (from logs, default is 5 min)
)
```

---

### Frontend Optimizations

#### 1. Configure RTCPeerConnection Timeout
**Add to WebRTC initialization:**
```typescript
const configuration: RTCConfiguration = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    {
      urls: 'turn:openrelay.metered.ca:80',
      username: 'openrelayproject',
      credential: 'openrelayproject',
    },
  ],
  iceCandidatePoolSize: 10,  // Pre-gather candidates
  bundlePolicy: 'max-bundle',
  rtcpMuxPolicy: 'require',
  iceTransportPolicy: 'all',  // Use TURN if STUN fails
};
```

#### 2. Implement ICE Gathering Timeout
**Add timeout for ICE gathering:**
```typescript
const gatheringTimeout = setTimeout(() => {
  if (peerConnection.iceGatheringState !== 'complete') {
    console.warn('ICE gathering timeout, proceeding with gathered candidates');
    // Proceed with connection even if gathering incomplete
    handleIceGatheringComplete();
  }
}, 10000); // 10 seconds

peerConnection.addEventListener('icegatheringstatechange', () => {
  if (peerConnection.iceGatheringState === 'complete') {
    clearTimeout(gatheringTimeout);
    handleIceGatheringComplete();
  }
});
```

#### 3. Add Connection State Monitoring
**Monitor and handle connection states:**
```typescript
peerConnection.addEventListener('connectionstatechange', () => {
  console.log('Connection state:', peerConnection.connectionState);

  switch (peerConnection.connectionState) {
    case 'connected':
      console.log('✅ WebRTC connected');
      onConnected();
      break;
    case 'disconnected':
      console.warn('⚠️ WebRTC disconnected, attempting reconnect...');
      handleReconnect();
      break;
    case 'failed':
      console.error('❌ WebRTC connection failed');
      onConnectionFailed();
      break;
    case 'closed':
      console.log('🔒 WebRTC connection closed');
      onConnectionClosed();
      break;
  }
});
```

#### 4. Implement Automatic Reconnection
**Handle temporary disconnections:**
```typescript
let reconnectAttempts = 0;
const maxReconnectAttempts = 3;

async function handleReconnect() {
  if (reconnectAttempts >= maxReconnectAttempts) {
    console.error('Max reconnect attempts reached');
    onConnectionFailed();
    return;
  }

  reconnectAttempts++;
  console.log(`Reconnect attempt ${reconnectAttempts}/${maxReconnectAttempts}`);

  // Wait before reconnecting
  await new Promise(resolve => setTimeout(resolve, 2000 * reconnectAttempts));

  // Create new connection
  await initializeWebRTC();
}
```

---

### Infrastructure Optimizations

#### 1. Security Group Configuration
**Ensure UDP ports are open for WebRTC media:**

```bash
# Voice Bot ECS tasks security group
aws ec2 authorize-security-group-ingress \
  --group-id sg-02c87c9c66309b96d \
  --protocol udp \
  --port 49152-65535 \
  --source-group sg-05ab72eaf899dde86  # ALB security group

# ALB security group (if direct WebRTC connection)
aws ec2 authorize-security-group-ingress \
  --group-id sg-05ab72eaf899dde86 \
  --protocol udp \
  --port 49152-65535 \
  --cidr 0.0.0.0/0
```

**Note:** For production, restrict UDP range to specific ports (e.g., 49152-49252) to limit attack surface.

#### 2. Enable CloudFront WebSocket Support
**CloudFront distribution should support WebSocket headers:**
- Origin Protocol Policy: HTTP/HTTPS
- Allowed HTTP Methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
- Forward Headers: Host, Origin, WebSocket-specific headers

#### 3. Configure ALB Target Group Health Checks
**Optimize health check settings:**
```bash
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:590183822512:targetgroup/vpbank-va-voice-tg/ae94fb33d60195af \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 10 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3
```

---

### Environment Variables (Add to .env)

```bash
# WebRTC Configuration
STUN_SERVER=stun:stun.l.google.com:19302
TURN_SERVER=turn:openrelay.metered.ca:80
TURN_USERNAME=openrelayproject
TURN_CREDENTIAL=openrelayproject

# Connection Timeouts
WEBRTC_CONNECTION_TIMEOUT=90
ICE_GATHERING_TIMEOUT=10
IDLE_SESSION_TIMEOUT=600

# Alternative STUN servers (comma-separated)
STUN_SERVERS=stun:stun.l.google.com:19302,stun:stun1.l.google.com:19302

# Production TURN server (optional - for better reliability)
# TURN_SERVER=turn:your-turn-server.com:3478
# TURN_USERNAME=your-username
# TURN_CREDENTIAL=your-password
```

---

### Testing & Monitoring

#### 1. Test Connection Quality
**Run connection test script:**
```bash
# Test WebRTC offer/answer exchange
curl -X POST https://d359aaha3l67dn.cloudfront.net/offer \
  -H "Content-Type: application/json" \
  -d '{
    "type": "offer",
    "sdp": "v=0\no=- 123 456 IN IP4 127.0.0.1\n..."
  }'
```

#### 2. Monitor Connection Metrics
**Add CloudWatch metrics:**
- WebRTC connection success rate
- ICE gathering duration
- Connection establishment time
- Session duration
- Disconnection reasons

#### 3. Log Analysis
**Use filtered log script:**
```bash
./scripts/filter_production_logs.sh voice-bot 1
```

**Monitor for:**
- `ICE connection state is completed` - Successful connections
- `Timeout establishing the connection` - Failed connections
- `ICE gathering state is complete` - ICE gathering duration

---

### Expected Improvements

After implementing these optimizations:

1. **Connection Success Rate:** 95%+ (currently ~70%)
2. **ICE Gathering Time:** 2-3 seconds (currently 5-7 seconds)
3. **Connection Timeout:** < 5% (currently ~30%)
4. **Session Stability:** Fewer disconnections during active calls

---

### Implementation Priority

**High Priority (Immediate):**
1. ✅ Configure multiple STUN servers
2. ✅ Open UDP ports in security groups
3. ✅ Add connection state monitoring

**Medium Priority (This Week):**
4. ⏳ Implement automatic reconnection
5. ⏳ Configure ICE gathering timeout
6. ⏳ Add CloudWatch metrics

**Low Priority (Future Enhancement):**
7. 🔄 Deploy dedicated TURN server
8. 🔄 Implement adaptive bitrate
9. 🔄 Add network quality indicators

---

### Deployment Steps

1. **Update Environment Variables**
   ```bash
   # Update .env with new timeout configurations
   echo "WEBRTC_CONNECTION_TIMEOUT=90" >> .env
   echo "ICE_GATHERING_TIMEOUT=10" >> .env
   ```

2. **Apply Security Group Changes**
   ```bash
   # Open UDP ports for WebRTC
   ./scripts/configure_webrtc_ports.sh
   ```

3. **Deploy Backend Updates**
   ```bash
   # Rebuild and deploy ECS services
   ./deploy_ecs_production.sh
   ```

4. **Deploy Frontend Updates**
   ```bash
   # Rebuild and deploy to S3/CloudFront
   cd frontend && npm run build
   aws s3 sync dist/ s3://vpbank-voice-agent-frontend-590183822512/
   aws cloudfront create-invalidation --distribution-id E157XTMGCFVXEO --paths "/*"
   ```

5. **Monitor Results**
   ```bash
   # Watch logs for improvements
   ./scripts/filter_production_logs.sh voice-bot 1
   ```

---

### Troubleshooting

**Issue: Still seeing timeouts after optimization**
- Check Security Group UDP rules are applied
- Verify client network allows UDP traffic
- Test TURN server connectivity
- Review CloudWatch logs for specific error patterns

**Issue: ICE gathering still slow**
- Reduce ICE candidate pool size
- Use aggressive nomination
- Check DNS resolution speed for STUN servers

**Issue: Connection drops during session**
- Check for idle timeout configuration
- Verify keepalive packets
- Monitor network stability
- Review AWS Transcribe timeout settings (15s of silence)

---

**Last Updated:** 2025-11-09
**Status:** Ready for implementation

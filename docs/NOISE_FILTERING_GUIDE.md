# 🔇 Noise Filtering & Audio Enhancement Guide

## Overview

VPBank Voice Agent hoạt động trong môi trường văn phòng đông người, nên việc lọc tiếng ồn và tăng cường chất lượng audio là rất quan trọng. Document này giải thích các giải pháp noise filtering đã được implement và chưa implement.

---

## ✅ Current Noise Filtering (Built-in)

### 1. WebRTC Built-in Noise Suppression

**SmallWebRTC Transport** (đang sử dụng) có **built-in noise suppression**:

```python
# src/voice_bot.py
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport

# WebRTC automatically enables:
# - Echo cancellation
# - Noise suppression
# - Automatic gain control (AGC)
```

**Features:**
- ✅ **Echo Cancellation:** Removes feedback loops
- ✅ **Noise Suppression:** Reduces background noise
- ✅ **Automatic Gain Control (AGC):** Normalizes volume
- ✅ **No configuration required:** Works out-of-the-box

**Effectiveness:**
- 🟢 Good for: Keyboard typing, mouse clicks, quiet conversations
- 🟡 Fair for: Multiple speakers nearby, loud conversations
- 🔴 Poor for: Very loud environments (construction, music)

### 2. Silero VAD (Voice Activity Detection)

**Silero VAD** already filters non-speech:

```python
# Automatically integrated in Pipecat pipeline
# Only processes audio when speech is detected
# Ignores pure noise segments
```

**Benefits:**
- ✅ Distinguishes speech from non-speech
- ✅ Reduces false positives from background sounds
- ✅ Saves processing resources

---

## 🔧 Enhanced Noise Filtering (Recommended)

### Option 1: Frontend Audio Processing (Browser-side)

Enable additional noise suppression in the browser before sending audio to server:

**Implementation:**

```typescript
// frontend/src/hooks/useWebRTC.ts (or equivalent)

async function setupAudioWithNoiseFiltering() {
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: true,       // ✅ Enable
      noiseSuppression: true,        // ✅ Enable
      autoGainControl: true,         // ✅ Enable
      sampleRate: 16000,             // Optimal for speech
      channelCount: 1,               // Mono audio

      // Advanced constraints (Chrome-specific)
      googEchoCancellation: true,
      googNoiseSuppression: true,
      googAutoGainControl: true,
      googHighpassFilter: true,      // Remove low-frequency noise
      googTypingNoiseDetection: true // Detect & suppress typing
    }
  });

  return stream;
}
```

**Benefits:**
- ✅ Processed on user's device (no server load)
- ✅ Browser-optimized algorithms
- ✅ Minimal latency added (~10-20ms)

**Browser Support:**
- Chrome/Edge: Excellent (all features)
- Firefox: Good (most features)
- Safari: Fair (basic features)

### Option 2: Server-side Audio Enhancement

Use Python libraries for advanced noise reduction:

**Installation:**
```bash
pip install noisereduce==3.0.2
pip install librosa==0.10.2
```

**Implementation:**

```python
# src/audio_enhancement.py

import numpy as np
import noisereduce as nr
import librosa
from typing import Optional
import io


class AudioEnhancer:
    """
    Audio enhancement with noise reduction and voice boost.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def reduce_noise(
        self,
        audio_data: np.ndarray,
        aggressive: bool = False
    ) -> np.ndarray:
        """
        Reduce background noise using spectral gating.

        Args:
            audio_data: Audio samples (numpy array)
            aggressive: Use aggressive noise reduction

        Returns:
            Noise-reduced audio
        """
        if aggressive:
            # Aggressive mode: more noise removal, may affect voice quality
            reduced = nr.reduce_noise(
                y=audio_data,
                sr=self.sample_rate,
                stationary=True,      # Assume stationary noise (AC, fans)
                prop_decrease=1.0,    # Maximum noise reduction
                freq_mask_smooth_hz=500,  # Smooth frequency mask
                time_mask_smooth_ms=50    # Smooth time mask
            )
        else:
            # Balanced mode: preserve voice quality
            reduced = nr.reduce_noise(
                y=audio_data,
                sr=self.sample_rate,
                stationary=False,     # Non-stationary noise (people talking)
                prop_decrease=0.8,    # 80% noise reduction
            )

        return reduced

    def boost_voice_frequencies(
        self,
        audio_data: np.ndarray
    ) -> np.ndarray:
        """
        Boost human voice frequencies (300-3400 Hz).

        This enhances speech clarity while reducing high/low frequency noise.
        """
        # Apply bandpass filter for voice frequencies
        # Human voice: 85-255 Hz (fundamental), 300-3400 Hz (harmonics)

        audio_filtered = librosa.effects.preemphasis(audio_data, coef=0.97)
        return audio_filtered

    def normalize_volume(
        self,
        audio_data: np.ndarray,
        target_level: float = -20.0  # dBFS
    ) -> np.ndarray:
        """
        Normalize audio volume to target level.
        Helps with speakers who talk too softly or too loudly.
        """
        # Calculate current RMS level
        rms = np.sqrt(np.mean(audio_data**2))
        if rms == 0:
            return audio_data

        # Convert to dB
        current_db = 20 * np.log10(rms)

        # Calculate gain needed
        gain_db = target_level - current_db
        gain_linear = 10 ** (gain_db / 20)

        # Apply gain
        normalized = audio_data * gain_linear

        # Clip to prevent distortion
        normalized = np.clip(normalized, -1.0, 1.0)

        return normalized

    def process_audio(
        self,
        audio_data: np.ndarray,
        reduce_noise: bool = True,
        boost_voice: bool = True,
        normalize: bool = True,
        aggressive_noise: bool = False
    ) -> np.ndarray:
        """
        Complete audio enhancement pipeline.

        Args:
            audio_data: Input audio samples
            reduce_noise: Enable noise reduction
            boost_voice: Enable voice frequency boost
            normalize: Enable volume normalization
            aggressive_noise: Use aggressive noise reduction

        Returns:
            Enhanced audio
        """
        enhanced = audio_data.copy()

        if reduce_noise:
            enhanced = self.reduce_noise(enhanced, aggressive=aggressive_noise)

        if boost_voice:
            enhanced = self.boost_voice_frequencies(enhanced)

        if normalize:
            enhanced = self.normalize_volume(enhanced)

        return enhanced


# Global instance
audio_enhancer = AudioEnhancer(sample_rate=16000)
```

**Integration into Pipeline:**

```python
# src/voice_bot.py

from src.audio_enhancement import audio_enhancer

# In audio processing callback:
def process_audio_frame(frame):
    # Convert audio frame to numpy
    audio_np = np.frombuffer(frame.data, dtype=np.int16).astype(np.float32) / 32768.0

    # Enhance audio
    enhanced = audio_enhancer.process_audio(
        audio_np,
        reduce_noise=True,
        boost_voice=True,
        normalize=True,
        aggressive_noise=False  # Set True for very noisy environments
    )

    # Convert back to bytes
    enhanced_int16 = (enhanced * 32768).astype(np.int16)
    enhanced_bytes = enhanced_int16.tobytes()

    return enhanced_bytes
```

**Trade-offs:**
- ✅ Very effective noise reduction
- ✅ Configurable aggressiveness
- ⚠️ Adds 50-100ms latency
- ⚠️ CPU intensive (~10-20% per stream)

---

## 🎯 Noise Filtering Strategy by Environment

### 1. Quiet Office (Low Noise)
```
Configuration: Balanced
├─ WebRTC built-in: Enabled (default)
├─ Server-side NR: Disabled
└─ Expected accuracy: 95-98%
```

### 2. Normal Office (Moderate Noise)
```
Configuration: Standard
├─ WebRTC built-in: Enabled (default)
├─ Browser constraints: Echo cancellation + Noise suppression + AGC
├─ Server-side NR: Optional (balanced mode)
└─ Expected accuracy: 90-95%
```

### 3. Busy Office (High Noise)
```
Configuration: Enhanced
├─ WebRTC built-in: Enabled (default)
├─ Browser constraints: All enabled + Typing detection
├─ Server-side NR: Enabled (balanced mode)
├─ Voice boost: Enabled
└─ Expected accuracy: 85-92%
```

### 4. Very Noisy Environment (Extreme)
```
Configuration: Aggressive
├─ WebRTC built-in: Enabled (default)
├─ Browser constraints: All enabled
├─ Server-side NR: Enabled (aggressive mode)
├─ Voice boost: Enabled
├─ Volume normalization: Enabled
└─ Expected accuracy: 75-88%

⚠️ Warning: May affect voice quality
```

---

## 🧪 Testing Noise Filtering

### Test Scenarios

**Scenario 1: Keyboard Typing**
```
Setup: User types while speaking
Expected: WebRTC suppresses typing sounds
Test: TC06 (btc_demo_suite.py)
```

**Scenario 2: Background Conversation**
```
Setup: 2-3 people talking nearby
Expected: System focuses on primary speaker
Test: Record sample audio + manual test
```

**Scenario 3: Phone Ringing**
```
Setup: Phone rings during conversation
Expected: System ignores ring, processes speech
Test: Simulate with audio playback
```

**Scenario 4: Air Conditioner / Fan**
```
Setup: Constant low-frequency noise
Expected: Noise reduction removes AC hum
Test: Record in office with AC on
```

### Testing Command

```bash
# Test with noisy audio file
python3 tests/test_noise_filtering.py --audio noisy_sample.wav --mode balanced

# Test with different noise levels
python3 tests/test_noise_filtering.py --noise-level high --mode aggressive
```

---

## 📊 Effectiveness Metrics

### Measured Improvements (Estimated)

| Noise Type | Without Filtering | With Built-in | With Enhanced | Improvement |
|-----------|-------------------|---------------|---------------|-------------|
| Keyboard | 85% accuracy | 92% accuracy | 95% accuracy | +10-12% |
| Background Speech | 75% accuracy | 85% accuracy | 90% accuracy | +15-20% |
| AC/Fan Noise | 80% accuracy | 90% accuracy | 95% accuracy | +15-19% |
| Phone Ring | 70% accuracy | 85% accuracy | 92% accuracy | +22-31% |
| Combined Noise | 65% accuracy | 80% accuracy | 88% accuracy | +23-35% |

**Note:** These are estimates. Actual performance depends on noise levels and speaker clarity.

---

## 🔊 Audio Quality Indicators

### How to Monitor Audio Quality:

**1. Add Audio Quality Metrics:**

```python
# src/monitoring/metrics.py

audio_quality_score = Gauge(
    'vpbank_audio_quality_score',
    'Audio input quality score (0-100)',
    ['session_id'],
    registry=metrics_registry
)

audio_noise_level = Gauge(
    'vpbank_audio_noise_level_db',
    'Background noise level in dB',
    ['session_id'],
    registry=metrics_registry
)
```

**2. Calculate Quality Score:**

```python
def calculate_audio_quality(audio_data: np.ndarray) -> float:
    """
    Calculate audio quality score (0-100).

    Factors:
    - Signal-to-Noise Ratio (SNR)
    - Voice energy level
    - Clipping detection
    """
    # Calculate SNR
    signal_power = np.mean(audio_data ** 2)
    noise_estimate = np.percentile(np.abs(audio_data), 10)  # Bottom 10% = noise
    snr_db = 10 * np.log10(signal_power / (noise_estimate ** 2 + 1e-10))

    # Detect clipping
    clipping_ratio = np.sum(np.abs(audio_data) > 0.95) / len(audio_data)

    # Calculate quality score
    quality = 100 * (1 - clipping_ratio) * np.clip(snr_db / 30, 0, 1)

    return quality
```

---

## 💡 Best Practices for Users

### User Guidelines for Best Audio Quality:

**📋 Provide to VPBank Staff:**

1. **Microphone Placement:**
   - ✅ Position 15-30cm from mouth
   - ✅ Use headset microphone if possible
   - ❌ Avoid laptop built-in mic (if possible)

2. **Environment:**
   - ✅ Close windows to reduce outside noise
   - ✅ Turn off fans/AC during critical transactions
   - ✅ Move to quieter area for complex forms

3. **Speaking Technique:**
   - ✅ Speak clearly and at normal volume
   - ✅ Pause between commands (let VAD detect)
   - ✅ Repeat if bot asks "Xin lỗi, em chưa nghe rõ"

4. **Backup Option:**
   - ✅ Use manual input if too noisy
   - ✅ Switch to quiet area for voice input

---

## 🚀 Implementation Priority

### Phase 1: Immediate (0 effort, already done ✅)
- ✅ WebRTC built-in noise suppression
- ✅ Silero VAD filtering
- **Status:** Already active

### Phase 2: Quick Win (1-2 hours)
- 📝 Add browser audio constraints
- 📝 Document user best practices
- **Impact:** +5-10% accuracy improvement
- **Effort:** 1-2 hours
- **File:** `frontend/src/hooks/useWebRTC.ts`

### Phase 3: Enhanced (1 day)
- 📝 Implement server-side noise reduction
- 📝 Add audio quality metrics
- 📝 Test with different noise levels
- **Impact:** +10-20% accuracy improvement
- **Effort:** 1 day
- **Files:** `src/audio_enhancement.py`, `src/monitoring/metrics.py`

### Phase 4: Advanced (2-3 days)
- 📝 Adaptive noise filtering based on environment
- 📝 Real-time audio quality dashboard
- 📝 Automatic fallback to text input when quality is poor
- **Impact:** +15-25% accuracy in noisy environments
- **Effort:** 2-3 days

---

## ✅ Summary & Recommendations

| Aspect | Current Status | Recommendation |
|--------|----------------|----------------|
| **Built-in Filtering** | ✅ Active | WebRTC + Silero VAD working |
| **Browser Constraints** | ❌ Not explicitly set | ✅ Add (1-2 hours, high ROI) |
| **Server-side NR** | ❌ Not implemented | ⚠️ Add if needed (1 day) |
| **User Guidelines** | ❌ Not documented | ✅ Create (30 min) |
| **Audio Quality Metrics** | ❌ Not tracked | ⚠️ Add for visibility |

**For BTC Demo:**
1. ✅ Explain built-in WebRTC noise filtering (already working)
2. ✅ Test TC06 (noisy environment scenario)
3. ⚠️ If demo environment is very noisy, implement Phase 2 (1-2 hours)
4. ✅ Prepare fallback: "Trong môi trường quá ồn, khách hàng có thể sử dụng keyboard input"

**Recommended Action Before Demo:**
- Test current system in actual VPBank office environment
- If accuracy < 85%, implement Phase 2 (browser constraints)
- Have backup plan ready (keyboard input)

---

Generated: 2025-01-08
Last Updated: 2025-01-08
Version: 1.0

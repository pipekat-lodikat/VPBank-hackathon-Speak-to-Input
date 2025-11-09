import { useEffect, useMemo, useRef, useState } from "react";
import { Plasma } from "@pipecat-ai/voice-ui-kit/webgl";
import {
  Mic,
  MicOff,
  Phone,
  PhoneOff,
  Settings,
  RefreshCw,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  Bot,
} from "lucide-react";
import Header from "../components/Header";
import VPBankWelcome from "../components/VPBankWelcome";
import { useTranscripts } from "../hooks/useTranscripts";
import { API_ENDPOINTS, WS_URL } from "../config/api";

type TranscriptMessage = {
  role: string;
  content: string;
};

interface UserInfo {
  name: string;
  role: string;
  department?: string;
}

interface ChatPageProps {
  accessToken: string;
  onSignOut: () => void;
}

class WebRTCClient {
  private pc: RTCPeerConnection | null = null;
  private localStream: MediaStream | null = null;
  private remoteAudio: HTMLAudioElement | null = null;
  public connected = false;
  public onStateChange?: (state: string) => void;
  public onLocalAudioTrack?: (track: MediaStreamTrack) => void;

  constructor() {
    this.pc = new RTCPeerConnection({
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
    });

    this.pc.onconnectionstatechange = () => {
      this.connected = this.pc?.connectionState === "connected";
      this.onStateChange?.(this.pc?.connectionState || "disconnected");
    };

    this.pc.ontrack = (event) => {
      if (event.track.kind === "audio") {
        if (!this.remoteAudio) {
          this.remoteAudio = new Audio();
          this.remoteAudio.autoplay = true;
          document.body.appendChild(this.remoteAudio);
        }

        const remoteStream = new MediaStream([event.track]);
        this.remoteAudio.srcObject = remoteStream;

        event.track.onended = () => {
          // Clean up handled in disconnect
        };
      }
    };
  }

  async startBotAndConnect(options: {
    endpoint: string;
    audioInput?: string;
    audioOutput?: string;
  }) {
    try {
      console.log("🎙️ [DEBUG] Starting WebRTC connection...");

      // Recreate peer connection if it was closed or doesn't exist
      if (!this.pc || this.pc.signalingState === 'closed') {
        console.log("🔧 [DEBUG] Creating new RTCPeerConnection");
        this.pc = new RTCPeerConnection({
          iceServers: [
            { urls: "stun:stun.l.google.com:19302" },
            { urls: "stun:stun1.l.google.com:19302" },
            { urls: "stun:stun2.l.google.com:19302" },
          ],
          iceCandidatePoolSize: 10,
        });

        this.pc.onconnectionstatechange = () => {
          const state = this.pc?.connectionState || "disconnected";
          console.log(`🔄 [DEBUG] Connection state changed: ${state}`);
          this.connected = this.pc?.connectionState === "connected";
          this.onStateChange?.(state);
        };

        this.pc.onicecandidate = (event) => {
          if (event.candidate) {
            console.log("🧊 [DEBUG] ICE candidate generated:", {
              type: event.candidate.type,
              protocol: event.candidate.protocol,
              address: event.candidate.address,
              port: event.candidate.port,
              candidate: event.candidate.candidate,
            });
          } else {
            console.log("🧊 [DEBUG] ICE gathering complete");
          }
        };

        this.pc.onicegatheringstatechange = () => {
          console.log("🧊 [DEBUG] ICE gathering state:", this.pc?.iceGatheringState);
        };

        this.pc.oniceconnectionstatechange = () => {
          const state = this.pc?.iceConnectionState;
          console.log("🧊 [DEBUG] ICE connection state:", state);
          if (state === "failed" || state === "disconnected") {
            console.error("❌ [DEBUG] ICE connection failed/disconnected");
          }
        };

        this.pc.onsignalingstatechange = () => {
          console.log("📡 [DEBUG] Signaling state:", this.pc?.signalingState);
        };

        this.pc.ontrack = (event) => {
          if (event.track.kind === "audio") {
            console.log("🔊 [DEBUG] Remote audio track received");
            if (!this.remoteAudio) {
              this.remoteAudio = new Audio();
              this.remoteAudio.autoplay = true;
              document.body.appendChild(this.remoteAudio);
            }

            const remoteStream = new MediaStream([event.track]);
            this.remoteAudio.srcObject = remoteStream;

            event.track.onended = () => {
              console.log("🔇 [DEBUG] Remote audio track ended");
            };
          }
        };
      }

      const constraints: MediaStreamConstraints = {
        audio: options.audioInput
          ? { deviceId: { exact: options.audioInput } }
          : true,
        video: false,
      };

      console.log("🎤 [DEBUG] Requesting microphone access with constraints:", constraints);
      this.localStream = await navigator.mediaDevices.getUserMedia(constraints);
      console.log("✅ [DEBUG] Microphone access granted");

      const localAudioTrack = this.localStream.getAudioTracks()[0];
      if (localAudioTrack) {
        console.log("🎙️ [DEBUG] Local audio track:", {
          id: localAudioTrack.id,
          label: localAudioTrack.label,
          enabled: localAudioTrack.enabled,
          readyState: localAudioTrack.readyState,
          muted: localAudioTrack.muted,
        });

        // Monitor audio track state changes
        localAudioTrack.onmute = () => console.log("⚠️ [DEBUG] Audio track muted");
        localAudioTrack.onunmute = () => console.log("✅ [DEBUG] Audio track unmuted");
        localAudioTrack.onended = () => console.log("❌ [DEBUG] Audio track ended");

        this.onLocalAudioTrack?.(localAudioTrack);
      } else {
        console.error("❌ [DEBUG] No audio track found in local stream!");
      }

      this.localStream.getTracks().forEach((track) => {
        console.log(`➕ [DEBUG] Adding ${track.kind} track to peer connection`);
        this.pc?.addTrack(track, this.localStream!);
      });

      const offer = await this.pc!.createOffer();
      await this.pc!.setLocalDescription(offer);

      console.log("🔗 [DEBUG] Connecting to WebRTC endpoint:", options.endpoint);
      console.log("📤 [DEBUG] Sending WebRTC offer SDP:", {
        type: offer.type,
        sdpLength: offer.sdp?.length,
        sdpPreview: offer.sdp?.substring(0, 200),
      });

      // Monitor connection state changes only
      let lastState = "";
      const monitorInterval = setInterval(() => {
        if (!this.pc || this.pc.connectionState === "closed") {
          clearInterval(monitorInterval);
          return;
        }
        const currentState = `${this.pc.connectionState}-${this.pc.iceConnectionState}`;
        if (currentState !== lastState) {
          console.log("📊 [DEBUG] Connection state changed:", {
            connectionState: this.pc.connectionState,
            iceConnectionState: this.pc.iceConnectionState,
          });
          lastState = currentState;
        }
        // Stop monitoring once connected
        if (this.pc.connectionState === "connected") {
          clearInterval(monitorInterval);
        }
      }, 1000);

      const response = await fetch(options.endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          type: offer.type,
          sdp: offer.sdp,
        }),
      });

      if (import.meta.env.DEV) {
        console.log("📥 Response status:", response.status, response.statusText);
      }

      if (!response.ok) {
        const errorText = await response.text();
        console.error("❌ Server error response:", errorText);
        throw new Error(
          `Server error: ${response.status} ${response.statusText}. ${errorText}`
        );
      }

      const answer = await response.json();

      console.log("✅ [DEBUG] Received WebRTC answer:", {
        type: answer.type,
        sdpLength: answer.sdp?.length,
        sdpPreview: answer.sdp?.substring(0, 200),
        hasIceCandidates: answer.sdp?.includes("a=candidate"),
      });

      // Check if peer connection is in correct state before setting remote description
      if (this.pc?.signalingState === "have-local-offer") {
        await this.pc.setRemoteDescription(answer);
        console.log("✅ [DEBUG] Remote description set successfully");
        console.log("📊 [DEBUG] Current peer connection state:", {
          connectionState: this.pc.connectionState,
          iceConnectionState: this.pc.iceConnectionState,
          iceGatheringState: this.pc.iceGatheringState,
          signalingState: this.pc.signalingState,
        });
      } else {
        console.error(`❌ [DEBUG] Cannot set remote description. Signaling state: ${this.pc?.signalingState}`);
        throw new Error(`Invalid signaling state: ${this.pc?.signalingState}. Expected "have-local-offer"`);
      }

      if (options.audioOutput && this.remoteAudio?.setSinkId) {
        try {
          await this.remoteAudio.setSinkId(options.audioOutput);
        } catch (err) {
          console.warn("Unable to set sink ID", err);
        }
      }
    } catch (error) {
      this.disconnect();
      throw error;
    }
  }

  async updateInputDevice(deviceId: string) {
    if (!this.localStream) return;
    try {
      const newStream = await navigator.mediaDevices.getUserMedia({
        audio: { deviceId: { exact: deviceId } },
        video: false,
      });
      const audioTrack = newStream.getAudioTracks()[0];
      const sender = this.pc
        ?.getSenders()
        .find((s) => s.track?.kind === "audio");
      if (sender && audioTrack) {
        await sender.replaceTrack(audioTrack);
        this.localStream.getAudioTracks().forEach((track) => track.stop());
        this.localStream = newStream;
        this.onLocalAudioTrack?.(audioTrack);
      }
    } catch (err) {
      console.error("Unable to update input device", err);
    }
  }

  async updateOutputDevice(deviceId: string) {
    if (this.remoteAudio?.setSinkId) {
      try {
        await this.remoteAudio.setSinkId(deviceId);
      } catch (err) {
        console.error("Unable to update output device", err);
      }
    }
  }

  toggleMute(): boolean {
    if (!this.localStream) return false;

    const audioTrack = this.localStream.getAudioTracks()[0];
    if (audioTrack) {
      audioTrack.enabled = !audioTrack.enabled;
      return !audioTrack.enabled;
    }
    return false;
  }

  disconnect() {
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = null;
    }
    if (this.remoteAudio) {
      this.remoteAudio.pause();
      this.remoteAudio.srcObject = null;
      if (this.remoteAudio.parentNode) {
        this.remoteAudio.parentNode.removeChild(this.remoteAudio);
      }
      this.remoteAudio = null;
    }
    if (this.pc) {
      this.pc.close();
      // Don't recreate peer connection here - will be created in startBotAndConnect
      this.pc = null;
    }
    this.connected = false;
    this.onStateChange?.("disconnected");
  }
}

const plasmaConfig = {
  intensity: 1.9,
  radius: 1.6,
  effectScale: 0.58,
  ringCount: 3,
  ringVisibility: 0.6,
  ringDistance: 0.07,
  ringBounce: 0.28,
  ringThickness: 14,
  ringVariance: 0.55,
  ringAmplitude: 0.045,
  ringSpeed: 1.8,
  ringSegments: 6,
  colorCycleSpeed: 0.9,
  plasmaSpeed: 1.5,
  useCustomColors: true,
  color1: "#16a34a",
  color2: "#10b981",
  color3: "#22d3ee",
  backgroundColor: "transparent",
  glowFalloff: 1.15,
  glowThreshold: 0.07,
  audioEnabled: true,
  audioSensitivity: 1.3,
  audioSmoothing: 0.82,
  frequencyBands: 32,
  bassResponse: 1.3,
  midResponse: 1.15,
  trebleResponse: 0.95,
  plasmaVolumeReactivity: 2.3,
  volumeThreshold: 0.07,
} as const;

const formatMessageLines = (
  text: string,
  preserveOriginal = false
): string[] => {
  if (!text) return [];

  if (preserveOriginal) {
    return text
      .split(/\n/)
      .map((s) => s.trim())
      .filter(Boolean);
  }

  let t = text.replace(/\r\n/g, "\n");
  t = t.replace(/([^\n])\s-\s/g, "$1\n• ");
  t = t.replace(/([^\n])\s•\s/g, "$1\n• ");
  t = t.replace(/([^\n])\s(\d+)\.\s/g, "$1\n$2. ");
  return t
    .split(/\n+/)
    .map((s) => s.trim())
    .filter(Boolean);
};

const ChatPage = ({ accessToken, onSignOut }: ChatPageProps) => {
  const clientRef = useRef<WebRTCClient>(new WebRTCClient());
  const client = clientRef.current;

  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<TranscriptMessage[]>([]);
  const [audioDevices, setAudioDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedInputDevice, setSelectedInputDevice] = useState("");
  const [selectedOutputDevice, setSelectedOutputDevice] = useState("");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [voiceGender, setVoiceGender] = useState<"male" | "female">("male");
  const [voiceRegion, setVoiceRegion] = useState<"north" | "central" | "south">(
    "north"
  );
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isLoadedFromFile, setIsLoadedFromFile] = useState(false);
  const [loadingTranscript, setLoadingTranscript] = useState(false);
  const [chatExpanded, setChatExpanded] = useState(true);
  const [showWelcome, setShowWelcome] = useState(true);
  const [micTrack, setMicTrack] = useState<MediaStreamTrack | null>(null);
  const [liveUrl, setLiveUrl] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const historyListRef = useRef<HTMLDivElement>(null);
  const settingsRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const transcriptScrollRef = useRef<HTMLDivElement>(null);

  const {
    transcripts: savedTranscripts,
    loadTranscript,
    refreshTranscripts,
  } = useTranscripts();

  useEffect(() => {
    client.onStateChange = (state) => {
      if (state === "connected") {
        setIsConnected(true);
        setIsConnecting(false);
      } else if (
        state === "disconnected" ||
        state === "failed" ||
        state === "closed"
      ) {
        setIsConnected(false);
        setIsConnecting(false);
      }
    };
    client.onLocalAudioTrack = (track) => {
      setMicTrack(track);
    };

    return () => {
      client.onStateChange = undefined;
      client.onLocalAudioTrack = undefined;
    };
  }, [client]);

  useEffect(() => {
    let cancelled = false;
    const fetchUserInfo = async () => {
      if (!accessToken) return;
      try {
        const res = await fetch(API_ENDPOINTS.AUTH.VERIFY, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: accessToken }),
        });
        const data = await res.json();
        if (!cancelled) {
          if (data.success && data.user) {
            const role = data.user.attributes?.["custom:role"] || "Staff";
            const name = data.user.attributes?.["name"] || data.user.username;
            const department = data.user.attributes?.["custom:department"];
            setUserInfo({ name, role, department });
          } else {
            onSignOut();
          }
        }
      } catch (err) {
        console.error("Unable to verify token", err);
        if (!cancelled) {
          onSignOut();
        }
      }
    };
    fetchUserInfo();

    return () => {
      cancelled = true;
    };
  }, [accessToken, onSignOut]);

  useEffect(() => {
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
    let reconnectAttempts = 0;
    let isIntentionalClose = false;
    const MAX_RECONNECT_ATTEMPTS = 10;
    const BASE_DELAY = 1000;

    const getReconnectDelay = (attempt: number): number => {
      // Exponential backoff: 1s, 2s, 4s, 8s, max 30s
      return Math.min(BASE_DELAY * Math.pow(2, attempt), 30000);
    };

    const connectWebSocket = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return;
      }

      // Check if we've exceeded max attempts
      if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.error(`WebSocket: Max reconnection attempts (${MAX_RECONNECT_ATTEMPTS}) reached`);
        return;
      }

      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        reconnectAttempts = 0; // Reset on successful connection
        if (import.meta.env.DEV) {
          console.log("WebSocket connected for transcript streaming");
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "transcript" && data.message) {
            // Debug log để kiểm tra message nhận được
            if (import.meta.env.DEV) {
              console.log("📨 Received transcript message:", {
                role: data.message.role,
                content: data.message.content?.substring(0, 50),
                fullMessage: data.message
              });
            }

            setTranscript((prev) => {
              const isDuplicate = prev.some(
                (msg) =>
                  msg.role === data.message.role &&
                  msg.content === data.message.content
              );

              if (isDuplicate) {
                if (import.meta.env.DEV) {
                  console.log("⚠️ Duplicate message detected, skipping");
                }
                return prev;
              }

              // Only create new conversation if there are NO existing messages
              // This prevents clearing transcript when reconnecting
              let targetConversationId = activeConversationId;
              if (!targetConversationId && prev.length === 0) {
                targetConversationId = createConversation();
                setActiveConversationId(targetConversationId);
              } else if (!targetConversationId && prev.length > 0) {
                // Messages exist but no conversation ID - create one without clearing
                const newSessionId = Date.now().toString();
                setActiveConversationId(newSessionId);
              }

              const newTranscript = [
                ...prev,
                data.message as TranscriptMessage,
              ];

              if (import.meta.env.DEV) {
                console.log("✅ Updated transcript, total messages:", newTranscript.length, "Roles:", newTranscript.map(m => m.role));
              }
              return newTranscript;
            });
          } else {
            if (import.meta.env.DEV) {
              console.log("📬 Received non-transcript message:", data.type);
            }
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      ws.onclose = (event) => {
        wsRef.current = null;

        // Don't reconnect if close was intentional (user logout/navigate away)
        if (isIntentionalClose) {
          if (import.meta.env.DEV) {
            console.log("WebSocket closed intentionally, not reconnecting");
          }
          return;
        }

        // Don't reconnect on normal closure (1000)
        if (event.code === 1000) {
          if (import.meta.env.DEV) {
            console.log("WebSocket closed normally, not reconnecting");
          }
          return;
        }

        // Reconnect with exponential backoff
        reconnectAttempts++;
        const delay = getReconnectDelay(reconnectAttempts - 1);

        if (import.meta.env.DEV) {
          console.log(`WebSocket closed (code: ${event.code}), reconnecting in ${delay}ms (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
        }

        reconnectTimeout = setTimeout(connectWebSocket, delay);
      };

      wsRef.current = ws;
    };

    connectWebSocket();

    return () => {
      isIntentionalClose = true;
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
    // Remove activeConversationId dependency to prevent unnecessary reconnects
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const getDevices = async () => {
      try {
        await navigator.mediaDevices.getUserMedia({ audio: true });
        const devices = await navigator.mediaDevices.enumerateDevices();
        setAudioDevices(devices);

        const defaultInput = devices.find((d) => d.kind === "audioinput");
        const defaultOutput = devices.find((d) => d.kind === "audiooutput");
        if (defaultInput) setSelectedInputDevice(defaultInput.deviceId);
        if (defaultOutput) setSelectedOutputDevice(defaultOutput.deviceId);
      } catch (err) {
        console.error("Unable to enumerate devices:", err);
      }
    };

    getDevices();

    navigator.mediaDevices.addEventListener("devicechange", getDevices);
    return () => {
      navigator.mediaDevices.removeEventListener("devicechange", getDevices);
    };
  }, []);

  // Cleanup WebRTC connection on unmount
  useEffect(() => {
    return () => {
      client.disconnect();
    };
  }, [client]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        settingsRef.current &&
        !settingsRef.current.contains(event.target as Node)
      ) {
        setSettingsOpen(false);
      }
      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(event.target as Node)
      ) {
        setUserMenuOpen(false);
      }
    };

    if (settingsOpen || userMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [settingsOpen, userMenuOpen]);

  // Poll Browser Service live URL
  useEffect(() => {
    // Skip if browser service URL is not configured (production)
    if (!API_ENDPOINTS.BROWSER.LIVE) return;
    
    let timer: ReturnType<typeof setInterval> | null = null;
    const fetchLive = async () => {
      try {
        const res = await fetch(API_ENDPOINTS.BROWSER.LIVE);
        if (!res.ok) return;
        const data = await res.json();
        if (data && typeof data.live_url === "string") {
          const url = data.live_url || null;
          setLiveUrl(url);
        }
      } catch {
        // Silently fail if browser service is not available
      }
    };
    fetchLive();
    timer = setInterval(fetchLive, 3000);
    return () => {
      if (timer) clearInterval(timer);
    };
  }, []);

  // Auto-scroll transcript to bottom when new messages arrive
  // Only auto-scroll during LIVE conversation (when connected), NOT when loading old conversations
  useEffect(() => {
    if (
      transcriptScrollRef.current &&
      transcript.length > 0 &&
      chatExpanded &&
      isConnected
    ) {
      const scrollToBottom = () => {
        if (transcriptScrollRef.current) {
          transcriptScrollRef.current.scrollTop =
            transcriptScrollRef.current.scrollHeight;
        }
      };

      // First scroll immediately
      requestAnimationFrame(() => {
        scrollToBottom();
        // Second scroll after short delay to ensure DOM is fully rendered
        setTimeout(scrollToBottom, 50);
      });
    }
  }, [transcript, chatExpanded, isConnected]);

  const inputDevices = useMemo(
    () => audioDevices.filter((device) => device.kind === "audioinput"),
    [audioDevices]
  );
  const outputDevices = useMemo(
    () => audioDevices.filter((device) => device.kind === "audiooutput"),
    [audioDevices]
  );

  const createConversation = () => {
    // Generate new session ID (will be created by backend when bot starts)
    const newSessionId = Date.now().toString();
    setActiveConversationId(newSessionId);
    setTranscript([]);
    setIsLoadedFromFile(false);

    return newSessionId;
  };

  const handleNewConversation = () => {
    if (isConnected) return;
    createConversation();
  };
  const handleStartFromWelcome = () => {
    if (!activeConversationId) {
      createConversation();
    }
    setShowWelcome(false);
  };

  const ensureConversation = () => {
    if (activeConversationId) return activeConversationId;

    // If we have existing messages, keep them and just create a new session ID
    if (transcript.length > 0) {
      const newSessionId = Date.now().toString();
      setActiveConversationId(newSessionId);
      return newSessionId;
    }

    // No messages, create fresh conversation
    return createConversation();
  };

  const handleConnect = async () => {
    if (isConnected) {
      // Disconnect - session will be saved to DynamoDB by backend
      client.disconnect();
      setIsConnected(false);
      setError(null);
      // Keep transcript - don't clear it on disconnect
      // User can continue the same conversation by reconnecting
      return;
    }

    const conversationId = ensureConversation();

    // Auto-expand chat to show real-time messages
    setChatExpanded(true);

    // Enable auto-scroll for new messages (disable loaded-from-file mode)
    setIsLoadedFromFile(false);

    try {
      setIsConnecting(true);
      setError(null);
      await client.startBotAndConnect({
        endpoint: API_ENDPOINTS.WEBRTC_OFFER,
        audioInput: selectedInputDevice || undefined,
        audioOutput: selectedOutputDevice || undefined,
      });
      setActiveConversationId(conversationId);
    } catch (err) {
      console.error("Connection error:", err);
      setError(err instanceof Error ? err.message : String(err));
      setIsConnected(false);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleToggleMute = () => {
    const muted = client.toggleMute();
    setIsMuted(muted);
  };

  const handleLoadConversation = async (convId: string) => {
    if (isConnected) return;

    // Always load from DynamoDB
    setLoadingTranscript(true);
    try {
      const data = await loadTranscript(convId);
      if (data) {
        const messages = data.messages.map((m) => ({
          role: m.role,
          content: m.content,
        }));
        setTranscript(messages);
        setActiveConversationId(convId);
        setIsLoadedFromFile(true);

        // Hide welcome screen and show chat interface
        setShowWelcome(false);

        // Auto-expand chat to show loaded messages
        setChatExpanded(true);
      }
    } catch (error) {
      console.error("Error loading transcript:", error);
    } finally {
      setLoadingTranscript(false);
    }
  };

  const handleSignOut = () => {
    client.disconnect();
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    onSignOut();
  };

  const statusLabel = isConnecting
    ? "Connecting..."
    : isConnected
    ? isMuted
      ? "Muted"
      : "Listening…"
    : "Disconnected";
  const statusColor = isConnected
    ? isMuted
      ? "#6b7280"
      : "#016d33"
    : isConnecting
    ? "#6b7280"
    : "#e20600";

  return (
    <div className="h-screen overflow-hidden bg-white flex flex-col">
      <Header />

      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -inset-[10px] opacity-20">
          <div
            className="absolute top-1/2 left-1/4 w-96 h-96 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"
            style={{ backgroundColor: "#00b74f" }}
          />
          <div
            className="absolute top-1/3 right-1/4 w-96 h-96 rounded-full mix-blend-multiply filter blur-3xl animate-pulse delay-700"
            style={{ backgroundColor: "#1d4289" }}
          />
          <div
            className="absolute bottom-1/3 left-1/2 w-96 h-96 rounded-full mix-blend-multiply filter blur-3xl animate-pulse delay-1000"
            style={{ backgroundColor: "#009440" }}
          />
        </div>
      </div>

      <div className="relative z-10 flex flex-1 overflow-hidden">
        {/* Sidebar - Fixed Position */}
        <div
          className="flex-shrink-0 history-sidebar transition-all duration-300"
          style={{
            position: "fixed",
            left: sidebarCollapsed ? "-256px" : 0,
            top: "64px",
            bottom: 0,
            width: "256px",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div className="flex items-center justify-between mb-4 px-3 pt-3">
            <h3 className="text-sm font-semibold text-gray-700">History</h3>
            <button
              onClick={handleNewConversation}
              disabled={isConnecting}
              className="text-xs px-2 py-1 rounded-lg font-medium transition-colors"
              style={{
                backgroundColor: "#016d33",
                color: "white",
                cursor: isConnecting ? "not-allowed" : "pointer",
                opacity: isConnecting ? 0.5 : 1,
              }}
            >
              + New
            </button>
          </div>

          <div
            ref={historyListRef}
            className="flex-1 overflow-y-auto px-3"
            style={{ paddingBottom: "140px" }}
          >
            {isConnecting && savedTranscripts.length === 0 && (
              <div className="p-2.5 rounded-lg bg-gradient-to-r from-green-50 to-blue-50 border border-green-100 mb-3">
                <div className="flex items-center gap-2.5">
                  <div
                    className="w-4 h-4 rounded-full border-2 border-t-transparent animate-spin"
                    style={{
                      borderColor: "#016d33",
                      borderTopColor: "transparent",
                    }}
                  />
                  <div className="flex-1">
                    <div className="text-xs font-medium text-gray-700">
                      Connecting...
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Session History from DynamoDB */}
            {savedTranscripts.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center justify-between text-xs font-bold text-gray-600 mb-2 px-1">
                  <span>Saved History</span>
                  <button
                    onClick={refreshTranscripts}
                    className="p-1 hover:bg-gray-100 rounded"
                    title="Refresh"
                  >
                    <RefreshCw className="w-3 h-3" />
                  </button>
                </div>
                <div className="space-y-1">
                  {savedTranscripts.map((item) => {
                    const dateStr = new Date(
                      item.started_at
                    ).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    });
                    const msgCount = item.message_count;
                    const isActive =
                      activeConversationId === item.id && isLoadedFromFile;
                    return (
                      <div
                        key={item.id}
                        onClick={() =>
                          !isConnected &&
                          !loadingTranscript &&
                          handleLoadConversation(item.id)
                        }
                        title={`Session ${item.id}`}
                        className={`group flex items-center gap-2 px-2.5 py-2 rounded-lg transition-all duration-150 cursor-pointer ${
                          isActive
                            ? "bg-yellow-50 border-l-2 border-yellow-400"
                            : "hover:bg-gray-50 border-l-2 border-transparent"
                        } ${loadingTranscript ? "opacity-50" : ""}`}
                        style={{
                          cursor:
                            isConnected || loadingTranscript
                              ? "not-allowed"
                              : "pointer",
                        }}
                      >
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-medium text-gray-800 truncate leading-tight">
                            Archived Session
                          </div>
                          <div
                            className="text-[10px] text-gray-500 mt-0.5 leading-tight"
                            style={{ opacity: 0.7 }}
                          >
                            {dateStr} · {msgCount} msg
                            {msgCount !== 1 ? "s" : ""}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Empty state */}
            {savedTranscripts.length === 0 && !isConnecting && (
              <div className="text-center py-8">
                <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
                  <MessageSquare
                    className="w-6 h-6 text-gray-400"
                    strokeWidth={1.25}
                  />
                </div>
                <p className="text-xs font-medium text-gray-600 mb-1">
                  No conversations yet
                </p>
                <p className="text-[10px] text-gray-400">
                  Click "+ New" to start
                </p>
              </div>
            )}
          </div>

          {/* Bottom Bar with User Info */}
          <div
            className="border-t border-gray-200 bg-gray-50/80 backdrop-blur-sm"
            style={{
              position: "absolute",
              bottom: 0,
              left: 0,
              right: 0,
              padding: "8px",
            }}
          >
            <div className="relative" ref={userMenuRef}>
              {/* User Info Card - Clickable */}
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 shadow-sm hover:bg-gray-50 transition-colors flex items-center gap-2"
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold flex-shrink-0"
                  style={{
                    background:
                      "linear-gradient(135deg, #00b74f 0%, #1d4289 100%)",
                  }}
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>
                <div className="flex-1 min-w-0 text-left">
                  <div className="text-xs font-semibold text-gray-900 truncate">
                    {userInfo?.name || "VPBank User"}
                  </div>
                  <div className="text-[10px] text-gray-500 capitalize flex items-center gap-1">
                    <span
                      className={`w-1 h-1 rounded-full ${
                        userInfo?.role === "employee"
                          ? "bg-blue-500"
                          : "bg-green-500"
                      }`}
                    />
                    {userInfo?.role === "employee"
                      ? "staff"
                      : userInfo?.role || "user"}
                  </div>
                </div>
                <svg
                  className={`w-4 h-4 text-gray-400 transition-transform ${
                    userMenuOpen ? "rotate-180" : ""
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 15l7-7 7 7"
                  />
                </svg>
              </button>

              {/* Popup Menu */}
              {userMenuOpen && (
                <div
                  className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden"
                  style={{ zIndex: 1000 }}
                >
                  <button
                    onClick={() => {
                      setUserMenuOpen(false);
                      setSettingsOpen(true);
                    }}
                    className="w-full px-4 py-2.5 flex items-center gap-3 hover:bg-gray-50 transition-colors text-left"
                  >
                    <Settings className="w-4 h-4 text-gray-600" />
                    <span className="text-sm font-medium text-gray-700">
                      Settings
                    </span>
                  </button>
                  <div className="border-t border-gray-100" />
                  <button
                    onClick={() => {
                      setUserMenuOpen(false);
                      handleSignOut();
                    }}
                    className="w-full px-4 py-2.5 flex items-center gap-3 hover:bg-red-50 transition-colors text-left group"
                  >
                    <svg
                      className="w-4 h-4 text-gray-600 group-hover:text-red-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                      />
                    </svg>
                    <span className="text-sm font-medium text-gray-700 group-hover:text-red-600">
                      Sign Out
                    </span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Settings Sidebar - Clean Design */}
        {settingsOpen && (
          <div
            ref={settingsRef}
            className="fixed top-0 left-0 bottom-0 w-72 bg-white shadow-2xl z-50 flex flex-col border-r border-gray-200"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
              <div>
                <h3 className="font-semibold text-gray-900 text-base">
                  Voice Settings
                </h3>
                <p className="text-gray-500 text-xs mt-0.5">
                  Customize your experience
                </p>
              </div>
              <button
                onClick={() => setSettingsOpen(false)}
                className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors"
              >
                <svg
                  className="w-5 h-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto px-5 py-6 space-y-8">
              {/* Voice Gender */}
              <div>
                <label className="block text-sm font-semibold text-gray-800 mb-3">
                  Voice Gender
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setVoiceGender("male")}
                    className={`rounded-xl p-4 transition-all duration-200 ${
                      voiceGender === "male"
                        ? "bg-blue-500 text-white shadow-lg"
                        : "bg-gray-50 hover:bg-gray-100 text-gray-700"
                    }`}
                  >
                    <div className="font-medium text-sm">Male</div>
                  </button>
                  <button
                    onClick={() => setVoiceGender("female")}
                    className={`rounded-xl p-4 transition-all duration-200 ${
                      voiceGender === "female"
                        ? "bg-orange-400 text-white shadow-lg"
                        : "bg-gray-50 hover:bg-gray-100 text-gray-700"
                    }`}
                  >
                    <div className="font-medium text-sm">Female</div>
                  </button>
                </div>
              </div>

              {/* Region */}
              <div>
                <label className="block text-sm font-semibold text-gray-800 mb-3">
                  Region
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    onClick={() => setVoiceRegion("north")}
                    className={`rounded-xl p-3 transition-all duration-200 ${
                      voiceRegion === "north"
                        ? "bg-emerald-500 text-white shadow-lg"
                        : "bg-gray-50 hover:bg-gray-100 text-gray-700"
                    }`}
                  >
                    <div className="font-medium text-xs">North</div>
                  </button>
                  <button
                    onClick={() => setVoiceRegion("central")}
                    className={`rounded-xl p-3 transition-all duration-200 ${
                      voiceRegion === "central"
                        ? "bg-emerald-500 text-white shadow-lg"
                        : "bg-gray-50 hover:bg-gray-100 text-gray-700"
                    }`}
                  >
                    <div className="font-medium text-xs">Central</div>
                  </button>
                  <button
                    onClick={() => setVoiceRegion("south")}
                    className={`rounded-xl p-3 transition-all duration-200 ${
                      voiceRegion === "south"
                        ? "bg-emerald-500 text-white shadow-lg"
                        : "bg-gray-50 hover:bg-gray-100 text-gray-700"
                    }`}
                  >
                    <div className="font-medium text-xs">South</div>
                  </button>
                </div>
              </div>

              {/* Microphone */}
              <div>
                <label className="block text-sm font-semibold text-gray-800 mb-3">
                  Microphone
                </label>
                <div className="relative">
                  <select
                    value={selectedInputDevice}
                    onChange={async (e) => {
                      const id = e.target.value;
                      setSelectedInputDevice(id);
                      if (isConnected) {
                        await client.updateInputDevice(id);
                      }
                    }}
                    className="w-full appearance-none bg-gray-50 border border-gray-200 hover:border-gray-300 rounded-lg px-3 py-2.5 pr-10 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all cursor-pointer"
                  >
                    {inputDevices.map((d) => (
                      <option key={d.deviceId} value={d.deviceId}>
                        {d.label || `Microphone ${d.deviceId.slice(0, 8)}`}
                      </option>
                    ))}
                  </select>
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                    <svg
                      className="w-4 h-4 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Speaker */}
              <div>
                <label className="block text-sm font-semibold text-gray-800 mb-3">
                  Speaker
                </label>
                <div className="relative">
                  <select
                    value={selectedOutputDevice}
                    onChange={async (e) => {
                      const id = e.target.value;
                      setSelectedOutputDevice(id);
                      if (isConnected) {
                        await client.updateOutputDevice(id);
                      }
                    }}
                    className="w-full appearance-none bg-gray-50 border border-gray-200 hover:border-gray-300 rounded-lg px-3 py-2.5 pr-10 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all cursor-pointer"
                  >
                    {outputDevices.map((d) => (
                      <option key={d.deviceId} value={d.deviceId}>
                        {d.label || `Speaker ${d.deviceId.slice(0, 8)}`}
                      </option>
                    ))}
                  </select>
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                    <svg
                      className="w-4 h-4 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Sidebar Toggle Button */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="fixed z-50 top-20 bg-white border border-gray-200 rounded-r-lg shadow-md hover:shadow-lg transition-all p-2"
          style={{
            left: sidebarCollapsed ? "0" : "256px",
            transition: "left 0.3s ease",
          }}
          title={sidebarCollapsed ? "Open sidebar" : "Close sidebar"}
        >
          {sidebarCollapsed ? (
            <ChevronRight className="w-4 h-4" style={{ color: "#016d33" }} />
          ) : (
            <ChevronLeft className="w-4 h-4" style={{ color: "#016d33" }} />
          )}
        </button>

        {/* Main Content Area */}
        <main
          className="flex-1 overflow-hidden pt-4 px-4 lg:px-6 transition-all duration-300"
          style={{
            marginLeft: sidebarCollapsed ? "0" : "256px",
          }}
        >
          <div className="h-full flex flex-col gap-4">
            <div className="grid grid-cols-12 gap-4 items-start flex-1 min-h-0">
              {showWelcome ? (
                <div className="col-span-12">
                  <VPBankWelcome onStartSpeaking={handleStartFromWelcome} />
                </div>
              ) : (
                <>
                  {/* Left Column: Waveform + Controls + Chat */}
                  <div className="col-span-12 lg:col-span-3 flex flex-col gap-2 h-full min-h-0 pb-4">
                    {/* Waveform Circle */}
                    <div className="w-full flex items-center justify-center">
                      <div className="relative voice-section voice-circle overflow-hidden w-full max-w-[160px] aspect-square mx-auto">
                        {micTrack ? (
                          <Plasma
                            initialConfig={plasmaConfig}
                            audioTrack={micTrack}
                            className="plasma-wrap absolute inset-0"
                          />
                        ) : (
                          <div className="absolute inset-0 flex items-center justify-center px-4 text-center text-gray-400 font-medium text-xs">
                            Start to speak
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Control Buttons */}
                    <div className="flex justify-center">
                      <div className="inline-flex items-center gap-3 control-bar rounded-2xl px-3 py-2">
                        <button
                          onClick={handleToggleMute}
                          disabled={!isConnected && !client.connected}
                          className={`w-10 h-10 grid place-items-center rounded-full border transition-colors ${
                            isMuted
                              ? "bg-rose-600 text-white border-rose-600"
                              : "bg-gray-800 text-white border-gray-800"
                          } disabled:opacity-50`}
                          title={isMuted ? "Unmute" : "Mute"}
                        >
                          {isMuted ? (
                            <MicOff className="w-4 h-4" />
                          ) : (
                            <Mic className="w-4 h-4" />
                          )}
                        </button>
                        <button
                          onClick={handleConnect}
                          disabled={isConnecting}
                          className={`w-10 h-10 grid place-items-center rounded-full text-white transition-all ${
                            isConnected ? "bg-rose-600" : "bg-emerald-600"
                          } ${
                            isConnecting ? "opacity-60 cursor-not-allowed" : ""
                          }`}
                          title={isConnected ? "End" : "Start"}
                        >
                          {isConnecting ? (
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          ) : isConnected ? (
                            <PhoneOff className="w-4 h-4" />
                          ) : (
                            <Phone className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Status */}
                    <div
                      className="text-center text-xs font-medium"
                      style={{ color: statusColor }}
                    >
                      {statusLabel}
                    </div>
                    {error && (
                      <div className="text-center text-xs text-red-600">
                        {error}
                      </div>
                    )}

                    {/* Chat Panel - Collapsible */}
                    <div
                      className={`bg-white/70 rounded-xl border border-gray-200 shadow-sm flex flex-col ${
                        chatExpanded ? "flex-1 min-h-0" : ""
                      }`}
                    >
                      {/* Chat Header */}
                      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-200 bg-white/50 backdrop-blur flex-shrink-0">
                        <div className="flex items-center gap-2">
                          <MessageSquare className="w-4 h-4 text-emerald-600" />
                          <h2 className="text-xs font-semibold text-gray-800">
                            {isLoadedFromFile ? "Saved" : "Chat"}
                          </h2>
                        </div>
                        <button
                          onClick={() => setChatExpanded((v) => !v)}
                          className="text-xs text-emerald-600 hover:underline"
                        >
                          {chatExpanded ? "▼" : "▲"}
                        </button>
                      </div>

                      {/* Chat Messages - Only show if expanded */}
                      {chatExpanded && (
                        <div
                          ref={transcriptScrollRef}
                          className="flex-1 min-h-0 overflow-y-auto p-2 space-y-2 text-xs"
                        >
                          {transcript.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center text-gray-400 text-xs">
                              <MessageSquare className="w-5 h-5 mb-1 text-emerald-400" />
                              <p className="text-center px-2">
                                No messages yet
                              </p>
                            </div>
                          ) : (
                            transcript.map((message, index) => {
                              // Debug log để kiểm tra message được render
                              if (import.meta.env.DEV && message.role !== "user") {
                                console.log("🤖 Rendering bot message:", {
                                  index,
                                  role: message.role,
                                  content: message.content?.substring(0, 50),
                                  hasContent: !!message.content
                                });
                              }

                              return message.role === "user" ? (
                                <div key={index} className="flex justify-end">
                                  <div className="max-w-[85%] bg-emerald-50 text-emerald-900 rounded-lg rounded-tr-sm px-2 py-1.5 shadow-sm whitespace-pre-wrap text-xs">
                                    {formatMessageLines(message.content).map(
                                      (line, i) => (
                                        <div
                                          key={i}
                                          className="mb-0.5 last:mb-0"
                                        >
                                          {line}
                                        </div>
                                      )
                                    )}
                                  </div>
                                </div>
                              ) : (
                                <div
                                  key={index}
                                  className="flex items-start gap-1.5"
                                  style={{ display: 'flex' }} // Đảm bảo hiển thị
                                >
                                  <div className="w-5 h-5 rounded-full grid place-items-center bg-gradient-to-br from-emerald-500 to-cyan-400 text-white shadow-sm flex-shrink-0">
                                    <Bot className="w-3 h-3" />
                                  </div>
                                  <div className="max-w-[80%] bg-white text-gray-900 rounded-lg rounded-tl-sm px-2 py-1.5 shadow-sm border border-gray-100 whitespace-pre-wrap text-xs">
                                    {message.content ? (
                                      formatMessageLines(
                                        message.content,
                                        isLoadedFromFile
                                      ).map((line, i) => (
                                        <div key={i} className="mb-0.5 last:mb-0">
                                          {line}
                                        </div>
                                      ))
                                    ) : (
                                      <div className="text-gray-400 italic">Empty message</div>
                                    )}
                                  </div>
                                </div>
                              );
                            })
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right Column: Browser View - Full Height */}
                  <div className="col-span-12 lg:col-span-9 flex flex-col h-full min-h-0 pb-4">
                    {liveUrl ? (
                      <div
                        className="flex-1 w-full rounded-xl border border-gray-200 shadow-sm overflow-hidden"
                        style={{
                          background: "#ffffff",
                        }}
                      >
                        <iframe
                          src={liveUrl}
                          className="w-full h-full border-0"
                          title="Live Browser View"
                          style={{
                            background: "#f3f4f6",
                            filter: "brightness(0.85) contrast(1.05) saturate(1.1)",
                          }}
                        />
                      </div>
                    ) : (
                      <div className="flex-1 rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 flex items-center justify-center">
                        <div className="text-center text-gray-400">
                          <svg
                            className="w-16 h-16 mx-auto mb-3 text-gray-300"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={1.5}
                              d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                            />
                          </svg>
                          <p className="text-sm font-medium">
                            Browser not active
                          </p>
                          <p className="text-xs mt-1">
                            Start a conversation to see browser view
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default ChatPage;

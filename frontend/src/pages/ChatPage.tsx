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

type TranscriptMessage = {
  role: string;
  content: string;
};

interface ConversationHistory {
  id: string;
  timestamp: Date;
  messages: TranscriptMessage[];
  semanticTitle?: string;
}

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
      const constraints: MediaStreamConstraints = {
        audio: options.audioInput
          ? { deviceId: { exact: options.audioInput } }
          : true,
        video: false,
      };

      this.localStream = await navigator.mediaDevices.getUserMedia(constraints);

      const localAudioTrack = this.localStream.getAudioTracks()[0];
      if (localAudioTrack) {
        this.onLocalAudioTrack?.(localAudioTrack);
      }

      this.localStream.getTracks().forEach((track) => {
        this.pc?.addTrack(track, this.localStream!);
      });

      const offer = await this.pc!.createOffer();
      await this.pc!.setLocalDescription(offer);

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

      if (!response.ok) {
        throw new Error(
          `Server error: ${response.status} ${response.statusText}`
        );
      }

      const answer = await response.json();

      await this.pc!.setRemoteDescription(answer);

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
        }
      };
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

const generateSemanticTitle = (messages: TranscriptMessage[]): string => {
  if (messages.length === 0) return "New Conversation";

  const firstMessages = messages
    .slice(0, 3)
    .map((m) => m.content.toLowerCase());
  const allText = firstMessages.join(" ");

  if (
    allText.includes("loan") ||
    allText.includes("vay") ||
    allText.includes("kyc")
  )
    return "Loan KYC Check";
  if (
    allText.includes("crm") ||
    allText.includes("customer") ||
    allText.includes("khách hàng")
  )
    return "Customer CRM Update";
  if (
    allText.includes("hr") ||
    allText.includes("leave") ||
    allText.includes("nghỉ phép")
  )
    return "HR Leave Request";
  if (
    allText.includes("compliance") ||
    allText.includes("audit") ||
    allText.includes("kiểm toán")
  )
    return "Compliance & Audit";
  if (
    allText.includes("transaction") ||
    allText.includes("giao dịch") ||
    allText.includes("risk")
  )
    return "Transaction Check";
  if (allText.includes("report") || allText.includes("báo cáo"))
    return "Report Generation";

  return "General Inquiry";
};

const groupConversationsByDate = (conversations: ConversationHistory[]) => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const thisWeekStart = new Date(today);
  thisWeekStart.setDate(thisWeekStart.getDate() - 7);

  const groups = {
    today: [] as ConversationHistory[],
    yesterday: [] as ConversationHistory[],
    thisWeek: [] as ConversationHistory[],
    older: [] as ConversationHistory[],
  };

  conversations.forEach((conv) => {
    const convDate = new Date(conv.timestamp);
    const convDateOnly = new Date(
      convDate.getFullYear(),
      convDate.getMonth(),
      convDate.getDate()
    );

    if (convDateOnly.getTime() === today.getTime()) {
      groups.today.push(conv);
    } else if (convDateOnly.getTime() === yesterday.getTime()) {
      groups.yesterday.push(conv);
    } else if (convDateOnly.getTime() >= thisWeekStart.getTime()) {
      groups.thisWeek.push(conv);
    } else {
      groups.older.push(conv);
    }
  });

  return groups;
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
  const [voiceGender, setVoiceGender] = useState<"male" | "female">("male");
  const [voiceRegion, setVoiceRegion] = useState<"north" | "central" | "south">(
    "north"
  );
  const [conversationHistory, setConversationHistory] = useState<
    ConversationHistory[]
  >([]);
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [newConvId, setNewConvId] = useState<string | null>(null);
  const [isLoadedFromFile, setIsLoadedFromFile] = useState(false);
  const [loadingTranscript, setLoadingTranscript] = useState(false);
  const [chatExpanded, setChatExpanded] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);
  const [micTrack, setMicTrack] = useState<MediaStreamTrack | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const historyListRef = useRef<HTMLDivElement>(null);
  const settingsRef = useRef<HTMLDivElement>(null);

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
        const res = await fetch("http://localhost:7860/api/auth/verify", {
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

    const connectWebSocket = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return;
      }

      const ws = new WebSocket("ws://localhost:7860/ws");

      ws.onopen = () => {
        console.log("WebSocket connected for transcript streaming");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "transcript" && data.message) {
            setTranscript((prev) => {
              const isDuplicate = prev.some(
                (msg) =>
                  msg.role === data.message.role &&
                  msg.content === data.message.content
              );

              if (isDuplicate) {
                return prev;
              }

              let targetConversationId = activeConversationId;
              if (!targetConversationId) {
                targetConversationId = createConversation();
                setActiveConversationId(targetConversationId);
              }

              const newTranscript = [
                ...prev,
                data.message as TranscriptMessage,
              ];

              setConversationHistory((prevHistory) =>
                prevHistory.map((conv) =>
                  conv.id === targetConversationId
                    ? {
                        ...conv,
                        messages: newTranscript,
                        timestamp: new Date(),
                      }
                    : conv
                )
              );

              return newTranscript;
            });
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      ws.onclose = () => {
        wsRef.current = null;
        reconnectTimeout = setTimeout(connectWebSocket, 1000);
      };

      wsRef.current = ws;
    };

    connectWebSocket();

    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeConversationId]);

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

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        settingsRef.current &&
        !settingsRef.current.contains(event.target as Node)
      ) {
        setSettingsOpen(false);
      }
    };

    if (settingsOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [settingsOpen]);

  const inputDevices = useMemo(
    () => audioDevices.filter((device) => device.kind === "audioinput"),
    [audioDevices]
  );
  const outputDevices = useMemo(
    () => audioDevices.filter((device) => device.kind === "audiooutput"),
    [audioDevices]
  );

  const createConversation = () => {
    const newConversation: ConversationHistory = {
      id: Date.now().toString(),
      timestamp: new Date(),
      messages: [],
    };
    setConversationHistory((prev) => [newConversation, ...prev]);
    setActiveConversationId(newConversation.id);
    setTranscript([]);
    setIsLoadedFromFile(false);
    setNewConvId(newConversation.id);

    setTimeout(() => {
      if (historyListRef.current) {
        historyListRef.current.scrollTo({ top: 0, behavior: "smooth" });
      }
    }, 100);

    setTimeout(() => setNewConvId(null), 2000);
    return newConversation.id;
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
    return createConversation();
  };

  const handleConnect = async () => {
    if (isConnected) {
      if (activeConversationId && transcript.length > 0) {
        setConversationHistory((prev) =>
          prev.map((conv) =>
            conv.id === activeConversationId
              ? { ...conv, messages: transcript }
              : conv
          )
        );
      }
      client.disconnect();
      setIsConnected(false);
      setError(null);
      setTranscript([]);
      return;
    }

    const conversationId = ensureConversation();

    try {
      setIsConnecting(true);
      setError(null);
      await client.startBotAndConnect({
        endpoint: "http://localhost:7860/offer",
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

  const handleLoadConversation = async (convId: string, fromFile = false) => {
    if (isConnected) return;

    if (fromFile) {
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
        }
      } catch (error) {
        console.error("Error loading transcript:", error);
      } finally {
        setLoadingTranscript(false);
      }
    } else {
      const conv = conversationHistory.find((c) => c.id === convId);
      if (conv) {
        setTranscript(conv.messages);
        setActiveConversationId(conv.id);
        setIsLoadedFromFile(false);
      }
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
            {isConnecting && conversationHistory.length === 0 && (
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

            {conversationHistory.length > 0 &&
              (() => {
                const grouped = groupConversationsByDate(conversationHistory);

                const renderGroup = (
                  title: string,
                  conversations: ConversationHistory[]
                ) => {
                  if (conversations.length === 0) return null;

                  return (
                    <div key={title} className="mb-4">
                      <div className="text-xs font-bold text-gray-600 mb-2 px-1">
                        {title}
                      </div>
                      <div className="space-y-1">
                        {conversations.map((conv) => {
                          const semanticTitle =
                            conv.semanticTitle ||
                            generateSemanticTitle(conv.messages);
                          const dateStr = conv.timestamp.toLocaleDateString(
                            "en-US",
                            { month: "short", day: "numeric" }
                          );
                          const msgCount = conv.messages.length;
                          const isActive =
                            activeConversationId === conv.id &&
                            !isLoadedFromFile;

                          return (
                            <div
                              key={conv.id}
                              onClick={() =>
                                !isConnected && handleLoadConversation(conv.id)
                              }
                              title={`Session ${conv.id}`}
                              className={`group flex items-center gap-2 px-2.5 py-2 rounded-lg transition-all duration-150 cursor-pointer ${
                                isActive
                                  ? "bg-yellow-50 border-l-2 border-yellow-400"
                                  : "hover:bg-gray-50 border-l-2 border-transparent"
                              } ${
                                newConvId === conv.id ? "animate-pulse" : ""
                              }`}
                              style={{
                                cursor: isConnected ? "not-allowed" : "pointer",
                                opacity: isConnected && !isActive ? 0.5 : 1,
                              }}
                            >
                              <div className="flex-1 min-w-0">
                                <div className="text-xs font-medium text-gray-800 truncate leading-tight">
                                  {semanticTitle}
                                </div>
                                <div
                                  className="text-[10px] text-gray-500 mt-0.5 leading-tight"
                                  style={{ opacity: 0.7 }}
                                >
                                  {dateStr} · {msgCount} msg
                                  {msgCount !== 1 ? "s" : ""}
                                </div>
                              </div>
                              {newConvId === conv.id && (
                                <span
                                  className="text-[9px] px-1.5 py-0.5 rounded-full font-semibold"
                                  style={{
                                    backgroundColor: "#1d4289",
                                    color: "white",
                                  }}
                                >
                                  New
                                </span>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                };

                return (
                  <>
                    {renderGroup("Today", grouped.today)}
                    {renderGroup("Yesterday", grouped.yesterday)}
                    {renderGroup("This Week", grouped.thisWeek)}
                    {renderGroup("Older", grouped.older)}
                  </>
                );
              })()}

            {/* Saved Transcripts from backend */}
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
                          handleLoadConversation(item.id, true)
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
            {conversationHistory.length === 0 &&
              savedTranscripts.length === 0 &&
              !isConnecting && (
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
              padding: "12px",
            }}
          >
            <div className="px-3 py-3 rounded-xl bg-white border border-gray-200 shadow-sm">
              {/* User Info */}
              <div className="flex items-center gap-3 mb-3">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0"
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
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-gray-900 truncate">
                    {userInfo?.name || "VPBank User"}
                  </div>
                  <div className="text-xs text-gray-500 capitalize flex items-center gap-1 mt-0.5">
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
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
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 pt-2 border-t border-gray-100">
                <button
                  onClick={() => setSettingsOpen(!settingsOpen)}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors text-xs font-medium text-gray-700"
                >
                  <Settings className="w-4 h-4" />
                  <span>Settings</span>
                </button>
                <button
                  onClick={handleSignOut}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-gray-50 hover:bg-red-50 transition-colors text-xs font-medium text-gray-700 hover:text-red-600"
                >
                  <svg
                    className="w-4 h-4"
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
                  <span>Sign Out</span>
                </button>
              </div>
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
          className="flex-1 overflow-hidden pt-6 px-4 lg:px-8 transition-all duration-300"
          style={{
            marginLeft: sidebarCollapsed ? "0" : "256px",
          }}
        >
          <div className="h-full flex flex-col gap-6">
            <div className="grid grid-cols-12 gap-6">
              {showWelcome ? (
                <div className="col-span-12">
                  <VPBankWelcome onStartSpeaking={handleStartFromWelcome} />
                </div>
              ) : (
                <>
                  <div
                    className={`col-span-12 ${
                      chatExpanded ? "lg:col-span-5" : "lg:col-span-7"
                    } flex flex-col`}
                  >
                    <div className="w-full flex items-center justify-center">
                      <div className="relative voice-section voice-circle overflow-hidden w-full max-w-[180px] sm:max-w-[220px] lg:max-w-[260px] aspect-square mx-auto">
                        {micTrack ? (
                          <Plasma
                            initialConfig={plasmaConfig}
                            audioTrack={micTrack}
                            className="plasma-wrap absolute inset-0"
                          />
                        ) : (
                          <div className="absolute inset-0 flex items-center justify-center px-4 text-center text-gray-400 font-medium">
                            Start to speak
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="mt-4 flex justify-center">
                      <div className="inline-flex items-center gap-4 control-bar rounded-2xl px-3 py-3">
                        <button
                          onClick={handleToggleMute}
                          disabled={!isConnected && !client.connected}
                          className={`w-11 h-11 grid place-items-center rounded-full border transition-colors ${
                            isMuted
                              ? "bg-rose-600 text-white border-rose-600"
                              : "bg-gray-800 text-white border-gray-800"
                          } disabled:opacity-50`}
                          title={isMuted ? "Unmute" : "Mute"}
                        >
                          {isMuted ? (
                            <MicOff className="w-5 h-5" />
                          ) : (
                            <Mic className="w-5 h-5" />
                          )}
                        </button>
                        <button
                          onClick={handleConnect}
                          disabled={isConnecting}
                          className={`w-11 h-11 grid place-items-center rounded-full text-white transition-all ${
                            isConnected ? "bg-rose-600" : "bg-emerald-600"
                          } ${
                            isConnecting ? "opacity-60 cursor-not-allowed" : ""
                          }`}
                          title={isConnected ? "End" : "Start"}
                        >
                          {isConnecting ? (
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          ) : isConnected ? (
                            <PhoneOff className="w-5 h-5" />
                          ) : (
                            <Phone className="w-5 h-5" />
                          )}
                        </button>
                      </div>
                    </div>
                    <div className="mt-2 text-center text-sm text-gray-700">
                      {statusLabel}
                    </div>
                    {error && (
                      <div className="mt-2 text-center text-sm text-red-600">
                        {error}
                      </div>
                    )}
                  </div>

                  <div
                    className={`col-span-12 ${
                      chatExpanded ? "lg:col-span-7" : "lg:col-span-5"
                    } flex flex-col min-h-[510px] lg:min-h-[590px] chat-section rounded-2xl p-4`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="w-4 h-4 text-emerald-600" />
                        <h2 className="text-sm font-semibold text-gray-800">
                          {isLoadedFromFile ? "Saved Transcript" : "Assistant"}
                        </h2>
                      </div>
                      <button
                        onClick={() => setChatExpanded((v) => !v)}
                        className="text-xs text-emerald-600 hover:underline"
                      >
                        {chatExpanded ? "Collapse" : "Expand"}
                      </button>
                    </div>

                    <div className="flex-1 overflow-hidden mt-3 bg-white/70 rounded-xl border border-gray-200">
                      <div className="h-full overflow-y-auto p-4 space-y-4 text-[15px]">
                        {transcript.length === 0 ? (
                          <div className="h-full flex flex-col items-center justify-center text-gray-400 text-sm">
                            <MessageSquare className="w-6 h-6 mb-2 text-emerald-400" />
                            <p>
                              No messages yet. Start speaking to see the
                              transcript.
                            </p>
                          </div>
                        ) : (
                          transcript.map((message, index) =>
                            message.role === "user" ? (
                              <div key={index} className="flex justify-end">
                                <div className="max-w-[70%] bg-emerald-50 text-emerald-900 rounded-2xl rounded-tr-sm px-4 py-2 shadow-sm whitespace-pre-wrap">
                                  {formatMessageLines(message.content).map(
                                    (line, i) => (
                                      <div key={i} className="mb-1 last:mb-0">
                                        {line}
                                      </div>
                                    )
                                  )}
                                </div>
                              </div>
                            ) : (
                              <div
                                key={index}
                                className="flex items-start gap-3"
                              >
                                <div className="w-8 h-8 rounded-full grid place-items-center bg-gradient-to-br from-emerald-500 to-cyan-400 text-white shadow-sm flex-shrink-0">
                                  <Bot className="w-4 h-4" />
                                </div>
                                <div className="max-w-[80%] bg-white text-gray-900 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm border border-gray-100 whitespace-pre-wrap">
                                  {formatMessageLines(
                                    message.content,
                                    isLoadedFromFile
                                  ).map((line, i) => (
                                    <div key={i} className="mb-1 last:mb-0">
                                      {line}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )
                          )
                        )}
                      </div>
                    </div>
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

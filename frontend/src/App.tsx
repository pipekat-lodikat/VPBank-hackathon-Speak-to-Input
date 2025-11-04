import { useState, useEffect, useRef } from 'react';
import { Plasma } from "@pipecat-ai/voice-ui-kit/webgl";
import Logo from "../Logo.svg";
import { Mic, MicOff, Phone, PhoneOff, Settings, Headphones } from 'lucide-react';
import { Sparkles } from 'lucide-react';

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
      console.log("Connection state:", this.pc?.connectionState);
      this.connected = this.pc?.connectionState === "connected";
      this.onStateChange?.(this.pc?.connectionState || 'disconnected');
    };

    this.pc.oniceconnectionstatechange = () => {
      console.log("Trạng thái kết nối ICE:", this.pc?.iceConnectionState);
    };

    this.pc.ontrack = (event) => {
      console.log("Nhận được track:", event.track.kind);
      if (event.track.kind === "audio") {
        if (!this.remoteAudio) {
          this.remoteAudio = new Audio();
          this.remoteAudio.autoplay = true;
          document.body.appendChild(this.remoteAudio);
        }
        
        const remoteStream = new MediaStream([event.track]);
        this.remoteAudio.srcObject = remoteStream;

        console.log("Âm thanh đã kết nối và đang phát");

        event.track.onended = () => {
          console.log("Track âm thanh đã kết thúc");
        };
        
        event.track.onmute = () => {
          console.log("Track âm thanh đã bị tắt tiếng");
        };
        
        event.track.onunmute = () => {
          console.log("Track âm thanh đã được bật tiếng");
        };
      }
    };
  }

  async startBotAndConnect(options: { endpoint: string; audioInput?: string; audioOutput?: string }) {
    try {
      console.log("🎤 Getting user media...");
      const constraints: MediaStreamConstraints = {
        audio: options.audioInput ? { deviceId: { exact: options.audioInput } } : true,
        video: false,
      };
      
      this.localStream = await navigator.mediaDevices.getUserMedia(constraints);

      const localAudioTrack = this.localStream.getAudioTracks()[0];
      if (localAudioTrack) {
        this.onLocalAudioTrack?.(localAudioTrack);
      }

      const transceiver = this.pc?.addTransceiver("audio", {
        direction: "sendrecv"
      });
      console.log("Đã thêm bộ chuyển âm thanh với hướng:", transceiver?.direction);

      this.localStream.getTracks().forEach((track) => {
        console.log("Thêm track âm thanh local:", track.kind);
        this.pc?.addTrack(track, this.localStream!);
      });

      console.log("Đang tạo offer...");
      const offer = await this.pc!.createOffer();
      await this.pc!.setLocalDescription(offer);

      console.log("Sending offer to server...");
      console.log("Offer SDP preview:", offer.sdp?.substring(0, 200));
      
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
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }

      const answer = await response.json();
      console.log("Đã nhận phản hồi từ máy chủ:", answer);
      console.log("Answer SDP preview:", answer.sdp?.substring(0, 200));

      await this.pc!.setRemoteDescription(answer);
      console.log("Kết nối WebRTC thành công");

      this.pc?.getTransceivers().forEach((t, i) => {
        console.log(`Transceiver ${i}: direction=${t.direction}, currentDirection=${t.currentDirection}`);
      });

      if (options.audioOutput && this.remoteAudio) {
        try {
          if (this.remoteAudio.setSinkId) {
            await this.remoteAudio.setSinkId(options.audioOutput);
            console.log("Đã thiết lập thiết bị đầu ra âm thanh");
          }
        } catch (err) {
          console.warn("Không thể thiết lập thiết bị đầu ra âm thanh:", err);
        }
      }

    } catch (error) {
      console.error("Kết nối không thành công:", error);
      throw error;
    }
  }

  async updateInputDevice(deviceId: string) {
    if (!this.localStream) return;
    
    try {
      const newStream = await navigator.mediaDevices.getUserMedia({
        audio: { deviceId: { exact: deviceId } },
        video: false
      });
      
      const audioTrack = newStream.getAudioTracks()[0];
      const sender = this.pc?.getSenders().find(s => s.track?.kind === 'audio');
      if (sender) {
        await sender.replaceTrack(audioTrack);
        this.localStream.getAudioTracks().forEach(track => track.stop());
        this.localStream = newStream;
        console.log("Thiết bị đầu vào đã được cập nhật");
      }
    } catch (err) {
      console.error("Không thể cập nhật thiết bị đầu vào  :", err);
    }
  }

  async updateOutputDevice(deviceId: string) {
    if (!this.remoteAudio) return;
    
    try {
      if (this.remoteAudio.setSinkId) {
        await this.remoteAudio.setSinkId(deviceId);
        console.log("Đã thiết lập thiết bị đầu ra âm thanh");
      }
    } catch (err) {
      console.error("Không thể cập nhật thiết bị đầu ra âm thanh:", err);
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

  get state(): string {
    if (this.pc?.connectionState === 'connected') return 'ready';
    if (this.pc?.connectionState === 'connecting') return 'connecting';
    return 'disconnected';
  }

  disconnect() {
    if (this.localStream) {
      this.localStream.getTracks().forEach(track => track.stop());
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
      this.pc = null;
    }
    this.connected = false;
  }
}

const client = new WebRTCClient();

function MainApp() {
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<Array<{role: string, content: string}>>([]);
  const [audioDevices, setAudioDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedInputDevice, setSelectedInputDevice] = useState<string>('');
  const [selectedOutputDevice, setSelectedOutputDevice] = useState<string>('');
  const wsRef = useRef<WebSocket | null>(null);
  const [micTrack, setMicTrack] = useState<MediaStreamTrack | null>(null);
  const [chatExpanded, setChatExpanded] = useState(false);
  const [devicesOpen, setDevicesOpen] = useState(false);
  const [voiceGender, setVoiceGender] = useState<'male' | 'female'>('male');
  const [voiceRegion, setVoiceRegion] = useState<'north' | 'central' | 'south'>('north');

  const formatMessageLines = (text: string): string[] => {
    if (!text) return [];
    let t = text.replace(/\r\n/g, "\n");
    // Insert newline before inline bullets or numbered items
    t = t.replace(/([^\n])\s-\s/g, "$1\n• ");
    t = t.replace(/([^\n])\s•\s/g, "$1\n• ");
    t = t.replace(/([^\n])\s(\d+)\.\s/g, "$1\n$2. ");
    return t.split(/\n+/).map(s => s.trim()).filter(Boolean);
  };

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
    color1: '#16a34a',
    color2: '#10b981',
    color3: '#22d3ee',
    backgroundColor: 'transparent',
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


  useEffect(() => {
    client.onStateChange = (state) => {
      console.log("Client state changed:", state);
      if (state === 'connected') {
        setIsConnected(true);
        setIsConnecting(false);
      } else if (state === 'disconnected' || state === 'failed') {
        setIsConnected(false);
        setIsConnecting(false);
      }
    };
    client.onLocalAudioTrack = (track) => {
      setMicTrack(track);
    };
  }, []);


  useEffect(() => {
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
    
    const connectWebSocket = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return; 
      }
      
      const ws = new WebSocket('ws://localhost:7860/ws');
      
      ws.onopen = () => {
        console.log('WebSocket kết nối thành công để nhận transcript streaming');
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Messege Websocket:', data);
          if (data.type === 'transcript' && data.message) {
            setTranscript(prev => {
              console.log('Xử lý messege cho transcript:', data.message);
              
              const isDuplicate = prev.some(msg => 
                msg.role === data.message.role && 
                msg.content === data.message.content
              );
              
              if (isDuplicate) {
                console.log('Tin nhắn trùng lặp, bỏ qua:', data.message.content.substring(0, 50));
                return prev;
              }
                console.log('Thêm messenge vào transcript:', data.message.content.substring(0, 50));
              return [...prev, data.message];
            });
          }
        } catch (error) {
          console.error('Lỗi parsing message WebSocket:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('Lỗi WebSocket:', error);
      };
      
      ws.onclose = () => {
        console.log('WebSocket đã đóng');
        wsRef.current = null;
        reconnectTimeout = setTimeout(connectWebSocket, 1000);
      };
      
      wsRef.current = ws;
    };

    console.log('Bắt đầu kết nối WebSocket khi component được mount');
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
  }, []); 

  useEffect(() => {
    const getDevices = async () => {
      try {
  
        await navigator.mediaDevices.getUserMedia({ audio: true });
        const devices = await navigator.mediaDevices.enumerateDevices();
        setAudioDevices(devices);

        const defaultInput = devices.find(d => d.kind === 'audioinput');
        const defaultOutput = devices.find(d => d.kind === 'audiooutput');
        if (defaultInput) setSelectedInputDevice(defaultInput.deviceId);
        if (defaultOutput) setSelectedOutputDevice(defaultOutput.deviceId);
      } catch (error) {
        console.error('Lỗi lấy thiết bị âm thanh:', error);
      }
    };

    getDevices();

    navigator.mediaDevices.addEventListener('devicechange', getDevices);
    return () => {
      navigator.mediaDevices.removeEventListener('devicechange', getDevices);
    };
  }, []);

  const inputDevices = audioDevices.filter(device => device.kind === 'audioinput');
  const outputDevices = audioDevices.filter(device => device.kind === 'audiooutput');


  const handleConnect = async () => {
    if (isConnected) {
      client.disconnect();
      setIsConnected(false);
      setError(null);
      setTranscript([]); 
    } else {
      try {
        setIsConnecting(true);
        setError(null);
        
        console.log("🔄 Starting WebRTC connection...");
        
        await client.startBotAndConnect({
          endpoint: "http://localhost:7860/offer",
          audioInput: selectedInputDevice || undefined,
          audioOutput: selectedOutputDevice || undefined
        });
        
        setIsConnected(true);
        console.log("Kết nối thành công");
      } catch (err) {
        console.error("Lỗi kết nối:", err);
        setError(err instanceof Error ? err.message : String(err));
        setIsConnected(false);
      } finally {
        setIsConnecting(false);
      }
    }
  };

  const handleDisconnect = () => {
    client.disconnect();
    setIsConnected(false);
    setError(null);
    setTranscript([]);
  };

  const handleToggleMute = () => {
    const muted = client.toggleMute();
    setIsMuted(muted);
  };


  // Removed old dropdown outside click handler

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-green-50 to-white">
      {/* Animated background */}
          <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -inset-[10px] opacity-30">
          <div className="absolute top-1/2 left-1/4 w-96 h-96 bg-green-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
          <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-emerald-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse delay-700"></div>
          <div className="absolute bottom-1/3 left-1/2 w-96 h-96 bg-teal-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse delay-1000"></div>
        </div>
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-4">
        {/* Main Container */}
        <div className="w-full max-w-6xl mx-auto">
          {/* Header centered */}
          <div className="mb-4 flex flex-col items-center gap-2">
            <img src={Logo} alt="Logo" className="h-8 md:h-9 opacity-95 select-none" />
            <h1 className="text-base md:text-lg font-semibold text-emerald-800">VPBank Hackathon Voice Agent</h1>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-12 gap-6 items-start">

            {/* Left - Waveform/Plasma zone (60%) */}
            <div className={`col-span-12 ${chatExpanded ? 'hidden lg:block lg:col-span-0' : 'lg:col-span-7'}`}> 
              <div className="w-full h-[520px] flex items-center justify-center">
                <div className="relative voice-section voice-circle overflow-hidden w-[520px] h-[520px] max-w-full">
                  {micTrack ? (
                    <Plasma
                      initialConfig={plasmaConfig}
                      audioTrack={micTrack}
                      className="plasma-wrap absolute inset-0"
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center text-gray-300">
                      No Audio / Waiting for microphone...
                    </div>
                  )}
                </div>
              </div>
              <div className="mt-2 text-center text-sm text-gray-700">
                {isConnected ? (isMuted ? 'Muted' : 'Listening…') : 'Stopped'}
              </div>
              {/* Controls under waveform centered under visualize */}
              <div className="mt-4 flex justify-center">
                <div className="inline-flex items-center gap-4 control-bar rounded-2xl px-3 py-3">
                  {/* Meet-like round controls */}
                  <button
                    onClick={handleToggleMute}
                    className={`w-11 h-11 grid place-items-center rounded-full border ${isMuted ? 'bg-rose-600 text-white border-rose-600' : 'bg-gray-800 text-white border-gray-800'} shadow-sm`}
                    title={isMuted ? 'Unmute' : 'Mute'}
                  >
                    {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                  </button>
                  <button
                    onClick={isConnected ? handleDisconnect : handleConnect}
                    disabled={isConnecting}
                    className={`w-11 h-11 grid place-items-center rounded-full shadow-sm ${isConnected ? 'bg-rose-600 text-white' : 'bg-emerald-600 text-white'} ${isConnecting ? 'opacity-60 cursor-not-allowed' : ''}`}
                    title={isConnected ? 'End' : 'Start'}
                  >
                    {isConnected ? <PhoneOff className="w-5 h-5" /> : <Phone className="w-5 h-5" />}
                  </button>
                  <div className="relative">
                    <button
                      onClick={() => setDevicesOpen(v => !v)}
                      className="w-11 h-11 grid place-items-center rounded-full bg-gray-800 text-white shadow-sm"
                      title="Setting"
                    >
                      <Settings className="w-5 h-5" />
                    </button>
                    {devicesOpen && (
                      <div className="absolute left-0 top-full mt-2 z-50 w-[520px] max-w-[80vw] bg-white/90 border border-gray-200 rounded-xl shadow-md p-3 backdrop-blur">
                        <div className="space-y-2">
                          <p className="text-xs text-gray-500 mb-1">Customize the user's input audio settings.</p>
                          {/* Gender */}
                          <div className="flex items-center gap-3">
                            <span className="text-gray-600 text-sm min-w-[92px]">Voice Gender</span>
                            <div className="inline-flex rounded-xl border border-gray-200 p-1 bg-white">
                              <button
                                onClick={() => setVoiceGender('male')}
                                className={`px-3 h-8 rounded-lg text-sm ${voiceGender==='male' ? 'bg-emerald-500 text-white' : 'text-gray-700'}`}
                              >Male</button>
                              <button
                                onClick={() => setVoiceGender('female')}
                                className={`px-3 h-8 rounded-lg text-sm ${voiceGender==='female' ? 'bg-emerald-500 text-white' : 'text-gray-700'}`}
                              >Female</button>
                            </div>
                          </div>
                          {/* Region */}
                          <div className="flex items-center gap-3">
                            <span className="text-gray-600 text-sm min-w-[92px]">Voice Region</span>
                            <div className="inline-flex rounded-xl border border-gray-200 p-1 bg-white">
                              <button
                                onClick={() => setVoiceRegion('north')}
                                className={`px-3 h-8 rounded-lg text-sm ${voiceRegion==='north' ? 'bg-emerald-500 text-white' : 'text-gray-700'}`}
                              >North</button>
                              <button
                                onClick={() => setVoiceRegion('central')}
                                className={`px-3 h-8 rounded-lg text-sm ${voiceRegion==='central' ? 'bg-emerald-500 text-white' : 'text-gray-700'}`}
                              >Central</button>
                              <button
                                onClick={() => setVoiceRegion('south')}
                                className={`px-3 h-8 rounded-lg text-sm ${voiceRegion==='south' ? 'bg-emerald-500 text-white' : 'text-gray-700'}`}
                              >South</button>
                            </div>
                          </div>
                          <div className="flex items-center gap-2 min-w-0">
                            <label className="text-gray-600 min-w-[24px] inline-flex items-center justify-center" title="Input">
                              <Mic className="w-4 h-4" aria-hidden="true" />
                            </label>
                            <select
                              value={selectedInputDevice}
                              onChange={async (e) => {
                                const id = e.target.value; setSelectedInputDevice(id);
                                if (isConnected) { await client.updateInputDevice(id); }
                              }}
                              className="w-full appearance-none outline-none bg-transparent border border-gray-300 rounded-lg h-9 px-2 text-gray-800 text-sm truncate"
                            >
                              {inputDevices.map((d) => (
                                <option key={d.deviceId} value={d.deviceId}>{d.label || `Mic ${d.deviceId.slice(0,8)}`}</option>
                              ))}
                            </select>
                          </div>
                          <div className="flex items-center gap-2 min-w-0">
                            <label className="text-gray-600 min-w-[24px] inline-flex items-center justify-center" title="Output">
                              <Headphones className="w-4 h-4" aria-hidden="true" />
                            </label>
                            <select
                              value={selectedOutputDevice}
                              onChange={async (e) => {
                                const id = e.target.value; setSelectedOutputDevice(id);
                                if (isConnected) { await client.updateOutputDevice(id); }
                              }}
                              className="w-full appearance-none outline-none bg-transparent border border-gray-300 rounded-lg h-9 px-2 text-gray-800 text-sm truncate"
                            >
                              {outputDevices.map((d) => (
                                <option key={d.deviceId} value={d.deviceId}>{d.label || `Spk ${d.deviceId.slice(0,8)}`}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              {error && (
                <div className="mt-2 text-center text-sm text-red-600">{error}</div>
              )}
            </div>

            {/* Right - Conversation zone (40%) with Expand */}
            <div className={`col-span-12 ${chatExpanded ? 'lg:col-span-12' : 'lg:col-span-5'} h-[520px] flex flex-col chat-section rounded-2xl p-4`}>
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-gray-800">Assistant</h2>
                <button onClick={() => setChatExpanded(v => !v)} className="text-xs text-emerald-600 hover:underline">{chatExpanded ? 'Collapse' : 'Expand'}</button>
              </div>

              <div className="flex-1 overflow-hidden mt-2">
                {/* Conversation bubbles */}
                <div className="h-full overflow-y-auto p-4 space-y-4 text-[15px]">
                  {transcript.map((message, index) => (
                    message.role === 'user' ? (
                      <div key={index} className="flex justify-end">
                        <div className="max-w-[70%] bg-emerald-50 text-emerald-900 rounded-2xl rounded-tr-sm px-4 py-2 shadow-sm whitespace-pre-wrap">
                          {formatMessageLines(message.content).map((line, i) => (
                            <div key={i} className="mb-1 last:mb-0">{line}</div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div key={index} className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full grid place-items-center bg-gradient-to-br from-emerald-500 to-cyan-400 text-white shadow-sm flex-shrink-0">
                          <Sparkles className="w-4 h-4" />
                        </div>
                        <div className="max-w-[80%] bg-white text-gray-900 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm border border-gray-100 whitespace-pre-wrap">
                          {formatMessageLines(message.content).map((line, i) => (
                            <div key={i} className="mb-1 last:mb-0">{line}</div>
                          ))}
                        </div>
                      </div>
                    )
                  ))}
                </div>
              </div>

              {/* Status Bar removed for clean look */}
            </div>
          </div>

          {/* bottom controls moved under waveform */}

          {/* Footer removed */}
        </div>
      </div>
    </div>
  );
}

export default MainApp;
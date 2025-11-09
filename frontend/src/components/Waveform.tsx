import React, { useCallback, useEffect, useRef, useState } from 'react';
import './Waveform.css';

interface WaveformProps {
    audioTrack?: MediaStreamTrack | null;
    isActive?: boolean;
    className?: string;
    variant?: 'default' | 'bottom';
}

const Waveform: React.FC<WaveformProps> = ({ audioTrack, isActive = false, className = '', variant = 'default' }) => {
    const [levels, setLevels] = useState(Array(variant === 'bottom' ? 100 : 60).fill(0));
    const rafRef = useRef<number>(0);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const dataArrayRef = useRef<Uint8Array<ArrayBuffer> | null>(null);
    const [audioContext, setAudioContext] = useState<AudioContext | null>(null);

    const startRealTimeAnimation = useCallback(() => {
        let frameCount = 0;
        let lastLog = Date.now();

        const tick = () => {
            if (analyserRef.current && dataArrayRef.current) {
                analyserRef.current.getByteTimeDomainData(dataArrayRef.current);

                // Convert waveform to RMS amplitude 0..1
                let rms = 0;
                for (let i = 0; i < dataArrayRef.current.length; i++) {
                    const v = (dataArrayRef.current[i] - 128) / 128; // -1..1
                    rms += v * v;
                }
                rms = Math.sqrt(rms / dataArrayRef.current.length);
                const amp = Math.min(1, rms * 4); // scale up

                // Log audio levels every 2 seconds
                frameCount++;
                if (Date.now() - lastLog > 2000) {
                    console.log(`📊 [DEBUG] Audio level: ${(amp * 100).toFixed(1)}% (frames: ${frameCount})`);
                    lastLog = Date.now();
                    frameCount = 0;
                }

                setLevels((prev) => {
                    const next = prev.slice(1);
                    next.push(amp);
                    return next;
                });
            }

            rafRef.current = requestAnimationFrame(tick);
        };

        rafRef.current = requestAnimationFrame(tick);
    }, []);

    const startFallbackAnimation = useCallback(() => {
        const tick = () => {
            // Fallback animation (if no mic permission)
            setLevels((prev) => {
                const next = prev.slice(1);
                const t = Date.now() / 350;
                next.push((Math.sin(t) * Math.sin(t * 1.7) * 0.5 + 0.5) * 0.6);
                return next;
            });

            rafRef.current = requestAnimationFrame(tick);
        };

        rafRef.current = requestAnimationFrame(tick);
    }, []);

    const cleanup = useCallback(() => {
        if (rafRef.current) {
            cancelAnimationFrame(rafRef.current);
        }
        if (analyserRef.current) {
            analyserRef.current.disconnect();
        }
        if (audioContext && audioContext.state !== 'closed') {
            audioContext.close();
        }
    }, [audioContext]);

    const setupAudioAnalysis = useCallback(async () => {
        if (!audioTrack) {
            console.log("📊 [DEBUG] No audio track provided to Waveform");
            return;
        }

        try {
            console.log("📊 [DEBUG] Setting up audio analysis for track:", {
                id: audioTrack.id,
                label: audioTrack.label,
                enabled: audioTrack.enabled,
                readyState: audioTrack.readyState,
                muted: audioTrack.muted,
            });

            const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
            const context = new AudioContextClass();
            setAudioContext(context);

            const source = context.createMediaStreamSource(new MediaStream([audioTrack]));
            const analyser = context.createAnalyser();

            analyser.fftSize = 1024;
            analyser.smoothingTimeConstant = 0.8;

            source.connect(analyser);

            analyserRef.current = analyser;
            dataArrayRef.current = new Uint8Array(new ArrayBuffer(analyser.fftSize));

            console.log("✅ [DEBUG] Audio analyser connected, starting animation");
            startRealTimeAnimation();
        } catch (error) {
            console.error('❌ [DEBUG] Error setting up audio analysis:', error);
            startFallbackAnimation();
        }
    }, [audioTrack, startRealTimeAnimation, startFallbackAnimation]);

    useEffect(() => {
        if (audioTrack && isActive) {
            queueMicrotask(() => setupAudioAnalysis());
        } else if (isActive) {
            // Fallback animation when no audio track
            startFallbackAnimation();
        } else {
            cleanup();
        }

        return cleanup;
    }, [audioTrack, isActive, setupAudioAnalysis, startFallbackAnimation, cleanup]);

    // Visual constants
    const H = variant === 'bottom' ? 40 : 60;
    const mid = H / 2;
    const barW = 2;
    const gap = variant === 'bottom' ? 1 : 2;
    const barCount = levels.length;

    const containerClass = variant === 'bottom'
        ? `waveform-pill ${className}`
        : `waveform-container ${isActive ? 'waveform-active' : 'waveform-inactive'} ${className}`;

    if (variant === 'bottom') {
        return (
            <div className={containerClass}>
                {/* Dotted baseline */}
                <div className="absolute left-4 right-4 top-1/2 -translate-y-1/2 border-t border-dotted border-gray-300" />

                {/* SVG waveform */}
                <svg
                    width="100%"
                    height={H}
                    viewBox={`0 0 ${(barW + gap) * barCount} ${H}`}
                    className="block relative z-10"
                >
                    {levels.map((a, i) => {
                        const x = i * (barW + gap);
                        const h = Math.max(2, a * (H - 6));
                        const y = mid - h / 2;
                        return (
                            <rect
                                key={i}
                                x={x}
                                y={y}
                                width={barW}
                                height={h}
                                rx={1}
                                ry={1}
                                fill={isActive ? "#00b74f" : "#9ca3af"}
                                opacity={isActive ? 0.8 : 0.4}
                            />
                        );
                    })}
                </svg>
            </div>
        );
    }

    // Default variant (welcome screen)
    return (
        <div className={containerClass}>
            <svg
                width="100%"
                height={H}
                viewBox={`0 0 ${(barW + gap) * barCount} ${H}`}
                className="block"
            >
                {levels.map((a, i) => {
                    const x = i * (barW + gap);
                    const h = Math.max(4, a * (H - 8));
                    const y = mid - h / 2;
                    return (
                        <rect
                            key={i}
                            x={x}
                            y={y}
                            width={barW}
                            height={h}
                            rx={1}
                            ry={1}
                            fill={isActive ? "#00b74f" : "#d1d5db"}
                        />
                    );
                })}
            </svg>
        </div>
    );
};

export default Waveform;
import { useState, useEffect } from 'react';

interface TranscriptFile {
  id: string;
  filename: string;
  started_at: string;
  ended_at?: string;
  message_count: number;
}

interface TranscriptData {
  session_id: string;
  started_at: string;
  ended_at?: string;
  messages: Array<{ role: string; content: string; timestamp: string }>;
}

export function useTranscripts() {
  const [transcripts, setTranscripts] = useState<TranscriptFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTranscripts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:7860/api/transcripts');
      if (!response.ok) throw new Error('Failed to load transcripts');
      const data = await response.json();
      setTranscripts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Error loading transcripts:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadTranscript = async (sessionId: string): Promise<TranscriptData | null> => {
    try {
      const response = await fetch(`http://localhost:7860/api/transcripts/${sessionId}`);
      if (!response.ok) throw new Error('Failed to load transcript');
      return await response.json();
    } catch (err) {
      console.error('Error loading transcript:', err);
      return null;
    }
  };

  useEffect(() => {
    loadTranscripts();
  }, []);

  return { transcripts, loading, error, loadTranscript, refreshTranscripts: loadTranscripts };
}

import { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config/api';

interface TranscriptFile {
  id: string;
  started_at: string;
  ended_at?: string;
  message_count: number;
}

interface TranscriptData {
  session_id: string;
  started_at: string;
  ended_at?: string;
  messages: Array<{ role: string; content: string; timestamp?: string }>;
}

interface SessionApiResponse {
  session_id: string;
  started_at: string;
  ended_at?: string;
  messages?: Array<{ role: string; content: string; timestamp?: string }>;
}

export function useTranscripts() {
  const [transcripts, setTranscripts] = useState<TranscriptFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTranscripts = async () => {
    setLoading(true);
    setError(null);
    try {
      // Use DynamoDB endpoint instead of file-based
      const response = await fetch(`${API_ENDPOINTS.SESSIONS.LIST}?limit=50`);
      if (!response.ok) throw new Error('Failed to load sessions');
      const result = await response.json();

      if (result.success && result.sessions) {
        // Transform DynamoDB sessions to match interface
        const sessions = result.sessions.map((session: SessionApiResponse) => ({
          id: session.session_id,
          started_at: session.started_at,
          ended_at: session.ended_at,
          message_count: session.messages?.length || 0,
        }));
        setTranscripts(sessions);
      } else {
        setTranscripts([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Error loading sessions from DynamoDB:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadTranscript = async (sessionId: string): Promise<TranscriptData | null> => {
    try {
      // Use DynamoDB endpoint instead of file-based
      const response = await fetch(API_ENDPOINTS.SESSIONS.GET(sessionId));
      if (!response.ok) throw new Error('Failed to load session');
      const result = await response.json();

      if (result.success && result.session) {
        return result.session as TranscriptData;
      }
      return null;
    } catch (err) {
      console.error('Error loading session from DynamoDB:', err);
      return null;
    }
  };

  useEffect(() => {
    loadTranscripts();
  }, []);

  return { transcripts, loading, error, loadTranscript, refreshTranscripts: loadTranscripts };
}

import { useState, useEffect } from 'react';
import { Clock, MessageSquare, ChevronRight, X, History } from 'lucide-react';
import { Sparkles } from 'lucide-react';
import { API_ENDPOINTS } from '../config/api';

interface Session {
  session_id: string;
  started_at: string;
  ended_at?: string;
  messages: Array<{
    role: string;
    content: string;
    timestamp?: string;
  }>;
  created_at: number;
}

interface SessionHistoryProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SessionHistory({ isOpen, onClose }: SessionHistoryProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchSessions();
    }
  }, [isOpen]);

  const fetchSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_ENDPOINTS.SESSIONS.LIST}?limit=50`);
      const data = await response.json();
      if (data.success) {
        setSessions(data.sessions || []);
      } else {
        setError(data.error || 'Failed to load sessions');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sessions');
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  const formatDateShort = (timestamp: number) => {
    try {
      const date = new Date(timestamp * 1000);
      return date.toLocaleString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '';
    }
  };

  const getMessageCount = (session: Session) => {
    return session.messages?.length || 0;
  };

  const formatMessageLines = (text: string): string[] => {
    if (!text) return [];
    let t = text.replace(/\r\n/g, "\n");
    t = t.replace(/([^\n])\s-\s/g, "$1\n• ");
    t = t.replace(/([^\n])\s•\s/g, "$1\n• ");
    t = t.replace(/([^\n])\s(\d+)\.\s/g, "$1\n$2. ");
    return t.split(/\n+/).map(s => s.trim()).filter(Boolean);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/50 backdrop-blur-sm">
      <div className="w-full max-w-6xl h-[85vh] bg-white rounded-2xl shadow-2xl flex flex-col m-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <History className="w-6 h-6" style={{color: 'var(--vp-green)'}} />
            <h2 className="text-xl font-semibold text-gray-800">Session History</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sessions List */}
          <div className="w-1/3 border-r border-gray-200 overflow-y-auto bg-gray-50">
            <div className="p-4">
              {loading ? (
                <div className="text-center py-8 text-gray-500">Loading...</div>
              ) : error ? (
                <div className="text-center py-8 text-red-600">{error}</div>
              ) : sessions.length === 0 ? (
                <div className="text-center py-8 text-gray-500">No sessions found</div>
              ) : (
                <div className="space-y-2">
                  {sessions.map((session) => (
                    <button
                      key={session.session_id}
                      onClick={() => setSelectedSession(session)}
                      className={`w-full text-left p-4 rounded-xl border transition ${
                        selectedSession?.session_id === session.session_id
                          ? 'border-emerald-500 bg-emerald-50'
                          : 'border-gray-200 bg-white hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Clock className="w-4 h-4 text-gray-500" />
                            <span className="text-xs text-gray-600">
                              {formatDateShort(session.created_at)}
                            </span>
                          </div>
                          <div className="text-sm font-medium text-gray-800 truncate">
                            {session.session_id}
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          <span>{getMessageCount(session)} messages</span>
                        </div>
                        {session.ended_at && (
                          <span className="text-emerald-600">Completed</span>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Session Details */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {selectedSession ? (
              <>
                {/* Session Header */}
                <div className="p-4 border-b border-gray-200 bg-white">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold text-gray-800">
                      {selectedSession.session_id}
                    </h3>
                    <button
                      onClick={() => setSelectedSession(null)}
                      className="text-sm text-gray-600 hover:text-gray-800"
                    >
                      Close
                    </button>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>Started: {formatDate(selectedSession.started_at)}</span>
                    {selectedSession.ended_at && (
                      <span>Ended: {formatDate(selectedSession.ended_at)}</span>
                    )}
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {selectedSession.messages?.map((message, index) => (
                    message.role === 'user' ? (
                      <div key={index} className="flex justify-end">
                        <div className="max-w-[70%] rounded-2xl rounded-tr-sm px-4 py-2 shadow-sm whitespace-pre-wrap" style={{backgroundColor:'#EAF7F0', color:'#0B3D2E'}}>
                          {formatMessageLines(message.content).map((line, i) => (
                            <div key={i} className="mb-1 last:mb-0">{line}</div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div key={index} className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full grid place-items-center vp-gradient text-white shadow-sm flex-shrink-0">
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
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Select a session to view transcript</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


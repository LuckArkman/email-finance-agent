import axios from 'axios';

// ─────────────────────────────────────────────────────────────
// Cliente HTTP base — aponta sempre para o Hermes.Gateway .NET
// O Gateway faz proxy seguro para o Hermes Agent internamente.
// ─────────────────────────────────────────────────────────────
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api/hermes',
  headers: { 'Content-Type': 'application/json' },
});

// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// ─────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface AgentStatus {
  online: boolean;
  version: string;
  model: string;
  provider: string;
  activeSessions: number;
  message?: string;
}

export interface AgentSession {
  sessionId: string;
  platform: string;
  createdAt: string;
  messageCount: number;
  tokensUsed: number;
}

// ─────────────────────────────────────────────────────────────
// Agent API — chama o Hermes.Gateway que faz proxy ao Hermes Agent
// ─────────────────────────────────────────────────────────────

export const agentApi = {
  /**
   * Verifica se o Hermes Agent está online e retorna metadados.
   * GET /api/hermes/agent/status
   */
  getStatus: async (): Promise<AgentStatus> => {
    const res = await api.get<AgentStatus>('/agent/status');
    return res.data;
  },

  /**
   * Lista sessões recentes do Hermes Agent.
   * GET /api/hermes/agent/sessions
   */
  getSessions: async (): Promise<AgentSession[]> => {
    const res = await api.get<{ sessions: AgentSession[] }>('/agent/sessions');
    return res.data.sessions;
  },

  /**
   * Envia mensagens para o Hermes Agent e recebe resposta.
   * POST /api/hermes/agent/chat
   */
  chat: async (messages: ChatMessage[]): Promise<string> => {
    const res = await api.post<{ reply: string }>('/agent/chat', { messages });
    return res.data.reply;
  },

  /**
   * Aciona o Hermes Agent para processar um documento manualmente.
   * POST /api/hermes/agent/process-document
   */
  processDocument: async (documentPath: string, sourceEmail: string): Promise<string> => {
    const res = await api.post<{ agentResponse: string }>('/agent/process-document', {
      documentPath,
      sourceEmail,
    });
    return res.data.agentResponse;
  },
};

// ─────────────────────────────────────────────────────────────
// Invoices API
// ─────────────────────────────────────────────────────────────
export const invoicesApi = {
  getAll: () => api.get('/invoices'),
  getById: (id: string) => api.get(`/invoices/${id}`),
  flagForReview: (id: string, reason: string) =>
    api.post(`/invoices/${id}/flag`, { reason }),
};

// ─────────────────────────────────────────────────────────────
// Auth API
// ─────────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (email: string, password: string) =>
    api.post('/auth/register', { email, password }),
};

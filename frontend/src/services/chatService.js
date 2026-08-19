import api from './api';

export const chatService = {
  getSessions: () => api.get('/chat/sessions'),
  createSession: (title) => api.post('/chat/sessions', { title }),
  getSession: (id) => api.get(`/chat/sessions/${id}`),
  deleteSession: (id) => api.delete(`/chat/sessions/${id}`),
  ask: (payload) => api.post('/chat/ask', payload),
};

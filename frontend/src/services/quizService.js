import api from './api';

export const quizService = {
  generateQuestions: (payload) => api.post('/quiz/generate-questions', payload),
  startQuiz: (payload) => api.post('/quiz/start-quiz', payload),
  evaluateAnswer: (payload) => api.post('/quiz/evaluate-answer', payload),
  getDashboardStats: () => api.get('/quiz/dashboard-stats'),
};

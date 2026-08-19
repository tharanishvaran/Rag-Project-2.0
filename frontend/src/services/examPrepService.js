import api from './api';

export const examPrepService = {
  getStrategy: (payload) => api.post('/exam-prep/strategy', payload),
  getStudyPlan: (payload) => api.post('/exam-prep/study-plan', payload),
  getImportantTopics: (payload) => api.post('/exam-prep/important-topics', payload),
  getPaperAnalysis: (payload) => api.post('/exam-prep/paper-analysis', payload),
  getExpectedQuestions: (payload) => api.post('/exam-prep/expected-questions', payload),
};

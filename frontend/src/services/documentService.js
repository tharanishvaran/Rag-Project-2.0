import api from './api';

export const documentService = {
  upload: (formData, onUploadProgress) =>
    api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress,
    }),
  getAll: (categoryId) =>
    api.get('/documents', { params: categoryId ? { category_id: categoryId } : {} }),
  getOne: (id) => api.get(`/documents/${id}`),
  getStatus: (id) => api.get(`/documents/${id}/status`),
  delete: (id) => api.delete(`/documents/${id}`),
  updateCategory: (id, categoryId) =>
    api.patch(`/documents/${id}/category`, { category_id: categoryId }),
};

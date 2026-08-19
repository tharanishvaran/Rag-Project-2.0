import { useState, useEffect, useRef } from 'react';
import { documentService } from '../services/documentService';
import { categoryService } from '../services/categoryService';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  FileText, 
  UploadCloud, 
  Trash2, 
  Filter, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Search,
  FolderOpen,
  Plus
} from 'lucide-react';
import './Documents.css';

function formatSize(bytes) {
  if (!bytes) return '';
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filterCat, setFilterCat] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('');
  const fileRef = useRef();

  const fetchAll = async () => {
    try {
      const [docsRes, catRes] = await Promise.all([
        documentService.getAll(filterCat || undefined),
        categoryService.getAll(),
      ]);
      setDocuments(docsRes.data.data.documents);
      setCategories(catRes.data.data.categories);
    } catch { 
      setError('Failed to fetch document repository.'); 
    } finally { 
      setLoading(false); 
    }
  };

  useEffect(() => { fetchAll(); }, [filterCat]);

  const handleUpload = async (files) => {
    if (!files || files.length === 0) return;
    setError(''); setSuccess('');
    setUploading(true); setUploadProgress(0);

    const formData = new FormData();
    Array.from(files).forEach(f => formData.append('files', f));
    if (selectedCategory) formData.append('category_id', selectedCategory);

    try {
      await documentService.upload(formData, e => {
        if (e.total) setUploadProgress(Math.round(e.loaded / e.total * 100));
      });
      setSuccess('PDF document uploaded & indexed into vector database!');
      fetchAll();
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed. Please try again.');
    } finally { 
      setUploading(false); setUploadProgress(0); 
    }
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;
    try {
      await documentService.delete(id);
      setDocuments(prev => prev.filter(d => d.id !== id));
      setSuccess('Document removed successfully.');
    } catch { 
      setError('Failed to delete document.'); 
    }
  };

  const filteredDocs = documents.filter(doc => 
    doc.original_filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) return <LoadingSpinner message="Accessing Document Repository..." />;

  return (
    <div className="documents-page animate-fade-in">
      <div className="page-header">
        <h1>Document Repository</h1>
        <p>Manage, upload, and organize your academic PDF documents for RAG intelligence.</p>
      </div>

      {/* Upload Zone Container */}
      <div className="upload-section glass-card">
        <div className="upload-section-header">
          <div className="section-title">
            <UploadCloud size={20} className="section-icon" />
            <h3>Upload Study Materials & Multi-Format Documents</h3>
          </div>
          <span className="badge badge-primary">PDF • Word (.docx) • Text (.txt) • Markdown (.md) • PowerPoint (.pptx)</span>
        </div>

        <div
          className={`upload-zone-modern ${dragOver ? 'drag-over' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files); }}
          onClick={() => fileRef.current?.click()}
        >
          <div className="upload-icon-circle">
            <UploadCloud size={32} />
          </div>
          <div className="upload-text-content">
            <h4>Drag & Drop your Study Materials here</h4>
            <p>Supports PDF, Word (.docx), Text (.txt), Markdown (.md), and PowerPoint (.pptx) up to 50MB per file</p>
          </div>
          <button className="btn btn-secondary btn-sm" type="button">
            Browse Files
          </button>
          <input ref={fileRef} type="file" multiple accept=".pdf,.docx,.doc,.txt,.md,.pptx" hidden onChange={e => handleUpload(e.target.files)} />
        </div>



        <div className="upload-controls">
          <select 
            className="input category-select" 
            value={selectedCategory} 
            onChange={e => setSelectedCategory(e.target.value)}
          >
            <option value="">Choose category (optional)...</option>
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>

          <button 
            className="btn btn-primary" 
            onClick={() => fileRef.current?.click()} 
            disabled={uploading}
          >
            {uploading ? (
              <>
                <Sparkles className="spin" size={16} />
                <span>Uploading {uploadProgress}%</span>
              </>
            ) : (
              <>
                <Plus size={18} />
                <span>Upload PDF</span>
              </>
            )}
          </button>
        </div>

        {uploading && (
          <div className="upload-progress-wrapper">
            <div className="progress-bar-track">
              <div className="progress-bar-fill" style={{ width: `${uploadProgress}%` }} />
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="alert alert-error animate-fade-in" style={{ marginBottom: 20 }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="alert alert-success animate-fade-in" style={{ marginBottom: 20 }}>
          <CheckCircle2 size={18} />
          <span>{success}</span>
        </div>
      )}

      {/* Filter Bar & Search */}
      <div className="doc-filter-bar glass-card">
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input 
            type="text" 
            className="input search-input" 
            placeholder="Search documents by name..." 
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="category-chips">
          <button 
            className={`filter-chip ${!filterCat ? 'active' : ''}`} 
            onClick={() => setFilterCat('')}
          >
            All Documents ({documents.length})
          </button>
          {categories.map(c => (
            <button 
              key={c.id} 
              className={`filter-chip ${filterCat == c.id ? 'active' : ''}`} 
              onClick={() => setFilterCat(c.id)}
            >
              {c.name}
            </button>
          ))}
        </div>
      </div>

      {/* Document Grid */}
      {filteredDocs.length === 0 ? (
        <div className="empty-state glass-card">
          <FolderOpen size={48} className="empty-icon" />
          <h3>No documents found</h3>
          <p>{searchQuery ? 'No documents match your search filter.' : 'Upload your first PDF document to begin asking questions.'}</p>
        </div>
      ) : (
        <div className="doc-grid">
          {filteredDocs.map(doc => (
            <div key={doc.id} className="doc-card glass-card card-hover">
              <div className="doc-card-top">
                <div className="doc-card-icon">
                  <FileText size={24} />
                </div>
                <span className={`badge ${
                  doc.upload_status === 'completed' ? 'badge-success' : 
                  doc.upload_status === 'failed' ? 'badge-danger' : 'badge-warning'
                }`}>
                  {doc.upload_status}
                </span>
              </div>

              <div className="doc-card-body">
                <h4 className="doc-card-title" title={doc.original_filename}>
                  {doc.original_filename}
                </h4>
                
                <div className="doc-card-meta">
                  {doc.category_name && (
                    <span className="badge badge-primary">{doc.category_name}</span>
                  )}
                  <span className="meta-text">
                    {doc.total_pages ? `${doc.total_pages} pages` : ''} 
                    {doc.file_size ? ` · ${formatSize(doc.file_size)}` : ''}
                  </span>
                </div>
              </div>

              <div className="doc-card-actions">
                <button 
                  className="btn btn-ghost btn-sm delete-btn" 
                  onClick={() => handleDelete(doc.id, doc.original_filename)}
                >
                  <Trash2 size={16} />
                  <span>Delete</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

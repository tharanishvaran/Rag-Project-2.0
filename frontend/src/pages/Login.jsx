import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Sparkles, Mail, Lock, ArrowRight, ShieldCheck } from 'lucide-react';

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      {/* Background ambient glowing blobs */}
      <div className="app-ambient-bg">
        <div className="blob blob-1" />
        <div className="blob blob-2" />
      </div>

      <div className="auth-card glass-card animate-fade-in">
        <div className="auth-logo">
          <div className="auth-logo-icon">
            <Sparkles size={22} className="logo-sparkle" />
          </div>
          <div className="auth-logo-text">
            SmartDoc <span className="logo-badge">AI</span>
          </div>
        </div>

        <h2 style={{ marginBottom: 6 }}>Welcome Back</h2>
        <p style={{ marginBottom: 28, fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          Sign in to access your RAG document intelligence workspace
        </p>

        {error && <div className="alert alert-error" style={{ marginBottom: 20 }}>⚠️ {error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Mail size={14} className="text-primary" /> Email address
            </label>
            <input
              className="input"
              type="email"
              placeholder="you@university.edu"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
              autoFocus
            />
          </div>

          <div className="input-group">
            <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Lock size={14} className="text-primary" /> Password
            </label>
            <input
              className="input"
              type="password"
              placeholder="Enter your password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>

          <button 
            className="btn btn-primary btn-lg" 
            type="submit" 
            disabled={loading} 
            style={{ width: '100%', marginTop: 8, justifyContent: 'center' }}
          >
            {loading ? (
              <>
                <Sparkles className="spin" size={18} />
                <span>Signing in...</span>
              </>
            ) : (
              <>
                <span>Sign In to Workspace</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="auth-footer" style={{ marginTop: 24, textAlign: 'center', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
          Don't have an account? <Link to="/register" style={{ fontWeight: 600 }}>Create one free</Link>
        </div>
      </div>
    </div>
  );
}

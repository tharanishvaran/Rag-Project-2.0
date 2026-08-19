export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="loading-overlay">
      <div className="spinner" />
      <span style={{ color: 'var(--text-3)', fontSize: '0.88rem' }}>{message}</span>
    </div>
  );
}

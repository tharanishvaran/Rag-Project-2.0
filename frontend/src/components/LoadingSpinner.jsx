export default function LoadingSpinner({ 
  message = 'Loading...', 
  variant = 'floating', 
  fullPage = false,
  className = ''
}) {
  if (variant === 'inline') {
    return (
      <div className={`loading-inline ${className}`}>
        <div className="spinner spinner-sm" />
        <span className="loading-message">{message}</span>
      </div>
    );
  }

  if (variant === 'bar') {
    return (
      <div className={`loading-bar-container ${className}`}>
        <div className="loading-bar-indeterminate" />
        <div className="loading-bar-content">
          <div className="spinner spinner-sm" />
          <span>{message}</span>
        </div>
      </div>
    );
  }

  // Default 'floating' or 'overlay'
  return (
    <div className={`loading-overlay-container ${fullPage ? 'full-page' : ''} ${className}`}>
      <div className="loading-glass-card">
        <div className="spinner-glow-wrapper">
          <div className="spinner" />
        </div>
        <div className="loading-card-text">
          <span className="loading-title">{message}</span>
          <span className="loading-subtitle">Retrieving data from backend...</span>
        </div>
      </div>
    </div>
  );
}


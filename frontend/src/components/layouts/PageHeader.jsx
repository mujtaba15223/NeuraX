import { RefreshCw } from "lucide-react";

function PageHeader({
  label,
  title,
  description,
  action,
  onAction,
  actionLoading = false,
}) {
  return (
    <div className="page-header">
      <div>
        {label && (
          <span className="header-label">
            {label}
          </span>
        )}

        <h1>{title}</h1>

        {description && (
          <p>{description}</p>
        )}
      </div>

      {action && onAction && (
        <button
          className="action-button"
          onClick={onAction}
          disabled={actionLoading}
        >
          <RefreshCw
            size={16}
            className={actionLoading ? "spin" : ""}
          />

          {action}
        </button>
      )}
    </div>
  );
}

export default PageHeader;
import { Image as ImageIcon, ZoomIn } from "lucide-react";

function ImageViewer({ image, fileName, status }) {
  if (!image) {
    return (
      <div className="dashboard-card image-viewer">
        <div className="card-header">
          <div>
            <span className="header-label">
              INSPECTION IMAGE
            </span>

            <h3>No Image Selected</h3>
          </div>

          <ImageIcon size={22} />
        </div>

        <div className="image-placeholder">
          <ImageIcon size={48} />

          <p>
            Upload a manufacturing image to begin
            visual inspection.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-card image-viewer">
      <div className="card-header">
        <div>
          <span className="header-label">
            INSPECTION IMAGE
          </span>

          <h3>{fileName || "Uploaded Image"}</h3>
        </div>

        <ZoomIn size={22} />
      </div>

      <div className="inspection-image-container">
        <img
          src={image}
          alt="Manufacturing inspection"
          className="inspection-image"
        />

        {status && (
          <div
            className={`inspection-status ${
              status.toLowerCase() === "defective"
                ? "status-defective"
                : "status-good"
            }`}
          >
            {status}
          </div>
        )}
      </div>

      <div className="image-viewer-footer">
        <span>
          Visual inspection input
        </span>

        <span>
          AI analysis ready
        </span>
      </div>
    </div>
  );
}

export default ImageViewer;
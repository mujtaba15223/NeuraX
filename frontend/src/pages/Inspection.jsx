import { useEffect, useState } from "react";
import {
  Upload,
  RefreshCw,
  Camera,
  AlertTriangle,
} from "lucide-react";

import ImageViewer from "../components/inspection/ImageViewer";
import DefectResult from "../components/inspection/DefectResult";
import DefectDetails from "../components/inspection/DefectDetails";
import ConfidenceBar from "../components/inspection/ConfidenceBar";
import API_BASE_URL from "../config/api";

function Inspection() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);
  const [backendReady, setBackendReady] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    checkBackend();

    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  const checkBackend = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/health`
      );

      setBackendReady(response.ok);
    } catch {
      setBackendReady(false);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!file.type.startsWith("image/")) {
      setError("Please select a valid image file.");
      return;
    }

    setError("");
    setResult(null);

    if (preview) {
      URL.revokeObjectURL(preview);
    }

    const imageUrl = URL.createObjectURL(file);

    setSelectedFile(file);
    setPreview(imageUrl);
  };

  const runInspection = async () => {
    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResult(null);

      const formData = new FormData();

      formData.append(
        "file",
        selectedFile
      );

      const response = await fetch(
        `${API_BASE_URL}/inspection`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            "Inspection failed."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message ||
          "Unable to complete inspection."
      );
    } finally {
      setLoading(false);
    }
  };

  const clearInspection = () => {
    if (preview) {
      URL.revokeObjectURL(preview);
    }

    setSelectedFile(null);
    setPreview("");
    setResult(null);
    setError("");
  };

  const inspectionResult =
    result?.inspection || result?.vision || result || {};

  const isDefective = Boolean(
    inspectionResult?.is_defective
  );

  const status =
    result
      ? inspectionResult?.status ||
        (isDefective ? "DEFECTIVE" : "GOOD")
      : null;

  const anomalyScore =
    inspectionResult?.anomaly_score ?? 0;

  const threshold =
    inspectionResult?.threshold ?? 0.138;

  const model =
    inspectionResult?.model ||
    "ResNet18 feature anomaly detector";

  const confidence =
    threshold > 0
      ? Math.min(
          1,
          Math.max(
            0,
            anomalyScore / threshold
          )
        )
      : 0;

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <span className="header-label">
            VISUAL INSPECTION
          </span>

          <h1>AI Defect Inspection</h1>

          <p>
            Upload a manufacturing image and let the
            vision model detect visual anomalies.
          </p>
        </div>

        <div className="inspection-header-status">
          <span
            className={
              backendReady
                ? "status-dot online"
                : "status-dot offline"
            }
          />

          {backendReady
            ? "AI Backend Online"
            : "AI Backend Offline"}
        </div>
      </div>

      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="header-label">
              IMAGE INPUT
            </span>

            <h3>
              Upload Product Image
            </h3>
          </div>

          <Camera size={22} />
        </div>

        <div className="upload-area">
          <input
            id="inspection-file"
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            hidden
          />

          <label
            htmlFor="inspection-file"
            className="upload-button"
          >
            <Upload size={18} />
            Choose Image
          </label>

          {selectedFile && (
            <div className="selected-file">
              <strong>
                {selectedFile.name}
              </strong>

              <span>
                {(
                  selectedFile.size /
                  1024
                ).toFixed(1)}{" "}
                KB
              </span>
            </div>
          )}

          <p className="upload-help">
            Use a product image from the inspection
            dataset. PNG and JPG images are supported.
          </p>
        </div>
      </div>

      {error && (
        <div className="dashboard-card inspection-error">
          <AlertTriangle size={20} />

          <div>
            <strong>
              Inspection Error
            </strong>

            <p>{error}</p>
          </div>
        </div>
      )}

      <div className="inspection-grid">
        <ImageViewer
          image={preview}
          fileName={
            selectedFile?.name
          }
          status={status}
        />

        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="header-label">
                INSPECTION CONTROL
              </span>

              <h3>
                Run AI Inspection
              </h3>
            </div>

            <RefreshCw size={22} />
          </div>

          <p className="control-description">
            The uploaded image will be converted into
            ResNet18 visual features and compared with
            the normal reference feature database.
          </p>

          <button
            className="primary-button"
            onClick={runInspection}
            disabled={
              !selectedFile ||
              loading ||
              !backendReady
            }
          >
            {loading ? (
              <>
                <RefreshCw
                  size={18}
                  className="spin"
                />

                Analyzing Image...
              </>
            ) : (
              <>
                <Camera size={18} />

                Run AI Inspection
              </>
            )}
          </button>

          {selectedFile && (
            <button
              className="secondary-button"
              onClick={clearInspection}
              disabled={loading}
            >
              Clear Inspection
            </button>
          )}
        </div>
      </div>

      {result && (
        <>
          <DefectResult
            status={status}
            anomalyScore={anomalyScore}
            threshold={threshold}
            model={model}
          />

          <DefectDetails
            status={status}
            anomalyScore={anomalyScore}
            threshold={threshold}
            defectType={
              inspectionResult?.defect_type
            }
            classificationConfidence={
              inspectionResult?.classification_confidence
            }
            prototypeSimilarity={
              inspectionResult?.prototype_similarity
            }
            classScores={
              inspectionResult?.class_scores
            }
            likelyCause={
              result?.likely_cause
            }
          />

          <div className="dashboard-card">
            <div className="card-header">
              <div>
                <span className="header-label">
                  CONFIDENCE SIGNAL
                </span>

                <h3>
                  Anomaly Confidence
                </h3>
              </div>
            </div>

            <ConfidenceBar
              value={confidence}
              label={
                isDefective
                  ? "Defect Signal"
                  : "Normal Signal"
              }
            />
          </div>
        </>
      )}
    </div>
  );
}

export default Inspection;
function ConfidenceBar({
  value = 0,
  label = "Confidence",
}) {
  const confidence = Math.max(
    0,
    Math.min(100, Number(value) * 100)
  );

  return (
    <div className="confidence-bar-container">
      <div className="confidence-header">
        <span>{label}</span>

        <strong>
          {confidence.toFixed(1)}%
        </strong>
      </div>

      <div className="confidence-track">
        <div
          className="confidence-fill"
          style={{
            width: `${confidence}%`,
          }}
        />
      </div>

      <div className="confidence-scale">
        <span>0%</span>
        <span>50%</span>
        <span>100%</span>
      </div>
    </div>
  );
}

export default ConfidenceBar;
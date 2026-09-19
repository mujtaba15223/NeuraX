import { useCallback, useEffect, useState } from "react";
import { getAnalysis } from "../services/api";

export function useApi() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalysis = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const result = await getAnalysis();
      setData(result);
    } catch (err) {
      setError(err.message || "Unable to connect to backend");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  return {
    data,
    loading,
    error,
    refresh: fetchAnalysis,
  };
}
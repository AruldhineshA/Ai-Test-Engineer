/**
 * useApi — Custom hook for API calls with loading/error state.
 * Eliminates repetitive try/catch/loading in every component.
 *
 * Usage:
 *   const { data, loading, error, execute } = useApi();
 *   execute(() => api.get("/projects"));
 */

import { useState, useCallback } from "react";

export function useApi() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiCall) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiCall();
      setData(response.data);
      return response.data;
    } catch (err) {
      const message = err.response?.data?.detail || err.message || "Something went wrong";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, loading, error, execute, reset };
}

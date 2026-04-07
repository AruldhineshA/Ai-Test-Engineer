/**
 * useProjects — Custom hook for project CRUD operations.
 */

import { useState, useEffect, useCallback } from "react";
import api from "../utils/api";

export function useProjects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get("/projects/");
      setProjects(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch projects");
    } finally {
      setLoading(false);
    }
  }, []);

  const createProject = async (name, description) => {
    const res = await api.post("/projects/", { name, description });
    setProjects((prev) => [res.data, ...prev]);
    return res.data;
  };

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return { projects, loading, error, createProject, refetch: fetchProjects };
}

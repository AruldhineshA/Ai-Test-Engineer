/**
 * Formatting utilities — Dates, text, colors.
 */

export const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text || "";
  return text.slice(0, maxLength) + "...";
};

export const capitalize = (str) => {
  if (!str) return "";
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const getStatusColor = (status) => {
  const colors = {
    draft: "#f59e0b",
    approved: "#10b981",
    rejected: "#ef4444",
    uploaded: "#3b82f6",
    analyzing: "#8b5cf6",
    analyzed: "#10b981",
    failed: "#ef4444",
    generated: "#3b82f6",
  };
  return colors[status] || "#6b7280";
};

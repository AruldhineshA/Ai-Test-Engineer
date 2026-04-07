/**
 * Reusable status badge with auto-coloring.
 */

import { capitalize } from "../../utils/formatters";

const statusStyles = {
  draft: "bg-amber-50 text-amber-700 border-amber-200",
  approved: "bg-emerald-50 text-emerald-700 border-emerald-200",
  rejected: "bg-red-50 text-red-700 border-red-200",
  uploaded: "bg-blue-50 text-blue-700 border-blue-200",
  analyzing: "bg-purple-50 text-purple-700 border-purple-200",
  analyzed: "bg-emerald-50 text-emerald-700 border-emerald-200",
  failed: "bg-red-50 text-red-700 border-red-200",
  generated: "bg-blue-50 text-blue-700 border-blue-200",
};

export function StatusBadge({ status }) {
  const style = statusStyles[status] || "bg-gray-50 text-gray-700 border-gray-200";

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style}`}>
      {capitalize(status)}
    </span>
  );
}

/**
 * Reusable loading spinner.
 */

import { Loader2 } from "lucide-react";

export function Loader({ text = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mb-3" />
      <p className="text-sm text-gray-500">{text}</p>
    </div>
  );
}

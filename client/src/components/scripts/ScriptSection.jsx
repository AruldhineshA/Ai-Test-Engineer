/**
 * ScriptSection — embedded inside the test case detail modal.
 * Lets the user generate Playwright Python/JS or Artillery YAML scripts
 * for a test case, view the code, copy it, and download as a file.
 */

import { useEffect, useState, useCallback } from "react";
import { Code2, Copy, Download, RefreshCw, Loader2, Trash2 } from "lucide-react";
import api from "../../utils/api";
import toast from "react-hot-toast";
import { Button } from "../common/Button";

const SCRIPT_OPTIONS = [
  { id: "playwright-python", label: "Playwright (Python)", script_type: "playwright", language: "python", lang: "python" },
  { id: "playwright-javascript", label: "Playwright (JavaScript)", script_type: "playwright", language: "javascript", lang: "javascript" },
  { id: "artillery-yaml", label: "Artillery (YAML)", script_type: "artillery", language: "yaml", lang: "yaml" },
];

export function ScriptSection({ testCaseId }) {
  const [scripts, setScripts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generatingId, setGeneratingId] = useState(null);
  const [activeOptionId, setActiveOptionId] = useState(SCRIPT_OPTIONS[0].id);

  const fetchScripts = useCallback(async () => {
    if (!testCaseId) return;
    setLoading(true);
    try {
      const res = await api.get(`/scripts/?test_case_id=${testCaseId}`);
      setScripts(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      if (err.response?.status !== 404) {
        toast.error("Failed to load scripts");
      }
      setScripts([]);
    } finally {
      setLoading(false);
    }
  }, [testCaseId]);

  useEffect(() => { fetchScripts(); }, [fetchScripts]);

  const findScript = (option) =>
    scripts.find(
      (s) => s.script_type === option.script_type && s.language === option.language
    );

  const handleGenerate = async (option) => {
    setGeneratingId(option.id);
    try {
      const res = await api.post("/scripts/generate", {
        test_case_id: testCaseId,
        script_type: option.script_type,
        language: option.language,
      });
      toast.success(`${option.label} generated!`);
      // Optimistically update list
      setScripts((prev) => {
        const others = prev.filter(
          (s) => !(s.script_type === option.script_type && s.language === option.language)
        );
        return [...others, res.data];
      });
      setActiveOptionId(option.id);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Generation failed");
    } finally {
      setGeneratingId(null);
    }
  };

  const handleCopy = async (code) => {
    try {
      await navigator.clipboard.writeText(code);
      toast.success("Copied to clipboard");
    } catch {
      toast.error("Copy failed — your browser may block clipboard access");
    }
  };

  const handleDownload = async (script) => {
    try {
      const res = await api.get(`/scripts/${script.id}/download`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      const ext = script.language === "python" ? "py"
        : script.language === "javascript" ? "spec.js"
        : "yml";
      link.setAttribute("download", `script_${script.test_case_id}_${script.script_type}.${ext}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      toast.error("Download failed");
    }
  };

  const handleDelete = async (script) => {
    if (!confirm("Delete this generated script?")) return;
    try {
      await api.delete(`/scripts/${script.id}`);
      setScripts((prev) => prev.filter((s) => s.id !== script.id));
      toast.success("Script deleted");
    } catch {
      toast.error("Delete failed");
    }
  };

  const activeOption = SCRIPT_OPTIONS.find((o) => o.id === activeOptionId);
  const activeScript = activeOption ? findScript(activeOption) : null;
  const isGenerating = generatingId === activeOptionId;

  return (
    <div className="border-t border-gray-100 pt-4 mt-2">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
          <Code2 className="w-4 h-4 text-indigo-600" />
          Automation Scripts
        </h4>
      </div>

      {/* Tabs for each script type */}
      <div className="flex flex-wrap gap-2 mb-3">
        {SCRIPT_OPTIONS.map((option) => {
          const exists = !!findScript(option);
          const isActive = option.id === activeOptionId;
          return (
            <button
              key={option.id}
              onClick={() => setActiveOptionId(option.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                isActive
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {option.label}
              {exists && (
                <span className={`ml-1.5 inline-block w-1.5 h-1.5 rounded-full ${
                  isActive ? "bg-emerald-300" : "bg-emerald-500"
                }`} />
              )}
            </button>
          );
        })}
      </div>

      {/* Active panel */}
      <div className="bg-gray-50 rounded-lg p-3">
        {loading ? (
          <div className="flex items-center justify-center py-6 text-sm text-gray-500">
            <Loader2 className="w-4 h-4 animate-spin mr-2" />
            Loading scripts...
          </div>
        ) : !activeScript ? (
          <div className="text-center py-4">
            <p className="text-sm text-gray-600 mb-3">
              No {activeOption.label} script yet.
            </p>
            <Button
              size="sm"
              icon={Code2}
              loading={isGenerating}
              onClick={() => handleGenerate(activeOption)}
            >
              {isGenerating ? "Generating..." : `Generate ${activeOption.label}`}
            </Button>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-500">
                Generated {new Date(activeScript.created_at).toLocaleString()}
              </span>
              <div className="flex gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  icon={RefreshCw}
                  loading={isGenerating}
                  onClick={() => handleGenerate(activeOption)}
                  title="Regenerate"
                >
                  Regenerate
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  icon={Copy}
                  onClick={() => handleCopy(activeScript.code_content)}
                  title="Copy code"
                >
                  Copy
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  icon={Download}
                  onClick={() => handleDownload(activeScript)}
                  title="Download file"
                >
                  Download
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  icon={Trash2}
                  onClick={() => handleDelete(activeScript)}
                  title="Delete"
                >
                  Delete
                </Button>
              </div>
            </div>
            <pre className="bg-gray-900 text-gray-100 text-xs p-3 rounded-md overflow-x-auto max-h-96 overflow-y-auto font-mono leading-relaxed">
              <code>{activeScript.code_content}</code>
            </pre>
          </>
        )}
      </div>
    </div>
  );
}

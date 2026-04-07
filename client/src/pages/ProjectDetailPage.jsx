/**
 * Project Detail — Upload documents, analyze, generate test cases.
 * This is the core Phase 1 workflow page.
 */

import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { Upload, FileText, Sparkles, ClipboardCheck, Download } from "lucide-react";
import { Card, CardBody, CardHeader } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { StatusBadge } from "../components/common/StatusBadge";
import { EmptyState } from "../components/common/EmptyState";
import { Loader } from "../components/common/Loader";
import { Modal } from "../components/common/Modal";
import { formatDate, truncateText } from "../utils/formatters";
import api from "../utils/api";
import toast from "react-hot-toast";

export function ProjectDetailPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [testCases, setTestCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showTestCase, setShowTestCase] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const [projRes, docsRes, tcsRes] = await Promise.all([
        api.get(`/projects/${projectId}`),
        api.get(`/documents/?project_id=${projectId}`).catch(() => ({ data: [] })),
        api.get(`/testcases/?project_id=${projectId}`).catch(() => ({ data: [] })),
      ]);
      setProject(projRes.data);
      setDocuments(Array.isArray(docsRes.data) ? docsRes.data : []);
      setTestCases(Array.isArray(tcsRes.data) ? tcsRes.data : []);
    } catch {
      toast.error("Failed to load project");
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      await api.post(`/documents/upload?project_id=${projectId}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success(`"${file.name}" uploaded!`);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async (docId) => {
    try {
      toast.loading("AI is analyzing the document...", { id: "analyze" });
      await api.post(`/documents/${docId}/analyze`);
      toast.success("Document analyzed!", { id: "analyze" });
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Analysis failed", { id: "analyze" });
    }
  };

  const handleGenerateTests = async (docId) => {
    try {
      toast.loading("AI is generating test cases...", { id: "generate" });
      const res = await api.post("/testcases/generate", {
        document_id: docId,
        include_positive: true,
        include_negative: true,
        include_edge: true,
      });
      toast.success(`Generated ${res.data.total_generated} test cases!`, { id: "generate" });
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Generation failed", { id: "generate" });
    }
  };

  const handleUpdateStatus = async (tcId, newStatus) => {
    try {
      await api.put(`/testcases/${tcId}`, { status: newStatus });
      toast.success(`Test case ${newStatus}`);
      fetchData();
    } catch (err) {
      toast.error("Failed to update status");
    }
  };

  const handleExport = async () => {
    try {
      const res = await api.get(`/testcases/export?project_id=${projectId}&format=csv`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `testcases_project_${projectId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success("Exported!");
    } catch {
      toast.error("Export failed");
    }
  };

  if (loading) return <Loader />;
  if (!project) return <EmptyState title="Project not found" />;

  return (
    <div className="space-y-6">
      {/* Project Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
          <p className="text-gray-500 mt-1">{project.description || "No description"}</p>
        </div>
        <div className="flex gap-3">
          <label>
            <input type="file" accept=".pdf,.docx,.md,.txt" onChange={handleUpload} className="hidden" />
            <Button icon={Upload} loading={uploading} onClick={() => {}} className="cursor-pointer" as="span">
              Upload Document
            </Button>
          </label>
          {testCases.length > 0 && (
            <Button variant="outline" icon={Download} onClick={handleExport}>
              Export CSV
            </Button>
          )}
        </div>
      </div>

      {/* Documents Section */}
      <Card>
        <CardHeader>
          <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            Documents ({documents.length})
          </h2>
        </CardHeader>
        <CardBody>
          {documents.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No documents uploaded yet. Upload a PDF, DOCX, MD, or TXT file.</p>
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                      <p className="text-xs text-gray-500">{doc.file_type?.toUpperCase()} &middot; {formatDate(doc.created_at)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={doc.status} />
                    {doc.status === "uploaded" && (
                      <Button size="sm" variant="outline" icon={Sparkles} onClick={() => handleAnalyze(doc.id)}>
                        Analyze
                      </Button>
                    )}
                    {doc.status === "analyzed" && (
                      <Button size="sm" icon={ClipboardCheck} onClick={() => handleGenerateTests(doc.id)}>
                        Generate Tests
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Test Cases Section */}
      <Card>
        <CardHeader>
          <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
            <ClipboardCheck className="w-5 h-5 text-emerald-600" />
            Test Cases ({testCases.length})
          </h2>
        </CardHeader>
        <CardBody>
          {testCases.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No test cases generated yet. Upload and analyze a document first.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b border-gray-100">
                    <th className="pb-3 font-medium">ID</th>
                    <th className="pb-3 font-medium">Scenario</th>
                    <th className="pb-3 font-medium">Type</th>
                    <th className="pb-3 font-medium">Status</th>
                    <th className="pb-3 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {testCases.map((tc) => (
                    <tr key={tc.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setShowTestCase(tc)}>
                      <td className="py-3 font-mono text-xs text-gray-500">{tc.test_case_id}</td>
                      <td className="py-3 text-gray-900">{truncateText(tc.scenario, 60)}</td>
                      <td className="py-3"><StatusBadge status={tc.case_type} /></td>
                      <td className="py-3"><StatusBadge status={tc.status} /></td>
                      <td className="py-3 text-right">
                        <div className="flex gap-1 justify-end" onClick={(e) => e.stopPropagation()}>
                          {tc.status === "draft" && (
                            <>
                              <Button size="sm" variant="success" onClick={() => handleUpdateStatus(tc.id, "approved")}>
                                Approve
                              </Button>
                              <Button size="sm" variant="danger" onClick={() => handleUpdateStatus(tc.id, "rejected")}>
                                Reject
                              </Button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Test Case Detail Modal */}
      <Modal isOpen={!!showTestCase} onClose={() => setShowTestCase(null)} title={showTestCase?.test_case_id || ""} size="lg">
        {showTestCase && (
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-500">Scenario</h4>
              <p className="text-gray-900 mt-1">{showTestCase.scenario}</p>
            </div>
            {showTestCase.preconditions && (
              <div>
                <h4 className="text-sm font-medium text-gray-500">Preconditions</h4>
                <p className="text-gray-900 mt-1">{showTestCase.preconditions}</p>
              </div>
            )}
            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-2">Test Steps</h4>
              <div className="space-y-2">
                {showTestCase.test_steps?.map((step, i) => (
                  <div key={i} className="flex gap-3 p-3 bg-gray-50 rounded-lg">
                    <span className="w-6 h-6 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-xs font-bold shrink-0">
                      {step.step_number || i + 1}
                    </span>
                    <div>
                      <p className="text-sm text-gray-900">{step.action}</p>
                      <p className="text-xs text-gray-500 mt-0.5">Expected: {step.expected}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-500">Expected Result</h4>
              <p className="text-gray-900 mt-1">{showTestCase.expected_result}</p>
            </div>
            <div className="flex gap-2">
              <StatusBadge status={showTestCase.case_type} />
              <StatusBadge status={showTestCase.status} />
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

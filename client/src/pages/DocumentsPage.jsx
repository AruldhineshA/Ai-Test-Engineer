/**
 * Documents page — View all documents across projects.
 */

import { useEffect, useState } from "react";
import { FileText } from "lucide-react";
import { Card, CardBody } from "../components/common/Card";
import { StatusBadge } from "../components/common/StatusBadge";
import { EmptyState } from "../components/common/EmptyState";
import { Loader } from "../components/common/Loader";
import { formatDate } from "../utils/formatters";
import api from "../utils/api";

export function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/documents/")
      .then((res) => setDocuments(Array.isArray(res.data) ? res.data : []))
      .catch(() => setDocuments([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
        <p className="text-gray-500 mt-1">All uploaded documents across your projects.</p>
      </div>

      {documents.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No documents yet"
          description="Upload documents from within a project to get started."
        />
      ) : (
        <div className="grid gap-3">
          {documents.map((doc) => (
            <Card key={doc.id}>
              <CardBody className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                    <p className="text-xs text-gray-500">
                      {doc.file_type?.toUpperCase()} &middot; Project #{doc.project_id} &middot; {formatDate(doc.created_at)}
                    </p>
                  </div>
                </div>
                <StatusBadge status={doc.status} />
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Projects page — List, create, and manage projects.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, FolderKanban } from "lucide-react";
import { Card, CardBody } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Input } from "../components/common/Input";
import { Modal } from "../components/common/Modal";
import { EmptyState } from "../components/common/EmptyState";
import { Loader } from "../components/common/Loader";
import { useProjects } from "../hooks/useProjects";
import { formatDate } from "../utils/formatters";
import toast from "react-hot-toast";

export function ProjectsPage() {
  const { projects, loading, createProject } = useProjects();
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      const project = await createProject(name, description);
      toast.success(`Project "${project.name}" created!`);
      setShowModal(false);
      setName("");
      setDescription("");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <Loader />;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-500 mt-1">{projects.length} project{projects.length !== 1 ? "s" : ""}</p>
        </div>
        <Button icon={Plus} onClick={() => setShowModal(true)}>
          New Project
        </Button>
      </div>

      {/* Project Grid */}
      {projects.length === 0 ? (
        <EmptyState
          icon={FolderKanban}
          title="No projects yet"
          description="Create your first project to start generating AI test cases."
          actionLabel="Create Project"
          onAction={() => setShowModal(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <Card
              key={project.id}
              hoverable
              onClick={() => navigate(`/projects/${project.id}`)}
            >
              <CardBody>
                <div className="flex items-start justify-between">
                  <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                    <FolderKanban className="w-5 h-5 text-indigo-600" />
                  </div>
                </div>
                <h3 className="text-base font-semibold text-gray-900 mt-3">{project.name}</h3>
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                  {project.description || "No description"}
                </p>
                <p className="text-xs text-gray-400 mt-3">{formatDate(project.created_at)}</p>
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Create New Project">
        <form onSubmit={handleCreate} className="space-y-4">
          <Input
            label="Project Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Login Module Testing"
            required
          />
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What will you be testing?"
              rows={3}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div className="flex gap-3 justify-end pt-2">
            <Button variant="secondary" onClick={() => setShowModal(false)}>Cancel</Button>
            <Button type="submit" loading={creating}>Create Project</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

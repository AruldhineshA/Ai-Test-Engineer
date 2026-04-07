/**
 * Dashboard — Overview with stats and quick actions.
 */

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FolderKanban, FileText, ClipboardCheck, Plus, ArrowRight } from "lucide-react";
import { Card, CardBody } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Loader } from "../components/common/Loader";
import { useAuth } from "../hooks/useAuth";
import api from "../utils/api";

export function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const projectsRes = await api.get("/projects/");
        setStats({
          projects: projectsRes.data.length,
          documents: 0,
          testCases: 0,
        });
      } catch {
        setStats({ projects: 0, documents: 0, testCases: 0 });
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <Loader />;

  const statCards = [
    { label: "Projects", value: stats.projects, icon: FolderKanban, color: "bg-indigo-500", path: "/projects" },
    { label: "Documents", value: stats.documents, icon: FileText, color: "bg-blue-500", path: "/documents" },
    { label: "Test Cases", value: stats.testCases, icon: ClipboardCheck, color: "bg-emerald-500", path: "/testcases" },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">
          Welcome back, {user?.full_name}. Here's your testing overview.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {statCards.map((stat) => (
          <Card key={stat.label} hoverable onClick={() => navigate(stat.path)}>
            <CardBody className="flex items-center gap-4">
              <div className={`w-12 h-12 ${stat.color} rounded-xl flex items-center justify-center`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-500">{stat.label}</p>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card hoverable onClick={() => navigate("/projects")}>
            <CardBody className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Plus className="w-5 h-5 text-indigo-600" />
                <span className="text-sm font-medium text-gray-700">Create New Project</span>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400" />
            </CardBody>
          </Card>

          <Card hoverable onClick={() => navigate("/documents")}>
            <CardBody className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-medium text-gray-700">Upload Document</span>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400" />
            </CardBody>
          </Card>

          <Card hoverable onClick={() => navigate("/testcases")}>
            <CardBody className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <ClipboardCheck className="w-5 h-5 text-emerald-600" />
                <span className="text-sm font-medium text-gray-700">View Test Cases</span>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400" />
            </CardBody>
          </Card>
        </div>
      </div>

      {/* Phase Info */}
      <Card>
        <CardBody>
          <h3 className="text-sm font-semibold text-gray-900 mb-3">How It Works</h3>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-xs font-bold">1</span>
              Create Project
            </div>
            <ArrowRight className="w-4 h-4 text-gray-300" />
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">2</span>
              Upload Document
            </div>
            <ArrowRight className="w-4 h-4 text-gray-300" />
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center text-xs font-bold">3</span>
              AI Analyzes
            </div>
            <ArrowRight className="w-4 h-4 text-gray-300" />
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center text-xs font-bold">4</span>
              Generate Test Cases
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}

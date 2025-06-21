"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Clock, 
  Play, 
  Square, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  Loader,
  Users,
  Search,
  Shield,
  AlertTriangle
} from "lucide-react";

interface Task {
  id: string;
  type: "ENSEMBLE" | "VALIDATION" | "RESEARCH" | "ANALYSIS";
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
  node_id: string;
  parameters: Record<string, unknown>;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress: number;
  result?: unknown;
  error?: string;
  estimated_duration: number;
  actual_duration?: number;
}

export default function TaskMonitor() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Mock data
  const mockTasks: Task[] = [
    {
      id: "task_001",
      type: "ENSEMBLE",
      status: "RUNNING",
      node_id: "node_quantum_1",
      parameters: { algorithm_id: "ai_knowledge_discovery", ensemble_size: 3 },
      created_at: "2024-01-10T10:25:00Z",
      started_at: "2024-01-10T10:26:00Z",
      progress: 67,
      estimated_duration: 300,
      actual_duration: 201
    },
    {
      id: "task_002",
      type: "VALIDATION",
      status: "COMPLETED",
      node_id: "node_ml_algorithms",
      parameters: { algorithm_id: "pattern_recognition", validation_type: "hybrid" },
      created_at: "2024-01-10T10:20:00Z",
      started_at: "2024-01-10T10:21:00Z",
      completed_at: "2024-01-10T10:24:00Z",
      progress: 100,
      estimated_duration: 180,
      actual_duration: 180,
      result: {
        validations: [
          { type: "knowledge_base", score: 0.92 },
          { type: "statistical", score: 0.85 },
          { type: "pattern", score: 0.89 }
        ]
      }
    },
    {
      id: "task_003",
      type: "RESEARCH",
      status: "FAILED",
      node_id: "node_cybersecurity",
      parameters: { algorithm_id: "risk_assessment", depth: 2 },
      created_at: "2024-01-10T10:15:00Z",
      started_at: "2024-01-10T10:16:00Z",
      completed_at: "2024-01-10T10:18:00Z",
      progress: 45,
      estimated_duration: 240,
      actual_duration: 120,
      error: "Algorithm execution failed: insufficient data quality"
    },
    {
      id: "task_004",
      type: "ANALYSIS",
      status: "PENDING",
      node_id: "node_data_structures",
      parameters: { algorithm_id: "complexity_analysis", max_depth: 5 },
      created_at: "2024-01-10T10:30:00Z",
      progress: 0,
      estimated_duration: 420
    },
    {
      id: "task_005",
      type: "ENSEMBLE",
      status: "RUNNING",
      node_id: "node_quantum_2",
      parameters: { algorithm_id: "quantum_optimization", ensemble_size: 5 },
      created_at: "2024-01-10T10:28:00Z",
      started_at: "2024-01-10T10:29:00Z",
      progress: 23,
      estimated_duration: 600,
      actual_duration: 90
    }
  ];

  useEffect(() => {
    setTasks(mockTasks);
    setSelectedTask(mockTasks[0]);
  }, []);

  const getStatusColor = (status: Task["status"]) => {
    switch (status) {
      case "PENDING": return "bg-gray-500";
      case "RUNNING": return "bg-blue-500";
      case "COMPLETED": return "bg-green-500";
      case "FAILED": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const getStatusIcon = (status: Task["status"]) => {
    switch (status) {
      case "PENDING": return <Clock className="h-4 w-4" />;
      case "RUNNING": return <Loader className="h-4 w-4 animate-spin" />;
      case "COMPLETED": return <CheckCircle className="h-4 w-4" />;
      case "FAILED": return <XCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const getTypeIcon = (type: Task["type"]) => {
    switch (type) {
      case "ENSEMBLE": return <Users className="h-4 w-4" />;
      case "VALIDATION": return <Shield className="h-4 w-4" />;
      case "RESEARCH": return <Search className="h-4 w-4" />;
      case "ANALYSIS": return <Play className="h-4 w-4" />;
      default: return <Play className="h-4 w-4" />;
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const refreshTasks = () => {
    setIsLoading(true);
    setTimeout(() => {
      setTasks([...mockTasks]);
      setIsLoading(false);
    }, 1000);
  };

  const cancelTask = (taskId: string) => {
    console.log(`Cancelling task ${taskId}`);
    // API call to cancel task
  };

  const runningTasks = tasks.filter(t => t.status === "RUNNING");
  const completedTasks = tasks.filter(t => t.status === "COMPLETED");
  const failedTasks = tasks.filter(t => t.status === "FAILED");
  const pendingTasks = tasks.filter(t => t.status === "PENDING");

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Task Monitor</h2>
          <p className="text-muted-foreground">Monitor background task execution</p>
        </div>
        <Button onClick={refreshTasks} disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Running</CardTitle>
            <Loader className="h-4 w-4 text-blue-500 animate-spin" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{runningTasks.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <Clock className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">{pendingTasks.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{completedTasks.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{failedTasks.length}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tasks List */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="all" className="space-y-4">
            <TabsList>
              <TabsTrigger value="all">All Tasks</TabsTrigger>
              <TabsTrigger value="running">Running</TabsTrigger>
              <TabsTrigger value="completed">Completed</TabsTrigger>
              <TabsTrigger value="failed">Failed</TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="space-y-4">
              <ScrollArea className="h-96">
                {tasks.map((task) => (
                  <Card 
                    key={task.id} 
                    className={`mb-4 cursor-pointer transition-colors ${selectedTask?.id === task.id ? 'ring-2 ring-primary' : ''}`}
                    onClick={() => setSelectedTask(task)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`h-3 w-3 rounded-full ${getStatusColor(task.status)} ${task.status === 'RUNNING' ? 'animate-pulse' : ''}`} />
                          <div className="flex items-center space-x-2">
                            {getTypeIcon(task.type)}
                            <CardTitle className="text-lg">{task.type}</CardTitle>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(task.status)}
                          <Badge variant="outline">{task.status}</Badge>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm font-medium">Node ID</p>
                          <p className="text-sm text-muted-foreground">{task.node_id}</p>
                        </div>

                        <div>
                          <p className="text-sm font-medium">Algorithm</p>
                          <p className="text-sm text-muted-foreground">{task.parameters.algorithm_id as string}</p>
                        </div>

                        {task.status === "RUNNING" && (
                          <div>
                            <div className="flex justify-between mb-2">
                              <span className="text-sm font-medium">Progress</span>
                              <span className="text-sm">{task.progress}%</span>
                            </div>
                            <Progress value={task.progress} />
                          </div>
                        )}

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                            <Clock className="h-4 w-4" />
                            <span>
                              {task.actual_duration 
                                ? `Duration: ${formatDuration(task.actual_duration)}` 
                                : `Est: ${formatDuration(task.estimated_duration)}`}
                            </span>
                          </div>
                          {task.status === "RUNNING" && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={(e) => {
                                e.stopPropagation();
                                cancelTask(task.id);
                              }}
                            >
                              <Square className="h-4 w-4 mr-2" />
                              Cancel
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </ScrollArea>
            </TabsContent>

            <TabsContent value="running">
              <ScrollArea className="h-96">
                {runningTasks.map((task) => (
                  <Card key={task.id} className="mb-4">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-2">
                          {getTypeIcon(task.type)}
                          <span className="font-medium">{task.type}</span>
                        </div>
                        <Badge variant="outline">{task.progress}%</Badge>
                      </div>
                      <Progress value={task.progress} />
                    </CardContent>
                  </Card>
                ))}
              </ScrollArea>
            </TabsContent>

            <TabsContent value="completed">
              <ScrollArea className="h-96">
                {completedTasks.map((task) => (
                  <Card key={task.id} className="mb-4">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          {getTypeIcon(task.type)}
                          <span className="font-medium">{task.type}</span>
                        </div>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">
                        Completed in {task.actual_duration ? formatDuration(task.actual_duration) : 'N/A'}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </ScrollArea>
            </TabsContent>

            <TabsContent value="failed">
              <ScrollArea className="h-96">
                {failedTasks.map((task) => (
                  <Card key={task.id} className="mb-4 border-red-200">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getTypeIcon(task.type)}
                          <span className="font-medium">{task.type}</span>
                        </div>
                        <XCircle className="h-4 w-4 text-red-500" />
                      </div>
                      {task.error && (
                        <div className="flex items-start space-x-2 mt-2">
                          <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-red-600">{task.error}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </div>

        {/* Task Details */}
        <div className="space-y-4">
          {selectedTask && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Task Details</CardTitle>
                  <CardDescription>{selectedTask.id}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Type</span>
                      <Badge variant="outline">{selectedTask.type}</Badge>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Status</span>
                      <Badge variant="outline">{selectedTask.status}</Badge>
                    </div>

                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Node</span>
                      <span className="text-sm">{selectedTask.node_id}</span>
                    </div>

                    <Separator />

                    <div>
                      <p className="text-sm font-medium mb-2">Parameters</p>
                      <div className="text-sm text-muted-foreground space-y-1">
                        {Object.entries(selectedTask.parameters).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span>{key}:</span>
                            <span>{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <p className="text-sm font-medium mb-2">Timing</p>
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div className="flex justify-between">
                          <span>Created:</span>
                          <span>{new Date(selectedTask.created_at).toLocaleTimeString()}</span>
                        </div>
                        {selectedTask.started_at && (
                          <div className="flex justify-between">
                            <span>Started:</span>
                            <span>{new Date(selectedTask.started_at).toLocaleTimeString()}</span>
                          </div>
                        )}
                        {selectedTask.completed_at && (
                          <div className="flex justify-between">
                            <span>Completed:</span>
                            <span>{new Date(selectedTask.completed_at).toLocaleTimeString()}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {selectedTask.result && (
                <Card>
                  <CardHeader>
                    <CardTitle>Results</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="text-sm bg-muted p-3 rounded overflow-auto">
                      {JSON.stringify(selectedTask.result, null, 2)}
                    </pre>
                  </CardContent>
                </Card>
              )}

              {selectedTask.error && (
                <Card className="border-red-200">
                  <CardHeader>
                    <CardTitle className="text-red-600">Error</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-red-600">{selectedTask.error}</p>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
} 
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Play,
  RefreshCw,
  Zap,
  Clock,
  CheckCircle,
  AlertCircle,
  Cpu,
  Database,
  Target
} from "lucide-react";

interface Algorithm {
  id: string;
  name: string;
  description: string;
  category: "knowledge_discovery" | "pattern_recognition" | "risk_assessment" | "optimization";
  parameters: Array<{
    name: string;
    type: "string" | "number" | "boolean" | "select";
    description: string;
    default?: unknown;
    options?: string[];
    required: boolean;
  }>;
  estimated_runtime: number;
  complexity: "LOW" | "MEDIUM" | "HIGH";
}

interface ExecutionResult {
  id: string;
  algorithm_id: string;
  node_id: string;
  status: "RUNNING" | "COMPLETED" | "FAILED";
  started_at: string;
  completed_at?: string;
    results?: unknown;
  error?: string;
  metrics: {
    execution_time: number;
    memory_usage: number;
    confidence: number;
  };
}

export default function AlgorithmRunner() {
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([]);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<Algorithm | null>(null);
  const [executions, setExecutions] = useState<ExecutionResult[]>([]);
  const [parameters, setParameters] = useState<Record<string, unknown>>({});
  const [selectedNodeId, setSelectedNodeId] = useState<string>("");
  const [isExecuting, setIsExecuting] = useState(false);
  const [activeTab, setActiveTab] = useState<string>("run");

  // Mock algorithms data
  const mockAlgorithms: Algorithm[] = [
    {
      id: "ai_knowledge_discovery",
      name: "AI Knowledge Discovery",
      description: "Discover hidden patterns and connections in knowledge graphs using advanced AI techniques",
      category: "knowledge_discovery",
      parameters: [
        {
          name: "max_depth",
          type: "number",
          description: "Maximum search depth for pattern discovery",
          default: 3,
          required: true
        },
        {
          name: "confidence_threshold",
          type: "number",
          description: "Minimum confidence threshold for discovered patterns",
          default: 0.7,
          required: true
        },
        {
          name: "algorithm_variant",
          type: "select",
          description: "Algorithm variant to use",
          options: ["standard", "enhanced", "experimental"],
          default: "standard",
          required: true
        }
      ],
      estimated_runtime: 120,
      complexity: "HIGH"
    },
    {
      id: "pattern_recognition",
      name: "Pattern Recognition",
      description: "Identify recurring patterns and anomalies in knowledge structures",
      category: "pattern_recognition",
      parameters: [
        {
          name: "pattern_type",
          type: "select",
          description: "Type of patterns to search for",
          options: ["structural", "temporal", "semantic", "hybrid"],
          default: "hybrid",
          required: true
        },
        {
          name: "sensitivity",
          type: "number",
          description: "Pattern detection sensitivity (0.1-1.0)",
          default: 0.8,
          required: true
        }
      ],
      estimated_runtime: 60,
      complexity: "MEDIUM"
    },
    {
      id: "risk_assessment",
      name: "Risk Assessment",
      description: "Evaluate potential risks and vulnerabilities in knowledge domains",
      category: "risk_assessment",
      parameters: [
        {
          name: "risk_categories",
          type: "select",
          description: "Categories of risks to assess",
          options: ["technical", "operational", "strategic", "all"],
          default: "all",
          required: true
        },
        {
          name: "include_mitigation",
          type: "boolean",
          description: "Include mitigation strategies in results",
          default: true,
          required: false
        }
      ],
      estimated_runtime: 90,
      complexity: "MEDIUM"
    },
    {
      id: "quantum_optimization",
      name: "Quantum Optimization",
      description: "Optimize knowledge graph structures using quantum-inspired algorithms",
      category: "optimization",
      parameters: [
        {
          name: "optimization_target",
          type: "select",
          description: "Target for optimization",
          options: ["connectivity", "efficiency", "reliability", "all"],
          default: "all",
          required: true
        },
        {
          name: "iterations",
          type: "number",
          description: "Number of optimization iterations",
          default: 100,
          required: true
        }
      ],
      estimated_runtime: 180,
      complexity: "HIGH"
    }
  ];

  // Mock execution results
  const mockExecutions: ExecutionResult[] = [
    {
      id: "exec_001",
      algorithm_id: "ai_knowledge_discovery",
      node_id: "node_quantum_1",
      status: "COMPLETED",
      started_at: "2024-01-10T10:30:00Z",
      completed_at: "2024-01-10T10:32:15Z",
      results: {
        patterns_discovered: 12,
        confidence_scores: [0.89, 0.76, 0.82, 0.94],
        connections_found: 8,
        recommendations: [
          "Strengthen connection to quantum entanglement concepts",
          "Explore relationship with error correction methods"
        ]
      },
      metrics: {
        execution_time: 135,
        memory_usage: 1.2,
        confidence: 0.87
      }
    },
    {
      id: "exec_002",
      algorithm_id: "pattern_recognition",
      node_id: "node_ml_algorithms",
      status: "RUNNING",
      started_at: "2024-01-10T10:35:00Z",
      metrics: {
        execution_time: 45,
        memory_usage: 0.8,
        confidence: 0.72
      }
    },
    {
      id: "exec_003",
      algorithm_id: "risk_assessment",
      node_id: "node_cybersecurity",
      status: "FAILED",
      started_at: "2024-01-10T10:28:00Z",
      completed_at: "2024-01-10T10:29:30Z",
      error: "Insufficient data quality for reliable risk assessment",
      metrics: {
        execution_time: 90,
        memory_usage: 0.5,
        confidence: 0.23
      }
    }
  ];

  useEffect(() => {
    setAlgorithms(mockAlgorithms);
    setExecutions(mockExecutions);
    setSelectedAlgorithm(mockAlgorithms[0]);
  }, []);

  useEffect(() => {
    if (selectedAlgorithm) {
      const defaultParams: Record<string, unknown> = {};
      selectedAlgorithm.parameters.forEach(param => {
        defaultParams[param.name] = param.default;
      });
      setParameters(defaultParams);
    }
  }, [selectedAlgorithm]);

  const handleParameterChange = (paramName: string, value: unknown) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const executeAlgorithm = async () => {
    if (!selectedAlgorithm || !selectedNodeId) return;

    setIsExecuting(true);

    // Simulate API call
    const newExecution: ExecutionResult = {
      id: `exec_${Date.now()}`,
      algorithm_id: selectedAlgorithm.id,
      node_id: selectedNodeId,
      status: "RUNNING",
      started_at: new Date().toISOString(),
      metrics: {
        execution_time: 0,
        memory_usage: 0,
        confidence: 0
      }
    };

    setExecutions(prev => [newExecution, ...prev]);

    // Simulate execution time
    setTimeout(() => {
      setExecutions(prev => prev.map(exec =>
        exec.id === newExecution.id
          ? {
            ...exec,
            status: "COMPLETED" as const,
            completed_at: new Date().toISOString(),
            results: {
              message: "Algorithm executed successfully",
              parameters_used: parameters
            },
            metrics: {
              execution_time: selectedAlgorithm.estimated_runtime,
              memory_usage: Math.random() * 2,
              confidence: 0.75 + Math.random() * 0.25
            }
          }
          : exec
      ));
      setIsExecuting(false);
    }, 3000);
  };    

  const getStatusIcon = (status: ExecutionResult["status"]) => {
    switch (status) {
      case "RUNNING": return <Clock className="h-4 w-4 text-blue-500 animate-spin" />;
      case "COMPLETED": return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "FAILED": return <AlertCircle className="h-4 w-4 text-red-500" />;
      default: return null;
    }
  };

  const getCategoryIcon = (category: Algorithm["category"]) => {
    switch (category) {
      case "knowledge_discovery": return <Database className="h-4 w-4" />;
      case "pattern_recognition": return <Target className="h-4 w-4" />;
      case "risk_assessment": return <AlertCircle className="h-4 w-4" />;
      case "optimization": return <Zap className="h-4 w-4" />;
      default: return null;
    }
  };

  const getComplexityColor = (complexity: Algorithm["complexity"]) => {
    switch (complexity) {
      case "LOW": return "bg-green-100 text-green-800";
      case "MEDIUM": return "bg-yellow-100 text-yellow-800";
      case "HIGH": return "bg-red-100 text-red-800";
      default: return "";
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Algorithm Runner</h2>
          <p className="text-muted-foreground">Execute algorithms on knowledge nodes</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="run" className="flex items-center space-x-2">
            <Play className="h-4 w-4 mr-1" />
            <span>Run Algorithm</span>
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center space-x-2">
            <Clock className="h-4 w-4 mr-1" />
            <span>Execution History</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="run">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Algorithm Selection & Configuration */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Algorithm Selection</CardTitle>
                  <CardDescription>Choose and configure an algorithm to run</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Algorithm</label>
                    <Select
                      value={selectedAlgorithm?.id || ""}
                      onValueChange={(value) => {
                        const algo = algorithms.find(a => a.id === value);
                        setSelectedAlgorithm(algo || null);
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select an algorithm" />
                      </SelectTrigger>
                      <SelectContent>
                        {algorithms.map((algorithm) => (
                          <SelectItem key={algorithm.id} value={algorithm.id}>
                            <div className="flex items-center space-x-2">
                              {getCategoryIcon(algorithm.category)}
                              <span>{algorithm.name}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {selectedAlgorithm && (
                    <div>
                      <div className="p-3 bg-muted rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{selectedAlgorithm.name}</h4>
                          <Badge className={getComplexityColor(selectedAlgorithm.complexity)}>
                            {selectedAlgorithm.complexity}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{selectedAlgorithm.description}</p>
                        <div className="flex items-center space-x-4 mt-2 text-sm text-muted-foreground">
                          <div className="flex items-center space-x-1">
                            <Clock className="h-4 w-4" />
                            <span>~{selectedAlgorithm.estimated_runtime}s</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Cpu className="h-4 w-4" />
                            <span>{selectedAlgorithm.category.replace("_", " ")}</span>
                          </div>
                        </div>
                      </div>

                      <div>
                        <label className="text-sm font-medium mb-2 block">Target Node ID</label>
                        <Input
                          placeholder="Enter node ID (e.g., node_quantum_1)"
                          value={selectedNodeId}
                          onChange={(e) => setSelectedNodeId(e.target.value)}
                        />
                      </div>

                      <Separator />

                      <div> 
                        <h4 className="font-medium mb-3">Parameters</h4>
                        <div className="space-y-3">
                          {selectedAlgorithm.parameters.map((param) => (
                            <div key={param.name}>
                              <label className="text-sm font-medium mb-1 block capitalize">
                                {param.name.replace("_", " ")}
                                {param.required && <span className="text-red-500 ml-1">*</span>}
                              </label>
                              <p className="text-xs text-muted-foreground mb-2">{param.description}</p>

                              {param.type === "select" && param.options ? (
                                <Select
                                  value={(parameters[param.name] || param.default || "") as string}
                                  onValueChange={(value) => handleParameterChange(param.name, value)}
                                >
                                  <SelectTrigger>
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {param.options.map((option) => (
                                      <SelectItem key={option} value={option}>
                                        {option}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              ) : param.type === "boolean" ? (
                                <Select
                                  value={parameters[param.name]?.toString() || param.default?.toString()}
                                  onValueChange={(value) => handleParameterChange(param.name, value === "true")}
                                >
                                  <SelectTrigger>
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="true">True</SelectItem>
                                    <SelectItem value="false">False</SelectItem>
                                  </SelectContent>
                                </Select>
                              ) : (
                                <Input
                                  type={param.type === "number" ? "number" : "text"}
                                  value={(parameters[param.name] || param.default || "") as string}
                                  onChange={(e) => handleParameterChange(param.name, param.type === "number" ? parseFloat(e.target.value) : e.target.value)}
                                />
                              )}
                            </div>
                          ))}
                        </div>
                      </div>

                      <Button
                        onClick={executeAlgorithm}
                        disabled={isExecuting || !selectedNodeId}
                        className="w-full"
                      >
                        {isExecuting ? (
                          <>
                            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                            Executing...
                          </>
                        ) : (
                          <>
                            <Play className="h-4 w-4 mr-2" />
                            Execute Algorithm
                          </>
                        )}
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Execution History & Results (in run tab, for quick reference) */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Execution History</CardTitle>
                  <CardDescription>Recent algorithm executions and results</CardDescription>
                </CardHeader>   
                <CardContent>
                  <ScrollArea className="h-96">
                    <div className="space-y-4">
                      {executions.map((execution) => (
                        <div key={execution.id} className="p-3 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(execution.status as ExecutionResult["status"])}
                              <span className="font-medium">
                                {algorithms.find(a => a.id === execution.algorithm_id)?.name}
                              </span>
                            </div>
                            <Badge variant="outline">{execution.status}</Badge>
                          </div>

                          <div className="text-sm text-muted-foreground space-y-1">
                            <div className="flex justify-between">
                              <span>Node:</span>
                              <span>{execution.node_id}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Started:</span>
                              <span>{new Date(execution.started_at).toLocaleTimeString()}</span>
                            </div>
                            {execution.completed_at && (
                              <div className="flex justify-between">
                                <span>Duration:</span>
                                <span>{execution.metrics.execution_time}s</span>
                              </div>
                            )}
                            <div className="flex justify-between">
                              <span>Confidence:</span>
                              <Badge variant="outline">{(execution.metrics.confidence * 100).toFixed(0)}%</Badge>
                            </div>
                          </div>

                          {execution.error && (
                            <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-600">
                              {execution.error}
                            </div>
                          )}    

                          <div className="mt-2">
                            <pre className="mt-2 text-xs bg-muted p-2 rounded overflow-auto">
                              {JSON.stringify(execution.results, null, 2)}
                            </pre>
                          </div>    
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Execution History</CardTitle>
              <CardDescription>Recent algorithm executions and results</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-4">
                  {executions.map((execution) => (
                    <div key={execution.id} className="p-3 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(execution.status)}
                          <span className="font-medium">    
                            {algorithms.find(a => a.id === execution.algorithm_id)?.name}
                          </span>
                        </div>
                        <Badge variant="outline">{execution.status}</Badge>
                      </div>

                      <div className="text-sm text-muted-foreground space-y-1">
                        <div className="flex justify-between">
                          <span>Node:</span>
                          <span>{execution.node_id}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Started:</span>
                          <span>{new Date(execution.started_at).toLocaleTimeString()}</span>
                        </div>
                        {execution.completed_at && (
                          <div className="flex justify-between">
                            <span>Duration:</span>
                            <span>{execution.metrics.execution_time}s</span>
                          </div>
                        )}
                        <div className="flex justify-between">
                          <span>Confidence:</span>
                          <Badge variant="outline">{(execution.metrics.confidence * 100).toFixed(0)}%</Badge>
                        </div>
                      </div>

                      {execution.error && (
                        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-600">
                          {execution.error}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
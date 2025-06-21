"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient, PersonaAgent } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Bot, 
  Play, 
  Pause, 
  Square, 
  RefreshCw, 
  Activity, 
  Brain,
  Clock,
  AlertCircle,
  CheckCircle
} from "lucide-react";

export default function AgentDashboard() {
  const [agents, setAgents] = useState<PersonaAgent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<PersonaAgent | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const mockAgents: PersonaAgent[] = [
    {
      id: "agent_1",
      name: "Quantum Analysis Agent",
      state: "PROCESSING",
      current_task: "Knowledge Discovery on Quantum Computing",
      success_rate: 92.5,
      total_processed: 847,
      last_activity: "2 minutes ago",
      confidence: 0.87,
      domain_coverage: ["PL19", "PL23", "PL11"],
      algorithms_available: ["ai_knowledge_discovery", "quantum_analysis"],
      learning_trace: [
        { timestamp: "2024-01-10T10:30:00Z", action: "Started quantum node analysis", confidence: 0.8 },
        { timestamp: "2024-01-10T10:31:00Z", action: "Applied knowledge discovery algorithm", confidence: 0.85 },
        { timestamp: "2024-01-10T10:32:00Z", action: "Gap detected - missing required axis", confidence: 0.7 },
        { timestamp: "2024-01-10T10:33:00Z", action: "Attempted axis imputation", confidence: 0.87 }
      ]
    },
    {
      id: "agent_2",
      name: "ML Pattern Recognition Agent",
      state: "IDLE",
      success_rate: 89.2,
      total_processed: 1203,
      last_activity: "15 minutes ago",
      confidence: 0.91,
      domain_coverage: ["PL13", "PL85", "PL02"],
      algorithms_available: ["pattern_recognition", "ai_knowledge_discovery"],
      learning_trace: [
        { timestamp: "2024-01-10T10:15:00Z", action: "Completed pattern analysis", confidence: 0.91 },
        { timestamp: "2024-01-10T10:16:00Z", action: "Updated knowledge base", confidence: 0.88 }
      ]
    },
    {
      id: "agent_3",
      name: "Security Assessment Agent",
      state: "ERROR",
      current_task: "Risk Assessment Failed",
      success_rate: 76.8,
      total_processed: 432,
      last_activity: "5 minutes ago",
      confidence: 0.45,
      domain_coverage: ["PL16", "PL78", "PL80"],
      algorithms_available: ["risk_assessment", "security_analysis"],
      learning_trace: [
        { timestamp: "2024-01-10T10:25:00Z", action: "Algorithm execution failed", confidence: 0.3 },
        { timestamp: "2024-01-10T10:26:00Z", action: "Attempting alternate algorithm", confidence: 0.45 },
        { timestamp: "2024-01-10T10:27:00Z", action: "Escalating to peer agent", confidence: 0.6 }
      ]
    },
    {
      id: "agent_4",
      name: "Data Structure Optimizer",
      state: "LEARNING",
      current_task: "Ensemble reasoning with peer agents",
      success_rate: 94.1,
      total_processed: 1589,
      last_activity: "1 minute ago",
      confidence: 0.78,
      domain_coverage: ["PL11", "PL14", "PL83"],
      algorithms_available: ["optimization", "ensemble_reasoning"],
      learning_trace: [
        { timestamp: "2024-01-10T10:29:00Z", action: "Started ensemble reasoning", confidence: 0.75 },
        { timestamp: "2024-01-10T10:30:00Z", action: "Collecting peer responses", confidence: 0.78 }
      ]
    }
  ];    

  useEffect(() => {
    setAgents(mockAgents);
    setSelectedAgent(mockAgents[0]);
  }, []);

  const getStateColor = (state: PersonaAgent["state"]) => {
    switch (state) {
      case "PROCESSING": return "bg-blue-500";
      case "IDLE": return "bg-green-500";
      case "ERROR": return "bg-red-500";
      case "LEARNING": return "bg-yellow-500";
      default: return "bg-gray-500";
    }
  };

  const getStateIcon = (state: PersonaAgent["state"]) => {
    switch (state) {
      case "PROCESSING": return <Activity className="h-4 w-4" />;
      case "IDLE": return <CheckCircle className="h-4 w-4" />;
      case "ERROR": return <AlertCircle className="h-4 w-4" />;
      case "LEARNING": return <Brain className="h-4 w-4" />;
      default: return <Bot className="h-4 w-4" />;
    }
  };

  const handleAgentAction = async (agentId: string, action: "start" | "pause" | "stop") => {
    setIsLoading(true);
    try {
      if (action === "start") {
        await apiClient.startAgent(agentId);
      } else if (action === "stop") {
        await apiClient.stopAgent(agentId);
      }
      await refreshAgents();
    } catch (error) {
      console.error(`Failed to ${action} agent:`, error);
    }
    setIsLoading(false);
  };    

  const refreshAgents = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.getAgents();
      if (response.data) {
        setAgents(response.data);
        if (!selectedAgent && response.data.length > 0) {
          setSelectedAgent(response.data[0]);
        }
      } else {
        setAgents(mockAgents);
        setSelectedAgent(mockAgents[0]);
      }
    } catch (error) {
      console.error("Failed to fetch agents:", error);
      setAgents(mockAgents);
      setSelectedAgent(mockAgents[0]);
    }
    setIsLoading(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Agent Dashboard</h2>
          <p className="text-muted-foreground">Monitor and control AI agents</p>
        </div>
        <Button onClick={refreshAgents} disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {agents.map((agent) => (
            <Card 
              key={agent.id} 
              className={`cursor-pointer transition-colors ${selectedAgent?.id === agent.id ? 'ring-2 ring-primary' : ''}`}
              onClick={() => setSelectedAgent(agent)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`h-3 w-3 rounded-full ${getStateColor(agent.state)} animate-pulse`} />
                    <div>
                      <CardTitle className="text-lg">{agent.name}</CardTitle>
                      <CardDescription>{agent.id}</CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStateIcon(agent.state)}
                    <Badge variant="outline">{agent.state}</Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {agent.current_task && (
                    <div>
                      <p className="text-sm font-medium">Current Task</p>
                      <p className="text-sm text-muted-foreground">{agent.current_task}</p>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm font-medium">Success Rate</p>
                      <p className="text-2xl font-bold text-green-600">{agent.success_rate || 0}%</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Processed</p>
                      <p className="text-2xl font-bold">{(agent.total_processed || 0).toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Confidence</p>
                      <p className="text-2xl font-bold text-blue-600">{((agent.confidence || 0) * 100).toFixed(0)}%</p>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Confidence Level</span>
                      <span className="text-sm text-muted-foreground">{((agent.confidence || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={(agent.confidence || 0) * 100} />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                      <Clock className="h-4 w-4" />
                      <span>Last activity: {agent.last_activity}</span>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAgentAction(agent.id, "start");
                        }}
                        disabled={agent.state === "PROCESSING"}
                      >
                        <Play className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAgentAction(agent.id, "pause");
                        }}
                        disabled={agent.state === "IDLE"}
                      >
                        <Pause className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAgentAction(agent.id, "stop");
                        }}
                      >
                        <Square className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Agent Details */}
        <div className="space-y-4">
          {selectedAgent && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Learning Trace</CardTitle>
                  <CardDescription>Recent agent actions and decisions</CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-64">
                    <div className="space-y-3">
                      {selectedAgent.learning_trace.map((trace, index) => (
                        <div key={index} className="flex items-start space-x-3">
                          <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                          <div className="flex-1">
                            <p className="text-sm">{trace.action}</p>
                            <div className="flex items-center justify-between mt-1">
                              <p className="text-xs text-muted-foreground">
                                {new Date(trace.timestamp).toLocaleTimeString()}
                              </p>
                              <Badge variant="outline" className="text-xs">
                                {(trace.confidence * 100).toFixed(0)}%
                              </Badge>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">Success Rate</span>
                        <span className="text-sm">{selectedAgent.success_rate || 0}%</span>
                      </div>
                      <Progress value={selectedAgent.success_rate || 0} />
                    </div>
                    
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">Current Confidence</span>
                        <span className="text-sm">{((selectedAgent.confidence || 0) * 100).toFixed(1)}%</span>
                      </div>
                      <Progress value={(selectedAgent.confidence || 0) * 100} />
                    </div>

                    <Separator />

                    <div className="flex justify-between">
                      <span className="text-sm">Total Processed</span>
                      <span className="font-medium">{(selectedAgent.total_processed || 0).toLocaleString()}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm">Status</span>
                      <Badge variant="outline">{selectedAgent.state}</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
} 
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { 
  Brain, 
  Network, 
  Bot, 
  Activity, 
  Settings, 
  Play, 
  TrendingUp,
  Users,
  Database,
  Cpu
} from "lucide-react";

import KnowledgeGraphVisualizer from "@/components/knowledge-graph-visualizer";
import AgentDashboard from "@/components/agent-dashboard";
import TaskMonitor from "@/components/task-monitor";
import AlgorithmRunner from "@/components/algorithm-runner";
import { UKGAxesVisualizer } from "@/components/ukg-axes-visualizer";
import { PillarLevelsExplorer } from "@/components/pillar-levels-explorer";

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Brain className="h-8 w-8 text-primary" />
                <h1 className="text-2xl font-bold">AKF3</h1>
              </div>
              <Badge variant="secondary">v1.0.0</Badge>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                System Active
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* System Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Knowledge Nodes</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,247</div>
              <p className="text-xs text-muted-foreground">
                +12% from last week
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">8</div>
              <p className="text-xs text-muted-foreground">
                3 processing, 5 idle
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tasks Running</CardTitle>
              <Cpu className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">23</div>
              <p className="text-xs text-muted-foreground">
                15 queued, 8 active
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Load</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">67%</div>
              <Progress value={67} className="mt-2" />
            </CardContent>
          </Card>
        </div>

        {/* Main Dashboard Tabs */}
        <Tabs defaultValue="graph" className="space-y-4">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="graph" className="flex items-center space-x-2">
              <Network className="h-4 w-4" />
              <span>Knowledge Graph</span>
            </TabsTrigger>
            <TabsTrigger value="pillars" className="flex items-center space-x-2">
              <Database className="h-4 w-4" />
              <span>87 Pillars</span>
            </TabsTrigger>
            <TabsTrigger value="axes" className="flex items-center space-x-2">
              <Brain className="h-4 w-4" />
              <span>UKG Axes</span>
            </TabsTrigger>
            <TabsTrigger value="agents" className="flex items-center space-x-2">
              <Bot className="h-4 w-4" />
              <span>Agents</span>
            </TabsTrigger>
            <TabsTrigger value="algorithms" className="flex items-center space-x-2">
              <Play className="h-4 w-4" />
              <span>Algorithms</span>
            </TabsTrigger>
            <TabsTrigger value="tasks" className="flex items-center space-x-2">
              <Activity className="h-4 w-4" />
              <span>Tasks</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="graph" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Knowledge Graph Visualization</CardTitle>
                <CardDescription>
                  Interactive visualization of knowledge nodes and relationships
                </CardDescription>
              </CardHeader>
              <CardContent>
                <KnowledgeGraphVisualizer />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="pillars" className="space-y-4">
            <PillarLevelsExplorer />
          </TabsContent>

          <TabsContent value="axes" className="space-y-4">
            <UKGAxesVisualizer />
          </TabsContent>

          <TabsContent value="agents" className="space-y-4">
            <AgentDashboard />
          </TabsContent>

          <TabsContent value="algorithms" className="space-y-4">
            <AlgorithmRunner />
          </TabsContent>

          <TabsContent value="tasks" className="space-y-4">
            <TaskMonitor />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

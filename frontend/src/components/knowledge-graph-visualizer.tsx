"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import * as d3 from "d3";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  ZoomIn, 
  ZoomOut, 
  RefreshCw, 
  Download, 
  Filter, 
  Search, 
  Play, 
  Pause, 
  RotateCcw,
  Maximize2,
  Settings,
  Network,
  Brain,
  Zap
} from "lucide-react";
import { apiClient } from "@/lib/api";

interface KnowledgeNode extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  description?: string;
  pillar_level_id: string;
  axis_values: Record<string, number>;
  connections?: number;
  importance?: number;
  cluster?: string;
  color?: string;
  size?: number;
}

interface KnowledgeEdge extends d3.SimulationLinkDatum<KnowledgeNode> {
  id: string;
  source: string | KnowledgeNode;
  target: string | KnowledgeNode;
  weight: number;
  relationship_type: string;
  color?: string;
  opacity?: number;
}

interface GraphData {
  nodes: KnowledgeNode[];
  edges: KnowledgeEdge[];
}

interface SimulationControls {
  isRunning: boolean;
  strength: number;
  distance: number;
  charge: number;
}

const PILLAR_COLORS = {
  // Mathematics & Logic (PL01-PL10)
  PL01: "#FF6B6B", PL02: "#FF8E53", PL03: "#FF6B9D", PL04: "#C44569", PL05: "#F8B500",
  PL06: "#FF7675", PL07: "#FD79A8", PL08: "#E17055", PL09: "#A29BFE", PL10: "#6C5CE7",
  
  // Computer Science & Technology (PL11-PL20)
  PL11: "#74B9FF", PL12: "#0984E3", PL13: "#00B894", PL14: "#00CEC9", PL15: "#55A3FF",
  PL16: "#5F27CD", PL17: "#00D2D3", PL18: "#FF9FF3", PL19: "#54A0FF", PL20: "#2E86AB",
  
  // Physical Sciences (PL21-PL30)
  PL21: "#FD79A8", PL22: "#FDCB6E", PL23: "#6C5CE7", PL24: "#A29BFE", PL25: "#FD79A8",
  PL26: "#00B894", PL27: "#00CEC9", PL28: "#74B9FF", PL29: "#0984E3", PL30: "#6C5CE7",
  
  // Life Sciences (PL31-PL40)
  PL31: "#00B894", PL32: "#00CEC9", PL33: "#55EFC4", PL34: "#81ECEC", PL35: "#00B894",
  PL36: "#00CEC9", PL37: "#A29BFE", PL38: "#74B9FF", PL39: "#0984E3", PL40: "#00D2D3",
  
  // Social Sciences (PL41-PL50)
  PL41: "#FDCB6E", PL42: "#E17055", PL43: "#F39C12", PL44: "#E67E22", PL45: "#D35400",
  PL46: "#F39C12", PL47: "#E67E22", PL48: "#D35400", PL49: "#FDCB6E", PL50: "#E17055",
  
  // Humanities (PL51-PL60)
  PL51: "#A29BFE", PL52: "#6C5CE7", PL53: "#5F27CD", PL54: "#341F97", PL55: "#8E44AD",
  PL56: "#9B59B6", PL57: "#BB8FCE", PL58: "#D2B4DE", PL59: "#E8DAEF", PL60: "#F4ECF7",
  
  // Applied Sciences & Engineering (PL61-PL70)
  PL61: "#E17055", PL62: "#D63031", PL63: "#74B9FF", PL64: "#0984E3", PL65: "#00B894",
  PL66: "#00CEC9", PL67: "#FDCB6E", PL68: "#F39C12", PL69: "#E67E22", PL70: "#D35400",
  
  // Business & Management (PL71-PL77)
  PL71: "#F39C12", PL72: "#E67E22", PL73: "#D35400", PL74: "#DC7633", PL75: "#CA6F1E",
  PL76: "#BA4A00", PL77: "#A04000",
  
  // Law & Governance (PL78-PL82)
  PL78: "#5F27CD", PL79: "#341F97", PL80: "#2C3E50", PL81: "#34495E", PL82: "#566573",
  
  // Interdisciplinary & Emerging (PL83-PL87)
  PL83: "#FF6B6B", PL84: "#4ECDC4", PL85: "#45B7D1", PL86: "#96CEB4", PL87: "#FFEAA7"
};

export default function KnowledgeGraphVisualizer() {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<KnowledgeNode, KnowledgeEdge> | null>(null);
  
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [selectedNode, setSelectedNode] = useState<KnowledgeNode | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterPillar, setFilterPillar] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(false);
  const [simulationControls, setSimulationControls] = useState<SimulationControls>({
    isRunning: true,
    strength: -300,
    distance: 100,
    charge: -300
  });
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  
  // Load graph data from API
  const loadGraphData = useCallback(async () => {
    setIsLoading(true);
    try {
      // Load nodes and edges from API
      const [nodesResponse, edgesResponse] = await Promise.all([
        apiClient.getNodes(),
        apiClient.getEdges()
      ]);

      // Check if API responses have data
      if (!nodesResponse.data || !edgesResponse.data) {
        throw new Error('Failed to load graph data from API');
      }

      // Process nodes with enhanced data
      const processedNodes: KnowledgeNode[] = nodesResponse.data.map((node) => ({
        id: node.id,
        label: node.label,
        description: node.description,
        pillar_level_id: node.pillar_level_id,
        axis_values: node.axis_values as Record<string, number>,
        connections: 0, // Will be calculated
        importance: Math.random() * 0.5 + 0.5, // Mock importance
        cluster: node.pillar_level_id.substring(0, 3), // Group by pillar category
        color: PILLAR_COLORS[node.pillar_level_id as keyof typeof PILLAR_COLORS] || "#6B7280",
        size: 0, // Will be calculated based on connections
        x: Math.random() * dimensions.width,
        y: Math.random() * dimensions.height
      }));

      // Process edges
      const processedEdges: KnowledgeEdge[] = edgesResponse.data.map((edge) => ({
        id: edge.id,
        source: edge.source_node_id as string,
        target: edge.target_node_id as string,
        weight: edge.weight,
        relationship_type: edge.relationship_type,
        color: "#94A3B8",
        opacity: Math.max(0.3, edge.weight)
      }));

      // Calculate node connections and sizes
      processedNodes.forEach(node => {
        node.connections = processedEdges.filter(
          edge => edge.source === node.id || edge.target === node.id
        ).length;
        node.size = Math.max(8, Math.min(25, 8 + node.connections * 2));
      });

      setGraphData({ nodes: processedNodes, edges: processedEdges });
    } catch (error) {
      console.error("Failed to load graph data:", error);
      // Fallback to enhanced mock data
      setGraphData(generateMockData());
    } finally {
      setIsLoading(false);
    }
  }, [dimensions]);

  // Generate enhanced mock data
  const generateMockData = (): GraphData => {
    const mockNodes: KnowledgeNode[] = [
      {
        id: "quantum_computing",
        label: "Quantum Computing",
        description: "Fundamental principles of quantum computation and quantum algorithms",
        pillar_level_id: "PL01",
        axis_values: { complexity: 0.95, uncertainty: 0.8, novelty: 0.9, impact: 0.85 },
        connections: 0,
        importance: 0.9,
        cluster: "PL0",
        color: PILLAR_COLORS.PL01,
        size: 20
      },
      {
        id: "machine_learning",
        label: "Machine Learning",
        description: "Algorithms and statistical models for computer systems",
        pillar_level_id: "PL13",
        axis_values: { complexity: 0.8, uncertainty: 0.6, novelty: 0.7, impact: 0.9 },
        connections: 0,
        importance: 0.95,
        cluster: "PL1",
        color: PILLAR_COLORS.PL13,
        size: 22
      },
      {
        id: "neural_networks",
        label: "Neural Networks",
        description: "Artificial neural networks and deep learning architectures",
        pillar_level_id: "PL13",
        axis_values: { complexity: 0.85, uncertainty: 0.7, novelty: 0.8, impact: 0.85 },
        connections: 0,
        importance: 0.8,
        cluster: "PL1",
        color: PILLAR_COLORS.PL13,
        size: 18
      },
      {
        id: "cryptography",
        label: "Cryptography",
        description: "Mathematical techniques for secure communication",
        pillar_level_id: "PL01",
        axis_values: { complexity: 0.9, uncertainty: 0.4, novelty: 0.3, impact: 0.95 },
        connections: 0,
        importance: 0.85,
        cluster: "PL0",
        color: PILLAR_COLORS.PL01,
        size: 16
      },
      {
        id: "blockchain",
        label: "Blockchain Technology",
        description: "Distributed ledger technology and cryptocurrencies",
        pillar_level_id: "PL12",
        axis_values: { complexity: 0.7, uncertainty: 0.8, novelty: 0.9, impact: 0.7 },
        connections: 0,
        importance: 0.7,
        cluster: "PL1",
        color: PILLAR_COLORS.PL12,
        size: 15
      },
      {
        id: "bioinformatics",
        label: "Bioinformatics",
        description: "Computational analysis of biological data",
        pillar_level_id: "PL31",
        axis_values: { complexity: 0.8, uncertainty: 0.7, novelty: 0.6, impact: 0.8 },
        connections: 0,
        importance: 0.75,
        cluster: "PL3",
        color: PILLAR_COLORS.PL31,
        size: 17
      },
      {
        id: "robotics",
        label: "Robotics",
        description: "Design and operation of robots and autonomous systems",
        pillar_level_id: "PL61",
        axis_values: { complexity: 0.85, uncertainty: 0.6, novelty: 0.7, impact: 0.8 },
        connections: 0,
        importance: 0.8,
        cluster: "PL6",
        color: PILLAR_COLORS.PL61,
        size: 18
      },
      {
        id: "climate_science",
        label: "Climate Science",
        description: "Study of climate systems and environmental changes",
        pillar_level_id: "PL21",
        axis_values: { complexity: 0.9, uncertainty: 0.8, novelty: 0.5, impact: 0.95 },
        connections: 0,
        importance: 0.9,
        cluster: "PL2",
        color: PILLAR_COLORS.PL21,
        size: 19
      }
    ];

    const mockEdges: KnowledgeEdge[] = [
      {
        id: "edge_1",
        source: "quantum_computing",
        target: "cryptography",
        weight: 0.8,
        relationship_type: "enables",
        color: "#3B82F6",
        opacity: 0.8
      },
      {
        id: "edge_2",
        source: "machine_learning",
        target: "neural_networks",
        weight: 0.9,
        relationship_type: "includes",
        color: "#10B981",
        opacity: 0.9
      },
      {
        id: "edge_3",
        source: "machine_learning",
        target: "bioinformatics",
        weight: 0.7,
        relationship_type: "applies_to",
        color: "#F59E0B",
        opacity: 0.7
      },
      {
        id: "edge_4",
        source: "blockchain",
        target: "cryptography",
        weight: 0.6,
        relationship_type: "depends_on",
        color: "#EF4444",
        opacity: 0.6
      },
      {
        id: "edge_5",
        source: "robotics",
        target: "machine_learning",
        weight: 0.8,
        relationship_type: "utilizes",
        color: "#8B5CF6",
        opacity: 0.8
      },
      {
        id: "edge_6",
        source: "bioinformatics",
        target: "climate_science",
        weight: 0.5,
        relationship_type: "informs",
        color: "#06B6D4",
        opacity: 0.5
      }
    ];

    // Calculate connections for mock data
    mockNodes.forEach(node => {
      node.connections = mockEdges.filter(
        edge => edge.source === node.id || edge.target === node.id
      ).length;
    });

    return { nodes: mockNodes, edges: mockEdges };
  };

  // Initialize D3 force simulation
  const initializeSimulation = useCallback(() => {
    if (!svgRef.current || !graphData.nodes.length) return;

    const svg = d3.select(svgRef.current);
    const { width, height } = dimensions;

    // Clear previous simulation
    if (simulationRef.current) {
      simulationRef.current.stop();
    }

    // Create simulation
    const simulation = d3.forceSimulation<KnowledgeNode>(graphData.nodes)
      .force("link", d3.forceLink<KnowledgeNode, KnowledgeEdge>(graphData.edges)
        .id(d => d.id)
        .distance(d => simulationControls.distance * (1 / Math.max(0.1, d.weight)))
        .strength(0.1)
      )
      .force("charge", d3.forceManyBody().strength(simulationControls.charge))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(d => (d as KnowledgeNode).size || 10 + 2))
      .force("x", d3.forceX(width / 2).strength(0.05))
      .force("y", d3.forceY(height / 2).strength(0.05));

    simulationRef.current = simulation;

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        svg.select(".graph-container").attr("transform", event.transform);
      });

    svg.call(zoom);

    // Clear and setup SVG
    svg.selectAll("*").remove();
    
    // Add definitions for patterns and gradients
    const defs = svg.append("defs");
    
    // Add arrow markers for directed edges
    defs.append("marker")
      .attr("id", "arrowhead")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 15)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#666");

    const container = svg.append("g").attr("class", "graph-container");

    // Create edges
    const link = container.append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(graphData.edges)
      .enter().append("line")
      .attr("stroke", d => d.color || "#999")
      .attr("stroke-opacity", d => d.opacity || 0.6)
      .attr("stroke-width", d => Math.sqrt(d.weight * 3))
      .attr("marker-end", "url(#arrowhead)");

    // Create nodes
    const node = container.append("g")
      .attr("class", "nodes")
      .selectAll("g")
      .data(graphData.nodes)
      .enter().append("g")
      .attr("class", "node")
      .style("cursor", "pointer")
      .call(d3.drag<SVGGElement, KnowledgeNode>()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
      );

    // Add circles for nodes
    node.append("circle")
      .attr("r", d => d.size || 10)
      .attr("fill", d => d.color || "#69b3a2")
      .attr("stroke", "#fff")
      .attr("stroke-width", 2)
      .style("filter", "drop-shadow(2px 2px 4px rgba(0,0,0,0.3))")
      .on("click", (event, d) => {
        event.stopPropagation();
        setSelectedNode(d);
      })
      .on("mouseover", function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", (d.size || 10) * 1.2)
          .style("filter", "drop-shadow(3px 3px 6px rgba(0,0,0,0.5))");
      })
      .on("mouseout", function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", d.size || 10)
          .style("filter", "drop-shadow(2px 2px 4px rgba(0,0,0,0.3))");
      });

    // Add labels
    node.append("text")
      .text(d => d.label.length > 15 ? d.label.substring(0, 15) + "..." : d.label)
      .attr("font-size", "12px")
      .attr("font-family", "Inter, sans-serif")
      .attr("font-weight", "500")
      .attr("text-anchor", "middle")
      .attr("dy", d => (d.size || 10) + 16)
      .attr("fill", "#374151")
      .style("pointer-events", "none")
      .style("user-select", "none");

    // Update positions on simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", d => (d.source as KnowledgeNode).x || 0)
        .attr("y1", d => (d.source as KnowledgeNode).y || 0)
        .attr("x2", d => (d.target as KnowledgeNode).x || 0)
        .attr("y2", d => (d.target as KnowledgeNode).y || 0);

      node
        .attr("transform", d => `translate(${d.x || 0},${d.y || 0})`);
    });

    // Control simulation
    if (!simulationControls.isRunning) {
      simulation.stop();
    }

  }, [graphData, dimensions, simulationControls]);

  // Load data on component mount
  useEffect(() => {
    loadGraphData();
  }, [loadGraphData]);

  // Initialize simulation when data changes
  useEffect(() => {
    if (graphData.nodes.length > 0) {
      initializeSimulation();
    }
  }, [graphData, initializeSimulation]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      const container = document.getElementById("graph-container");
      if (container) {
        const rect = container.getBoundingClientRect();
        setDimensions({ width: rect.width, height: rect.height });
      }
    };

    window.addEventListener("resize", handleResize);
    handleResize();

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Filter nodes based on search and pillar filter
  const filteredNodes = graphData.nodes.filter(node => {
    const matchesSearch = searchTerm === "" || 
      node.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (node.description && node.description.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesPillar = filterPillar === "all" || 
      node.pillar_level_id === filterPillar ||
      node.cluster === filterPillar;

    return matchesSearch && matchesPillar;
  });

  // Control functions
  const handlePlayPause = () => {
    if (simulationRef.current) {
      if (simulationControls.isRunning) {
        simulationRef.current.stop();
      } else {
        simulationRef.current.restart();
      }
      setSimulationControls(prev => ({ ...prev, isRunning: !prev.isRunning }));
    }
  };

  const handleReset = () => {
    if (simulationRef.current) {
      simulationRef.current.alpha(1).restart();
    }
  };

  const handleZoomIn = () => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    svg.call(d3.zoom<SVGSVGElement, unknown>().scaleBy as any, 1.5);
  };

  const handleZoomOut = () => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    svg.call(d3.zoom<SVGSVGElement, unknown>().scaleBy as any, 1 / 1.5);
  };

  const handleZoomReset = () => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    svg.call(d3.zoom<SVGSVGElement, unknown>().transform as any, d3.zoomIdentity);
  };

  const exportGraph = () => {
    const svgElement = svgRef.current;
    if (!svgElement) return;

    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svgElement);
    const blob = new Blob([svgString], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement("a");
    link.href = url;
    link.download = "knowledge-graph.svg";
    link.click();
    
    URL.revokeObjectURL(url);
  };

  // Get unique pillar categories for filtering
  const pillarCategories = Array.from(new Set(graphData.nodes.map(n => n.cluster))).sort();

  return (
    <div className="space-y-4">
      {/* Enhanced Controls */} 
      <div className="flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handlePlayPause}
              className="flex items-center space-x-1"
            >
              {simulationControls.isRunning ? 
                <Pause className="h-4 w-4" /> : 
                <Play className="h-4 w-4" />
              }
              <span>{simulationControls.isRunning ? "Pause" : "Play"}</span>
            </Button>
            <Button variant="outline" size="sm" onClick={handleReset}>
              <RotateCcw className="h-4 w-4" />
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <Button variant="outline" size="sm" onClick={handleZoomIn}>
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={handleZoomOut}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={handleZoomReset}>
              <Maximize2 className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={loadGraphData} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
          <Button variant="outline" size="sm" onClick={exportGraph}>
            <Download className="h-4 w-4 mr-2" />
            Export SVG
          </Button>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 flex-1">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search nodes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-sm"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4" />
            <Select value={filterPillar} onValueChange={setFilterPillar}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {pillarCategories.map(category => (
                  <SelectItem key={category} value={category || ""}>
                    {category === "PL0" && "Mathematics & Logic"}
                    {category === "PL1" && "Computer Science"}
                    {category === "PL2" && "Physical Sciences"}
                    {category === "PL3" && "Life Sciences"}
                    {category === "PL4" && "Social Sciences"}
                    {category === "PL5" && "Humanities"}
                    {category === "PL6" && "Engineering"}
                    {category === "PL7" && "Business"}
                    {category === "PL8" && "Law & Governance"}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Main Graph Visualization */}
        <div className="lg:col-span-3">
          <Card className="overflow-hidden">
            <CardContent className="p-0">
              <div id="graph-container" className="relative">
                <svg
                  ref={svgRef}
                  width={dimensions.width}
                  height={dimensions.height}
                  className="w-full h-[600px] bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-blue-900"
                  style={{ minHeight: "600px" }}
                />
                {isLoading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-white/80 dark:bg-slate-900/80">
                    <div className="flex items-center space-x-2">
                      <RefreshCw className="h-6 w-6 animate-spin" />
                      <span>Loading knowledge graph...</span>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar with Details and Controls */}
        <div className="space-y-4">
          <Tabs defaultValue="details" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="details">Details</TabsTrigger>
              <TabsTrigger value="stats">Stats</TabsTrigger>
              <TabsTrigger value="controls">Controls</TabsTrigger>
            </TabsList>
            
            <TabsContent value="details">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center space-x-2">
                    <Brain className="h-5 w-5" />
                    <span>Node Details</span>
                  </CardTitle>
                  <CardDescription>
                    {selectedNode ? "Selected node information" : "Click a node to view details"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {selectedNode ? (
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold text-lg">{selectedNode.label}</h4>
                        <Badge 
                          variant="secondary" 
                          style={{ backgroundColor: selectedNode.color, color: "white" }}
                        >
                          {selectedNode.pillar_level_id}
                        </Badge>
                        {selectedNode.description && (
                          <p className="text-sm text-muted-foreground mt-2">
                            {selectedNode.description}
                          </p>
                        )}
                      </div>
                      <Separator />
                      <div>
                        <h5 className="font-medium mb-3 flex items-center space-x-2">
                          <Zap className="h-4 w-4" />
                          <span>Axis Values</span>
                        </h5>
                        <div className="space-y-3">
                          {Object.entries(selectedNode.axis_values).map(([axis, value]: [string, number]) => (
                            <div key={axis} className="space-y-1">
                              <div className="flex justify-between items-center">
                                <span className="capitalize text-sm font-medium">{axis}</span>
                                <Badge variant="outline">{(value * 100).toFixed(0)}%</Badge>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${value * 100}%` }}
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                      <Separator />
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Connections:</span>
                          <Badge variant="outline">{selectedNode.connections}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Importance:</span>
                          <Badge variant="outline">
                            {((selectedNode.importance || 0) * 100).toFixed(0)}%
                          </Badge>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Network className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground text-sm">
                        Select a node to view its properties and relationships.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="stats">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Graph Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">{filteredNodes.length}</div>
                        <div className="text-sm text-muted-foreground">Nodes</div>
                      </div>
                      <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">{graphData.edges.length}</div>
                        <div className="text-sm text-muted-foreground">Edges</div>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Avg Connections</span>
                        <Badge variant="outline">
                          {graphData.nodes.length > 0 ? 
                            (graphData.edges.length * 2 / graphData.nodes.length).toFixed(1) : 0}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Density</span>
                        <Badge variant="outline">
                          {graphData.nodes.length > 1 ? 
                            `${((graphData.edges.length * 2) / (graphData.nodes.length * (graphData.nodes.length - 1)) * 100).toFixed(1)}%` : "0%"}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Categories</span>
                        <Badge variant="outline">{pillarCategories.length}</Badge>
                      </div>
                    </div>

                    <Separator />
                    
                    <div>
                      <h6 className="font-medium mb-2">Top Connected Nodes</h6>
                      <div className="space-y-1">
                        {graphData.nodes
                          .sort((a: KnowledgeNode, b: KnowledgeNode) => (b.connections || 0) - (a.connections || 0))
                          .slice(0, 3)
                          .map((node: KnowledgeNode) => (
                            <div key={node.id} className="flex justify-between items-center text-sm">
                              <span className="truncate flex-1">{node.label}</span>
                              <Badge variant="outline" className="ml-2">
                                {node.connections}
                              </Badge>
                            </div>
                          ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="controls">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center space-x-2">
                    <Settings className="h-5 w-5" />
                    <span>Simulation Controls</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">Force Strength</label>
                      <input
                        title="Force Strength"
                        type="range"
                        min="-1000"
                        max="-50"
                        value={simulationControls.strength}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSimulationControls(prev => ({
                          ...prev,
                          strength: parseInt(e.target.value)
                        }))}
                        className="w-full mt-1"
                      />
                      <div className="text-xs text-muted-foreground mt-1">
                        {simulationControls.strength}
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium">Link Distance</label>
                      <input
                        title="Link Distance"
                        type="range"
                        min="50"
                        max="200"
                        value={simulationControls.distance}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSimulationControls(prev => ({
                          ...prev,
                          distance: parseInt(e.target.value)
                        }))}
                        className="w-full mt-1"
                      />
                      <div className="text-xs text-muted-foreground mt-1">
                        {simulationControls.distance}px
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Simulation</span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handlePlayPause}
                      >
                        {simulationControls.isRunning ? "Pause" : "Play"}
                      </Button>
                    </div>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleReset}
                      className="w-full"
                    >
                      Reset Layout
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
} 
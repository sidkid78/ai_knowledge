const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiResponse<T> {
  data?: T
  error?: string
  message?: string
}

export interface KnowledgeNode {
  id: string
  label: string
  description: string
  pillar_level_id: string
  axis_values: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface KnowledgeEdge {
  id: string
  source_node_id: string
  target_node_id: string
  relationship_type: string
  weight: number
  metadata: Record<string, unknown>
}

export interface PillarLevel {
  id: string
  name: string
  description: string
  parent_id?: string
  domain_type: string
  created_at: string
  updated_at: string
}

export interface PersonaAgent {
  id: string
  name: string
  domain_coverage: string[]
  algorithms_available: string[]
  state: 'IDLE' | 'PROCESSING' | 'ERROR' | 'LEARNING'
  learning_trace: Array<{
    timestamp: string
    action: string
    confidence: number
  }>
  success_rate?: number
  total_processed?: number
  last_activity?: string
  confidence?: number
  current_task?: string
}

export interface Algorithm {
  id: string
  name: string
  description: string
  version: string
  axis_parameters: Array<{
    axis: string
    required: boolean
    weight: number
  }>
  implementation_ref: string
}

export interface AxisValue {
  axis_name: string
  value: number
  metadata: Record<string, unknown>
  confidence: number
}

export interface ComputeAxesRequest {
  data: Record<string, unknown>
  axes?: string[]
}

export interface ComputeAxesResponse {
  results: AxisValue[]
  computation_time: number
  metadata: Record<string, unknown>
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        return {
          error: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        }
      }

      const data = await response.json()
      return { data }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      }
    }
  }

  // Knowledge Nodes
  async getNodes(): Promise<ApiResponse<KnowledgeNode[]>> {
    return this.request<KnowledgeNode[]>('/api/v1/nodes/')
  }

  async getNode(nodeId: string): Promise<ApiResponse<KnowledgeNode>> {
    return this.request<KnowledgeNode>(`/api/v1/nodes/${nodeId}`)
  }

  async createNode(node: Partial<KnowledgeNode>): Promise<ApiResponse<KnowledgeNode>> {
    return this.request<KnowledgeNode>('/api/v1/nodes/', {
      method: 'POST',
      body: JSON.stringify(node),
    })
  }

  // Knowledge Edges
  async getEdges(): Promise<ApiResponse<KnowledgeEdge[]>> {
    return this.request<KnowledgeEdge[]>('/api/v1/edges/')
  }

  async createEdge(edge: Partial<KnowledgeEdge>): Promise<ApiResponse<KnowledgeEdge>> {
    return this.request<KnowledgeEdge>('/api/v1/edges/', {
      method: 'POST',
      body: JSON.stringify(edge),
    })
  }

  // Pillar Levels
  async getPillarLevels(): Promise<ApiResponse<PillarLevel[]>> {
    return this.request<PillarLevel[]>('/api/v1/pillar-levels/')
  }

  async getPillarLevel(pillarId: string): Promise<ApiResponse<PillarLevel>> {
    return this.request<PillarLevel>(`/api/v1/pillar-levels/${pillarId}`)
  }

  // Agents
  async getAgents(): Promise<ApiResponse<PersonaAgent[]>> {
    return this.request<PersonaAgent[]>('/api/v1/agents/')
  }

  async getAgent(agentId: string): Promise<ApiResponse<PersonaAgent>> {
    return this.request<PersonaAgent>(`/api/v1/agents/${agentId}`)
  }

  async startAgent(agentId: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/api/v1/agents/${agentId}/start`, {
      method: 'POST',
    })
  }

  async stopAgent(agentId: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/api/v1/agents/${agentId}/stop`, {
      method: 'POST',
    })
  }

  // Algorithms
  async getAlgorithms(): Promise<ApiResponse<Algorithm[]>> {
    return this.request<Algorithm[]>('/api/v1/algorithms/')
  }

  async runAlgorithm(
    algorithmId: string,
    nodeId: string,
    parameters?: Record<string, unknown>
  ): Promise<ApiResponse<{ result: unknown; computation_time: number }>> {
    return this.request<{ result: unknown; computation_time: number }>(`/api/v1/algorithms/${algorithmId}/run`, {
      method: 'POST',
      body: JSON.stringify({ node_id: nodeId, parameters }),
    })
  }

  // UKG Axes
  async getAxes(): Promise<ApiResponse<{ id: string; name: string; formula: string; description: string }[]>> {
    return this.request<{ id: string; name: string; formula: string; description: string }[]>('/api/v1/axes/')
  }

  async computeAxes(request: ComputeAxesRequest): Promise<ApiResponse<ComputeAxesResponse>> {
    return this.request<ComputeAxesResponse>('/api/v1/axes/compute', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getNodeAxes(nodeId: string): Promise<ApiResponse<AxisValue[]>> {
    return this.request<AxisValue[]>(`/api/v1/axes/node/${nodeId}/axes`)
  }

  // System Status
  async getSystemStatus(): Promise<ApiResponse<{
    status: string
    uptime: number
    agents_active: number
    tasks_running: number
    knowledge_nodes: number
  }>> {
    return this.request('/api/v1/system/status')
  }
}

export const apiClient = new ApiClient()
export default apiClient 
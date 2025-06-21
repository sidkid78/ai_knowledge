"use client"

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Calculator, TrendingUp, Zap, Activity } from 'lucide-react'

interface AxisInfo {
  name: string
  formula: string
  description: string
}

interface AxisValue {
  value: number
  formula: string
  components: Record<string, unknown>
  confidence: number
  computed_at: string
}

const SAMPLE_AXES: AxisInfo[] = [
  {
    name: "pillar_function",
    formula: "Σ wi · pi(x)",
    description: "Weighted sum of pillar attributes"
  },
  {
    name: "level_hierarchy",
    formula: "∫ li, dt",
    description: "Integral over level index li with time deltas"
  },
  {
    name: "branch_navigator",
    formula: "Π bi(x) · ri(x)",
    description: "Product of branch and route components"
  },
  {
    name: "node_mapping",
    formula: "max(Σ ni(x)·vi(x))",
    description: "Maximum sum of node*value pairs"
  },
  {
    name: "honeycomb_crosswalk",
    formula: "Π ci(x) · wi(x)",
    description: "Product of crosswalk and weight per axis"
  },
  {
    name: "spiderweb_provisions",
    formula: "Σ si(x) · ri(x)",
    description: "Weighted sum of provision and route"
  },
  {
    name: "octopus_sector_mappings",
    formula: "∫ δs/δt, dt",
    description: "Integral of sector deltas over time"
  },
  {
    name: "role_id_layer",
    formula: "min(Σ ai(x)·ri(x))",
    description: "Minimum sum of attribute*route for roles"
  },
  {
    name: "sector_expert_function",
    formula: "Π si(x) · ci(x)",
    description: "Product of sector/provision and compliance"
  },
  {
    name: "temporal_axis",
    formula: "∫ δt, dt",
    description: "Accumulation over time intervals"
  },
  {
    name: "unified_system_function",
    formula: "Σ ui(x)·wi(x)",
    description: "System-wide weighted sum"
  },
  {
    name: "location_mapping",
    formula: "geoi(x)·scalei(x)",
    description: "Geospatial position scaling"
  },
  {
    name: "time_evolution_function",
    formula: "Σ epochi·Δki(x)",
    description: "Epoch-wise knowledge delta sum"
  }
]

export function UKGAxesVisualizer() {
  const [axes] = useState<AxisInfo[]>(SAMPLE_AXES)
  const [computedAxes, setComputedAxes] = useState<Record<string, AxisValue>>({})
  const [selectedAxis, setSelectedAxis] = useState<string>('')
  const [axisInputs, setAxisInputs] = useState<Record<string, Record<string, number[]>>>({})
  const [isComputing, setIsComputing] = useState(false)

  const getAxisInputFields = (axisName: string) => {
    switch (axisName) {
      case 'pillar_function':
        return [
          { key: 'weights', label: 'Weights', placeholder: '0.8, 0.6, 0.9' },
          { key: 'values', label: 'Pillar Values', placeholder: '0.7, 0.8, 0.5' }
        ]
      case 'level_hierarchy':
        return [
          { key: 'values', label: 'Level Indices', placeholder: '1.0, 2.0, 1.5' },
          { key: 'time_deltas', label: 'Time Deltas', placeholder: '0.5, 1.0, 0.8' }
        ]
      case 'branch_navigator':
        return [
          { key: 'branch_values', label: 'Branch Values', placeholder: '0.9, 0.7, 0.8' },
          { key: 'route_values', label: 'Route Values', placeholder: '0.6, 0.8, 0.9' }
        ]
      case 'node_mapping':
        return [
          { key: 'node_values', label: 'Node Values', placeholder: '1.2, 0.8, 1.5' },
          { key: 'mapping_values', label: 'Mapping Values', placeholder: '0.7, 0.9, 0.6' }
        ]
      case 'honeycomb_crosswalk':
        return [
          { key: 'crosswalk_values', label: 'Crosswalk Values', placeholder: '0.8, 0.9, 0.7' },
          { key: 'weights', label: 'Weights', placeholder: '1.0, 0.8, 0.9' }
        ]
      case 'spiderweb_provisions':
        return [
          { key: 'provision_values', label: 'Provision Values', placeholder: '0.7, 0.8, 0.9' },
          { key: 'route_values', label: 'Route Values', placeholder: '0.6, 0.7, 0.8' }
        ]
      case 'octopus_sector_mappings':
        return [
          { key: 'sector_deltas', label: 'Sector Deltas', placeholder: '0.1, 0.2, 0.15' },
          { key: 'time_intervals', label: 'Time Intervals', placeholder: '1.0, 2.0, 1.5' }
        ]
      case 'role_id_layer':
        return [
          { key: 'attributes', label: 'Attributes', placeholder: '0.8, 0.9, 0.7' },
          { key: 'routes', label: 'Routes', placeholder: '0.6, 0.8, 0.9' }
        ]
      case 'sector_expert_function':
        return [
          { key: 'sector_values', label: 'Sector Values', placeholder: '0.9, 0.8, 0.7' },
          { key: 'compliance_values', label: 'Compliance Values', placeholder: '0.85, 0.9, 0.8' }
        ]
      case 'temporal_axis':
        return [
          { key: 'timestamps', label: 'Timestamps (ISO)', placeholder: '2024-01-01T00:00:00Z, 2024-01-02T00:00:00Z' },
          { key: 'time_deltas', label: 'Time Deltas', placeholder: '1.0, 2.0, 1.5' }
        ]
      case 'unified_system_function':
        return [
          { key: 'system_metrics', label: 'System Metrics', placeholder: '0.9, 0.7, 0.8' },
          { key: 'weights', label: 'Weights', placeholder: '1.0, 0.8, 0.9' }
        ]
      case 'location_mapping':
        return [
          { key: 'geo_points', label: 'Geo Points (lat,lon pairs)', placeholder: '40.7128,-74.0060,34.0522,-118.2437' },
          { key: 'scale_factors', label: 'Scale Factors', placeholder: '1.0, 0.8' }
        ]
      case 'time_evolution_function':
        return [
          { key: 'epoch_keys', label: 'Epoch Keys', placeholder: 'epoch1, epoch2, epoch3' },
          { key: 'delta_knowledge', label: 'Delta Knowledge', placeholder: '0.1, 0.2, 0.15' }
        ]
      default:
        return [
          { key: 'values', label: 'Values', placeholder: '1.0, 2.0, 1.5' },
          { key: 'weights', label: 'Weights', placeholder: '0.5, 1.0, 0.8' }
        ]
    }
  }

  const handleInputChange = (axisName: string, field: string, value: string) => {
    setAxisInputs(prev => ({
      ...prev,
      [axisName]: {
        ...prev[axisName],
        [field]: value.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v))
      }
    }))
  }

  const computeAxis = async (axisName: string) => {
    setIsComputing(true)
    
    try {
      // Mock computation result
      const mockResult: AxisValue = {
        value: Math.random() * 10,
        formula: axes.find(a => a.name === axisName)?.formula || '',
        components: axisInputs[axisName] || {},
        confidence: 0.85 + Math.random() * 0.15,
        computed_at: new Date().toISOString()
      }
      
      setComputedAxes(prev => ({
        ...prev,
        [axisName]: mockResult
      }))
      
    } catch (error) {
      console.error('Error computing axis:', error)
    } finally {
      setIsComputing(false)
    }
  }

  const formatAxisName = (name: string) => {
    return name.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  const getAxisIcon = (axisName: string) => {
    if (axisName.includes('temporal') || axisName.includes('time')) return <TrendingUp className="h-4 w-4" />
    if (axisName.includes('system') || axisName.includes('unified')) return <Activity className="h-4 w-4" />
    if (axisName.includes('mapping') || axisName.includes('location')) return <Zap className="h-4 w-4" />
    return <Calculator className="h-4 w-4" />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">UKG Mathematical Axes</h2>
          <p className="text-muted-foreground">
            Explore and compute the 13 mathematical dimensions of the Universal Knowledge Graph
          </p>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="compute">Compute Axes</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {axes.map((axis) => (
              <Card key={axis.name} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    {getAxisIcon(axis.name)}
                    <CardTitle className="text-lg">{formatAxisName(axis.name)}</CardTitle>
                  </div>
                  <Badge variant="secondary" className="w-fit font-mono text-xs">
                    {axis.formula}
                  </Badge>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm">
                    {axis.description}
                  </CardDescription>
                  {computedAxes[axis.name] && (
                    <div className="mt-3 space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Value:</span>
                        <Badge variant="outline">
                          {computedAxes[axis.name].value.toFixed(3)}
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Confidence:</span>
                        <div className="flex items-center gap-2">
                          <Progress 
                            value={computedAxes[axis.name].confidence * 100} 
                            className="w-16 h-2"
                          />
                          <span className="text-xs text-muted-foreground">
                            {(computedAxes[axis.name].confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="compute" className="space-y-4">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Select Axis to Compute</CardTitle>
                <CardDescription>
                  Choose an axis and configure its input parameters
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {axes.map((axis) => (
                    <div
                      key={axis.name}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedAxis === axis.name
                          ? 'border-primary bg-primary/5'
                          : 'hover:border-primary/50'
                      }`}
                      onClick={() => setSelectedAxis(axis.name)}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        {getAxisIcon(axis.name)}
                        <span className="font-medium">{formatAxisName(axis.name)}</span>
                      </div>
                      <div className="text-xs text-muted-foreground font-mono">
                        {axis.formula}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>
                  {selectedAxis ? `Configure ${formatAxisName(selectedAxis)}` : 'Select an Axis'}
                </CardTitle>
                <CardDescription>
                  {selectedAxis 
                    ? axes.find(a => a.name === selectedAxis)?.description
                    : 'Choose an axis from the left to configure its parameters'
                  }
                </CardDescription>
              </CardHeader>
              <CardContent>
                {selectedAxis && (
                  <div className="space-y-4">
                    {getAxisInputFields(selectedAxis).map((field) => (
                      <div key={field.key} className="space-y-2">
                        <label className="text-sm font-medium">{field.label}</label>
                        <Input
                          placeholder={field.placeholder}
                          onChange={(e) => handleInputChange(selectedAxis, field.key, e.target.value)}
                        />
                        <p className="text-xs text-muted-foreground">
                          Enter comma-separated values
                        </p>
                      </div>
                    ))}
                    <Button 
                      onClick={() => computeAxis(selectedAxis)} 
                      disabled={isComputing}
                      className="w-full"
                    >
                      {isComputing ? 'Computing...' : `Compute ${formatAxisName(selectedAxis)}`}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
} 
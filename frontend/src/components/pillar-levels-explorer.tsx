"use client"

import React, { useState, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Brain, 
  Cpu, 
  Atom, 
  Dna, 
  Users, 
  Book, 
  Wrench, 
  Briefcase, 
  Scale, 
  Network,
  Search,
  TreePine,
  Filter
} from 'lucide-react'

interface PillarLevel {
  id: string
  name: string
  description: string
  parent: string | null
  domain_type: string
}

const PILLAR_LEVELS: PillarLevel[] = [
  // Mathematics & Logic (PL01-PL10)
  { id: "PL01", name: "Pure Mathematics", description: "Abstract mathematical concepts, number theory, algebra", parent: null, domain_type: "mathematical" },
  { id: "PL02", name: "Applied Mathematics", description: "Mathematical modeling, optimization, statistics", parent: "PL01", domain_type: "mathematical" },
  { id: "PL03", name: "Logic & Proof Theory", description: "Formal logic, proof systems, computational logic", parent: "PL01", domain_type: "mathematical" },
  { id: "PL04", name: "Geometry & Topology", description: "Spatial mathematics, geometric structures", parent: "PL01", domain_type: "mathematical" },
  { id: "PL05", name: "Calculus & Analysis", description: "Differential and integral calculus, real analysis", parent: "PL01", domain_type: "mathematical" },
  { id: "PL06", name: "Discrete Mathematics", description: "Combinatorics, graph theory, discrete structures", parent: "PL01", domain_type: "mathematical" },
  { id: "PL07", name: "Probability & Statistics", description: "Stochastic processes, statistical inference", parent: "PL02", domain_type: "mathematical" },
  { id: "PL08", name: "Numerical Methods", description: "Computational mathematics, numerical algorithms", parent: "PL02", domain_type: "mathematical" },
  { id: "PL09", name: "Mathematical Physics", description: "Mathematics applied to physical phenomena", parent: "PL02", domain_type: "mathematical" },
  { id: "PL10", name: "Operations Research", description: "Optimization, decision theory, game theory", parent: "PL02", domain_type: "mathematical" },

  // Computer Science & Technology (PL11-PL20)
  { id: "PL11", name: "Computer Science Fundamentals", description: "Algorithms, data structures, computational theory", parent: null, domain_type: "computational" },
  { id: "PL12", name: "Software Engineering", description: "Software design, development methodologies", parent: "PL11", domain_type: "computational" },
  { id: "PL13", name: "Artificial Intelligence", description: "Machine learning, neural networks, AI systems", parent: "PL11", domain_type: "computational" },
  { id: "PL14", name: "Database Systems", description: "Data management, query processing, storage", parent: "PL11", domain_type: "computational" },
  { id: "PL15", name: "Computer Networks", description: "Network protocols, distributed systems", parent: "PL11", domain_type: "computational" },
  { id: "PL16", name: "Cybersecurity", description: "Information security, cryptography, threat analysis", parent: "PL11", domain_type: "computational" },
  { id: "PL17", name: "Human-Computer Interaction", description: "User interfaces, usability, interaction design", parent: "PL11", domain_type: "computational" },
  { id: "PL18", name: "Computer Graphics", description: "Visualization, rendering, computer vision", parent: "PL11", domain_type: "computational" },
  { id: "PL19", name: "Quantum Computing", description: "Quantum algorithms, quantum information theory", parent: "PL11", domain_type: "computational" },
  { id: "PL20", name: "Bioinformatics", description: "Computational biology, genomics, biodata analysis", parent: "PL11", domain_type: "computational" },

  // Physical Sciences (PL21-PL30)
  { id: "PL21", name: "Physics", description: "Fundamental physical laws and phenomena", parent: null, domain_type: "physical" },
  { id: "PL22", name: "Classical Mechanics", description: "Newtonian mechanics, dynamics, statics", parent: "PL21", domain_type: "physical" },
  { id: "PL23", name: "Quantum Mechanics", description: "Quantum theory, wave functions, particle physics", parent: "PL21", domain_type: "physical" },
  { id: "PL24", name: "Thermodynamics", description: "Heat, energy, statistical mechanics", parent: "PL21", domain_type: "physical" },
  { id: "PL25", name: "Electromagnetism", description: "Electric and magnetic fields, electromagnetic waves", parent: "PL21", domain_type: "physical" },
  { id: "PL26", name: "Relativity", description: "Special and general relativity, spacetime", parent: "PL21", domain_type: "physical" },
  { id: "PL27", name: "Astronomy & Astrophysics", description: "Celestial mechanics, stellar physics, cosmology", parent: "PL21", domain_type: "physical" },
  { id: "PL28", name: "Chemistry", description: "Molecular structure, chemical reactions, materials", parent: null, domain_type: "physical" },
  { id: "PL29", name: "Materials Science", description: "Material properties, nanotechnology, engineering materials", parent: "PL28", domain_type: "physical" },
  { id: "PL30", name: "Earth Sciences", description: "Geology, meteorology, environmental science", parent: null, domain_type: "physical" },

  // Life Sciences (PL31-PL40)
  { id: "PL31", name: "Biology", description: "Living organisms, biological processes", parent: null, domain_type: "biological" },
  { id: "PL32", name: "Molecular Biology", description: "DNA, RNA, proteins, cellular mechanisms", parent: "PL31", domain_type: "biological" },
  { id: "PL33", name: "Genetics", description: "Heredity, genomics, genetic engineering", parent: "PL31", domain_type: "biological" },
  { id: "PL34", name: "Ecology", description: "Ecosystems, environmental interactions, biodiversity", parent: "PL31", domain_type: "biological" },
  { id: "PL35", name: "Evolutionary Biology", description: "Evolution, natural selection, phylogenetics", parent: "PL31", domain_type: "biological" },
  { id: "PL36", name: "Neuroscience", description: "Brain function, neural networks, cognition", parent: "PL31", domain_type: "biological" },
  { id: "PL37", name: "Medicine", description: "Human health, disease, medical treatment", parent: "PL31", domain_type: "biological" },
  { id: "PL38", name: "Pharmacology", description: "Drug action, therapeutics, toxicology", parent: "PL37", domain_type: "biological" },
  { id: "PL39", name: "Biotechnology", description: "Applied biology, bioengineering, synthetic biology", parent: "PL31", domain_type: "biological" },
  { id: "PL40", name: "Agricultural Science", description: "Crop science, livestock, sustainable agriculture", parent: "PL31", domain_type: "biological" },

  // Social Sciences (PL41-PL50)
  { id: "PL41", name: "Psychology", description: "Human behavior, cognition, mental processes", parent: null, domain_type: "social" },
  { id: "PL42", name: "Sociology", description: "Social structures, institutions, group behavior", parent: null, domain_type: "social" },
  { id: "PL43", name: "Anthropology", description: "Human culture, evolution, social organization", parent: null, domain_type: "social" },
  { id: "PL44", name: "Economics", description: "Markets, financial systems, economic theory", parent: null, domain_type: "social" },
  { id: "PL45", name: "Political Science", description: "Government, policy, political systems", parent: null, domain_type: "social" },
  { id: "PL46", name: "International Relations", description: "Global politics, diplomacy, international law", parent: "PL45", domain_type: "social" },
  { id: "PL47", name: "Public Policy", description: "Policy analysis, governance, public administration", parent: "PL45", domain_type: "social" },
  { id: "PL48", name: "Education", description: "Learning theory, pedagogy, educational systems", parent: null, domain_type: "social" },
  { id: "PL49", name: "Communication Studies", description: "Media, rhetoric, information theory", parent: null, domain_type: "social" },
  { id: "PL50", name: "Urban Planning", description: "City design, infrastructure, regional development", parent: null, domain_type: "social" },

  // Humanities (PL51-PL60)
  { id: "PL51", name: "Philosophy", description: "Logic, ethics, metaphysics, epistemology", parent: null, domain_type: "humanities" },
  { id: "PL52", name: "Ethics", description: "Moral philosophy, applied ethics, bioethics", parent: "PL51", domain_type: "humanities" },
  { id: "PL53", name: "History", description: "Historical analysis, historiography, cultural history", parent: null, domain_type: "humanities" },
  { id: "PL54", name: "Literature", description: "Literary analysis, creative writing, comparative literature", parent: null, domain_type: "humanities" },
  { id: "PL55", name: "Linguistics", description: "Language structure, phonetics, syntax, semantics", parent: null, domain_type: "humanities" },
  { id: "PL56", name: "Art History", description: "Visual arts, artistic movements, cultural aesthetics", parent: null, domain_type: "humanities" },
  { id: "PL57", name: "Music Theory", description: "Musical composition, harmony, acoustic principles", parent: null, domain_type: "humanities" },
  { id: "PL58", name: "Religious Studies", description: "Theology, comparative religion, spiritual traditions", parent: null, domain_type: "humanities" },
  { id: "PL59", name: "Cultural Studies", description: "Cultural theory, identity, social movements", parent: null, domain_type: "humanities" },
  { id: "PL60", name: "Archaeology", description: "Material culture, historical reconstruction", parent: "PL53", domain_type: "humanities" },

  // Applied Sciences & Engineering (PL61-PL70)
  { id: "PL61", name: "Engineering", description: "Applied science, design, construction", parent: null, domain_type: "engineering" },
  { id: "PL62", name: "Mechanical Engineering", description: "Machines, thermodynamics, manufacturing", parent: "PL61", domain_type: "engineering" },
  { id: "PL63", name: "Electrical Engineering", description: "Electronics, power systems, signal processing", parent: "PL61", domain_type: "engineering" },
  { id: "PL64", name: "Civil Engineering", description: "Infrastructure, structures, transportation", parent: "PL61", domain_type: "engineering" },
  { id: "PL65", name: "Chemical Engineering", description: "Process design, reaction engineering, separation", parent: "PL61", domain_type: "engineering" },
  { id: "PL66", name: "Aerospace Engineering", description: "Aircraft, spacecraft, propulsion systems", parent: "PL61", domain_type: "engineering" },
  { id: "PL67", name: "Biomedical Engineering", description: "Medical devices, biomechanics, tissue engineering", parent: "PL61", domain_type: "engineering" },
  { id: "PL68", name: "Environmental Engineering", description: "Pollution control, sustainability, green technology", parent: "PL61", domain_type: "engineering" },
  { id: "PL69", name: "Industrial Engineering", description: "Systems optimization, quality control, logistics", parent: "PL61", domain_type: "engineering" },
  { id: "PL70", name: "Nuclear Engineering", description: "Nuclear technology, radiation, reactor design", parent: "PL61", domain_type: "engineering" },

  // Business & Management (PL71-PL77)
  { id: "PL71", name: "Business Administration", description: "Management, strategy, organizational behavior", parent: null, domain_type: "business" },
  { id: "PL72", name: "Finance", description: "Investment, risk management, financial markets", parent: "PL71", domain_type: "business" },
  { id: "PL73", name: "Marketing", description: "Consumer behavior, branding, market research", parent: "PL71", domain_type: "business" },
  { id: "PL74", name: "Operations Management", description: "Supply chain, production, quality management", parent: "PL71", domain_type: "business" },
  { id: "PL75", name: "Entrepreneurship", description: "Innovation, startup development, venture capital", parent: "PL71", domain_type: "business" },
  { id: "PL76", name: "Human Resources", description: "Personnel management, organizational development", parent: "PL71", domain_type: "business" },
  { id: "PL77", name: "Information Systems", description: "Business technology, data analytics, digital transformation", parent: "PL71", domain_type: "business" },

  // Law & Governance (PL78-PL82)
  { id: "PL78", name: "Law", description: "Legal systems, jurisprudence, legal theory", parent: null, domain_type: "legal" },
  { id: "PL79", name: "Constitutional Law", description: "Government structure, civil rights, constitutional interpretation", parent: "PL78", domain_type: "legal" },
  { id: "PL80", name: "Criminal Law", description: "Criminal justice, procedure, evidence", parent: "PL78", domain_type: "legal" },
  { id: "PL81", name: "Commercial Law", description: "Business law, contracts, intellectual property", parent: "PL78", domain_type: "legal" },
  { id: "PL82", name: "International Law", description: "Treaties, human rights, global governance", parent: "PL78", domain_type: "legal" },

  // Interdisciplinary & Emerging Fields (PL83-PL87)
  { id: "PL83", name: "Systems Science", description: "Complex systems, network theory, emergence", parent: null, domain_type: "interdisciplinary" },
  { id: "PL84", name: "Cognitive Science", description: "Mind, consciousness, artificial cognition", parent: null, domain_type: "interdisciplinary" },
  { id: "PL85", name: "Data Science", description: "Big data, machine learning, predictive analytics", parent: null, domain_type: "interdisciplinary" },
  { id: "PL86", name: "Sustainability Science", description: "Environmental policy, renewable energy, climate science", parent: null, domain_type: "interdisciplinary" },
  { id: "PL87", name: "Digital Humanities", description: "Technology in humanities, digital scholarship", parent: null, domain_type: "interdisciplinary" }
]

const DOMAIN_INFO = {
  mathematical: { name: "Mathematics & Logic", icon: Brain, color: "bg-blue-500", count: 10 },
  computational: { name: "Computer Science & Technology", icon: Cpu, color: "bg-green-500", count: 10 },
  physical: { name: "Physical Sciences", icon: Atom, color: "bg-purple-500", count: 10 },
  biological: { name: "Life Sciences", icon: Dna, color: "bg-emerald-500", count: 10 },
  social: { name: "Social Sciences", icon: Users, color: "bg-orange-500", count: 10 },
  humanities: { name: "Humanities", icon: Book, color: "bg-pink-500", count: 10 },
  engineering: { name: "Applied Sciences & Engineering", icon: Wrench, color: "bg-red-500", count: 10 },
  business: { name: "Business & Management", icon: Briefcase, color: "bg-yellow-500", count: 7 },
  legal: { name: "Law & Governance", icon: Scale, color: "bg-indigo-500", count: 5 },
  interdisciplinary: { name: "Interdisciplinary & Emerging", icon: Network, color: "bg-teal-500", count: 5 }
}

export function PillarLevelsExplorer() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDomain, setSelectedDomain] = useState<string>('all')
  const [selectedPillar, setSelectedPillar] = useState<PillarLevel | null>(null)

  const filteredPillars = useMemo(() => {
    return PILLAR_LEVELS.filter(pillar => {
      const matchesSearch = pillar.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           pillar.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           pillar.id.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesDomain = selectedDomain === 'all' || pillar.domain_type === selectedDomain
      return matchesSearch && matchesDomain
    })
  }, [searchTerm, selectedDomain])

  const getDomainIcon = (domainType: string) => {
    const IconComponent = DOMAIN_INFO[domainType as keyof typeof DOMAIN_INFO]?.icon || Network
    return <IconComponent className="h-4 w-4" />
  }

  const getDomainColor = (domainType: string) => {
    return DOMAIN_INFO[domainType as keyof typeof DOMAIN_INFO]?.color || "bg-gray-500"
  }

  const getChildPillars = (parentId: string) => {
    return PILLAR_LEVELS.filter(pillar => pillar.parent === parentId)
  }

  const getRootPillars = (domainType: string) => {
    return PILLAR_LEVELS.filter(pillar => pillar.domain_type === domainType && pillar.parent === null)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">UKG Pillar Levels</h2>
          <p className="text-muted-foreground">
            Explore all 87 knowledge domains of the Universal Knowledge Graph
          </p>
        </div>
        <Badge variant="secondary" className="text-lg px-3 py-1">
          87 Domains
        </Badge>
      </div>

      {/* Search and Filter Controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search pillar levels..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            className="px-3 py-2 border rounded-md bg-background"
            aria-label="Filter by domain"
          >
            <option value="all">All Domains</option>
            {Object.entries(DOMAIN_INFO).map(([key, info]) => (
              <option key={key} value={key}>{info.name}</option>
            ))}
          </select>
        </div>
      </div>

      <Tabs defaultValue="domains" className="space-y-4">
        <TabsList>
          <TabsTrigger value="domains">By Domain</TabsTrigger>
          <TabsTrigger value="hierarchy">Hierarchy View</TabsTrigger>
          <TabsTrigger value="list">Complete List</TabsTrigger>
        </TabsList>

        <TabsContent value="domains" className="space-y-6">
          {/* Domain Overview Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(DOMAIN_INFO).map(([key, info]) => {
              const IconComponent = info.icon
              const domainPillars = PILLAR_LEVELS.filter(p => p.domain_type === key)
              
              return (
                <Card key={key} className="hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => setSelectedDomain(key)}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${info.color} text-white`}>
                        <IconComponent className="h-5 w-5" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{info.name}</CardTitle>
                        <Badge variant="outline">{info.count} pillars</Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {domainPillars.slice(0, 3).map(pillar => (
                        <div key={pillar.id} className="text-sm text-muted-foreground">
                          {pillar.id}: {pillar.name}
                        </div>
                      ))}
                      {domainPillars.length > 3 && (
                        <div className="text-sm text-muted-foreground">
                          +{domainPillars.length - 3} more...
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        <TabsContent value="hierarchy" className="space-y-4">
          <ScrollArea className="h-96">
            {selectedDomain === 'all' ? (
              Object.entries(DOMAIN_INFO).map(([domainKey, domainInfo]) => (
                <div key={domainKey} className="mb-6">
                  <div className="flex items-center gap-2 mb-3">
                    <domainInfo.icon className="h-5 w-5" />
                    <h3 className="text-lg font-semibold">{domainInfo.name}</h3>
                  </div>
                  <div className="space-y-2 ml-4">
                    {getRootPillars(domainKey).map(rootPillar => (
                      <div key={rootPillar.id}>
                        <div className="flex items-center gap-2 p-2 rounded border">
                          <TreePine className="h-4 w-4" />
                          <span className="font-medium">{rootPillar.id}: {rootPillar.name}</span>
                        </div>
                        <div className="ml-6 mt-1 space-y-1">
                          {getChildPillars(rootPillar.id).map(child => (
                            <div key={child.id} className="text-sm text-muted-foreground p-1">
                              └─ {child.id}: {child.name}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="space-y-4">
                {getRootPillars(selectedDomain).map(rootPillar => (
                  <div key={rootPillar.id}>
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <TreePine className="h-4 w-4" />
                          {rootPillar.id}: {rootPillar.name}
                        </CardTitle>
                        <CardDescription>{rootPillar.description}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {getChildPillars(rootPillar.id).map(child => (
                            <div key={child.id} className="flex items-center gap-2 p-2 border rounded">
                              <Badge variant="outline">{child.id}</Badge>
                              <span className="font-medium">{child.name}</span>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </TabsContent>

        <TabsContent value="list" className="space-y-4">
          <div className="text-sm text-muted-foreground mb-4">
            Showing {filteredPillars.length} of {PILLAR_LEVELS.length} pillar levels
          </div>
          <ScrollArea className="h-96">
            <div className="grid gap-3 md:grid-cols-2">
              {filteredPillars.map(pillar => (
                <Card key={pillar.id} className="hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => setSelectedPillar(pillar)}>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">{pillar.id}</Badge>
                      <div className="flex items-center gap-1">
                        {getDomainIcon(pillar.domain_type)}
                        <span className={`w-2 h-2 rounded-full ${getDomainColor(pillar.domain_type)}`} />
                      </div>
                    </div>
                    <CardTitle className="text-base">{pillar.name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-xs">
                      {pillar.description}
                    </CardDescription>
                    {pillar.parent && (
                      <Badge variant="secondary" className="mt-2 text-xs">
                        Child of {pillar.parent}
                      </Badge>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>

      {/* Selected Pillar Detail Modal/Panel */}
      {selectedPillar && (
        <Card className="border-2 border-primary">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Badge variant="default">{selectedPillar.id}</Badge>
                <CardTitle>{selectedPillar.name}</CardTitle>
              </div>
              <Button variant="outline" size="sm" onClick={() => setSelectedPillar(null)}>
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">Description</h4>
                <p className="text-muted-foreground">{selectedPillar.description}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-2">Domain</h4>
                  <div className="flex items-center gap-2">
                    {getDomainIcon(selectedPillar.domain_type)}
                    <span>{DOMAIN_INFO[selectedPillar.domain_type as keyof typeof DOMAIN_INFO]?.name}</span>
                  </div>
                </div>
                
                {selectedPillar.parent && (
                  <div>
                    <h4 className="font-medium mb-2">Parent Pillar</h4>
                    <Badge variant="secondary">{selectedPillar.parent}</Badge>
                  </div>
                )}
              </div>

              {getChildPillars(selectedPillar.id).length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Sub-pillars</h4>
                  <div className="flex flex-wrap gap-2">
                    {getChildPillars(selectedPillar.id).map(child => (
                      <Badge key={child.id} variant="outline" className="cursor-pointer"
                             onClick={() => setSelectedPillar(child)}>
                        {child.id}: {child.name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
} 
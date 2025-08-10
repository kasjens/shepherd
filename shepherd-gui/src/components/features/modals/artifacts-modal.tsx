'use client'

import React, { useState } from 'react'
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Package, 
  Code, 
  FileText, 
  Download, 
  Copy, 
  Eye, 
  Calendar, 
  User,
  Tag,
  Search,
  Filter
} from 'lucide-react'
import { Input } from '@/components/ui/input'

interface Artifact {
  id: string
  name: string
  type: 'python' | 'markdown' | 'json' | 'text' | 'csv' | 'html' | 'yaml'
  size: number
  created: Date
  content: string
  description?: string
  tags?: string[]
  conversationId: string
}

interface ArtifactsModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const mockArtifacts: Artifact[] = [
  {
    id: '1',
    name: 'system_analysis.py',
    type: 'python',
    size: 2048,
    created: new Date(Date.now() - 24 * 60 * 1000),
    content: `#!/usr/bin/env python3
"""
System Analysis Script
Analyzes system performance and resource usage
"""

import psutil
import json
from datetime import datetime

def analyze_system():
    return {
        'cpu': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory()._asdict(),
        'disk': psutil.disk_usage('/')._asdict(),
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    analysis = analyze_system()
    print(json.dumps(analysis, indent=2))`,
    description: 'Python script for comprehensive system analysis',
    tags: ['system', 'monitoring', 'performance'],
    conversationId: 'conv-1'
  },
  {
    id: '2',
    name: 'performance_report.md',
    type: 'markdown',
    size: 1534,
    created: new Date(Date.now() - 24 * 60 * 1000),
    content: `# System Performance Report

## Executive Summary
This report analyzes the current system performance and identifies optimization opportunities.

## Key Findings
- **CPU Usage**: 45% average, with peaks during heavy operations
- **Memory Usage**: 78% utilization, approaching capacity limits
- **Disk I/O**: Moderate activity with room for optimization

## Recommendations
1. **Memory Optimization**: Consider adding RAM or optimizing memory-intensive processes
2. **Process Cleanup**: 127 running services can be reduced
3. **Cache Configuration**: Implement better caching strategies

## Next Steps
- Implement monitoring alerts for memory usage > 85%
- Schedule weekly performance reviews
- Consider upgrading hardware if trends continue`,
    description: 'Detailed performance analysis and recommendations',
    tags: ['report', 'performance', 'recommendations'],
    conversationId: 'conv-1'
  },
  {
    id: '3',
    name: 'memory_analysis.json',
    type: 'json',
    size: 892,
    created: new Date(Date.now() - 19 * 60 * 1000),
    content: `{
  "top_processes": [
    {
      "name": "postgres",
      "memory_mb": 1228.8,
      "memory_percent": 15.2,
      "pid": 1234
    },
    {
      "name": "chrome",
      "memory_mb": 819.2,
      "memory_percent": 10.1,
      "pid": 5678
    },
    {
      "name": "java",
      "memory_mb": 614.4,
      "memory_percent": 7.6,
      "pid": 9012
    }
  ],
  "total_memory_gb": 8.0,
  "available_memory_gb": 1.8,
  "memory_usage_percent": 77.5,
  "analysis_timestamp": "2024-01-15T14:30:00Z"
}`,
    description: 'Memory usage breakdown by process',
    tags: ['memory', 'processes', 'analysis'],
    conversationId: 'conv-1'
  }
]

function getFileIcon(type: string) {
  switch (type) {
    case 'python':
      return <Code className="h-4 w-4 text-blue-600" />
    case 'markdown':
      return <FileText className="h-4 w-4 text-gray-600" />
    case 'json':
      return <Package className="h-4 w-4 text-green-600" />
    default:
      return <FileText className="h-4 w-4" />
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatTime(date: Date): string {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return date.toLocaleDateString()
}

export function ArtifactsModal({ open, onOpenChange }: ArtifactsModalProps) {
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<string>('all')

  const filteredArtifacts = mockArtifacts.filter(artifact => {
    const matchesSearch = artifact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         artifact.description?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = filterType === 'all' || artifact.type === filterType
    return matchesSearch && matchesType
  })

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content)
    // Could add a toast notification here
  }

  const handleDownload = (artifact: Artifact) => {
    const blob = new Blob([artifact.content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = artifact.name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            Artifacts ({filteredArtifacts.length})
          </DialogTitle>
        </DialogHeader>
        
        <div className="flex gap-4 h-full overflow-hidden">
          {/* Artifacts List */}
          <div className="w-1/3 border-r border-border pr-4 overflow-hidden flex flex-col">
            {/* Search and Filter */}
            <div className="space-y-2 mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search artifacts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
              
              <Tabs value={filterType} onValueChange={setFilterType}>
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="python">Python</TabsTrigger>
                  <TabsTrigger value="markdown">Docs</TabsTrigger>
                  <TabsTrigger value="json">Data</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
            
            {/* Artifacts List */}
            <div className="flex-1 overflow-y-auto space-y-2">
              {filteredArtifacts.map((artifact) => (
                <Card
                  key={artifact.id}
                  className={`p-3 cursor-pointer transition-colors hover:bg-accent ${
                    selectedArtifact?.id === artifact.id ? 'ring-2 ring-primary' : ''
                  }`}
                  onClick={() => setSelectedArtifact(artifact)}
                >
                  <div className="flex items-start gap-2">
                    {getFileIcon(artifact.type)}
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">
                        {artifact.name}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatFileSize(artifact.size)} • {formatTime(artifact.created)}
                      </div>
                      {artifact.description && (
                        <div className="text-xs text-muted-foreground mt-1 line-clamp-2">
                          {artifact.description}
                        </div>
                      )}
                      {artifact.tags && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {artifact.tags.map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
          
          {/* Artifact Preview */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {selectedArtifact ? (
              <>
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    {getFileIcon(selectedArtifact.type)}
                    <h3 className="font-medium">{selectedArtifact.name}</h3>
                    <Badge variant="outline">{selectedArtifact.type}</Badge>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCopy(selectedArtifact.content)}
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDownload(selectedArtifact)}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
                
                {/* Metadata */}
                <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4 pb-4 border-b">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    {selectedArtifact.created.toLocaleString()}
                  </div>
                  <div>{formatFileSize(selectedArtifact.size)}</div>
                  {selectedArtifact.tags && (
                    <div className="flex items-center gap-1">
                      <Tag className="h-4 w-4" />
                      {selectedArtifact.tags.join(', ')}
                    </div>
                  )}
                </div>
                
                {/* Content */}
                <div className="flex-1 overflow-y-auto">
                  <pre className="text-sm font-mono bg-muted p-4 rounded-lg whitespace-pre-wrap">
                    {selectedArtifact.content}
                  </pre>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-center text-muted-foreground">
                <div>
                  <Eye className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <h3 className="font-medium mb-2">Select an artifact to preview</h3>
                  <p className="text-sm">Choose from {filteredArtifacts.length} available artifacts</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
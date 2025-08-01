'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Search, 
  Download, 
  X, 
  Copy, 
  Play, 
  Edit, 
  Save,
  FileText,
  Code,
  Database,
  FileImage
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface ArtifactsPanelProps {
  className?: string
}

const sampleArtifact = {
  id: '1',
  name: 'system_analysis.py',
  type: 'python',
  content: `#!/usr/bin/env python3
import psutil
import json

def analyze_system():
    """Analyze system performance."""
    cpu_percent = psutil.cpu_percent(1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'cpu': cpu_percent,
        'memory': {
            'percent': memory.percent,
            'available': memory.available
        },
        'disk': {
            'percent': disk.percent,
            'free': disk.free
        }
    }

if __name__ == '__main__':
    result = analyze_system()
    print(json.dumps(result, indent=2))`,
  language: 'python',
  size: '45 lines',
  created: '12m ago'
}

const getFileIcon = (type: string) => {
  switch (type) {
    case 'python':
    case 'javascript':
    case 'typescript':
      return <Code className="h-4 w-4" />
    case 'json':
    case 'yaml':
      return <Database className="h-4 w-4" />
    case 'markdown':
    case 'text':
      return <FileText className="h-4 w-4" />
    case 'image':
    case 'png':
    case 'jpg':
      return <FileImage className="h-4 w-4" />
    default:
      return <FileText className="h-4 w-4" />
  }
}

export function ArtifactsPanel({ className }: ArtifactsPanelProps) {
  const [selectedTab, setSelectedTab] = useState('all')

  return (
    <div className={cn("artifacts-panel", className)}>
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold">📦 Artifacts</h2>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <Search className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <Download className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-1">
          {['all', 'code', 'scripts', 'reports'].map((tab) => (
            <Button
              key={tab}
              variant={selectedTab === tab ? 'default' : 'ghost'}
              size="sm"
              className="h-7 px-3 text-xs"
              onClick={() => setSelectedTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Artifact Viewer */}
      <div className="flex-1 overflow-y-auto p-4">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm flex items-center gap-2">
                {getFileIcon(sampleArtifact.type)}
                {sampleArtifact.name}
              </CardTitle>
              <div className="flex items-center gap-1">
                <Button variant="ghost" size="icon" className="h-6 w-6">
                  <Copy className="h-3 w-3" />
                </Button>
                <Button variant="ghost" size="icon" className="h-6 w-6">
                  <Download className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="p-0">
            {/* Code Content */}
            <div className="relative">
              <pre className="text-xs bg-terminal-black text-prompt-white p-4 overflow-x-auto rounded-none">
                <code className="language-python">
                  {sampleArtifact.content}
                </code>
              </pre>
            </div>
            
            {/* Metadata */}
            <div className="p-4 border-t border-border bg-muted/20">
              <div className="text-xs text-muted-gray mb-3">
                Language: {sampleArtifact.language} • {sampleArtifact.size} • Created {sampleArtifact.created}
              </div>
              
              {/* Actions */}
              <div className="flex gap-2">
                <Button size="sm" className="h-7">
                  <Play className="h-3 w-3 mr-1" />
                  Run Script
                </Button>
                <Button variant="outline" size="sm" className="h-7">
                  <Edit className="h-3 w-3 mr-1" />
                  Edit
                </Button>
                <Button variant="outline" size="sm" className="h-7">
                  <Save className="h-3 w-3 mr-1" />
                  Save As...
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Command Output */}
        <Card className="mt-4">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              🖥️ Command Output
              <div className="flex items-center gap-1 ml-auto">
                <Button variant="ghost" size="icon" className="h-6 w-6">
                  <Copy className="h-3 w-3" />
                </Button>
                <Button variant="ghost" size="icon" className="h-6 w-6">
                  <Play className="h-3 w-3" />
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="p-0">
            <div className="bg-terminal-black text-prompt-white p-4 rounded-none">
              <div className="text-success-green text-xs mb-2">$ python system_analysis.py</div>
              <pre className="text-xs">
{`{
  "cpu": 45.2,
  "memory": {
    "percent": 78.4,
    "available": 1843200000
  },
  "disk": {
    "percent": 62.1,
    "free": 45231616000
  }
}`}
              </pre>
              <div className="text-success-green text-xs mt-2">✅ Executed successfully in 0.8s</div>
            </div>
            
            <div className="p-3 border-t border-border bg-muted/20">
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="h-7">
                  Save Output
                </Button>
                <Button variant="outline" size="sm" className="h-7">
                  Run Again
                </Button>
                <Button variant="outline" size="sm" className="h-7">
                  Clear
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
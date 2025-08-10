'use client'

import React, { useState } from 'react'
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Settings, 
  Palette, 
  Database, 
  Shield, 
  Bell, 
  User,
  Monitor,
  Folder,
  Key,
  Globe,
  Zap,
  Brain,
  MessageSquare,
  Save,
  RotateCcw,
  CheckCircle
} from 'lucide-react'

interface SettingsModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function SettingsModal({ open, onOpenChange }: SettingsModalProps) {
  const [theme, setTheme] = useState('system')
  const [notifications, setNotifications] = useState(true)
  const [autoSave, setAutoSave] = useState(true)
  const [maxConversations, setMaxConversations] = useState('50')
  const [apiUrl, setApiUrl] = useState('http://localhost:8000')
  const [unsavedChanges, setUnsavedChanges] = useState(false)

  const handleSave = () => {
    // Save settings logic here
    setUnsavedChanges(false)
  }

  const handleReset = () => {
    // Reset to defaults
    setTheme('system')
    setNotifications(true)
    setAutoSave(true)
    setMaxConversations('50')
    setApiUrl('http://localhost:8000')
    setUnsavedChanges(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl h-[90vh] overflow-hidden">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Settings & Configuration
            </DialogTitle>
            {unsavedChanges && (
              <Badge variant="secondary" className="text-xs">
                Unsaved changes
              </Badge>
            )}
          </div>
        </DialogHeader>
        
        <Tabs defaultValue="appearance" className="flex-1 overflow-hidden">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="appearance" className="flex items-center gap-2">
              <Palette className="h-4 w-4" />
              Theme
            </TabsTrigger>
            <TabsTrigger value="general" className="flex items-center gap-2">
              <Monitor className="h-4 w-4" />
              General
            </TabsTrigger>
            <TabsTrigger value="ai" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              AI Settings
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Security
            </TabsTrigger>
            <TabsTrigger value="advanced" className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Advanced
            </TabsTrigger>
          </TabsList>
          
          <div className="overflow-y-auto flex-1 mt-4 space-y-4">
            <TabsContent value="appearance" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Theme Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Color Theme</label>
                    <div className="grid grid-cols-3 gap-3 mt-2">
                      <div 
                        className={`p-4 border rounded-lg cursor-pointer ${theme === 'light' ? 'ring-2 ring-primary' : ''}`}
                        onClick={() => setTheme('light')}
                      >
                        <div className="w-full h-16 bg-white border rounded mb-2"></div>
                        <div className="text-sm font-medium">Light</div>
                      </div>
                      <div 
                        className={`p-4 border rounded-lg cursor-pointer ${theme === 'dark' ? 'ring-2 ring-primary' : ''}`}
                        onClick={() => setTheme('dark')}
                      >
                        <div className="w-full h-16 bg-gray-900 border rounded mb-2"></div>
                        <div className="text-sm font-medium">Dark</div>
                      </div>
                      <div 
                        className={`p-4 border rounded-lg cursor-pointer ${theme === 'system' ? 'ring-2 ring-primary' : ''}`}
                        onClick={() => setTheme('system')}
                      >
                        <div className="w-full h-16 bg-gradient-to-r from-white to-gray-900 border rounded mb-2"></div>
                        <div className="text-sm font-medium">System</div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Accent Color</label>
                    <div className="flex gap-2 mt-2">
                      {['blue', 'green', 'purple', 'red', 'orange'].map((color) => (
                        <div
                          key={color}
                          className={`w-8 h-8 rounded-full cursor-pointer border-2 border-transparent bg-${color}-500`}
                        />
                      ))}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Compact UI</label>
                      <Button variant="outline" size="sm">Toggle</Button>
                    </div>
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Show Line Numbers</label>
                      <Button variant="outline" size="sm">Toggle</Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="general" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">General Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Project Folder</label>
                    <div className="flex gap-2 mt-1">
                      <Input 
                        placeholder="/path/to/project"
                        className="flex-1"
                      />
                      <Button variant="outline">
                        <Folder className="h-4 w-4 mr-2" />
                        Browse
                      </Button>
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Max Conversations</label>
                    <Input 
                      type="number"
                      value={maxConversations}
                      onChange={(e) => setMaxConversations(e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Auto-save conversations</label>
                      <Button 
                        variant={autoSave ? "default" : "outline"} 
                        size="sm"
                        onClick={() => setAutoSave(!autoSave)}
                      >
                        {autoSave ? <CheckCircle className="h-4 w-4" /> : "Enable"}
                      </Button>
                    </div>
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Confirm dangerous operations</label>
                      <Button variant="default" size="sm">
                        <CheckCircle className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="ai" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">AI Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Default Model</label>
                    <div className="grid grid-cols-2 gap-3 mt-2">
                      <Card className="p-3 cursor-pointer ring-2 ring-primary">
                        <div className="text-sm font-medium">llama3.1:8b</div>
                        <div className="text-xs text-muted-foreground">General purpose, balanced</div>
                      </Card>
                      <Card className="p-3 cursor-pointer">
                        <div className="text-sm font-medium">codellama:7b</div>
                        <div className="text-xs text-muted-foreground">Optimized for coding</div>
                      </Card>
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Temperature</label>
                    <Input type="number" step="0.1" min="0" max="2" defaultValue="0.7" className="mt-1" />
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Max Tokens</label>
                    <Input type="number" defaultValue="2048" className="mt-1" />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Stream responses</label>
                      <Button variant="default" size="sm">
                        <CheckCircle className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Enable memory</label>
                      <Button variant="default" size="sm">
                        <CheckCircle className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="notifications" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Notification Preferences</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">Workflow completions</div>
                        <div className="text-xs text-muted-foreground">Get notified when workflows finish</div>
                      </div>
                      <Button variant="default" size="sm">
                        <CheckCircle className="h-4 w-4" />
                      </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">Error notifications</div>
                        <div className="text-xs text-muted-foreground">Critical errors and failures</div>
                      </div>
                      <Button variant="default" size="sm">
                        <CheckCircle className="h-4 w-4" />
                      </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">Performance alerts</div>
                        <div className="text-xs text-muted-foreground">System resource warnings</div>
                      </div>
                      <Button variant="outline" size="sm">
                        Disabled
                      </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">Learning updates</div>
                        <div className="text-xs text-muted-foreground">New patterns and insights</div>
                      </div>
                      <Button variant="default" size="sm">
                        <CheckCircle className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="security" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Security & Privacy</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">API Key</label>
                    <div className="flex gap-2 mt-1">
                      <Input type="password" placeholder="••••••••••••••••" className="flex-1" />
                      <Button variant="outline">
                        <Key className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">Encrypt local data</div>
                        <div className="text-xs text-muted-foreground">Encrypt conversations and artifacts</div>
                      </div>
                      <Button variant="default" size="sm">
                        <CheckCircle className="h-4 w-4" />
                      </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">Auto-clear sensitive data</div>
                        <div className="text-xs text-muted-foreground">Clear after 30 days</div>
                      </div>
                      <Button variant="outline" size="sm">
                        Configure
                      </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">Require confirmation for system commands</div>
                        <div className="text-xs text-muted-foreground">Safety for destructive operations</div>
                      </div>
                      <Button variant="default" size="sm">
                        <CheckCircle className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="advanced" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Advanced Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">API Endpoint</label>
                    <Input 
                      value={apiUrl}
                      onChange={(e) => setApiUrl(e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Request Timeout (seconds)</label>
                    <Input type="number" defaultValue="30" className="mt-1" />
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Max Concurrent Workflows</label>
                    <Input type="number" defaultValue="5" className="mt-1" />
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">Debug mode</div>
                        <div className="text-xs text-muted-foreground">Enable detailed logging</div>
                      </div>
                      <Button variant="outline" size="sm">
                        Disabled
                      </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">Experimental features</div>
                        <div className="text-xs text-muted-foreground">Access beta functionality</div>
                      </div>
                      <Button variant="outline" size="sm">
                        Enable
                      </Button>
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t">
                    <Button variant="destructive" size="sm">
                      Reset All Settings
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </div>
        </Tabs>
        
        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="text-sm text-muted-foreground">
            Changes are saved automatically
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset
            </Button>
            <Button onClick={handleSave}>
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { FolderOpen, Folder, X } from 'lucide-react'
import { useProjectStore } from '@/stores/project-store'
import { isTauri } from '@/lib/tauri'

export function ProjectFolderSelector() {
  const { projectFolder, setProjectFolder, clearProjectFolder } = useProjectStore()
  const [isSelecting, setIsSelecting] = useState(false)

  const handleSelectFolder = async () => {
    setIsSelecting(true)
    
    try {
      // Try Tauri first
      if (isTauri()) {
        try {
          // Dynamic import with string literal to prevent webpack analysis
          const { open } = await eval('import("@tauri-apps/api/dialog")')
          
          const selected = await open({
            directory: true,
            multiple: false,
            title: 'Select Project Folder',
          })
          
          if (selected && typeof selected === 'string') {
            setProjectFolder(selected)
            setIsSelecting(false)
            return
          }
        } catch (error) {
          console.warn('Tauri API not available:', error)
        }
      }
      
      // Fallback for web version - use file input with webkitdirectory
      const input = document.createElement('input')
      input.type = 'file'
      input.webkitdirectory = true
      input.multiple = true
      
      input.onchange = (e) => {
        const files = (e.target as HTMLInputElement).files
        if (files && files.length > 0) {
          // Get the common path from the first file
          const firstFile = files[0]
          const pathParts = firstFile.webkitRelativePath.split('/')
          if (pathParts.length > 1) {
            // Remove the file name to get the directory
            pathParts.pop()
            const folderPath = pathParts.join('/')
            setProjectFolder(folderPath)
          }
        }
      }
      
      input.click()
    } catch (error) {
      console.error('Error selecting folder:', error)
    } finally {
      setIsSelecting(false)
    }
  }

  const handleClearFolder = () => {
    clearProjectFolder()
  }

  const getDisplayPath = (folder: string) => {
    // Show only the last 2 parts of the path for better UI
    const parts = folder.split(/[/\\]/)
    if (parts.length > 2) {
      return `.../${parts.slice(-2).join('/')}`
    }
    return folder
  }

  return (
    <div className="space-y-2">
      <div className="text-xs font-medium text-muted-gray uppercase tracking-wide">
        📁 PROJECT FOLDER
      </div>
      
      {projectFolder ? (
        <div className="space-y-2">
          <div 
            className="p-2 rounded bg-accent/20 border border-border-gray flex items-center gap-2"
            title={projectFolder}
          >
            <Folder className="h-4 w-4 text-muted-gray flex-shrink-0" />
            <span className="text-sm truncate flex-1" style={{ color: 'var(--foreground)' }}>
              {getDisplayPath(projectFolder)}
            </span>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={handleClearFolder}
              title="Clear project folder"
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
          
          <Button
            variant="outline"
            size="sm"
            className="w-full h-7 text-xs"
            onClick={handleSelectFolder}
            disabled={isSelecting}
          >
            <FolderOpen className="h-3 w-3 mr-1" />
            {isSelecting ? 'Selecting...' : 'Change Folder'}
          </Button>
        </div>
      ) : (
        <Button
          variant="outline"
          size="sm"
          className="w-full h-8"
          onClick={handleSelectFolder}
          disabled={isSelecting}
        >
          <FolderOpen className="h-4 w-4 mr-2" />
          {isSelecting ? 'Selecting...' : 'Set Project Folder'}
        </Button>
      )}
    </div>
  )
}
'use client'

import React, { memo, useState, useCallback, useMemo } from 'react'
import { FixedSizeList as List, VariableSizeList as VariableList } from 'react-window'
import AutoSizer from 'react-virtualized-auto-sizer'
import {
  Folder,
  File,
  FileText,
  FileCode,
  FileImage,
  FileVideo,
  FileAudio,
  Download,
  Eye,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  Grid,
  List as ListIcon,
  MoreVertical,
  Star,
  Upload,
  RefreshCw
} from 'lucide-react'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'

export interface FileItem {
  id: string
  name: string
  type: 'file' | 'folder'
  size?: number
  mimeType?: string
  extension?: string
  path: string
  parentPath: string
  createdAt: Date
  modifiedAt: Date
  permissions: {
    read: boolean
    write: boolean
    execute: boolean
  }
  starred: boolean
  tags: string[]
  preview?: string
  content?: string
}

export interface FileBrowserProps {
  files: FileItem[]
  currentPath: string
  selectedFiles: Set<string>
  viewMode: 'grid' | 'list'
  sortBy: 'name' | 'modified' | 'size' | 'type'
  sortOrder: 'asc' | 'desc'
  searchQuery: string
  filterType: 'all' | 'files' | 'folders' | 'starred'
  onNavigate: (path: string) => void
  onSelectFiles: (fileIds: Set<string>) => void
  onViewModeChange: (mode: 'grid' | 'list') => void
  onSortChange: (sortBy: string, order: 'asc' | 'desc') => void
  onSearchChange: (query: string) => void
  onFilterChange: (filter: string) => void
  onFileAction: (action: string, fileIds: string[]) => void
  onCreateFolder: (name: string) => void
  onUploadFiles: (files: FileList) => void
  onRefresh: () => void
  className?: string
}

const FILE_TYPE_ICONS = {
  folder: Folder,
  'text/plain': FileText,
  'application/javascript': FileCode,
  'text/html': FileCode,
  'text/css': FileCode,
  'application/json': FileCode,
  'image/jpeg': FileImage,
  'image/png': FileImage,
  'image/svg+xml': FileImage,
  'video/mp4': FileVideo,
  'video/avi': FileVideo,
  'audio/mp3': FileAudio,
  'audio/wav': FileAudio,
  default: File
}

const FileBrowser = memo<FileBrowserProps>(({
  files,
  currentPath,
  selectedFiles,
  viewMode,
  sortBy,
  sortOrder,
  searchQuery,
  filterType,
  onNavigate,
  onSelectFiles,
  onViewModeChange,
  onSortChange,
  onSearchChange,
  onFilterChange,
  onFileAction,
  onCreateFolder,
  onUploadFiles,
  onRefresh,
  className
}) => {
  const { reducedMotion, theme } = useUIStore(state => ({
    reducedMotion: state.reducedMotion,
    theme: state.theme
  }))

  const [contextMenu, setContextMenu] = useState<{
    x: number
    y: number
    fileId: string
  } | null>(null)

  const [dragOver, setDragOver] = useState(false)

  // Filter and sort files
  const filteredFiles = useMemo(() => {
    let filtered = files.filter(file => {
      // Search filter
      if (searchQuery && !file.name.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false
      }

      // Type filter
      switch (filterType) {
        case 'files':
          return file.type === 'file'
        case 'folders':
          return file.type === 'folder'
        case 'starred':
          return file.starred
        default:
          return true
      }
    })

    // Sort files
    filtered.sort((a, b) => {
      let comparison = 0

      // Folders first
      if (a.type !== b.type) {
        return a.type === 'folder' ? -1 : 1
      }

      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name)
          break
        case 'modified':
          comparison = a.modifiedAt.getTime() - b.modifiedAt.getTime()
          break
        case 'size':
          comparison = (a.size || 0) - (b.size || 0)
          break
        case 'type':
          comparison = (a.extension || '').localeCompare(b.extension || '')
          break
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return filtered
  }, [files, searchQuery, filterType, sortBy, sortOrder])

  const getFileIcon = useCallback((file: FileItem) => {
    if (file.type === 'folder') {
      return FILE_TYPE_ICONS.folder
    }
    
    const IconComponent = FILE_TYPE_ICONS[file.mimeType as keyof typeof FILE_TYPE_ICONS] || FILE_TYPE_ICONS.default
    return IconComponent
  }, [])

  const formatFileSize = useCallback((bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }, [])

  const handleFileClick = useCallback((file: FileItem, event: React.MouseEvent) => {
    if (event.ctrlKey || event.metaKey) {
      // Toggle selection
      const newSelection = new Set(selectedFiles)
      if (selectedFiles.has(file.id)) {
        newSelection.delete(file.id)
      } else {
        newSelection.add(file.id)
      }
      onSelectFiles(newSelection)
    } else if (event.shiftKey && selectedFiles.size > 0) {
      // Range selection
      const lastSelected = Array.from(selectedFiles)[selectedFiles.size - 1]
      const lastIndex = filteredFiles.findIndex(f => f.id === lastSelected)
      const currentIndex = filteredFiles.findIndex(f => f.id === file.id)
      
      const start = Math.min(lastIndex, currentIndex)
      const end = Math.max(lastIndex, currentIndex)
      
      const rangeSelection = new Set(selectedFiles)
      for (let i = start; i <= end; i++) {
        rangeSelection.add(filteredFiles[i].id)
      }
      onSelectFiles(rangeSelection)
    } else {
      // Single selection or navigation
      if (file.type === 'folder') {
        onNavigate(file.path)
      } else {
        onSelectFiles(new Set([file.id]))
      }
    }
  }, [selectedFiles, filteredFiles, onSelectFiles, onNavigate])

  const handleDoubleClick = useCallback((file: FileItem) => {
    if (file.type === 'folder') {
      onNavigate(file.path)
    } else {
      onFileAction('open', [file.id])
    }
  }, [onNavigate, onFileAction])

  const handleContextMenu = useCallback((event: React.MouseEvent, file: FileItem) => {
    event.preventDefault()
    setContextMenu({
      x: event.clientX,
      y: event.clientY,
      fileId: file.id
    })
  }, [])

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setDragOver(false)
  }, [])

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setDragOver(false)
    
    const files = event.dataTransfer.files
    if (files.length > 0) {
      onUploadFiles(files)
    }
  }, [onUploadFiles])

  const breadcrumbParts = useMemo(() => {
    return currentPath.split('/').filter(Boolean)
  }, [currentPath])

  // Grid Item Component
  const GridItem = memo<{ index: number; style: React.CSSProperties }>(({ index, style }) => {
    const file = filteredFiles[index]
    const IconComponent = getFileIcon(file)
    const isSelected = selectedFiles.has(file.id)

    return (
      <div style={style} className="p-2">
        <div
          className={cn(
            'group relative p-4 rounded-lg border cursor-pointer select-none',
            'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700',
            isSelected && 'border-blue-500 bg-blue-50 dark:bg-blue-950',
            !isSelected && 'border-gray-200 dark:border-gray-700',
            !reducedMotion && 'transition-all duration-200'
          )}
          onClick={(e) => handleFileClick(file, e)}
          onDoubleClick={() => handleDoubleClick(file)}
          onContextMenu={(e) => handleContextMenu(e, file)}
        >
          {/* Selection indicator */}
          {selectedFiles.size > 0 && (
            <div className="absolute top-2 left-2">
              <input
                type="checkbox"
                checked={isSelected}
                readOnly
                className="w-4 h-4 text-blue-600"
              />
            </div>
          )}

          {/* Star indicator */}
          {file.starred && (
            <div className="absolute top-2 right-2">
              <Star className="w-4 h-4 text-yellow-500" fill="currentColor" />
            </div>
          )}

          {/* File icon and name */}
          <div className="flex flex-col items-center text-center">
            <IconComponent className={cn(
              'w-12 h-12 mb-2',
              file.type === 'folder' ? 'text-blue-500' : 'text-gray-500'
            )} />
            
            <div className="w-full">
              <div className="font-medium text-sm text-gray-900 dark:text-gray-100 line-clamp-2 break-words">
                {file.name}
              </div>
              
              <div className="text-xs text-gray-500 mt-1">
                {file.type === 'file' && file.size && (
                  <div>{formatFileSize(file.size)}</div>
                )}
                <div>{format(file.modifiedAt, 'MMM dd, yyyy')}</div>
              </div>
            </div>
          </div>

          {/* Action menu */}
          <div className={cn(
            'absolute bottom-2 right-2 opacity-0 group-hover:opacity-100',
            !reducedMotion && 'transition-opacity duration-200'
          )}>
            <button
              onClick={(e) => {
                e.stopPropagation()
                handleContextMenu(e, file)
              }}
              className="p-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              <MoreVertical className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    )
  })

  // List Item Component
  const ListItem = memo<{ index: number; style: React.CSSProperties }>(({ index, style }) => {
    const file = filteredFiles[index]
    const IconComponent = getFileIcon(file)
    const isSelected = selectedFiles.has(file.id)

    return (
      <div
        style={style}
        className={cn(
          'group flex items-center px-4 py-2 border-b border-gray-100 dark:border-gray-800 cursor-pointer select-none',
          'hover:bg-gray-50 dark:hover:bg-gray-700',
          isSelected && 'bg-blue-50 dark:bg-blue-950',
          !reducedMotion && 'transition-colors duration-200'
        )}
        onClick={(e) => handleFileClick(file, e)}
        onDoubleClick={() => handleDoubleClick(file)}
        onContextMenu={(e) => handleContextMenu(e, file)}
      >
        {/* Checkbox */}
        <div className="w-8 flex justify-center">
          {selectedFiles.size > 0 && (
            <input
              type="checkbox"
              checked={isSelected}
              readOnly
              className="w-4 h-4 text-blue-600"
            />
          )}
        </div>

        {/* Icon */}
        <div className="w-8 flex justify-center mr-3">
          <IconComponent className={cn(
            'w-5 h-5',
            file.type === 'folder' ? 'text-blue-500' : 'text-gray-500'
          )} />
        </div>

        {/* Name */}
        <div className="flex-1 min-w-0 mr-4">
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-900 dark:text-gray-100 truncate">
              {file.name}
            </span>
            {file.starred && <Star className="w-4 h-4 text-yellow-500" fill="currentColor" />}
          </div>
          {file.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {file.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="px-1.5 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded"
                >
                  {tag}
                </span>
              ))}
              {file.tags.length > 3 && (
                <span className="text-xs text-gray-500">+{file.tags.length - 3}</span>
              )}
            </div>
          )}
        </div>

        {/* Size */}
        <div className="w-20 text-right text-sm text-gray-500 mr-4">
          {file.type === 'file' && file.size ? formatFileSize(file.size) : '—'}
        </div>

        {/* Modified date */}
        <div className="w-32 text-right text-sm text-gray-500 mr-4">
          {format(file.modifiedAt, 'MMM dd, yyyy')}
        </div>

        {/* Actions */}
        <div className={cn(
          'w-8 opacity-0 group-hover:opacity-100',
          !reducedMotion && 'transition-opacity duration-200'
        )}>
          <button
            onClick={(e) => {
              e.stopPropagation()
              handleContextMenu(e, file)
            }}
            className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
          >
            <MoreVertical className="w-4 h-4" />
          </button>
        </div>
      </div>
    )
  })

  return (
    <div 
      className={cn('flex flex-col h-full bg-white dark:bg-gray-900', className)}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          {/* Breadcrumbs */}
          <nav className="flex items-center space-x-1">
            <button
              onClick={() => onNavigate('/')}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Root
            </button>
            {breadcrumbParts.map((part, index) => (
              <React.Fragment key={index}>
                <span className="text-gray-400">/</span>
                <button
                  onClick={() => onNavigate('/' + breadcrumbParts.slice(0, index + 1).join('/'))}
                  className={cn(
                    'text-sm',
                    index === breadcrumbParts.length - 1
                      ? 'text-gray-900 dark:text-gray-100 font-medium'
                      : 'text-blue-600 hover:text-blue-800'
                  )}
                >
                  {part}
                </button>
              </React.Fragment>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search files..."
              className="pl-10 pr-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Filter */}
          <select
            value={filterType}
            onChange={(e) => onFilterChange(e.target.value)}
            className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Items</option>
            <option value="files">Files</option>
            <option value="folders">Folders</option>
            <option value="starred">Starred</option>
          </select>

          {/* View Mode */}
          <div className="flex border border-gray-300 dark:border-gray-600 rounded-md overflow-hidden">
            <button
              onClick={() => onViewModeChange('grid')}
              className={cn(
                'p-2 border-r border-gray-300 dark:border-gray-600',
                viewMode === 'grid'
                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-600'
                  : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700'
              )}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => onViewModeChange('list')}
              className={cn(
                'p-2',
                viewMode === 'list'
                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-600'
                  : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700'
              )}
            >
              <ListIcon className="w-4 h-4" />
            </button>
          </div>

          {/* Actions */}
          <button
            onClick={() => {
              const input = document.createElement('input')
              input.type = 'file'
              input.multiple = true
              input.onchange = (e) => {
                const files = (e.target as HTMLInputElement).files
                if (files) onUploadFiles(files)
              }
              input.click()
            }}
            className={cn(
              'p-2 text-blue-600 border border-blue-300 rounded-md hover:bg-blue-50 dark:hover:bg-blue-950',
              !reducedMotion && 'transition-colors duration-200'
            )}
            title="Upload Files"
          >
            <Upload className="w-4 h-4" />
          </button>

          <button
            onClick={() => {
              const name = prompt('Folder name:')
              if (name) onCreateFolder(name)
            }}
            className={cn(
              'p-2 text-green-600 border border-green-300 rounded-md hover:bg-green-50 dark:hover:bg-green-950',
              !reducedMotion && 'transition-colors duration-200'
            )}
            title="Create Folder"
          >
            <Plus className="w-4 h-4" />
          </button>

          <button
            onClick={onRefresh}
            className={cn(
              'p-2 text-gray-600 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700',
              !reducedMotion && 'transition-colors duration-200'
            )}
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* File Grid/List */}
      <div className={cn(
        'flex-1 relative',
        dragOver && 'bg-blue-50 dark:bg-blue-950 border-2 border-dashed border-blue-400'
      )}>
        {filteredFiles.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Folder className="w-16 h-16 mb-4 opacity-50" />
            <div className="text-lg font-medium">
              {searchQuery ? 'No files match your search' : 'This folder is empty'}
            </div>
            <div className="text-sm mt-2">
              {searchQuery ? 'Try a different search term' : 'Upload files or create a new folder to get started'}
            </div>
          </div>
        ) : (
          <AutoSizer>
            {({ height, width }) => (
              viewMode === 'grid' ? (
                <List
                  height={height}
                  width={width}
                  itemCount={Math.ceil(filteredFiles.length / 4)} // 4 items per row
                  itemSize={160}
                  overscanCount={3}
                >
                  {({ index, style }) => (
                    <div style={style} className="flex">
                      {Array.from({ length: 4 }, (_, i) => {
                        const fileIndex = index * 4 + i
                        return fileIndex < filteredFiles.length ? (
                          <div key={fileIndex} className="flex-1">
                            <GridItem index={fileIndex} style={{ height: '100%', width: '100%' }} />
                          </div>
                        ) : (
                          <div key={i} className="flex-1" />
                        )
                      })}
                    </div>
                  )}
                </List>
              ) : (
                <List
                  height={height}
                  width={width}
                  itemCount={filteredFiles.length}
                  itemSize={60}
                  overscanCount={5}
                >
                  {ListItem}
                </List>
              )
            )}
          </AutoSizer>
        )}
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <div
          className="fixed z-50 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg py-1 min-w-32"
          style={{
            left: contextMenu.x,
            top: contextMenu.y
          }}
          onClick={() => setContextMenu(null)}
        >
          <button
            onClick={() => {
              onFileAction('open', [contextMenu.fileId])
              setContextMenu(null)
            }}
            className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
          >
            <Eye className="w-4 h-4" />
            Open
          </button>
          <button
            onClick={() => {
              onFileAction('download', [contextMenu.fileId])
              setContextMenu(null)
            }}
            className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Download
          </button>
          <button
            onClick={() => {
              onFileAction('star', [contextMenu.fileId])
              setContextMenu(null)
            }}
            className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
          >
            <Star className="w-4 h-4" />
            Star
          </button>
          <hr className="my-1 border-gray-200 dark:border-gray-700" />
          <button
            onClick={() => {
              onFileAction('delete', [contextMenu.fileId])
              setContextMenu(null)
            }}
            className="w-full px-3 py-2 text-left text-sm hover:bg-red-50 dark:hover:bg-red-950 text-red-600 flex items-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </button>
        </div>
      )}

      {/* Drag overlay */}
      {dragOver && (
        <div className="absolute inset-0 bg-blue-500/20 flex items-center justify-center backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border-2 border-dashed border-blue-400">
            <Upload className="w-8 h-8 mx-auto mb-2 text-blue-600" />
            <div className="text-lg font-medium text-blue-600">Drop files here</div>
          </div>
        </div>
      )}
    </div>
  )
})

FileBrowser.displayName = 'FileBrowser'

export default FileBrowser
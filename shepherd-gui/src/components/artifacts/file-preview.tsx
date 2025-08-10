'use client'

import React, { memo, useState, useCallback, useMemo } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/cjs/styles/prism'
import {
  FileText,
  FileImage,
  FileVideo,
  FileAudio,
  File as FileIcon,
  Download,
  Edit,
  Copy,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Maximize2,
  Play,
  Pause,
  Volume2,
  VolumeX,
  Eye,
  EyeOff,
  X
} from 'lucide-react'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'
import type { FileItem } from './file-browser'

export interface FilePreviewProps {
  file: FileItem | null
  onClose: () => void
  onEdit?: (file: FileItem) => void
  onDownload?: (file: FileItem) => void
  className?: string
}

const SUPPORTED_CODE_LANGUAGES = {
  'js': 'javascript',
  'jsx': 'javascript',
  'ts': 'typescript',
  'tsx': 'typescript',
  'py': 'python',
  'html': 'html',
  'css': 'css',
  'scss': 'scss',
  'json': 'json',
  'xml': 'xml',
  'md': 'markdown',
  'sql': 'sql',
  'sh': 'bash',
  'yml': 'yaml',
  'yaml': 'yaml'
}

const SUPPORTED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/svg+xml', 'image/webp']
const SUPPORTED_VIDEO_TYPES = ['video/mp4', 'video/webm', 'video/ogg', 'video/avi', 'video/mov']
const SUPPORTED_AUDIO_TYPES = ['audio/mp3', 'audio/wav', 'audio/ogg', 'audio/aac', 'audio/flac']

const FilePreview = memo<FilePreviewProps>(({ file, onClose, onEdit, onDownload, className }) => {
  const { theme, reducedMotion } = useUIStore(state => ({
    theme: state.theme,
    reducedMotion: state.reducedMotion
  }))

  const [imageZoom, setImageZoom] = useState(100)
  const [imageRotation, setImageRotation] = useState(0)
  const [videoPlaying, setVideoPlaying] = useState(false)
  const [videoMuted, setVideoMuted] = useState(false)
  const [audioPlaying, setAudioPlaying] = useState(false)
  const [audioMuted, setAudioMuted] = useState(false)
  const [showRaw, setShowRaw] = useState(false)

  if (!file) return null

  const getLanguage = useCallback((extension: string): string => {
    return SUPPORTED_CODE_LANGUAGES[extension.toLowerCase() as keyof typeof SUPPORTED_CODE_LANGUAGES] || 'text'
  }, [])

  const isCodeFile = useMemo(() => {
    if (!file.extension) return false
    return file.extension.toLowerCase() in SUPPORTED_CODE_LANGUAGES
  }, [file.extension])

  const isImageFile = useMemo(() => {
    return file.mimeType ? SUPPORTED_IMAGE_TYPES.includes(file.mimeType) : false
  }, [file.mimeType])

  const isVideoFile = useMemo(() => {
    return file.mimeType ? SUPPORTED_VIDEO_TYPES.includes(file.mimeType) : false
  }, [file.mimeType])

  const isAudioFile = useMemo(() => {
    return file.mimeType ? SUPPORTED_AUDIO_TYPES.includes(file.mimeType) : false
  }, [file.mimeType])

  const isTextFile = useMemo(() => {
    return file.mimeType?.startsWith('text/') || isCodeFile
  }, [file.mimeType, isCodeFile])

  const handleCopyContent = useCallback(async () => {
    if (file.content) {
      try {
        await navigator.clipboard.writeText(file.content)
        // You would show a toast notification here
      } catch (error) {
        console.error('Failed to copy content:', error)
      }
    }
  }, [file.content])

  const handleZoom = useCallback((direction: 'in' | 'out' | 'reset') => {
    setImageZoom(prev => {
      switch (direction) {
        case 'in':
          return Math.min(prev + 25, 500)
        case 'out':
          return Math.max(prev - 25, 25)
        case 'reset':
          return 100
        default:
          return prev
      }
    })
  }, [])

  const handleRotate = useCallback(() => {
    setImageRotation(prev => (prev + 90) % 360)
  }, [])

  const formatFileSize = useCallback((bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }, [])

  const renderPreviewContent = () => {
    // Image preview
    if (isImageFile) {
      return (
        <div className="flex-1 flex items-center justify-center bg-gray-100 dark:bg-gray-800 p-4 overflow-auto">
          <div className="relative max-w-full max-h-full">
            <img
              src={file.path}
              alt={file.name}
              className={cn(
                'max-w-full max-h-full object-contain',
                !reducedMotion && 'transition-transform duration-200'
              )}
              style={{
                transform: `scale(${imageZoom / 100}) rotate(${imageRotation}deg)`
              }}
            />
          </div>
        </div>
      )
    }

    // Video preview
    if (isVideoFile) {
      return (
        <div className="flex-1 flex items-center justify-center bg-black p-4">
          <video
            src={file.path}
            controls
            className="max-w-full max-h-full"
            onPlay={() => setVideoPlaying(true)}
            onPause={() => setVideoPlaying(false)}
            muted={videoMuted}
          />
        </div>
      )
    }

    // Audio preview
    if (isAudioFile) {
      return (
        <div className="flex-1 flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-800 p-8">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-8 shadow-lg max-w-md w-full">
            <div className="text-center mb-6">
              <FileAudio className="w-16 h-16 mx-auto text-blue-500 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                {file.name}
              </h3>
              {file.size && (
                <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
              )}
            </div>
            
            <audio
              src={file.path}
              controls
              className="w-full"
              onPlay={() => setAudioPlaying(true)}
              onPause={() => setAudioPlaying(false)}
            />
          </div>
        </div>
      )
    }

    // Code/Text preview
    if (isTextFile && file.content) {
      return (
        <div className="flex-1 overflow-auto">
          {showRaw || !isCodeFile ? (
            <pre className="p-6 text-sm font-mono whitespace-pre-wrap break-words text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-900">
              {file.content}
            </pre>
          ) : (
            <SyntaxHighlighter
              language={getLanguage(file.extension || '')}
              style={theme === 'dark' ? oneDark : oneLight}
              customStyle={{
                margin: 0,
                padding: '1.5rem',
                fontSize: '0.875rem',
                lineHeight: '1.5'
              }}
              showLineNumbers
              wrapLines
            >
              {file.content}
            </SyntaxHighlighter>
          )}
        </div>
      )
    }

    // Fallback for unsupported files
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-gray-500 p-8">
        <FileIcon className="w-16 h-16 mb-4 opacity-50" />
        <h3 className="text-lg font-medium mb-2">Preview not available</h3>
        <p className="text-sm text-center mb-6">
          This file type cannot be previewed in the browser.<br />
          You can download it to view with an appropriate application.
        </p>
        <button
          onClick={() => onDownload?.(file)}
          className={cn(
            'flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700',
            !reducedMotion && 'transition-colors duration-200'
          )}
        >
          <Download className="w-4 h-4" />
          Download File
        </button>
      </div>
    )
  }

  return (
    <div className={cn(
      'fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center',
      className
    )}>
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-2xl max-w-6xl max-h-[90vh] w-full h-full mx-4 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <div className="flex-shrink-0">
              {isImageFile && <FileImage className="w-5 h-5 text-blue-500" />}
              {isVideoFile && <FileVideo className="w-5 h-5 text-red-500" />}
              {isAudioFile && <FileAudio className="w-5 h-5 text-green-500" />}
              {isTextFile && <FileText className="w-5 h-5 text-purple-500" />}
              {!isImageFile && !isVideoFile && !isAudioFile && !isTextFile && (
                <FileIcon className="w-5 h-5 text-gray-500" />
              )}
            </div>
            
            <div className="min-w-0 flex-1">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 truncate">
                {file.name}
              </h2>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                {file.size && <span>{formatFileSize(file.size)}</span>}
                <span>Modified {format(file.modifiedAt, 'MMM dd, yyyy HH:mm')}</span>
                {file.mimeType && <span>{file.mimeType}</span>}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            {/* Image controls */}
            {isImageFile && (
              <>
                <button
                  onClick={() => handleZoom('out')}
                  disabled={imageZoom <= 25}
                  className="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 disabled:opacity-50"
                  title="Zoom Out"
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                
                <span className="text-sm text-gray-500 min-w-[4ch] text-center">
                  {imageZoom}%
                </span>
                
                <button
                  onClick={() => handleZoom('in')}
                  disabled={imageZoom >= 500}
                  className="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 disabled:opacity-50"
                  title="Zoom In"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
                
                <button
                  onClick={handleRotate}
                  className="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                  title="Rotate"
                >
                  <RotateCw className="w-4 h-4" />
                </button>
              </>
            )}

            {/* Code/Text controls */}
            {isTextFile && isCodeFile && (
              <button
                onClick={() => setShowRaw(!showRaw)}
                className={cn(
                  'p-2 rounded',
                  showRaw
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-600'
                    : 'text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200'
                )}
                title={showRaw ? 'Show Syntax Highlighting' : 'Show Raw Text'}
              >
                {showRaw ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
              </button>
            )}

            {/* Common actions */}
            {file.content && (
              <button
                onClick={handleCopyContent}
                className="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                title="Copy Content"
              >
                <Copy className="w-4 h-4" />
              </button>
            )}

            {onEdit && (
              <button
                onClick={() => onEdit(file)}
                className="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                title="Edit File"
              >
                <Edit className="w-4 h-4" />
              </button>
            )}

            {onDownload && (
              <button
                onClick={() => onDownload(file)}
                className="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                title="Download File"
              >
                <Download className="w-4 h-4" />
              </button>
            )}

            <button
              onClick={onClose}
              className="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        {renderPreviewContent()}

        {/* Footer with metadata */}
        {file.tags.length > 0 && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Tags:</span>
              <div className="flex flex-wrap gap-1">
                {file.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
})

FilePreview.displayName = 'FilePreview'

export default FilePreview
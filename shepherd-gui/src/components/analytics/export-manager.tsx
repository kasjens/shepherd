'use client'

import React, { useState, useCallback, useRef } from 'react'
import { 
  Download, 
  FileText, 
  Image, 
  FileSpreadsheet, 
  Archive,
  Settings,
  X,
  Check,
  AlertCircle,
  Clock,
  ChevronDown
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { ChartWidget, DashboardData } from './advanced-dashboard'

export type ExportFormat = 'png' | 'pdf' | 'json' | 'csv' | 'excel' | 'svg'

export interface ExportOptions {
  format: ExportFormat
  includeWidgets?: string[] // Widget IDs to include
  includeMeta?: boolean
  quality?: number // For image formats
  pageSize?: 'A4' | 'Letter' | 'A3'
  orientation?: 'portrait' | 'landscape'
  dateRange?: {
    start: Date
    end: Date
  }
  filters?: Record<string, any>
}

export interface ExportJob {
  id: string
  format: ExportFormat
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress: number
  startTime: Date
  endTime?: Date
  error?: string
  downloadUrl?: string
  fileName: string
  options: ExportOptions
}

interface ExportManagerProps {
  widgets: ChartWidget[]
  data: DashboardData
  onClose?: () => void
  className?: string
}

// Web Worker for export processing
const createExportWorker = () => {
  if (typeof Worker === 'undefined') return null
  
  const workerCode = `
    self.onmessage = function(e) {
      const { type, data, options } = e.data;
      
      try {
        let result;
        
        switch (type) {
          case 'csv':
            result = convertToCSV(data, options);
            break;
          case 'json':
            result = convertToJSON(data, options);
            break;
          case 'excel':
            result = convertToExcel(data, options);
            break;
          default:
            throw new Error('Unsupported export format');
        }
        
        self.postMessage({ success: true, data: result });
      } catch (error) {
        self.postMessage({ success: false, error: error.message });
      }
    };
    
    function convertToCSV(data, options) {
      const headers = [];
      const rows = [];
      
      // Extract all unique headers
      const allKeys = new Set();
      Object.values(data).forEach(dataset => {
        if (Array.isArray(dataset)) {
          dataset.forEach(item => {
            Object.keys(item).forEach(key => allKeys.add(key));
          });
        }
      });
      
      headers.push(...Array.from(allKeys));
      
      // Add data rows
      Object.entries(data).forEach(([source, dataset]) => {
        if (Array.isArray(dataset)) {
          dataset.forEach(item => {
            const row = headers.map(header => {
              const value = item[header];
              if (typeof value === 'string' && value.includes(',')) {
                return '"' + value.replace(/"/g, '""') + '"';
              }
              return value || '';
            });
            rows.push(row.join(','));
          });
        }
      });
      
      return headers.join(',') + '\\n' + rows.join('\\n');
    }
    
    function convertToJSON(data, options) {
      const exportData = {
        exported: new Date().toISOString(),
        options: options,
        data: data
      };
      
      if (options.includeMeta) {
        exportData.meta = {
          totalRecords: Object.values(data).reduce((sum, dataset) => 
            sum + (Array.isArray(dataset) ? dataset.length : 0), 0
          ),
          dataSources: Object.keys(data).length
        };
      }
      
      return JSON.stringify(exportData, null, 2);
    }
    
    function convertToExcel(data, options) {
      // Basic Excel-compatible CSV format
      // In a real implementation, you'd use a library like xlsx
      return convertToCSV(data, options);
    }
  `
  
  const blob = new Blob([workerCode], { type: 'application/javascript' })
  return new Worker(URL.createObjectURL(blob))
}

export function ExportManager({ widgets, data, onClose, className }: ExportManagerProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('json')
  const [selectedWidgets, setSelectedWidgets] = useState<string[]>(widgets.map(w => w.id))
  const [exportOptions, setExportOptions] = useState<Partial<ExportOptions>>({
    includeMeta: true,
    quality: 90,
    pageSize: 'A4',
    orientation: 'landscape'
  })
  const [jobs, setJobs] = useState<ExportJob[]>([])
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false)
  
  const workerRef = useRef<Worker | null>(null)

  // Initialize worker
  React.useEffect(() => {
    workerRef.current = createExportWorker()
    return () => {
      if (workerRef.current) {
        workerRef.current.terminate()
      }
    }
  }, [])

  const createJob = useCallback((format: ExportFormat, options: ExportOptions): ExportJob => {
    const jobId = `export_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const fileName = `dashboard_export_${new Date().toISOString().split('T')[0]}.${format}`
    
    return {
      id: jobId,
      format,
      status: 'pending',
      progress: 0,
      startTime: new Date(),
      fileName,
      options
    }
  }, [])

  const startExport = useCallback(async () => {
    const options: ExportOptions = {
      format: selectedFormat,
      includeWidgets: selectedWidgets,
      ...exportOptions
    }
    
    const job = createJob(selectedFormat, options)
    setJobs(prev => [job, ...prev])

    // Update job status
    const updateJob = (updates: Partial<ExportJob>) => {
      setJobs(prev => prev.map(j => j.id === job.id ? { ...j, ...updates } : j))
    }

    updateJob({ status: 'processing', progress: 10 })

    try {
      // Filter data based on selected widgets
      const filteredData: DashboardData = {}
      selectedWidgets.forEach(widgetId => {
        const widget = widgets.find(w => w.id === widgetId)
        if (widget && data[widget.dataSource]) {
          filteredData[widget.dataSource] = data[widget.dataSource]
        }
      })

      updateJob({ progress: 30 })

      let result: string | Blob
      let mimeType: string
      let fileExtension: string

      switch (selectedFormat) {
        case 'json':
        case 'csv':
          // Use Web Worker for data processing
          if (workerRef.current) {
            const workerResult = await new Promise<any>((resolve, reject) => {
              if (!workerRef.current) {
                reject(new Error('Worker not available'))
                return
              }

              workerRef.current.postMessage({
                type: selectedFormat,
                data: filteredData,
                options
              })

              workerRef.current.onmessage = (e) => {
                const { success, data, error } = e.data
                if (success) {
                  resolve(data)
                } else {
                  reject(new Error(error))
                }
              }

              setTimeout(() => reject(new Error('Export timeout')), 30000)
            })

            result = workerResult
            mimeType = selectedFormat === 'json' ? 'application/json' : 'text/csv'
            fileExtension = selectedFormat
          } else {
            throw new Error('Worker not supported')
          }
          break

        case 'png':
        case 'pdf':
          // For image/PDF export, we'd need to render the charts
          result = await exportAsImage(selectedWidgets, widgets, options)
          mimeType = selectedFormat === 'png' ? 'image/png' : 'application/pdf'
          fileExtension = selectedFormat
          break

        case 'excel':
          // Use Web Worker for Excel processing
          result = await new Promise<string>((resolve, reject) => {
            if (!workerRef.current) {
              reject(new Error('Worker not available'))
              return
            }

            workerRef.current.postMessage({
              type: 'excel',
              data: filteredData,
              options
            })

            workerRef.current.onmessage = (e) => {
              const { success, data, error } = e.data
              if (success) {
                resolve(data)
              } else {
                reject(new Error(error))
              }
            }
          })
          mimeType = 'application/vnd.ms-excel'
          fileExtension = 'csv' // Simplified Excel format
          break

        default:
          throw new Error('Unsupported format')
      }

      updateJob({ progress: 80 })

      // Create download blob
      const blob = typeof result === 'string' 
        ? new Blob([result], { type: mimeType })
        : result

      const downloadUrl = URL.createObjectURL(blob)
      const finalFileName = job.fileName.replace(/\.[^.]+$/, `.${fileExtension}`)

      updateJob({
        status: 'completed',
        progress: 100,
        endTime: new Date(),
        downloadUrl,
        fileName: finalFileName
      })

      // Auto-download
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = finalFileName
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)

    } catch (error) {
      updateJob({
        status: 'error',
        progress: 0,
        endTime: new Date(),
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    }
  }, [selectedFormat, selectedWidgets, exportOptions, widgets, data, createJob])

  // Image export using canvas
  const exportAsImage = async (widgetIds: string[], widgets: ChartWidget[], options: ExportOptions): Promise<Blob> => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    if (!ctx) throw new Error('Canvas context not available')

    // Set canvas size based on page format
    const dimensions = {
      A4: { width: 2480, height: 3508 }, // 300 DPI
      Letter: { width: 2550, height: 3300 },
      A3: { width: 3508, height: 4961 }
    }

    const { width, height } = dimensions[options.pageSize || 'A4']
    canvas.width = options.orientation === 'portrait' ? width : height
    canvas.height = options.orientation === 'portrait' ? height : width

    // White background
    ctx.fillStyle = '#FFFFFF'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // This is a simplified implementation
    // In a real scenario, you'd render each widget's chart to the canvas
    ctx.fillStyle = '#000000'
    ctx.font = '48px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('Dashboard Export', canvas.width / 2, 100)

    ctx.font = '24px sans-serif'
    ctx.fillText(`${widgetIds.length} widgets exported`, canvas.width / 2, 200)
    ctx.fillText(new Date().toLocaleDateString(), canvas.width / 2, 250)

    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        resolve(blob!)
      }, `image/${options.format}`, (options.quality || 90) / 100)
    })
  }

  const deleteJob = useCallback((jobId: string) => {
    setJobs(prev => {
      const job = prev.find(j => j.id === jobId)
      if (job?.downloadUrl) {
        URL.revokeObjectURL(job.downloadUrl)
      }
      return prev.filter(j => j.id !== jobId)
    })
  }, [])

  const downloadJob = useCallback((job: ExportJob) => {
    if (job.downloadUrl) {
      const a = document.createElement('a')
      a.href = job.downloadUrl
      a.download = job.fileName
      a.click()
    }
  }, [])

  const formatIcons = {
    png: Image,
    pdf: FileText,
    json: Archive,
    csv: FileSpreadsheet,
    excel: FileSpreadsheet,
    svg: Image
  }

  return (
    <div className={cn('bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg', className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <Download className="w-5 h-5 text-blue-500" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Export Dashboard
          </h3>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <div className="p-4 space-y-6">
        {/* Format Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Export Format
          </label>
          <div className="grid grid-cols-3 gap-2">
            {(Object.keys(formatIcons) as ExportFormat[]).map((format) => {
              const Icon = formatIcons[format]
              return (
                <button
                  key={format}
                  onClick={() => setSelectedFormat(format)}
                  className={cn(
                    'flex items-center gap-2 p-3 border rounded-md text-sm font-medium',
                    selectedFormat === format
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300'
                      : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {format.toUpperCase()}
                </button>
              )
            })}
          </div>
        </div>

        {/* Widget Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Widgets to Export ({selectedWidgets.length} of {widgets.length})
          </label>
          <div className="max-h-32 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded-md">
            {widgets.map((widget) => (
              <label key={widget.id} className="flex items-center gap-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700">
                <input
                  type="checkbox"
                  checked={selectedWidgets.includes(widget.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedWidgets(prev => [...prev, widget.id])
                    } else {
                      setSelectedWidgets(prev => prev.filter(id => id !== widget.id))
                    }
                  }}
                  className="rounded border-gray-300"
                />
                <span className="text-sm">{widget.title}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Advanced Options */}
        <div>
          <button
            onClick={() => setIsAdvancedOpen(!isAdvancedOpen)}
            className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            <ChevronDown className={cn('w-4 h-4 transition-transform', isAdvancedOpen && 'rotate-180')} />
            Advanced Options
          </button>
          
          {isAdvancedOpen && (
            <div className="mt-3 space-y-4 pl-6">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={exportOptions.includeMeta || false}
                  onChange={(e) => setExportOptions(prev => ({ ...prev, includeMeta: e.target.checked }))}
                  className="rounded border-gray-300"
                />
                <span className="text-sm">Include metadata</span>
              </label>

              {(selectedFormat === 'png' || selectedFormat === 'pdf') && (
                <>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Quality ({exportOptions.quality}%)
                    </label>
                    <input
                      type="range"
                      min="10"
                      max="100"
                      value={exportOptions.quality || 90}
                      onChange={(e) => setExportOptions(prev => ({ ...prev, quality: Number(e.target.value) }))}
                      className="w-full"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Page Size
                      </label>
                      <select
                        value={exportOptions.pageSize || 'A4'}
                        onChange={(e) => setExportOptions(prev => ({ ...prev, pageSize: e.target.value as 'A4' | 'Letter' | 'A3' }))}
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded text-sm"
                      >
                        <option value="A4">A4</option>
                        <option value="Letter">Letter</option>
                        <option value="A3">A3</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Orientation
                      </label>
                      <select
                        value={exportOptions.orientation || 'landscape'}
                        onChange={(e) => setExportOptions(prev => ({ ...prev, orientation: e.target.value as 'portrait' | 'landscape' }))}
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded text-sm"
                      >
                        <option value="portrait">Portrait</option>
                        <option value="landscape">Landscape</option>
                      </select>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* Export Button */}
        <button
          onClick={startExport}
          disabled={selectedWidgets.length === 0}
          className={cn(
            'w-full py-3 px-4 rounded-md font-medium',
            selectedWidgets.length > 0
              ? 'bg-blue-500 hover:bg-blue-600 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          )}
        >
          Export {selectedWidgets.length} Widget{selectedWidgets.length !== 1 ? 's' : ''}
        </button>

        {/* Export Jobs */}
        {jobs.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Recent Exports
            </h4>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {jobs.map((job) => (
                <div
                  key={job.id}
                  className="flex items-center gap-3 p-2 border border-gray-200 dark:border-gray-600 rounded text-sm"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      {job.status === 'completed' && <Check className="w-4 h-4 text-green-500" />}
                      {job.status === 'processing' && <Clock className="w-4 h-4 text-yellow-500 animate-spin" />}
                      {job.status === 'error' && <AlertCircle className="w-4 h-4 text-red-500" />}
                      <span className="font-medium truncate">{job.fileName}</span>
                    </div>
                    {job.status === 'processing' && (
                      <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                        <div
                          className="bg-blue-500 h-1 rounded-full transition-all"
                          style={{ width: `${job.progress}%` }}
                        />
                      </div>
                    )}
                    {job.error && (
                      <div className="text-red-500 text-xs mt-1">{job.error}</div>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-1">
                    {job.status === 'completed' && job.downloadUrl && (
                      <button
                        onClick={() => downloadJob(job)}
                        className="p-1 text-blue-500 hover:text-blue-700"
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={() => deleteJob(job.id)}
                      className="p-1 text-gray-400 hover:text-red-500"
                      title="Remove"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
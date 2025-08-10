'use client'

import React, { useEffect, useRef, useCallback } from 'react'
import { ChartConfig } from '../advanced-dashboard'

export interface LineChartProps {
  data: any[]
  config: ChartConfig
  width: string | number
  height: string | number
  onError?: (error: string) => void
  onLoadingChange?: (isLoading: boolean) => void
}

// Web Worker for data processing
const createDataWorker = () => {
  if (typeof Worker === 'undefined') return null
  
  const workerCode = `
    self.onmessage = function(e) {
      const { data, config } = e.data;
      
      try {
        // Process data for line chart
        const processedData = data.map(item => ({
          x: item[config.xAxis] || item.timestamp,
          y: item[config.yAxis] || item.value,
          label: item.label || item.name
        }));
        
        // Sort by x-axis
        processedData.sort((a, b) => new Date(a.x).getTime() - new Date(b.x).getTime());
        
        self.postMessage({ success: true, data: processedData });
      } catch (error) {
        self.postMessage({ success: false, error: error.message });
      }
    };
  `
  
  const blob = new Blob([workerCode], { type: 'application/javascript' })
  return new Worker(URL.createObjectURL(blob))
}

export default function LineChart({ data, config, width, height, onError, onLoadingChange }: LineChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const workerRef = useRef<Worker | null>(null)
  const animationRef = useRef<number>(0)

  // Initialize worker
  useEffect(() => {
    workerRef.current = createDataWorker()
    return () => {
      if (workerRef.current) {
        workerRef.current.terminate()
      }
    }
  }, [])

  // Draw chart using Canvas API
  const drawChart = useCallback((processedData: any[]) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const rect = canvas.getBoundingClientRect()
    const dpr = window.devicePixelRatio || 1
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    ctx.scale(dpr, dpr)

    // Clear canvas
    ctx.clearRect(0, 0, rect.width, rect.height)

    if (processedData.length === 0) {
      // Draw "No data" message
      ctx.fillStyle = '#9CA3AF'
      ctx.font = '14px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('No data available', rect.width / 2, rect.height / 2)
      return
    }

    // Chart margins
    const margin = { top: 20, right: 40, bottom: 40, left: 60 }
    const chartWidth = rect.width - margin.left - margin.right
    const chartHeight = rect.height - margin.top - margin.bottom

    // Calculate scales
    const xValues = processedData.map(d => new Date(d.x).getTime())
    const yValues = processedData.map(d => d.y)
    
    const xMin = Math.min(...xValues)
    const xMax = Math.max(...xValues)
    const yMin = Math.min(...yValues) * 0.9
    const yMax = Math.max(...yValues) * 1.1

    const xScale = (x: number) => margin.left + ((x - xMin) / (xMax - xMin)) * chartWidth
    const yScale = (y: number) => margin.top + chartHeight - ((y - yMin) / (yMax - yMin)) * chartHeight

    // Draw grid
    if (config.showGrid !== false) {
      ctx.strokeStyle = '#E5E7EB'
      ctx.lineWidth = 1
      ctx.setLineDash([2, 2])

      // Horizontal grid lines
      for (let i = 0; i <= 5; i++) {
        const y = margin.top + (chartHeight / 5) * i
        ctx.beginPath()
        ctx.moveTo(margin.left, y)
        ctx.lineTo(margin.left + chartWidth, y)
        ctx.stroke()
      }

      // Vertical grid lines
      for (let i = 0; i <= 5; i++) {
        const x = margin.left + (chartWidth / 5) * i
        ctx.beginPath()
        ctx.moveTo(x, margin.top)
        ctx.lineTo(x, margin.top + chartHeight)
        ctx.stroke()
      }

      ctx.setLineDash([])
    }

    // Draw axes
    ctx.strokeStyle = '#374151'
    ctx.lineWidth = 2

    // Y-axis
    ctx.beginPath()
    ctx.moveTo(margin.left, margin.top)
    ctx.lineTo(margin.left, margin.top + chartHeight)
    ctx.stroke()

    // X-axis
    ctx.beginPath()
    ctx.moveTo(margin.left, margin.top + chartHeight)
    ctx.lineTo(margin.left + chartWidth, margin.top + chartHeight)
    ctx.stroke()

    // Draw labels
    ctx.fillStyle = '#6B7280'
    ctx.font = '12px sans-serif'
    ctx.textAlign = 'center'

    // Y-axis labels
    for (let i = 0; i <= 5; i++) {
      const value = yMin + ((yMax - yMin) / 5) * i
      const y = yScale(value)
      ctx.textAlign = 'right'
      ctx.fillText(value.toFixed(1), margin.left - 10, y + 4)
    }

    // X-axis labels
    for (let i = 0; i <= 5; i++) {
      const timestamp = xMin + ((xMax - xMin) / 5) * i
      const x = xScale(timestamp)
      ctx.textAlign = 'center'
      const date = new Date(timestamp)
      ctx.fillText(
        date.toLocaleDateString(), 
        x, 
        margin.top + chartHeight + 20
      )
    }

    // Draw line
    const colors = config.colors || ['#3B82F6', '#EF4444', '#10B981']
    ctx.strokeStyle = colors[0]
    ctx.lineWidth = 2
    ctx.lineJoin = 'round'
    ctx.lineCap = 'round'

    ctx.beginPath()
    processedData.forEach((point, index) => {
      const x = xScale(new Date(point.x).getTime())
      const y = yScale(point.y)
      
      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })
    ctx.stroke()

    // Draw points
    ctx.fillStyle = colors[0]
    processedData.forEach(point => {
      const x = xScale(new Date(point.x).getTime())
      const y = yScale(point.y)
      
      ctx.beginPath()
      ctx.arc(x, y, 4, 0, Math.PI * 2)
      ctx.fill()
    })

    // Draw hover effects (simple implementation)
    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect()
      const mouseX = e.clientX - rect.left
      const mouseY = e.clientY - rect.top

      // Find nearest point
      let nearestPoint: any = null
      let minDistance = Infinity

      processedData.forEach(point => {
        const x = xScale(new Date(point.x).getTime())
        const y = yScale(point.y)
        const distance = Math.sqrt((mouseX - x) ** 2 + (mouseY - y) ** 2)
        
        if (distance < minDistance && distance < 20) {
          minDistance = distance
          nearestPoint = { ...point, screenX: x, screenY: y }
        }
      })

      // Show tooltip for nearest point
      if (nearestPoint) {
        canvas.title = `${nearestPoint.label || 'Value'}: ${nearestPoint.y} at ${new Date(nearestPoint.x).toLocaleString()}`
        canvas.style.cursor = 'pointer'
      } else {
        canvas.title = ''
        canvas.style.cursor = 'default'
      }
    })

  }, [config])

  // Process data and render chart
  useEffect(() => {
    if (!data || data.length === 0) {
      drawChart([])
      return
    }

    onLoadingChange?.(true)

    if (workerRef.current) {
      // Use web worker for data processing
      workerRef.current.postMessage({ data, config })
      
      workerRef.current.onmessage = (e) => {
        const { success, data: processedData, error } = e.data
        
        if (success) {
          // Animate chart rendering if enabled
          if (config.animate !== false) {
            let progress = 0
            const animate = () => {
              progress += 0.1
              if (progress <= 1) {
                const animatedData = processedData.slice(0, Math.floor(processedData.length * progress))
                drawChart(animatedData)
                animationRef.current = requestAnimationFrame(animate)
              } else {
                drawChart(processedData)
                onLoadingChange?.(false)
              }
            }
            animate()
          } else {
            drawChart(processedData)
            onLoadingChange?.(false)
          }
        } else {
          onError?.(error)
          onLoadingChange?.(false)
        }
      }
    } else {
      // Fallback: process data on main thread
      try {
        const processedData = data.map((item: any) => {
          const yAxisKey = Array.isArray(config.yAxis) ? config.yAxis[0] : config.yAxis || 'value'
          return {
            x: item[config.xAxis || 'timestamp'],
            y: item[yAxisKey],
            label: item.label || item.name
          }
        }).sort((a, b) => new Date(a.x).getTime() - new Date(b.x).getTime())
        
        drawChart(processedData)
        onLoadingChange?.(false)
      } catch (error) {
        onError?.(error instanceof Error ? error.message : 'Unknown error')
        onLoadingChange?.(false)
      }
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [data, config, drawChart, onError, onLoadingChange])

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      if (canvasRef.current) {
        // Redraw chart on resize
        setTimeout(() => drawChart([]), 100)
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [drawChart])

  return (
    <div className="w-full h-full relative">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ width, height }}
      />
    </div>
  )
}
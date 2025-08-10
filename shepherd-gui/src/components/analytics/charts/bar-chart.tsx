'use client'

import React, { useEffect, useRef, useCallback } from 'react'
import { ChartConfig } from '../advanced-dashboard'

export interface BarChartProps {
  data: any[]
  config: ChartConfig
  width: string | number
  height: string | number
  onError?: (error: string) => void
  onLoadingChange?: (isLoading: boolean) => void
}

export default function BarChart({ data, config, width, height, onError, onLoadingChange }: BarChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>(0)

  const drawChart = useCallback((processedData: any[], animationProgress = 1) => {
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
      ctx.fillStyle = '#9CA3AF'
      ctx.font = '14px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('No data available', rect.width / 2, rect.height / 2)
      return
    }

    // Chart margins
    const margin = { top: 20, right: 40, bottom: 60, left: 60 }
    const chartWidth = rect.width - margin.left - margin.right
    const chartHeight = rect.height - margin.top - margin.bottom

    // Calculate scales
    const yValues = processedData.map(d => d.y)
    const yMax = Math.max(...yValues) * 1.1
    const yMin = Math.min(0, Math.min(...yValues) * 0.9)

    const barWidth = chartWidth / processedData.length * 0.8
    const barSpacing = chartWidth / processedData.length * 0.2

    // Draw grid
    if (config.showGrid !== false) {
      ctx.strokeStyle = '#E5E7EB'
      ctx.lineWidth = 1
      ctx.setLineDash([2, 2])

      for (let i = 0; i <= 5; i++) {
        const y = margin.top + (chartHeight / 5) * i
        ctx.beginPath()
        ctx.moveTo(margin.left, y)
        ctx.lineTo(margin.left + chartWidth, y)
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

    // Draw Y-axis labels
    ctx.fillStyle = '#6B7280'
    ctx.font = '12px sans-serif'
    ctx.textAlign = 'right'

    for (let i = 0; i <= 5; i++) {
      const value = yMin + ((yMax - yMin) / 5) * (5 - i)
      const y = margin.top + (chartHeight / 5) * i
      ctx.fillText(value.toFixed(1), margin.left - 10, y + 4)
    }

    // Colors
    const colors = config.colors || ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6']

    // Draw bars
    processedData.forEach((item, index) => {
      const x = margin.left + (chartWidth / processedData.length) * index + barSpacing / 2
      const barHeight = ((item.y - yMin) / (yMax - yMin)) * chartHeight * animationProgress
      const y = margin.top + chartHeight - barHeight

      // Bar
      ctx.fillStyle = colors[index % colors.length]
      ctx.fillRect(x, y, barWidth, barHeight)

      // Bar border
      ctx.strokeStyle = '#FFFFFF'
      ctx.lineWidth = 1
      ctx.strokeRect(x, y, barWidth, barHeight)

      // X-axis labels
      ctx.fillStyle = '#6B7280'
      ctx.font = '11px sans-serif'
      ctx.textAlign = 'center'
      
      // Rotate text if needed
      const labelWidth = ctx.measureText(item.label || item.x).width
      if (labelWidth > barWidth * 1.5) {
        ctx.save()
        ctx.translate(x + barWidth / 2, margin.top + chartHeight + 15)
        ctx.rotate(-Math.PI / 4)
        ctx.fillText(item.label || item.x, 0, 0)
        ctx.restore()
      } else {
        ctx.fillText(item.label || item.x, x + barWidth / 2, margin.top + chartHeight + 15)
      }

      // Value labels on bars
      if (barHeight > 20) {
        ctx.fillStyle = '#FFFFFF'
        ctx.font = '10px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(item.y.toString(), x + barWidth / 2, y + barHeight / 2 + 3)
      }
    })

    // Interactive hover effects
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      const mouseX = e.clientX - rect.left
      const mouseY = e.clientY - rect.top

      let hoveredBar = -1
      processedData.forEach((item, index) => {
        const x = margin.left + (chartWidth / processedData.length) * index + barSpacing / 2
        const barHeight = ((item.y - yMin) / (yMax - yMin)) * chartHeight
        const y = margin.top + chartHeight - barHeight

        if (mouseX >= x && mouseX <= x + barWidth && mouseY >= y && mouseY <= y + barHeight) {
          hoveredBar = index
        }
      })

      if (hoveredBar >= 0) {
        const item = processedData[hoveredBar]
        canvas.title = `${item.label || item.x}: ${item.y}`
        canvas.style.cursor = 'pointer'
      } else {
        canvas.title = ''
        canvas.style.cursor = 'default'
      }
    }

    canvas.removeEventListener('mousemove', handleMouseMove)
    canvas.addEventListener('mousemove', handleMouseMove)

  }, [config])

  // Process data and render chart
  useEffect(() => {
    onLoadingChange?.(true)

    try {
      // Process data
      const processedData = data.map((item: any, index) => {
        const yAxisKey = Array.isArray(config.yAxis) ? config.yAxis[0] : config.yAxis || 'value'
        return {
          x: item[config.xAxis || 'category'] || `Item ${index + 1}`,
          y: item[yAxisKey] || 0,
          label: item.label || item.name || item[config.xAxis || 'category']
        }
      })

      // Sort if needed
      if (config.groupBy) {
        processedData.sort((a, b) => b.y - a.y) // Sort by value descending
      }

      if (config.animate !== false) {
        let progress = 0
        const animate = () => {
          progress += 0.05
          if (progress <= 1) {
            drawChart(processedData, progress)
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
    } catch (error) {
      onError?.(error instanceof Error ? error.message : 'Unknown error')
      onLoadingChange?.(false)
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [data, config, drawChart, onError, onLoadingChange])

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
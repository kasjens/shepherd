'use client'

import React, { useEffect, useRef, useCallback } from 'react'
import { ChartConfig } from '../advanced-dashboard'

export interface AreaChartProps {
  data: any[]
  config: ChartConfig
  width: string | number
  height: string | number
  onError?: (error: string) => void
  onLoadingChange?: (isLoading: boolean) => void
}

export default function AreaChart({ data, config, width, height, onError, onLoadingChange }: AreaChartProps) {
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
    const margin = { top: 20, right: 40, bottom: 40, left: 60 }
    const chartWidth = rect.width - margin.left - margin.right
    const chartHeight = rect.height - margin.top - margin.bottom

    // Calculate scales
    const xValues = processedData.map(d => new Date(d.x).getTime())
    const yValues = processedData.flatMap(d => 
      Array.isArray(d.y) ? d.y : [d.y]
    )
    
    const xMin = Math.min(...xValues)
    const xMax = Math.max(...xValues)
    const yMin = Math.min(0, Math.min(...yValues) * 0.9)
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

    // Y-axis labels
    ctx.textAlign = 'right'
    for (let i = 0; i <= 5; i++) {
      const value = yMin + ((yMax - yMin) / 5) * (5 - i)
      const y = margin.top + (chartHeight / 5) * i
      ctx.fillText(value.toFixed(1), margin.left - 10, y + 4)
    }

    // X-axis labels
    ctx.textAlign = 'center'
    for (let i = 0; i <= 5; i++) {
      const timestamp = xMin + ((xMax - xMin) / 5) * i
      const x = xScale(timestamp)
      const date = new Date(timestamp)
      ctx.fillText(
        date.toLocaleDateString(),
        x,
        margin.top + chartHeight + 20
      )
    }

    // Colors
    const colors = config.colors || ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6']

    // Handle multiple series
    const series = config.yAxis && Array.isArray(config.yAxis) ? config.yAxis : [config.yAxis || 'value']
    
    // Draw areas (in reverse order so first series is on top)
    for (let seriesIndex = series.length - 1; seriesIndex >= 0; seriesIndex--) {
      const seriesKey = series[seriesIndex]
      const seriesData = processedData.map(d => ({
        x: new Date(d.x).getTime(),
        y: d[seriesKey] || 0
      }))

      if (seriesData.length === 0) continue

      // Limit data based on animation progress
      const visibleData = seriesData.slice(0, Math.floor(seriesData.length * animationProgress))
      if (visibleData.length === 0) continue

      const color = colors[seriesIndex % colors.length]
      
      // Create area path
      ctx.beginPath()
      
      // Start from bottom-left of first point
      const firstPoint = visibleData[0]
      ctx.moveTo(xScale(firstPoint.x), yScale(0))
      
      // Draw line to first point
      ctx.lineTo(xScale(firstPoint.x), yScale(firstPoint.y))
      
      // Draw curve through all points
      visibleData.forEach((point, index) => {
        if (index === 0) return
        
        const prevPoint = visibleData[index - 1]
        const x = xScale(point.x)
        const y = yScale(point.y)
        const prevX = xScale(prevPoint.x)
        const prevY = yScale(prevPoint.y)
        
        // Smooth curve using quadratic bezier
        const cpX = prevX + (x - prevX) * 0.5
        ctx.quadraticCurveTo(cpX, prevY, x, y)
      })
      
      // Close path to bottom
      const lastPoint = visibleData[visibleData.length - 1]
      ctx.lineTo(xScale(lastPoint.x), yScale(0))
      ctx.closePath()
      
      // Fill area with gradient
      const gradient = ctx.createLinearGradient(0, margin.top, 0, margin.top + chartHeight)
      gradient.addColorStop(0, color + '80') // 50% opacity at top
      gradient.addColorStop(1, color + '20') // 12% opacity at bottom
      
      ctx.fillStyle = gradient
      ctx.fill()
      
      // Draw stroke line
      ctx.beginPath()
      ctx.moveTo(xScale(firstPoint.x), yScale(firstPoint.y))
      
      visibleData.forEach((point, index) => {
        if (index === 0) return
        
        const prevPoint = visibleData[index - 1]
        const x = xScale(point.x)
        const y = yScale(point.y)
        const prevX = xScale(prevPoint.x)
        const prevY = yScale(prevPoint.y)
        
        const cpX = prevX + (x - prevX) * 0.5
        ctx.quadraticCurveTo(cpX, prevY, x, y)
      })
      
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.stroke()
      
      // Draw data points
      ctx.fillStyle = color
      visibleData.forEach(point => {
        const x = xScale(point.x)
        const y = yScale(point.y)
        
        ctx.beginPath()
        ctx.arc(x, y, 3, 0, Math.PI * 2)
        ctx.fill()
      })
    }

    // Legend
    if (config.showLegend !== false && series.length > 1) {
      const legendY = margin.top
      const legendItemWidth = 100

      series.forEach((seriesKey, index) => {
        const x = margin.left + chartWidth - (series.length - index) * legendItemWidth
        const color = colors[index % colors.length]
        
        // Legend color box
        ctx.fillStyle = color
        ctx.fillRect(x, legendY, 12, 12)
        
        // Legend text
        ctx.fillStyle = '#374151'
        ctx.font = '11px sans-serif'
        ctx.textAlign = 'left'
        ctx.fillText(seriesKey, x + 18, legendY + 9)
      })
    }

    // Interactive hover
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      const mouseX = e.clientX - rect.left
      const mouseY = e.clientY - rect.top

      if (mouseX >= margin.left && mouseX <= margin.left + chartWidth &&
          mouseY >= margin.top && mouseY <= margin.top + chartHeight) {
        
        // Find nearest x position
        const xValue = xMin + ((mouseX - margin.left) / chartWidth) * (xMax - xMin)
        let nearestPoint: any = null
        let minDistance = Infinity

        processedData.forEach(point => {
          const distance = Math.abs(new Date(point.x).getTime() - xValue)
          if (distance < minDistance) {
            minDistance = distance
            nearestPoint = point
          }
        })

        if (nearestPoint) {
          const values = series.map(key => `${key}: ${nearestPoint[key] || 0}`).join(', ')
          canvas.title = `${new Date(nearestPoint.x).toLocaleDateString()} - ${values}`
          canvas.style.cursor = 'pointer'
        } else {
          canvas.title = ''
          canvas.style.cursor = 'default'
        }
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
      const processedData = data.map(item => {
        const result: any = {
          x: item[config.xAxis || 'timestamp'] || item.date
        }
        
        // Handle multiple y-axis values
        if (config.yAxis && Array.isArray(config.yAxis)) {
          config.yAxis.forEach(key => {
            result[key] = parseFloat(item[key]) || 0
          })
        } else {
          result[config.yAxis || 'value'] = parseFloat(item[config.yAxis || 'value']) || 0
        }
        
        return result
      })

      // Sort by x-axis
      processedData.sort((a, b) => new Date(a.x).getTime() - new Date(b.x).getTime())

      if (config.animate !== false) {
        let progress = 0
        const animate = () => {
          progress += 0.03
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
'use client'

import React, { useEffect, useRef, useCallback } from 'react'
import { ChartConfig } from '../advanced-dashboard'

export interface HeatmapProps {
  data: any[]
  config: ChartConfig
  width: string | number
  height: string | number
  onError?: (error: string) => void
  onLoadingChange?: (isLoading: boolean) => void
}

export default function Heatmap({ data, config, width, height, onError, onLoadingChange }: HeatmapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

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
      ctx.fillStyle = '#9CA3AF'
      ctx.font = '14px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('No data available', rect.width / 2, rect.height / 2)
      return
    }

    // Get unique x and y values
    const xValues = [...new Set(processedData.map(d => d.x))].sort()
    const yValues = [...new Set(processedData.map(d => d.y))].sort()

    if (xValues.length === 0 || yValues.length === 0) return

    // Chart margins
    const margin = { top: 40, right: 100, bottom: 60, left: 80 }
    const chartWidth = rect.width - margin.left - margin.right
    const chartHeight = rect.height - margin.top - margin.bottom

    const cellWidth = chartWidth / xValues.length
    const cellHeight = chartHeight / yValues.length

    // Calculate value range for color scaling
    const values = processedData.map(d => d.value)
    const minValue = Math.min(...values)
    const maxValue = Math.max(...values)
    const valueRange = maxValue - minValue

    // Color scale function
    const getColor = (value: number) => {
      if (valueRange === 0) return 'rgb(200, 200, 200)'
      
      const intensity = (value - minValue) / valueRange
      const colors = config.colors || ['#3B82F6', '#EF4444'] // Blue to Red
      
      if (colors.length === 2) {
        // Interpolate between two colors
        const r = Math.round(parseInt(colors[0].slice(1, 3), 16) * (1 - intensity) + parseInt(colors[1].slice(1, 3), 16) * intensity)
        const g = Math.round(parseInt(colors[0].slice(3, 5), 16) * (1 - intensity) + parseInt(colors[1].slice(3, 5), 16) * intensity)
        const b = Math.round(parseInt(colors[0].slice(5, 7), 16) * (1 - intensity) + parseInt(colors[1].slice(5, 7), 16) * intensity)
        return `rgb(${r}, ${g}, ${b})`
      }
      
      // Default intensity-based coloring
      return `rgba(59, 130, 246, ${intensity * 0.8 + 0.2})`
    }

    // Draw cells
    processedData.forEach(point => {
      const xIndex = xValues.indexOf(point.x)
      const yIndex = yValues.indexOf(point.y)
      
      const x = margin.left + xIndex * cellWidth
      const y = margin.top + yIndex * cellHeight
      
      ctx.fillStyle = getColor(point.value)
      ctx.fillRect(x, y, cellWidth, cellHeight)
      
      // Cell border
      ctx.strokeStyle = '#FFFFFF'
      ctx.lineWidth = 1
      ctx.strokeRect(x, y, cellWidth, cellHeight)
      
      // Value text (if cell is large enough)
      if (cellWidth > 40 && cellHeight > 20) {
        const textColor = point.value > (minValue + valueRange * 0.5) ? '#FFFFFF' : '#000000'
        ctx.fillStyle = textColor
        ctx.font = '11px sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(
          point.value.toFixed(1),
          x + cellWidth / 2,
          y + cellHeight / 2
        )
      }
    })

    // Draw axes labels
    ctx.fillStyle = '#374151'
    ctx.font = '12px sans-serif'
    
    // X-axis labels
    ctx.textAlign = 'center'
    xValues.forEach((value, index) => {
      const x = margin.left + index * cellWidth + cellWidth / 2
      const y = margin.top + chartHeight + 20
      ctx.fillText(value.toString(), x, y)
    })
    
    // Y-axis labels
    ctx.textAlign = 'right'
    ctx.textBaseline = 'middle'
    yValues.forEach((value, index) => {
      const x = margin.left - 10
      const y = margin.top + index * cellHeight + cellHeight / 2
      ctx.fillText(value.toString(), x, y)
    })

    // Draw color scale legend
    const legendWidth = 20
    const legendHeight = chartHeight
    const legendX = rect.width - margin.right + 20
    const legendY = margin.top

    // Draw legend gradient
    for (let i = 0; i < legendHeight; i++) {
      const value = maxValue - (i / legendHeight) * valueRange
      ctx.fillStyle = getColor(value)
      ctx.fillRect(legendX, legendY + i, legendWidth, 1)
    }

    // Legend border
    ctx.strokeStyle = '#374151'
    ctx.strokeRect(legendX, legendY, legendWidth, legendHeight)

    // Legend labels
    ctx.fillStyle = '#374151'
    ctx.font = '11px sans-serif'
    ctx.textAlign = 'left'
    
    ctx.fillText(maxValue.toFixed(1), legendX + legendWidth + 5, legendY + 5)
    ctx.fillText(minValue.toFixed(1), legendX + legendWidth + 5, legendY + legendHeight - 5)

    // Interactive hover
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      const mouseX = e.clientX - rect.left
      const mouseY = e.clientY - rect.top

      if (mouseX >= margin.left && mouseX <= margin.left + chartWidth &&
          mouseY >= margin.top && mouseY <= margin.top + chartHeight) {
        
        const xIndex = Math.floor((mouseX - margin.left) / cellWidth)
        const yIndex = Math.floor((mouseY - margin.top) / cellHeight)
        
        if (xIndex >= 0 && xIndex < xValues.length && yIndex >= 0 && yIndex < yValues.length) {
          const xValue = xValues[xIndex]
          const yValue = yValues[yIndex]
          const point = processedData.find(p => p.x === xValue && p.y === yValue)
          
          if (point) {
            canvas.title = `${xValue}, ${yValue}: ${point.value}`
            canvas.style.cursor = 'pointer'
          } else {
            canvas.title = `${xValue}, ${yValue}: No data`
            canvas.style.cursor = 'default'
          }
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
      // Process data for heatmap
      const processedData = data.map((item: any) => {
        const yAxisKey = Array.isArray(config.yAxis) ? config.yAxis[0] : config.yAxis || 'y'
        return {
          x: item[config.xAxis || 'x'] || item.category,
          y: item[yAxisKey] || item.series,
          value: parseFloat(item.value) || 0
        }
      }).filter(item => item.x != null && item.y != null)

      drawChart(processedData)
      onLoadingChange?.(false)
    } catch (error) {
      onError?.(error instanceof Error ? error.message : 'Unknown error')
      onLoadingChange?.(false)
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
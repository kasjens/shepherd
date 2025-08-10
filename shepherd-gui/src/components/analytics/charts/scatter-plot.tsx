'use client'

import React from 'react'
import { ChartConfig } from '../advanced-dashboard'

export interface ScatterPlotProps {
  data: any[]
  config: ChartConfig
  width: string | number
  height: string | number
  onError?: (error: string) => void
  onLoadingChange?: (isLoading: boolean) => void
}

const ScatterPlot: React.FC<ScatterPlotProps> = ({ data, config, width, height, onError, onLoadingChange }) => {
  return (
    <div className="w-full h-full relative">
      <canvas
        className="w-full h-full"
        style={{ width, height }}
      />
    </div>
  )
}

export default ScatterPlot
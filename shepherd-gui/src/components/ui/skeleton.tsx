/**
 * Loading Skeleton Components
 * Phase 7: Performance Optimization & Polish
 */

import React from 'react'
import { cn } from '@/lib/utils'

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string
  animate?: boolean
}

/**
 * Base skeleton component
 */
export function Skeleton({ className, animate = true, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        'bg-gray-200 dark:bg-gray-800 rounded-md',
        animate && 'animate-pulse',
        className
      )}
      {...props}
    />
  )
}

/**
 * Message skeleton for conversation area
 */
export function MessageSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('flex gap-3 p-4', className)}>
      <Skeleton className="w-8 h-8 rounded-full flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    </div>
  )
}

/**
 * Widget skeleton for analytics dashboard
 */
export function WidgetSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('p-4 border border-gray-200 dark:border-gray-700 rounded-lg', className)}>
      <div className="flex items-center justify-between mb-4">
        <Skeleton className="h-5 w-1/3" />
        <Skeleton className="h-4 w-4 rounded" />
      </div>
      <div className="space-y-3">
        <Skeleton className="h-32 w-full" />
        <div className="flex justify-between">
          <Skeleton className="h-4 w-1/4" />
          <Skeleton className="h-4 w-1/4" />
        </div>
      </div>
    </div>
  )
}

/**
 * Chart skeleton
 */
export function ChartSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('w-full h-full flex items-end gap-1 p-4', className)}>
      {Array.from({ length: 12 }, (_, i) => (
        <Skeleton
          key={i}
          className="flex-1"
          style={{ height: `${Math.random() * 80 + 20}%` }}
        />
      ))}
    </div>
  )
}

/**
 * Agent card skeleton for sidebar
 */
export function AgentCardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('p-3 border border-gray-200 dark:border-gray-700 rounded-lg', className)}>
      <div className="flex items-center gap-3">
        <Skeleton className="w-10 h-10 rounded-full" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-2/3" />
          <Skeleton className="h-3 w-1/2" />
        </div>
        <Skeleton className="w-4 h-4 rounded" />
      </div>
    </div>
  )
}

/**
 * Table skeleton
 */
export function TableSkeleton({ 
  rows = 5, 
  columns = 4, 
  className 
}: { 
  rows?: number
  columns?: number
  className?: string 
}) {
  return (
    <div className={cn('w-full', className)}>
      {/* Header */}
      <div className="flex gap-4 p-4 border-b border-gray-200 dark:border-gray-700">
        {Array.from({ length: columns }, (_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }, (_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4 p-4 border-b border-gray-100 dark:border-gray-800">
          {Array.from({ length: columns }, (_, colIndex) => (
            <Skeleton key={colIndex} className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  )
}

/**
 * List skeleton
 */
export function ListSkeleton({ 
  items = 5, 
  className 
}: { 
  items?: number
  className?: string 
}) {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: items }, (_, i) => (
        <div key={i} className="flex items-center gap-3">
          <Skeleton className="w-6 h-6 rounded" />
          <Skeleton className="h-4 flex-1" />
          <Skeleton className="h-4 w-16" />
        </div>
      ))}
    </div>
  )
}

/**
 * Card skeleton
 */
export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('p-6 border border-gray-200 dark:border-gray-700 rounded-lg', className)}>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-6 w-1/3" />
          <Skeleton className="h-5 w-5 rounded" />
        </div>
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-2/3" />
        <div className="flex gap-2 pt-2">
          <Skeleton className="h-8 w-20 rounded" />
          <Skeleton className="h-8 w-16 rounded" />
        </div>
      </div>
    </div>
  )
}

/**
 * Dashboard skeleton - full page loading state
 */
export function DashboardSkeleton() {
  return (
    <div className="flex h-screen">
      {/* Sidebar skeleton */}
      <div className="w-80 border-r border-gray-200 dark:border-gray-700 p-4 space-y-4">
        <Skeleton className="h-8 w-3/4" />
        <div className="space-y-3">
          {Array.from({ length: 4 }, (_, i) => (
            <AgentCardSkeleton key={i} />
          ))}
        </div>
        <div className="pt-4 space-y-2">
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-6 w-2/3" />
        </div>
      </div>
      
      {/* Main content skeleton */}
      <div className="flex-1 p-6">
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <Skeleton className="h-8 w-1/4" />
            <div className="flex gap-2">
              <Skeleton className="h-8 w-20" />
              <Skeleton className="h-8 w-16" />
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }, (_, i) => (
              <WidgetSkeleton key={i} />
            ))}
          </div>
          
          <div className="space-y-4">
            {Array.from({ length: 3 }, (_, i) => (
              <MessageSkeleton key={i} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Progressive loading skeleton that adapts to content
 */
export function ProgressiveSkeleton({ 
  isLoading,
  children,
  fallback
}: {
  isLoading: boolean
  children: React.ReactNode
  fallback?: React.ReactNode
}) {
  if (isLoading) {
    return <>{fallback || <Skeleton className="h-20 w-full" />}</>
  }
  
  return <>{children}</>
}
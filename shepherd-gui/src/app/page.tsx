'use client'

import { useState, useRef, useCallback } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { ConversationArea } from '@/components/layout/conversation-area'

export default function Home() {
  const [sidebarWidth, setSidebarWidth] = useState(280) // Default 280px
  const [isCollapsed, setIsCollapsed] = useState(false)
  
  const isResizing = useRef(false)

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    isResizing.current = true
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }, [])

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isResizing.current) {
      const newWidth = Math.max(200, Math.min(600, e.clientX))
      setSidebarWidth(newWidth)
    }
  }, [])

  const handleMouseUp = useCallback(() => {
    isResizing.current = false
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }, [handleMouseMove])

  return (
    <div className="h-screen w-screen flex overflow-hidden fixed inset-0" style={{ backgroundColor: 'var(--background)', color: 'var(--foreground)' }}>
      <Sidebar 
        width={isCollapsed ? 48 : sidebarWidth}
        isCollapsed={isCollapsed}
        onCollapsedChange={setIsCollapsed}
      />
      
      {/* Resize handle */}
      {!isCollapsed && (
        <div
          className="w-1 bg-transparent hover:bg-border-gray cursor-col-resize flex-shrink-0 transition-colors"
          onMouseDown={handleMouseDown}
        />
      )}
      
      <ConversationArea className="flex-1 min-w-0" />
    </div>
  )
}
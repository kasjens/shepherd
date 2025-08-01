'use client'

import { useState, useRef, useCallback } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { ConversationArea } from '@/components/layout/conversation-area'
import { ArtifactsPanel } from '@/components/layout/artifacts-panel'

export default function Home() {
  const [leftWidth, setLeftWidth] = useState(320) // 80 * 4 = 320px (w-80)
  const [rightWidth, setRightWidth] = useState(384) // 96 * 4 = 384px (w-96)
  const [isLeftCollapsed, setIsLeftCollapsed] = useState(false)
  const [isRightCollapsed, setIsRightCollapsed] = useState(true)
  
  const isResizingLeft = useRef(false)
  const isResizingRight = useRef(false)

  const handleMouseDown = useCallback((side: 'left' | 'right') => (e: React.MouseEvent) => {
    e.preventDefault()
    if (side === 'left') {
      isResizingLeft.current = true
    } else {
      isResizingRight.current = true
    }
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }, [])

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isResizingLeft.current) {
      const newWidth = Math.max(200, Math.min(600, e.clientX))
      setLeftWidth(newWidth)
    } else if (isResizingRight.current) {
      const newWidth = Math.max(250, Math.min(700, window.innerWidth - e.clientX))
      setRightWidth(newWidth)
    }
  }, [])

  const handleMouseUp = useCallback(() => {
    isResizingLeft.current = false
    isResizingRight.current = false
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }, [handleMouseMove])

  const leftPanelWidth = isLeftCollapsed ? 48 : leftWidth
  const rightPanelWidth = isRightCollapsed ? 48 : rightWidth

  return (
    <div className="h-screen w-screen flex overflow-hidden fixed inset-0" style={{ backgroundColor: 'var(--background)', color: 'var(--foreground)' }}>
      <Sidebar 
        width={leftPanelWidth}
        isCollapsed={isLeftCollapsed}
        onCollapsedChange={setIsLeftCollapsed}
      />
      
      {/* Left resize handle */}
      {!isLeftCollapsed && (
        <div
          className="w-1 bg-transparent hover:bg-border-gray cursor-col-resize flex-shrink-0 transition-colors"
          onMouseDown={handleMouseDown('left')}
        />
      )}
      
      <ConversationArea className="flex-1 min-w-0" />
      
      {/* Right resize handle */}
      {!isRightCollapsed && (
        <div
          className="w-1 bg-transparent hover:bg-border-gray cursor-col-resize flex-shrink-0 transition-colors"
          onMouseDown={handleMouseDown('right')}
        />
      )}
      
      <ArtifactsPanel 
        width={rightPanelWidth}
        isCollapsed={isRightCollapsed}
        onCollapsedChange={setIsRightCollapsed}
      />
    </div>
  )
}
'use client'

import { Sidebar } from '@/components/layout/sidebar'
import { ConversationArea } from '@/components/layout/conversation-area'
import { ArtifactsPanel } from '@/components/layout/artifacts-panel'

export default function Home() {
  return (
    <div className="app-layout">
      <Sidebar />
      <ConversationArea />
      <ArtifactsPanel />
    </div>
  )
}
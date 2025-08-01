import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface ProjectStore {
  projectFolder: string | null
  setProjectFolder: (folder: string) => void
  clearProjectFolder: () => void
}

export const useProjectStore = create<ProjectStore>()(
  persist(
    (set) => ({
      projectFolder: null,
      
      setProjectFolder: (folder: string) => {
        set({ projectFolder: folder })
      },
      
      clearProjectFolder: () => {
        set({ projectFolder: null })
      },
    }),
    {
      name: 'shepherd-project-folder',
      storage: createJSONStorage(() => localStorage),
    }
  )
)
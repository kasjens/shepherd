/**
 * Test for ProjectFolderSelector component
 */

import { render, screen, fireEvent } from '../../../setup'

// Mock functions
const mockSetProjectFolder = jest.fn()
const mockClearProjectFolder = jest.fn()
let mockProjectFolder: string | null = null

// Mock the project store
jest.mock('@/stores/project-store', () => ({
  useProjectStore: () => ({
    projectFolder: mockProjectFolder,
    setProjectFolder: mockSetProjectFolder,
    clearProjectFolder: mockClearProjectFolder,
  }),
}))

// Mock Tauri
jest.mock('@/lib/tauri', () => ({
  isTauri: jest.fn(() => false),
}))

// Mock the Tauri API module
jest.mock('@tauri-apps/api/dialog', () => ({
  open: jest.fn(),
}), { virtual: true })

// Import after mocks
import { ProjectFolderSelector } from '@/components/features/settings/project-folder-selector'

describe('ProjectFolderSelector', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockProjectFolder = null // Reset to no folder selected
  })

  test('renders without project folder', () => {
    render(<ProjectFolderSelector />)
    
    expect(screen.getByText('📁 PROJECT FOLDER')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /set project folder/i })).toBeInTheDocument()
  })

  test('button is clickable when no folder selected', () => {
    render(<ProjectFolderSelector />)
    
    const button = screen.getByRole('button', { name: /set project folder/i })
    expect(button).not.toBeDisabled()
    fireEvent.click(button)
    // Button click doesn't throw error
  })
})

describe('ProjectFolderSelector with folder', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockProjectFolder = '/home/user/my-project' // Set to folder selected
  })

  test('renders with selected project folder', () => {
    render(<ProjectFolderSelector />)
    
    expect(screen.getByText('📁 PROJECT FOLDER')).toBeInTheDocument()
    expect(screen.getByText('.../user/my-project')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /change folder/i })).toBeInTheDocument()
  })

  test('displays full path in title attribute', () => {
    render(<ProjectFolderSelector />)
    
    const folderDisplay = screen.getByTitle('/home/user/my-project')
    expect(folderDisplay).toBeInTheDocument()
  })

  test('clear button works', () => {
    render(<ProjectFolderSelector />)
    
    const clearButton = screen.getByRole('button', { name: /clear project folder/i })
    fireEvent.click(clearButton)
    
    expect(mockClearProjectFolder).toHaveBeenCalledTimes(1)
  })
})
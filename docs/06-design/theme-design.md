# Shepherd Theme Design Document
*Based on the Shepherd Logo Visual Language*

## Overview
This document defines the visual design system for the Shepherd application, drawing inspiration from the logo's modern, developer-centric aesthetic that combines technical precision with guidance symbolism.

## Core Design Philosophy

### Terminal-Inspired Minimalism
- **Clean, flat design** with no unnecessary shadows or gradients
- **High contrast** for optimal readability and technical clarity
- **Geometric precision** reflecting developer tools and command-line interfaces
- **Purposeful whitespace** to reduce cognitive load

### Guidance & Leadership Symbolism
- **Subtle directional cues** that guide user workflow
- **Hierarchical information architecture** that shepherds users through complex tasks
- **Progressive disclosure** revealing complexity only when needed

## Color Palette

### Primary Colors
```
Terminal Black:     #1a1d21  (Main backgrounds, headers)
Command Gray:       #2c3136  (Secondary backgrounds, panels)
Border Gray:        #495057  (Borders, dividers, subtle elements)
Prompt White:       #f8f9fa  (Primary text, icons)
Muted Gray:         #adb5bd  (Secondary text, metadata)
```

### Accent Colors
```
Shepherd Blue:      #0969da  (Primary actions, links, active states)
Success Green:      #2da44e  (Success states, completed tasks)
Warning Amber:      #fb8500  (Warnings, important notifications)
Error Red:          #cf222e  (Errors, destructive actions)
```

### Theme Variations

#### Light Theme - "Terminal Day"
- **Background**: Clean white (#ffffff) with subtle gray panels
- **Text**: Dark charcoal (#212529) for maximum readability
- **Accents**: Maintains terminal-inspired blue with softer contrast
- **Metaphor**: A bright, clean terminal session

#### Dark Theme - "Terminal Night"
- **Background**: Deep terminal black (#1a1d21)
- **Text**: Soft terminal white (#f8f9fa)
- **Accents**: Brighter blues and greens for visibility
- **Metaphor**: Classic dark terminal environment

#### Blue Theme - "Guided Mode"
- **Background**: Soft blue-gray (#f0f7ff)
- **Text**: Deep blue (#0a3069) for authority
- **Accents**: Warmer blues emphasizing guidance
- **Metaphor**: Professional guidance interface

## Typography

### Font Hierarchy
```
Primary: SF Pro / Segoe UI / -apple-system, sans-serif
Code: SF Mono / Consolas / Monaco, monospace
```

### Scale
- **Logo/Brand**: 18px, 600 weight
- **Section Headers**: 16px, 600 weight, uppercase tracking
- **Body Text**: 14px, 400 weight
- **Metadata**: 12px, 400 weight
- **Code/Terminal**: 13px, 400 weight, monospace

## Layout Principles

### Terminal-Inspired Grid
- **Command Line Structure**: Input at bottom, output scrolling above
- **Left-to-Right Flow**: Mimicking terminal prompt → command → output
- **Consistent Margins**: 16px base unit for spacing
- **Panel Separation**: Clear visual boundaries like terminal windows

### Responsive Breakpoints
- **Sidebar**: 280px default, 200-500px resizable range
- **Main Content**: Flexible with 800px optimal reading width  
- **Artifacts Panel**: 350px default, 250-600px resizable range

## Component Design

### Navigation (Sidebar)
```
Visual Style: Terminal directory tree
- Clean lines with prompt-style indicators (›)
- Hover states with subtle background change
- Active states with accent color left border
- Section headers in muted caps
```

### Conversation Area
```
Visual Style: Terminal session log
- Messages flow top-to-bottom like command history
- User messages: Right-aligned with light background
- AI responses: Left-aligned with system-style formatting
- Timestamps in muted terminal green
```

### Input Area
```
Visual Style: Command prompt
- Clean input field with subtle border
- Send button styled like terminal execute
- Multi-line support with proper text wrapping
- Placeholder text in muted terminal style
```

### Artifacts Panel
```
Visual Style: File browser/editor
- Clean file-like structure
- Code syntax highlighting
- Action buttons as terminal commands
- Tabbed interface for multiple artifacts
```

## Interactive Elements

### Buttons
```
Primary Actions:
- Background: Shepherd Blue (#0969da)
- Text: White
- Hover: Darker blue (#0860ca)
- Style: 6px border radius, clean sans-serif

Secondary Actions:
- Background: Transparent
- Border: 1px solid border-gray
- Text: Primary text color
- Hover: Subtle background tint

Terminal-Style Actions:
- Monospace font
- Bracketed format: [copy] [save] [run]
- Minimal styling, high functionality
```

### Form Controls
```
Input Fields:
- Border: 1px solid border-gray
- Focus: Accent color border
- Background: Panel background
- Padding: 8px 12px

Dropdowns/Selects:
- Terminal-style chevrons (›)
- Clean option lists
- Keyboard navigation support
```

### Status Indicators
```
Connection Status:
- ● Online (green dot)
- ● Connecting (amber dot)
- ● Offline (red dot)

Progress States:
- Terminal-style progress bars
- Percentage indicators
- Step-by-step process flows
```

## Animation & Transitions

### Micro-Interactions
```
Timing: Fast and purposeful (200-300ms)
Easing: Ease-out for natural feel
Effects:
- Button hover: Subtle color shift
- Panel resize: Smooth width transition
- Loading states: Terminal-style dots (...)
- Success feedback: Brief green flash
```

### Loading States
```
Terminal Command Style:
- "Processing..." with animated dots
- Cursor blink animation
- Progressive text reveal for responses
```

## Accessibility

### Contrast Requirements
- **WCAG AA**: Minimum 4.5:1 for normal text
- **WCAG AAA**: Target 7:1 for enhanced readability
- **High Contrast Mode**: Support for system settings

### Keyboard Navigation
- **Tab Order**: Logical flow through interface
- **Focus Indicators**: Clear accent-colored outlines
- **Shortcuts**: Terminal-inspired key combinations
- **Screen Reader**: Proper ARIA labels and descriptions

## Implementation Guidelines

### CSS Variables Structure
```css
:root {
  /* Core Colors */
  --terminal-black: #1a1d21;
  --command-gray: #2c3136;
  --border-gray: #495057;
  --prompt-white: #f8f9fa;
  --muted-gray: #adb5bd;
  
  /* Accent Colors */
  --shepherd-blue: #0969da;
  --success-green: #2da44e;
  --warning-amber: #fb8500;
  --error-red: #cf222e;
  
  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  
  /* Typography */
  --font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'SF Mono', Monaco, 'Cascadia Code', monospace;
}
```

### Theme Switching
- **localStorage Persistence**: Remember user preference
- **System Preference Detection**: Respect OS dark/light mode
- **Smooth Transitions**: CSS transitions for theme changes
- **Component Consistency**: All elements update simultaneously

## Brand Integration

### Logo Usage
- **Sidebar Header**: 24px logo with "Shepherd" text
- **Loading States**: Animated logo for brand reinforcement
- **Empty States**: Subtle logo watermark
- **Favicon**: Simplified square version

### Voice & Tone in UI
- **Confident**: Clear, authoritative language
- **Helpful**: Guiding without being condescending  
- **Technical**: Precise terminology for developer audience
- **Friendly**: Approachable despite technical nature

## Quality Assurance

### Browser Support
- **Modern Browsers**: Chrome 90+, Firefox 90+, Safari 14+, Edge 90+
- **Performance**: 60fps animations, smooth scrolling
- **Responsive**: Mobile-friendly responsive design

### Testing Checklist
- [ ] Color contrast meets WCAG AA standards
- [ ] All interactive elements have focus states
- [ ] Theme switching works across all components  
- [ ] Resize functionality maintains visual hierarchy
- [ ] Loading states provide clear feedback
- [ ] Error messages are helpful and actionable

---

*This design system creates a cohesive, professional interface that reflects the Shepherd logo's balance of technical precision and guiding symbolism, ensuring users feel both empowered and supported in their workflow orchestration tasks.*
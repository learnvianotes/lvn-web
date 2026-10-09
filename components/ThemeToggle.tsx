'use client'

import { Moon, Sun } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/state/theme'

export function ThemeToggle({ labels }: { labels: { toLight: string; toDark: string } }) {
  const { theme, setTheme } = useTheme()
  // The theme is only known in the browser; render a stable icon until hydrated.
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])
  const dark = mounted && theme === 'dark'
  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={dark ? labels.toLight : labels.toDark}
      onClick={() => setTheme(dark ? 'light' : 'dark')}
    >
      {dark ? <Sun className="size-[18px]" aria-hidden /> : <Moon className="size-[18px]" aria-hidden />}
    </Button>
  )
}

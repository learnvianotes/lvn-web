/* ============================================================
   TopicDetailPage — Interactive Topic & Problem Workspace
   Loads the specific module or topic with multi-language code tabs,
   intuition, algorithms, and Firestore progress sync.
   ============================================================ */

import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Maximize2,
  Minimize2,
  ExternalLink,
  RotateCcw,
  BookOpen,
} from 'lucide-react'
import { getSubjectById, getSubjectContentUrl } from '@/data/subjects'
import { getSubjectIcon } from '@/data/subjectIcons'
import { NotFound } from '@/components/feedback/NotFound'
import { useTheme } from '@/hooks/useTheme'
import { ThemeToggle } from '@/features/theme/ThemeToggle'
import { saveContinueLearning, saveSubjectProgress } from '@/lib/firestoreService'

function formatSlug(slug: string): string {
  return slug
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

export function TopicDetailPage() {
  const { subjectId, topicId } = useParams<{
    subjectId: string
    topicId: string
  }>()
  const navigate = useNavigate()
  const { theme } = useTheme()
  const iframeRef = useRef<HTMLIFrameElement>(null)

  const [isLoading, setIsLoading] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [iframeKey, setIframeKey] = useState(0)

  const subject = subjectId ? getSubjectById(subjectId) : undefined
  const topicLabel = topicId ? formatSlug(topicId) : ''
  const contentUrl = subject && topicId ? getSubjectContentUrl(subject.id, topicId) : ''
  const IconComponent = subject ? getSubjectIcon(subject.id) : BookOpen

  // Sync topic visit to Firestore
  useEffect(() => {
    if (subject && topicId) {
      const continueData = {
        subjectId: subject.id,
        subjectTitle: subject.title.toUpperCase(),
        topicTitle: topicLabel,
        path: `/subjects/${subject.id}/topics/${topicId}`,
        color: '#38bdf8',
      }

      try {
        localStorage.setItem('cnote_last_visited', JSON.stringify(continueData))
      } catch {}

      saveContinueLearning(continueData).catch(() => {})
      saveSubjectProgress(subject.id, {
        lastTopicId: topicId,
        lastTopicTitle: topicLabel,
      }).catch(() => {})
    }
  }, [subject, topicId, topicLabel])

  // Sync theme to iframe
  const syncThemeToIframe = useCallback(() => {
    try {
      const iframeDoc = iframeRef.current?.contentDocument
      const iframeWin = iframeRef.current?.contentWindow as any
      if (iframeDoc) {
        iframeDoc.documentElement.setAttribute('data-theme', theme)
        try {
          iframeWin?.localStorage?.setItem('cnote_theme', theme)
          iframeWin?.localStorage?.setItem('cnote:theme', theme)
        } catch {}
        if (typeof iframeWin?.updateThemeIcon === 'function') {
          iframeWin.updateThemeIcon(theme)
        }
      }
    } catch {}
  }, [theme])

  useEffect(() => {
    syncThemeToIframe()
  }, [theme, syncThemeToIframe])

  // Inject embedded styling into the iframe to remove duplicate topbars and fix sidebar
  const injectEmbeddedStyles = (doc: Document) => {
    try {
      doc.documentElement.setAttribute('data-embedded', 'true')
      doc.body?.classList.add('is-embedded')

      let style = doc.getElementById('cnote-embedded-style') as HTMLStyleElement | null
      if (!style) {
        style = doc.createElement('style')
        style.id = 'cnote-embedded-style'
        doc.head?.appendChild(style)
      }
      style.textContent = `
        .topbar, .sub-topbar, #subTopbar, .mobile-nav {
          display: none !important;
        }
        .layout {
          padding-top: 0 !important;
          margin-top: 0 !important;
          min-height: 100vh !important;
        }
        html[data-embedded="true"] .sidebar,
        html[data-embedded="true"] aside.sidebar,
        html[data-embedded="true"] #sidebar,
        body.is-embedded .sidebar,
        body.is-embedded aside.sidebar,
        body.is-embedded #sidebar,
        :root[data-embedded="true"] #sidebar,
        .sidebar,
        #sidebar,
        aside.sidebar,
        aside#sidebar,
        div#sidebar {
          top: 0 !important;
          margin-top: 0 !important;
          padding-top: 0 !important;
          height: 100vh !important;
          height: 100dvh !important;
          bottom: 0 !important;
          width: 280px !important;
          max-width: 280px !important;
        }
        .sidebar-header {
          display: flex !important;
          padding-top: 14px !important;
        }
        .main-content {
          margin-left: 280px !important;
          width: calc(100% - 280px) !important;
          padding-top: 24px !important;
          padding-bottom: 80px !important;
        }
      `
    } catch {}
  }

  // Handle iframe load event
  const handleIframeLoad = () => {
    setIsLoading(false)
    syncThemeToIframe()

    try {
      const iframeDoc = iframeRef.current?.contentDocument
      const iframeWin = iframeRef.current?.contentWindow
      if (iframeDoc && iframeWin) {
        injectEmbeddedStyles(iframeDoc)

        const backLinks = iframeDoc.querySelectorAll<HTMLAnchorElement>(
          'a[href="/subjects"], a[href="../../index.html"]'
        )
        backLinks.forEach((link) => {
          link.addEventListener('click', (e) => {
            e.preventDefault()
            navigate('/subjects')
          })
        })
      }
    } catch {}
  }

  // Reload iframe
  const handleRefresh = () => {
    setIsLoading(true)
    setIframeKey((prev) => prev + 1)
  }

  // Escape key to exit fullscreen
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isFullscreen])

  if (!subject || !topicId) {
    return (
      <div style={{ padding: '40px 20px', maxWidth: '800px', margin: '0 auto' }}>
        <NotFound message="Topic not found." />
      </div>
    )
  }

  return (
    <div className={`learning-viewer ${isFullscreen ? 'learning-viewer--fullscreen' : ''}`}>
      {/* Top Toolbar */}
      <div className="learning-viewer__toolbar">
        <div className="learning-viewer__left">
          <Link
            to={`/subjects/${subject.id}`}
            className="learning-viewer__back-btn"
            aria-label={`Back to ${subject.title}`}
          >
            <ArrowLeft size={14} />
            <span>{subject.shortTitle || subject.title}</span>
          </Link>

          <div className="learning-viewer__title-group">
            <IconComponent size={18} style={{ color: 'var(--color-accent)', flexShrink: 0 }} />
            <span className="learning-viewer__title">{topicLabel}</span>
            <span className="learning-viewer__badge">Topic Module</span>
          </div>
        </div>

        <div className="learning-viewer__right">
          <button
            className="learning-viewer__btn"
            onClick={handleRefresh}
            title="Reload content"
            aria-label="Reload content"
          >
            <RotateCcw size={14} />
          </button>

          <a
            href={contentUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="learning-viewer__btn"
            title="Open in new window"
            aria-label="Open in new window"
          >
            <ExternalLink size={14} />
          </a>

          <button
            className="learning-viewer__btn"
            onClick={() => setIsFullscreen(!isFullscreen)}
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
            aria-label={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>

          <div style={{ marginLeft: '4px', display: 'flex', alignItems: 'center' }}>
            <ThemeToggle />
          </div>
        </div>
      </div>

      {/* Frame Container */}
      <div className="learning-viewer__frame-container">
        {isLoading && (
          <div className="learning-viewer__loading">
            <div className="learning-viewer__spinner" />
            <span>Loading {topicLabel}...</span>
          </div>
        )}

        {contentUrl ? (
          <iframe
            key={iframeKey}
            ref={iframeRef}
            src={contentUrl}
            title={`${subject.title} - ${topicLabel}`}
            className="learning-viewer__frame"
            onLoad={handleIframeLoad}
          />
        ) : (
          <div style={{ padding: '40px', textAlign: 'center' }}>
            <p>No interactive content available for this topic.</p>
          </div>
        )}
      </div>
    </div>
  )
}

/* ============================================================
   SubjectDetailPage — Interactive Learning Workspace
   Loads the rich subject learning modules with full multi-language
   code, solution breakdowns, search, and Firestore progress sync.
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
import { saveContinueLearning, saveSubjectProgress, saveQuestionProgress, getAllQuestionsProgress, batchSeedSheet150Problems } from '@/lib/firestoreService'
import { SHEET_150_CORE_PROBLEMS } from '@/data/sheet150Problems'

export function SubjectDetailPage() {
  const { subjectId } = useParams<{ subjectId: string }>()
  const navigate = useNavigate()
  const { theme } = useTheme()
  const iframeRef = useRef<HTMLIFrameElement>(null)

  const [isLoading, setIsLoading] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [iframeKey, setIframeKey] = useState(0)

  const subject = subjectId ? getSubjectById(subjectId) : undefined
  const contentUrl = subject ? getSubjectContentUrl(subject.id) : ''
  const IconComponent = subject ? getSubjectIcon(subject.id) : BookOpen

  // Sync initial subject visit to Firestore
  useEffect(() => {
    if (subject) {
      const topicTitle = subject.id === 'sheet-150'
        ? 'Sheet 150 Hub'
        : (subject.topicIds[0]
            ? subject.topicIds[0].split('-').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
            : (subject.shortTitle || subject.title))

      const continueData = {
        subjectId: subject.id,
        subjectTitle: subject.title.toUpperCase(),
        topicTitle,
        path: `/subjects/${subject.id}`,
        color: '#38bdf8',
      }

      try {
        localStorage.setItem('cnote_last_visited', JSON.stringify(continueData))
      } catch {}

      saveContinueLearning(continueData).catch(() => {})
      saveSubjectProgress(subject.id, {
        lastTopicId: subject.topicIds[0] || '',
        lastTopicTitle: topicTitle,
      }).catch(() => {})

      if (subject.id === 'sheet-150') {
        batchSeedSheet150Problems(SHEET_150_CORE_PROBLEMS).catch(() => {})
      }
    }
  }, [subject])

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
    } catch {
      // ignore cross-origin error if any
    }
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

  // Push Firestore progress back into iframe after it signals ready
  const pushProgressToIframe = useCallback(async () => {
    if (!subject || subject.id !== 'sheet-150') return
    try {
      const progress = await getAllQuestionsProgress('sheet-150')
      // Flatten to { questionId: status } map
      const progressMap: Record<string, string> = {}
      Object.values(progress).forEach((q) => {
        progressMap[q.questionId] = q.status
      })
      iframeRef.current?.contentWindow?.postMessage({
        type: 'CNOTE_INIT_DATA',
        progress: progressMap,
      }, '*')
    } catch {}
  }, [subject])

  // Handle iframe load event
  const handleIframeLoad = () => {
    setIsLoading(false)
    syncThemeToIframe()

    try {
      const iframeDoc = iframeRef.current?.contentDocument
      const iframeWin = iframeRef.current?.contentWindow
      if (iframeDoc && iframeWin) {
        injectEmbeddedStyles(iframeDoc)

        // Intercept home back buttons inside iframe to navigate via React router
        const backLinks = iframeDoc.querySelectorAll<HTMLAnchorElement>(
          'a[href="/subjects"], a[href="../../index.html"]'
        )
        backLinks.forEach((link) => {
          link.addEventListener('click', (e) => {
            e.preventDefault()
            navigate('/subjects')
          })
        })

        // Track page title inside iframe for Continue Learning
        const handleLocationChange = () => {
          try {
            injectEmbeddedStyles(iframeDoc)
            const pageTitle = iframeDoc.title || subject?.title || 'Subject Notes'
            const cleanTitle = pageTitle
              .replace(' — Sheet 150 | C-Note', '')
              .replace(' — Sheet 150', '')
              .replace(' — C-Note', '')
              .trim()

            if (subject && cleanTitle) {
              const continueData = {
                subjectId: subject.id,
                subjectTitle: subject.title.toUpperCase(),
                topicTitle: cleanTitle,
                path: `/subjects/${subject.id}`,
                color: '#38bdf8',
              }
              try {
                localStorage.setItem('cnote_last_visited', JSON.stringify(continueData))
              } catch {}
              saveContinueLearning(continueData).catch(() => {})
            }
          } catch {}
        }

        iframeWin.addEventListener('hashchange', handleLocationChange)
      }
    } catch {}

    // After iframe loads, push Firestore state in
    setTimeout(() => pushProgressToIframe(), 600)
  }

  // Listen for postMessages from the Sheet 150 iframe
  useEffect(() => {
    const handleMessage = async (event: MessageEvent) => {
      const data = event.data
      if (!data || typeof data !== 'object') return

      if (data.type === 'CNOTE_REQUEST_INITIAL_STATE') {
        // iframe is asking for initial state — push progress from Firestore
        await pushProgressToIframe()
      } else if (data.type === 'CNOTE_PROBLEM_STATUS_CHANGE') {
        const { questionId, status, subjectId: msgSubjectId, topicId, title, notes } = data
        if (!questionId || !msgSubjectId) return

        try {
          await saveQuestionProgress({
            questionId,
            subjectId: msgSubjectId,
            topicId: topicId || 'unknown',
            status: (status === 'solved' || status === 'revisit') ? status : 'unsolved',
            ...(notes !== undefined ? { notes: String(notes) } : {}),
          })

          // Sync Continue Learning with the specific problem
          if (title && subject) {
            const continueData = {
              subjectId: subject.id,
              subjectTitle: subject.title.toUpperCase(),
              topicTitle: String(title),
              path: `/subjects/${subject.id}`,
              color: '#38bdf8',
            }
            try {
              localStorage.setItem('cnote_last_visited', JSON.stringify(continueData))
            } catch {}
            saveContinueLearning(continueData).catch(() => {})
          }

          // Acknowledge sync back to iframe
          iframeRef.current?.contentWindow?.postMessage({
            type: 'CNOTE_SYNC_SUCCESS',
            questionId,
          }, '*')
        } catch (err) {
          console.warn('[C-Note] Failed to sync problem status to Firestore:', err)
        }
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [subject, pushProgressToIframe])

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

  if (!subject) {
    return (
      <div style={{ padding: '40px 20px', maxWidth: '800px', margin: '0 auto' }}>
        <NotFound message={`Subject "${subjectId}" was not found.`} />
      </div>
    )
  }

  return (
    <div className={`learning-viewer ${isFullscreen ? 'learning-viewer--fullscreen' : ''}`}>
      {/* Top Toolbar */}
      <div className="learning-viewer__toolbar">
        <div className="learning-viewer__left">
          <Link to="/subjects" className="learning-viewer__back-btn" aria-label="Back to Subjects Dashboard">
            <ArrowLeft size={14} />
            <span>Dashboard</span>
          </Link>

          <div className="learning-viewer__title-group">
            <IconComponent size={18} style={{ color: 'var(--color-accent)', flexShrink: 0 }} />
            <span className="learning-viewer__title">{subject.title}</span>
            {subject.id === 'sheet-150' ? (
              <span className="learning-viewer__badge">150 Problems</span>
            ) : (
              subject.displayTags && subject.displayTags[0] && (
                <span className="learning-viewer__badge">{subject.displayTags[0]}</span>
              )
            )}
          </div>
        </div>

        <div className="learning-viewer__right">
          {subject.id === 'sheet-150' && (
            <Link
              to="/sheet-150"
              className="learning-viewer__beta-badge"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                fontSize: '12px',
                fontWeight: 600,
                padding: '4px 10px',
                borderRadius: '9999px',
                border: '1px solid var(--color-accent-border)',
                background: 'var(--color-accent-subtle)',
                color: 'var(--color-accent)',
                textDecoration: 'none',
              }}
            >
              ✨ Open React Hub (Beta) →
            </Link>
          )}

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
            <span>Loading {subject.title}...</span>
          </div>
        )}

        {contentUrl ? (
          <iframe
            key={iframeKey}
            ref={iframeRef}
            src={contentUrl}
            title={subject.title}
            className="learning-viewer__frame"
            onLoad={handleIframeLoad}
          />
        ) : (
          <div style={{ padding: '40px', textAlign: 'center' }}>
            <p>No interactive content available for this subject.</p>
          </div>
        )}
      </div>
    </div>
  )
}

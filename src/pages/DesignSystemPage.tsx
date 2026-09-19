/* ============================================================
   DesignSystemPage — C-NOTE Design Lab
   Internal reference page showing all design tokens and
   UI primitives in both dark and light themes.
   Not user-facing. Route: /design-system
   ============================================================ */

import { useState } from 'react'
import { PageContainer } from '@/components/layout/PageContainer'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import {
  Button,
  IconButton,
  Input,
  Badge,
  Divider,
  Spinner,
  Skeleton,
  SkeletonText,
  EmptyState,
  Tooltip,
} from '@/components/ui'
import { ErrorState } from '@/components/feedback/ErrorState'
import { LoadingState } from '@/components/feedback/LoadingState'
import { NotFound } from '@/components/feedback/NotFound'
import { useTheme } from '@/hooks/useTheme'
import {
  Search,
  Star,
  Trash2,
  FlaskConical,
  Inbox,
  BookOpen,
  AlertTriangle,
  Info,
  CheckCircle,
  Sun,
  Moon,
  Code2,
} from 'lucide-react'

/* ── Section wrapper ──────────────────────────────────────── */
function Section({
  id,
  title,
  children,
}: {
  id: string
  title: string
  children: React.ReactNode
}) {
  return (
    <section id={id} aria-labelledby={`${id}-heading`} className="ds-section">
      <h2 id={`${id}-heading`} className="ds-section__title">
        {title}
      </h2>
      <div className="ds-section__body">{children}</div>
    </section>
  )
}

/* ── Row inside section ───────────────────────────────────── */
function Row({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <div className="ds-row">
      <span className="ds-row__label">{label}</span>
      <div className="ds-row__content">{children}</div>
    </div>
  )
}

/* ── Color swatch ─────────────────────────────────────────── */
function Swatch({ token, label }: { token: string; label: string }) {
  return (
    <div className="ds-swatch">
      <div
        className="ds-swatch__color"
        style={{ background: `var(${token})` }}
        title={token}
      />
      <span className="ds-swatch__token">{token}</span>
      <span className="ds-swatch__label">{label}</span>
    </div>
  )
}

/* ── Main page ────────────────────────────────────────────── */
export function DesignSystemPage() {
  const { theme, toggleTheme } = useTheme()
  const [inputValue, setInputValue] = useState('')
  const [inputError, setInputError] = useState('')

  const handleInputDemo = (v: string) => {
    setInputValue(v)
    setInputError(v.length > 0 && v.length < 3 ? 'Minimum 3 characters' : '')
  }

  return (
    <PageContainer>
      <Breadcrumbs items={[{ label: 'Design Lab' }]} />

      {/* Page header */}
      <div className="page-header">
        <p className="page-header__label">Internal · Developer Reference</p>
        <h1 className="page-header__title">
          <FlaskConical
            size={22}
            aria-hidden="true"
            style={{ display: 'inline', verticalAlign: 'middle', marginRight: 8 }}
          />
          Design Lab
        </h1>
        <p className="page-header__description">
          Visual reference for C-NOTE's design tokens and UI primitives.
          This page is not user-facing and will be removed before any public release.
        </p>
      </div>

      {/* Theme toggle strip */}
      <div className="ds-theme-strip">
        <span className="ds-theme-strip__label">
          Current theme: <strong>{theme}</strong>
        </span>
        <Button variant="secondary" size="sm" onClick={toggleTheme}>
          {theme === 'dark' ? <Sun size={13} /> : <Moon size={13} />}
          Switch to {theme === 'dark' ? 'light' : 'dark'}
        </Button>
      </div>

      <Divider />

      {/* ── Colors ── */}
      <Section id="colors" title="Color Tokens">
        <div className="ds-swatch-group">
          <p className="ds-group-label">Background / Surface</p>
          <div className="ds-swatches">
            <Swatch token="--color-background"     label="Background" />
            <Swatch token="--color-surface"         label="Surface" />
            <Swatch token="--color-surface-raised"  label="Raised" />
            <Swatch token="--color-surface-hover"   label="Hover" />
          </div>
        </div>

        <div className="ds-swatch-group">
          <p className="ds-group-label">Text</p>
          <div className="ds-swatches">
            <Swatch token="--color-text-primary"   label="Primary" />
            <Swatch token="--color-text-secondary" label="Secondary" />
            <Swatch token="--color-text-muted"     label="Muted" />
            <Swatch token="--color-text-disabled"  label="Disabled" />
          </div>
        </div>

        <div className="ds-swatch-group">
          <p className="ds-group-label">Borders</p>
          <div className="ds-swatches">
            <Swatch token="--color-border"        label="Border" />
            <Swatch token="--color-border-subtle" label="Subtle" />
          </div>
        </div>

        <div className="ds-swatch-group">
          <p className="ds-group-label">Semantic</p>
          <div className="ds-swatches">
            <Swatch token="--color-accent"   label="Accent" />
            <Swatch token="--color-success"  label="Success" />
            <Swatch token="--color-warning"  label="Warning" />
            <Swatch token="--color-danger"   label="Danger" />
            <Swatch token="--color-info"     label="Info" />
          </div>
        </div>

        <div className="ds-swatch-group">
          <p className="ds-group-label">Difficulty</p>
          <div className="ds-swatches">
            <Swatch token="--color-difficulty-easy"   label="Easy" />
            <Swatch token="--color-difficulty-medium" label="Medium" />
            <Swatch token="--color-difficulty-hard"   label="Hard" />
          </div>
        </div>
      </Section>

      <Divider subtle />

      {/* ── Typography ── */}
      <Section id="typography" title="Typography">
        <div className="ds-type-stack">
          <div>
            <span className="ds-row__label">Display · 36px · bold</span>
            <p className="type-display">The quick brown fox</p>
          </div>
          <div>
            <span className="ds-row__label">Page Title · 28px · semibold</span>
            <p className="type-page-title">Computer Networks</p>
          </div>
          <div>
            <span className="ds-row__label">Section Title · 22px · semibold</span>
            <p className="type-section-title">TCP / IP Stack</p>
          </div>
          <div>
            <span className="ds-row__label">Subheading · 18px · medium</span>
            <p className="type-subheading">Application Layer</p>
          </div>
          <div>
            <span className="ds-row__label">Body · 15px · regular</span>
            <p className="type-body">
              The Transmission Control Protocol ensures reliable, ordered, and
              error-checked delivery of a stream of bytes between applications.
            </p>
          </div>
          <div>
            <span className="ds-row__label">Small · 13px</span>
            <p className="type-small">Updated 3 days ago · 12 questions</p>
          </div>
          <div>
            <span className="ds-row__label">Caption · 11px</span>
            <p className="type-caption">Phase 1 · Placeholder content</p>
          </div>
          <div>
            <span className="ds-row__label">Label · 11px · uppercase</span>
            <p className="type-label">Subject · Difficulty · Status</p>
          </div>
          <div>
            <span className="ds-row__label">Inline code</span>
            <p className="type-body">
              Use <code>O(n log n)</code> for sorting, <code>O(1)</code> for hash lookups.
            </p>
          </div>
        </div>
      </Section>

      <Divider subtle />

      {/* ── Buttons ── */}
      <Section id="buttons" title="Buttons">
        <Row label="Variants">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="danger">Danger</Button>
        </Row>
        <Row label="Sizes">
          <Button variant="secondary" size="sm">Small</Button>
          <Button variant="secondary" size="md">Medium</Button>
          <Button variant="secondary" size="lg">Large</Button>
        </Row>
        <Row label="With icon">
          <Button variant="primary" size="sm">
            <Search size={13} aria-hidden="true" /> Search
          </Button>
          <Button variant="secondary" size="sm">
            <Star size={13} aria-hidden="true" /> Bookmark
          </Button>
          <Button variant="danger" size="sm">
            <Trash2 size={13} aria-hidden="true" /> Delete
          </Button>
        </Row>
        <Row label="States">
          <Button variant="primary" isLoading>Loading</Button>
          <Button variant="secondary" disabled>Disabled</Button>
        </Row>
        <Row label="Icon buttons">
          <IconButton aria-label="Search" variant="ghost">
            <Search size={16} />
          </IconButton>
          <IconButton aria-label="Bookmark" variant="ghost">
            <Star size={16} />
          </IconButton>
          <Tooltip content="Delete item">
            <IconButton aria-label="Delete" variant="secondary">
              <Trash2 size={16} />
            </IconButton>
          </Tooltip>
        </Row>
      </Section>

      <Divider subtle />

      {/* ── Input ── */}
      <Section id="inputs" title="Input">
        <div className="ds-input-grid">
          <Input
            label="Default"
            placeholder="Type something…"
            value={inputValue}
            onChange={(e) => handleInputDemo(e.target.value)}
            hint="This is a hint message"
            error={inputError}
          />
          <Input
            label="With icon"
            placeholder="Search subjects…"
            leadingIcon={<Search size={14} />}
          />
          <Input
            label="Disabled"
            placeholder="Cannot edit"
            disabled
            defaultValue="Locked value"
          />
        </div>
      </Section>

      <Divider subtle />

      {/* ── Badges ── */}
      <Section id="badges" title="Badges">
        <Row label="Semantic">
          <Badge variant="default">Default</Badge>
          <Badge variant="accent">Accent</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="danger">Danger</Badge>
          <Badge variant="info">Info</Badge>
        </Row>
        <Row label="Difficulty">
          <Badge variant="difficulty-easy">Easy</Badge>
          <Badge variant="difficulty-medium">Medium</Badge>
          <Badge variant="difficulty-hard">Hard</Badge>
        </Row>
        <Row label="In context">
          <Badge variant="default">150 items</Badge>
          <Badge variant="default">Coming soon</Badge>
          <Badge variant="accent">Active</Badge>
        </Row>
      </Section>

      <Divider subtle />

      {/* ── Dividers ── */}
      <Section id="dividers" title="Dividers">
        <Row label="Default">
          <div style={{ width: '100%', flex: 1 }}>
            <Divider />
          </div>
        </Row>
        <Row label="Subtle">
          <div style={{ width: '100%', flex: 1 }}>
            <Divider subtle />
          </div>
        </Row>
        <Row label="Labeled">
          <div style={{ width: '100%', flex: 1 }}>
            <Divider label="or" />
          </div>
        </Row>
        <Row label="Vertical">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, height: 24 }}>
            <span className="type-small">Item A</span>
            <Divider orientation="vertical" />
            <span className="type-small">Item B</span>
            <Divider orientation="vertical" />
            <span className="type-small">Item C</span>
          </div>
        </Row>
      </Section>

      <Divider subtle />

      {/* ── Spinners ── */}
      <Section id="loading" title="Loading & Skeleton">
        <Row label="Spinner sizes">
          <Spinner size="sm" />
          <Spinner size="md" />
          <Spinner size="lg" />
        </Row>
        <Row label="Skeleton block">
          <Skeleton width={200} height={14} />
          <Skeleton width={140} height={14} />
          <Skeleton width={80} height={14} />
        </Row>
        <Row label="Skeleton text">
          <div style={{ width: 300 }}>
            <SkeletonText lines={4} />
          </div>
        </Row>
        <Row label="Skeleton rounded">
          <Skeleton width={40} height={40} rounded />
          <Skeleton width={80} height={16} />
        </Row>
      </Section>

      <Divider subtle />

      {/* ── Empty State ── */}
      <Section id="empty-state" title="Empty State">
        <div className="ds-feedback-grid">
          <div className="ds-feedback-box">
            <EmptyState
              icon={<Inbox size={28} />}
              title="No items yet"
              description="This section is empty. Content will appear here once it is added."
              action={<Button variant="secondary" size="sm">Add item</Button>}
            />
          </div>
          <div className="ds-feedback-box">
            <EmptyState
              icon={<BookOpen size={28} />}
              title="No subjects found"
              description="Try adjusting your search or filters."
            />
          </div>
        </div>
      </Section>

      <Divider subtle />

      {/* ── Feedback States ── */}
      <Section id="feedback" title="Feedback States">
        <div className="ds-feedback-grid">
          <div className="ds-feedback-box">
            <ErrorState
              title="Failed to load"
              description="Could not fetch subject data. Please try again."
              onRetry={() => {}}
            />
          </div>
          <div className="ds-feedback-box">
            <LoadingState message="Loading subjects…" />
          </div>
        </div>
        <div className="ds-feedback-box" style={{ marginTop: 'var(--space-4)' }}>
          <NotFound message="The subject you are looking for does not exist." />
        </div>
      </Section>

      <Divider subtle />

      {/* ── Code block placeholder ── */}
      <Section id="code" title="Code Block (Placeholder)">
        <p className="type-small" style={{ marginBottom: 'var(--space-3)', color: 'var(--color-text-muted)' }}>
          Full syntax-highlighted code blocks will be implemented in Phase 2 using a lightweight highlighter.
        </p>
        <div className="ds-code-block">
          <div className="ds-code-block__header">
            <Code2 size={13} aria-hidden="true" />
            <span>python</span>
          </div>
          <pre className="ds-code-block__body">
            <code>{`def contains_duplicate(nums: list[int]) -> bool:
    seen = set()
    for n in nums:
        if n in seen:
            return True
        seen.add(n)
    return False`}</code>
          </pre>
        </div>
      </Section>

      <Divider subtle />

      {/* ── Callouts ── */}
      <Section id="callouts" title="Callout Variants">
        <div className="ds-callout-stack">
          <div className="callout callout--info">
            <Info size={15} aria-hidden="true" className="callout__icon" />
            <div>
              <strong>Note:</strong> This is an informational callout. Use for context and background.
            </div>
          </div>
          <div className="callout callout--success">
            <CheckCircle size={15} aria-hidden="true" className="callout__icon" />
            <div>
              <strong>Tip:</strong> This pattern has O(n) time complexity using a hash set.
            </div>
          </div>
          <div className="callout callout--warning">
            <AlertTriangle size={15} aria-hidden="true" className="callout__icon" />
            <div>
              <strong>Warning:</strong> Watch out for integer overflow in languages without big integers.
            </div>
          </div>
          <div className="callout callout--danger">
            <AlertTriangle size={15} aria-hidden="true" className="callout__icon" />
            <div>
              <strong>Important:</strong> Never modify a list while iterating over it.
            </div>
          </div>
        </div>
      </Section>

      {/* Footer note */}
      <div style={{ marginTop: 'var(--space-16)', paddingTop: 'var(--space-6)', borderTop: '1px solid var(--color-border-subtle)' }}>
        <p className="type-caption">
          Design Lab · C-NOTE Phase 1 · Developer reference only · Not user-facing
        </p>
      </div>
    </PageContainer>
  )
}

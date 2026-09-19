/* ============================================================
   Skeleton — C-NOTE UI Primitive
   Placeholder shimmer for loading states.
   ============================================================ */

interface SkeletonProps {
  width?: string | number
  height?: string | number
  rounded?: boolean
  className?: string
}

export function Skeleton({
  width,
  height,
  rounded = false,
  className = '',
}: SkeletonProps) {
  return (
    <span
      className={`skeleton ${rounded ? 'skeleton--rounded' : ''} ${className}`}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
      }}
      aria-hidden="true"
    />
  )
}

/** A multi-line text skeleton block */
export function SkeletonText({ lines = 3 }: { lines?: number }) {
  return (
    <div className="skeleton-text" aria-hidden="true">
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton
          key={i}
          width={i === lines - 1 ? '65%' : '100%'}
          height={14}
          className="skeleton-text__line"
        />
      ))}
    </div>
  )
}

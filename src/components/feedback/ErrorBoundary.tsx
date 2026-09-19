/* ============================================================
   ErrorBoundary — catches React rendering errors
   ============================================================ */

import { Component, type ReactNode, type ErrorInfo } from 'react'
import { ErrorState } from './ErrorState'

interface Props {
  children: ReactNode
  /** Custom fallback — if not provided, renders ErrorState */
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // In production, send to an error reporting service
    if (import.meta.env.DEV) {
      console.error('[C-NOTE ErrorBoundary]', error, info)
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback

      return (
        <ErrorState
          title="Something went wrong"
          description={
            import.meta.env.DEV && this.state.error
              ? this.state.error.message
              : 'An unexpected error occurred. Please try refreshing the page.'
          }
          onRetry={this.handleReset}
        />
      )
    }

    return this.props.children
  }
}

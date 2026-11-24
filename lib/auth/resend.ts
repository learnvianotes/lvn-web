type Problem = { code?: string | null; message?: string | null; retryAfter?: number | null }

/**
 * What to show after resendVerification. A RATE_LIMITED error keeps the API's sentence and adds the wait
 * from retryAfter when the sentence does not already contain that number.
 */
export function resendVerificationNotice(problems: readonly Problem[] | null | undefined, wait: (seconds: number) => string): { tone: 'success' } | { tone: 'error'; message: string } | { tone: 'empty' } {
  const problem = problems?.find((item) => item.message?.trim() || item.code === 'RATE_LIMITED')
  if (!problem) return { tone: 'empty' }
  const message = problem.message?.trim() ?? ''
  const waitFor = problem.code === 'RATE_LIMITED' ? problem.retryAfter : null
  if (waitFor != null && waitFor > 0 && !message.includes(String(waitFor))) {
    const extra = wait(waitFor)
    return { tone: 'error', message: message ? `${message} ${extra}` : extra }
  }
  return { tone: 'error', message: message }
}

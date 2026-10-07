/* Activity tracking was for signed-in learners only; /core is guest-only and sends nothing (spec §15.2). */
export const track: (type: string, fields?: Record<string, unknown>) => void = () => {}

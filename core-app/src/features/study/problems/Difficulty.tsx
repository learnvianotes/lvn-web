export function Difficulty({ level }: { level: string }) {
  return <span className={`difficulty difficulty--${level.toLowerCase()}`}>{level}</span>
}

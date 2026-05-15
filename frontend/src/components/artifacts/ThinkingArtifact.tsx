interface ThinkingArtifactProps {
  payload: string
}

export default function ThinkingArtifact({ payload }: ThinkingArtifactProps) {
  const isComplete = payload === 'Анализ завершён.'

  return (
    <div className="flex items-start gap-3 text-sm text-text-secondary italic py-2">
      <span className="mt-0.5 flex-shrink-0 text-base">
        {isComplete ? '✓' : <span className="animate-spin inline-block">⟳</span>}
      </span>
      <span>
        {payload}
      </span>
    </div>
  )
}

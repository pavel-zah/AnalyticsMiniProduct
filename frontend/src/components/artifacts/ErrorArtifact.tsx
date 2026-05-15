interface ErrorArtifactProps {
  payload: string
}

export default function ErrorArtifact({ payload }: ErrorArtifactProps) {
  return (
    <div className="bg-error-bg border border-error-border rounded-lg p-4">
      <div className="flex items-start gap-3">
        <span className="text-xl flex-shrink-0">⚠️</span>
        <div className="text-sm text-error-text leading-relaxed">
          {payload}
        </div>
      </div>
    </div>
  )
}

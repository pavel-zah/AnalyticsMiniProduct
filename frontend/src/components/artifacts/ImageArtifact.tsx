import { useState } from 'react'

interface ImageArtifactProps {
  title?: string
  payload: string
}

export default function ImageArtifact({ title, payload }: ImageArtifactProps) {
  const [hasError, setHasError] = useState(false)

  if (!payload) {
    return (
      <div className="text-center text-text-secondary py-4">
        Изображение недоступно
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {title && (
        <h3 className="text-lg font-semibold text-text-primary">
          {title}
        </h3>
      )}
      <div className="border border-border-gray rounded-lg bg-white p-4">
        {hasError ? (
          <div className="text-sm text-error-text">
            Не удалось загрузить изображение
          </div>
        ) : (
          <img
            src={payload}
            alt={title || 'График'}
            onError={() => setHasError(true)}
            style={{
              display: 'block',
              width: '100%',
              maxWidth: '100%',
              height: 'auto',
            }}
          />
        )}
      </div>
    </div>
  )
}

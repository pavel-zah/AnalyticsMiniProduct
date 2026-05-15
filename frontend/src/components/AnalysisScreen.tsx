import { useEffect, useState, useRef } from 'react'
import { Artifact } from '../App'
import ArtifactRenderer from './ArtifactRenderer'

interface AnalysisScreenProps {
  sessionId: string
  fileName: string
  artifacts: Artifact[]
  setArtifacts: (artifacts: Artifact[]) => void
  onNewAnalysis: () => void
}

export default function AnalysisScreen({
  sessionId,
  fileName,
  artifacts,
  setArtifacts,
  onNewAnalysis,
}: AnalysisScreenProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(true)
  const [error, setError] = useState('')
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const eventSource = new EventSource(`/v1/stream/${sessionId}`)

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        const newArtifact: Artifact = data

        setArtifacts((prev) => [...prev, newArtifact])

        if (newArtifact.type === 'thinking' && newArtifact.payload === 'Анализ завершён.') {
          eventSource.close()
          setIsAnalyzing(false)
        }
      } catch (err) {
        console.error('Error parsing artifact:', err)
      }
    }

    eventSource.onerror = () => {
      setError('Потеря соединения с сервером')
      eventSource.close()
      setIsAnalyzing(false)
    }

    return () => {
      eventSource.close()
    }
  }, [sessionId, setArtifacts])

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [artifacts])

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'white' }}>
      {/* Header */}
      <div style={{
        position: 'sticky',
        top: 0,
        zIndex: 10,
        backgroundColor: 'white',
        borderBottom: '1px solid var(--color-border)',
      }}>
        <div style={{
          maxWidth: 'var(--width-content)',
          margin: '0 auto',
          padding: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                Анализируется файл
              </p>
              <p style={{ 
                fontWeight: 600, 
                fontSize: '0.875rem', 
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                maxWidth: '300px'
              }}>
                {fileName}
              </p>
            </div>
          </div>
          <button
            onClick={onNewAnalysis}
            style={{
              padding: '8px 16px',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: 'var(--color-primary)',
              backgroundColor: 'transparent',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer',
              transition: 'background-color 0.2s',
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--color-bg-secondary)'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            Новый анализ
          </button>
        </div>
      </div>

      {/* Artifacts Container */}
      <div
        ref={containerRef}
        style={{
          maxHeight: 'calc(100vh - 80px)',
          overflowY: 'auto',
        }}
      >
        <div style={{
          width: '100%',
          maxWidth: 'var(--width-content)',
          margin: '0 auto',
          padding: '32px 16px',
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {artifacts.length === 0 && isAnalyzing && (
              <div style={{ textAlign: 'center', padding: '48px 0' }}>
                <div style={{ display: 'inline-block' }}>
                  <div className="animate-spin" style={{ fontSize: '2.25rem', marginBottom: '16px' }}>
                    ⟳
                  </div>
                  <p style={{ color: 'var(--color-text-secondary)' }}>
                    Инициализация анализа...
                  </p>
                </div>
              </div>
            )}

            {artifacts.map((artifact, idx) => (
              <div key={idx} className="animate-fadeInUp">
                <ArtifactRenderer artifact={artifact} />
              </div>
            ))}

            {error && (
              <div style={{
                backgroundColor: 'var(--color-error-bg)',
                border: '1px solid var(--color-error-border)',
                borderRadius: 'var(--radius-md)',
                padding: '16px',
                color: 'var(--color-error-text)',
              }}>
                ⚠️ {error}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Loading Indicator */}
      {isAnalyzing && artifacts.length > 0 && (
        <div style={{
          position: 'fixed',
          bottom: '32px',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: 'var(--color-primary)',
          color: 'white',
          padding: '12px 24px',
          borderRadius: '9999px',
          boxShadow: 'var(--shadow-light)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}
          className="animate-pulse"
        >
          <div className="animate-spin">⟳</div>
          <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>
            Агент анализирует данные...
          </span>
        </div>
      )}
    </div>
  )
}
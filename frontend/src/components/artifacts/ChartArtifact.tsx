import { useEffect, useRef, useState } from 'react'
import Plot from 'react-plotly.js'

interface ChartArtifactProps {
  title?: string
  payload: string
}

export default function ChartArtifact({ title, payload }: ChartArtifactProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState<{ width: number; height: number } | null>(null)

    useEffect(() => {
    console.group('🔍 ChartArtifact Full Debug')
    console.log('Title:', title)
    console.log('Payload type:', typeof payload)
    console.log('Payload length:', payload?.length)
    console.log('Payload (first 2000 chars):', payload?.substring(0, 2000))
    
    try {
      let cleaned = payload.trim()
      if (cleaned.startsWith('"') && cleaned.endsWith('"')) {
        cleaned = JSON.parse(cleaned)
      }
      const parsed = JSON.parse(cleaned)
      console.log('✅ Parsed successfully!')
      console.log('Parsed keys:', Object.keys(parsed))
      console.log('Data:', parsed.data)
      console.log('Data type:', Array.isArray(parsed.data))
      console.log('Data length:', parsed.data?.length)
      if (parsed.data && parsed.data.length > 0) {
        console.log('First trace:', parsed.data[0])
        console.log('First trace keys:', Object.keys(parsed.data[0]))
      }
      console.log('Layout:', parsed.layout)
    } catch (e) {
      console.error('❌ Parse failed:', e)
    }
    console.groupEnd()
  }, [payload, title])

  useEffect(() => {
    if (!containerRef.current) return

    const updateDimensions = () => {
      const rect = containerRef.current?.getBoundingClientRect()
      if (rect && rect.width > 0) {
        const width = Math.max(300, rect.width - 48) // 48px для padding
        const height = Math.max(400, width * 0.6)
        setDimensions({ width, height })
      }
    }

    // Измеряем с небольшой задержкой для корректного layout
    const timer = setTimeout(updateDimensions, 100)
    
    const resizeObserver = new ResizeObserver(updateDimensions)
    resizeObserver.observe(containerRef.current)
    window.addEventListener('resize', updateDimensions)

    return () => {
      clearTimeout(timer)
      resizeObserver.disconnect()
      window.removeEventListener('resize', updateDimensions)
    }
  }, [])

  try {
    if (!payload || typeof payload !== 'string') {
      throw new Error('Invalid payload')
    }

    let figData
    let cleaned = payload.trim()

    // Убираем двойную сериализацию
    if (cleaned.startsWith('"') && cleaned.endsWith('"')) {
      cleaned = JSON.parse(cleaned)
    }

    // Парсинг
    try {
      figData = JSON.parse(cleaned)
    } catch (e) {
      const start = cleaned.indexOf('{')
      const end = cleaned.lastIndexOf('}')
      if (start !== -1 && end !== -1) {
        figData = JSON.parse(cleaned.substring(start, end + 1))
      } else {
        throw e
      }
    }

    if (!figData.data || !Array.isArray(figData.data)) {
      throw new Error('Missing or invalid "data" array')
    }

    // Показываем placeholder пока не измерили контейнер
    if (!dimensions) {
      return (
        <div className="space-y-4">
          {title && (
            <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
              {title}
            </h3>
          )}
          <div 
            ref={containerRef} 
            style={{
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--spacing-lg)',
              backgroundColor: 'var(--color-bg-primary)',
              minHeight: '400px',
              width: '100%',
            }}
          >
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              height: '400px',
              color: 'var(--color-text-secondary)' 
            }}>
              Загрузка графика...
            </div>
          </div>
        </div>
      )
    }

    // Рендерим график
    const layout = {
      ...figData.layout,
      width: dimensions.width,
      height: dimensions.height,
      autosize: false,
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'rgba(245, 245, 247, 0.3)',
      font: { 
        family: 'SF Pro Display, -apple-system, system-ui, sans-serif',
        size: 12,
        color: '#000000'
      },
      margin: { l: 60, r: 40, t: 40, b: 60 },
      xaxis: {
        ...figData.layout?.xaxis,
        gridcolor: 'rgba(0, 0, 0, 0.05)',
      },
      yaxis: {
        ...figData.layout?.yaxis,
        gridcolor: 'rgba(0, 0, 0, 0.05)',
      }
    }

    return (
      <div className="space-y-4">
        {title && (
          <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {title}
          </h3>
        )}
        <div 
          ref={containerRef}
          style={{
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--spacing-lg)',
            backgroundColor: 'var(--color-bg-primary)',
            overflow: 'hidden',
            width: '100%',
          }}
        >
                    <Plot
            key={dimensions ? `${dimensions.width}x${dimensions.height}` : 'loading'}
            data={figData.data}
            layout={layout}
            config={{
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
            revision={Date.now()}
          />
        </div>
      </div>
    )

  } catch (err) {
    console.error('❌ Chart rendering error:', err)
    console.error('Payload preview:', payload?.substring(0, 500))
    
    return (
      <div className="space-y-4">
        {title && (
          <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {title}
          </h3>
        )}
        <div style={{
          backgroundColor: 'var(--color-error-bg)',
          border: '1px solid var(--color-error-border)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--spacing-md)',
          color: 'var(--color-error-text)',
        }}>
          <div style={{ fontWeight: 600, marginBottom: '8px' }}>
            ⚠️ Ошибка отрисовки графика
          </div>
          <div style={{ fontSize: '0.875rem' }}>
            {err instanceof Error ? err.message : 'Unknown error'}
          </div>
          <details style={{ marginTop: '8px', fontSize: '0.75rem' }}>
            <summary style={{ cursor: 'pointer' }}>Показать детали</summary>
            <pre style={{ 
              marginTop: '8px', 
              padding: '8px', 
              backgroundColor: '#FFE0E0',
              borderRadius: '4px',
              overflow: 'auto',
              maxHeight: '160px',
              fontSize: '0.75rem'
            }}>
              {payload?.substring(0, 1000)}
            </pre>
          </details>
        </div>
      </div>
    )
  }
}
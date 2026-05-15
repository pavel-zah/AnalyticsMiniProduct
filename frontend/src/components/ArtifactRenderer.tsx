import { Artifact } from '../App'
import ThinkingArtifact from './artifacts/ThinkingArtifact'
import TextArtifact from './artifacts/TextArtifact'
import CodeArtifact from './artifacts/CodeArtifact'
import ChartArtifact from './artifacts/ChartArtifact'
import ImageArtifact from './artifacts/ImageArtifact'
import TableArtifact from './artifacts/TableArtifact'
import ErrorArtifact from './artifacts/ErrorArtifact'

interface ArtifactRendererProps {
  artifact: Artifact
}

export default function ArtifactRenderer({ artifact }: ArtifactRendererProps) {
  return (
    <div style={{ width: '100%' }}>
      {(() => {
        switch (artifact.type) {
          case 'thinking':
            return <ThinkingArtifact payload={artifact.payload} />
          case 'text':
            return <TextArtifact title={artifact.title} payload={artifact.payload} />
          case 'code':
            return <CodeArtifact title={artifact.title} payload={artifact.payload} />
          case 'chart':
            return <ChartArtifact title={artifact.title} payload={artifact.payload} />
          case 'image':
            return <ImageArtifact title={artifact.title} payload={artifact.payload} />
          case 'table':
            return <TableArtifact title={artifact.title} payload={artifact.payload} />
          case 'error':
            return <ErrorArtifact payload={artifact.payload} />
          default:
            return null
        }
      })()}
    </div>
  )
}
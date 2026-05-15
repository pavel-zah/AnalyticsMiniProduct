import { useState } from 'react'
import UploadScreen from './components/UploadScreen'
import AnalysisScreen from './components/AnalysisScreen'

export interface Artifact {
  type: 'thinking' | 'text' | 'code' | 'chart' | 'image' | 'table' | 'error'
  payload: string
  title?: string
}

function App() {
  const [screen, setScreen] = useState<'upload' | 'analysis'>('upload')
  const [sessionId, setSessionId] = useState<string>('')
  const [fileName, setFileName] = useState<string>('')
  const [artifacts, setArtifacts] = useState<Artifact[]>([])

  const handleUploadStart = (sid: string, fname: string) => {
    setSessionId(sid)
    setFileName(fname)
    setArtifacts([])
    setScreen('analysis')
  }

  const handleNewAnalysis = () => {
    setScreen('upload')
    setSessionId('')
    setFileName('')
    setArtifacts([])
  }

  return (
    <div className="min-h-screen bg-white">
      {screen === 'upload' ? (
        <UploadScreen onUploadStart={handleUploadStart} />
      ) : (
        <AnalysisScreen
          sessionId={sessionId}
          fileName={fileName}
          artifacts={artifacts}
          setArtifacts={setArtifacts}
          onNewAnalysis={handleNewAnalysis}
        />
      )}
    </div>
  )
}

export default App

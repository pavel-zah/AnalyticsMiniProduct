import { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface CodeArtifactProps {
  title?: string
  payload: string
}

export default function CodeArtifact({ title, payload }: CodeArtifactProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(payload)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-text-secondary uppercase tracking-wide">Python</span>
          {title && <span className="text-sm text-text-secondary">— {title}</span>}
        </div>
        <button
          onClick={handleCopy}
          className="px-3 py-1 text-xs font-medium text-text-secondary hover:bg-light-gray
                     rounded transition-colors"
        >
          {copied ? '✓ Скопировано' : 'Копировать'}
        </button>
      </div>
      
      <div className="bg-light-gray rounded-lg overflow-hidden border border-border-gray">
        <SyntaxHighlighter
          language="python"
          style={oneLight}
          showLineNumbers={false}
          customStyle={{
            margin: 0,
            padding: '16px',
            backgroundColor: '#F5F5F7',
            fontSize: '13px',
            lineHeight: '1.5',
          }}
        >
          {payload}
        </SyntaxHighlighter>
      </div>
    </div>
  )
}

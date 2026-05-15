import { useState } from 'react'

interface UploadScreenProps {
  onUploadStart: (sessionId: string, fileName: string) => void
}

export default function UploadScreen({ onUploadStart }: UploadScreenProps) {
  const [file, setFile] = useState<File | null>(null)
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.name.endsWith('.csv')) {
      setFile(droppedFile)
      setError('')
    } else {
      setError('Пожалуйста, выберите CSV файл')
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile)
      setError('')
    } else {
      setError('Пожалуйста, выберите CSV файл')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('user_message', prompt)

      const response = await fetch('/v1/analyse', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        // Улучшенная обработка ошибок
        const contentType = response.headers.get('content-type')
        
        if (contentType?.includes('application/json')) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Ошибка при загрузке файла')
        } else {
          throw new Error(`Ошибка сервера (${response.status})`)
        }
      }

      const data = await response.json()
      onUploadStart(data.session_id, file.name)
    } catch (err) {
      console.error('Upload error:', err)  // Для отладки
      setError(err instanceof Error ? err.message : 'Ошибка при загрузке')
      setLoading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="max-w-content w-full">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-2">Analytics Agent</h1>
          <p className="text-text-secondary text-lg">Загрузите данные для анализа</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Drag and Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className="relative border-2 border-dashed border-border-gray rounded-2xl p-12 text-center
                       transition-all hover:border-primary-blue hover:bg-light-gray/30 cursor-pointer
                       bg-white"
          >
            <input
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            
            {file ? (
              <div>
                <div className="text-4xl mb-3">✓</div>
                <p className="font-semibold text-sm mb-1">{file.name}</p>
                <p className="text-text-secondary text-sm">{formatFileSize(file.size)}</p>
              </div>
            ) : (
              <div>
                <div className="text-4xl mb-3">📄</div>
                <p className="font-semibold text-sm mb-1">Перетащите CSV файл</p>
                <p className="text-text-secondary text-sm">или нажмите для выбора</p>
              </div>
            )}
          </div>

          {/* Prompt Textarea */}
          <div>
            <label className="block text-sm font-medium mb-3">
              Описание анализа (опционально)
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Опишите что хотите узнать из данных... Или оставьте пустым для стандартного анализа"
              className="w-full h-32 p-4 border border-border-gray rounded-lg bg-white
                         focus:ring-2 focus:ring-primary-blue focus:border-transparent
                         resize-none text-sm leading-relaxed"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-error-bg border border-error-border rounded-lg p-4 text-error-text text-sm">
              ⚠️ {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!file || loading}
            className="w-full py-3 px-4 bg-primary-blue hover:bg-blue-600 disabled:bg-gray-300
                       text-white font-semibold rounded-lg transition-colors duration-200
                       disabled:cursor-not-allowed"
          >
            {loading ? 'Загрузка...' : 'Начать анализ'}
          </button>
        </form>
      </div>
    </div>
  )
}

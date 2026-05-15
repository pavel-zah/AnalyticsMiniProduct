import { useState } from 'react'

interface TableArtifactProps {
  title?: string
  payload: string
}

export default function TableArtifact({ title, payload }: TableArtifactProps) {
  const [showAll, setShowAll] = useState(false)

  try {
    const data = JSON.parse(payload)
    
    if (!Array.isArray(data) || data.length === 0) {
      return (
        <div className="text-center text-text-secondary py-4">
          Таблица пуста
        </div>
      )
    }

    const columns = Object.keys(data[0])
    const displayData = showAll ? data : data.slice(0, 10)
    const hasMore = data.length > 10

    return (
      <div className="space-y-3">
        {title && (
          <h3 className="text-lg font-semibold text-text-primary">
            {title}
          </h3>
        )}
        
        <div className="border border-border-gray rounded-lg overflow-hidden bg-white">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-light-gray border-b border-border-gray">
                  {columns.map((col) => (
                    <th
                      key={col}
                      className="px-4 py-3 text-left font-semibold text-text-primary"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {displayData.map((row, idx) => (
                  <tr
                    key={idx}
                    className={`border-b border-border-gray ${
                      idx % 2 === 0 ? 'bg-white' : 'bg-light-gray/30'
                    } hover:bg-light-gray/50 transition-colors`}
                  >
                    {columns.map((col) => (
                      <td
                        key={`${idx}-${col}`}
                        className="px-4 py-3 text-text-primary"
                      >
                        {String(row[col]).substring(0, 100)}
                        {String(row[col]).length > 100 ? '...' : ''}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {hasMore && !showAll && (
          <button
            onClick={() => setShowAll(true)}
            className="text-sm font-medium text-primary-blue hover:underline py-2"
          >
            Показать все {data.length} строк
          </button>
        )}

        {showAll && (
          <button
            onClick={() => setShowAll(false)}
            className="text-sm font-medium text-primary-blue hover:underline py-2"
          >
            Скрыть
          </button>
        )}
      </div>
    )
  } catch (err) {
    return (
      <div className="bg-error-bg border border-error-border rounded-lg p-4 text-error-text text-sm">
        ⚠️ Ошибка при отрисовке таблицы
      </div>
    )
  }
}

import ReactMarkdown from 'react-markdown'

interface TextArtifactProps {
  title?: string
  payload: string
}

export default function TextArtifact({ title, payload }: TextArtifactProps) {
  return (
    <div className="space-y-3">
      {title && (
        <h3 className="text-lg font-semibold text-text-primary">
          {title}
        </h3>
      )}
      <div className="markdown prose prose-sm max-w-none text-text-primary">
        <ReactMarkdown
          components={{
            h1: ({ node, ...props }) => <h1 className="text-2xl font-bold my-4" {...props} />,
            h2: ({ node, ...props }) => <h2 className="text-xl font-bold my-3" {...props} />,
            h3: ({ node, ...props }) => <h3 className="text-lg font-semibold my-2" {...props} />,
            p: ({ node, ...props }) => <p className="my-2 leading-relaxed" {...props} />,
            ul: ({ node, ...props }) => <ul className="list-disc list-inside my-2 space-y-1" {...props} />,
            ol: ({ node, ...props }) => <ol className="list-decimal list-inside my-2 space-y-1" {...props} />,
            li: ({ node, ...props }) => <li className="ml-2" {...props} />,
            code: ({ node, inline, ...props }) =>
              inline ? (
                <code className="bg-light-gray px-2 py-1 rounded text-sm font-mono text-primary-blue" {...props} />
              ) : (
                <code className="block bg-light-gray p-3 rounded text-sm font-mono my-2 overflow-x-auto" {...props} />
              ),
            blockquote: ({ node, ...props }) => (
              <blockquote className="border-l-4 border-primary-blue pl-4 py-2 my-2 italic text-text-secondary" {...props} />
            ),
            table: ({ node, ...props }) => (
              <table className="border-collapse border border-border-gray my-2 w-full text-sm" {...props} />
            ),
            thead: ({ node, ...props }) => (
              <thead className="bg-light-gray" {...props} />
            ),
            tr: ({ node, ...props }) => (
              <tr className="border-b border-border-gray" {...props} />
            ),
            td: ({ node, ...props }) => (
              <td className="border border-border-gray px-3 py-2" {...props} />
            ),
            th: ({ node, ...props }) => (
              <th className="border border-border-gray px-3 py-2 font-semibold text-left" {...props} />
            ),
          }}
        >
          {payload}
        </ReactMarkdown>
      </div>
    </div>
  )
}

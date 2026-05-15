# Analytics Agent Frontend

React + TypeScript фронтенд для AI агента анализа данных с поддержкой real-time обновлений через SSE.

## Стек технологий

- **React 18** + **TypeScript** — UI компоненты
- **Tailwind CSS** + CSS переменные — стилизация в стиле Apple Design
- **Vite** — быстрая сборка
- **react-plotly.js** — интерактивные графики
- **react-markdown** + **react-syntax-highlighter** — рендер markdown и кода

## Структура проекта

```
src/
├── components/
│   ├── UploadScreen.tsx         # Экран загрузки файла
│   ├── AnalysisScreen.tsx       # Экран с потоком артефактов
│   ├── ArtifactRenderer.tsx     # Роутер типов артефактов
│   └── artifacts/
│       ├── ThinkingArtifact.tsx # Процесс анализа
│       ├── TextArtifact.tsx     # Markdown блоки
│       ├── CodeArtifact.tsx     # Код с подсветкой
│       ├── ChartArtifact.tsx    # Plotly графики
│       ├── TableArtifact.tsx    # Красивые таблицы
│       └── ErrorArtifact.tsx    # Ошибки
├── App.tsx                      # Главный компонент с роутингом
├── index.css                    # Глобальные стили
└── main.tsx                     # Entry point
```

## Установка и запуск

### 1. Установка зависимостей

```bash
npm install
```

### 2. Запуск dev сервера

```bash
npm run dev
```

Приложение откроется на `http://localhost:3000`

### 3. Сборка для production

```bash
npm run build
```

## API интеграция

### Endpoints

- **POST /api/upload** — загрузка CSV файла и промпта
  ```json
  {
    "file": File,
    "prompt": "string (опционально)"
  }
  ```
  Ответ: `{ "session_id": "string" }`

- **GET /api/stream/:session_id** — SSE поток с артефактами
  Формат события: `{ type, payload, title? }`

## Типы артефактов

| Type | Описание |
|------|---------|
| `thinking` | Процесс анализа (иконка спиннера → галочка) |
| `text` | Markdown блок с заголовком |
| `code` | Python код с подсветкой синтаксиса |
| `chart` | Plotly график в JSON формате |
| `table` | JSON массив объектов (пагинация > 10 строк) |
| `error` | Красная карточка с ошибкой |

## Дизайн

**Apple-inspired минимализм:**
- Белый фон, тонкие бордеры (1px, opacity 0.1-0.15)
- Большие скруглённые углы (16-20px)
- Акцентный цвет: #007AFF (Apple blue)
- Max-width: 680px, по центру
- Щедрые отступы, очень лёгкие тени

## CSS переменные

```css
--color-primary: #007AFF
--color-bg-primary: #FFFFFF
--color-bg-secondary: #F5F5F7
--color-text-primary: #000000
--color-text-secondary: #8E8E93
--color-border: rgba(0, 0, 0, 0.1)
--color-error-bg: #FFF2F2
--color-error-border: #FFD0D0
```

## Browser Support

- Chrome/Edge (последние 2 версии)
- Firefox (последние 2 версии)
- Safari 14+

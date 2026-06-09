import React, { useState, useRef, useEffect } from 'react';
import { Upload, Send, CheckSquare, Square, Trash2 } from 'lucide-react';

export default function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Состояния для модалки и выбора категории
  const [uploadModal, setUploadModal] = useState({ open: false, file: null });
  const [docCategory, setDocCategory] = useState('other'); 
  
  const fileInputRef = useRef(null);

  // --- 1. ЗАГРУЗКА СПИСКА ДОКУМЕНТОВ ПРИ СТАРТЕ ---
  const fetchDocuments = async () => {
    try {
      const res = await fetch('http://localhost:8000/documents/');
      if (res.ok) {
        const data = await res.json();
        
        console.log("=== ЧТО ПРИШЛО С БЭКЕНДА ===", data);
        
        if (Array.isArray(data)) {
          setDocuments(data);
        } else if (data && Array.isArray(data.documents)) {
          setDocuments(data.documents);
        } else if (data && Array.isArray(data.items)) {
          setDocuments(data.items);
        } else {
          console.warn("Бэкенд вернул что-то странное, это не массив:", data);
        }
      }
    } catch (e) {
      console.error("Ошибка при получении документов:", e);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  // --- ЛОГИКА ЧАТА (Стриминг) ---
  const handleAsk = async () => {
    // ЗАЩИТА: если поле пустое ИЛИ уже идет стриминг — полностью блокируем повторный запуск
    if (!query.trim() || loading) return;

    setMessages(prev => [...prev, { role: 'user', text: query }]);
    const currentQuery = query;
    setQuery('');
    setLoading(true);
    setMessages(prev => [...prev, { role: 'bot', text: '' }]);

    try {
      const response = await fetch('http://localhost:8000/chat/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            query: currentQuery,
            active_docs: documents.filter(d => d.is_active ?? d.active).map(d => d.filename),
            categories: documents.filter(d => d.is_active ?? d.active).map(d => d.doc_type)
        }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setMessages(prev => {
          const newMsgs = [...prev];
          const lastIdx = newMsgs.length - 1;
          newMsgs[lastIdx] = {
          ...newMsgs[lastIdx],
            text: newMsgs[lastIdx].text + chunk
          };

          return newMsgs
        });
      }
    } catch (e) {
      console.error("Ошибка чата:", e);
    } finally {
      setLoading(false);
    }
  };

  // --- ЛОГИКА ЗАГРУЗКИ ---
  const onFileDrop = (files) => {
    if (files.length > 0) setUploadModal({ open: true, file: files[0] });
  };

  const submitFile = async () => {
    const formData = new FormData();
    formData.append('file', uploadModal.file);
    formData.append('file_type', docCategory);

    try {
      const res = await fetch('http://localhost:8000/documents/upload', {
        method: 'POST',
        body: formData, 
      });

      if (res.ok) {
        await fetchDocuments();
      }
    } catch (e) {
      console.error("Ошибка загрузки:", e);
    }
    setUploadModal({ open: false, file: null });
  };

  // --- 2. СИНХРОННОЕ ПЕРЕКЛЮЧЕНИЕ АКТИВНОСТИ (PATCH) ---
  const toggleDocument = async (id) => {
    try {
      const res = await fetch(`http://localhost:8000/documents/${id}/toggle`, {
        method: 'PATCH',
      });
      if (res.ok) {
        await fetchDocuments();
      }
    } catch (e) {
      console.error("Ошибка изменения статуса документа:", e);
    }
  };

  // --- 3. СИНХРОННОЕ УДАЛЕНИЕ ДОКУМЕНТА (DELETE) ---
  const deleteDocument = async (id) => {
    try {
      const res = await fetch(`http://localhost:8000/documents/${id}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        setDocuments(prev => prev.filter(d => d.id !== id));
      }
    } catch (e) {
      console.error("Ошибка удаления документа:", e);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex p-4 gap-4">
      {/* Модальное окно выбора категории */}
      {uploadModal.open && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-zinc-900 p-6 rounded-xl border border-zinc-700 w-full max-w-sm shadow-2xl">
            <h3 className="font-bold mb-1">Выберите категорию</h3>
            <p className="text-xs text-zinc-400 mb-4 truncate">{uploadModal.file.name}</p>
            
            <select 
              className="w-full bg-zinc-800 p-2 rounded mb-6 border border-zinc-700 text-white"
              value={docCategory}
              onChange={(e) => setDocCategory(e.target.value)}
            >
              <option value="other">Другое (Other)</option>
              <option value="legal">Юридические (Legal)</option>
              <option value="tech">Технические (Tech)</option>
              <option value="finance">Финансовые (Finance)</option>
              <option value="criminalist">Криминалистика (Criminalist)</option>
            </select>
            
            <div className="flex gap-2">
              <button onClick={() => setUploadModal({ open: false, file: null })} className="flex-1 p-2 text-zinc-400 hover:text-white">Отмена</button>
              <button onClick={submitFile} className="flex-1 p-2 bg-blue-600 hover:bg-blue-500 rounded text-white font-bold">Загрузить</button>
            </div>
          </div>
        </div>
      )}

      {/* Основная зона чата */}
      <div className="flex-1 flex flex-col gap-4 max-w-4xl mx-auto w-full">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`p-4 rounded-xl max-w-[80%] ${msg.role === 'user' ? 'bg-zinc-800 ml-auto' : 'bg-zinc-900 border border-zinc-800'}`}>
              {msg.text || <span className="animate-pulse">...</span>}
            </div>
          ))}
        </div>
        
        {/* Использование HTML-формы решает проблему Enter-дублирования */}
        <form 
          onSubmit={(e) => {
            e.preventDefault(); // Предотвращаем перезагрузку страницы браузером
            handleAsk();
          }}
          className="relative"
        >
          <input 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-700 p-4 pr-12 rounded-xl focus:outline-none focus:border-zinc-500 disabled:opacity-50"
            placeholder={loading ? "Нейросеть печатает..." : "Задай вопрос по документам..."}
            disabled={loading} // Блокируем инпут во время ответа, чтобы избежать спама
          />
          <button 
            type="submit" // Кнопка теперь отправляет форму
            disabled={loading} 
            className="absolute right-4 top-4 text-zinc-400 hover:text-white disabled:opacity-30 transition-opacity"
          >
            <Send size={20} />
          </button>
        </form>
      </div>

      {/* Боковая панель (Менеджер документов) */}
      <div className="w-80 bg-zinc-900 p-6 rounded-2xl border border-zinc-800 flex flex-col h-[calc(100vh-32px)]">
        <h3 className="text-sm font-bold text-zinc-400 uppercase mb-4">Document Manager</h3>
        
        <div 
          className="border-2 border-dashed border-zinc-700 rounded-xl p-6 text-center text-zinc-500 mb-6 cursor-pointer hover:border-zinc-500 transition-colors"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => { e.preventDefault(); onFileDrop(e.dataTransfer.files); }}
          onClick={() => fileInputRef.current.click()}
        >
          <Upload className="mx-auto mb-2" size={24} />
          <p className="text-xs">Перетащи или кликни</p>
        </div>
        <input type="file" ref={fileInputRef} className="hidden" multiple onChange={(e) => onFileDrop(e.target.files)} />

        {/* Список загруженных документов */}
        <div className="space-y-2 overflow-y-auto flex-1">
          {documents.map(doc => {
            const isActive = doc.is_active ?? doc.active ?? true;

            return (
              <div key={doc.id} className="flex items-center gap-3 p-2 hover:bg-zinc-800 rounded group">
                <button onClick={() => toggleDocument(doc.id)} className="text-zinc-500 hover:text-zinc-300">
                  {isActive ? <CheckSquare size={18} className="text-blue-500" /> : <Square size={18} />}
                </button>
                
                <div className="flex-1 min-w-0">
                  <p className={`text-sm truncate ${!isActive ? 'text-zinc-600 line-through' : ''}`}>
                    {doc.filename}
                  </p>
                  <p className="text-[10px] text-zinc-500 uppercase">
                    {doc.doc_type}
                  </p>
                </div>

                <button onClick={() => deleteDocument(doc.id)} className="opacity-0 group-hover:opacity-100 text-zinc-600 hover:text-red-400 transition-opacity">
                  <Trash2 size={16} />
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
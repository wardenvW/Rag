import React, { useState, useRef, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import { 
  Upload, 
  Send, 
  CheckSquare, 
  Square, 
  Trash2, 
  Terminal, 
  RefreshCw, 
  MessageSquare,
  ShieldCheck
} from 'lucide-react';

// ==========================================
// КОМПОНЕНТ-ЗАЩИТНИК (ProtectedRoute / Route Guard)
// ==========================================
// Он проверяет, авторизован ли админ. Если нет — жестко редиректит на главную.
function ProtectedRoute({ isAdmin, children }) {
  if (!isAdmin) {
    // Пользователь не админ? Отправляем его на главную страницу "/"
    return <Navigate to="/" replace />;
  }
  return children;
}

// ==========================================
// 1. СТРАНИЦА ЧАТА (Главная: доступна всем по "/")
// ==========================================
function ChatPage() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadModal, setUploadModal] = useState({ open: false, file: null });
  const [docCategory, setDocCategory] = useState('other'); 
  const fileInputRef = useRef(null);

  const fetchDocuments = async () => {
    try {
      const res = await fetch('http://localhost:8000/documents/');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) setDocuments(data);
        else if (data && Array.isArray(data.documents)) setDocuments(data.documents);
        else if (data && Array.isArray(data.items)) setDocuments(data.items);
      }
    } catch (e) { console.error(e); }
  };

  useEffect(() => { fetchDocuments(); }, []);

  const handleAsk = async () => {
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
          newMsgs[lastIdx] = { ...newMsgs[lastIdx], text: newMsgs[lastIdx].text + chunk };
          return newMsgs;
        });
      }
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  const onFileDrop = (files) => { if (files.length > 0) setUploadModal({ open: true, file: files[0] }); };
  
  const submitFile = async () => {
    const formData = new FormData();
    formData.append('file', uploadModal.file);
    formData.append('file_type', docCategory);
    try {
      const res = await fetch('http://localhost:8000/documents/upload', { method: 'POST', body: formData });
      if (res.ok) await fetchDocuments();
    } catch (e) { console.error(e); }
    setUploadModal({ open: false, file: null });
  };

  const toggleDocument = async (id) => {
    try {
      const res = await fetch(`http://localhost:8000/documents/${id}/toggle`, { method: 'PATCH' });
      if (res.ok) await fetchDocuments();
    } catch (e) { console.error(e); }
  };

  const deleteDocument = async (id) => {
    try {
      const res = await fetch(`http://localhost:8000/documents/${id}`, { method: 'DELETE' });
      if (res.ok) setDocuments(prev => prev.filter(d => d.id !== id));
    } catch (e) { console.error(e); }
  };

  return (
    <div className="flex-1 flex gap-4 min-h-0">
      {uploadModal.open && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-zinc-900 p-6 rounded-xl border border-zinc-700 w-full max-w-sm shadow-2xl">
            <h3 className="font-bold mb-1">Выберите категорию</h3>
            <p className="text-xs text-zinc-400 mb-4 truncate">{uploadModal.file.name}</p>
            <select className="w-full bg-zinc-800 p-2 rounded mb-6 border border-zinc-700 text-white" value={docCategory} onChange={(e) => setDocCategory(e.target.value)}>
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

      <div className="flex-1 flex flex-col gap-4 max-w-4xl mx-auto w-full h-[calc(100vh-100px)]">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`p-4 rounded-xl max-w-[80%] whitespace-pre-wrap ${msg.role === 'user' ? 'bg-zinc-800 ml-auto' : 'bg-zinc-900 border border-zinc-800'}`}>
              {msg.text || <span className="animate-pulse">...</span>}
            </div>
          ))}
        </div>
        <form onSubmit={(e) => { e.preventDefault(); handleAsk(); }} className="relative">
          <input value={query} onChange={(e) => setQuery(e.target.value)} className="w-full bg-zinc-900 border border-zinc-700 p-4 pr-12 rounded-xl focus:outline-none focus:border-zinc-500 disabled:opacity-50" placeholder={loading ? "Нейросеть печатает..." : "Задай вопрос по документам..."} disabled={loading} />
          <button type="submit" disabled={loading} className="absolute right-4 top-4 text-zinc-400 hover:text-white disabled:opacity-30 transition-opacity">
            <Send size={20} />
          </button>
        </form>
      </div>

      <div className="w-80 bg-zinc-900 p-6 rounded-2xl border border-zinc-800 flex flex-col h-[calc(100vh-100px)]">
        <h3 className="text-sm font-bold text-zinc-400 uppercase mb-4">Document Manager</h3>
        <div className="border-2 border-dashed border-zinc-700 rounded-xl p-6 text-center text-zinc-500 mb-6 cursor-pointer hover:border-zinc-500 transition-colors" onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); onFileDrop(e.dataTransfer.files); }} onClick={() => fileInputRef.current.click()}>
          <Upload className="mx-auto mb-2" size={24} />
          <p className="text-xs">Перетащи или кликни</p>
        </div>
        <input type="file" ref={fileInputRef} className="hidden" multiple onChange={(e) => onFileDrop(e.target.files)} />
        <div className="space-y-2 overflow-y-auto flex-1 min-h-0">
          {documents.map(doc => {
            const isActive = doc.is_active ?? doc.active ?? true;
            return (
              <div key={doc.id} className="flex items-center gap-3 p-2 hover:bg-zinc-800 rounded group">
                <button onClick={() => toggleDocument(doc.id)} className="text-zinc-500 hover:text-zinc-300">
                  {isActive ? <CheckSquare size={18} className="text-blue-500" /> : <Square size={18} />}
                </button>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm truncate ${!isActive ? 'text-zinc-600 line-through' : ''}`}>{doc.filename}</p>
                  <p className="text-[10px] text-zinc-500 uppercase">{doc.doc_type}</p>
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

// ==========================================
// 2. СТРАНИЦА АДМИНКИ (Доступна только по "/admin")
// ==========================================
function AdminLogsPage() {
  const [logs, setLogs] = useState('');
  const [status, setStatus] = useState('connecting'); 
  const logEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  const startLogStream = async () => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    abortControllerRef.current = new AbortController();
    setStatus('connecting');
    try {
      const response = await fetch('http://localhost:8000/admin/', { signal: abortControllerRef.current.signal });
      if (!response.body) { setStatus('error'); return; }
      setStatus('active');
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setLogs((prev) => prev + chunk);
      }
    } catch (e) {
      if (e.name !== 'AbortError') { setStatus('error'); }
    }
  };

  useEffect(() => {
    startLogStream();
    return () => { if (abortControllerRef.current) abortControllerRef.current.abort(); };
  }, []);

  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [logs]);

  return (
    <div className="flex-1 bg-zinc-950 flex flex-col font-mono selection:bg-emerald-500/30 h-[calc(100vh-100px)]">
      <div className="flex items-center justify-between border-b border-zinc-900 pb-4 mb-4">
        <div className="flex items-center gap-3">
          <Terminal className={`w-5 h-5 ${status === 'active' ? 'text-emerald-400 animate-pulse' : 'text-zinc-500'}`} />
          <div>
            <h1 className="text-sm font-bold uppercase tracking-wider">System Live Logs</h1>
            <p className="text-[10px] text-zinc-500 mt-0.5">
              Статус соединения:{' '}
              <span className={`font-bold ${status === 'active' ? 'text-emerald-400' : status === 'connecting' ? 'text-yellow-500' : 'text-red-500'}`}>
                {status === 'active' ? 'ПОДКЛЮЧЕНО' : status === 'connecting' ? 'СОЕДИНЕНИЕ...' : 'ОШИБКА'}
              </span>
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={startLogStream} className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors">
            <RefreshCw size={14} />
            <span>Переподключить</span>
          </button>
          <button onClick={() => setLogs('')} className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs hover:bg-zinc-800 text-zinc-400 hover:text-red-400 transition-colors">
            <Trash2 size={14} />
            <span>Очистить экран</span>
          </button>
        </div>
      </div>
      <div className="flex-1 bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-4 overflow-y-auto shadow-2xl flex flex-col min-h-0">
        <div className="flex-1 overflow-y-auto text-xs text-emerald-500/90 leading-relaxed whitespace-pre-wrap">
          {!logs && status === 'active' && <div className="text-zinc-700 italic">Ожидание новых событий от FastAPI бэкенда...</div>}
          {logs}
          <div ref={logEndRef} />
        </div>
      </div>
    </div>
  );
}

// ==========================================
// 3. КОРНЕВОЙ КОМПОНЕНТ С АВТОРИЗАЦИЕЙ
// ==========================================
export default function App() {
  // Локальный тумблер для теста (заглушка авторизации). 
  // Когда сделаешь бэкенд, будешь сетить сюда true после успешного login.
  const [isAdmin, setIsAdmin] = useState(false);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col p-4 gap-4 font-sans">
        
        {/* Навбар управления */}
        <div className="flex justify-between items-center border-b border-zinc-800 pb-2">
          <div className="flex gap-2">
            <Link 
              to="/" 
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors text-zinc-400 hover:text-zinc-200"
            >
              <MessageSquare size={16} />
              Панель Чата RAG
            </Link>
            
            {/* Ссылка на логи видна в навбаре ТОЛЬКО если вошел админ */}
            {isAdmin && (
              <Link 
                to="/admin" 
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors text-zinc-400 hover:text-zinc-200"
              >
                <Terminal size={16} />
                Живые Логи Сервера
              </Link>
            )}
          </div>

          {/* Переключатель-заглушка для ручного тестирования прямо на экране */}
          <button
            onClick={() => setIsAdmin(!isAdmin)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${
              isAdmin 
                ? 'bg-emerald-950/40 border-emerald-500 text-emerald-400' 
                : 'bg-zinc-900 border-zinc-800 text-zinc-500'
            }`}
          >
            <ShieldCheck size={14} />
            <span>{isAdmin ? "Режим: Администратор" : "Войти как Админ (Заглушка)"}</span>
          </button>
        </div>

        {/* Роутинг приложений */}
        <Routes>
          <Route path="/" element={<ChatPage />} />
          
          {/* Роут логов обернут в ProtectedRoute. Без isAdmin сюда невозможно попасть */}
          <Route 
            path="/admin" 
            element={
              <ProtectedRoute isAdmin={isAdmin}>
                <AdminLogsPage />
              </ProtectedRoute>
            } 
          />
        </Routes>

      </div>
    </BrowserRouter>
  );
}
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Mic, Bot, Loader2, LogOut, Settings } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api';

export default function StudentDashboard({ user, onLogout }) {
  const [messages, setMessages] = useState([{ role: 'bot', text: `Welcome ${user.name}! Click the mic or type to speak to your AI Assistant.` }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  
  const [a11y, setA11y] = useState({ highContrast: false, largeText: false, showMenu: false });
  
  const scrollRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => { scrollRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await axios.post(`${API_BASE_URL}/chat/ask`, { session_id: "student-session", query_text: input });
      setMessages(prev => [...prev, { role: 'bot', text: res.data.response_text }]);
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: "Service unavailable." }]);
    } finally { setIsLoading(false); }
  };

  const toggleRecording = async () => {
    if (isRecording) {
      if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) audioChunksRef.current.push(e.data); };
        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: mediaRecorder.mimeType });
          if (audioBlob.size > 1000) sendVoiceMessage(audioBlob);
          else alert("Recording too short.");
          stream.getTracks().forEach(t => t.stop());
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (err) { alert("Microphone access denied."); }
    }
  };

  const sendVoiceMessage = async (audioBlob) => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.webm');

    try {
      const res = await axios.post(`${API_BASE_URL}/speech/voice-query`, { headers: { 'Content-Type': 'multipart/form-data' } });
      setMessages(prev => [...prev, { role: 'user', text: res.data.user_text }, { role: 'bot', text: res.data.bot_text }]);
      if (res.data.audio_base64) {
        new Audio("data:audio/mp3;base64," + res.data.audio_base64).play();
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: "Voice processing failed." }]);
    } finally { setIsLoading(false); }
  };

  const theme = {
    bg: a11y.highContrast ? 'bg-black' : 'bg-slate-50',
    header: a11y.highContrast ? 'bg-yellow-400 text-black border-b-4 border-white' : 'bg-blue-800 text-white shadow-2xl',
    botBubble: a11y.highContrast ? 'bg-black text-yellow-400 border-2 border-yellow-400' : 'bg-white text-slate-800 border',
    userBubble: a11y.highContrast ? 'bg-yellow-400 text-black font-bold' : 'bg-blue-700 text-white',
    textSize: a11y.largeText ? 'text-xl leading-loose' : 'text-base leading-relaxed',
    inputBox: a11y.highContrast ? 'bg-black text-yellow-400 border-yellow-400' : 'bg-white border-slate-200'
  };

  return (
    <div className={`flex flex-col h-screen ${theme.bg}`}>
      <header className={`${theme.header} p-5 flex justify-between items-center z-10`}>
        <div className="flex items-center space-x-3"><Bot size={32} /> <span className="font-black text-xl uppercase">Student Hub</span></div>
        <div className="flex items-center space-x-4 relative">
          <button onClick={() => setA11y({...a11y, showMenu: !a11y.showMenu})} className="p-2 hover:bg-black/10 rounded-full"><Settings size={24}/></button>
          {a11y.showMenu && (
            <div className="absolute top-14 right-12 bg-white text-slate-800 w-64 rounded-2xl shadow-2xl p-4 z-50">
              <h4 className="font-black text-sm uppercase text-slate-400 mb-4 border-b pb-2">Accessibility</h4>
              <div className="space-y-4">
                <label className="flex items-center justify-between"><span className="font-bold">High Contrast</span><input type="checkbox" checked={a11y.highContrast} onChange={() => setA11y({...a11y, highContrast: !a11y.highContrast})} className="w-5 h-5 accent-blue-600" /></label>
                <label className="flex items-center justify-between"><span className="font-bold">Large Text</span><input type="checkbox" checked={a11y.largeText} onChange={() => setA11y({...a11y, largeText: !a11y.largeText})} className="w-5 h-5 accent-blue-600" /></label>
              </div>
            </div>
          )}
          <button onClick={onLogout} className="p-2 hover:bg-black/10 rounded-full"><LogOut size={24}/></button>
        </div>
      </header>
      <main className="flex-1 overflow-y-auto p-6 space-y-6" aria-live="polite">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-5 rounded-3xl shadow-sm ${theme.textSize} ${m.role === 'user' ? `${theme.userBubble} rounded-tr-none` : `${theme.botBubble} rounded-tl-none`}`}>{m.text}</div>
          </div>
        ))}
        {isLoading && <div className={`flex items-center space-x-2 font-bold ${a11y.highContrast ? 'text-yellow-400' : 'text-blue-800'} animate-pulse`}> <Loader2 className="animate-spin" size={18}/><span>{isRecording ? "" : "AI is processing..."}</span></div>}
        <div ref={scrollRef} />
      </main>
      <footer className={`p-5 border-t flex space-x-3 items-center relative ${a11y.highContrast ? 'bg-black border-yellow-400' : 'bg-white'}`}>
        <div className="relative flex flex-col items-center">
          {isRecording && <div className="absolute -top-8 bg-red-500 text-white text-[10px] font-bold px-3 py-1 rounded-full animate-bounce">Recording...</div>}
          <button onClick={toggleRecording} className={`p-4 rounded-full shadow-md ${isRecording ? 'bg-red-500 text-white animate-pulse' : a11y.highContrast ? 'bg-yellow-400 text-black' : 'bg-slate-100 text-slate-500 hover:bg-blue-100'}`}><Mic size={24}/></button>
        </div>
        <input className={`flex-1 border-2 rounded-full px-6 py-4 outline-none shadow-sm font-medium ${theme.textSize} ${theme.inputBox}`} value={input} onChange={e => setInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && handleSend()} placeholder={isRecording ? "🔴 Listening... Click mic to stop." : "Type your query here..."} disabled={isRecording || isLoading} />
        <button onClick={handleSend} disabled={isRecording || isLoading} className={`p-4 rounded-full shadow-lg transition-all active:scale-90 disabled:opacity-50 ${a11y.highContrast ? 'bg-yellow-400 text-black' : 'bg-blue-800 text-white hover:bg-blue-900'}`}><Send size={24} /></button>
      </footer>
    </div>
  );
}
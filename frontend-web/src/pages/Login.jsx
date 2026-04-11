import React, { useState } from 'react';
import axios from 'axios';
import { Loader2, AlertCircle } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api';

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, { email, password });
      onLogin(response.data); 
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid Credentials. Check your connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 px-4">
      <div className="max-w-md w-full bg-white rounded-[2.5rem] shadow-2xl p-10 border-t-[12px] border-blue-700">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-black text-blue-900 tracking-tighter uppercase">SRM Portal</h2>
          <p className="text-slate-500 font-bold uppercase text-[10px] tracking-[0.3em] mt-2 italic">AI Academic Assistant</p>
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 text-sm flex items-center rounded-xl">
            <AlertCircle size={20} className="mr-3" /> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-black text-slate-400 uppercase ml-1">University Email</label>
            <input 
              type="email" required className="w-full px-6 py-4 bg-slate-50 border-2 border-slate-100 rounded-2xl focus:border-blue-700 outline-none transition-all font-medium"
              value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. shubh@srmist.edu.in"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-black text-slate-400 uppercase ml-1">Password</label>
            <input 
              type="password" required className="w-full px-6 py-4 bg-slate-50 border-2 border-slate-100 rounded-2xl focus:border-blue-700 outline-none transition-all font-medium"
              value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          <button 
            type="submit" disabled={loading}
            className="w-full py-5 bg-blue-700 text-white rounded-2xl font-black text-lg shadow-xl hover:bg-blue-800 transition-all active:scale-95 disabled:bg-slate-300 uppercase tracking-widest"
          >
            {loading ? <Loader2 className="animate-spin mx-auto" /> : "Access System"}
          </button>
        </form>
      </div>
    </div>
  );
}
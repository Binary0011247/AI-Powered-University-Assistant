import React, { useState } from 'react';
import axios from 'axios';
import { BookOpen, LogOut, Upload, CheckCircle, Loader2 } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api';

export default function FacultyDashboard({ user, onLogout }) {
  const [status, setStatus] = useState('');
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
      setStatus('');
    } else {
      alert("Please select a valid PDF file.");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setStatus(`Processing document for ${user.department || 'your department'}...`);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('faculty_email', user.email);
    formData.append('department', user.department || "General"); 

    try {
      const res = await axios.post(`${API_BASE_URL}/ingest/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStatus(`✅ Success! Database ID: ${res.data.database_id}. ${res.data.chunks_added} knowledge points learned.`);
      setFile(null); // Reset the file input
    } catch (err) {
      console.error(err.response?.data);
      setStatus('❌ Upload failed. The file may be corrupt or the server is offline.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-emerald-800 text-white p-5 flex justify-between items-center shadow-lg">
        <div className="flex items-center space-x-3">
          <BookOpen size={32} /> 
          <span className="font-black text-xl uppercase tracking-tighter">Faculty Portal</span>
        </div>
        <button onClick={onLogout} className="bg-emerald-900 px-5 py-2 rounded-xl flex items-center space-x-2 font-bold hover:bg-red-900 transition-all shadow-md">
          <LogOut size={20}/>
          <span>Logout</span>
        </button>
      </header>

      <div className="p-10 max-w-5xl mx-auto">
        <div className="bg-white rounded-[3rem] shadow-2xl p-16 border-b-[12px] border-emerald-600">
          <h2 className="text-4xl font-black text-slate-900 mb-2 italic">Knowledge Ingestion</h2>
          <p className="text-slate-500 mb-12 font-bold uppercase text-xs tracking-widest">
            Upload University PDFs to update the AI Knowledge Base
          </p>
          
          <div className="border-4 border-dashed border-slate-200 rounded-[2.5rem] p-24 text-center bg-slate-50 hover:border-emerald-300 transition-all">
            <input 
              type="file" 
              accept=".pdf" 
              onChange={handleFileChange} 
              className="hidden" 
              id="pdf-upload" 
            />
            <label htmlFor="pdf-upload" className="cursor-pointer block w-full h-full">
              <Upload className="mx-auto text-emerald-200 mb-8" size={80} />
              <p className="text-slate-600 font-bold mb-4">
                {file ? file.name : "Click to select a University PDF"}
              </p>
              <p className="text-xs text-slate-400">
                (Syllabus, Timetables, Policy Documents)
              </p>
            </label>
            
            <button 
              onClick={handleUpload}
              disabled={uploading || !file}
              className={`mt-8 px-12 py-5 rounded-3xl font-black text-lg text-white shadow-2xl transition-all active:scale-95 ${
                uploading || !file ? 'bg-slate-400 cursor-not-allowed' : 'bg-emerald-600 hover:bg-emerald-700'
              }`}
            >
              {uploading ? 
                <span className="flex items-center"><Loader2 className="animate-spin mr-3" /> Generating AI Vectors...</span> : 
                'Upload & Train AI'
              }
            </button>
          </div>
          
          {status && (
            <div className={`mt-10 p-6 rounded-3xl border-l-8 flex items-center font-black shadow-sm italic ${
              status.includes('Success') 
                ? 'bg-emerald-50 text-emerald-800 border-emerald-500 animate-bounce' 
                : 'bg-red-50 text-red-800 border-red-500'
            }`}>
              <CheckCircle className="mr-3" /> {status}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
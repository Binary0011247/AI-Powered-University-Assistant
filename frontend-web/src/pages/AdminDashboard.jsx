import React, { useState, useEffect } from 'react';
import axios from 'axios';
import * as XLSX from 'xlsx'; // Needed for Excel file parsing
import { 
  Users, LogOut, Upload, Shield, Download, ClipboardCheck, X, 
  User as UserIcon, Loader2, Briefcase 
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api';

export default function AdminDashboard({ user, onLogout }) {
  const [users, setUsers] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [previewData, setPreviewData] = useState(null); 
  const [isProcessing, setIsProcessing] = useState(false);
  
  // State for adding a single user
  const [newEmail, setNewEmail] = useState('');
  const [newRole, setNewRole] = useState('student');
  const [newDept, setNewDept] = useState('Computer Science');
  
  // State for credentials generated after enrollment
  const [generatedCreds, setGeneratedCreds] = useState(null);

  // Fetch all users from the backend when the component loads
  useEffect(() => { fetchUsers(); }, []);

  const fetchUsers = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/admin/users`);
      setUsers(res.data);
    } catch (error) {
      console.error("Failed to fetch users:", error);
      // Optional: Set an error state to display a message to the admin
    }
  };

  // --- HANDLERS FOR SINGLE USER ADDITION ---
  const handleAddUser = async (e) => {
    e.preventDefault(); // Prevent default form submission
    try {
      const res = await axios.post(`${API_BASE_URL}/admin/users/single`, { 
        email: newEmail, 
        role: newRole,
        department: newDept 
      });
      // Store generated credentials to allow download
      setGeneratedCreds([{ email: res.data.email, password: res.data.password, role: res.data.role }]);
      setShowAddModal(false); // Close the modal
      setNewEmail(''); // Clear form fields
      setNewDept('Computer Science'); // Reset department
      fetchUsers(); // Refresh the user list
    } catch (err) { 
      alert(err.response?.data?.detail || "Error adding user. Check for duplicates."); 
    }
  };

  // --- HANDLERS FOR BULK UPLOAD WITH PREVIEW ---
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (ev) => {
      let parsed = [];
      try {
        if (file.name.endsWith('.csv')) {
          const lines = ev.target.result.split('\n');
          parsed = lines.slice(1).filter(l => l.trim()).map(l => {
            const [email, role, dept] = l.split(',');
            return { email: email.trim(), role: role.trim().toLowerCase(), department: (dept || "CSE").trim() };
          });
        } else { // Handle .xlsx or .xls files
          const data = new Uint8Array(ev.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          const worksheet = workbook.Sheets[workbook.SheetNames[0]]; // Get first sheet
          const json = XLSX.utils.sheet_to_json(worksheet);

          // Map Excel rows to the expected format for the API
          parsed = json.map(row => ({
            email: row.email?.toString().trim(),
            role: row.role?.toString().toLowerCase().trim(),
            department: (row.department || "CSE").toString().trim()
          }));
        }
        setPreviewData(parsed); // Open the preview modal with the parsed data
      } catch (err) { 
        alert("File Format Error: Ensure columns are 'email', 'role', 'department' in the first row."); 
        console.error("File parsing error:", err);
      }
    };

    // Read file based on its type
    if (file.name.endsWith('.csv')) {
      reader.readAsText(file);
    } else {
      reader.readAsArrayBuffer(file);
    }
  };

  const handleConfirmUpload = async () => {
    setIsProcessing(true); // Show loading spinner
    try {
      const res = await axios.post(`${API_BASE_URL}/admin/users/bulk`, { users: previewData });
      setGeneratedCreds(res.data.credentials); // Store credentials for download
      setPreviewData(null); // Close the preview modal
      fetchUsers(); // Refresh the user list in the background
    } catch (err) { 
      alert(err.response?.data?.detail || "Bulk upload failed. Check for duplicate emails or server issues."); 
      console.error("Bulk upload error:", err);
    } finally { 
      setIsProcessing(false); 
    }
  };

  // --- CREDENTIAL DOWNLOAD HANDLER ---
  const downloadCreds = () => {
    if (!generatedCreds) return;
    const csvData = "Email,Temporary Password,Role\n" + generatedCreds.map(c => `${c.email},${c.password},${c.role}`).join("\n");
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'new_user_credentials.csv'; // Filename for download
    document.body.appendChild(a); // Temporarily add to DOM to trigger download
    a.click(); // Trigger click
    window.URL.revokeObjectURL(url); // Clean up
    a.remove(); // Clean up
    setGeneratedCreds(null); // Clear credentials from state for security
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-slate-900 text-white p-5 flex justify-between items-center shadow-2xl">
        <div className="flex items-center space-x-3">
          <Shield size={32} className="text-red-500" /> 
          <span className="font-black text-xl uppercase tracking-tighter">Admin Portal</span>
        </div>
        <button onClick={onLogout} className="bg-slate-800 px-6 py-3 rounded-2xl font-black hover:bg-red-700 transition-all flex items-center space-x-2 shadow-lg">
          <LogOut size={20}/>
          <span>Logout</span>
        </button>
      </header>
      
      <div className="p-10">
        {/* Admin Header with Buttons */}
        <div className="flex justify-between items-center mb-12">
          <h2 className="text-5xl font-black text-slate-800 tracking-tighter flex items-center">
            <Users size={48} className="mr-6 text-blue-700"/> User Access
          </h2>
          <div className="flex space-x-4">
            <label className="bg-indigo-600 text-white px-8 py-4 rounded-[1.5rem] font-black shadow-2xl hover:bg-indigo-700 cursor-pointer flex items-center transition-all active:scale-95">
              <Upload className="mr-3" size={24}/> Bulk CSV / Excel
              <input type="file" accept=".csv, .xlsx, .xls" className="hidden" onChange={handleFileSelect} />
            </label>
            <button onClick={() => setShowAddModal(true)} className="bg-blue-700 text-white px-8 py-4 rounded-[1.5rem] font-black shadow-2xl hover:bg-blue-800 transition-all active:scale-95">
              + New User
            </button>
          </div>
        </div>

        {/* Credentials Download Alert */}
        {generatedCreds && (
          <div className="mb-12 bg-emerald-50 border-l-[12px] border-emerald-500 p-8 rounded-[2.5rem] shadow-2xl flex justify-between items-center animate-bounce">
             <div>
              <p className="font-black text-emerald-900 text-xl tracking-tight">✅ {generatedCreds.length} User(s) Enrolled</p>
              <p className="text-emerald-800 font-bold italic mt-1 uppercase text-xs tracking-widest">Download credentials immediately. These passwords cannot be retrieved later.</p>
            </div>
            <button onClick={downloadCreds} className="bg-emerald-600 text-white px-10 py-4 rounded-2xl font-black shadow-xl hover:bg-emerald-700 flex items-center">
              <Download className="mr-2" /> Download Passwords
            </button>
          </div>
        )}

        {/* --- USERS TABLE --- */}
        <div className="bg-white rounded-[3rem] shadow-2xl overflow-hidden border border-slate-100">
          <table className="w-full text-left">
            <thead className="bg-slate-50 border-b">
              <tr>
                <th className="p-8 font-black text-slate-400 uppercase text-xs tracking-widest">Email</th>
                <th className="p-8 font-black text-slate-400 uppercase text-xs tracking-widest">Unit</th>
                <th className="p-8 font-black text-slate-400 uppercase text-xs tracking-widest">Role</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {users.map((u, i) => (
                <tr key={i} className="hover:bg-blue-50/50">
                  <td className="p-8 font-bold text-slate-800">{u.email}</td>
                  <td className="p-8 text-slate-500 uppercase font-bold text-sm tracking-widest">{u.dept || "GENERAL"}</td>
                  <td className="p-8">
                    <span className={`px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-widest ${
                      u.role === 'admin' ? 'bg-red-100 text-red-700' : 
                      u.role === 'faculty' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'
                    }`}>{u.role}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* --- PREVIEW MODAL (for Bulk Upload) --- */}
        {previewData && (
          <div className="fixed inset-0 bg-slate-900/90 backdrop-blur-md flex items-center justify-center z-50 p-6">
            <div className="bg-white rounded-[3.5rem] shadow-2xl w-full max-w-4xl max-h-[85vh] flex flex-col border-t-[16px] border-indigo-600">
              <div className="p-10 border-b flex justify-between items-center">
                <h3 className="text-4xl font-black text-slate-800 tracking-tighter">Data Preview</h3>
                <button onClick={() => setPreviewData(null)} className="p-3 bg-slate-100 rounded-full hover:bg-red-100 transition-all"><X /></button>
              </div>
              
              <div className="flex-1 overflow-y-auto p-10 bg-slate-50/50">
                <table className="w-full text-left">
                  <thead className="bg-white sticky top-0 shadow-sm">
                    <tr>
                      <th className="p-5 font-black text-xs uppercase text-slate-400">Email</th>
                      <th className="p-5 font-black text-xs uppercase text-slate-400">Role</th>
                      <th className="p-5 font-black text-xs uppercase text-slate-400">Dept</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {previewData.map((row, i) => (
                      <tr key={i} className="bg-white">
                        <td className="p-5 font-bold text-slate-700">{row.email}</td>
                        <td className="p-5"><span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-[10px] font-black uppercase tracking-widest">{row.role}</span></td>
                        <td className="p-5 text-slate-500 font-medium">{row.department}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="p-10 bg-slate-50 rounded-b-[3.5rem] flex justify-end space-x-6">
                <button onClick={() => setPreviewData(null)} className="px-10 py-5 text-slate-400 font-black uppercase text-sm">Discard</button>
                <button onClick={handleConfirmUpload} disabled={isProcessing} className="px-12 py-5 bg-indigo-600 text-white font-black rounded-3xl shadow-2xl hover:bg-indigo-700 flex items-center transition-all disabled:bg-slate-300">
                  {isProcessing ? <Loader2 className="animate-spin mr-3"/> : <ClipboardCheck className="mr-3" />} Finalize Enrollment
                </button>
              </div>
            </div>
          </div>
        )}

        {/* --- ADD SINGLE USER MODAL --- */}
        {showAddModal && (
          <div className="fixed inset-0 bg-slate-900/90 backdrop-blur-md flex items-center justify-center z-50 p-6">
            <div className="bg-white p-12 rounded-[3.5rem] shadow-2xl w-full max-w-md border-t-[16px] border-blue-700">
              <h3 className="text-3xl font-black text-slate-800 mb-8 flex items-center tracking-tighter"><UserIcon className="mr-3 text-blue-700" size={36} /> Grant Access</h3>
              <form onSubmit={handleAddUser} className="space-y-6">
                <div>
                  <label className="block text-xs font-black text-slate-400 uppercase mb-2 ml-1">University Email</label>
                  <input type="email" required className="w-full border-2 border-slate-100 rounded-2xl p-5 focus:border-blue-700 outline-none font-medium" value={newEmail} onChange={e => setNewEmail(e.target.value)} />
                </div>
                <div>
                  <label className="block text-xs font-black text-slate-400 uppercase mb-2 ml-1">Department / Division</label>
                  <input type="text" required className="w-full border-2 border-slate-100 rounded-2xl p-5 focus:border-blue-700 outline-none font-medium" value={newDept} onChange={e => setNewDept(e.target.value)} />
                </div>
                <div>
                  <label className="block text-xs font-black text-slate-400 uppercase mb-2 ml-1">Role Allocation</label>
                  <select className="w-full border-2 border-slate-100 rounded-2xl p-5 focus:border-blue-700 outline-none font-black" value={newRole} onChange={e => setNewRole(e.target.value)}>
                    <option value="student">STUDENT ACCESS</option>
                    <option value="faculty">FACULTY ACCESS</option>
                    <option value="admin">ADMIN ACCESS</option>
                  </select>
                </div>
                <div className="flex space-x-4 pt-8">
                  <button type="button" onClick={() => setShowAddModal(false)} className="flex-1 px-8 py-5 text-slate-400 font-bold hover:bg-slate-50 rounded-3xl transition-all">Cancel</button>
                  <button type="submit" className="flex-1 px-8 py-5 bg-blue-700 text-white font-black rounded-3xl hover:bg-blue-800 shadow-2xl transition-all active:scale-95">Enroll Now</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
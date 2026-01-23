
import React, { useState, useEffect } from 'react';
import api from '../lib/api';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { User, Trash2, ArrowLeft } from 'lucide-react';

const Profile = () => {
    const navigate = useNavigate();
    const userId = localStorage.getItem("user_id");

    const [profile, setProfile] = useState({ username: '', full_name: '' });
    const [memories, setMemories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [msg, setMsg] = useState('');

    useEffect(() => {
        if (!userId) navigate("/auth");
        else loadData();
    }, [userId]);

    const loadData = async () => {
        try {
            const [profRes, memRes] = await Promise.all([
                api.get(`/me/${userId}`),
                api.get(`/memories/${userId}`)
            ]);
            setProfile(profRes.data);
            setMemories(memRes.data);
        } catch (err) {
            console.error("Failed to load profile", err);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateProfile = async () => {
        try {
            await api.put(`/me/${userId}`, { full_name: profile.full_name });
            setMsg("Profile updated successfully!");
            setTimeout(() => setMsg(''), 3000);
        } catch (err) {
            setMsg("Failed to update profile.");
        }
    };

    const handleDeleteMemory = async (id) => {
        if (!window.confirm("Forget this memory?")) return;
        try {
            await api.delete(`/memories/${id}`);
            setMemories(memories.filter(m => m.id !== id));
        } catch (err) {
            console.error("Failed to delete memory", err);
        }
    };

    return (
        <div style={{ display: 'flex', width: '100%', height: '100vh' }}>
            <Sidebar userId={userId} onNewChat={() => navigate("/chat")} />

            <div className="main-content" style={{ padding: '40px', overflowY: 'auto' }}>
                <div style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>

                    <button onClick={() => navigate("/chat")} style={{
                        background: 'none', border: 'none', color: '#5f6368',
                        cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px',
                        marginBottom: '20px', fontSize: '14px'
                    }}>
                        <ArrowLeft size={16} /> Back to Chat
                    </button>

                    <h1 style={{ fontSize: '28px', marginBottom: '30px' }}>Settings & Memories</h1>

                    {/* Profile Section */}
                    <div style={{ background: 'white', padding: '30px', borderRadius: '12px', border: '1px solid #dfe1e5', marginBottom: '30px' }}>
                        <h2 style={{ fontSize: '20px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <User size={20} /> My Profile
                        </h2>

                        <div className="form-group">
                            <label>Username</label>
                            <input value={profile.username} disabled style={{ background: '#f1f3f4', cursor: 'not-allowed' }} />
                        </div>

                        <div className="form-group">
                            <label>Full Name</label>
                            <input
                                value={profile.full_name}
                                onChange={e => setProfile({ ...profile, full_name: e.target.value })}
                                placeholder="How should I call you?"
                            />
                        </div>

                        <button onClick={handleUpdateProfile} className="auth-submit" style={{ width: 'auto', padding: '10px 24px' }}>
                            Save Changes
                        </button>
                        {msg && <span style={{ marginLeft: '15px', color: '#137333', fontSize: '14px' }}>{msg}</span>}
                    </div>

                    {/* Memories Section */}
                    <div style={{ background: 'white', padding: '30px', borderRadius: '12px', border: '1px solid #dfe1e5' }}>
                        <h2 style={{ fontSize: '20px', marginBottom: '20px' }}>🧠 Long-term Memories</h2>
                        <p style={{ color: '#5f6368', fontSize: '14px', marginBottom: '20px' }}>
                            These are things I have learned about you from our conversations.
                        </p>

                        {memories.length === 0 ? (
                            <p style={{ color: '#9aa0a6', fontStyle: 'italic' }}>No memories yet. Chat with me to form memories!</p>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                {memories.map(mem => (
                                    <div key={mem.id} style={{
                                        padding: '12px 16px', background: '#f8f9fa', borderRadius: '8px',
                                        display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                                    }}>
                                        <span style={{ fontSize: '15px', color: '#3c4043' }}>{mem.content}</span>
                                        <button onClick={() => handleDeleteMemory(mem.id)} style={{ border: 'none', background: 'transparent', color: '#d93025', cursor: 'pointer' }}>
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                </div>
            </div>
        </div>
    );
};

export default Profile;

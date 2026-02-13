import React, { useEffect, useState } from 'react';
import api from '../lib/api';
import { supabase } from '../lib/supabaseClient';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Plus, LogOut, Trash2, User, Bell } from 'lucide-react';

const Sidebar = ({ userId, currentSessionId, onSelectSession, onNewChat, isOpen, onClose }) => {
    const [sessions, setSessions] = useState([]);
    const navigate = useNavigate();
    const userName = localStorage.getItem("username") || "User";

    const loadSessions = async () => {
        try {
            const res = await api.get(`/sessions/${userId}`);
            setSessions(res.data);
        } catch (err) {
            console.error("Failed to load sessions", err);
        }
    };

    useEffect(() => {
        if (userId) loadSessions();
    }, [userId, currentSessionId]); // Reload when session changes (e.g. new title)

    const handleDelete = async (e, sessionId) => {
        e.stopPropagation();
        if (!window.confirm("Delete this chat?")) return;
        try {
            await api.delete(`/sessions/${sessionId}`);
            loadSessions();
            if (currentSessionId === sessionId) onNewChat();
        } catch (err) {
            console.error("Failed to delete", err);
        }
    };

    const handleLogout = async () => {
        await supabase.auth.signOut();
        localStorage.removeItem("user_id");
        localStorage.removeItem("username");
        navigate("/auth");
    };

    return (
        <>
            {/* Mobile Overlay */}
            {isOpen && <div className="sidebar-overlay" onClick={onClose} />}

            <div className={`sidebar ${isOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <span>RepliMate 🧠</span>
                    {/* Close button for mobile */}
                    <div className="mobile-close-btn" onClick={onClose} style={{ marginLeft: 'auto', cursor: 'pointer' }}>
                        &times;
                    </div>
                </div>

                <div className="new-chat-btn" onClick={() => { onNewChat(); onClose(); }}>
                    <Plus size={18} />
                    <span>New Chat</span>
                </div>

                <div className="history-list">
                    {sessions.map(sess => (
                        <div
                            key={sess.id}
                            className={`history-item ${currentSessionId === sess.id ? 'active' : ''}`}
                            onClick={() => { onSelectSession(sess.id); onClose(); }}
                        >
                            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>{sess.title}</span>
                            <Trash2
                                className="delete-icon"
                                size={14}
                                onClick={(e) => handleDelete(e, sess.id)}
                            />
                        </div>
                    ))}
                </div>

                <div className="sidebar-footer">
                    <div className="profile-btn" onClick={() => navigate("/reminders")}>
                        <Bell size={16} />
                        Reminders
                    </div>
                    <div className="profile-btn" onClick={() => navigate("/profile")}>
                        <User size={16} />
                        {userName}
                    </div>
                    <button className="logout-btn" onClick={handleLogout}>
                        <LogOut size={16} />
                        Logout
                    </button>
                </div>
            </div>
        </>
    );
};

export default Sidebar;


import React, { useState, useEffect, useRef } from 'react';
import api from '../lib/api';
import Sidebar from '../components/Sidebar';
import { useNavigate } from 'react-router-dom';
import { Plus, Trash2, CheckCircle, Circle, Bell, Clock } from 'lucide-react';

const Reminders = () => {
    const navigate = useNavigate();
    const userId = localStorage.getItem("user_id");
    const [reminders, setReminders] = useState([]);
    const [content, setContent] = useState("");
    const [dueDate, setDueDate] = useState("");
    const [loading, setLoading] = useState(false);
    const [toast, setToast] = useState(null); // In-App Notification State

    // Ref to avoid stale closures in setInterval
    const remindersRef = useRef([]);

    useEffect(() => {
        remindersRef.current = reminders;
    }, [reminders]);

    useEffect(() => {
        if (!userId) {
            navigate("/auth");
            return;
        }
        loadReminders();

        // Request Notification Permission on mount
        if (Notification.permission !== "granted" && Notification.permission !== "denied") {
            Notification.requestPermission();
        }

        // Check for due reminders every 10 seconds
        const interval = setInterval(checkReminders, 10000);
        return () => clearInterval(interval);
    }, [userId]);

    const loadReminders = async () => {
        try {
            const res = await api.get(`/reminders/${userId}`);
            // Sort by due date (soonest first)
            const sorted = res.data.sort((a, b) => {
                if (!a.due_date) return 1;
                if (!b.due_date) return -1;
                return new Date(a.due_date) - new Date(b.due_date);
            });
            setReminders(sorted);
        } catch (err) {
            console.error("Failed to load reminders", err);
        }
    };

    const checkReminders = () => {
        const now = new Date();
        remindersRef.current.forEach(r => {
            if (!r.is_completed && r.due_date) {
                // Backend sends naive UTC string (e.g., "2023-10-27T14:30:00")
                // We append 'Z' to force browser to treat it as UTC, then convert to local
                const utcDateString = r.due_date.endsWith("Z") ? r.due_date : r.due_date + "Z";
                const due = new Date(utcDateString);

                const diffSeconds = (now - due) / 1000;

                // Trigger if due in the last 2 minutes (0 to 120s ago)
                // This covers us if the interval missed the exact second.
                if (diffSeconds >= 0 && diffSeconds < 120) {
                    showNotification(r.content);
                }
            }
        });
    };

    const showNotification = async (text) => {
        // ALWAYS show in-app toast (guaranteed visibility)
        setToast(text);
        setTimeout(() => setToast(null), 5000); // Hide after 5s

        // Try System Notification
        if ("Notification" in window && Notification.permission === "granted") {
            new Notification("RepliMate Reminder", {
                body: text,
                icon: "/favicon.ico"
            });
        }

        // Play Sound
        const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
        audio.play().catch(e => console.log("Audio play failed", e));
    };

    const handleAdd = async (e) => {
        e.preventDefault();
        if (!content.trim()) return;
        setLoading(true);

        try {
            // Send ISO string (UTC) to backend
            const isoDate = dueDate ? new Date(dueDate).toISOString() : null;

            await api.post(`/reminders/${userId}`, {
                content: content,
                due_date: isoDate
            });
            setContent("");
            setDueDate("");
            loadReminders();
        } catch (err) {
            console.error("Failed to add", err);
        } finally {
            setLoading(false);
        }
    };

    const handleToggle = async (id) => {
        setReminders(prev => prev.map(r =>
            r.id === id ? { ...r, is_completed: !r.is_completed } : r
        ));

        try {
            await api.put(`/reminders/${id}/toggle`);
        } catch (err) {
            console.error("Failed to toggle", err);
            loadReminders(); // Revert
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this reminder?")) return;
        try {
            await api.delete(`/reminders/${id}`);
            setReminders(prev => prev.filter(r => r.id !== id));
        } catch (err) {
            console.error("Failed to delete", err);
        }
    };

    const formatTime = (dateStr) => {
        if (!dateStr) return null;
        const utcDate = dateStr.endsWith("Z") ? dateStr : dateStr + "Z";
        return new Date(utcDate).toLocaleString([], {
            weekday: 'short', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    return (
        <div style={{ display: 'flex', width: '100%', height: '100vh', background: '#f8f9fa' }}>
            <Sidebar userId={userId} currentSessionId={null} onSelectSession={() => navigate("/chat")} onNewChat={() => navigate("/chat")} />

            <div className="main-content" style={{ flex: 1, padding: '40px', overflowY: 'auto', position: 'relative' }}>
                {toast && (
                    <div style={{
                        position: 'fixed', top: '20px', right: '20px',
                        background: '#323232', color: 'white', padding: '15px 25px',
                        borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                        zIndex: 1000, display: 'flex', alignItems: 'center', gap: '10px',
                        animation: 'slideIn 0.3s ease-out'
                    }}>
                        <Bell size={20} color="#8ab4f8" />
                        <span style={{ fontSize: '15px', fontWeight: '500' }}>{toast}</span>
                    </div>
                )}
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>

                    {/* Header */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '30px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                            <Bell size={28} color="#1a73e8" />
                            <h1 style={{ fontSize: '24px', fontWeight: '500', color: '#202124', margin: 0 }}>Reminders</h1>
                        </div>
                        <button
                            onClick={() => showNotification("Test Notification from RepliMate! 🔔")}
                            style={{
                                padding: '8px 16px', background: '#e8f0fe', color: '#1967d2',
                                border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: '600',
                                transition: 'background 0.2s'
                            }}
                        >
                            Test Notification
                        </button>
                    </div>

                    {/* Add Form */}
                    <form onSubmit={handleAdd} style={{
                        background: 'white', padding: '20px', borderRadius: '12px',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.08)', marginBottom: '25px', display: 'flex', gap: '12px', alignItems: 'center'
                    }}>
                        <input
                            style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid #dadce0', fontSize: '15px', outline: 'none' }}
                            value={content}
                            onChange={e => setContent(e.target.value)}
                            placeholder="Add a task..."
                            autoFocus
                        />
                        <input
                            type="datetime-local"
                            style={{ padding: '11px', borderRadius: '8px', border: '1px solid #dadce0', fontFamily: 'inherit', color: '#5f6368', fontSize: '14px' }}
                            value={dueDate}
                            onChange={e => setDueDate(e.target.value)}
                        />
                        <button type="submit" disabled={loading} style={{
                            background: '#1a73e8', color: 'white', border: 'none', borderRadius: '8px',
                            padding: '12px 20px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '500'
                        }}>
                            <Plus size={18} /> Add
                        </button>
                    </form>

                    {/* Pending List */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        {reminders.filter(r => !r.is_completed).map(r => (
                            <ReminderItem key={r.id} r={r} onToggle={handleToggle} onDelete={handleDelete} formatTime={formatTime} />
                        ))}
                    </div>

                    {/* Completed Section (if any) */}
                    {reminders.some(r => r.is_completed) && (
                        <div style={{ marginTop: '40px' }}>
                            <h3 style={{ fontSize: '14px', color: '#5f6368', marginBottom: '15px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Completed</h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', opacity: 0.6 }}>
                                {reminders.filter(r => r.is_completed).map(r => (
                                    <ReminderItem key={r.id} r={r} onToggle={handleToggle} onDelete={handleDelete} formatTime={formatTime} />
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

const ReminderItem = ({ r, onToggle, onDelete, formatTime }) => (
    <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '16px 20px', background: 'white', borderRadius: '10px',
        boxShadow: r.is_completed ? 'none' : '0 1px 2px rgba(0,0,0,0.05)',
        border: '1px solid #f1f3f4', transition: 'all 0.2s'
    }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '15px', flex: 1 }}>
            <div onClick={() => onToggle(r.id)} style={{ cursor: 'pointer', color: r.is_completed ? '#1e8e3e' : '#bdc1c6', marginTop: '2px' }}>
                {r.is_completed ? <CheckCircle size={22} /> : <Circle size={22} />}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{
                    fontSize: '15px', fontWeight: r.is_completed ? '400' : '500',
                    textDecoration: r.is_completed ? 'line-through' : 'none',
                    color: r.is_completed ? '#5f6368' : '#202124'
                }}>
                    {r.content}
                </span>
                {r.due_date && (
                    <span style={{ fontSize: '12px', color: r.is_completed ? '#9aa0a6' : '#d93025', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                        <Clock size={12} /> {formatTime(r.due_date)}
                    </span>
                )}
            </div>
        </div>
        <button onClick={() => onDelete(r.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#dadce0', padding: '5px' }}>
            <Trash2 size={16} />
        </button>
    </div>
);

export default Reminders;

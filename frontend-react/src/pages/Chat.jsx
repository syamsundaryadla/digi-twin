
import React, { useState, useEffect, useRef } from 'react';
import api from '../lib/api';
import { useNavigate, useParams } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { Send, Mic } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const Typewriter = ({ text }) => {
    const [displayedText, setDisplayedText] = useState('');

    useEffect(() => {
        let i = 0;
        setDisplayedText('');
        const intervalId = setInterval(() => {
            setDisplayedText((prev) => prev + text.charAt(i));
            i++;
            if (i > text.length - 1) clearInterval(intervalId);
        }, 15);
        return () => clearInterval(intervalId);
    }, [text]);

    return (
        <ReactMarkdown
            components={{
                p: ({ node, ...props }) => <p style={{ marginBottom: '10px' }} {...props} />,
                ul: ({ node, ...props }) => <ul style={{ marginLeft: '20px', marginBottom: '10px' }} {...props} />,
                li: ({ node, ...props }) => <li style={{ marginBottom: '5px' }} {...props} />
            }}
        >
            {displayedText}
        </ReactMarkdown>
    );
};

const Chat = () => {
    const navigate = useNavigate();
    const { sessionId: routeSessionId } = useParams(); // Get ID from URL
    const userId = localStorage.getItem("user_id");
    const userName = localStorage.getItem("username");

    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    // Redirect if not logged in
    useEffect(() => {
        if (!userId) navigate("/auth");
    }, [userId, navigate]);

    // Sync Route Param with State
    useEffect(() => {
        if (routeSessionId) {
            loadHistory(routeSessionId);
        } else {
            setMessages([]); // New Chat
        }
    }, [routeSessionId]);

    const loadHistory = async (sid) => {
        try {
            const res = await api.get(`/history/${sid}`);
            // History messages are NOT new, so no animation
            setMessages(res.data.map(m => ({ ...m, isNew: false })));
            scrollToBottom();
        } catch (err) {
            console.error("Failed to load history", err);
        }
    };

    const scrollToBottom = () => {
        setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
        }, 100);
    };

    const handleSend = async () => {
        if (!input.trim() || loading) return;
        const userMsg = input.trim();
        setInput('');
        setLoading(true);

        // Optimistic UI
        const tempMsg = { role: 'user', content: userMsg, isNew: false };
        setMessages(prev => [...prev, tempMsg]);
        scrollToBottom();

        try {
            const res = await api.post("/chat", {
                user_id: userId,
                question: userMsg,
                session_id: routeSessionId || null // Use route ID if exists
            });

            const { answer, session_id } = res.data;

            // If we started a new chat, navigate to the new URL
            if (!routeSessionId && session_id) {
                // We navigate silently to update URL without reloading full page if possible,
                // but standard navigate works fine.
                navigate(`/chat/${session_id}`, { replace: true });
            }

            // Add Bot Response with isNew=true for animation
            setMessages(prev => [...prev, { role: 'assistant', content: answer, isNew: true }]);
            scrollToBottom();

        } catch (err) {
            console.error("Chat error", err);
            setMessages(prev => [...prev, { role: 'assistant', content: "Error connecting to server.", isNew: false }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') handleSend();
    };

    return (
        <div style={{ display: 'flex', width: '100%', height: '100vh' }}>
            <Sidebar
                userId={userId}
                currentSessionId={routeSessionId}
                onSelectSession={(sid) => navigate(`/chat/${sid}`)}
                onNewChat={() => navigate("/chat")}
            />

            <div className="main-content">
                {!routeSessionId && messages.length === 0 ? (
                    // Hero View
                    <div className="hero-container">
                        <h1 className="hero-title">How can I help, {userName}?</h1>
                        <div className={`input-wrapper bottom`}>
                            <div className="search-bar">
                                <input
                                    value={input}
                                    onChange={e => setInput(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Message RepliMate..."
                                    autoFocus
                                />
                                <div className="mic-icon" onClick={handleSend}>
                                    {loading ? "..." : <Send size={20} />}
                                </div>
                            </div>
                        </div>
                    </div>
                ) : (
                    // Chat View
                    <>
                        <div className="chat-list">
                            {messages.map((msg, i) => (
                                <div key={i} className={`message ${msg.role === 'user' ? 'user' : 'bot'}`}>
                                    <div style={{ width: '100%' }}>
                                        {/* Only animate if it's the LAST message, it is an assistant, AND it is tagged as New */}
                                        {msg.role === 'assistant' && i === messages.length - 1 && msg.isNew ? (
                                            <Typewriter text={msg.content} />
                                        ) : (
                                            <ReactMarkdown
                                                components={{
                                                    p: ({ node, ...props }) => <p style={{ marginBottom: '10px' }} {...props} />,
                                                    ul: ({ node, ...props }) => <ul style={{ marginLeft: '20px', marginBottom: '10px' }} {...props} />,
                                                    li: ({ node, ...props }) => <li style={{ marginBottom: '5px' }} {...props} />
                                                }}
                                            >
                                                {msg.content}
                                            </ReactMarkdown>
                                        )}
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div className="message bot">
                                    <div className="typing-indicator">
                                        <span>.</span><span>.</span><span>.</span>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        <div className="input-wrapper bottom">
                            <div className="search-bar">
                                <input
                                    value={input}
                                    onChange={e => setInput(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Message RepliMate..."
                                    autoFocus
                                    disabled={loading}
                                />
                                <div className="mic-icon" onClick={handleSend}>
                                    {loading ? "..." : <Send size={20} />}
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default Chat;

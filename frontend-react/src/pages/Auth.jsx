import React, { useState } from 'react';
import { supabase } from '../lib/supabaseClient';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { Eye, EyeOff } from 'lucide-react';

const Auth = () => {
    const [mode, setMode] = useState('login'); // 'login' or 'signup'
    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState('');
    const navigate = useNavigate();

    // Form State
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    // Check for existing session on mount
    React.useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (session) {
                syncUserWithBackend(session.user);
            }
        });

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            if (session) {
                syncUserWithBackend(session.user);
            }
        });

        return () => subscription.unsubscribe();
    }, []);

    const syncUserWithBackend = async (user) => {
        try {
            console.log("Syncing with backend...");
            const res = await api.post("/auth/sync", {
                email: user.email,
                full_name: user.user_metadata?.full_name
            });

            if (res.data.user_id) {
                localStorage.setItem("user_id", res.data.user_id);
                localStorage.setItem("username", res.data.username);

                if (res.data.is_new_user) {
                    navigate("/onboarding");
                } else {
                    navigate("/chat");
                }
            }
        } catch (err) {
            console.error("Sync failed", err);
            // If backend is down, we can't really proceed safely to chat context, 
            // but we might let them delete msg to retry.
            setMsg("Connected to Supabase but failed to sync with Backend. Is the server running?");
        }
    };

    const handleLogin = async () => {
        if (!email || !password) return setMsg("Email and Password required");
        setLoading(true);
        try {
            const { error } = await supabase.auth.signInWithPassword({
                email,
                password,
            })
            if (error) throw error;
            // Sync handled by listener
        } catch (err) {
            setMsg(err.message || "Login failed");
            setLoading(false);
        }
    };

    const handleSignup = async () => {
        if (!email || !password || !confirm) return setMsg("All fields required");
        if (password !== confirm) return setMsg("Passwords do not match");

        setLoading(true);
        setMsg("Creating account...");
        try {
            const { error } = await supabase.auth.signUp({
                email,
                password,
                options: {
                    emailRedirectTo: window.location.origin
                }
            })
            if (error) throw error;
            setMsg("Signup successful! Check your email if verification is enabled.");
        } catch (err) {
            setMsg(err.message || "Signup failed");
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <h2>RepliMate</h2>
                    <p>Your AI Digital Twin.</p>
                </div>

                <div className="auth-tabs">
                    <button
                        className={`tab-btn ${mode === 'login' ? 'active' : ''}`}
                        onClick={() => setMode('login')}
                    >Login</button>
                    <button
                        className={`tab-btn ${mode === 'signup' ? 'active' : ''}`}
                        onClick={() => setMode('signup')}
                    >Sign Up</button>
                </div>

                <div className="auth-form">
                    <div className="form-group">
                        <label>Email</label>
                        <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="name@example.com" />
                    </div>

                    <div className="form-group" style={{ position: 'relative' }}>
                        <label>Password</label>
                        <input
                            type={showPassword ? "text" : "password"}
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            placeholder="Enter password"
                        />
                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            style={{
                                position: 'absolute', right: '12px', top: '32px',
                                background: 'none', border: 'none', cursor: 'pointer',
                                color: '#5f6368'
                            }}
                        >
                            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                        </button>
                    </div>

                    {mode === 'signup' && (
                        <div className="form-group">
                            <label>Confirm Password</label>
                            <input
                                type={showPassword ? "text" : "password"}
                                value={confirm}
                                onChange={e => setConfirm(e.target.value)}
                                placeholder="Confirm password"
                            />
                        </div>
                    )}

                    {mode === 'login' ? (
                        <button className="primary-btn auth-submit" onClick={handleLogin} disabled={loading}>
                            {loading ? "Loading..." : "Login"}
                        </button>
                    ) : (
                        <button className="primary-btn auth-submit" onClick={handleSignup} disabled={loading}>
                            {loading ? "Creating..." : "Create Account"}
                        </button>
                    )}
                </div>

                <p className="error-text">{msg}</p>
            </div>
        </div>
    );
};

export default Auth;

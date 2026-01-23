
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { ArrowRight, Sparkles, Smile, BookOpen, User } from 'lucide-react';

const Onboarding = () => {
    const navigate = useNavigate();
    const userId = localStorage.getItem("user_id");
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);

    const [data, setData] = useState({
        nickname: localStorage.getItem("username") || "",
        hobbies: "",
        interests: "",
        vibe: "Friendly"
    });

    const handleNext = () => setStep(prev => prev + 1);

    const handleSubmit = async () => {
        setLoading(true);
        try {
            // Updated Profile Name
            if (data.nickname) {
                await api.put(`/me/${userId}`, { full_name: data.nickname });
            }

            // Create Memories
            const memories = [
                `User prefers to be called ${data.nickname}.`,
                `User enjoys these hobbies: ${data.hobbies}.`,
                `User is interested in learning about: ${data.interests}.`,
                `User prefers a ${data.vibe} communication style.`
            ];

            await api.post(`/memories/${userId}`, { items: memories });

            navigate("/chat");
        } catch (err) {
            console.error("Onboarding failed", err);
            // Fallback to chat anyway
            navigate("/chat");
        }
    };

    const renderStep = () => {
        switch (step) {
            case 1:
                return (
                    <div className="onboard-step fade-in">
                        <User size={48} className="onboard-icon" />
                        <h2>What should I call you?</h2>
                        <input
                            value={data.nickname}
                            onChange={e => setData({ ...data, nickname: e.target.value })}
                            placeholder="Your preferred name"
                            autoFocus
                        />
                        <button className="primary-btn" onClick={handleNext} disabled={!data.nickname}>Next</button>
                    </div>
                );
            case 2:
                return (
                    <div className="onboard-step fade-in">
                        <Smile size={48} className="onboard-icon" />
                        <h2>What do you do for fun?</h2>
                        <input
                            value={data.hobbies}
                            onChange={e => setData({ ...data, hobbies: e.target.value })}
                            placeholder="e.g. Hiking, Gaming, Coding"
                            autoFocus
                        />
                        <button className="primary-btn" onClick={handleNext}>Next</button>
                    </div>
                );
            case 3:
                return (
                    <div className="onboard-step fade-in">
                        <BookOpen size={48} className="onboard-icon" />
                        <h2>What do you want to learn?</h2>
                        <input
                            value={data.interests}
                            onChange={e => setData({ ...data, interests: e.target.value })}
                            placeholder="e.g. Python, History, Cooking"
                            autoFocus
                        />
                        <button className="primary-btn" onClick={handleNext}>Next</button>
                    </div>
                );
            case 4:
                return (
                    <div className="onboard-step fade-in">
                        <Sparkles size={48} className="onboard-icon" />
                        <h2>How should I talk to you?</h2>
                        <div className="vibe-options">
                            {["Formal", "Friendly", "Sarcastic", "Concise"].map(v => (
                                <button
                                    key={v}
                                    className={`vibe-btn ${data.vibe === v ? 'active' : ''}`}
                                    onClick={() => setData({ ...data, vibe: v })}
                                >
                                    {v}
                                </button>
                            ))}
                        </div>
                        <button className="primary-btn" onClick={handleSubmit} disabled={loading}>
                            {loading ? "Personalizing..." : "Finish"}
                        </button>
                    </div>
                );
            default: return null;
        }
    };

    return (
        <div className="onboarding-container">
            <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${step * 25}%` }}></div>
            </div>
            {renderStep()}
        </div>
    );
};

export default Onboarding;

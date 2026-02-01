import React, { useState } from 'react';
import { registerUser, loginUser } from './api/auth';

const AuthForm = ({ type }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (type === 'register') {
                const response = await registerUser(username, password);
                setMessage(response.message);
            } else if (type === 'login') {
                const response = await loginUser(username, password);
                setMessage(response.message);
            }
        } catch (error) {
            setMessage('An error occurred. Please try again.');
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <h2>{type === 'register' ? 'Register' : 'Login'}</h2>
            <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit">Submit</button>
            {message && <p>{message}</p>}
        </form>
    );
};

export default AuthForm;
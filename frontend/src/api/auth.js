import axios from 'axios';

const API_BASE_URL = '/account';

axios.defaults.withCredentials = true;

export const registerUser = async (username, password) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/register/`, {
            username,
            password,
        });
        return response.data;
    } catch (error) {
        console.error('Error registering user:', error);
        throw error;
    }
};

export const loginUser = async (username, password) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/login/`, {
            username,
            password,
        });
        return response.data;
    } catch (error) {
        console.error('Error logging in:', error);
        throw error;
    }
};
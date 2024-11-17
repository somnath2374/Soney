import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';
const AUTH_TOKEN_KEY = 'authToken';

axios.defaults.baseURL = API_BASE_URL;

// Helper to set the Authorization header
export const setAuthToken = (token: string | null) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  } else {
    delete axios.defaults.headers.common['Authorization'];
    localStorage.removeItem(AUTH_TOKEN_KEY);
  }
};

// Get token from localStorage (if available)
const token = localStorage.getItem(AUTH_TOKEN_KEY);
if (token) {
  setAuthToken(token);
}

// API Requests
//Authorization
export const signup = async (username: string, email: string, password: string) => {
  const response = await axios.post('/auth/signup', { username, email, password });
  return response.data;
};

export const login = async (username: string, password: string) => {
  const response = await axios.post('/auth/login', new URLSearchParams({ username, password }));
  const { access_token } = response.data;
  setAuthToken(access_token);
  return access_token;
};

export const logout = () => {
  setAuthToken(null);
};

export const getUserProfile = async () => {
  const response = await axios.get('/user/profile');
  return response.data;
};

//Posts
export const getPosts = async () => {
  const response = await axios.get('/post/posts');
  return response.data;
};

export const getUserPosts = async (user_id: string) => {
  const url=`/post/user/${user_id}`;
  const response = await axios.get(url);  
  return response.data;
};

export const createPost = async (title: string, content: string, hashtags: string[],pictures: string[], videos: string[]) => {
  const response = await axios.post('/post/create', { title,content, hashtags, pictures, videos });
  return response.data;
};

export const likePost = async (postId: string) => {
  const response = await axios.post(`/post/like/${postId}`);
  return response.data;
};

export const dislikePost = async (postId: string) => {
  const response = await axios.post(`/post/dislike/${postId}`);
  return response.data;
};

export const commentPost = async (postId: string, comment: string) => {
  const response = await axios.post(`/post/comment/${postId}`, { comment });
  return response.data;
};

//chat
export const sendMessage = async (receiver_id: string, message: string) => {
  const response = await axios.post('chat/messages', { receiver_id, message });
  return response.data;
};

export const getMessages = async (friendId: string) => {
  const response = await axios.get(`chat/messages/${friendId}`);
  return response.data;
};

//Friends
export const sendFriendRequest = async (friendId: string) => {
  const response = await axios.post(`/friends/send_request/${friendId}`);
  return response.data;
};

export const acceptFriendRequest = async (friendId: string) => {
  const response = await axios.post(`/friends/accept_request/${friendId}`);
  return response.data;
};

export const rejectFriendRequest = async (friendId: string) => {
  const response = await axios.post(`/friends/reject_request/${friendId}`);
  return response.data;
};

export const getFriends = async (user_id: string) => {
  const url=`/friends/${user_id}`;
  const response = await axios.get(url);  
  return response.data;
};

import React, { useEffect, useState } from 'react';
import { getUserProfile, getPosts, logout } from '../services/api';
import { useNavigate } from 'react-router-dom';
import "./Home.css";

type Post = {
  id: string;
  title: string;
  content: string;
  author: string;
};

const Home: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    getPosts().then(data => setPosts(data));
  }, []);

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const userProfile = await getUserProfile();
        setUser(userProfile);
      } catch (error) {
        setUser(null);
      }
    };
    fetchUserProfile();
  }, []);


  return (
    <div className='home'>
      <h1>Home</h1>
      {user ? (
        <div className="welcome">
          <p>Welcome, {user.email}</p>
        </div>
      ) : (
        <p>Please log in..</p>
      )}
      <h1>Posts page</h1>
      <ul>
        {posts.map((post) => (
          <li key={post.id}>
            <h2>{post.title}</h2>
            <p>{post.content}</p>
            <p>Author: {post.author}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Home;

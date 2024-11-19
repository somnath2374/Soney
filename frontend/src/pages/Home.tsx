import React, { useEffect, useState } from 'react';
import { getUserProfile, getPosts, logout } from '../services/api';
import { useNavigate } from 'react-router-dom';
import "./Home.css";
import PostItem from '../components/PostItem';

type Post = {
  id: string;
  title: string;
  content: string;
  author: string;
};

const Home: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [user, setUser] = useState<any>(null);
  const [comments, setComments] = useState<{ [key: string]: string }>({});

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
      <h1>Posts</h1>
      <ul>
        {posts.map((post) => (
          <PostItem
            key={post.id}
            post={post}
            posts={posts}
            comments={comments}
            setPosts={setPosts}
          />
        ))}
      </ul>
    </div>
  );
};

export default Home;

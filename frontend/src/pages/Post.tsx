import React, { useEffect, useState } from 'react';
import { getPosts, createPost, getUserProfile } from '../services/api';
import './Post.css';
import PostItem from '../components/PostItem';

const Post: React.FC = () => {
  const [posts, setPosts] = useState<any[]>([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [pictures, setPictures] = useState<string[]>([]);
  const [videos, setVideos] = useState<string[]>([]);
  const [authorId, setAuthorId] = useState('');
  const [comments, setComments] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    const fetchUserProfile = async () => {
      const userProfile = await getUserProfile();
      setAuthorId(userProfile.id);
    };
    fetchUserProfile();
  }, []);

  useEffect(() => {
    const fetchPosts = async () => {
      const data = await getPosts();
      setPosts(data);
    };
    fetchPosts();
  }, []);

  const handleCreatePost = async () => {
    await createPost(title, content, hashtags, pictures, videos);
    setTitle('');
    setContent('');
    setHashtags([]);
    setPictures([]);
    setVideos([]);
    alert('Post created successfully');
    const data = await getPosts();
    setPosts(data);
  };

  const handleHashtagsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setHashtags(e.target.value.split(',').map(tag => tag.trim()));
  };

  const handlePicturesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPictures(e.target.value.split(',').map(url => url.trim()));
  };

  const handleVideosChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setVideos(e.target.value.split(',').map(url => url.trim()));
  };

  return (
    <div className='post-container'>
      <div className='create-post'>
        <h1>Create Post</h1>
        <div>
          <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <input placeholder="Content" value={content} onChange={(e) => setContent(e.target.value)} />
          <input placeholder="Hashtags (comma separated)" value={hashtags.join(', ')} onChange={handleHashtagsChange} />
          <input placeholder="Pictures URLs (comma separated)" value={pictures.join(', ')} onChange={handlePicturesChange} />
          <input placeholder="Videos URLs (comma separated)" value={videos.join(', ')} onChange={handleVideosChange} />
          <div className='button-container'>
            <button onClick={handleCreatePost}>Create Post</button>
          </div>
        </div>
      </div>
      <div className='posts'>
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
    </div>
  );
};

export default Post;

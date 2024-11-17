import React, { useEffect, useState } from 'react';
import { getPosts, createPost, likePost, dislikePost, commentPost, getUserProfile } from '../services/api';
import './Post.css';

const Post: React.FC = () => {
  const [posts, setPosts] = useState<any[]>([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [pictures, setPictures] = useState<string[]>([]);
  const [videos, setVideos] = useState<string[]>([]);
  const [authorId, setAuthorId] = useState('');
  const [comment, setComment] = useState('');

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

  const handleLikePost = async (postId: string) => {
    await likePost(postId);
    alert('Post liked');
  };

  const handleDislikePost = async (postId: string) => {
    await dislikePost(postId);
    alert('Post disliked');
  };

  const handleCommentPost = async (postId: string) => {
    if (comment.trim() === '') {
      alert('Comment cannot be empty');
      return;
    }
    await commentPost(postId, comment);
    setComment('');
    alert('Comment added');
  };

  return (
    <div className='post'>
      <h1>Posts</h1>
      <div>
        <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <input placeholder="Content" value={content} onChange={(e) => setContent(e.target.value)} />
        <input placeholder="Hashtags (comma separated)" value={hashtags.join(', ')} onChange={handleHashtagsChange} />
        <input placeholder="Pictures URLs (comma separated)" value={pictures.join(', ')} onChange={handlePicturesChange} />
        <input placeholder="Videos URLs (comma separated)" value={videos.join(', ')} onChange={handleVideosChange} />
        <button onClick={handleCreatePost}>Create Post</button>
      </div>
      <ul>
        {posts.map((post) => (
          <li key={post.id}>
            <h2>{post.title}</h2>
            <p>{post.content}</p>
            <p>Author: {post.author_id}</p>
            <p>Hashtags: {post.hashtags.join(', ')}</p>
            {post.pictures && post.pictures.map((pic: string, index: number) => (
              <img key={index} src={pic} alt="Post pic" style={{ maxWidth: '100%' }} />
            ))}
            {post.videos && post.videos.map((video: string, index: number) => (
              <video key={index} controls style={{ maxWidth: '100%' }}>
                <source src={video} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            ))}
            <div>
              <button onClick={() => handleLikePost(post.id)}>Like</button>
              <button onClick={() => handleDislikePost(post.id)}>Dislike</button>
              <input placeholder="Add a comment" value={comment} onChange={(e) => setComment(e.target.value)} />
              <button onClick={() => handleCommentPost(post.id)}>Comment</button>
            </div>
            <div>
              <h3>Comments</h3>
              <ul>
                {post.comments && post.comments.map((comment: any, index: number) => (
                  <li key={index}>{comment.content}</li>
                ))}
              </ul>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Post;

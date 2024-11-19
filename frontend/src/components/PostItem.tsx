import React, { useState } from 'react';
import { likePost, dislikePost, commentPost } from '../services/api';
import '../pages/Post.css';

interface PostItemProps {
  post: any;
  posts: any[];
  comments: { [key: string]: string };
  setPosts: React.Dispatch<React.SetStateAction<any[]>>;
}
const PostItem: React.FC<PostItemProps> = ({ post, posts, comments, setPosts }) => {
  const [comment, setComment] = useState('');

  const handleLikePost = async (postId: string) => {
    await likePost(postId);
    const updatedPosts = posts.map(p => {
      if (p.id === postId) {
        return { ...p, likes_count: p.likes_count + 1 };
      }
      return p;
    });
    setPosts(updatedPosts);
  };

  const handleDislikePost = async (postId: string) => {
    await dislikePost(postId);
    const updatedPosts = posts.map(p => {
      if (p.id === postId) {
        return { ...p, dislikes_count: p.dislikes_count + 1 };
      }
      return p;
    });
    setPosts(updatedPosts);
  };

  const handleCommentChange = (postId: string, value: string) => {
    setComment(value);
  };

  const handleCommentPost = async (postId: string) => {
    if (comment.trim() === '') {
      alert('Comment cannot be empty');
      return;
    }
    await commentPost(postId, comment);
    const updatedPosts = posts.map(p => {
      if (p.id === postId) {
        return {
          ...p,
          comments: [...p.comments, { content: comment }],
          comments_count: p.comments_count + 1,
        };
      }
      return p;
    });
    setPosts(updatedPosts);
    setComment('');
    alert('Comment added');
  };

  return (
    <li key={post.id} className='post'>
      <h2>{post.title}</h2>
      <p>{post.content}</p>
      <p>Author: {post.author_id}</p>
      <p>
        Hashtags: {post.hashtags.map((tag: string, index: number) => (
          <span key={index} className='hashtag'>#{tag}</span>
        ))}
      </p>
      {post.pictures && post.pictures.map((pic: string, index: number) => (
        <img key={index} src={pic} alt="Post pic" className='post-image' />
      ))}
      {post.videos && post.videos.map((video: string, index: number) => (
        <video key={index} controls className='post-video'>
          <source src={video} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      ))}
      <div className='post-actions'>
        <button onClick={() => handleLikePost(post.id)}>Like ({post.likes_count})</button>
        <button onClick={() => handleDislikePost(post.id)}>Dislike ({post.dislikes_count})</button>
        <input
          placeholder="Add a comment"
          value={comment}
          onChange={(e) => handleCommentChange(post.id, e.target.value)}
        />
        <button onClick={() => handleCommentPost(post.id)}>Comment</button>
      </div>
      <div className='post-comments'>
        <h3>Comments ({post.comments_count})</h3>
        <div className='comments-scroll'>
          <ul>
            {post.comments && post.comments.map((comment: any, index: number) => (
              <li key={index}>{comment.content}</li>
            ))}
          </ul>
        </div>
      </div>
    </li>
  );
};

export default PostItem;
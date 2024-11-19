import React, { useEffect, useState } from 'react';
import { getUserProfile, sendFriendRequest } from '../services/api';
import './Profile.css';
import Friends from './Friends';

const Profile: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [newFriendId, setNewFriendId] = useState<string>('');

  useEffect(() => {
    const fetchProfile = async () => {
      const data = await getUserProfile();
      setUser(data);
    };
    fetchProfile();
  }, []);

  const handleSendFriendRequest = async () => {
    await sendFriendRequest(newFriendId);
    alert('Friend request sent');
    setNewFriendId('');
  };

  return (
    <div className='profile-container'>
      <div className='profile'>
        <h1>Profile</h1>
        {user ? (
          <div>
            <p>User: {user.username}</p>
            <p>Email: {user.email}</p>
          </div>
        ) : (
          <p>Loading...</p>
        )}
        <div className='friend-request'>
          <h2>Send Friend Request</h2>
          <input
            placeholder="Friend ID"
            value={newFriendId}
            onChange={(e) => setNewFriendId(e.target.value)}
          />
          <button onClick={handleSendFriendRequest}>Send Friend Request</button>
        </div>
      </div>
      <Friends />
    </div>
  );
};

export default Profile;

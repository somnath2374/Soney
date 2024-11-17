import React, { useEffect, useState } from 'react';
import { getFriends, sendFriendRequest, acceptFriendRequest, rejectFriendRequest, getUserProfile } from '../services/api';
import './Friends.css';
import { AxiosResponse } from 'axios';

const Friends: React.FC = () => {
  const [friends, setFriends] = useState<string[]>([]);
  const [friendRequests, setFriendRequests] = useState<string[]>([]);
  const [userId, setUserId] = useState<string>('');
  const [newFriendId, setNewFriendId] = useState<string>('');
  
  useEffect(() => {
    const fetchUserProfile = async () => {
      const userProfile = await getUserProfile();
      setUserId(userProfile.id);
      setFriendRequests(userProfile.friend_requests);
    };
    fetchUserProfile();
  }, []);

  useEffect(() => {
    const fetchFriends = async () => {
      const userProfile = await getUserProfile();
      const data = await getFriends(userProfile.id);
      setFriends(data);
    };
    fetchFriends();
  }, []);

  const handleSendFriendRequest = async () => {
    const userProfile = await getUserProfile();
    await sendFriendRequest(newFriendId);
    alert('Friend request sent');
    setNewFriendId('');
  };

  const handleAcceptFriendRequest = async (friendId: string) => {
    await acceptFriendRequest(friendId);
    alert('Friend request accepted');
    setFriendRequests(friendRequests.filter(id => id !== friendId));
    setFriends([...friends, friendId]);
  };

  const handleRejectFriendRequest = async (friendId: string) => {
    await rejectFriendRequest(friendId);
    alert('Friend request rejected');
    setFriendRequests(friendRequests.filter(id => id !== friendId));
  };

  return (
    <div className='friends'>
      <h1>Friends</h1>
      <div>
        <input placeholder="Friend ID" value={newFriendId} onChange={(e) => setNewFriendId(e.target.value)} />
        <button onClick={handleSendFriendRequest}>Send Friend Request</button>
      </div>
      <h2>Friend Requests</h2>
      <ul>
        {friendRequests.map((friendId) => (
          <li key={friendId}>
            {friendId}
            <button onClick={() => handleAcceptFriendRequest(friendId)}>Accept</button>
            <button onClick={() => handleRejectFriendRequest(friendId)}>Reject</button>
          </li>
        ))}
      </ul>
      <h2>Friends List</h2>
      <ul>
        {friends.map((friend) => (
          <li key={friend}>{friend}</li>
        ))}
      </ul>
    </div>
  );
};

export default Friends;
import React, { useEffect, useState } from 'react';
import { getFriends, acceptFriendRequest, rejectFriendRequest, getUserProfile } from '../services/api';
import './Friends.css';

const Friends: React.FC = () => {
  const [friends, setFriends] = useState<string[]>([]);
  const [friendRequests, setFriendRequests] = useState<string[]>([]);
  const [userId, setUserId] = useState<string>('');

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
    <div className='friends-container'>
      <div className='friends'>
        <h2>Friend Requests</h2>
        {friendRequests.length > 0 ? (
          <ul>
            {friendRequests.map((friendId) => (
              <li key={friendId}>
                {friendId}
                <button onClick={() => handleAcceptFriendRequest(friendId)}>Accept</button>
                <button onClick={() => handleRejectFriendRequest(friendId)}>Reject</button>
              </li>
            ))}
          </ul>
        ) : (
          <p>No friend requests</p>
        )}
        <h2>Friends List</h2>
        {friends.length > 0 ? (
          <ul>
            {friends.map((friend) => (
              <li key={friend}>{friend}</li>
            ))}
          </ul>
        ) : (
          <p>No friends</p>
        )}
      </div>
    </div>
  );
};

export default Friends;
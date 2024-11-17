import React, { useEffect, useState } from 'react';
import { getUserProfile } from '../services/api';
import './Profile.css';
import Friends from './Friends';

const Profile: React.FC = () => {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      const data = await getUserProfile();
      setUser(data);
    };
    fetchProfile();
  }, []);

  return (
    <div className='profile'>
      <h1>Profile</h1>
      {user ? (
        <div>
          <h2>{user.name}</h2>
          <p>Email: {user.email}</p>
          <Friends/>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default Profile;

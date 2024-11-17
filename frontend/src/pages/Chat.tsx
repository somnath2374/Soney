import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getFriends, getUserProfile, getMessages, sendMessage } from '../services/api';
import './Chat.css';

const WEBSOCKET_URL = 'ws://127.0.0.1:8000/ws/chat/';

interface Message {
    sender_id: string,
    receiver_id: string,
    message: string,
    timestamp: Date,
    read: boolean
}

const Chat: React.FC = () => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [friends, setFriends] = useState<string[]>([]);
  const [selectedFriend, setSelectedFriend] = useState<string | null>(null);
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchFriends = async () => {
      const user = await getUserProfile();
      const friendsList = await getFriends(user.id);
      setFriends(friendsList);
    };
    fetchFriends();
  }, []);

  useEffect(() => {
    let ws: WebSocket;
    if (selectedFriend) {
      const fetchMessages = async () => {
        const messages = await getMessages(selectedFriend);
        setMessages(messages);
        scrollToBottom();
      };
      fetchMessages();

      const token = localStorage.getItem('authToken');
      if (!token) {
        navigate('/login');
        return;
      }

      ws = new WebSocket(`${WEBSOCKET_URL}${selectedFriend}/${token}`);

      ws.onopen = () => {
        console.log('Connected to chat');
        setSocket(ws);
      };

      ws.onmessage = (event) => {
        try {
          const messageData = JSON.parse(event.data);
          setMessages((prevMessages) => [...prevMessages, messageData]);
          scrollToBottom();
        } catch (e) {
          console.log('Message parsing error:', e);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = (event) => {
        console.log('WebSocket connection closed', event);
      };
    }

    return () => {
      ws?.close();
    };
  }, [selectedFriend, navigate]);

  const handleSendMessage = async () => {
    if (socket && input.trim()) {
      const user = await getUserProfile();
      const newMessage: Message = {
        sender_id: user.username, // Replace with the actual sender ID
        receiver_id: selectedFriend!,
        message: input,
        timestamp: new Date(),
        read: false,
      };
      await sendMessage(selectedFriend!, input);
      socket.send(JSON.stringify(newMessage));
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      setInput('');
      scrollToBottom();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className='chat-container'>
      <div className='friends-list'>
        <div className='friends-list-header'>Friends</div>
        <ul>
          {friends.map((friend) => (
            <li key={friend} className='friend-item' onClick={() => setSelectedFriend(friend)}>
              {friend}
            </li>
          ))}
        </ul>
      </div>
      <div className='chat'>
        {selectedFriend ? (
          <>
            <div className='chat-header'>{selectedFriend}</div>
            <div className='chat-messages'>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`message ${message.sender_id === selectedFriend ? 'received' : 'sent'}`}
                >
                  <strong>{message.sender_id}</strong>: {message.message}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <div className='input-container'>
              <input
                type="text"
                className='message-input'
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type a message"
              />
              <button className='send-button' onClick={handleSendMessage}>➤</button>
            </div>
          </>
        ) : (
          <div className='chat-header'>Select a friend to start chatting</div>
        )}
      </div>
    </div>
  );
};

export default Chat;

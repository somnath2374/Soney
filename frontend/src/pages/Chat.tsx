import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getFriends, getUserProfile, getMessages, startAnalysis,getAnalysisResult,getDetectedUsers } from '../services/api';
import './Chat.css';

const WEBSOCKET_URL = 'ws://127.0.0.1:8000/ws/chat/';

interface Message {
    sender_id: string,
    receiver_id: string,
    message: string,
    timestamp: string,
    read: boolean
}

const Chat: React.FC = () => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [friends, setFriends] = useState<Friend[]>([]);
  const [selectedFriend, setSelectedFriend] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  interface Friend {
    username: string;
    isSuspicious: boolean;
  }
  
  useEffect(() => {
    const fetchFriends = async () => {
      const user = await getUserProfile();
      setCurrentUser(user.username);
      const friendsList = await getFriends(user.id);
      const detectedUsers = await getDetectedUsers(); // Add this API call
      
      // Map friends to include suspicious flag
      const friendsWithFlags: Friend[] = friendsList.map((friend: string) => ({
        username: friend,
        isSuspicious: detectedUsers.some((detected: { username: string }) => detected.username === friend)
      }))
      
      setFriends(friendsWithFlags);
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
          setMessages((prevMessages) => {
            const messageExists = prevMessages.some(msg => 
              msg.sender_id === messageData.sender_id && 
              msg.message === messageData.message && 
              msg.timestamp === messageData.timestamp
            );
            return messageExists ? prevMessages : [...prevMessages, messageData];
          });
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
        sender_id: user.username,
        receiver_id: selectedFriend!,
        message: input,
        timestamp: new Date().toISOString(),
        read: false,
      };

      // Send the message via WebSocket
      socket.send(JSON.stringify(newMessage));

      // Update the state to reflect the new message
      setMessages((prevMessages) => [...prevMessages, newMessage]);

      setInput('');
      scrollToBottom();
    }
  };
  // Add new state
const [isAnalyzing, setIsAnalyzing] = useState(false);
const [analysisResult, setAnalysisResult] = useState<string | null>(null);

// Add analyze function after handleSendMessage
const handleAnalyze = async () => {
  if (selectedFriend) {
    setIsAnalyzing(true);
    await startAnalysis(selectedFriend);
    const pollInterval = setInterval(async () => {
      const result = await getAnalysisResult(selectedFriend);
      if (result.status !== 'no_analysis_found' && result.is_genuine !== undefined) {
        setAnalysisResult(result.is_genuine);
        setIsAnalyzing(false);
        clearInterval(pollInterval);
      }
    }, 5000);
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
        {friends.map((friend: Friend) => (
            <li 
              key={friend.username} 
              className={`friend-item ${friend.isSuspicious ? 'suspicious' : ''}`} 
              onClick={() => setSelectedFriend(friend.username)}
            >
              {friend.username}
              {friend.isSuspicious && <span className="warning-icon">⚠️</span>}
            </li>
          ))}
        </ul>
      </div>
      <div className='chat'>
        {selectedFriend ? (
          <>
            <div className='chat-header'>{selectedFriend}
            {analysisResult && (
          <div className={`analysis-result-message ${analysisResult !== 'genuine' ? 'negative' : 'positive'}`}>
          Analysis Result: {analysisResult}
        </div>
          )}
            <button 
              className='analyze-button'
              onClick={handleAnalyze}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze User'}
            </button>
            </div>
            <div className='chat-messages'>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`message ${message.sender_id === selectedFriend ? 'received' : 'sent'}`}
                >
                  <strong>{message.sender_id === currentUser ? 'You' : message.sender_id}:</strong> {message.message}
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
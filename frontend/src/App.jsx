import { useState, useRef, useEffect } from 'react';
import { loginUser, registerUser } from './api/auth';
import './App.css';

// ⚠️ 이미지 파일명이 정확한지 확인하세요! (대소문자 구분함)
import heartA from './assets/heart_a.png';
import heartClosed from './assets/heart_closed.png';
import heartO from './assets/heart_o.png';

// 백엔드 API URL (Django) - Vite Proxy 사용 시 상대 경로
const API_BASE_URL = '';

function App() {
  // 📋 상담사 목록
  const counselors = [
    { id: '권승현', name: '권승현' },
    { id: '주우재', name: '주우재' },
    { id: '강탱의 이야기', name: '강탱의 이야기' },
    { id: '연애언어TV', name: '연애언어TV' },
    { id: '김달', name: '김달' },
    { id: '랄라브루스', name: '랄라브루스' },
    { id: '준우', name: '준우' },
    { id: '박코', name: '박코' },
    { id: '모두의지인', name: '모두의지인' },
    { id: '김유신', name: '김유신' },
    { id: '오은영 박사', name: '오은영 박사' },
    { id: '홍차TV', name: '홍차TV' },
    { id: '마튜브', name: '마튜브' }
  ];

  // 현재 선택된 상담사 (기본값: 김달)
  const [selectedCounselor, setSelectedCounselor] = useState(counselors[4]);

  // 🔧 사이드바 열림/닫힘 상태
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // 🔐 인증 상태 (Django에서 관리할 예정)
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('chat_user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch (error) {
      return null;
    }
  });

  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState({ name: '', nickname: '', password: '' });
  const [authError, setAuthError] = useState('');

  // 대화 목록
  const [messages, setMessages] = useState([
    { id: 1, text: "안녕하세요! 김달입니다. 연애 고민이 있으시면 편하게 말씀해주세요 💕", sender: 'bot' }
  ]);

  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  // 📜 채팅 기록 관리
  const [chatSessions, setChatSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);

  // 봇 이미지 상태 관리
  const [currentBotImage, setCurrentBotImage] = useState(heartA);
  const botImages = [heartA, heartO, heartClosed, heartO];
  const imageIndex = useRef(0);
  const messagesEndRef = useRef(null);

  // 스크롤 자동 내리기
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 🔄 Select에서 상담사 변경
  const handleCounselorChange = (e) => {
    const selected = counselors.find(c => c.id === e.target.value);
    if (selected && selected.id !== selectedCounselor.id) {
      setSelectedCounselor(selected);
      setIsTyping(false);
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: `💫 상담사가 ${selected.name}(으)로 변경되었습니다. 이어서 상담해주세요!`,
        sender: 'bot'
      }]);
    }
  };

  // 🍔 사이드바 토글
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  // 🔐 로그인 (Django 연동)
  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');

    // 유효성 검사
    if (!authForm.nickname.trim()) {
      setAuthError('닉네임을 입력해주세요.');
      return;
    }
    if (!authForm.password) {
      setAuthError('비밀번호를 입력해주세요.');
      return;
    }

    try {
      const response = await loginUser(authForm.nickname, authForm.password);
      console.log("Login success:", response);
      // nickname을 user state에 저장 (서버 응답 혹은 입력값 사용)
      const userData = { username: response.username || authForm.nickname };
      setUser(userData);
      localStorage.setItem('chat_user', JSON.stringify(userData));

      setShowAuthModal(false);
      setAuthForm({ name: '', nickname: '', password: '' });

      // 로그인 성공 시 채팅 기록 불러오기
      fetchChatHistory();
    } catch (error) {
      console.error("Login error:", error);
      if (error.response && error.response.status === 401) {
        setAuthError('로그인 실패: 아이디 또는 비밀번호가 일치하지 않습니다.');
      } else {
        setAuthError('로그인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      }
    }
  };

  // 📝 회원가입 (Django 연동)
  const handleRegister = async (e) => {
    e.preventDefault();
    setAuthError('');

    // 유효성 검사
    if (!authForm.name.trim()) {
      setAuthError('이름을 입력해주세요.');
      return;
    }
    if (!authForm.nickname.trim()) {
      setAuthError('닉네임을 입력해주세요.');
      return;
    }
    if (!authForm.password) {
      setAuthError('비밀번호를 입력해주세요.');
      return;
    }
    if (authForm.password.length < 8) {
      setAuthError('비밀번호는 8글자 이상이어야 합니다.');
      return;
    }

    try {
      const response = await registerUser(authForm.nickname, authForm.password);
      console.log("Register success:", response);
      setAuthMode('login');
      setAuthForm({ name: '', nickname: '', password: '' });
      alert('회원가입 성공! 로그인해주세요.');
    } catch (error) {
      console.error("Register error:", error);
      if (error.response && error.response.data) {
        // 백엔드에서 보내주는 에러 메시지 표시 (예: 이미 존재하는 아이디 등)
        const errorMsg = typeof error.response.data === 'object'
          ? Object.values(error.response.data).join(' ')
          : '회원가입 실패';
        setAuthError(errorMsg);
      } else {
        setAuthError('회원가입 중 오류가 발생했습니다.');
      }
    }
  };

  // 🚪 로그아웃
  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('chat_user');
    setChatSessions([]); // 기록 초기화
    setCurrentSessionId(null);
    setMessages([{ id: 1, text: "안녕하세요! 김달입니다. 연애 고민이 있으시면 편하게 말씀해주세요 💕", sender: 'bot' }]);
  };

  // 📜 채팅 세션 목록 가져오기
  const fetchChatHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/history/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setChatSessions(data);
      }
    } catch (error) {
      console.error("Failed to fetch chat history:", error);
    }
  };

  // 📜 특정 세션 불러오기
  const loadSession = async (sessionId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/history/${sessionId}/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        // 메시지 포맷 변환 (Backend: role, message -> Frontend: sender, text)
        const formattedMessages = data.map(msg => ({
          id: msg.message_id || Date.now(), // Fallback ID
          text: msg.message,
          sender: msg.role === 'user' ? 'user' : 'bot'
        }));
        setMessages(formattedMessages);
        setCurrentSessionId(sessionId);
        if (window.innerWidth <= 768) setIsSidebarOpen(false); // 모바일에서 닫기
      }
    } catch (error) {
      console.error("Failed to load session:", error);
    }
  };

  // 🆕 새 채팅 시작
  const handleNewChat = () => {
    setMessages([{ id: Date.now(), text: "새로운 상담을 시작합니다. 무엇을 도와드릴까요?", sender: 'bot' }]);
    setCurrentSessionId(null);
    if (window.innerWidth <= 768) setIsSidebarOpen(false);
  };

  // 앱 로드/로그인 시 기록 가져오기
  useEffect(() => {
    if (user) {
      fetchChatHistory();
    }
  }, [user]);

  // 🤖 말할 때 입 벙긋거리는 애니메이션
  useEffect(() => {
    let interval;
    if (isTyping) {
      interval = setInterval(() => {
        imageIndex.current = (imageIndex.current + 1) % botImages.length;
        setCurrentBotImage(botImages[imageIndex.current]);
      }, 150);
    } else {
      setCurrentBotImage(heartA);
      imageIndex.current = 0;
    }
    return () => clearInterval(interval);
  }, [isTyping]);

  // CSRF Token 가져오기 함수
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // 🚀 Django 스트리밍 API 호출 (StreamingHttpResponse)
  const callStreamingAPI = async (question, youtuberName) => {
    try {
      const csrftoken = getCookie('csrftoken');
      const response = await fetch(`${API_BASE_URL}/chat/stream/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        credentials: 'include',
        body: JSON.stringify({
          question: question,
          youtuber_name: youtuberName,
          session_id: currentSessionId // 현재 세션 ID 전송
        })
      });

      if (!response.ok) throw new Error('API 응답 오류');

      // 🆔 세션 ID 업데이트 (새로 생성된 경우)
      const newSessionId = response.headers.get('X-Chat-Session-Id');
      if (newSessionId && newSessionId !== currentSessionId) {
        setCurrentSessionId(newSessionId);
        fetchChatHistory(); // 목록 갱신
      }

      // 스트리밍 응답 처리
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText = '';
      const botMessageId = Date.now() + 1;

      // 빈 메시지 먼저 추가
      setMessages(prev => [...prev, { id: botMessageId, text: '', sender: 'bot' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        fullText += chunk;

        // 실시간으로 메시지 업데이트
        setMessages(prev => prev.map(msg =>
          msg.id === botMessageId ? { ...msg, text: fullText } : msg
        ));
      }

      setIsTyping(false);
      return fullText;
    } catch (error) {
      console.error('API 호출 실패:', error);
      // 폴백: 기본 타이핑 효과 사용
      return null;
    }
  };

  // 일반 API 호출 (폴백용)
  const callAPI = async (question, youtuberName) => {
    try {
      const csrftoken = getCookie('csrftoken');
      const response = await fetch(`${API_BASE_URL}/chat/chatting/`, { // End slash added
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        credentials: 'include', // Added credentials
        body: JSON.stringify({
          question: question,
          youtuber_name: youtuberName
        })
      });

      if (!response.ok) throw new Error('API 응답 오류');
      const data = await response.json();
      return data.answer || data.response || "응답을 받지 못했습니다.";
    } catch (error) {
      console.error('API 호출 실패:', error);
      return `[${youtuberName}] 스타일 답변:\n\n연애 고민에 대해 진심으로 들어드릴게요. 지금 말씀하신 "${question}"에 대해서 천천히 이야기해볼까요?\n\n(※ 서버 연결 확인 필요)`;
    }
  };

  const sendMessage = async () => {
    if (inputText.trim() === "") return;
    const currentInput = inputText;
    const userMessage = { id: Date.now(), text: currentInput, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInputText("");
    setIsTyping(true);

    // 스트리밍 API 시도
    const streamResult = await callStreamingAPI(currentInput, selectedCounselor.id);

    // 스트리밍 실패 시 일반 API + 타이핑 효과
    if (streamResult === null) {
      const botResponseText = await callAPI(currentInput, selectedCounselor.id);
      typeWriterEffect(botResponseText);
    }
  };

  const typeWriterEffect = (fullText) => {
    let index = 0;
    const botMessageId = Date.now() + 1;
    setMessages(prev => [...prev, { id: botMessageId, text: "", sender: 'bot' }]);
    const interval = setInterval(() => {
      if (index < fullText.length) {
        const currentText = fullText.substring(0, index + 1);
        setMessages(prev => prev.map(msg =>
          msg.id === botMessageId ? { ...msg, text: currentText } : msg
        ));
        index++;
      } else {
        clearInterval(interval);
        setIsTyping(false);
      }
    }, 30);
  };

  // 🚫 로그인 검사: 로그인하지 않은 경우 로그인 페이지만 표시
  if (!user) {
    return (
      <div className="modal-overlay" style={{ backgroundColor: '#f5f5f5', backdropFilter: 'none' }}>
        <div className="modal">
          <h2>{authMode === 'login' ? '로그인' : '회원가입'}</h2>

          <form onSubmit={authMode === 'login' ? handleLogin : handleRegister}>
            {authMode === 'register' && (
              <input
                type="text"
                placeholder="이름"
                value={authForm.name}
                onChange={(e) => setAuthForm({ ...authForm, name: e.target.value })}
              />
            )}
            <input
              type="text"
              placeholder="닉네임"
              value={authForm.nickname}
              onChange={(e) => setAuthForm({ ...authForm, nickname: e.target.value })}
            />
            <input
              type="password"
              placeholder={authMode === 'register' ? "비밀번호 (8글자 이상)" : "비밀번호"}
              value={authForm.password}
              onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
            />
            {authError && <div className="auth-error">{authError}</div>}
            <button type="submit" className="auth-submit">
              {authMode === 'login' ? '로그인' : '회원가입'}
            </button>
          </form>

          <div className="auth-switch">
            {authMode === 'login' ? (
              <span>계정이 없으신가요? <button onClick={() => setAuthMode('register')}>회원가입</button></span>
            ) : (
              <span>이미 계정이 있으신가요? <button onClick={() => setAuthMode('login')}>로그인</button></span>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="main-container">

      {/* 🍔 햄버거 토글 버튼 */}
      <div className="toggle-container">
        <button className="hamburger-btn" onClick={toggleSidebar}>☰</button>
      </div>

      {/* 👈 왼쪽 사이드바 */}
      <div className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>

        {/* 사이드바 유저 정보 */}
        {user && (
          <div className="sidebar-user">
            <div className="user-info">
              <span className="user-name">👤 {user.username}</span>
              <button className="logout-btn" onClick={handleLogout}>로그아웃</button>
            </div>
          </div>
        )}

        {/* 상담사 선택 Select */}
        <div className="sidebar-section">
          <label className="section-label">상담사 선택</label>
          <select
            className="counselor-select"
            value={selectedCounselor.id}
            onChange={handleCounselorChange}
          >
            {counselors.map((counselor) => (
              <option key={counselor.id} value={counselor.id}>
                {counselor.name}
              </option>
            ))}
          </select>
        </div>

        {/* 📜 채팅 기록 (History) */}
        <div className="sidebar-section">
          <label className="section-label">
            상담 기록
            <button className="new-chat-btn" onClick={handleNewChat} title="새 대화 시작">
              +
            </button>
          </label>
          <div className="history-list">
            {chatSessions.length === 0 ? (
              <div className="no-history">기록이 없습니다.</div>
            ) : (
              chatSessions.map((session) => (
                <div
                  key={session.session_id}
                  className={`history-item ${currentSessionId === session.session_id ? 'active' : ''}`}
                  onClick={() => loadSession(session.session_id)}
                >
                  <span className="history-date">
                    {new Date(session.created_at).toLocaleDateString()}
                  </span>
                  <span className="history-id">
                    {session.session_id.slice(0, 8)}...
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* 👉 채팅창 영역 */}
      <div className="chat-area">
        <div className="chat-header">
          <div className="header-title">연애 상담소</div>

          {/* 🔐 오른쪽 상단 인증 버튼 (로그인 상태이므로 로그아웃만 표시 or 숨김) */}
          <div className="header-auth">
            {/* 이미 사이드바에 유저 정보가 있으므로 헤더는 심플하게 유지하거나 중복 표시 */}
            <div className="user-info-header">
              <span className="user-name-header">👤 {user.username}</span>
              <button className="logout-btn-header" onClick={handleLogout}>로그아웃</button>
            </div>
          </div>
        </div>

        <div className="message-list">
          {messages.map((msg, index) => (
            <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
              {msg.sender === 'bot' && (
                <img
                  src={(isTyping && index === messages.length - 1) ? currentBotImage : heartA}
                  alt="Bot"
                  className="bot-image"
                />
              )}
              <div className={`bubble ${msg.sender}`}>{msg.text}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="input-wrapper">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder={`${selectedCounselor.name}에게 연애 상담하기...`}
              disabled={isTyping}
            />
            <button className="send-btn" onClick={sendMessage} disabled={isTyping}>
              {isTyping ? '⏳' : '➤'}
            </button>
          </div>
        </div>
      </div>

      {/* 🔐 모달 제거됨 (로그인 페이지로 대체) */}
    </div>
  );
}

export default App;
import { useState, useRef, useEffect } from 'react';

import { useLocation } from 'react-router-dom';

import axios from "axios";

import './App.css';

// 이미지 파일 
import heartA from './assets/heart_a.png';
import heartClosed from './assets/heart_closed.png';
import heartO from './assets/heart_o.png';

// 백엔드 API URL (Django)
const API_BASE_URL = 'http://localhost:8000';

function App() {
  const location = useLocation();
  
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

  // 메인페이지에서 선택된 상담사 가져오기
  const getInitialCounselor = () => {
    const selectedName = location.state?.selectedCounselor;
    if (selectedName) {
      const found = counselors.find(c => c.name === selectedName);
      return found || counselors[4];
    }
    return counselors[4]; // 기본값: 김달
  };

  // 현재 선택된 상담사
  const [selectedCounselor, setSelectedCounselor] = useState(getInitialCounselor);
  
  // 🔧 사이드바 열림/닫힘 상태
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  // 🌙 다크모드 상태
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  // 🔐 인증 상태 (Django에서 관리할 예정)
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState({ name: '', nickname: '', password: '' });
  const [authError, setAuthError] = useState('');

  // 대화 목록 - 선택된 상담사로 초기 메시지 설정
  const initialCounselor = getInitialCounselor();
  const [messages, setMessages] = useState([
    { id: 1, text: `안녕하세요! ${initialCounselor.name}입니다. 연애 고민이 있으시면 편하게 말씀해주세요 💕`, sender: 'bot' }
  ]);
  
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);  // 3초 로딩 상태
  
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

  // 🔐 로그인 (Django 연동 예정)
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
    
    // TODO: Django 로그인 API 연동
    setUser({ username: authForm.nickname });
    setShowAuthModal(false);
    setAuthForm({ name: '', nickname: '', password: '' });
  };

  // 📝 회원가입 (Django 연동 예정)
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
    
    // TODO: Django 회원가입 API 연동
    setAuthMode('login');
    setAuthForm({ name: '', nickname: '', password: '' });
    alert('회원가입 성공! 로그인해주세요.');
  };

  // 🚪 로그아웃
  const handleLogout = () => {
    setUser(null);
  };

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

  // 🚀 Django 스트리밍 API 호출 (StreamingHttpResponse)
  const callStreamingAPI = async (question, youtuberName) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/stream/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          youtuber_name: youtuberName
        })
      });

      if (!response.ok) throw new Error('API 응답 오류');
      
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
      const response = await fetch(`${API_BASE_URL}/api/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
    const res = await axios.post("http://127.0.0.1:8000/chat/stream",
        { message },
        {
        headers: {
            "Content-Type": "application/json",
        },
        }
    );
    setAnswer(res.data.answer);

    setMessages(prev => [...prev, userMessage]);
    setInputText("");
    setIsTyping(true);

    setIsLoading(true);  // 로딩 시작
    
    // 3초 후 로딩 종료
    setTimeout(() => {
      setIsLoading(false);
    }, 3000);
    



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

  return (
    <div className={`main-container ${isDarkMode ? 'dark' : ''}`}>
      
      {/* 🍔 햄버거 토글 버튼 */}
      <div className="toggle-container">
        <button className="hamburger-btn" onClick={toggleSidebar}>☰</button>
      </div>

      {/* 👈 왼쪽 사이드바 */}
      <div className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
        
        {/* 상담사 선택 리스트 */}
        <div className="sidebar-section">
          <label className="section-label">상담사 선택</label>
          <div className="counselor-list">
            {counselors.map((counselor) => (
              <div 
                key={counselor.id}
                className={`counselor-item ${selectedCounselor.id === counselor.id ? 'active' : ''}`}
                onClick={() => {
                  if (counselor.id !== selectedCounselor.id) {
                    setSelectedCounselor(counselor);
                    setIsTyping(false);
                    setMessages(prev => [...prev, { 
                      id: Date.now(), 
                      text: `💫 상담사가 ${counselor.name}(으)로 변경되었습니다. 이어서 상담해주세요!`, 
                      sender: 'bot' 
                    }]);
                    // 상담사 선택 통계 업데이트
                    fetch(`${API_BASE_URL}/chat/api/counselor-select/`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ counselor_name: counselor.name })
                    }).catch(err => console.log('통계 업데이트 실패:', err));
                  }
                }}
              >
                {counselor.name}
              </div>
            ))}
          </div>
        </div>
        

      </div>

      {/* 👉 채팅창 영역 */}
      <div className="chat-area">
        <div className="chat-header">
          <div className="header-title">연애 상담소</div>
          
          {/* 🔐 오른쪽 상단 인증 버튼 */}
          <div className="header-auth">
            {/* 🌙 다크모드 토글 스위치 */}
            <div className="dark-mode-toggle">
              <span className="toggle-label">{isDarkMode ? '🌙' : '☀️'}</span>
              <div 
                className={`toggle-switch ${isDarkMode ? 'active' : ''}`}
                onClick={() => setIsDarkMode(!isDarkMode)}
              />
            </div>
            
            {user ? (
              <div className="user-info-header">
                <span className="user-name-header">👤 {user.username}</span>
                <button className="logout-btn-header" onClick={handleLogout}>로그아웃</button>
              </div>
            ) : (
              <div className="auth-buttons">
                <button className="login-btn-header" onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}>
                  로그인
                </button>
                <button className="register-btn-header" onClick={() => { setAuthMode('register'); setShowAuthModal(true); }}>
                  회원가입
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="message-list">
          {messages.map((msg, index) => (
            <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
              {msg.sender === 'bot' && (
                <>
                  {/* 로딩 중이고 마지막 메시지이면 스피너, 아니면 캐릭터 */}
                  {(isLoading && index === messages.length - 1) ? (
                    <div className="typing-indicator">
                      <div className="loading-spinner"></div>
                    </div>
                  ) : (
                    <img 
                      src={(isTyping && index === messages.length - 1) ? currentBotImage : heartA} 
                      alt="Bot" 
                      className="bot-image" 
                    />
                  )}
                  <div className="bot-info">
                    <span className="counselor-name">{selectedCounselor.name}</span>
                    <div className={`bubble ${msg.sender}`}>{msg.text}</div>
                  </div>
                </>
              )}
              {msg.sender === 'user' && (
                <div className={`bubble ${msg.sender}`}>{msg.text}</div>
              )}
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

      {/* 🔐 로그인/회원가입 모달 */}
      {showAuthModal && (
        <div className="modal-overlay" onClick={() => setShowAuthModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowAuthModal(false)}>×</button>
            <h2>{authMode === 'login' ? '로그인' : '회원가입'}</h2>
            
            <form onSubmit={authMode === 'login' ? handleLogin : handleRegister}>
              {authMode === 'register' && (
                <input
                  type="text"
                  placeholder="이름"
                  value={authForm.name}
                  onChange={(e) => setAuthForm({...authForm, name: e.target.value})}
                />
              )}
              <input
                type="text"
                placeholder="닉네임"
                value={authForm.nickname}
                onChange={(e) => setAuthForm({...authForm, nickname: e.target.value})}
              />
              <input
                type="password"
                placeholder={authMode === 'register' ? "비밀번호 (8글자 이상)" : "비밀번호"}
                value={authForm.password}
                onChange={(e) => setAuthForm({...authForm, password: e.target.value})}
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
      )}
    </div>
  );
}

export default App;
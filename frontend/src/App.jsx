import { useState, useRef, useEffect } from 'react';
import './App.css';

// ⚠️ 이미지 파일명이 정확한지 확인하세요! (대소문자 구분함)
import heartA from './assets/heart_a.png';
import heartClosed from './assets/heart_closed.png';
import heartO from './assets/heart_o.png';

// 백엔드 API URL
const API_BASE_URL = 'http://localhost:8000';

function App() {
  // 📋 상담사 목록 (templates.py의 PERSONA_FILE_MAP과 일치)
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
  const [selectedCounselor, setSelectedCounselor] = useState(counselors[4]); // 김달

  // 대화 목록
  const [messages, setMessages] = useState([
    { id: 1, text: "안녕하세요! 김달입니다. 연애 고민이 있으시면 편하게 말씀해주세요 💕", sender: 'bot' }
  ]);
  
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  
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

  // 🔄 Select에서 상담사 선택 시 실행되는 함수
  const handleSelectChange = (e) => {
    const selected = counselors.find(c => c.id === e.target.value);
    if (selected && selected.id !== selectedCounselor.id) {
      setSelectedCounselor(selected);
      setIsTyping(false);
      
      // 대화 내용 유지하고, 상담사 변경 안내 메시지만 추가
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        text: `💫 상담사가 ${selected.name}(으)로 변경되었습니다. 이어서 상담해주세요!`, 
        sender: 'bot' 
      }]);
    }
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

  // 🚀 백엔드 RAG API 호출
  const callRAGAPI = async (question, youtuberName) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          youtuber_name: youtuberName
        })
      });

      if (!response.ok) {
        throw new Error('API 응답 오류');
      }

      const data = await response.json();
      return data.answer || data.response || "응답을 받지 못했습니다.";
    } catch (error) {
      console.error('API 호출 실패:', error);
      // API 실패 시 시뮬레이션 응답
      return `[${youtuberName}] 스타일 답변:\n\n연애 고민에 대해 진심으로 들어드릴게요. 지금 말씀하신 "${question}"에 대해서 천천히 이야기해볼까요?\n\n(※ 서버 연결 확인 필요)`;
    }
  };

  const sendMessage = async () => {
    if (inputText.trim() === "") return;

    const currentInput = inputText;
    
    // 1. 내 메시지 추가
    const userMessage = { id: Date.now(), text: currentInput, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInputText("");

    setIsTyping(true);

    // 2. RAG API 호출 (선택된 상담사 페르소나로)
    const botResponseText = await callRAGAPI(currentInput, selectedCounselor.id);
    
    // 3. 타이핑 효과로 응답 표시
    typeWriterEffect(botResponseText);
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
    }, 30); // 속도 약간 빠르게
  };

  return (
    <div className="main-container">
      
      {/* 👉 채팅창 영역 (전체 화면) */}
      <div className="chat-area">
        {/* 🔝 상단 헤더: 상담사 선택 Select */}
        <div className="chat-header">
          <div className="header-title">💕 연애 상담소</div>
          <div className="counselor-select-wrapper">
            <label htmlFor="counselor-select">상담사: </label>
            <select 
              id="counselor-select"
              value={selectedCounselor.id}
              onChange={handleSelectChange}
              className="counselor-select"
            >
              {counselors.map((counselor) => (
                <option key={counselor.id} value={counselor.id}>
                  {counselor.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 💬 메시지 리스트 */}
        <div className="message-list">
          {messages.map((msg, index) => (
            <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
              {/* 봇이고, 가장 최근 메시지이고, 타이핑 중이면 -> 움직이는 이미지 */}
              {msg.sender === 'bot' && (
                <img 
                  src={(isTyping && index === messages.length - 1) ? currentBotImage : heartA} 
                  alt="Bot" 
                  className="bot-image" 
                />
              )}
              <div className={`bubble ${msg.sender}`}>
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* ⌨️ 입력 영역 */}
        <div className="input-area">
          <input 
            type="text" 
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder={`${selectedCounselor.name}에게 연애 상담하기...`}
            disabled={isTyping}
          />
          <button onClick={sendMessage} disabled={isTyping}>
            {isTyping ? '응답 중...' : '전송'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
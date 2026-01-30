import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './MainPage.css';

// 캐릭터 이미지
import characterImg from './assets/character.png';

// 백엔드 API URL
const API_BASE_URL = 'http://43.201.89.96:8000';

function MainPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [typedText, setTypedText] = useState('');
  const sectionRef = useRef(null);

  // 타이핑할 텍스트
  const fullText = '당신의 연애 고민,\n전문 상담사가 도와드려요';

  // 상담사 목록 (왼쪽 2열 + 오른쪽 2열)
  const leftCol1 = ['권승현', '주우재', '강탱의 이야기'];
  const leftCol2 = ['연애언어TV', '김달', '랄라브루스', '준우'];
  const rightCol1 = ['박코', '모두의지인', '김유신'];
  const rightCol2 = ['오은영 박사', '홍차TV', '마튜브'];

  // 불규칙 위치 오프셋
  const offsets1 = [0, 30, 15];
  const offsets2 = [20, 0, 40, 10];
  const offsets3 = [15, 35, 5];
  const offsets4 = [0, 25, 10];

  // 타이핑 효과
  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      if (index <= fullText.length) {
        setTypedText(fullText.slice(0, index));
        index++;
      } else {
        clearInterval(interval);
      }
    }, 80);

    return () => clearInterval(interval);
  }, []);

  // 스크롤 감지
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  // 통계 데이터 가져오기
  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/api/counselor-stats/`);
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats || []);
      }
    } catch (error) {
      console.error('통계 로드 실패:', error);
    }
  };

  // 상담사 클릭 시 채팅 페이지로 이동
  const handleCounselorClick = (counselorName) => {
    fetch(`${API_BASE_URL}/chat/api/counselor-select/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ counselor_name: counselorName })
    }).catch(err => console.log('통계 업데이트 실패:', err));
    
    navigate('/chat', { state: { selectedCounselor: counselorName } });
  };

  return (
    <div className={`main-page ${isDarkMode ? 'dark' : ''}`}>
      {/* 헤더 */}
      <header className="main-header">
        <h1 className="main-title">💕 연애 상담소</h1>
        <div className="header-controls">
          <div className="dark-mode-toggle">
            <span className="toggle-label">{isDarkMode ? '🌙' : '☀️'}</span>
            <div 
              className={`toggle-switch ${isDarkMode ? 'active' : ''}`}
              onClick={() => setIsDarkMode(!isDarkMode)}
            />
          </div>
        </div>
      </header>

      {/* 스크롤 스냅 컨테이너 */}
      <div className="scroll-container">
        {/* 첫 번째 페이지: 인트로 */}
        <section className="page intro-page">
          <h2 className="typing-text">
            {typedText.split('\n').map((line, i) => (
              <span key={i}>
                {line}
                {i === 0 && <br />}
              </span>
            ))}
          </h2>
          <div className="scroll-indicator">
            <div className="scroll-arrow"></div>
          </div>
        </section>

        {/* 두 번째 페이지: 상담사 선택 */}
        <section 
          ref={sectionRef}
          className={`page counselor-page ${isVisible ? 'visible' : ''}`}
        >
          {/* 왼쪽 영역 (2열) */}
          <div className="counselor-side left">
            <div className="counselor-column">
              {leftCol1.map((name, index) => (
                <button
                  key={name}
                  className="counselor-pill"
                  style={{ 
                    marginLeft: `${offsets1[index]}px`,
                    animationDelay: `${0.3 + index * 0.12}s`
                  }}
                  onClick={() => handleCounselorClick(name)}
                >
                  {name}
                </button>
              ))}
            </div>
            <div className="counselor-column">
              {leftCol2.map((name, index) => (
                <button
                  key={name}
                  className="counselor-pill"
                  style={{ 
                    marginLeft: `${offsets2[index]}px`,
                    animationDelay: `${0.4 + index * 0.12}s`
                  }}
                  onClick={() => handleCounselorClick(name)}
                >
                  {name}
                </button>
              ))}
            </div>
          </div>

          {/* 가운데 캐릭터 */}
          <div className="character-wrapper">
            <p className="character-subtitle">13명의 상담사가 기다리고 있어요</p>
            <img src={characterImg} alt="상담사 캐릭터" className="character-image" />
            <p className="character-text">상담사를 선택해주세요!</p>
          </div>

          {/* 오른쪽 영역 (2열) */}
          <div className="counselor-side right">
            <div className="counselor-column">
              {rightCol1.map((name, index) => (
                <button
                  key={name}
                  className="counselor-pill"
                  style={{ 
                    marginRight: `${offsets3[index]}px`,
                    animationDelay: `${0.35 + index * 0.12}s`
                  }}
                  onClick={() => handleCounselorClick(name)}
                >
                  {name}
                </button>
              ))}
            </div>
            <div className="counselor-column">
              {rightCol2.map((name, index) => (
                <button
                  key={name}
                  className="counselor-pill"
                  style={{ 
                    marginRight: `${offsets4[index]}px`,
                    animationDelay: `${0.45 + index * 0.12}s`
                  }}
                  onClick={() => handleCounselorClick(name)}
                >
                  {name}
                </button>
              ))}
            </div>
          </div>
        </section>
      </div>

      {/* 푸터 */}
      <footer className="main-footer">
        <p>© 2025 연애 상담소. AI 기반 맞춤 연애 상담 서비스</p>
      </footer>
    </div>
  );
}

export default MainPage;

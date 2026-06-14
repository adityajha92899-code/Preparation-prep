import { useEffect, useMemo, useState } from 'react';

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const tabs = ['Chat', 'DSA Problems', 'Daily Plan', 'Health'];

function App() {
  const [activeTab, setActiveTab] = useState('Chat');
  const [problems, setProblems] = useState([]);
  const [plan, setPlan] = useState(null);
  const [health, setHealth] = useState(null);
  const [chatInput, setChatInput] = useState('Explain sliding window');
  const [chatResponse, setChatResponse] = useState(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${apiUrl}/dsa/problems?limit=10`)
      .then((res) => res.json())
      .then((data) => {
        if (data.success) setProblems(data.problems);
      })
      .catch(() => setError('Unable to load problems.'));

    fetch(`${apiUrl}/health`)
      .then((res) => res.json())
      .then(setHealth)
      .catch(() => setHealth({ status: 'unavailable' }));
  }, []);

  const sendChat = async () => {
    setChatLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: chatInput, user_id: 'frontend-user' }),
      });
      const data = await response.json();
      if (!data.success) throw new Error('Chat failed');
      setChatResponse(data);
    } catch (err) {
      setError('Chat request failed.');
    } finally {
      setChatLoading(false);
    }
  };

  const loadDailyPlan = async () => {
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/dsa/daily-plan?company=Google&solved_count=20`);
      const data = await response.json();
      if (!data.success) throw new Error('Failed to load plan');
      setPlan(data);
      setActiveTab('Daily Plan');
    } catch {
      setError('Unable to load daily plan.');
    }
  };

  const activeContent = useMemo(() => {
    switch (activeTab) {
      case 'DSA Problems':
        return (
          <section>
            <h2>DSA Problems</h2>
            <p>Showing the first 10 prepared problems.</p>
            <div className="card-grid">
              {problems.map((problem) => (
                <article key={problem.id} className="card">
                  <h3>{problem.id}. {problem.title}</h3>
                  <p>Difficulty: {problem.difficulty}</p>
                  <p>Patterns: {problem.patterns.join(', ')}</p>
                </article>
              ))}
            </div>
          </section>
        );
      case 'Daily Plan':
        return (
          <section>
            <h2>Daily Study Plan</h2>
            {plan ? (
              <div>
                <p>Company: {plan.target_company}</p>
                <p>Problem mix: {plan.date_problem_mix}</p>
                <ul>
                  {plan.problems.map((item) => (
                    <li key={item.id}>{item.id}. {item.title} — {item.difficulty}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <p>Click the button to load a plan.</p>
            )}
          </section>
        );
      case 'Health':
        return (
          <section>
            <h2>Service Health</h2>
            <pre>{JSON.stringify(health, null, 2)}</pre>
          </section>
        );
      default:
        return (
          <section>
            <h2>Chat with the Prep Builder</h2>
            <textarea
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              rows={5}
            />
            <button onClick={sendChat} disabled={chatLoading}>
              {chatLoading ? 'Sending...' : 'Send'}
            </button>
            {chatResponse && (
              <div className="response-card">
                <p><strong>Agent:</strong> {chatResponse.agent}</p>
                <p><strong>Model:</strong> {chatResponse.model}</p>
                <p>{chatResponse.response}</p>
                <p className="meta">Latency: {chatResponse.latency_ms} ms</p>
              </div>
            )}
          </section>
        );
    }
  }, [activeTab, chatInput, chatLoading, chatResponse, health, plan, problems]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">MAANG Prep Builder</div>
        <nav>
          {tabs.map((tab) => (
            <button
              key={tab}
              className={activeTab === tab ? 'active' : ''}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </nav>
        <div className="actions">
          <button onClick={loadDailyPlan}>Load Daily Plan</button>
        </div>
      </aside>
      <main>
        {error && <div className="error">{error}</div>}
        {activeContent}
      </main>
    </div>
  );
}

export default App;

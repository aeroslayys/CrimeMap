import { useState } from 'react';
import { LockKeyhole, MapPinned, ShieldCheck } from 'lucide-react';
import { signIn } from '../../api';
import ThemeToggle from '../../components/ThemeToggle.jsx';
import './auth.css';

export default function Login({ onLogin, onBack, theme, onToggleTheme }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [working, setWorking] = useState(false);
  const [error, setError] = useState('');

  async function submit(event) {
    event.preventDefault();
    setError('');
    setWorking(true);
    try {
      const user = await signIn(username, password);
      setPassword('');
      onLogin(user);
    } catch (reason) {
      setError(reason.message || 'Could not sign in.');
    } finally {
      setWorking(false);
    }
  }

  return <main className="auth-screen">
    <div className="auth-theme-switch"><ThemeToggle theme={theme} onToggle={onToggleTheme} /></div>
    <section className="auth-card" aria-labelledby="login-heading">
      {onBack && <button className="auth-return-overview" type="button" onClick={onBack}>← About CrimeMap</button>}
      <div className="auth-brand"><MapPinned size={27} /><strong>Crime<span>Map</span></strong></div>
      <div className="eyebrow">SYNTHETIC DEVELOPMENT WORKSPACE</div>
      <h1 id="login-heading">Sign in to CrimeMap</h1>
      <p>Use a demonstration account created by a CrimeMap administrator. Access to records and analysis depends on your assigned role.</p>
      <form onSubmit={submit} className="auth-fields">
        <label>Username
          <input type="text" autoComplete="username" autoCapitalize="none"
            minLength={3} maxLength={40} required autoFocus
            value={username} onChange={e => setUsername(e.target.value)} />
        </label>
        <label>Password
          <input type="password" autoComplete="current-password" required
            value={password} onChange={e => setPassword(e.target.value)} />
        </label>
        {error && <div className="auth-error" role="alert">{error}</div>}
        <button type="submit" className="button primary" disabled={working}>
          <LockKeyhole size={17} /> {working ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <div className="auth-footnote"><ShieldCheck size={16} />
        <span>No default account credentials. Ask your demonstration administrator for access. Local deployments initialize their own separate accounts.</span>
      </div>
    </section>
  </main>;
}

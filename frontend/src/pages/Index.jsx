import './Index.css'
import { Link, useNavigate } from 'react-router-dom'
import { Landmark, QrCode, ShieldCheck, Receipt } from 'lucide-react'

const Index = () => {
  const navigate = useNavigate()

  return (
    <div className="landing-page">
      <header className="landing-header">
        <div className="icon-titleform">
          <div className="icon">
            <Landmark />
          </div>
          <div className="title-form">LF Bank</div>
        </div>
        <div className="header-actions">
          <Link to="/login" className="btn-outline">Entrar</Link>
          <button className="btn-primary" onClick={() => navigate('/register')}>
            Criar conta
          </button>
        </div>
      </header>

      <section className="hero">
        <h1>Seu dinheiro, do jeito simples.</h1>
        <p>
          Conta digital gratuita, Pix na hora e controle total do seu extrato
          — sem taxas escondidas.
        </p>
        <button className="btn-primary btn-large" onClick={() => navigate('/register')}>
          Abrir minha conta
        </button>
      </section>

      <section className="features">
        <div className="feature-card">
          <div className="feature-icon feature-icon-teal">
            <QrCode size={20} />
          </div>
          <p className="feature-title">Pix instantâneo</p>
          <p className="feature-description">Envie e receba na hora, todos os dias.</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon feature-icon-amber">
            <ShieldCheck size={20} />
          </div>
          <p className="feature-title">Seguro por padrão</p>
          <p className="feature-description">Autenticação e criptografia em cada operação.</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon feature-icon-coral">
            <Receipt size={20} />
          </div>
          <p className="feature-title">Sem taxas</p>
          <p className="feature-description">Conta e cartão sem mensalidade.</p>
        </div>
      </section>
    </div>
  )
}

export default Index
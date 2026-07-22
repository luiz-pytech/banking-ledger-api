import './AuthForm.css'
import { userLogin } from '../api/auth'
import { Landmark, Eye, EyeOff } from 'lucide-react'
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'


const LoginForm = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

 async function handleSubmit(e) {
    e.preventDefault()

    try {
        const token = await userLogin(email, password)
        localStorage.setItem('token', token)
        navigate('/dashboard')
    } catch (error) {
        setError("Email ou senha inválidos. Por favor, tente novamente.")
    }

  }

  return (
    <div className="auth-page">
    <form className="login-form" onSubmit={handleSubmit}>
        <div className="icon-titleform">
            <div className="icon">
                <Landmark />
            </div>
            <div className="title-form">LF Bank</div>
        </div>
        <h3>Entrar</h3>
        <p>Acesse sua conta para continuar</p>
        <div className="label-input">
            <label htmlFor="email">Email</label>
            <input id="email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            type="email" 
            placeholder="Email" />
        </div>
        <div className="label-input">
            <label htmlFor="password">Senha</label>
            <div className="password-wrapper">
                <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Senha"
                />
                <button
                    type="button"
                    className="toggle-password"
                    onClick={() => setShowPassword(!showPassword)}>
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
            </div>
        </div>
        <div className="error-message">
            {error && <p>{error}</p>}
        </div>
        <button className="submit-button" type="submit">Entrar</button>
        <p className="auth-switch">
            Não tem conta? <Link to="/register">Cadastre-se</Link>
        </p>
    </form>
    </div>

  )
}

export default LoginForm
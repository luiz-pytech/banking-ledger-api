import './AuthForm.css';
import { userRegister } from '../api/auth'
import { Landmark,Eye, EyeOff } from 'lucide-react'
import { useNavigate, Link} from 'react-router-dom';
import {useState} from 'react'

const RegisterForm = () => {
  const [name, setName] = useState('');
  const [cpf, setCpf] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  async function handleSubmit(event){
    event.preventDefault();

    try {
        const data = await userRegister({name, document:cpf, email, password})
        if (data){
            navigate('/login');
        }
    } catch (error) {
        setError("Não foi possível criar a conta. Por favor, tente novamente.")
    }
  }

  return (
    <div className="auth-page">
    <form className="register-form" onSubmit={handleSubmit}>
        <div className="icon-titleform">
            <div className="icon">
                <Landmark />
            </div>
            <div className="title-form">LF Bank</div>
        </div>
        <h3>Criar Conta</h3>
        <p>Leva menos de 1 minuto</p>
        
        <div className="label-input">
            <label htmlFor="name">Nome completo</label>
            <input id="name" 
            value={name} 
            onChange={(e) => setName(e.target.value)} 
            type="text" placeholder="Nome completo" />
        </div>
        <div className="label-input">
            <label htmlFor="cpf">CPF</label>
            <input id="cpf" 
            value={cpf} 
            onChange={(e) => setCpf(e.target.value)} 
            type="text" placeholder="CPF" />
        </div>
        <div className="label-input">
            <label htmlFor="email">Email</label>
            <input id="email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            type="email" placeholder="Email" />
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
                   onClick={() => setShowPassword(!showPassword)}
                > {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
            </div>
        </div>
        <div className="error-message">
            {error && <p>{error}</p>}
        </div>
        <button className="submit-button" type="submit">Cadastrar</button>
        <p className="auth-switch">
            Já tem conta? <Link to="/login">Faça login</Link>
        </p>
    </form>
    </div>
  )
}

export default RegisterForm
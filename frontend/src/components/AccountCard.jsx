import './AccountCard.css'
import { QrCode, ArrowDown, ArrowUp } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const AccountCard = ({ typeAccount, numberAccount, balance, highlight = false }) => {
  const navigate = useNavigate()
  
  const formattedBalance = balance.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  })
  
  const typeLabel = typeAccount === 'current' ? 'Conta corrente' : 'Conta poupança'

  return (
    <div className={highlight ? 'account-card account-card-highlight' : 'account-card'}>
      <p className="account-card-label">{typeLabel} · {numberAccount}</p>
      <p className="account-card-balance">{formattedBalance}</p>

      {highlight && (
        <div className="account-card-actions">
          <button className="account-action-btn">
            <QrCode size={16} />
            <span>Pix</span>
          </button>
          <button  onClick={()=> navigate('/deposit')} className="account-action-btn">
            <ArrowDown size={16} />
            <span>Depositar</span>
          </button>
          <button onClick={()=> navigate('/withdraw')} className="account-action-btn account-action-accent">
            <ArrowUp size={16} />
            <span>Sacar</span>
          </button>
        </div>
      )}
    </div>
  )
}

export default AccountCard
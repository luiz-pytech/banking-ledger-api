import { useState } from 'react'
import './ActionsForms.css'

const formDeposit = () => {
    const [account, setAccount] = useState('')
    const [value, setValue] = useState('')

    async function handleSubmit(e) {
        e.preventDefault()

        const token = localStorage.getItem('token')
        
    }
    
}

const DepositCard = () => {
  return (
    <form className="deposit-form">
        <h3>Depositar</h3>
        <p>Adicione dinheiro à sua conta</p>

        <div className="label-input">
            <label htmlFor="account">Conta de destino</label>
            <input id="account" 
            value={account} 
            onChange={(e) => setAccount(e.target.value)} 
            type="text" 
            placeholder="Conta" />
        </div>
        <div className="label-input">
            <label htmlFor="value">Valor</label>
            <input id="value" 
            value={value} 
            onChange={(e) => setValue(e.target.value)} 
            type="text" 
            placeholder="Valor" />
        </div>

        <button type="submit" className="deposit-button">Confirmar depósito</button>
        <button type="button" className="cancel-button">Cancelar</button>
    </form>
        
  )
}

export default DepositCard
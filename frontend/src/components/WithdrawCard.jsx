import './ActionsForms.css'

const WithdrawCard = () => {
  return (
    <form className="withdraw-form">
        <h3>Sacar</h3>
        <p>Retire saldo da sua conta corrente</p>

        <div className="available-value">
            <p className="available-label">Saldo disponível</p>
            <p className="available-amount">R$ 1.000,00</p>
        </div>
        <div className="label-input">
            <label htmlFor="value">Valor</label>
            <input id="value" 
            value={value} 
            onChange={(e) => setValue(e.target.value)} 
            type="text" 
            placeholder="Valor" />
        </div>

        <button type="submit" className="withdraw-button">Confirmar saque</button>
        <button type="button" className="cancel-button">Cancelar</button>

    </form>
        
  )
}
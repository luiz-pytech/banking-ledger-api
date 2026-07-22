import './TransactionList.css'
import { ArrowDownLeft, ShoppingCart } from 'lucide-react'

const TransactionList = ({ transactions }) => {
  return (
    <div className="transaction-list-card">
      <p className="transaction-list-title">Extrato recente</p>

      <div className="transaction-list">
        {transactions.map((transaction) => (
          <TransactionRow key={transaction.id} transaction={transaction} />
        ))}
      </div>
    </div>
  )
}

const TransactionRow = ({ transaction }) => {
  const isCredit = transaction.type === 'credit'
  const formattedValue = transaction.value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  })

  return (
    <div className="transaction-row">
      <div className="transaction-row-left">
        <div className={isCredit ? 'transaction-icon transaction-icon-credit' : 'transaction-icon transaction-icon-debit'}>
          {isCredit ? <ArrowDownLeft size={16} /> : <ShoppingCart size={16} />}
        </div>
        <span>{transaction.description}</span>
      </div>
      <span className={isCredit ? 'transaction-value transaction-value-credit' : 'transaction-value'}>
        {isCredit ? '+' : '-'}{formattedValue}
      </span>
    </div>
  )
}

export default TransactionList
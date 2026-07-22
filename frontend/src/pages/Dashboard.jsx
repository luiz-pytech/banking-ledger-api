import './Dashboard.css'
import Sidebar from '../components/Sidebar'
import AccountCard from '../components/AccountCard'
import TransactionList from '../components/TransactionList'

// Dados fixos por enquanto -- na E11 isso vira useEffect + chamada à API.
const MOCK_ACCOUNTS = [
  { id: '1', typeAccount: 'current', numberAccount: '000123', balance: 1284.5 },
  { id: '2', typeAccount: 'savings', numberAccount: '000124', balance: 3920.0 },
]

const MOCK_TRANSACTIONS = [
  { id: 't1', type: 'credit', description: 'Pix recebido — João Silva', value: 150.0 },
  { id: 't2', type: 'debit', description: 'Pix enviado — Mercado Bom Preço', value: 42.9 },
  { id: 't3', type: 'credit', description: 'Depósito', value: 500.0 },
]

const Dashboard = () => {
  return (
    <div className="dashboard-layout">
      <Sidebar />

      <main className="dashboard-content">
        <div className="dashboard-header">
          <div>
            <p className="dashboard-greeting-label">Olá,</p>
            <p className="dashboard-greeting-name">Luiz</p>
          </div>
          <div className="dashboard-avatar">LF</div>
        </div>

        <div className="dashboard-accounts">
          <AccountCard
            typeAccount={MOCK_ACCOUNTS[0].typeAccount}
            numberAccount={MOCK_ACCOUNTS[0].numberAccount}
            balance={MOCK_ACCOUNTS[0].balance}
            highlight
          />
          <AccountCard
            typeAccount={MOCK_ACCOUNTS[1].typeAccount}
            numberAccount={MOCK_ACCOUNTS[1].numberAccount}
            balance={MOCK_ACCOUNTS[1].balance}
          />
        </div>

        <TransactionList transactions={MOCK_TRANSACTIONS} />
      </main>
    </div>
  )
}

export default Dashboard
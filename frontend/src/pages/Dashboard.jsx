import './Dashboard.css'
import Sidebar from '../components/Sidebar'
import AccountCard from '../components/AccountCard'
import TransactionList from '../components/TransactionList'
import { useState, useEffect } from 'react'
import { getAccounts, getAccountBalance } from '../api/accounts'
import { getUser, getFirstName, getFirstLetters} from '../api/users'

const MOCK_TRANSACTIONS = [
  { id: 't1', type: 'credit', description: 'Pix recebido — João Silva', value: 150.0 },
  { id: 't2', type: 'debit', description: 'Pix enviado — Mercado Bom Preço', value: 42.9 },
  { id: 't3', type: 'credit', description: 'Depósito', value: 500.0 },
]


const Dashboard = () => {
  const [nameUser, setnameUser] = useState('')
  const [profileLetters, setProfileLetters] = useState('')
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  

  useEffect(() => {
    async function fetchUserData(){
      try {
        const token = localStorage.getItem('token')
        const userData = await getUser(token)
        const firstName = getFirstName(userData)
        const profileLetters = getFirstLetters(userData)

        setProfileLetters(profileLetters)
        setnameUser(firstName)
      } catch (error) {
        setError('Erro ao buscar dados do usuário')
      }
    }
    async function fetchAccountsWithBalance() {
      try {
        const token = localStorage.getItem('token')
        const accountsData = await getAccounts(token)

        const balancesData = await Promise.all(
          accountsData.map((account) => getAccountBalance(token, account.id))
        )

        const accountsWithBalance = accountsData.map((account, index) => ({
          ...account,
          balance: balancesData[index].balance,
        }))

        setAccounts(accountsWithBalance)

      } catch (error) {
        setError('Erro ao buscar contas e saldos:')
      } finally {
        setLoading(false)
      }
    }
    
    fetchUserData()
    fetchAccountsWithBalance()
  }, [])
  
  if (loading) {
    return <p>Carregando...</p>
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />

      <main className="dashboard-content">
        <div className="dashboard-header">
          <div>
            <p className="dashboard-greeting-label">Olá,</p>
            <p className="dashboard-greeting-name">{nameUser}</p>
          </div>
          <div className="dashboard-avatar">{profileLetters}</div>
        </div>

        {error && <p>{error}</p>}

         <div className="dashboard-accounts">
          {accounts.map((account, index) => (
            <AccountCard
              key={account.id}
              typeAccount={account.type_account}
              numberAccount={account.number_account}
              balance={account.balance}
              highlight={index === 0}
            />
          ))}
        </div>

        <TransactionList transactions={MOCK_TRANSACTIONS} />
      </main>
    </div>
  )
}

export default Dashboard
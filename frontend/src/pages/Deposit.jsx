import Sidebar from "../components/Sidebar"
import DepositCard from "../components/DepositCard"
import './ActionsPages.css'

const Deposit = () => {
  return (
    <div className="deposit-layout">
      <Sidebar />

      <main className="deposit-content">
        <DepositCard />
      </main>
    </div>
  )
}

export default Deposit
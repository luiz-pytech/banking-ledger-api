import Sidebar from "../components/Sidebar"
import WithdrawCard from "../components/WithdrawCard"
import './ActionsPages.css'

const Withdraw = () => {
  return (
    <div className="withdraw-layout">
      <Sidebar />

      <main className="withdraw-content">
        <WithdrawCard />
      </main>
    </div>
  )
}

export default Withdraw
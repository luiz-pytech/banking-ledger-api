import './Sidebar.css'
import { Link, useLocation } from 'react-router-dom'
import { Landmark, Home, FileText, Key, CreditCard, Settings } from 'lucide-react'

const NAV_ITEMS = [
  { label: 'Início', path: '/dashboard', icon: Home },
  { label: 'Extrato', path: '/statement', icon: FileText },
  { label: 'Chaves Pix', path: '/pix-keys', icon: Key },
  { label: 'Contas', path: '/accounts', icon: CreditCard },
]

const Sidebar = () => {
  const location = useLocation()

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <Landmark size={20} />
        <span>lf_bank</span>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={isActive ? 'sidebar-link sidebar-link-active' : 'sidebar-link'}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="sidebar-footer">
        <Link to="/settings" className="sidebar-link">
          <Settings size={18} />
          <span>Configurações</span>
        </Link>
      </div>
    </aside>
  )
}

export default Sidebar
import { Routes, Route } from "react-router-dom";

import Login from './pages/Login'  
import Register from './pages/Register'
import Index from './pages/Index'
import Dashboard from './pages/Dashboard'
import Deposit from './pages/Deposit'
import Withdraw from './pages/Withdraw'

import PrivateRoute from './components/PrivateRoute'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Index />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/deposit"
        element={
          <PrivateRoute>
            <Deposit />
          </PrivateRoute>
        }
      />
      <Route
        path="/withdraw"
        element={
          <PrivateRoute>
            <Withdraw />
          </PrivateRoute>
        }
      />
    </Routes>
  )
}

export default App;
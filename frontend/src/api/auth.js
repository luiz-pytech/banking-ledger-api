const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export async function userLogin(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    throw new Error('Credenciais inválidas.')
  }

  const data = await response.json()
  return data.access_token
}

export async function userRegister({ name, document, email, password }) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, document, email, password }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => null)
    throw new Error(errorData?.detail || 'Não foi possível criar a conta.')
  }

  return response.json()
}
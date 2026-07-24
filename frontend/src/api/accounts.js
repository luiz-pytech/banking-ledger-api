const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export async function getAccounts(token) {
  const response = await fetch(`${API_BASE_URL}/accounts/`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    throw new Error('Não foi possível carregar suas contas.')
  }
  return response.json()
}

export async function getDestinationNumberAccount(token, number_account){
  await fetch(`${API_BASE_URL}/accounts/${number_account}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    throw new Error('Conta não encontrada para realizar deposito')
  }
  return response.json()
}

export async function getAccountBalance(token, accountId) {
  const response = await fetch(`${API_BASE_URL}/accounts/${accountId}/balance`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    throw new Error('Não foi possível carregar o saldo.')
  }
  return response.json()
}

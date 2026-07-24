const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export async function getUser(token){
    const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
    })

    if (!response.ok){
       throw new Error("Não foi possível carregar seus dados")
    }

    return response.json()

}

export function getFirstName(response){
    const firstName = response.name.split(' ')[0].toUpperCase()
    return firstName
}

export function getFirstLetters(response){
    const firstLetters = response.name.split(' ').slice(0, 2).map(word => word[0]).join('').toUpperCase()
    return firstLetters
}
import { create } from 'zustand'

interface User {
  id: string
  email: string
  full_name: string
  picture_url: string | null
  is_admin: boolean
}

interface AuthState {
  user: User | null
  loading: boolean
  fetchUser: () => Promise<void>
  clear: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,

  fetchUser: async () => {
    set({ loading: true })
    try {
      const res = await fetch('/api/users/me', { credentials: 'include' })
      if (!res.ok) {
        set({ user: null })
        return
      }
      const data = await res.json()
      set({ user: data.user })
    } finally {
      set({ loading: false })
    }
  },

  clear: () => set({ user: null }),
}))

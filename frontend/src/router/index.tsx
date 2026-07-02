import { createBrowserRouter } from 'react-router-dom'
import App from '@/App'
import HomeView from '@/views/HomeView'
import LoginView from '@/views/LoginView'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <HomeView /> },
      { path: 'login', element: <LoginView /> },
    ],
  },
])


import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../services/auth'

function Login() {
  const navigate = useNavigate()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    setError("")
    setSuccess("")

    if (!email.trim() || !password) {
      setError("Please enter both email and password.")
      return
    }

    setLoading(true)

    try {
      const user = await login(email, password)

      console.log("Authenticated user:", user)

      setSuccess("Login successful. User profile loaded.")
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>SMART CAMPUS</h1>

      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
      />

      <br />

      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
      />

      <br />

      <button onClick={handleLogin} disabled={loading}>
        {loading ? "Logging in..." : "Login"}
      </button>

      {error && <p role="alert">{error}</p>}
      {success && <p role="status">{success}</p>}

      <p>Forgot Password?</p>
    </div>
  )
}

export default Login

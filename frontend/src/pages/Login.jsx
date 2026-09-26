import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {login} from '../services/auth'

function Login() {

  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword]= useState("")
  const [error, setError]=useState("")
  const [loading,setLoading]=useState(false)

  const handleLogin= async()=>{
    setLoading(true)
    try{
      const data=await login(email,password)
      console.log(data)
    }
    catch(error){
      setError(error.message)
    }
    finally{
      setLoading(false)
    }
  }
  return (
    <div>
      <h1>SMART CAMPUS</h1>

      <label>Email</label>
      <input
      type="email"
      value={email}
      onChange={(event)=> setEmail(event.target.value)}
      />

      <br/>

      <label>Password</label>
      <input
      type="password"
      value={password}
      onChange={(event)=> setPassword(event.target.value)}
      />

      <br/>

      <button onClick={handleLogin}>
        {loading? "Logging in...":"Login"}
      </button>

      {error && <p>{error}</p>}

      <p>
        Forgot Password?
      </p>
    </div>
  )
}
export default Login
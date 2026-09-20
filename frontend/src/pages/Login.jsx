import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {login} from '../services/auth'

function Login() {

  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword]= useState("")

  const handleLogin= async()=>{
    try{
      const data=await login(email,password)
      console.log(data)
    }
    catch(error){

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

      <button onClick={handleLogin}>Login</button>
      
      <p>
        Forgot Password?
      </p>
    </div>
  )
}
export default Login
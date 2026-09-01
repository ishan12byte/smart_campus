import { useNavigate } from 'react-router-dom'
function Login() {
  const navigate = useNavigate()
  return (
    <div>
      <h1>SMART CAMPUS</h1>

      <label>Email</label>
      <input type="email" />

      <br/>

      <label>Password</label>
      <input type="password" />

      <br/>

      <button onClick={()=>navigate("/student")}>Login</button>
      
      <p>
        Forgot Password?
      </p>
    </div>
  )
}
export default Login
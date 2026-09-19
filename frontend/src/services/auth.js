import {apiRequest} from "./api";
export async function login(email,password){
    const data=await apiRequest("/auth/login,{
        method:"POST",
        
    )
}
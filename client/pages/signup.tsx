import { Inter } from 'next/font/google'
import useSWR from 'swr'
import * as React from 'react';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import Link from '@mui/material/Link';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { createTheme, ThemeProvider } from '@mui/material/styles'; 
import axios from 'axios';
import { useRouter } from 'next/router'
import { useAuth } from '@/components/AuthProvider';

const inter = Inter({ subsets: ['latin'] })

interface UserData {
  firstName : string, 
  lastName : string,
  username: string, 
  email : string, 
  password : string, 
  confirmedassword : string  
}
  
// TODO remove, this demo shouldn't need to reset the theme.
  const defaultTheme = createTheme({
    palette: {
        mode: 'light',
      },
  });
  
  export default function SignIn() {
    const router = useRouter();  
    const {isAuthenticated} = useAuth(); 

    const [isValidFirstName, setIsValidFirstName] = React.useState(true); 
    const [firstName, setFirstName] = React.useState(""); 

    const [isValidLastName, setIsValidLastName] = React.useState(true); 
    const [lastName, setLastName] = React.useState(""); 

    const [isValidEmail, setIsValidEmail] = React.useState(true); 
    const [email, setEmail] = React.useState(""); 

    const [isValidPassword, setIsValidPassword] = React.useState(true); 
    const [password, setPassword] = React.useState(""); 
    
    const [isValidConfrimedPassword, setIsValidConfirmedPassword] = React.useState(true); 
    const [confirmedPassword, setConfirmedPassword] = React.useState(""); 

    const [showStatus, setShowStatus] = React.useState(false); 
    const [isGood, setIsGood] = React.useState(true); 


    const onChangeFirstName = (event : React.ChangeEvent<HTMLInputElement>) => {
      const firstName = event.currentTarget.value 
      const isValid = firstName.length > 0 
      setFirstName(firstName);
      setIsValidFirstName(isValid); 
    } 

    const onChangeLastName = (event : React.ChangeEvent<HTMLInputElement>) => {
      const lastName = event.currentTarget.value 
      const isValid = lastName.length > 0 
      setLastName(lastName);
      setIsValidLastName(isValid); 
    } 

    const onChangeEmail = (event : React.ChangeEvent<HTMLInputElement>) => {
      const email = event.currentTarget.value 
      const isValid = email.length > 0 && validateEmail(email) 
      setEmail(email);
      setIsValidEmail(isValid); 
    }

  const onChangePassword = (event : React.ChangeEvent<HTMLInputElement>) => {
    const password = event.currentTarget.value 
    const isValid = password.length > 0 
    setPassword(password); 
    setIsValidPassword(isValid); 
  } 

  const onChangeConfirmedPassword = (event : React.ChangeEvent<HTMLInputElement>) => {
    const confirmedPassword = event.currentTarget.value 
    const isValid = confirmedPassword.length > 0 && password === confirmedPassword
    setConfirmedPassword(confirmedPassword); 
    setIsValidConfirmedPassword(isValid); 
  } 


    const validateEmail = (email : string) => {
      let res = /\S+@\S+\.\S+/;
      return res.test(email);
    }
  

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
    
      const formData = new FormData();
      formData.append("firstName", firstName);
      formData.append("lastName", lastName);
      formData.append("email", email);
      formData.append("password", password);
      formData.append("confirmedPassword", confirmedPassword);
    
      try {
        const response = await axios.post('/api/auth/register', formData);
        setShowStatus(true); 
        if (response.status === 201) {
          setIsGood(true); 
          router.push("/");
        }
        else {
          setIsGood(false); 
          alert("Registration failed: " + response.data.msg);
        }
      } catch (error) {
        setShowStatus(true); 
        setIsGood(false); 
      }
    };
  
    return (
        <Container component="main" maxWidth="xs">
          <CssBaseline />
          <Box
            sx={{
              marginTop: 8,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <Typography component="h1" variant="h5">
              Sign up
            </Typography>
            <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="firstname"
                label="First Name"
                name="firstname" 
                autoFocus
                onChange={onChangeFirstName}
                error={!isValidFirstName}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                id="lastname"
                label="Last Name"
                name="lastname" 
                autoFocus
                onChange={onChangeLastName}
                error={!isValidLastName}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="email"
                label="Email"
                type="email"
                id="email"
                autoComplete="current-email"
                onChange={onChangeEmail}
                error={!isValidEmail}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                onChange={onChangePassword}
                error={!isValidPassword}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Confirm Password"
                type="password"
                id="confirm-password"
                autoComplete="confirm-normal-password"
                onChange={onChangeConfirmedPassword}
                error={!isValidConfrimedPassword}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
              >
                Sign up
              </Button>
              <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            className="text-center"
            component="div"
          >
            {
              showStatus &&
              <div>
                  <Typography style={{color : isGood ? " #32612D" : "#cc0000"}}>{isGood ? "Account Created" : "Failed creating account"}</Typography>
                </div>
            }
          </Box> 
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                class="text-center"
              >
                <Link href="/login" variant="body2">
                  {"Already have an account? Login"}
                </Link>
              </Box>
            </Box>
          </Box>
        </Container>
    );
  }
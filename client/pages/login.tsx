import { Inter } from "next/font/google";
import useSWR from "swr";
import * as React from "react";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import TextField from "@mui/material/TextField";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";
import Link from "@mui/material/Link";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { useAuth } from "@/components/AuthProvider";
import { useRouter } from "next/router";


export default function SignIn() {
  const { login, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [isValidEmail, setIsValidEmail] = React.useState(true);
  const [email, setEmail] = React.useState("");

  const [isValidPassword, setIsValidPassword] = React.useState(true);
  const [password, setPassword] = React.useState("");

  const [showStatus, setShowStatus] = React.useState(false); 
  const [isGood, setIsGood] = React.useState(true); 

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (email.length <= 0 || password.length <= 0) {
      setIsValidEmail(email.length > 0);
      setIsValidPassword(password.length > 0);
      return;
    }

    login(email, password).then(result => {
      setShowStatus(true); 
      if(result) {
        setIsGood(true); 
        setTimeout(() => {
          router.push("/");
        }, 4000)
      }

      else {
        setIsGood(false); 
      }
    });
  };

  const onChangeEmail = (event: React.ChangeEvent<HTMLInputElement>) => {
    const email = event.currentTarget.value;
    const isValid = email.length > 0;
    setEmail(email);
    setIsValidEmail(isValid);
  };

  const onChangePassword = (event: React.ChangeEvent<HTMLInputElement>) => {
    const password = event.currentTarget.value;
    const isValid = password.length > 0;
    setPassword(password);
    setIsValidPassword(isValid);
  };

  if (!isLoading && isAuthenticated) {
    router.push("/");
  }

  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <Box
        sx={{
          marginTop: 8,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <Typography component="h1" variant="h5">
          Sign in
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email"
            name="email"
            autoComplete="email"
            onChange={onChangeEmail}
            autoFocus
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
          <FormControlLabel
            control={<Checkbox value="remember" color="primary" />}
            label="Remember me"
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            Log In
          </Button>
          <Box
            display="flex"
            flexDirection="column"
            gap={2}
            justifyContent="center"
            alignItems="center"
            className="text-center"
            component="div"
          >
            {
              showStatus &&
              <div>
                  <Typography style={{color : isGood ? " #32612D" : "#cc0000"}}>{isGood ? "Login in Successful" : "Login in not Successful"}</Typography>
                </div>
            }
          </Box> 
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            className="text-center"
            component="div"
          >
            <Link href="/signup" variant="body2">
              {"Don't have an account? Sign Up"}
            </Link>
            <Link href="/password-reset" variant="body2">
              {"Forgot Password?"}
            </Link>
          </Box>
        </Box>
      </Box>
    </Container>
  );
}

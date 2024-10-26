import { useRouter } from 'next/router'
import { useState } from 'react';
import { Typography, Box, TextField, Button, Container } from '@mui/material'
import { useAuth } from "@/components/AuthProvider";

const resetPwRoute = "/api/emails/resetpassword";

const PasswordResetForm = () => {
    const [isValidEmail, setIsValidEmail] = useState(false);
    const [email, setEmail] = useState("");
    const { getCsrfToken } = useAuth();

    const onChangeEmail = (event: React.ChangeEvent<HTMLInputElement>) => {
        setEmail(event.currentTarget.value);
        setIsValidEmail(email.length > 0);
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const res = await fetch(resetPwRoute, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCsrfToken() || ''
            },
            body: JSON.stringify({ recipient: email })
        });
        if (res.ok) {
            alert("Follow the link in your email. You can now close this tab.")
        }
    };

    return (
        <Container component="main" maxWidth="xs" sx={{ marginTop: 10 }}>
            <Typography component="h1" variant="h5">
                Change Password
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
                    error={!isValidEmail}
                />
                <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    sx={{ mt: 3, mb: 2 }}
                >
                    Submit
                </Button>
            </Box>
        </Container>
    )
}

export default PasswordResetForm;
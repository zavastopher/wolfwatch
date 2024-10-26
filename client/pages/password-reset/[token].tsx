import { useRouter } from 'next/router'
import React, { useState } from 'react';
import { Typography, Box, TextField, Button, Container } from '@mui/material'
import { useAuth } from "@/components/AuthProvider";

const resetPwRoute = "/api/emails/resetpassword";

const ChangePasswordForm = () => {
    const router = useRouter();
    const { token } = router.query;

    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const { getCsrfToken } = useAuth();

    const onChangePassword = (event: React.ChangeEvent<HTMLInputElement>) => {
        setPassword(event.currentTarget.value);
    };

    const onChangeConfirmPassword = (event: React.ChangeEvent<HTMLInputElement>) => {
        setConfirmPassword(event.currentTarget.value);
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        if (password.length < 8 || password !== confirmPassword) {
            alert("Password must be at least 8 characters long and match the confirmation password");
            return;
        }

        const res = await fetch(resetPwRoute, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCsrfToken() || ''
            },
            body: JSON.stringify({
                "newPassword": password,
                "confirmedNewPassword": confirmPassword,
                "resetToken": token
            })
        });
        if (res.ok) {
            alert("Password changed successfully");
            router.push("/login");
        }
    };

    return (
        <Container component="main" maxWidth="xs" sx={{ mt: 8 }}>
            <Typography component="h1" variant="h5">
                Change Password
            </Typography>
            <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
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
                />
                <TextField
                    margin="normal"
                    required
                    fullWidth
                    name="confirmPassword"
                    label="Confirm Password"
                    type="password"
                    id="password"
                    onChange={onChangeConfirmPassword}
                />
                <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    sx={{ mt: 3, mb: 2 }}
                >
                    Change Password
                </Button>
            </Box>
        </Container>
    )
}

export default ChangePasswordForm;
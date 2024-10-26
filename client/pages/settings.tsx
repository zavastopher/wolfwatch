import { Inter } from 'next/font/google'
import * as React from 'react';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Header from '@/components/Header';
import { FormControlLabel, FormLabel, Radio, RadioGroup } from '@mui/material';
import { useEffect, useState } from 'react';
import Layout from '../components/DefaultLayout'
import { useAuth } from '@/components/AuthProvider';

const inter = Inter({ subsets: ['latin'] })

type Instructor = {
  firstName: string,
  lastName: string,
  email: string,
  notificationFrequency: Frequency,
  lastLogin: Date
}

type Frequency = "DAILY" | "WEEKLY" | "MONTHLY";

export default function Signup() {
  const [isValidFirstName, setIsValidFirstName] = useState(true);
  const [firstName, setFirstName] = useState('');

  const [isValidLastName, setIsValidLastName] = useState(true);
  const [lastName, setLastName] = useState('');

  const [isValidEmail, setIsValidEmail] = useState(true);
  const [email, setEmail] = useState('');

  const [frequency, setFrequency] = useState<Frequency>("WEEKLY");

  //fetch instructor and populate fields
  const { getCsrfToken } = useAuth();
  useEffect(() => {
    const fetchInstructor = async () => {
      try {
        const response = await fetch('/api/instructor', {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': getCsrfToken() || ''
          },
        });
        if (response.ok) {
          const instructor: Instructor = await response.json();
          setFirstName(instructor.firstName);
          setLastName(instructor.lastName);
          setEmail(instructor.email);
          setFrequency(instructor.notificationFrequency);
        } else {
        }
      } catch (error) {
      }
    };
    fetchInstructor();
  }, [getCsrfToken]);
  const onChangeFirstName = (event: React.ChangeEvent<HTMLInputElement>) => {
    const firstName = event.currentTarget.value
    const isValid = firstName.length > 0
    setFirstName(firstName);
    setIsValidFirstName(isValid);
  }

  const onChangeLastName = (event: React.ChangeEvent<HTMLInputElement>) => {
    const lastName = event.currentTarget.value
    const isValid = lastName.length > 0
    setLastName(lastName);
    setIsValidLastName(isValid);
  }

  const onChangeEmail = (event: React.ChangeEvent<HTMLInputElement>) => {
    const email = event.currentTarget.value
    const isValid = email.length > 0 && validateEmail(email)
    setEmail(email);
    setIsValidEmail(isValid);
  }

  const validateEmail = (email: string) => {
    let res = /\S+@\S+\.\S+/;
    return res.test(email);
  }

  const handleFreqChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFrequency((event.target as HTMLInputElement).value as Frequency);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (firstName.length <= 0 || lastName.length <= 0 || email.length <= 0 || !validateEmail(email) || !frequency) {
      setIsValidFirstName(firstName.length > 0)
      setIsValidLastName(lastName.length > 0)
      setIsValidEmail(email.length > 0 && validateEmail(email))
    } else { //submit changes
      const putInstructor = async () => {
        try {
          const response = await fetch('/api/instructor/edit', {
            method: 'PUT',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRF-TOKEN': getCsrfToken() || ''
            },
            body: JSON.stringify({
              firstName: firstName,
              lastName: lastName,
              email: email,
              notificationFrequency: frequency
            })
          });

          if (response.ok) {
            alert('Update successful!')
          } else {
            throw new Error();
          }
        } catch (error) {
          alert('Failed to update :(')
        }
      };
      putInstructor();
    }
  };

  return (
    <Layout>
      <Box
        component="main"
        sx={{
          margin: '5% auto',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          maxWidth: '40%',
        }}
      >
        <Typography component="h1" variant="h5">
          Settings
        </Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="firstname"
            label="First Name"
            name="firstname"
            value={firstName}
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
            value={lastName}
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
            value={email}
            onChange={onChangeEmail}
            error={!isValidEmail}
          />
          <FormLabel>Scan Frequency</FormLabel>
          <RadioGroup onChange={handleFreqChange} value={frequency}>
            <FormControlLabel value="DAILY" control={<Radio />} label="Daily" />
            <FormControlLabel value="WEEKLY" control={<Radio />} label="Weekly" />
            <FormControlLabel value="MONTHLY" control={<Radio />} label="Monthly" />
          </RadioGroup>
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            Update
          </Button>
        </Box>
      </Box>
    </Layout>
  );
}

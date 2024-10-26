import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { SWRConfig } from 'swr'
import fetcher from './api'
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import AuthProvider from "@/components/AuthProvider";
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#cc2000',
    },
    secondary: {
      main: '#f50057',
    },
  },
});


export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider theme={theme}> 
      <AuthProvider> 
      <SWRConfig value={{
      fetcher,
    }}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <Component {...pageProps} />
      </LocalizationProvider>
    </SWRConfig>
    </AuthProvider> 
    </ThemeProvider>
  )
}

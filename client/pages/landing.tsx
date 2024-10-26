import * as React from "react";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import Grid from "@mui/material/Grid";

export default function Landing() {
    return (
        <Grid container component="main" sx={{height: '100vh'}}>
            <CssBaseline/>
            <Grid
                item 
                xs={false}
                sm={4}
                md={7}
                sx={{
                    bgcolor: '#CC0000',
                    display: 'flex',
                    flexDirection: "column",                    
                    justifyContent: 'center',
                    alignContent: 'center'
                }}
            >
                <h1 style={{justifySelf: 'center', alignSelf: 'center', fontSize: '5em'}}>Wolf<a style={{ color: '#ffffff'}}>Watch</a></h1>
                <img 
                    src="wolfshilloutte.png"
                    alt="wolfshilloutte"
                    style={{  height: 'auto', maxWidth: '70%', alignSelf: 'center' }}
                />

            </Grid>

            <Grid item xs={12} sm={8} md={5} elevation={6} square
            sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                alignContent: 'center',
                justifyContent: 'center',
                height: '100vh'
            }}
            >
                <Button type="button" variant="contained" 
                   fullwidth size="large" href="/signup" sx={{ mt: 3, mb: 2, width: 3/4, height: 1/15, fontSize: '1em'}}>
                        Sign Up
                </Button>
                <Button type="button" variant="contained" 
                    fullwidth size="large" href="/login" sx={{ mt: 3, mb: 2, width: 3/4, height: 1/15, fontSize: '1em'}}>
                        Login
                </Button>
            </Grid>
        </Grid>

    );
}

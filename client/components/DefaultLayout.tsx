import { useAuth } from "./AuthProvider";
import Header from "./Header";
import { CircularProgress } from "@mui/material";
import { useEffect } from "react";
import { useRouter } from "next/router";
import Router from "next/router";

//TODO - make the naming of this file and function more specific if needed
export default function Layout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  // Checking auth state
  if (isLoading) {
    return (
      <>
        <Header />
        <CircularProgress
          color="error"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            marginTop: "-20px",
            marginLeft: "-20px",
          }}
        />
      </>
    );
  }

  // Not authenticated, redirect to login
  if (!isAuthenticated && !isLoading) {
    Router.push("/");
    return null;
  }

  // Authenticated, show page
  return (
    <>
      <Header />
      {children}
    </>
  );
}

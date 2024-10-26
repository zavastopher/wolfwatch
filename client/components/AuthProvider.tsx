import React, { useState, useEffect, useContext } from 'react';

type Identity = {
    firstName: string,
    lastName: string,
}

type AuthContextType = {
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<boolean>;
    logout: () => Promise<void>;
    getCsrfToken: () => string | undefined;
    identity: Identity | undefined;
};

// Provides a context for authentication state & functions
const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

// Utility function to get a cookie by name
function getCookieValue(name: string): string | undefined {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(';').shift();
}

/**
 * AuthProvider is a React component that wraps its children with an authentication context.
 * 
 * Props:
 * - children: Components that will have access to the authentication context
 */
const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState(true);
    const [identity, setIdentity] = useState<Identity>();

    const login = async (email: string, password: string) => {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (response.status === 200) {
                setIsAuthenticated(true);
                const identity = await response.json();
                setIdentity(identity);
                return true;
            } else {
                alert("Error during login: " + response.status);
                return false;
            }
        } catch (error) {
            alert("Error during login: " + error.response.data.msg);
        }
    };

    const logout = async () => {
        try {
            const csrfToken = getCookieValue('csrf_access_token');

            const response = await fetch('/api/auth/logout', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrfToken || ''
                }
            });
            if (response.ok) {
                setIsAuthenticated(false);
            } else {
                // Handle error
            }
        } catch (error) {
            console.error("Error during logout:", error);
        }
    };

    const getCsrfToken = () => {
        return getCookieValue('csrf_access_token');
    };

    // On mount, check if user is authenticated
    // also check on children change
    useEffect(() => {
        const checkAuthStatus = async () => {
            try {
                setIsLoading(true);
                const response = await fetch('/api/auth/status', {
                    method: 'GET',
                    credentials: 'include'
                });

                if (response.ok) {
                    setIsAuthenticated(true);
                    const identity = await response.json();
                    setIdentity(identity);
                } else {
                    setIsAuthenticated(false);
                }
                setIsLoading(false);
            } catch (error) {
                console.error("Error checking authentication status:", error);
            }
        };

        checkAuthStatus();
    }, []);

    return (
        <AuthContext.Provider value={{ isAuthenticated, isLoading, login, logout, getCsrfToken, identity }}>
            {children}
        </AuthContext.Provider>
    );
};

// Custom hook for easy way to access authentication context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};

export default AuthProvider;

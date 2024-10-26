import { useAuth } from "@/components/AuthProvider";
import Dashboard from "./dashboard";
import Landing from "./landing";

export default function Home() {
  const { isAuthenticated } = useAuth();

  return isAuthenticated ? <Dashboard /> : <Landing />;
}

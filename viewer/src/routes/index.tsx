import { useRoutes } from "react-router-dom";
import Dashboard from "@/features/Dashboard";

export const AppRoutes = () => {
    const element = useRoutes([{ path: "/", element: <Dashboard /> }]);

    return <>{element}</>;
};

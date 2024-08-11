import * as React from "react";
import { PropsWithChildren } from "react";
import { ErrorBoundary } from "react-error-boundary";
import { BrowserRouter as Router } from "react-router-dom";
import Theme from "./Theme";

function ErrorFallback() {
    return (
        <div
            className="text-red-500 w-screen h-screen flex flex-col justify-center items-center"
            role="alert">
            <h2 className="text-lg font-semibold">
                Ooops, something went wrong :({" "}
            </h2>
            <button
                className="mt-4"
                onClick={() => window.location.assign(window.location.origin)}>
                Refresh
            </button>
        </div>
    );
}

export default function AppProvider({ children }: PropsWithChildren) {
    const loadFallback = (
        <div className="flex items-center justify-center w-screen h-screen">
            pending...
        </div>
    );
    return (
        <React.Suspense fallback={loadFallback}>
            <ErrorBoundary FallbackComponent={ErrorFallback}>
                <Theme.Provider>
                    <Router>{children}</Router>
                </Theme.Provider>
            </ErrorBoundary>
        </React.Suspense>
    );
}

import { PropsWithChildren, createContext, useState } from "react";
import * as themes from "@/theme";

const localStorageKey = "color-theme";

/**
 * Get the preferred theme from local storage if set
 *
 * @returns the preferred theme or null
 */
function getStoredThemePreference(): string | null {
    try {
        return window.localStorage.getItem(localStorageKey);
    } catch (e) {
        // localstorage not available
        return null;
    }
}

/**
 * Set the preferred theme in local storage, or clear it.
 *
 * @param theme the preferred theme, or null to clear
 * @returns whether write to local storage succeeded
 */
function setStoredThemePreference(theme: string | null): boolean {
    try {
        if (theme === null) {
            window.localStorage.removeItem(localStorageKey);
        } else {
            window.localStorage.setItem(localStorageKey, theme);
        }
        return true;
    } catch (e) {
        // localstorage not available (incognito etc)
        return false;
    }
}

/**
 * Derive the preferred theme from media preference (i.e. if user specified
 * dark in laptop settings).
 *
 * @returns the preferred theme or null if not specified
 */
function getMediaThemePreference(): string | null {
    if (matchMedia("(prefers-color-scheme: dark)").matches) return "dark";
    if (matchMedia("(prefers-color-scheme: light)").matches) return "light";
    return null;
}

/**
 * Get the preferred theme from one of:
 *  - local storage
 *  - media settings
 *
 * or fall back to a default.
 *
 * @returns the preferred theme or a fallback
 */
function getThemePreference(): themes.Theme {
    const savedThemeName = getStoredThemePreference();
    const savedTheme = themes.themes.find((v) => v.name === savedThemeName);
    if (savedTheme) {
        return savedTheme;
    }
    const mediaThemeName = getMediaThemePreference();
    const mediaTheme = themes.themes.find((v) => v.name === mediaThemeName);
    const backupTheme = mediaTheme ?? themes.themes[0];
    return {
        name: `auto (${backupTheme.name})`,
        theme: backupTheme.theme,
    };
}

/**
 * Get the current theme, and a method to update it
 *
 * @returns current theme, theme setter
 */
function useTheme() {
    const initialTheme = getThemePreference();
    const [theme, setTheme] = useState(initialTheme);

    const setAndSaveTheme = (newTheme: themes.Theme | null): void => {
        // Set the theme, saving the preference in local storage if possible
        // null resets the theme to auto
        if (newTheme === null) {
            setStoredThemePreference(null);
            setTheme(getThemePreference());
        } else {
            setStoredThemePreference(newTheme.name);
            setTheme(newTheme);
        }
    };

    // Listen the color preference media events, and set theme when they do.
    window
        .matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", () => setTheme(getThemePreference()));

    window
        .matchMedia("(prefers-color-scheme: light)")
        .addEventListener("change", () => setTheme(getThemePreference()));

    return [theme, setAndSaveTheme] as const;
}

/**
 * Internal theme context, exposed on 'Theme'
 */
const ThemeContext = createContext({
    theme: themes.themes[0],
    setTheme: (_theme: themes.Theme | null) => {},
});

/**
 * Theme context for using and setting the theme
 */
const Theme = {
    Provider: ({ children }: PropsWithChildren) => {
        const [theme, setTheme] = useTheme();
        return (
            <ThemeContext.Provider value={{ theme, setTheme }}>
                <div className={theme.theme.className}>{children}</div>
            </ThemeContext.Provider>
        );
    },
    Consumer: ThemeContext.Consumer,
};
export default Theme;

// stitches.config.ts
import { createStitches } from "@stitches/react";

const lightThemeDef = {
    name: "light",
    theme: {
        colors: {
            primarybg: "#F0F0F0",
            secondarybg: "#E0E0E0",
            tertiarybg: "#FFFFFF",
            lowlightbg: "#d7d7d7",
            highlightbg: "#FFFFFF",
            accentbg: "#9999DD",
            saturatedtxt: "#000000",
            primarytxt: "#222222",
            desaturatedtxt: "#888888",
        },
    },
};

const darkThemeDef: typeof lightThemeDef = {
    name: "dark",
    theme: {
        colors: {
            primarybg: "#202020",
            secondarybg: "#181818",
            tertiarybg: "#303030",
            lowlightbg: "#303030",
            highlightbg: "#505050",
            accentbg: "#9999DD",
            saturatedtxt: "#FFFFFF",
            primarytxt: "#CCCCCC",
            desaturatedtxt: "#888888",
        },
    },
};

const oddThemeDef: typeof lightThemeDef = {
    name: "odd",
    theme: {
        colors: {
            primarybg: "beige",
            secondarybg: "brown",
            tertiarybg: "#fefe84",
            lowlightbg: "#b05050",
            highlightbg: "#fefe84",
            accentbg: "#9999DD",
            saturatedtxt: "#AAFFFF",
            primarytxt: "#44CCCC",
            desaturatedtxt: "#888888",
        },
    },
};

const themeDefs = [lightThemeDef, darkThemeDef, oddThemeDef];

const stitches = createStitches({ theme: themeDefs[0].theme });

function createTheme(themeDef: typeof lightThemeDef) {
    const baseTheme = stitches.createTheme(themeDef.theme);
    return {
        name: themeDef.name,
        theme: baseTheme,
    };
}

export type Theme = ReturnType<typeof createTheme>;
export const themes = themeDefs.map(createTheme);
export const { styled } = stitches;
const theme = stitches.theme;
export default theme;

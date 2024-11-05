/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2023-2024 Vypercore. All Rights Reserved
 */

// stitches.config.ts
import { createStitches } from "@stitches/react";

const lightThemeDef = {
    name: "light",
    theme: {
        colors: {
            primarybg: "#F6F6F6",
            secondarybg: "#E0E0E0",
            tertiarybg: "#FFFFFF",
            lowlightbg: "#d7d7d7",
            highlightbg: "#FFFFFF",
            accentbg: "#9999DD",
            saturatedtxt: "#000000",
            primarytxt: "#222222",
            desaturatedtxt: "#888888",
            positivebg: "#4bFF4b",
            negativebg: "#FF4b4b",
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
            positivebg: "#2BAA2B",
            negativebg: "#AA2B2B",
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
            positivebg: "#ADFF6E",
            negativebg: "#FFB6B6",
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
export default stitches.theme;

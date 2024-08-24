/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2023-2024 Vypercore. All Rights Reserved
 */

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
// Plugin that synchronises vite's path searching with tsconfig settings.
import tsconfigPaths from "vite-tsconfig-paths";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react(), tsconfigPaths()],
});

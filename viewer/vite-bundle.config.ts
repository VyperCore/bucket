/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2023-2024 Vypercore. All Rights Reserved
 */

// #!/usr/bin/env node --no-warnings=ExperimentalWarning
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
// Plugin that synchronises vite's path searching with tsconfig settings.
import tsconfigPaths from "vite-tsconfig-paths";
import { viteSingleFile } from "vite-plugin-singlefile"
import {resolve} from 'path'
import { createRequire } from "module";

export default defineConfig(async () => {
    let cvgPathJSON = process.env["BUCKET_CVG_JSON"];
    if (cvgPathJSON === undefined) {
        throw new Error("`BUCKET_CVG_JSON` env not defined!")
    }
    cvgPathJSON = resolve(cvgPathJSON)

    let coverage = createRequire(import.meta.url)(cvgPathJSON);
    // Note modern but experimental syntax is:
    //  `await import(cvgPathJSON, { with: { type: 'json' }});`

    return {
        plugins: [react(), tsconfigPaths(), viteSingleFile()],
        define: {
            __BUCKET_CVG_JSON: coverage
        }
    }
});

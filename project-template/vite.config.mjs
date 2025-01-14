import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
    plugins: [],
    build: {
        outDir: "main/static/dist",
        rollupOptions: {
            // overwrite default .html entry
            input: [
                // Import main.scss via .js so we get HMR
                path.resolve(__dirname, "main/frontend/js/main.js"),
                // TODO: But keep vendor outside 
                path.resolve(__dirname, "main/frontend/css/vendor.scss"),
            ],
            output: {
                assetFileNames: "assets/[name].[ext]",
                chunkFileNames: "chunks/[name].js",
                entryFileNames: "assets/[name].js",
            },
        },
    },
    server: {
        hot: true,
    },
});

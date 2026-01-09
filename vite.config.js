import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    outDir: 'static',
    emptyOutDir: false,
    rollupOptions: {
      input: {
        app: 'ui/app.css'
      },
      output: {
        assetFileNames: (assetInfo) => {
          if (assetInfo.name === 'app.css') return 'css/app.css';
          return 'assets/[name]-[hash][extname]';
        }
      }
    }
  }
});

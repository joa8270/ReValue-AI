import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';

// Custom plugin to handle Vercel serverless functions locally
const vercelApiMiddleware = () => ({
  name: 'vercel-api-middleware',
  configureServer(server) {
    server.middlewares.use(async (req, res, next) => {
      if (req.url.startsWith('/api/')) {
        const apiName = req.url.split('/')[2]; // e.g., 'analyze'
        const handlerPath = path.resolve(__dirname, 'api', `${apiName}.js`);

        if (fs.existsSync(handlerPath)) {
          console.log(`[API Middleware] Handling ${apiName} locally`);
          try {
            // Invalidate cache to allow hot reloading of API functions
            delete require.cache[require.resolve(handlerPath)];
            const handler = (await import(handlerPath)).default;

            // Parse body if needed (simple json body parser)
            let body = {};
            if (req.method === 'POST') {
              const buffers = [];
              for await (const chunk of req) {
                buffers.push(chunk);
              }
              const data = Buffer.concat(buffers).toString();
              if (data) {
                try {
                  body = JSON.parse(data);
                } catch (e) {
                  console.error("Body parse error", e);
                }
              }
            }

            // Create a pseudo-request object with body
            const pseudoReq = {
              ...req,
              body,
              method: req.method,
              query: req.url.split('?')[1] || '' // simplified
            };

            // Custom response object to capture output
            const pseudoRes = {
              status: (code) => {
                res.statusCode = code;
                return pseudoRes;
              },
              json: (data) => {
                res.setHeader('Content-Type', 'application/json');
                res.end(JSON.stringify(data));
              }
            };

            // Mock process.env for the handler if not already set by dotenv (vite loadEnv does this but let's be sure for API context)
            // Note: vite handles env vars, but process.env in node context might need .env loading if not handled by vite's server start
            // Actually Vite loads .env into process.env for config, but let's check.

            await handler(pseudoReq, pseudoRes);
            return;
          } catch (error) {
            console.error(`API Handler Error for ${apiName}:`, error);
            res.statusCode = 500;
            res.end(JSON.stringify({ error: error.message }));
            return;
          }
        }
      }
      next();
    });
  },
});

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '');

  // Inject non-VITE envs into process.env for local API handlers
  process.env.GEMINI_API_KEY = env.GEMINI_API_KEY || env.VITE_GEMINI_API_KEY;

  return {
    server: {
      port: 3000,
      host: '0.0.0.0',
    },
    plugins: [react(), vercelApiMiddleware()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      }
    },
    optimizeDeps: {
      exclude: ['lucide-react'],
    },
  };
});

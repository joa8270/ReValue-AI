<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# AI Refurbished Device Valuation (Ai-Valuation-Rewrite)

AI-powered valuation tool for refurbished devices.

## Getting Started

### Prerequisites

- Node.js (v20 or higher)
- npm

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in the root directory based on `.env.example` (if available) or add your API keys:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### Development

Start the development server:
```bash
npm run dev
```

### Build

Build for production:
```bash
npm run build
```

## Deployment

This project is configured to deploy to GitHub Pages automatically via GitHub Actions.

1. Go to your repository **Settings** > **Pages**.
2. Under "Build and deployment", set **Source** to **GitHub Actions**.
3. Push your changes to the `main` branch.
4. Ensure you have set the `GEMINI_API_KEY` in your repository **Settings** > **Secrets and variables** > **Actions**.

The workflow is defined in `.github/workflows/deploy.yml`.

## Technologies

- React 18
- Vite
- TypeScript
- Tailwind CSS
- Google Gemini API

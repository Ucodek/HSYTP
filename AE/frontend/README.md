# HSYTP Frontend

A modern, feature-rich web frontend for the HSYTP platform, built with Next.js, TypeScript, Tailwind CSS, and shadcn/ui. This application provides interactive tools for portfolio optimization, stock forecasting, and financial analytics, integrating seamlessly with the backend API.

## Features

- **Next.js 15** with App Router and TypeScript
- **shadcn/ui** and **Radix UI** for accessible, customizable components
- **Tailwind CSS** for rapid, utility-first styling
- **Internationalization (i18n)** with `next-intl` (multi-language support)
- **Authentication** (login, signup, JWT/session management)
- **Portfolio Optimization**: input, output, risk metrics, backtesting
- **Stock Forecasting**
- **Market Overview, Economic Events, News, and Blog Content**
- **State Management** with Zustand
- **API Integration** via Axios (with circuit breaker, caching, token management)
- **Responsive, modern UI/UX**

## Getting Started

### 1. Install Dependencies
```powershell
npm install
# or
pnpm install
# or
yarn install
# or
bun install
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env.local` and fill in the required values:
```powershell
cp .env.example .env.local
```

### 3. Run the Development Server
```powershell
npm run dev
# or
pnpm dev
# or
yarn dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure
```
frontend/
├── public/                # Static assets
├── messages/              # Localization files (en.json, tr.json, ...)
├── src/
│   ├── app/               # Next.js app directory (routing, pages)
│   ├── components/        # UI components (shadcn/ui, custom, etc.)
│   ├── data/              # Static/mock data
│   ├── i18n/              # i18n config and helpers
│   ├── lib/               # API, repositories, stores, types, utils
│   └── middleware.ts      # Next.js middleware
├── tailwind.config.ts     # Tailwind CSS config
├── next.config.ts         # Next.js config
├── package.json           # Project metadata and scripts
└── ...
```

## UI System
- Uses [shadcn/ui](https://ui.shadcn.com/) for headless, accessible, and customizable UI components.
- Uses [Radix UI](https://www.radix-ui.com/) primitives for dialogs, popovers, tooltips, etc.
- All components are styled with Tailwind CSS and can be easily customized.

## Scripts
- `npm run dev` – Start development server
- `npm run build` – Build for production
- `npm run start` – Start production server
- `npm run lint` – Lint code

## Internationalization
- All routes and content support multiple languages using `next-intl`.
- Add new locales in the `messages/` directory and update i18n config as needed.

## API Integration
- All data and authentication flows are handled via the backend API (`NEXT_PUBLIC_API_URL`).
- See `src/lib/requests.ts` and `src/lib/repositories/` for API logic.
- See [`src/lib/README.md`](src/lib/README.md) for the API integration and state management pattern used in this project.

## Development & Contribution
- Code style: ESLint, Prettier, TypeScript strict mode
- UI: shadcn/ui, Radix UI, Tailwind CSS
- State: Zustand
- Please open issues or pull requests for improvements or bugfixes.

## License
[MIT](LICENSE)

---
For more details, see the codebase and in-code documentation.

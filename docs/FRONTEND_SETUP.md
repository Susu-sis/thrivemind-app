# ThriveMind Frontend Setup

## Step 1: Create the Next.js project

```bash
cd c:\Users\Suha.Saad\Proyectos\thrivemind-app

npx create-next-app@latest frontend --typescript --eslint --tailwind --app --no-src-dir --import-alias "@/*"
```

## Step 2: Install dependencies

```bash
cd frontend

# shadcn/ui init
npx shadcn@latest init

# shadcn components
npx shadcn@latest add button card input slider badge progress tabs dialog sheet toast avatar separator select switch

# Charts, icons, HTTP client, forms, theme
npm install recharts lucide-react axios react-hook-form @hookform/resolvers zod next-themes sonner
```

## Step 3: Copy custom files

After running the commands above, copy these files from `frontend-src/` into the `frontend/` directory:

- `frontend-src/lib/api.ts` → `frontend/lib/api.ts`
- `frontend-src/hooks/useAuth.ts` → `frontend/hooks/useAuth.ts`
- `frontend-src/components/theme-provider.tsx` → `frontend/components/theme-provider.tsx`
- `frontend-src/middleware.ts` → `frontend/middleware.ts`

Then replace the auto-generated files:
- `frontend-src/app/layout.tsx` → `frontend/app/layout.tsx`
- Create subdirectories: `app/login/`, `app/register/`, `app/dashboard/`, etc.
- Copy page files from `frontend-src/app/` into the matching directories.

## Step 4: Create .env.local

```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
```

## Step 5: Run the dev server

```bash
cd frontend
npm run dev
```

Open http://localhost:3000 to see the app.

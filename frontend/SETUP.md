# Lore Emotion - Frontend Setup Guide

## Prerequisites

- Node.js 18+
- npm or yarn

## Installation

### 1. Install Dependencies

```powershell
cd frontend
npm install
```

### 2. Configure Environment

Copy the example environment file:

```powershell
copy .env.local.example .env.local
```

Update `.env.local` with your values:
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_COGNITO_USER_POOL_ID` - AWS Cognito User Pool ID
- `NEXT_PUBLIC_COGNITO_CLIENT_ID` - AWS Cognito Client ID
- `NEXT_PUBLIC_COGNITO_REGION` - AWS Region

### 3. Run Development Server

```powershell
npm run dev
```

The application will be available at: `http://localhost:3000`

## Building for Production

```powershell
# Build the application
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js 14 App Router
│   ├── auth/              # Authentication pages
│   │   ├── signin/        # Sign in page
│   │   ├── signup/        # Sign up page
│   │   └── confirm/       # Email confirmation
│   ├── dashboard/         # Protected dashboard
│   ├── globals.css        # Global styles (Tailwind + custom)
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # Reusable components
├── lib/                   # Utilities
│   ├── auth.ts           # Cognito auth service
│   ├── api.ts            # Backend API client
│   └── store.ts          # Zustand state management
├── public/               # Static assets
├── tailwind.config.ts    # Tailwind configuration
├── next.config.js        # Next.js configuration
└── package.json          # Dependencies
```

## Key Features

### Design System
- **Color Palette**: Lore.co-inspired warm and calming colors
- **Typography**: Inter font for readability
- **Components**: Tailwind CSS with custom utilities
- **Animations**: Framer Motion for smooth interactions
- **Accessibility**: WCAG 2.1 AA compliant

### Authentication
- AWS Cognito integration
- Email/password authentication
- Email verification flow
- Password reset functionality
- Persistent sessions

### State Management
- Zustand for global state
- Local storage persistence
- Authentication state
- User profile data

### API Integration
- Axios client with interceptors
- Automatic token injection
- Error handling
- Type-safe endpoints

## Available Scripts

```powershell
# Development
npm run dev              # Start dev server

# Production
npm run build           # Build for production
npm start              # Start production server

# Code Quality
npm run lint           # Run ESLint
npm run type-check     # TypeScript type checking
```

## Environment Variables

### Required Variables
- `NEXT_PUBLIC_API_URL` - Backend API endpoint
- `NEXT_PUBLIC_COGNITO_USER_POOL_ID` - Cognito User Pool ID
- `NEXT_PUBLIC_COGNITO_CLIENT_ID` - Cognito Client ID
- `NEXT_PUBLIC_COGNITO_REGION` - AWS Region

### Optional Variables
- `NEXT_PUBLIC_SENTRY_DSN` - Sentry error tracking
- `NEXT_PUBLIC_ANALYTICS_ID` - Analytics tracking ID

## Deployment

### Vercel (Recommended)
1. Push code to GitHub
2. Import repository in Vercel
3. Configure environment variables
4. Deploy automatically on push

### Docker
```powershell
docker build -t lore-emotion-frontend .
docker run -p 3000:3000 lore-emotion-frontend
```

### Static Export
```powershell
npm run build
# Deploy the .next/out folder to any static hosting
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Optimization

- Image optimization with Next.js Image component
- Code splitting and lazy loading
- Font optimization
- CSS optimization with Tailwind
- Server-side rendering for initial load

## Security

- HTTPS only in production
- Content Security Policy headers
- XSS protection
- CSRF protection
- Secure cookie handling
- Token encryption

## Accessibility

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support
- High contrast mode
- Reduced motion support

## Troubleshooting

### Module not found errors
```powershell
rm -rf node_modules package-lock.json
npm install
```

### Build errors
```powershell
npm run type-check  # Check for TypeScript errors
npm run lint        # Check for linting errors
```

### Authentication issues
- Verify Cognito configuration
- Check environment variables
- Clear browser local storage
- Check CORS settings on backend

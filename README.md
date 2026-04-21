# PropertyPulse

Real Estate Investment Analysis Platform

## Tech Stack

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Payment**: LemonSqueezy
- **API**: RentCast

## Local Development

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Backend (.env)
```
DATABASE_URL=sqlite:///./propertypulse.db
SECRET_KEY=your-secret-key
RENTCAST_API_KEY=your-api-key
LEMONSQUEEZY_API_KEY=your-api-key
LEMONSQUEEZY_STORE_ID=your-store-id
LEMONSQUEEZY_STARTER_VARIANT_ID=xxx
LEMONSQUEEZY_PRO_VARIANT_ID=xxx
LEMONSQUEEZY_TEAM_VARIANT_ID=xxx
```

## Deployment

### Frontend (Vercel)
1. Connect GitHub repo to Vercel
2. Set root directory to `frontend`
3. Add environment variables
4. Deploy

### Backend (Railway)
1. Connect GitHub repo to Railway
2. Set root directory to `backend`
3. Add environment variables
4. Deploy

## License

MIT

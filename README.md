# Neuro Adaptive AI Assistant

An adaptive learning platform using **FastAPI** (Backend) and **Next.js** (Frontend) with Google OAuth2 authentication.

## 🚀 Getting Started

To contribute or run this project locally, follow these steps.

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- PostgreSQL (or update config to use SQLite)

### 1. Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in `backend/` based on this template:
   ```ini
   SECRET_KEY=generate_a_random_secure_key
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/neuro_db
   # Get these from Google Cloud Console
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   FRONTEND_URL=http://localhost:3000
   ```

4. **Run Database Migrations:**
   ```bash
   # Ensure your database exists first (e.g., created via psql)
   python -m alembic upgrade head
   ```

5. **Start the Server:**
   ```bash
   python main.py
   ```
   Server runs at: `http://localhost:8000`

---

### 2. Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure Environment Variables:**
   Create a `.env.local` file in `frontend/` based on this template:
   ```ini
   # Must match backend env
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   
   # NextAuth Config
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=generate_another_random_secret
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```
   > **Note:** Add `http://localhost:3000/api/auth/callback/google` to your Google Cloud Console's **Authorized redirect URIs**.

4. **Start the Development Server:**
   ```bash
   npm run dev
   ```
   App runs at: `http://localhost:3000`

## 🤝 Contributing

1. **Fork the repository** on GitHub.
2. **Clone** your fork locally.
3. Create a **feature branch**: `git checkout -b my-new-feature`.
4. Commit your changes.
5. Push to your fork and submit a **Pull Request**.

## 🛠 Tech Stack
- **Frontend:** Next.js 16, TypeScript, Tailwind CSS, NextAuth.js
- **Backend:** FastAPI, SQLAlchemy, Alembic, Pydantic
- **Database:** PostgreSQL

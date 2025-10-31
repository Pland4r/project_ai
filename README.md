# SaaS User Growth Analyzer

## Setup

### Backend
1. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Set OpenAI API key:
   ```bash
   echo OPENAI_API_KEY=your_key_here > .env
   ```
4. Run Flask app:
   ```bash
   python app.py
   ```

### Frontend
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Run Next.js app:
   ```bash
   npm run dev
   ```

## Usage
1. Access frontend at `http://localhost:3000`
2. Upload clean user data (CSV/XLSX)
3. View analytics dashboard with AI insights

## Deployment to GitHub Pages

1. Push the project to a GitHub repository
2. Go to repository Settings > Pages
3. Set source to "GitHub Actions"
4. The deployment workflow will automatically build and deploy the frontend when you push to the `main` branch

Note: The backend must be hosted separately (e.g. on a cloud service) for production use.

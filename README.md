# MBT Affordability Benchmarking Tool

A comprehensive mortgage broker tool for running automated affordability scenarios across multiple lenders with historical tracking and analytics.

## Features

- 🏠 **32+ Mortgage Scenarios**: Automated testing across different income levels and employment types
- 💳 **Credit Commitment Analysis**: 1% and 10% income scenarios for realistic client situations
- 📊 **Historical Tracking**: Store and visualize trends over time with Supabase integration
- 📈 **Advanced Analytics**: Gen H ranking, lender gap analysis, and performance metrics
- 🚀 **Real-time Dashboard**: Interactive web interface with charts and data export

## Local Development

### Prerequisites
- Python 3.8+
- Playwright browsers
- Supabase account (free tier works)

### Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install Playwright browsers: `playwright install chromium`
4. Configure environment variables in `.env`:
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```
5. Run the server: `python enhanced_server.py`
6. Open http://127.0.0.1:8001

## Railway Deployment

### Quick Deploy
1. Fork/clone this repository
2. Connect your GitHub to Railway
3. Create a new Railway project from this repository
4. Add environment variables in Railway dashboard:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_ANON_KEY`: Your Supabase anonymous key
5. Deploy automatically handles Playwright installation

### Environment Variables Required
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous public key
- `PORT`: Automatically set by Railway
- `HOST`: Automatically set by Railway

## Database Setup

1. Create a Supabase project at https://supabase.com
2. Run the SQL schema from `supabase_schema.sql` in your Supabase SQL editor
3. Get your project URL and anon key from the API settings
4. Add them to your environment variables

## Usage

### Running Automation
- **Sample Test**: Quick 4-scenario test for validation
- **Credit Scenarios**: 32 scenarios with credit commitments (1% and 10% of income)
- **Full Automation**: All 64 scenarios (normal + credit)

### Historical Analytics
- View trends over time in the Historical Trends tab
- Compare Gen H performance vs market average
- Track rank improvements/declines for each scenario type
- Export data in CSV, Excel, or JSON formats

## Tech Stack

- **Backend**: FastAPI + Python
- **Automation**: Playwright for web scraping
- **Database**: Supabase (PostgreSQL)
- **Frontend**: Vanilla JavaScript + Chart.js
- **Deployment**: Railway (with automatic Playwright setup)

## API Endpoints

- `GET /` - Dashboard interface
- `GET /api/latest-results` - Latest automation results
- `GET /api/historical-summary` - Historical summary statistics
- `GET /api/historical-gen-h-rank` - Gen H rank trends over time
- `GET /api/historical-gen-h-gap` - Performance gap trends
- `GET /api/scenario-rank-changes` - Rank changes between runs
- `GET /api/export-data/{format}` - Export data in CSV/Excel/JSON

## Support

For issues or questions about deployment, check the Railway logs and ensure:
1. Environment variables are set correctly
2. Supabase project is active and accessible
3. Database schema has been created properly
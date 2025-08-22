# Supabase Setup Guide for MBT Affordability Tool

This guide will help you set up Supabase integration for historical data tracking and analytics.

## Prerequisites

- A Supabase account (free tier is sufficient)
- Python dependencies installed: `pip3 install supabase python-dotenv`

## Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Choose your organization
5. Set project name: "MBT Affordability Tool"
6. Set a database password (save this!)
7. Choose a region close to you
8. Click "Create new project"
9. Wait for the project to be set up (2-3 minutes)

## Step 2: Get Your Project Credentials

1. In your Supabase dashboard, go to **Settings** > **API**
2. Copy the following values:
   - **Project URL** (e.g., `https://abcdefghijk.supabase.co`)
   - **anon public** key (the long JWT token)

## Step 3: Set Up Environment Variables

1. In your MBT tool directory, copy the template:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` file and add your credentials:
   ```
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

## Step 4: Create Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste the entire contents of `supabase_schema.sql`
4. Click **Run** to execute the SQL
5. You should see success messages for creating tables and functions

## Step 5: Test the Setup

Run the setup script:
```bash
python3 setup_supabase.py
```

This will:
- ✅ Check your .env file
- ✅ Test Supabase connection  
- ✅ Verify database access

## Step 6: Start Using Historical Features

1. Start your server: `python3 enhanced_server.py`
2. Open http://127.0.0.1:8001
3. Run some automation scenarios (credit or full)
4. Check the **Historical** tab to see your data building up over time

## What Gets Stored

### Automation Runs Table
- Session ID, run type (normal/credit/full)
- Total/successful scenarios
- Average Gen H rank and percentages
- Complete results JSON
- Timestamp

### Scenario Results Table
- Individual scenario performance
- Gen H amount, rank, and gap vs average
- Lender results JSON
- Linked to automation run

## Historical Analytics Available

### Dashboard Summary
- **Total automation runs**: Count of all historical runs
- **Average Gen H rank**: Across all runs and scenarios
- **Best performing scenario**: Lowest average rank
- **Last run**: Most recent automation timestamp

### Charts
1. **Gen H Rank Over Time**: Line chart showing average rank trends
2. **Gen H vs Average Gap**: How much better/worse Gen H performs vs average lender
3. **Rank Changes**: Bar charts showing improvement/decline for each scenario type

## Troubleshooting

### "Supabase credentials not found"
- Check your `.env` file exists and has the correct variable names
- Ensure no extra spaces around the `=` signs

### "Database not connected"
- Verify your SUPABASE_URL and SUPABASE_ANON_KEY are correct
- Check your Supabase project is still active

### "Need at least 2 runs to calculate rank changes"
- This is normal - rank change charts need historical data
- Run automation scenarios multiple times to build up data

### SQL Errors When Creating Schema
- Make sure you copied the entire `supabase_schema.sql` content
- Check you have proper permissions in your Supabase project
- Try running individual CREATE TABLE statements one by one

## Data Privacy

- All data stays in your Supabase project
- You control access and can delete data anytime
- The anon key is safe to use in client-side code
- For production, consider setting up Row Level Security (RLS)

## Support

If you encounter issues:
1. Check the server logs for specific error messages
2. Verify your Supabase project is active and accessible
3. Test the connection with `python3 setup_supabase.py`
4. Check the SQL Editor in Supabase for any failed queries
-- MBT Affordability Tool - Supabase Database Schema (Fixed)
-- Run these SQL commands in your Supabase SQL editor

-- Table: automation_runs
-- Stores summary data for each automation run
CREATE TABLE automation_runs (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL UNIQUE,
    run_type TEXT NOT NULL,
    total_scenarios INTEGER NOT NULL DEFAULT 0,
    successful_scenarios INTEGER NOT NULL DEFAULT 0,
    average_gen_h_rank DECIMAL(5,2) DEFAULT 0,
    rank_1_percentage DECIMAL(5,2) DEFAULT 0,
    rank_2_percentage DECIMAL(5,2) DEFAULT 0,
    rank_3_percentage DECIMAL(5,2) DEFAULT 0,
    top_3_percentage DECIMAL(5,2) DEFAULT 0,
    run_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    results_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: scenario_results
-- Stores detailed results for each scenario in each run
CREATE TABLE scenario_results (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    description TEXT,
    gen_h_amount INTEGER DEFAULT 0,
    average_lender_amount DECIMAL(12,2) DEFAULT 0,
    gen_h_rank INTEGER DEFAULT 0,
    gen_h_difference DECIMAL(12,2) DEFAULT 0,
    gen_h_vs_average_gap DECIMAL(12,2) DEFAULT 0,
    total_lenders INTEGER DEFAULT 0,
    lender_results_json JSONB,
    run_timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (session_id) REFERENCES automation_runs(session_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_automation_runs_timestamp ON automation_runs(run_timestamp);
CREATE INDEX idx_automation_runs_type ON automation_runs(run_type);
CREATE INDEX idx_scenario_results_session ON scenario_results(session_id);
CREATE INDEX idx_scenario_results_scenario ON scenario_results(scenario_id);
CREATE INDEX idx_scenario_results_timestamp ON scenario_results(run_timestamp);

-- Function: Calculate average Gen H rank across all automation runs
CREATE OR REPLACE FUNCTION calculate_average_gen_h_rank()
RETURNS DECIMAL(5,2)
LANGUAGE sql
AS $$
    SELECT COALESCE(AVG(average_gen_h_rank), 0)::DECIMAL(5,2)
    FROM automation_runs
    WHERE average_gen_h_rank > 0;
$$;

-- Function: Get best performing scenario
CREATE OR REPLACE FUNCTION get_best_performing_scenario()
RETURNS TEXT
LANGUAGE sql
AS $$
    SELECT COALESCE(
        (SELECT scenario_id 
         FROM scenario_results 
         WHERE gen_h_rank > 0 
         GROUP BY scenario_id 
         ORDER BY AVG(gen_h_rank::DECIMAL) ASC 
         LIMIT 1),
        'No data'::TEXT
    );
$$;

-- Function: Get Gen H vs average gap over time for charting
CREATE OR REPLACE FUNCTION get_gen_h_gap_over_time(run_limit INTEGER DEFAULT 20)
RETURNS TABLE(
    run_timestamp TIMESTAMPTZ,
    run_type TEXT,
    average_gap DECIMAL(12,2)
)
LANGUAGE sql
AS $$
    SELECT 
        ar.run_timestamp,
        ar.run_type,
        COALESCE(AVG(sr.gen_h_vs_average_gap), 0)::DECIMAL(12,2) as average_gap
    FROM automation_runs ar
    LEFT JOIN scenario_results sr ON ar.session_id = sr.session_id
    GROUP BY ar.session_id, ar.run_timestamp, ar.run_type
    ORDER BY ar.run_timestamp ASC
    LIMIT run_limit;
$$;

-- Function: Get scenario performance summary
CREATE OR REPLACE FUNCTION get_scenario_performance_summary()
RETURNS TABLE(
    scenario_id TEXT,
    avg_rank DECIMAL(5,2),
    best_rank INTEGER,
    worst_rank INTEGER,
    total_runs_count INTEGER
)
LANGUAGE sql
AS $$
    SELECT 
        scenario_id,
        ROUND(AVG(gen_h_rank::DECIMAL), 2)::DECIMAL(5,2) as avg_rank,
        MIN(gen_h_rank) as best_rank,
        MAX(gen_h_rank) as worst_rank,
        COUNT(*)::INTEGER as total_runs_count
    FROM scenario_results
    WHERE gen_h_rank > 0
    GROUP BY scenario_id
    ORDER BY avg_rank ASC;
$$;
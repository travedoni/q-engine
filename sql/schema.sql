-- Core securities table
CREATE TABLE securities (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    first_trade_date DATE,
    last_trade_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily price data
CREATE TABLE daily_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) REFERENCES securities(ticker),
    date DATE NOT NULL,
    open DECIMAL(12, 4),
    high DECIMAL(12, 4),
    low DECIMAL(12, 4),
    close DECIMAL(12, 4),
    volume BIGINT,
    adj_close DECIMAL(12, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, date)
);

-- Index for fast queries by date and ticker
CREATE INDEX idx_daily_prices_ticker_date ON daily_prices(ticker, date);
CREATE INDEX idx_daily_prices_date ON daily_prices(date);

-- Foundamental data (quarterly)
CREATE TABLE fundamentals (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) REFERENCES securities(ticker),
    report_date DATE NOT NULL,
    period_end_date DATE,
    fiscal_quarter INTEGER,
    fiscal_year INTEGER,
    market_cap BIGINT,
    pe_ratio DECIMAL(10, 4),
    pb_ratio DECIMAL(10, 4),
    ps_ratio DECIMAL(10, 4),
    roe DECIMAL(10, 4),
    roa DECIMAL(10, 4),
    debt_to_equity DECIMAL(10, 4),
    current_ratio DECIMAL(10, 4),
    revenue BIGINT,
    net_income BIGINT,
    operation_cash_flow BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, report_date)
);

-- Market-wide data (indices, risk-free rate, ...)
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    index_name VARCHAR(50) NOT NULL,
    close DECIMAL(12, 4),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, index_name)
);

-- Risk-free rate (Treasury yelds)
CREATE TABLE risk_free_rate (
    date DATE PRIMARY KEY,
    rate_3m DECIMAL(6, 4), -- 3-month Treasury
    rate_10y DECIMAL(6, 4), -- 10-year Treasury
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Corporate actions (splits, dividents)
CREATE TABLE corporate_actions (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) REFERENCES securities(ticker),
    date DATE NOT NULL,
    action_type VARCHAR(20), -- 'SPLIT', 'DIVIDEND', 'MERGER'
    value DECIMAL(10, 4),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


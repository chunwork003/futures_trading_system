# Data Architecture

## Storage Strategy

Primary technologies:

- Polars
- Parquet
- DuckDB

Design principle:

Parquet is the persistent analytical data layer.

DuckDB provides relational querying and database functionality.

Polars is used for high-performance dataframe processing.

## Database

Primary database:

database/market.duckdb

Validation database:

database/validation_github.duckdb

## Schema

Current schema files:

- 01_instrument.sql
- 02_contract.sql
- 03_calendar.sql
- 03_calendar_exception.sql
- 04_continuous.sql
- 05_backtest.sql
- 06_margin.sql
- validation_github.sql

## Views

Current 1m views include:

- mxf_1m.sql
- twii_1m.sql
- txf_1m.sql

## Domain

Current domain modules:

- bars.py
- contracts.py
- instruments.py
- signals.py
- ticks.py
- trades.py

## Storage

Current storage modules:

- duckdb_manager.py
- initialize.py
- parquet.py

## Data Pipeline

Planned architecture:

Raw Data
-> Ingestion
-> Validation
-> Cleaning
-> Contract Mapping
-> Trading Calendar
-> Bar Aggregation
-> Parquet
-> DuckDB
-> Features
-> Strategy

## Contract Model

The architecture separates:

- Instrument
- Contract
- Continuous Contract

This is necessary because futures instruments and individual listed contracts have different lifecycles.

## Trading Calendar

Trading calendar is a first-class data component.

It is responsible for:

- Trading dates
- Sessions
- Holidays
- Exceptions
- Day / night sessions
- Contract-specific trading periods

## Data Integrity

Before strategy research, data should be validated for:

- Duplicate timestamps
- Missing bars
- Invalid OHLC
- Timestamp ordering
- Trading-session consistency
- Contract rollover correctness
- Symbol mapping
- Timezone consistency

## Current Priority

The immediate priority is to establish a reliable 1m historical data foundation before building a large strategy library.

Strategy complexity should not exceed data quality and backtest reliability.

# Personal Finance Tracker

A REST API for tracking personal income and expenses, built with FastAPI,
SQLAlchemy, and SQLite. Includes AI-powered financial analysis using Groq
and LangChain.

## Purpose

This application helps individuals manage their personal finances by:
- Tracking income and expense transactions
- Organising transactions into categories
- Generating AI-powered financial insights and summaries
- Providing a clear view of savings rate and spending patterns

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Groq API (llama-3.3-70b-versatile)
- LangChain
- LangGraph
- Docker
- Gradio (demo UI)
- pytest

## Project Structure

    finance-tracker/
    app/
        ai/                  AI and agentic workflows
        config/              Logging, database, and settings configuration
        constants/           Application-wide constants
        exceptions/          Custom domain exceptions
        models/              SQLAlchemy database models
        prompts/             LLM prompt templates
        repository/          Database query layer
        routes/              FastAPI route handlers
        schemas/             Pydantic request and response schemas
        services/            Business logic layer
        tests/               Pytest test suite
        ui/                  Gradio demo interface
        utils/               Shared utility functions
        health.py            Health check endpoints
        main.py              FastAPI entry point
        starter.py           Application bootstrap
    data/                    Local data files
    logs/                    Application logs
    docker-compose.yml
    Dockerfile
    requirements.txt
    .env.example
    README.md

## Getting Started

    # Clone the repository
    git clone https://github.com/YOUR_USERNAME/finance-tracker.git
    cd finance-tracker

    # Create and activate virtual environment
    python -m venv venv
    venv\Scripts\activate

    # Install dependencies
    pip install -r requirements.txt

    # Set up environment variables
    cp .env.example .env
    # Edit .env with your values

    # Run the application
    uvicorn app.main:app --reload

    # Run with Gradio UI
    python run.py

## API Endpoints

    Transactions
    POST   /transactions          Create a transaction
    GET    /transactions          List all transactions
    GET    /transactions/{id}     Get a transaction
    PUT    /transactions/{id}     Update a transaction
    DELETE /transactions/{id}     Delete a transaction
    GET    /transactions/analyze  AI-powered financial analysis

    Categories
    POST   /categories            Create a category
    GET    /categories            List all categories
    GET    /categories/{id}       Get a category
    DELETE /categories/{id}       Delete a category

## Running Tests

    pytest app/tests/

## Running with Docker

    docker compose up --build
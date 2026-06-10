# FitCoach AI

FitCoach AI is a portfolio project for building a production-minded AI fitness coaching assistant.

## Goal

Build a backend-first LLM application that demonstrates:

- FastAPI
- Direct LLM SDK usage
- Structured output
- RAG-based grounding
- Safety guardrails
- Evals
- Observability
- User feedback loops

## Problem Statement

Many fitness beginners do not know how to create a workout plan that matches their goals, schedule, equipment, and current ability. Generic plans are often too vague, too intense, or not personalized enough.

FitCoach AI explores how an LLM-powered assistant can generate structured and safer workout plans grounded in a curated fitness knowledge base.

## Target Users

- Fitness beginners
- Busy people who want simple weekly workout plans
- Users training at home or in a gym
- People with general fitness goals such as fat loss, muscle gain, endurance, and overall health

## Planned Tech Stack

- Backend: Python, FastAPI, Pydantic
- LLM: OpenAI SDK directly
- Vector DB: Qdrant
- Observability: Langfuse
- App DB: SQLite for MVP, PostgreSQL later

## Current Scope

This repository is currently focused on the backend foundation and project structure.

## Local Setup

Local setup instructions will be added as the backend skeleton is implemented.

Planned setup steps:

1. Create a virtual environment.
2. Install backend dependencies.
3. Copy `.env.example` to `.env`.
4. Run the FastAPI backend locally.

## Roadmap

- Setup FastAPI backend skeleton
- Define domain schemas
- Implement structured workout plan generation
- Add retrieval with Qdrant
- Add safety validation
- Add eval dataset and runner
- Add observability and feedback collection

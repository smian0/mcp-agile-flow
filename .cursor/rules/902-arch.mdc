---
description: Use when creating or updating Architecture Documentation to ensure proper structure and technical clarity
globs: **/*.arch.md, ai-docs/arch.md
alwaysApply: false
---

# Architecture Documentation Standards

## Context
- When creating a new Architecture Document
- When updating existing architecture documentation
- When making significant technical decisions
- When defining project structure and technology choices

## Requirements
- Document architectural decisions clearly
- Maintain a Changelog for updates
- Use diagrams to illustrate system components and interactions
- Define technology stack and justifications
- Outline project structure
- Include data models and API specifications

## Template Structure

### Required Sections

#### 1. Title
- Format: "Architecture for {project}"

#### 2. Status
- Draft
- Approved

#### 3. Technical Summary
- Brief overview of the architectural approach
- Key design patterns and principles
- High-level system description

#### 4. Technology Table
- Table listing choices for languages, libraries, infrastructure, etc.
- Column for technology name/type
- Column for description and justification

#### 5. Architectural Diagrams
- System component diagrams
- Data flow diagrams
- Interaction models
- Use Mermaid syntax for diagrams

#### 6. Data Models, API Specs, Schemas
- Database schema definitions
- API endpoints and specifications
- Data structures and types
- Not exhaustive but covering key components

#### 7. Project Structure
- Folder and file organization
- Component relationships
- Code organization principles

#### 8. Change Log
- Table of key changes after document approval
- Includes change title, related story ID, and description

## Commands
- "Create architecture document for {project}": Generates a new architecture file
- "Update architecture status to {status}": Updates architecture status
- "Add technology {technology} to architecture": Adds a new technology to the stack

## Examples
<example>
# Architecture for Sensor Data Processing Platform

## Status
Approved

## Technical Summary
The Sensor Data Processing Platform is designed as a scalable, event-driven system that collects, processes, and analyzes data from various IoT sensors. The architecture follows a microservices approach with a message queue for handling high-volume data streams.

## Technology Table
| Technology | Description |
|------------|-------------|
| Node.js | Backend services for API and data processing |
| MongoDB | Primary database for sensor data storage |
| Kafka | Message queue for event streaming |
| React | Frontend dashboard for visualization |
| Docker | Containerization for deployment |
| AWS | Cloud infrastructure provider |

## Architectural Diagrams

```mermaid
graph TD
    A[Sensors] -->|Data| B[Ingest API]
    B -->|Raw Data| C[Kafka]
    C -->|Events| D[Processing Service]
    D -->|Processed Data| E[MongoDB]
    E --> F[Analytics Service]
    F --> G[Dashboard API]
    G --> H[React Frontend]
    
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style C fill:#bbf,stroke:#333
    style D fill:#bbf,stroke:#333
    style E fill:#dfd,stroke:#333
    style F fill:#bbf,stroke:#333
    style G fill:#bbf,stroke:#333
    style H fill:#f9f,stroke:#333
```

## Data Models

### Sensor Reading
```json
{
  "sensorId": "string",
  "timestamp": "datetime",
  "value": "number",
  "type": "string",
  "location": {
    "lat": "number",
    "long": "number"
  },
  "metadata": "object"
}
```

## Project Structure
```
/src
  /api         # REST API endpoints
  /services    # Business logic
  /models      # Data models
  /utils       # Helper functions
  /config      # Configuration files
/frontend
  /components  # React components
  /pages       # Page layouts
  /state       # State management
/scripts       # Deployment scripts
/docs          # Additional documentation
```

## Change Log
| Change | Story ID | Description |
|--------|----------|-------------|
| Added Kafka | Story-3 | Integrated Kafka for improved scalability |
| Updated Schema | Story-7 | Added metadata field to sensor readings |
</example>

<example type="invalid">
# Technical Design

- Node.js backend
- MongoDB database
- React frontend

We'll use microservices.

Project will be organized into folders.

TODO: Add diagrams later.
</example>

## Critical Rules
- Architecture document must define clear technology choices with justifications
- Diagrams must be included to illustrate system components and interactions
- Data models must be defined for key entities
- Project structure must be clearly documented
- Changes must be tracked in the changelog after approval
- Technical decisions must be clearly explained 
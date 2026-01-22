# Homework Answers

## Question 1: Initial Implementation

**Prompt:** "Create a full-stack application with a React frontend (using Vite) and an Express.js backend. The app should allow real-time collaborative coding using WebSockets (Socket.io). It should have a code editor (Monaco Editor) on the frontend and broadcast changes to all connected clients."

## Question 2: Integration Tests

**Command:** `npm test` (inside `server` directory)

## Question 3: Running Both Client and Server

**Command:** `npm run dev` (inside `package.json` scripts: `"concurrently \"npm run start:server\" \"npm run start:client\""`)

## Question 4: Syntax Highlighting

**Library:** `@monaco-editor/react` (Monaco Editor)

## Question 5: Code Execution

**Library:** `pyodide`

## Question 6: Containerization

**Base Image:** `node:18-alpine`

## Question 7: Deployment

**Service:** Render (or Railway)

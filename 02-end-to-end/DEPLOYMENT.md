# Deployment Instructions

## Deploying to Render

1. Create a new Web Service on Render.
2. Connect your GitHub repository.
3. Select the `02-end-to-end` directory (if possible, or root if repo is just this).
   - Since this is a monorepo-style setup inside a course repo, you might need to configure the Root Directory in Render settings to `02-end-to-end`.
4. Select `Docker` as the Runtime.
5. Render will automatically detect the `Dockerfile` and build it.
6. Set environment variables if needed.
7. Click Deploy.

## Deploying to Railway

1. Create a new project on Railway.
2. Deploy from GitHub repo.
3. Configure the Root Directory to `02-end-to-end`.
4. Railway should detect the Dockerfile.
5. Deploy.

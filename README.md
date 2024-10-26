# Wolf Watch

Wolf Watch is a web application that provides a centralized location for faculty to monitor their assignments for presence on cheating sites.

## Components

- api: Backend component that provides a RESTful API and runs various scrapers.

- client: The frontend of Wolf Watch, built using Next.js, React, and TypeScript.

- nginx: An nginx reverse proxy that routes requests to the API and client.

## Getting Started

### Pre-requisites

- Ensure you have Docker and Docker Compose installed.

#### Environment Files

Some of our services require environment variables to function. To define the values for these variables securely, we use environment files. We have 2 different environment files: `.env.development` and `.env.production`.

**The existance of these files is a requirement of running the project successfully.** In the root of this repository are example files `.env.development.example` and `.env.production.example`, both of which have comments on to configure them.

#### Creating Environment Secrets

Both environment examples have purposefully left the `APPLICATION_SECRET_KEY` and `MYSQL_ROOT_PASSWORD` fields blank for security reasons. These values are **strings** and should be randomly generated.

Our reccomendation is 32-character randomly generated strings. **DO NOT USE THE SAME STRING FOR THE APPLICATION SECRET AND THE MYSQL ROOT PASSWORD!** String generation can be done using any one of the following CLI commands:

##### UNIX/MACOS/WSL

`tr -dc A-Za-z0-9 </dev/urandom | head -c 32 ; echo ''`

##### Windows Powershell

`-join ((48..57) + (97..122) | Get-Random -Count 32 | % {[char]$_})`

### Development Mode

For developers looking to run Wolf Watch in a development environment, follow these steps:

1. Make sure you're in the project's root directory.
2. Use the development-specific Docker Compose configuration to spin up the services:

   `docker-compose -f docker-compose.dev.yml up -d --build`

3. Services will now run using the configurations specified in their `Dockerfile.dev` files.
4. Navigate to `http://localhost` to view the application.

5. You can now debug and hot-reload as per the configurations set for development!

6. To stop the services, run:

   `docker-compose down`

7. If there are database updates you will need to run:
   `docker-compose down --volumes` (NEVER RUN THIS COMMAND ON THE PRODUCTION DEPLOYMENT)

### Production Mode

For developers looking to run Wolf Watch in a production environment, follow these steps:

1. Make sure you're in the project's root directory.
2. Use the production-specific Docker Compose configuration to spin up the services:

   `docker-compose -f docker-compose.yml up -d --build`

3. Services will now run using the configurations specified in their `Dockerfile` files.
4. Go to `http://localhost` to view the application.
5. To stop the services, run:

   `docker-compose down`

# `cecil`
An API that makes analyzing Twitter user relationships easier for humans. Relies on, [baquet](https://github.com/calebglawson/baquet), a library that makes analyzing Twitter user relationships easier for humans.

## Quick Start
Download and set up dependency, `baquet`. Fill out the sample `config.json` with your Twitter API keys and a securely generated password salt.

Run `uvicorn go:CECIL`

Swagger docs at `http://localhost:8000/docs`

Admin user default credentials: admin, password

**Please update your admin user's password.**
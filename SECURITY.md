# Security

Do not commit API keys or `.env` files. The service should be placed behind authentication and rate
limits before exposure to the public internet. Treat uploaded documents as untrusted input, validate
file types and sizes, and scan them before ingestion in a production deployment.

This research system is not operational aviation advice. Report security issues privately to the
repository owner rather than opening a public issue.


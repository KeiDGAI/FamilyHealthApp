#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""
import os
import logging
from app import app

# Production logging configuration
if not app.debug:
    logging.basicConfig(level=logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application starting in production mode')

if __name__ == "__main__":
    # For local development
    app.run(host='0.0.0.0', port=5000, debug=False)
"""
AWS Elastic Beanstalk entry point
This file MUST exist and MUST expose 'application' variable
"""
from app.main import app as application

# This is the WSGI application that EB will use
# DO NOT modify this file unless you know what you're doing
#!/bin/bash
if [ $# -eq 0 ]; then
    echo "Usage: $0 <migration_message>"
    exit 1
fi

alembic revision --autogenerate -m "$1"

# wait for Postgres to start
function postgres_ready() {
    python << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(dbname="uks", user="postgres", password="root", host="172.17.0.2")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done

# Start app
>&2 echo "Postgres is up - executing command"

./start.sh
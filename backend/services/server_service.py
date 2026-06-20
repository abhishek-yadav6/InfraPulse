from sqlalchemy import text
from backend.database.connection import engine


def get_servers():

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT * FROM servers")
        )

        return result.fetchall()


def add_server(
    hostname,
    ip_address,
    os_type,
    environment,
    owner,
    status
):

    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO servers
                (
                    hostname,
                    ip_address,
                    os_type,
                    environment,
                    owner,
                    status
                )
                VALUES
                (
                    :hostname,
                    :ip_address,
                    :os_type,
                    :environment,
                    :owner,
                    :status
                )
            """),
            {
                "hostname": hostname,
                "ip_address": ip_address,
                "os_type": os_type,
                "environment": environment,
                "owner": owner,
                "status": status
            }
        )


def delete_server(server_id):

    with engine.begin() as conn:

        conn.execute(
            text("""
                DELETE FROM servers
                WHERE id = :id
            """),
            {
                "id": server_id
            }
        )


def get_total_servers():

    with engine.connect() as conn:

        return conn.execute(
            text("SELECT COUNT(*) FROM servers")
        ).scalar()


def get_online_servers():

    with engine.connect() as conn:

        return conn.execute(
            text(
                "SELECT COUNT(*) FROM servers WHERE status='Online'"
            )
        ).scalar()


def get_warning_servers():

    with engine.connect() as conn:

        return conn.execute(
            text(
                "SELECT COUNT(*) FROM servers WHERE status='Warning'"
            )
        ).scalar()


def get_critical_servers():

    with engine.connect() as conn:

        return conn.execute(
            text(
                "SELECT COUNT(*) FROM servers WHERE status='Critical'"
            )
        ).scalar()
    
def pause_monitoring(server_id):

    with engine.begin() as conn:

        conn.execute(
            text("""
                UPDATE servers
                SET monitoring_enabled = 0
                WHERE id = :id
            """),
            {
                "id": server_id
            }
        )

def resume_monitoring(server_id):

    with engine.begin() as conn:

        conn.execute(
            text("""
                UPDATE servers
                SET monitoring_enabled = 1
                WHERE id = :id
            """),
            {
                "id": server_id
            }
        )

def get_alert_history():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT *
                FROM monitoring_history
                ORDER BY event_time DESC
                LIMIT 100
            """)
        )

        return result.fetchall()
    
def get_avg_cpu():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT ROUND(AVG(cpu_usage),1)
                FROM servers
            """)
        ).scalar()

        return result or 0


def get_avg_memory():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT ROUND(AVG(memory_usage),1)
                FROM servers
            """)
        ).scalar()

        return result or 0


def get_avg_disk():

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT ROUND(AVG(disk_usage),1)
                FROM servers
            """)
        ).scalar()

        return result or 0
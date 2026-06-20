import platform
import subprocess
from datetime import datetime

import psutil

from sqlalchemy import text
from backend.database.connection import engine

from backend.services.email_service import (
    send_alert_email
)


def ping_server(ip):

    param = "-n" if platform.system().lower() == "windows" else "-c"

    result = subprocess.run(
        ["ping", param, "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


def get_system_metrics():

    cpu_usage = psutil.cpu_percent(interval=1)

    memory_usage = psutil.virtual_memory().percent

    disk_usage = psutil.disk_usage("/").percent

    return (
        cpu_usage,
        memory_usage,
        disk_usage
    )


def monitor_servers():

    print("Monitoring Job Running...")

    with engine.connect() as conn:

        servers = conn.execute(
            text("""
                SELECT
                    id,
                    hostname,
                    ip_address,
                    status,
                    monitoring_enabled
                FROM servers
            """)
        ).fetchall()

    print(f"Servers Found: {len(servers)}")

    for server in servers:

        if server.monitoring_enabled != 1:

            print(
                f"Monitoring Paused for Server ID {server.id}"
            )

            continue

        new_status = (
            "Online"
            if ping_server(server.ip_address)
            else "Critical"
        )

        old_status = server.status

        cpu_usage, memory_usage, disk_usage = (
            get_system_metrics()
        )

        print(
            f"Server ID: {server.id} | "
            f"IP: {server.ip_address} | "
            f"Old: {old_status} | "
            f"New: {new_status} | "
            f"CPU: {cpu_usage}% | "
            f"MEM: {memory_usage}% | "
            f"DISK: {disk_usage}%"
        )

        with engine.begin() as conn:

            conn.execute(
                text("""
                    UPDATE servers
                    SET
                        status = :status,
                        cpu_usage = :cpu_usage,
                        memory_usage = :memory_usage,
                        disk_usage = :disk_usage,
                        last_checked = :last_checked
                    WHERE id = :id
                """),
                {
                    "status": new_status,
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "disk_usage": disk_usage,
                    "last_checked": datetime.now(),
                    "id": server.id
                }
            )

            if old_status != new_status:

                conn.execute(
                    text("""
                        INSERT INTO monitoring_history
                        (
                            server_id,
                            hostname,
                            old_status,
                            new_status
                        )
                        VALUES
                        (
                            :server_id,
                            :hostname,
                            :old_status,
                            :new_status
                        )
                    """),
                    {
                        "server_id": server.id,
                        "hostname": server.hostname,
                        "old_status": old_status,
                        "new_status": new_status
                    }
                )

                print(
                    f"ALERT: {server.hostname} "
                    f"{old_status} -> {new_status}"
                )

                try:

                    send_alert_email(
                        server.hostname,
                        server.ip_address,
                        old_status,
                        new_status
                    )

                except Exception as e:

                    print(
                        f"Email Alert Failed: {e}"
                    )

    print("Monitoring Cycle Completed")
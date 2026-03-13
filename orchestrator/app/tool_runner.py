"""Tool runner executes scanner commands in isolated containers via docker exec."""

import asyncio
import json
import shlex
from dataclasses import dataclass


@dataclass
class CommandResult:
    command: str
    stdout: str
    stderr: str
    returncode: int


async def run_command(command: str, timeout: int = 1800) -> CommandResult:
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return CommandResult(command, "", "command timeout", 124)

    return CommandResult(
        command=command,
        stdout=stdout.decode("utf-8", errors="ignore"),
        stderr=stderr.decode("utf-8", errors="ignore"),
        returncode=proc.returncode,
    )


async def run_nmap(target: str, args: str = "-sV -sC --top-ports 1000") -> dict:
    cmd = f"docker exec expl0v1n-nmap nmap {args} -oX - {shlex.quote(target)}"
    result = await run_command(cmd, timeout=1800)
    return {
        "tool": "nmap",
        "success": result.returncode == 0,
        "raw": result.stdout,
        "error": result.stderr,
    }


async def run_nuclei(targets_file: str, templates: str = "", rate_limit: int = 150) -> dict:
    template_arg = f"-t {templates}" if templates else ""
    cmd = (
        "docker exec expl0v1n-nuclei nuclei "
        f"-l {shlex.quote(targets_file)} -rl {rate_limit} -json -silent {template_arg}"
    )
    result = await run_command(cmd, timeout=3600)
    findings = []
    for line in result.stdout.splitlines():
        try:
            findings.append(json.loads(line))
        except Exception:
            continue
    return {
        "tool": "nuclei",
        "success": result.returncode == 0,
        "findings": findings,
        "error": result.stderr,
    }


async def run_httpx(input_file: str, timeout: int = 10) -> dict:
    cmd = (
        "docker exec expl0v1n-httpx httpx "
        f"-l {shlex.quote(input_file)} -ports 80,443,8080,8443,8000,3000 "
        f"-timeout {timeout} -title -status-code -tech-detect -content-length -json"
    )
    result = await run_command(cmd, timeout=1800)
    hosts = []
    for line in result.stdout.splitlines():
        try:
            hosts.append(json.loads(line))
        except Exception:
            continue
    return {"tool": "httpx", "success": result.returncode == 0, "hosts": hosts, "error": result.stderr}


async def run_katana(targets_file: str) -> dict:
    cmd = f"docker exec expl0v1n-katana katana -list {shlex.quote(targets_file)} -jsonl"
    result = await run_command(cmd, timeout=3600)
    urls = []
    for line in result.stdout.splitlines():
        try:
            urls.append(json.loads(line))
        except Exception:
            continue
    return {"tool": "katana", "success": result.returncode == 0, "urls": urls, "error": result.stderr}

from __future__ import annotations

import io
import os
import tarfile
import time
from dataclasses import dataclass

import docker


@dataclass(frozen=True)
class ExecResult:
    exit_code: int
    stdout: str
    stderr: str


class DockerToolRunner:
    def __init__(self) -> None:
        self.client = docker.from_env()

    def put_text(self, *, container_name: str, path: str, content: str) -> None:
        container = self.client.containers.get(container_name)
        directory = os.path.dirname(path) or "/"
        filename = os.path.basename(path)
        data = content.encode("utf-8")

        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            info = tarfile.TarInfo(name=filename)
            info.size = len(data)
            info.mtime = int(time.time())
            tar.addfile(info, io.BytesIO(data))
        tar_stream.seek(0)
        container.put_archive(directory, tar_stream.read())

    def exec(self, *, container_name: str, cmd: list[str], timeout: int | None = None) -> ExecResult:
        container = self.client.containers.get(container_name)
        # docker-py exec_run does not support a hard timeout reliably; keep commands conservative.
        res = container.exec_run(cmd, demux=True)
        stdout_b, stderr_b = res.output if isinstance(res.output, tuple) else (res.output, b"")
        stdout = (stdout_b or b"").decode("utf-8", errors="replace")
        stderr = (stderr_b or b"").decode("utf-8", errors="replace")
        return ExecResult(exit_code=int(res.exit_code), stdout=stdout, stderr=stderr)

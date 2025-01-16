import logging
import asyncio
import subprocess
import os

from openswebcad import OpenScadScriptError

class Xvfb:
    def __init__(self, display=99):
        self.logger = logging.getLogger(__name__+".xvfb")
        self.process = None
        self.display = display

    def __enter__(self):
        self._start()

    def __exit__(self, type, value, traceback):
        self.logger.info(f"stopping xvfb on {self.display}")
        self.process.terminate()
        try:
            self.process.wait(1.0)
        except subprocess.TimeoutExpired:
            self.logger.warning("xvfb did not exit properly")
        self.process = None

    def get_env(self):
        if self.process is None:
            return {}
        else:
            self._assert_running()
            return {"DISPLAY": f":{self.display}"}

    def _assert_running(self):
        if not self._is_running():
            self.logger.error(self.process.stderr)
            raise RuntimeError("xvfb process has terminated")

    def _is_running(self):
        return self.process.poll() is None

    def _start(self):
        self.logger.info(f"starting xvfb on {self.display}")
        self.process = subprocess.Popen(["Xvfb", f":{self.display}"], stderr=subprocess.PIPE)

xvfb_context = Xvfb()

async def generate_openscad(script: str, out_format: str, image_size: tuple[int, int]|None=None) -> bytes:
    assert out_format in ("png", "stl")
    cmd = ["openscad", "-o", "-", "--export-format", out_format, "-"]
    if out_format == "png":
        assert image_size
        cmd += ["--imgsize", "{0},{1}".format(*image_size)]
    scad = script.encode()
    
    env = os.environ | xvfb_context.get_env()
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE, env=env)
    stdout, stderr = await process.communicate(scad)
    if process.returncode != 0:
        raise OpenScadScriptError(scad, stderr.decode())
    assert isinstance(stdout, bytes)
    assert len(stdout) > 0
    return stdout



import asyncio

async def generate_openscad(script: str, out_format: str, image_size: tuple[int, int]|None=None) -> bytes:
    assert out_format in ("png", "stl")
    cmd = ["openscad", "-o", "-", "--export-format", out_format, "-"]
    if out_format == "png":
        assert image_size
        cmd += ["--imgsize", "{0},{1}".format(*image_size)]
    scad = script.encode()
    
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate(scad)
    if process.returncode != 0:
        raise OpenScadScriptError(scad, stderr.decode())
    assert isinstance(stdout, bytes)
    assert len(stdout) > 0
    return stdout



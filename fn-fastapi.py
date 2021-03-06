import os, sys, random, string, time, threading, atexit
from pathlib import Path

from starlette.requests import SERVER_PUSH_HEADERS_TO_COPY

import uvicorn
from main import app

DEFAULT_LISTENER = '/tmp/fnlsnr.sock'

def randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def unlink(actual: Path, phony: Path):
    #print('func: unlink', file=sys.stderr)
    actual.unlink(missing_ok=True)
    phony.unlink(missing_ok=True)


def make_symlink(actual: Path, phony: Path):
    #print('func: make_symlink', file=sys.stderr)
    # wait for uvicorn to start listening uds
    while not phony.exists():
        time.sleep(100/1000)
    phony.chmod(0o666)
    actual.symlink_to(phony.name)
    print(f'Ready to receive calls via {actual} -> {phony.name}', file=sys.stderr, flush=True)


if __name__ == '__main__':
    fn_listener = None
    try:
        print(f'ENV FN_LISTENER: {os.environ["FN_LISTENER"]}', file=sys.stderr)
        fn_listener = os.environ['FN_LISTENER'].replace('unix:','')
    except:
        print(f'ENV FN_LISTENER not defined - using default: {DEFAULT_LISTENER}', file=sys.stderr)
        fn_listener = DEFAULT_LISTENER
        pass
    actual = Path(fn_listener)
    phony = Path(str(actual.parent) + '/' + randomname(8) + '_' + actual.name)
    print(f'actual: {actual}', file=sys.stderr)
    print(f'phony: {phony}', file=sys.stderr)

    unlink(actual, phony)
    thread = threading.Thread(target=make_symlink, args=(actual, phony))
    thread.start()
    atexit.register(unlink, actual, phony)
    uvicorn.run(app=app, uds=str(phony))

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

@app.post('/call')
async def post_call(request: Request):
    L = []

    L.append('[REQUEST HEADERS]\n')
    for key in request.headers.keys():
        L.append(f'{key}: {request.headers[key]}\n')

    body = await request.body()
    L.append('\n[REQUEST BODY]\n')
    L.append(body.decode())
    L.append('\n')

    return PlainTextResponse(''.join(L))

# Functions without FDK

## Fn (OCI Functions) の Function を FDK を使わずに作成する方法 - Python/FastAPI 編

FDK (Function Development Kit) を使わずに Function を作る方法として「 [netty と reactor-netty で実装してみた](https://github.com/tkote/fn-netty) 」を以前紹介したが、今回はその Python/FastAPI 編。使い慣れたフレームワークを使って Fnctions を開発したいという人は多いハズ。

## 仕組み

Functions のロジックを実装しているもの (main.py)と、ASGI (Asynchronous Server Gateway Interface) 実装である uvicorn の起動や Fn/Functions の流儀に従ってソケットまわりのお世話をしているもの (fn-fastapi.py) の二つで構成されていて、fn-fastapi.py は全くいじる必要なし。  
main.py で 通常 FastAPI で API を実装するのと同じように、`/call` に対する POST リクエストを実装すればOK。ここでは簡易的なデモ実装をしている。

```python
@app.post('/call')
async def post_call():
    ... 実際の処理 ...
```

Fn/Functions がどういう仕様で Unix Domain Socket を使ってコンテナと通信しているかについては、前述の netty/reactor-netty 編を参照されたし。

## ビルド & 実行

* ローカルで実行

  ```bash
  # preparation
  $ pip install fastapi
  $ pip install uvicorn

  # run server
  $ python fn-fastapi.py
  
  # call function
  $ curl --unix-socket /tmp/fnlsnr.sock -X POST -d 'Hello World!' http:/call
  ```

* Docker image を作成 & 実行
  
  ```bash
  # build
  $ docker build -t fn-fastapi:0.0.1 .
  
  # run server
  $ docker run --rm -it --name fn-fastapi -v /tmp:/tmp fn-fastapi:0.0.1

  # call function
  $ curl --unix-socket /tmp/fnlsnr.sock -X POST -d 'Hello World!' http:/call
  ```

* ローカル Fn Server で実行
  
  Fn CLIはインストール済みという前提で
  
  ```bash
  # start Fn server
  $ fn start

  # setup Fn CLI
  $ fn use context default
  
  # create app
  $ fn create app funcapp

  # deploy function
  $ fn deploy -app funcapp --local --no-bump -v

  # call function
  $ echo -n 'Hello World!' | fn invoke funcapp fn-fastapi
  ```

* OCI Functions にデプロイ & 実行

  OCI Functions で アプリケーション funcapp が作成されている前提で

  ```bash
  # setup Fn CLI
  $ fn use context XXXXXX

  # deploy function
  $ fn deploy -app funcapp --no-bump -v

  # call functions
  $ echo -n 'Hello World!' | fn invoke funcapp fn-fastapi
  ```

## デモ

```
# call OCI Functions
$ echo -n 'Hello World!' | fn invoke funcapp fn-fastapi
[REQUEST HEADERS]
host: localhost
user-agent: Go-http-client/1.1
transfer-encoding: chunked
accept-encoding: gzip
content-type: application/json
date: Sun, 09 May 2021 08:37:51 GMT
fn-call-id: 01F584D3CM1BT0010ZJ005T5M1
fn-deadline: 2021-05-09T08:43:16Z
oci-subject-id: ocid1.user.oc1..
oci-subject-tenancy-id: ocid1.tenancy.oc1..
oci-subject-type: user
opc-compartment-id: ocid1.compartment.oc1..
opc-request-id: /01F584D3AJ1BT0010ZJ005T5KR/01F584D3AJ1BT0010ZJ005T5KS
x-content-sha256: f4OxZX/x/FO5LcGBSKHWXfwtSx+j1ncoSt3SABJtkGk=

[REQUEST BODY]
Hello World!
```

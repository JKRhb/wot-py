> :warning: Please note that this project is currently behind the current version of the W3C WoT specifications. Our intention is to get it up to speed and implement the latest Thing Description and Scripting API versions. However, we cannot provide a timeframe for this update.

# WoTPy

[![Travis (.com)](https://img.shields.io/travis/com/agmangas/wot-py)](https://travis-ci.com/agmangas/wot-py) [![Coveralls](https://img.shields.io/coveralls/github/agmangas/wot-py)](https://coveralls.io/github/agmangas/wot-py) [![PyPI](https://img.shields.io/pypi/v/wotpy)](https://pypi.org/project/wotpy/)

## Introduction

WoTPy is an experimental implementation of a [W3C WoT Runtime](https://github.com/w3c/wot-architecture/blob/master/proposals/terminology.md#wot-runtime) and the [W3C WoT Scripting API](https://github.com/w3c/wot-architecture/blob/master/proposals/terminology.md#scripting-api) in Python.

Inspired by the exploratory implementations located in the [thingweb GitHub page](https://github.com/thingweb).

## Features

- Supports Python 2.7 and Python 3.
- Fully-implemented `WoT` interface.
- Multicast discovery based on mDNS.
- Asynchronous I/O programming model based on coroutines.
- Multiple client and server [Protocol Binding](https://github.com/w3c/wot-architecture/blob/master/proposals/terminology.md#protocol-binding) implementations.

### Feature support matrix

|            Feature | Python 2.7               | Python 3           | Implementation based on                                                 |
| -----------------: | ------------------------ | ------------------ | ----------------------------------------------------------------------- |
|       HTTP binding | :heavy_check_mark:       | :heavy_check_mark: | [tornadoweb/tornado](https://github.com/tornadoweb/tornado)             |
| WebSockets binding | :heavy_check_mark:       | :heavy_check_mark: | [tornadoweb/tornado](https://github.com/tornadoweb/tornado)             |
|       CoAP binding | :heavy_multiplication_x: | :heavy_check_mark: | [chrysn/aiocoap](https://github.com/chrysn/aiocoap)                     |
|       MQTT binding | :heavy_multiplication_x: | :heavy_check_mark: | [beerfactory/hbmqtt](https://github.com/beerfactory/hbmqtt)             |
|     mDNS discovery | :heavy_multiplication_x: | :heavy_check_mark: | [jstasiak/python-zeroconf](https://github.com/jstasiak/python-zeroconf) |

## Couroutine APIs

WoTPy is based on the [Tornado Framework](https://www.tornadoweb.org). Users therefore have two different API options to write code based on coroutines:

- Users on **Python 3** may use the native [asyncio](https://docs.python.org/3/library/asyncio.html) module. This is, in fact, the recommended approach. It should be noted that Tornado on Python 3 acts basically [as a wrapper](https://www.tornadoweb.org/en/stable/asyncio.html) around `asyncio`.
- Users on **Python 2.7** are restricted to writing [Tornado coroutines](https://www.tornadoweb.org/en/stable/guide/coroutines.html) (`asyncio` is not available on Python 2.7).

## Installation

```
pip install wotpy
```

### Development

To install in development mode with all the test dependencies:

```
pip install -U -e .[tests]
```

To run the tests in all supported environments:

```
WOTPY_TESTS_MQTT_BROKER_URL=mqtt://broker-url tox
```

Some WoTPy features (e.g. CoAP binding) are not available outside of Linux. If you have Docker available in your system, and want to easily run the tests in a Linux environment (whether you're on macOS or Windows) you can use the Docker-based test script:

```
$ WOTPY_TESTS_MQTT_BROKER_URL=mqtt://192.168.1.141 ./pytest-docker-all.sh
...
+ docker run --rm -it -v /var/folders/zd/02pk7r3954s_t03lktjmvbdc0000gn/T/wotpy-547bed6bacf34ddc95b41eceb46553dd:/app -e WOTPY_TESTS_MQTT_BROKER_URL=mqtt://192.168.1.141 python:3.9 /bin/bash -c 'cd /app && pip install -U .[tests] && pytest -v --disable-warnings'
...
Python 2.7 :: OK
Python 3.6 :: OK
Python 3.7 :: OK
Python 3.8 :: OK
Python 3.9 :: OK
```

## Docs

Move to the `docs` folder and run:

```
make html
```

If you attempt to build the docs on a non-Linux platform or with Python 2.7 `_autosummary` will complain about being unable to import the unsupported modules (e.g. MQTT on Python 2.7). In this case the docs will be missing the sections regarding unsupported features.

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
# noinspection PyCompatibility
from concurrent.futures import ThreadPoolExecutor

# noinspection PyPackageRequirements
import pytest
import six
import tornado.gen
import tornado.ioloop
# noinspection PyPackageRequirements
from faker import Faker
from tornado.concurrent import Future

from wotpy.wot.dictionaries import PropertyInitDictionary
from wotpy.wot.enums import TDChangeMethod, TDChangeType


def test_read_property(exposed_thing, property_init):
    """Properties may be retrieved on ExposedThings."""

    @tornado.gen.coroutine
    def test_coroutine():
        prop_name = Faker().pystr()
        exposed_thing.add_property(prop_name, property_init)
        value = yield exposed_thing.read_property(prop_name)
        assert value == property_init.value

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)


def test_write_property(exposed_thing, property_init):
    """Properties may be updated on ExposedThings."""

    assert property_init.writable

    @tornado.gen.coroutine
    def test_coroutine():
        updated_val = Faker().pystr()
        prop_name = Faker().pystr()

        exposed_thing.add_property(prop_name, property_init)

        yield exposed_thing.write_property(prop_name, updated_val)

        value = yield exposed_thing.read_property(prop_name)

        assert value == updated_val

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)


def test_write_non_writable_property(exposed_thing):
    """Attempts to write a non-writable property should return an error."""

    prop_init_non_writable = PropertyInitDictionary({
        "type": "string",
        "writable": False
    })

    @tornado.gen.coroutine
    def test_coroutine():
        prop_name = Faker().pystr()
        exposed_thing.add_property(prop_name, prop_init_non_writable)

        with pytest.raises(Exception):
            yield exposed_thing.write_property(prop_name, Faker().pystr())

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)


def test_invoke_action(exposed_thing, action_init):
    """Actions can be invoked on ExposedThings."""

    thread_executor = ThreadPoolExecutor(max_workers=1)

    def upper_thread(val):
        return thread_executor.submit(lambda x: time.sleep(0.1) or str(x).upper(), val)

    def upper(val):
        loop = tornado.ioloop.IOLoop.current()
        return loop.run_in_executor(None, lambda x: time.sleep(0.1) or str(x).upper(), val)

    @tornado.gen.coroutine
    def lower(val):
        yield tornado.gen.sleep(0.1)
        raise tornado.gen.Return(str(val).lower())

    def title(val):
        future = Future()
        future.set_result(val.title())
        return future

    handlers_map = {
        upper_thread: lambda x: x.upper(),
        upper: lambda x: x.upper(),
        lower: lambda x: x.lower(),
        title: lambda x: x.title()
    }

    @tornado.gen.coroutine
    def test_coroutine():
        action_name = Faker().pystr()
        exposed_thing.add_action(action_name, action_init)

        for handler, assert_func in six.iteritems(handlers_map):
            exposed_thing.set_action_handler(action_handler=handler, action_name=action_name)
            action_arg = Faker().sentence(10)
            result = yield exposed_thing.invoke_action(action_name, val=action_arg)
            assert result == assert_func(action_arg)

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)


def test_invoke_action_undefined_handler(exposed_thing, action_init):
    """Actions with undefined handlers return an error."""

    @tornado.gen.coroutine
    def test_coroutine():
        action_name = Faker().pystr()
        exposed_thing.add_action(action_name, action_init)

        with pytest.raises(Exception):
            yield exposed_thing.invoke_action(action_name)

        @tornado.gen.coroutine
        def dummy_func():
            raise tornado.gen.Return(True)

        exposed_thing.set_action_handler(action_handler=dummy_func, action_name=action_name)

        result = yield exposed_thing.invoke_action(action_name)

        assert result

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)


def test_on_property_change(exposed_thing, property_init):
    """Property changes can be observed."""

    assert property_init.observable

    @tornado.gen.coroutine
    def test_coroutine():
        prop_name = Faker().pystr()
        exposed_thing.add_property(prop_name, property_init)

        observable_prop = exposed_thing.on_property_change(prop_name)

        property_values = Faker().pylist(5, True, *(str,))

        emitted_values = []

        def on_next_property_event(ev):
            emitted_values.append(ev.data.value)

        subscription = observable_prop.subscribe(on_next_property_event)

        for val in property_values:
            yield exposed_thing.write_property(prop_name, val)

        assert emitted_values == property_values

        subscription.dispose()

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)


def test_on_property_change_non_observable(exposed_thing, property_init):
    """Observe requests to non-observable properties are rejected."""

    prop_init_non_observable = PropertyInitDictionary({
        "type": "string",
        "writable": True,
        "observable": False
    })

    @tornado.gen.coroutine
    def test_coroutine():
        prop_name = Faker().pystr()
        exposed_thing.add_property(prop_name, prop_init_non_observable)

        observable_prop = exposed_thing.on_property_change(prop_name)

        future_next = Future()
        future_error = Future()

        def on_next(item):
            future_next.set_result(item)

        def on_error(err):
            future_error.set_exception(err)

        subscription = observable_prop.subscribe(on_next=on_next, on_error=on_error)

        yield exposed_thing.write_property(prop_name, Faker().pystr())

        with pytest.raises(Exception):
            future_error.result()

        assert not future_next.done()

        subscription.dispose()

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)


def test_on_event(exposed_thing, event_init):
    """Events defined in the Thing Description can be observed."""

    event_name = Faker().pystr()
    exposed_thing.add_event(event_name, event_init)

    observable_event = exposed_thing.on_event(event_name)

    event_payloads = [Faker().pystr() for _ in range(5)]

    emitted_payloads = []

    def on_next_event(ev):
        emitted_payloads.append(ev.data)

    subscription = observable_event.subscribe(on_next_event)

    for val in event_payloads:
        exposed_thing.emit_event(event_name, val)

    assert emitted_payloads == event_payloads

    subscription.dispose()


def test_on_td_change(exposed_thing, property_init, event_init, action_init):
    """Thing Description changes can be observed."""

    prop_name = Faker().pystr()
    event_name = Faker().pystr()
    action_name = Faker().pystr()

    observable_td = exposed_thing.on_td_change()

    complete_futures = {
        (TDChangeType.PROPERTY, TDChangeMethod.ADD): Future(),
        (TDChangeType.PROPERTY, TDChangeMethod.REMOVE): Future(),
        (TDChangeType.EVENT, TDChangeMethod.ADD): Future(),
        (TDChangeType.EVENT, TDChangeMethod.REMOVE): Future(),
        (TDChangeType.ACTION, TDChangeMethod.ADD): Future(),
        (TDChangeType.ACTION, TDChangeMethod.REMOVE): Future()
    }

    def on_next_td_event(ev):
        change_type = ev.data.td_change_type
        change_method = ev.data.method
        interaction_name = ev.data.name
        future_key = (change_type, change_method)
        complete_futures[future_key].set_result(interaction_name)

    subscription = observable_td.subscribe(on_next_td_event)

    exposed_thing.add_event(event_name, event_init)

    assert complete_futures[(TDChangeType.EVENT, TDChangeMethod.ADD)].result() == event_name
    assert not complete_futures[(TDChangeType.EVENT, TDChangeMethod.REMOVE)].done()

    exposed_thing.remove_event(name=event_name)
    exposed_thing.add_property(prop_name, property_init)

    assert complete_futures[(TDChangeType.EVENT, TDChangeMethod.REMOVE)].result() == event_name
    assert complete_futures[(TDChangeType.PROPERTY, TDChangeMethod.ADD)].result() == prop_name
    assert not complete_futures[(TDChangeType.PROPERTY, TDChangeMethod.REMOVE)].done()

    exposed_thing.remove_property(name=prop_name)
    exposed_thing.add_action(action_name, action_init)
    exposed_thing.remove_action(name=action_name)

    assert complete_futures[(TDChangeType.PROPERTY, TDChangeMethod.REMOVE)].result() == prop_name
    assert complete_futures[(TDChangeType.ACTION, TDChangeMethod.ADD)].result() == action_name
    assert complete_futures[(TDChangeType.ACTION, TDChangeMethod.REMOVE)].result() == action_name

    subscription.dispose()


def test_thing_property_get(exposed_thing, property_init):
    """Property values can be retrieved on ExposedThings using the map-like interface."""

    @tornado.gen.coroutine
    def test_coroutine():
        prop_name = Faker().pystr()
        exposed_thing.add_property(prop_name, property_init)
        value = yield exposed_thing.properties[prop_name].get()
        assert value == property_init.value

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)


def test_thing_property_set(exposed_thing, property_init):
    """Property values can be updated on ExposedThings using the map-like interface."""

    assert property_init.writable

    @tornado.gen.coroutine
    def test_coroutine():
        updated_val = Faker().pystr()
        prop_name = Faker().pystr()
        exposed_thing.add_property(prop_name, property_init)
        yield exposed_thing.properties[prop_name].set(updated_val)
        value = yield exposed_thing.properties[prop_name].get()
        assert value == updated_val

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)


def test_thing_property_subscribe(exposed_thing, property_init):
    """Property updates can be observed on ExposedThings using the map-like interface."""

    assert property_init.observable

    @tornado.gen.coroutine
    def test_coroutine():
        prop_name = Faker().pystr()
        exposed_thing.add_property(prop_name, property_init)

        property_values = [Faker().sentence() for _ in range(10)]

        emitted_values = []

        def on_next(ev):
            emitted_values.append(ev.data.value)

        subscription = exposed_thing.properties[prop_name].subscribe(on_next)

        for val in property_values:
            yield exposed_thing.properties[prop_name].set(val)

        assert emitted_values == property_values

        subscription.dispose()

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)

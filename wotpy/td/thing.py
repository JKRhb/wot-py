#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class that represents a Thing.
"""

import hashlib
import itertools
import uuid

# noinspection PyPackageRequirements
from slugify import slugify

from wotpy.td.interaction import Property, Action, Event


class Thing(object):
    """An abstraction of a physical or virtual entity whose metadata
    and interfaces are described by a WoT Thing Description."""

    def __init__(self, **kwargs):
        self.id = kwargs.pop("id")
        self._name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.support = kwargs.get("support")
        self._properties = {}
        self._actions = {}
        self._events = {}

    @property
    def name(self):
        """Thing name."""

        return self._name if self._name is not None else self.id

    @property
    def label(self):
        """Thing label (same as name for backward compatibility)."""

        return self.name

    @property
    def uuid(self):
        """Thing UUID in hex string format (e.g. a5220c5f-6bcb-4675-9c67-a2b1adc280b7).
        This value is deterministic and derived from the Thing ID.
        It may be of use in places where chars that can appear in an URI could be a problem."""

        hasher = hashlib.md5()
        hasher.update(self.id.encode())
        bytes_id_hash = hasher.digest()

        return str(uuid.UUID(bytes=bytes_id_hash))

    @property
    def url_name(self):
        """Returns the URL-safe name of this Thing."""

        return slugify("{}-{}".format(self._name, self.uuid)) if self._name else self.uuid

    @property
    def properties(self):
        """Properties interactions."""

        return self._properties

    @property
    def actions(self):
        """Actions interactions."""

        return self._actions

    @property
    def events(self):
        """Events interactions."""

        return self._events

    @property
    def interactions(self):
        """Sequence of interactions linked to this thing."""

        return itertools.chain(
            self._properties.values(),
            self._actions.values(),
            self._events.values())

    def find_interaction(self, name):
        """Finds an existing Interaction by name.
        The name argument may be the original name or the URL-safe version."""

        def is_match(intrct):
            return intrct.name == name or intrct.url_name == name

        return next((intrct for intrct in self.interactions if is_match(intrct)), None)

    def add_interaction(self, interaction):
        """Add a new Interaction."""

        assert isinstance(interaction, (Property, Event, Action))
        assert interaction.thing is self

        if self.find_interaction(interaction.name) is not None:
            raise ValueError("Duplicate Interaction: {}".format(interaction.name))

        interaction_dict_map = {
            Property: self._properties,
            Action: self._actions,
            Event: self._events
        }

        interaction_class = next(
            klass for klass in [Property, Action, Event]
            if isinstance(interaction, klass))

        interaction_dict_map[interaction_class][interaction.name] = interaction

    def remove_interaction(self, name):
        """Removes an existing Interaction by name.
        The name argument may be the original name or the URL-safe version."""

        interaction = self.find_interaction(name)

        if interaction is None:
            return

        self._properties.pop(interaction.name, None)
        self._actions.pop(interaction.name, None)
        self._events.pop(interaction.name, None)

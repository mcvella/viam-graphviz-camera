"""
This file registers the model with the Python SDK.
"""

from viam.components.camera import Camera

from viam.resource.registry import Registry, ResourceCreatorRegistration

from .graphViz import graphViz

Registry.register_resource_creator(Camera.SUBTYPE, graphViz.MODEL, ResourceCreatorRegistration(graphViz.new, graphViz.validate))

import asyncio
import sys
from typing import (Any, ClassVar, Dict, Final, List, Mapping, Optional,
                    Sequence, Tuple, cast)

from typing_extensions import Self
from viam.components.camera import *
from viam.gen import common, component
from viam.media.video import NamedImage, ViamImage
from viam.module.module import Module
from viam.proto.app.robot import ModuleConfig
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName, ResponseMetadata
from viam.proto.component.camera import GetPropertiesResponse
from viam.resource.base import ResourceBase
from viam.module.types import Reconfigurable
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes, struct_to_dict
from viam.components.generic import Generic as GenericComponent
from viam.services.generic import Generic as GenericService
from viam.components.sensor import Sensor
from viam.media.video import ViamImage
from viam.media.utils.pil import pil_to_viam_image, CameraMimeType
from viam.logging import getLogger

import pydot
import json
from PIL import Image 
import io
import requests as req

LOGGER = getLogger(__name__)

class graphViz(Camera, Reconfigurable):
    MODEL: ClassVar[Model] = Model(
        ModelFamily("mcvella", "camera"), "graphviz"
    )
    URL: str = ""
    RESOURCE: dict = {}

    @classmethod
    def new(cls, config: ModuleConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        my_class = cls(config.name)
        my_class.reconfigure(config, dependencies)
        return my_class

    @classmethod
    def validate(cls, config: ComponentConfig) -> Sequence[str]:
        attributes = struct_to_dict(config.attributes)
        deps = []
        source = attributes.get("source", {})
        if "type" in source:
            if source["type"] == "resource":
                if "resource_name" in source:
                    if ("resource_type" in source) and ("resource_subtype" in source) and ("resource_method" in source):
                        deps = [source["resource_name"]]
                    else:
                        raise Exception("resource_type, resource_subtype and resource_method must be defined if source type='resource'")
                else:
                    raise Exception("A resource_name must be defined if source type='resource'")
            elif source["type"] == "url":
                if not "url" in source:
                    raise Exception("A url must be defined if source type='url'")

        return deps

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        attributes = struct_to_dict(config.attributes)
        source = attributes.get("source", {})
        if "type" in source:
            if source["type"] == "resource":
                if source["resource_type"] == "component" and source["resource_subtype"] == "generic":
                    resource_dep = dependencies[GenericComponent.get_resource_name(source["resource_name"])]
                    resource = cast(GenericComponent, resource_dep)
                elif source["resource_type"] == "service" and source["resource_subtype"] == "generic":
                    resource_dep = dependencies[GenericService.get_resource_name(source["resource_name"])]
                    resource = cast(GenericService, resource_dep)
                elif source["resource_type"] == "component" and source["resource_subtype"] == "sensor":
                    resource_dep = dependencies[Sensor.get_resource_name(source["resource_name"])]
                    resource = cast(Sensor, resource_dep)

                self.RESOURCE["resource"] = resource
                self.RESOURCE["method"] = source["resource_method"]
                if "resource_payload" in source:
                    self.RESOURCE["payload"] = json.loads(source["resource_payload"].replace("'", "\""))
                if "result_key" in source:
                    self.RESOURCE["result_key"] = source["result_key"]
            elif source["type"] == "url":
                self.URL = source["url"]
        return

    async def get_image(
        self,
        mime_type: str = "",
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> ViamImage:
        
        # default to empty graph
        dot_string = """graph my_graph {
            }"""
        if dot_string in extra:
            dot_string = extra["dot_string"]
        elif self.URL != "":
            resp = req.get(self.URL)
            dot_string = resp.text
        elif "method" in self.RESOURCE != "":
            method = getattr(self.RESOURCE["resource"], self.RESOURCE["method"])
            dot_string = await method(**self.RESOURCE["payload"])
            if "result_key" in self.RESOURCE:
                dot_string = dot_string[self.RESOURCE["result_key"]]
        graphs = pydot.graph_from_dot_data(dot_string)
        graph = graphs[0]
        return pil_to_viam_image(Image.open(io.BytesIO(graph.create_jpg())), CameraMimeType.JPEG)

    async def get_images(
        self, *, timeout: Optional[float] = None, **kwargs
    ) -> Tuple[
        List[NamedImage], common.v1.common_pb2.ResponseMetadata
    ]:
        raise NotImplementedError()

    async def get_point_cloud(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Tuple[bytes, str]:
        raise NotImplementedError()

    async def get_properties(
        self, *, timeout: Optional[float] = None, **kwargs
    ) -> component.camera.v1.camera_pb2.GetPropertiesResponse:
        raise NotImplementedError()


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())


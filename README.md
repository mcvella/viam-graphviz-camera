# viam-graphviz-camera

Viam camera model that visualizes [Graphviz DOT](https://graphviz.org/doc/info/lang.html) input as diagram images.
The model this module makes available is *mcvella:camera:graphviz*

DOT input can be:

* Passed with each GetImage() call
* Retrieved via a configured URL
* Retrieved via another Viam Generic or Sensor resource

## API

The graphviz camera resource implements the [rdk camera API](https://github.com/rdk/camera-api), specifically get_image().

### get_image()

On each get_image() call, a rendered Graphviz diagram will be returned, based on either a DOT string passed with each call, or configured DOT input (see [Configuration](#configuration)).

To pass DOT with the *get_image()* extra parameter, pass:

#### dot_string (string)

A valid DOT string must be passed.

Example:

```python
camera.get_image(extra={"dot_string":"digraph G {a0 -> a1 -> a2 -> a3; label = 'process #1';}"})
```

## Configuration

Example attribute configuration with a URL as DOT source:

```json
{
    "source": {
        "type": "url",
        "url": "https://raw.githubusercontent.com/pinczakko/GraphViz-Samples/refs/heads/master/complex.dot"
    }
}
```

Example attribute configuration with a Viam sensor as a DOT source.

Note: only Viam generic components and services, and sensor components are currently supported.

This example calls get_readings() for the "event-manager" sensor component, passing a payload and retrieving the DOT result from the "dot" key in the returned response:

```json
{
  "source": {
    "type": "resource",
    "resource_name": "event-manager",
    "resource_type": "component",
    "resource_subtype": "sensor",
    "resource_method": "get_readings",
    "resource_payload": "{'extra': {'include_dot': true}}",
    "result_key": "dot"
  }
}
```

*source* attributes

### type (string, REQUIRED)

Either "url" (get DOT from a URL) or "resource" (get DOT from another configured Viam resource)

### url (string)

If "type" is configured as "url", set the URL from which to retrieve a valid DOT string from.

### resource_name (string)

If "type" is configured as "resource", "resource_name" is the name of the configured resource from which to retrieve DOT output.

### resource_type (string)

If "type" is configured as "resource", "resource_type" is the type of the configured resource from which to retrieve DOT output, either "component" or "service".

### resource_subtype (string)

If "type" is configured as "resource", "resource_subtype" is the subtype of the configured resource from which to retrieve DOT output, currently "generic" and "sensor" are supported.

### resource_method (string)

If "type" is configured as "resource", "resource_method" is the name of the configured resource method to call in order to retrieve DOT output - for example get_readings().
Note that this module uses the [Viam Python SDK](https://python.viam.dev/), so use the corresponding Python SDK methods.

### resource_payload (string)

If "type" is configured as "resource", "resource_payload" is optional stringified JSON to pass into the specified "resource_method" in order to retrieve DOT output.
Single quotes will be converted into double quotes so that the JSON input is valid.

### result_key (string)

If "type" is configured as "resource", "result_key" is optional key from which to retrieve DOT output from the response returned from "resource_method".
For example, you might pass "dot_here" as the "result_key" if the returned response looks like:

``` json
{
    "stuff": {"not": "dot"},
    "dot_here": "digraph G {a0 -> a1 -> a2 -> a3; label = 'process #1';}"
}
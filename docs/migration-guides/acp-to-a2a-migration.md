# ACP to A2A Migration (0.3.x BeeAI Platform)

The BeeAI platform is migrating to A2A starting with version 0.3.x. The team has worked hard to make the migration of your agents as seamless as possible. This guide provides practical examples and explains the reasoning behind the changes.

## Abandoning `acp_sdk` in Favor of `beeai_sdk`

The most prominent change is the deprecation of the `acp_sdk` dependency in favor of `beeai_sdk`. Most previously available features are now included in the new package.

BeeAI allows you to build fully compatible A2A agents either from the ground up using the official A2A SDK or by leveraging `beeai_sdk` for higher-level constructs. As a result, usage of the SDK remains very similar to ACP.

For example, a pre-0.3.0 agent implementation:

```python
import os
from collections.abc import AsyncGenerator


from acp_sdk import Annotations, MessagePart, Metadata
from acp_sdk.models import Message
from acp_sdk.models.platform import PlatformUIAnnotation, PlatformUIType
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

server = Server()

@server.agent(
    metadata=Metadata(
        annotations=Annotations(
            beeai_ui=PlatformUIAnnotation(ui_type=PlatformUIType.HANDSOFF)
        )
    )
)
async def example_agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Polite agent that greets the user"""
    yield "Hello World!"


def run():
    server.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)))


if __name__ == "__main__":
    run()
```

Now, with `beeai_sdk`, you can use a very similar approach:

```python
import os

from a2a.types import (
    AgentCapabilities,
    Message,
)
from beeai_sdk.server import Server
from beeai_sdk.server.context import Context
from beeai_sdk.a2a.extensions import AgentDetail

server = Server()

@server.agent(
    detail=AgentDetail(ui_type="hands-off"),
    capabilities=AgentCapabilities(
        streaming=True,
    )
)
async def example_agent(input: Message, context: Context):
    """Polite agent that greets the user"""
    yield "Hello World!"

def run():
    server.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)))
```


## Core Changes

**Capabilities are mandatory**

The BeeAI UI expects all agents to be streaming-capable. You must provide the streaming capability for your agent to run on the platform.

**`Metadata` Has Been Removed in Favor of A2A Extensions**

Since A2A is a natively extensible protocol, we've adopted extensions to allow agent developers to specify metadata that enables parameterization of agents on the BeeAI platform.

**`AgentDetail` Replaces `beeai_ui` Metadata**

When defining `@server.agent`, the beeai_ui metadata has been replaced with `AgentDetail`. This allows you to specify fields specific to the BeeAI UI.

The SDK internally converts `AgentDetail` into an A2A-compatible extension (`AgentDetailExtension`). `AgentDetail` only exists to simplify the agent setup process.

## Extensions

As previously mentioned, BeeAI heavily relies on A2A extensions. The first and most visible extension is `AgentDetail`, which is deeply integrated into the SDK for a seamless experience. However, the SDK also exposes other extensions you can use. More coming soon.

BeeAI organizes extensions into two logical categories:

- **UI extensions** - Extend the protocol with UI-specific semantics.
- **Service extensions** - Represent services provided by the platform that agents can request, similar to Dependency Injection.


### Implemented UI extensions

There are currently three UI extensions available:

- Citations
- Trajectory
- AgentDetails

These serve as direct replacements for `CitationMetadata`, `TrajectoryMetadata` and `PlatformUIAnnotation` from the ACP.

More extensions will be introduced as the platform evolves to support increasingly complex GUI components and parameterization.


#### Citation Extension
The Citation Extension is a direct replacement for `CitationMetadata` from the ACP and follows the same specification. You must inject the extension using the `Annotated[TrajectoryExtensionServer, TrajectoryExtensionSpec()]` construct and then use it to yield a citation, which has the same structure as `CitationMetadata` in the ACP.

```python
import os
from typing import Annotated

from a2a.types import AgentCapabilities
from beeai_sdk.server import Server
from beeai_sdk.a2a.extensions import AgentDetail
from beeai_sdk.a2a.extensions.ui.trajectory import TrajectoryExtensionServer, TrajectoryExtensionSpec

server = Server()

@server.agent(
    detail=AgentDetail(ui_type="chat"),
    capabilities=AgentCapabilities(
        streaming=True,
    ),
)
async def example_agent(trajectory: Annotated[TrajectoryExtensionServer, TrajectoryExtensionSpec()]):
    """Polite agent that greets the user"""
    yield trajectory.trajectory_metadata(title="Hello", content="World")


def run():
    server.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)))


if __name__ == "__main__":
    run()
```


#### Trajectory Extension

The Trajectory Extension replaces `TrajectoryMetadata` from the ACP. We've simplified its specification to include just `title` and `content`. It is injected in the same way as the citation extension:


```python
import os
from typing import Annotated

from a2a.types import AgentCapabilities
from beeai_sdk.server import Server
from beeai_sdk.a2a.extensions import AgentDetail
from beeai_sdk.a2a.extensions.ui.trajectory import TrajectoryExtensionServer, TrajectoryExtensionSpec

server = Server()


@server.agent(
    detail=AgentDetail(ui_type="chat"),
    capabilities=AgentCapabilities(
        streaming=True,
    ),
)
async def example_agent(trajectory: Annotated[TrajectoryExtensionServer, TrajectoryExtensionSpec()]):
    """Polite agent that greets the user"""
    yield trajectory.trajectory_metadata(title="Hello", content="World")


def run():
    server.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)))


if __name__ == "__main__":
    run()
```

#### Agent Detail Extension


The Agent Detail Extension replaces `PlatformUIAnnotation` from the ACP. It provides metadata required by the platform to parameterize the agent's UI. See the `AgentDetail` type definition for a full list of supported parameters. You can provide the `AgentDetail` to `@server.agent` decorator and there's no need to extra injection.


```python
import os

from a2a.types import AgentCapabilities
from beeai_sdk.server import Server
from beeai_sdk.a2a.extensions import AgentDetail, AgentDetailTool

server = Server()

@server.agent(
    detail=AgentDetail(
        ui_type='chat',
        display_name="Chat Agent",
        description=(
            "Conversational agent with memory, supporting real-time search, "
            "Wikipedia lookups, and weather updates through integrated tools"
        ),
        user_greeting="Hello! I'm your AI assistant. How can I help you today?",
        tools=[
            AgentDetailTool(name="Weather", description=""),
            AgentDetailTool(name="Wikipedia", description=""),
            AgentDetailTool(
                name="Google Search", description=""
            ),
        ],
        framework="BeeAI",
        author={
            "name": "John Smith",
            "email": "jsmith@example.com",
            "url": "https://example.com"
        }
    ),
    capabilities=AgentCapabilities(
        streaming=True,
    ),
)
async def example_agent():
    """Agent Details Example"""
    yield "Hello World!"


def run():
    server.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)))


if __name__ == "__main__":
    run()
```
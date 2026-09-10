# HENU OS Application Specification: henu-ai

> **System Component: Core AI Stack**  
> **Package Identifier: henu-ai**  
> **Status: Specification Draft**

---

## 1. Purpose
Provides the background AI runtime environment, handling model loads, prompt generation, context memory, and secure local model execution. It acts as the central interface broker between offline neural models and user applications.

## 2. Features
- **Local Model Loader**: Dynamically load ONNX or GGUF formatted local LLMs.
- **Unified Query API**: Local socket API interface that system apps connect to for intelligence prompts.
- **Context memory broker**: Manages session-based text history and user interaction logs.
- **System Prompt Templates**: Preset security templates ensuring AI safety rules.

## 3. Dependencies
- `python3-onnxruntime`
- `python3-numpy`
- `llama.cpp` CLI wrapper
- `openblas`

## 4. Permissions
- **Network**: Denied by default (fully local model execution).
- **FileSystem**: Read access to `/usr/share/henu/models/`; write access to local user temp path (`~/.cache/henu-ai/`).
- **Process**: Restricted from spawning root privileges.

## 5. User Interface (UI)
None (Daemon/System Service). Exposes a local UNIX socket at `/run/henu-ai.sock`.

## 6. Future Roadmap
- Integration with local hardware NPUs (Intel/AMD/NVIDIA).
- Voice and audio transcoding engine integration.

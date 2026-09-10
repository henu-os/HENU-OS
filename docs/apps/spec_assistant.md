# HENU OS Application Specification: henu-assistant

> **System Component: Desktop Assistant Interface**  
> **Package Identifier: henu-assistant**  
> **Status: Specification Draft**

---

## 1. Purpose
Provides a graphical desktop conversational interface that queries the local `henu-ai` daemon, assisting developers and operators with queries, code snippets, and OS automation tasks.

## 2. Features
- **Sidebar Chat Panel**: Integrated screen panel for text chat.
- **Voice Commands Handler**: Microphone transcription interface.
- **Developer helper modes**: Code syntax highlights and terminal command generation.

## 3. Dependencies
- `gtk4`
- `henu-ai` local service
- `whisper-cpp` (for speech-to-text)

## 4. Permissions
- **Socket Network**: Connect to `/run/henu-ai.sock` socket.
- **Hardware**: Access to system microphone input devices.
- **FileSystem**: Read access to user folders to process code contextual files.

## 5. User Interface (UI)
Modern floating GTK panel (responsive window layout) with voice level indicator and formatted markdown viewer.

## 6. Future Roadmap
- Direct terminal script executor hooks with security confirmation checks.
- Adaptive desktop screen contexts scanning.

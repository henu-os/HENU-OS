# HENU OS 3.0 — Testing & QA Subsystem

This workspace houses automated boot verification and developer testing harnesses.

## 🧪 Testing Layers

1. **Automated QEMU Test (`testing/qemu/`)**:
   - Executes headless QEMU boot test during ISO build verification (Stage 17).
   - Validates kernel startup, initramfs mounting, and systemd readiness.

2. **Developer VirtualBox / Desktop Testing (`testing/virtualbox/`)**:
   - For interactive manual verification of visual themes, animations, audio, and GNOME Shell integrations.

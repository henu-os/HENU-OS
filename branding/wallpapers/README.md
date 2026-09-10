# wallpapers/

All HENU OS wallpaper images go here.

## Resolution Requirements

| Folder | Resolution | Format | Use Case |
|---|---|---|---|
| `official/4k/` | 3840×2160 | JPG (Q95) or PNG | 4K display default |
| `official/2k/` | 2560×1440 | JPG (Q95) or PNG | 2K display default |
| `official/fhd/` | 1920×1080 | JPG (Q95) or PNG | FHD display default |
| `login/` | 1920×1080 | PNG (lossless) | GDM login screen |
| `lockscreen/` | 1920×1080 | PNG (lossless) | Lock screen |
| `installer/` | 1920×1080 | PNG (lossless) | Calamares installer |
| `grub/` | 1920×1080 | PNG (lossless) | GRUB boot background |
| `plymouth/` | 1920×1080 | PNG (lossless) | Plymouth boot animation |

## Naming Pattern

```
henu-wallpaper-[name]-[width]x[height].[ext]

Examples:
  henu-wallpaper-default-3840x2160.jpg
  henu-wallpaper-default-1920x1080.jpg
  henu-wallpaper-circuit-1920x1080.jpg
```

## Color Profile

- All wallpapers must be exported in **sRGB** color space.
- Installer and GRUB images: **no ICC profile embedded** (use raw sRGB).
- File size targets: 4K < 6MB, FHD < 2MB, system images < 1MB.

# LAN Offline Guide

## Fixed Workflow (Recommended)
1. Manually replace student folders/files under:
   - `local_media/学号_姓名/pre_plant_1.*`
   - `local_media/学号_姓名/pre_plant_2.*`
   - `local_media/学号_姓名/pre_plant_3.*`
   - `local_media/学号_姓名/pre_record_card.*`
2. Run DB URL rebuild:
```powershell
python .\rebuild_pre_media_urls_from_local.py
```

## Optional
- Preview only:
```powershell
python .\rebuild_pre_media_urls_from_local.py --dry-run
```
- Clear DB field when local file missing:
```powershell
python .\rebuild_pre_media_urls_from_local.py --clear-missing
```

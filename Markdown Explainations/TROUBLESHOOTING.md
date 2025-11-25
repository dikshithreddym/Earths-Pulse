# Troubleshooting Guide

## Sidebar is Now Visible ✅

The sidebar animation has been fixed - it now starts visible instead of sliding in from the left.

## Module Export Errors

If you're still seeing errors like "'cos' is not exported from 'three/tsl'", try:

1. **Stop the dev server** (Ctrl+C)

2. **Clear all caches:**
   ```powershell
   Remove-Item -Recurse -Force .next
   Remove-Item -Recurse -Force node_modules/.cache -ErrorAction SilentlyContinue
   ```

3. **Reapply patches:**
   ```powershell
   npx patch-package three three-globe
   ```

4. **Verify patches are applied:**
   ```powershell
   # Check if files exist
   Test-Path node_modules/three/tsl.js
   Test-Path node_modules/three/webgpu.js
   
   # Check exports
   Get-Content node_modules/three/tsl.js | Select-String "export.*cos"
   ```

5. **Restart dev server:**
   ```powershell
   npm run dev
   ```

## Globe is Black / No Data

The globe might be black because there's no data. To seed data:

1. **Make sure backend is running** (should be on port 8000)

2. **Trigger data refresh:**
   - Visit: http://localhost:8000/api/moods/refresh (POST request)
   - Or use curl: `curl -X POST http://localhost:8000/api/moods/refresh`

3. **Or seed data manually:**
   ```powershell
   cd ..\backend
   # Activate venv first
   venv\Scripts\activate
   python scripts/seed_data.py
   ```

## If Module Errors Persist

The patches should work, but if Next.js still complains:

1. The exports ARE in the files - check `node_modules/three/tsl.js`
2. Next.js might be doing static analysis before patches apply
3. Try a hard refresh in browser (Ctrl+Shift+R)
4. Check browser console for actual runtime errors vs build warnings

The warnings might be non-blocking - check if the app actually works despite the warnings.


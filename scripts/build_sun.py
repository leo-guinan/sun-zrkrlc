#!/usr/bin/env python3
from __future__ import annotations
import runpy
from pathlib import Path
factory=Path(__file__).resolve().parents[2].parent/'community-solar-systems-factory'/'scripts'/'generate_account_repos.py'
if not factory.exists():
    print('Factory not found; sun.json left unchanged. Run the factory rebuild to regenerate this repo.')
else:
    ns=runpy.run_path(str(factory))
    username=Path('README.md').read_text().split('@',1)[1].split()[0].strip('`.,')
    ns['build_sun'](Path('.'), username.lower())
    print('wrote sun.json')

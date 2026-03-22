#!/usr/bin/env python3
"""Batch image analysis runner for 镖人2 project."""

import json
import os
import sys
import time
import subprocess
import re

JOBS_FILE = "/Users/wangsha886/.openclaw/workspace/temp_assets/core_analysis_jobs.json"
OUTPUT_FILE = "/Users/wangsha886/.openclaw/workspace/temp_assets/project_index.json"

# Mapping from Desktop original paths to temp_assets paths
# Desktop: /Users/wangsha886/Desktop/资产/人设定稿/<key>/<name>
# temp_assets/characters: /Users/wangsha886/.openclaw/workspace/temp_assets/characters/<name>
# temp_assets/scenes: /Users/wangsha886/.openclaw/workspace/temp_assets/scenes/<name>
# temp_assets/props: /Users/wangsha886/.openclaw/workspace/temp_assets/props/<name>

CATEGORY_MAP = {
    "characters": "/Users/wangsha886/.openclaw/workspace/temp_assets/characters",
    "scenes": "/Users/wangsha886/.openclaw/workspace/temp_assets/scenes",
    "props": "/Users/wangsha886/.openclaw/workspace/temp_assets/props",
}

ANALYSIS_PROMPT = '''分析这张图片，输出JSON：{"description":"一句话描述","tags":["关键词1","关键词2"],"scene":"场景类型","has_people":true或false,"has_character":"角色名或null","mood":"氛围","time_of_day":"时间"}'''


def find_actual_path(category, filename):
    """Find the actual file path in temp_assets."""
    base_dir = CATEGORY_MAP.get(category)
    if not base_dir:
        return None
    
    # Try exact match first
    exact = os.path.join(base_dir, filename)
    if os.path.exists(exact):
        return exact
    
    # Try without (1), (2) etc suffixes in filename
    # e.g., "镖人2-杨勇贴身侍卫-推面.png" might be "镖人2-杨勇贴身侍卫-推面(1).png"
    name_without_ext = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1]
    
    # Try removing (1), (2) etc from the name
    clean_name = re.sub(r'\(\d+\)$', '', name_without_ext)
    if clean_name != name_without_ext:
        clean_path = os.path.join(base_dir, clean_name + ext)
        if os.path.exists(clean_path):
            return clean_path
    
    # Try adding (1) - common pattern
    for suffix in ['(1)', '(2)', '(1)(1)']:
        trial = os.path.join(base_dir, name_without_ext + suffix + ext)
        if os.path.exists(trial):
            return trial
    
    return None


def get_image_path_from_job(job):
    """Get the actual accessible path for a job."""
    category = job.get("category", "characters")
    name = job.get("name", "")
    
    # The Desktop path is not accessible to image tool
    # Try to find in temp_assets
    actual = find_actual_path(category, name)
    if actual:
        return actual
    
    # Fallback: construct from temp_assets base
    base = CATEGORY_MAP.get(category)
    if base:
        fallback = os.path.join(base, name)
        if os.path.exists(fallback):
            return fallback
    
    return None


def call_image_tool(image_path):
    """Call the image tool via subprocess/openclaw CLI."""
    # Use openclaw analyze or similar command
    # Actually, we need to use the tool directly - let's try a different approach
    # We'll use the openclaw CLI if available, or just call it via a script that
    # generates the tool call
    
    # For now, let's use a simple approach: write a temporary script that
    # calls the image tool via openclaw's internal mechanism
    pass


def main():
    with open(JOBS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jobs = data.get('images', [])
    print(f"Loaded {len(jobs)} jobs")
    
    # First, map all jobs to actual paths
    path_map = {}
    missing = []
    for job in jobs:
        key = job.get('key', job.get('name', 'unknown'))
        actual = get_image_path_from_job(job)
        if actual:
            path_map[key] = actual
        else:
            path_map[key] = None
            missing.append((key, job.get('name', ''), job.get('category', '')))
    
    print(f"\nFound paths for {len(jobs) - len(missing)}/{len(jobs)} images")
    if missing:
        print(f"\nMissing ({len(missing)}):")
        for k, n, c in missing[:10]:
            print(f"  {c}: {n} (key: {k})")
        if len(missing) > 10:
            print(f"  ... and {len(missing)-10} more")
    
    # Save the path mapping for reference
    mapping_file = "/Users/wangsha886/.openclaw/workspace/temp_assets/path_mapping.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump({k: v for k, v in path_map.items()}, f, ensure_ascii=False, indent=2)
    print(f"\nPath mapping saved to {mapping_file}")
    
    # Output the resolved paths
    print("\nResolved paths sample:")
    for i, (k, v) in enumerate(list(path_map.items())[:5]):
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()

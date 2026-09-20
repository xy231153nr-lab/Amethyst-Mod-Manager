"""
resolver.py
Check installed Nexus mods for missing requirements (dependencies) and then resolve open permision dependencies
Workflow:
 1. Get list of missing requirements
 2. Figure out what needs to be resolved
 3. auto-resolve open permision dependencies
 4. Prompt user to install closed permisoin dependecies
 """
from __future__ import annotations
from dataclasses import dataclass,field,replace
from pathlib import Path
from typing import Callable,Optional
import requests
# Game scope: None = apply to all games; str = Nexus game domain (e.g. "fallout4", "skyrimspecialedition")
GameScope=Optional[str]
from Nexus.nexus_api import NexusAPI,NexusModRequirement,NexusModUpdateInfo
from Nexus.nexus_meta import(NexusModMeta,normalise_game_domain,scan_installed_mods,write_meta)
from Utils.config_paths import get_requirement_external_tool_mod_ids_path
from Utils.ca_bundle import resolve_ca_bundle
ProgressCallback=Callable[[str], None]
# Remote list of mod IDs to treat as external tools (script extenders, xEdit, etc.).
# Fetched on each requirement check; new IDs are merged into the local cache.
REQUIREMENT_FILTER_URL=("https://raw.githubusercontent.com/ChrisDKN/Amethyst-Mod-Manager/main/src/Nexus/updatefilter.txt")_FETCH_TIMEOUT=10
@dataclass
class MissingRequirementInfo:
	mod_name:str
	mod_id:int
	missing:list[NexusModRequirement]=field(default_factory=list)
def _parse_filter_text(text:str,)->tuple[set[tuple[GameScope,int]],dict[tuple[GameScope,int],set[int]],dict[tuple[GameScope,int],tuple[int,str]],]:

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DependencyRecipe:
    name: str
    category: str
    winetricks_packages: tuple[str, ...]
    notes: str
    reboot_recommended: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "winetricks_packages": list(self.winetricks_packages),
            "notes": self.notes,
            "reboot_recommended": self.reboot_recommended,
        }


RECIPES: dict[str, DependencyRecipe] = {
    "directx9": DependencyRecipe(
        name="directx9",
        category="graphics",
        winetricks_packages=("d3dx9", "d3dcompiler_43"),
        notes="Older games and 3D apps often need DirectX 9 helper DLLs.",
    ),
    "directx10_11": DependencyRecipe(
        name="directx10_11",
        category="graphics",
        winetricks_packages=("d3dcompiler_47", "dxvk"),
        notes="Modern Direct3D 10/11 apps usually need DXVK plus compiler DLLs when supported by the runner.",
    ),
    "vcrun2010": DependencyRecipe(
        name="vcrun2010",
        category="runtime",
        winetricks_packages=("vcrun2010",),
        notes="Visual C++ 2010 runtime.",
    ),
    "vcrun2015_2022": DependencyRecipe(
        name="vcrun2015_2022",
        category="runtime",
        winetricks_packages=("vcrun2022",),
        notes="Common runtime for many modern Windows desktop apps.",
    ),
    "dotnet48": DependencyRecipe(
        name="dotnet48",
        category="runtime",
        winetricks_packages=("dotnet48",),
        notes=".NET Framework 4.8. Heavy and sometimes fragile. Use only when the app requires it.",
        reboot_recommended=True,
    ),
    "corefonts": DependencyRecipe(
        name="corefonts",
        category="fonts",
        winetricks_packages=("corefonts",),
        notes="Common Microsoft fonts for UI/layout compatibility.",
    ),
    "maker_3d_basic": DependencyRecipe(
        name="maker_3d_basic",
        category="bundle",
        winetricks_packages=("vcrun2022", "corefonts", "d3dcompiler_47"),
        notes="Baseline for slicers, viewers, and light CAD utilities before adding heavier graphics layers.",
    ),
    "maker_3d_dxvk": DependencyRecipe(
        name="maker_3d_dxvk",
        category="bundle",
        winetricks_packages=("vcrun2022", "corefonts", "d3dcompiler_47", "dxvk"),
        notes="Maker/3D profile with DXVK for Direct3D translation when GPU support is available.",
    ),
}


def list_recipes() -> list[dict[str, Any]]:
    return [recipe.to_dict() for recipe in RECIPES.values()]


def get_recipe(name: str) -> DependencyRecipe:
    key = name.strip().lower()
    if key not in RECIPES:
        known = ", ".join(sorted(RECIPES))
        raise KeyError(f"Unknown dependency recipe '{name}'. Known recipes: {known}")
    return RECIPES[key]


def winetricks_command(recipe_name: str, prefix_path: str) -> list[str]:
    recipe = get_recipe(recipe_name)
    return ["env", f"WINEPREFIX={prefix_path}", "winetricks", "-q", *recipe.winetricks_packages]

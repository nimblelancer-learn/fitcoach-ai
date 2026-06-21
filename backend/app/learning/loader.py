from __future__ import annotations

import tomllib
from importlib import import_module
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.learning.models import (
    FlowPage,
    GlossaryEntry,
    LearningPortalContent,
    ModulePage,
    OverviewPage,
)


class LearningContentError(RuntimeError):
    """Raised when curated learning content is invalid."""


def load_learning_portal(
    content_dir: Path | None = None,
) -> LearningPortalContent:
    base_dir = content_dir or Path(__file__).resolve().parent / "content"

    overview = _load_model(base_dir / "overview.toml", OverviewPage)

    modules = _load_collection(
        base_dir / "modules",
        ModulePage,
    )
    flows = _load_collection(
        base_dir / "flows",
        FlowPage,
    )
    glossary = _load_collection(
        base_dir / "glossary",
        GlossaryEntry,
        required=False,
    )

    portal = LearningPortalContent(
        overview=overview,
        modules=modules,
        flows=flows,
        glossary=glossary,
    )
    _validate_references(portal)
    return portal


def _load_collection(
    directory: Path,
    model_type: type[ModulePage] | type[FlowPage] | type[GlossaryEntry],
    *,
    required: bool = True,
) -> dict[str, Any]:
    if not directory.exists():
        if required:
            raise LearningContentError(
                f"Missing learning content directory: {directory}",
            )
        return {}

    items: dict[str, Any] = {}

    for path in sorted(directory.glob("*.toml")):
        item = _load_model(path, model_type)
        slug = item.slug

        if slug in items:
            raise LearningContentError(
                f"Duplicate learning content slug '{slug}' in {path}",
            )

        items[slug] = item

    return items


def _load_model(path: Path, model_type: type[Any]) -> Any:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LearningContentError(
            f"Missing learning content file: {path}",
        ) from exc
    except tomllib.TOMLDecodeError as exc:
        raise LearningContentError(
            f"Invalid TOML in {path}: {exc}",
        ) from exc

    try:
        return model_type.model_validate(data)
    except ValidationError as exc:
        raise LearningContentError(
            f"Invalid learning content schema in {path}: {exc}",
        ) from exc


def _validate_references(portal: LearningPortalContent) -> None:
    for module_page in portal.modules.values():
        _import_module(module_page.module_path, module_page.slug)

        for function_entry in module_page.key_functions:
            _resolve_python_path(
                function_entry.python_path,
                f"module '{module_page.slug}' key function '{function_entry.name}'",
            )

        for related_slug in module_page.related_modules:
            if related_slug not in portal.modules:
                raise LearningContentError(
                    f"Unknown related module slug '{related_slug}' "
                    f"referenced by module '{module_page.slug}'",
                )

        for related_slug in module_page.related_flows:
            if related_slug not in portal.flows:
                raise LearningContentError(
                    f"Unknown related flow slug '{related_slug}' "
                    f"referenced by module '{module_page.slug}'",
                )

    for flow_page in portal.flows.values():
        for related_slug in flow_page.related_modules:
            if related_slug not in portal.modules:
                raise LearningContentError(
                    f"Unknown related module slug '{related_slug}' "
                    f"referenced by flow '{flow_page.slug}'",
                )

        for step in flow_page.steps:
            if step.module_path:
                _import_module(
                    step.module_path,
                    f"flow '{flow_page.slug}' step '{step.title}'",
                )

            if step.python_path:
                _resolve_python_path(
                    step.python_path,
                    f"flow '{flow_page.slug}' step '{step.title}'",
                )

    for featured_module in portal.overview.featured_modules:
        if featured_module not in portal.modules:
            raise LearningContentError(
                f"Unknown featured module slug '{featured_module}' referenced by overview",
            )

    for featured_flow in portal.overview.featured_flows:
        if featured_flow not in portal.flows:
            raise LearningContentError(
                f"Unknown featured flow slug '{featured_flow}' referenced by overview",
            )

    for glossary_entry in portal.glossary.values():
        for related_slug in glossary_entry.related_modules:
            if related_slug not in portal.modules:
                raise LearningContentError(
                    f"Unknown related module slug '{related_slug}' "
                    f"referenced by glossary entry '{glossary_entry.slug}'",
                )


def _import_module(module_path: str, context: str) -> None:
    try:
        import_module(module_path)
    except ModuleNotFoundError as exc:
        raise LearningContentError(
            f"Unknown module path '{module_path}' referenced by {context}",
        ) from exc


def _resolve_python_path(python_path: str, context: str) -> object:
    module_path, _, attribute_name = python_path.rpartition(".")

    if not module_path or not attribute_name:
        raise LearningContentError(
            f"Invalid python_path '{python_path}' referenced by {context}",
        )

    module = import_module(module_path)

    if not hasattr(module, attribute_name):
        raise LearningContentError(
            f"Unknown function path '{python_path}' referenced by {context}",
        )

    return getattr(module, attribute_name)

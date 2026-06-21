from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.learning.models import LearningPortalContent

router = APIRouter(prefix="/__learn", tags=["Internal"])

templates = Jinja2Templates(
    directory=str(
        Path(__file__).resolve().parent.parent / "learning" / "templates",
    ),
)


def _render_disabled_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="disabled.html",
        context={
            "flag_name": "ENABLE_DEV_LEARNING_PORTAL",
        },
        status_code=404,
    )


def _get_learning_portal(
    request: Request,
) -> LearningPortalContent | None:
    settings = request.app.state.settings

    if not settings.enable_dev_learning_portal:
        return None

    return getattr(request.app.state, "learning_portal", None)


@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def learning_overview(request: Request) -> HTMLResponse:
    portal = _get_learning_portal(request)

    if portal is None:
        return _render_disabled_page(request)

    featured_modules = [portal.modules[slug] for slug in portal.overview.featured_modules]
    featured_flows = [portal.flows[slug] for slug in portal.overview.featured_flows]

    return templates.TemplateResponse(
        request=request,
        name="overview.html",
        context={
            "overview": portal.overview,
            "featured_modules": featured_modules,
            "featured_flows": featured_flows,
            "module_count": len(portal.modules),
            "flow_count": len(portal.flows),
            "glossary_count": len(portal.glossary),
        },
    )


@router.get(
    "/modules/{slug}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def learning_module_detail(
    slug: str,
    request: Request,
) -> HTMLResponse:
    portal = _get_learning_portal(request)

    if portal is None:
        return _render_disabled_page(request)

    module_page = portal.modules.get(slug)

    if module_page is None:
        return templates.TemplateResponse(
            request=request,
            name="not_found.html",
            context={
                "item_type": "module",
                "slug": slug,
                "return_path": "/__learn",
            },
            status_code=404,
        )

    related_modules = [portal.modules[related_slug] for related_slug in module_page.related_modules]
    related_flows = [portal.flows[related_slug] for related_slug in module_page.related_flows]
    related_glossary_entries = sorted(
        [entry for entry in portal.glossary.values() if module_page.slug in entry.related_modules],
        key=lambda entry: entry.term.lower(),
    )

    return templates.TemplateResponse(
        request=request,
        name="module_detail.html",
        context={
            "module_page": module_page,
            "related_modules": related_modules,
            "related_flows": related_flows,
            "related_glossary_entries": related_glossary_entries,
        },
    )


@router.get(
    "/flows/{slug}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def learning_flow_detail(
    slug: str,
    request: Request,
) -> HTMLResponse:
    portal = _get_learning_portal(request)

    if portal is None:
        return _render_disabled_page(request)

    flow_page = portal.flows.get(slug)

    if flow_page is None:
        return templates.TemplateResponse(
            request=request,
            name="not_found.html",
            context={
                "item_type": "flow",
                "slug": slug,
                "return_path": "/__learn",
            },
            status_code=404,
        )

    related_modules = [portal.modules[related_slug] for related_slug in flow_page.related_modules]

    return templates.TemplateResponse(
        request=request,
        name="flow_detail.html",
        context={
            "flow_page": flow_page,
            "related_modules": related_modules,
        },
    )


@router.get(
    "/glossary",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def learning_glossary(request: Request) -> HTMLResponse:
    portal = _get_learning_portal(request)

    if portal is None:
        return _render_disabled_page(request)

    glossary_entries = sorted(
        portal.glossary.values(),
        key=lambda entry: entry.term.lower(),
    )

    related_modules = {
        entry.slug: [portal.modules[related_slug] for related_slug in entry.related_modules]
        for entry in glossary_entries
    }

    return templates.TemplateResponse(
        request=request,
        name="glossary.html",
        context={
            "glossary_entries": glossary_entries,
            "related_modules": related_modules,
        },
    )

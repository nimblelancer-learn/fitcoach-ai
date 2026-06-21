from pydantic import BaseModel, ConfigDict, Field


class LearningBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class KeyFunctionEntry(LearningBaseModel):
    name: str
    python_path: str
    summary: str
    why_it_matters: str


class ModulePage(LearningBaseModel):
    slug: str
    title: str
    module_path: str
    summary: str
    why_it_exists: str
    when_it_runs: str
    dependencies: list[str] = Field(default_factory=list)
    used_by: list[str] = Field(default_factory=list)
    safe_edit_notes: list[str] = Field(default_factory=list)
    related_modules: list[str] = Field(default_factory=list)
    related_flows: list[str] = Field(default_factory=list)
    key_functions: list[KeyFunctionEntry] = Field(default_factory=list)


class FlowStep(LearningBaseModel):
    title: str
    description: str
    module_path: str | None = None
    python_path: str | None = None


class FlowPage(LearningBaseModel):
    slug: str
    title: str
    summary: str
    why_it_matters: str
    when_to_read: str
    related_modules: list[str] = Field(default_factory=list)
    steps: list[FlowStep] = Field(default_factory=list)


class GlossaryEntry(LearningBaseModel):
    slug: str
    term: str
    definition: str
    why_it_matters_in_repo: str
    related_modules: list[str] = Field(default_factory=list)


class OverviewPage(LearningBaseModel):
    title: str
    intro: str
    high_level_notes: list[str] = Field(default_factory=list)
    featured_modules: list[str] = Field(default_factory=list)
    featured_flows: list[str] = Field(default_factory=list)


class LearningPortalContent(LearningBaseModel):
    overview: OverviewPage
    modules: dict[str, ModulePage]
    flows: dict[str, FlowPage]
    glossary: dict[str, GlossaryEntry] = Field(default_factory=dict)

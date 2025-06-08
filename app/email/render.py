from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

template_dir = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(["html", "xml"]))


# 필터 등록
def currency_format(value: int | float) -> str:
    return f"{value:,.0f}"


env.filters["currency_format"] = currency_format


def render_template(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(**context)

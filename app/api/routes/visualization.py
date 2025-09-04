"""
Visualization routes for the Exoplanet API.

This module renders simple, on-the-fly charts as PNG images:
- Histogram of host star effective temperature (T_eff)
- Discoveries by year (bar chart)
- Discoveries by method (horizontal bar chart)

Notes:
- Uses a headless Matplotlib backend suitable for servers (Agg).
- Responses are returned as PNG bytes with caching disabled.
"""

from io import BytesIO
from typing import Literal

import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.cm as cm

from fastapi import APIRouter, Depends, Query
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db.session import get_db
from app.db.models import Planet


router = APIRouter(prefix="/vis", tags=["visualization"])


def _empty_png() -> StreamingResponse:
    """
    Return a blank PNG (used when there is no data to render).
    """
    buf = BytesIO()
    try:
        fig = plt.figure()
        fig.gca().axis("off")
        fig.tight_layout()
        fig.savefig(buf, format="png", dpi=120)
    finally:
        plt.close("all")
        buf.seek(0)

    resp = StreamingResponse(buf, media_type="image/png")

    resp.headers["Cache-Control"] = "no-store"
    return resp


@router.get(
    "/discovery.png",
    summary="Render discovery charts",
    description=(
        "Renders one of three charts as a PNG image.\n\n"
        "- `hist`: Histogram of host star effective temperature (Teff)\n"
        "- `year`: Discoveries per year (bar chart)\n"
        "- `method`: Discoveries per method (horizontal bar chart)\n\n"
        "Response has `Cache-Control: no-store` to disable browser caching."
    ),
)
def vis_discovery(
    db: Session = Depends(get_db),
    chart: Literal["hist", "year", "method"] = Query(
        description=(
                "Choose which chart to render:\n"
                "- **hist**: Histogram of host star effective temperature (Teff)\n"
                "- **year**: Number of planets discovered per year\n"
                "- **method**: Number of planets discovered by method (horizontal bar chart)"
        )
    ),
    bins: int = Query(
        30,
        ge=5,
        le=200,
        description="Number of histogram bins (for chart=hist, 5..200)",
    ),
    sigma: float = Query(
        3.0,
        ge=0.0,
        le=10.0,
        description="Sigma range for outlier filtering (0 = no filter, only for chart=hist, 0..10)",
    ),
) -> StreamingResponse:
    """
    Render chart as PNG and return it as a streaming response.

    Returns:
        StreamingResponse: PNG image with `Cache-Control: no-store`.
    """

    def _as_png(fig) -> StreamingResponse:
        buf = BytesIO()
        try:
            fig.tight_layout()
            fig.savefig(buf, format="png", dpi=120)
        finally:
            plt.close(fig)
            buf.seek(0)
        resp = StreamingResponse(buf, media_type="image/png")
        resp.headers["Cache-Control"] = "no-store"
        return resp

    if chart == "hist":
        vals = db.execute(select(Planet.st_teff)).scalars().all()
        vals = [v for v in vals if v is not None]

        if not vals:
            return _empty_png()

        data = np.asarray(vals, dtype=float)
        mu = float(np.mean(data))
        sd = float(np.std(data))

        if sigma > 0 and sd > 0:
            lower = mu - sigma * sd
            upper = mu + sigma * sd
            data = data[(data >= lower) & (data <= upper)]
        else:
            lower = upper = None

        fig = plt.figure()
        ax = fig.gca()
        ax.hist(data, bins=bins, edgecolor="black")
        ax.set_xlabel("Host Star Effective Temperature (K)")
        ax.set_ylabel("Number of Planets")
        ax.set_title(f"$T_{{eff}}$ Histogram (bins={bins}, ±{int(sigma)}σ)")
        ax.axvline(mu, linestyle="--", linewidth=1.5, label=f"Mean = {int(round(mu))} K")
        if lower is not None and upper is not None:
            ax.axvline(lower, linestyle=":", linewidth=1.5, label=f"-{int(sigma)}σ = {int(round(lower))} K")
            ax.axvline(upper, linestyle=":", linewidth=1.5, label=f"+{int(sigma)}σ = {int(round(upper))} K")
        ax.legend()

        return _as_png(fig)

    if chart == "year":
        rows = (
            db.execute(
                select(Planet.disc_year, func.count())
                .where(Planet.disc_year.isnot(None))
                .where(Planet.is_deleted == False)
                .group_by(Planet.disc_year)
                .order_by(Planet.disc_year.asc())
            )
            .all()
        )

        if not rows:
            return _empty_png()

        years = [int(y) for y, _ in rows]
        counts = [int(c) for _, c in rows]

        fig = plt.figure()
        ax = fig.gca()
        ax.bar(years, counts)
        ax.set_xlabel("Discovery Year")
        ax.set_ylabel("Number of Planets Discovered")
        ax.set_title("Discoveries by Year")

        if len(years) > 15:
            step = max(1, len(years) // 15)
            ax.set_xticks(years[::step])
        else:
            ax.set_xticks(years)
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha("right")

        return _as_png(fig)

    # chart == "method"
    rows = (
        db.execute(
            select(Planet.disc_method, func.count())
            .where(Planet.disc_method.isnot(None))
            .where(Planet.is_deleted == False)
            .group_by(Planet.disc_method)
            .order_by(func.count().desc())
        )
        .all()
    )

    if not rows:
        return _empty_png()

    methods = [m for m, _ in rows]
    counts = [int(c) for _, c in rows]
    colors = cm.Dark2(np.linspace(0, 1, len(methods)))

    fig = plt.figure(figsize=(12, 6))
    ax = fig.gca()
    ax.barh(methods, counts, color=colors)
    ax.set_xlabel("Number of Planets")
    ax.set_title("Discoveries by Method")

    right_pad = max(counts) * 0.01 if counts else 0.0
    for i, v in enumerate(counts):
        ax.text(v + right_pad, i, str(v), va="center")

    return _as_png(fig)
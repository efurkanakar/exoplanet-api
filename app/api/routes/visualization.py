from fastapi import APIRouter, Depends, Query
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Literal

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from io import BytesIO

from app.db.session import get_db
from app.db.models import Planet


router = APIRouter(prefix="/vis", tags=["visualization"])

@router.get("/discovery.png")
def vis_discovery(
    db: Session = Depends(get_db),
    chart: Literal["hist", "year", "method"] = Query(
        default="hist",
        description=(
            "Which chart to render: 'hist' (Teff histogram), 'year' (discoveries by year), "
            "'method' (discoveries by method, horizontal bar)"
        ),
    ),
    bins: int = Query(30, description="Number of histogram bins (for chart=hist)"),
    sigma: float = Query(3.0, description="Sigma range for filtering (0 = no filter, only for chart=hist)"),
):
    buf = BytesIO()

    if chart == "hist":
        vals = db.execute(select(Planet.st_teff)).scalars().all()
        vals = [v for v in vals if v is not None]

        if not vals:
            plt.figure(); plt.axis("off"); plt.tight_layout()
            plt.savefig(buf, format="png", dpi=120); plt.close()
            buf.seek(0)
            return StreamingResponse(buf, media_type="image/png")

        data = np.array(vals, dtype=float)
        mu = float(np.mean(data))
        sd = float(np.std(data))
        lower = upper = None
        if sigma > 0 and sd > 0:
            lower, upper = mu - sigma * sd, mu + sigma * sd
            data = data[(data >= lower) & (data <= upper)]

        plt.figure()
        plt.hist(data, bins=bins, edgecolor="black")
        plt.xlabel("Host Star Effective Temperature (K)")
        plt.ylabel("Number of Planets")
        plt.title(f"$T_{{eff}}$ Histogram (bins={bins}, ±{int(sigma)}σ)")
        plt.axvline(mu, linestyle="--", linewidth=1.5, label=f"Mean = {int(round(mu))} K")
        if lower is not None and upper is not None:
            plt.axvline(lower, linestyle=":", linewidth=1.5, label=f"-{int(sigma)}σ = {int(round(lower))} K")
            plt.axvline(upper, linestyle=":", linewidth=1.5, label=f"+{int(sigma)}σ = {int(round(upper))} K")
        plt.legend()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=120)
        plt.close()
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")

    elif chart == "year":
        rows = db.execute(
            select(Planet.disc_year, func.count())
            .where(Planet.disc_year.isnot(None))
            .group_by(Planet.disc_year)
            .order_by(Planet.disc_year.asc())
        ).all()

        if not rows:
            plt.figure(); plt.axis("off"); plt.tight_layout(); plt.savefig(buf, format="png", dpi=120); plt.close()
            buf.seek(0)
            return StreamingResponse(buf, media_type="image/png")

        years = [int(y) for y, _ in rows]
        counts = [int(c) for _, c in rows]

        plt.figure()
        plt.bar(years, counts)
        plt.xlabel("Discovery Year")
        plt.ylabel("Number of Planets Discovered")
        plt.title("Discoveries by Year")
        if len(years) > 15:
            step = max(1, len(years)//15)
            plt.xticks(years[:: step], rotation=45, ha="right")
        else:
            plt.xticks(years, rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=120)
        plt.close()
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")

    elif chart == "method":
        rows = db.execute(
            select(Planet.disc_method, func.count())
            .where(Planet.disc_method.isnot(None))
            .group_by(Planet.disc_method)
            .order_by(func.count().desc())
        ).all()

        if not rows:
            plt.figure(); plt.axis("off"); plt.tight_layout(); plt.savefig(buf, format="png", dpi=120); plt.close()
            buf.seek(0)
            return StreamingResponse(buf, media_type="image/png")

        methods = [m for m, _ in rows]
        counts  = [int(c) for _, c in rows]
        colors = cm.Dark2(np.linspace(0, 1, len(methods)))

        plt.figure(figsize=(12, 6))
        plt.barh(methods, counts, color=colors)
        plt.xlabel("Number of Planets")
        plt.title("Discoveries by Method")

        for i, v in enumerate(counts):
            plt.text(v + max(counts)*0.01, i, str(v), va="center")

        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=120)
        plt.close()
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")

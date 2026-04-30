"""
Reusable Plotly chart builders for the BehaveDrift dashboard.
Consistent colour palette and styling across all visualisations.
"""

from __future__ import annotations

import plotly.graph_objects as go

# ── Colour Palette ───────────────────────────────────────────

COLOURS = {
    "stable": "#22c55e",       # Green
    "watch_t1": "#eab308",     # Yellow
    "concern_t2": "#f97316",   # Orange
    "alert_t3": "#ef4444",     # Red
    "critical_t4": "#991b1b",  # Dark Red
    "primary": "#06b6d4",      # Cyan
    "surface": "#1e293b",      # Slate 800
    "text": "#e2e8f0",         # Slate 200
    "muted": "#94a3b8",        # Slate 400
}

TIER_COLOURS = {
    "T1": COLOURS["watch_t1"],
    "T2": COLOURS["concern_t2"],
    "T3": COLOURS["alert_t3"],
    "T4": COLOURS["critical_t4"],
}

TIER_LABELS = {
    "T1": "Watch",
    "T2": "Concern",
    "T3": "Alert",
    "T4": "Critical",
}

_LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLOURS["text"], family="Inter, sans-serif"),
    margin=dict(l=40, r=20, t=40, b=40),
)


# ── Risk Distribution Donut ─────────────────────────────────


def build_risk_donut(risk_distribution: dict) -> go.Figure:
    """Build a donut chart showing population risk distribution."""
    labels = ["Stable", "Watch (T1)", "Concern (T2)", "Alert (T3)", "Critical (T4)"]
    values = [
        risk_distribution.get("stable", 0),
        risk_distribution.get("watch_t1", 0),
        risk_distribution.get("concern_t2", 0),
        risk_distribution.get("alert_t3", 0),
        risk_distribution.get("critical_t4", 0),
    ]
    colours = [
        COLOURS["stable"],
        COLOURS["watch_t1"],
        COLOURS["concern_t2"],
        COLOURS["alert_t3"],
        COLOURS["critical_t4"],
    ]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colours, line=dict(color="#0f172a", width=2)),
                textinfo="label+value",
                textfont=dict(size=13),
                hoverinfo="label+value+percent",
            )
        ]
    )
    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title=dict(text="Population Risk Distribution", font=dict(size=16)),
        showlegend=False,
        height=380,
    )
    # Add centre annotation
    total = sum(values)
    fig.add_annotation(
        text=f"<b>{total}</b><br>Residents",
        showarrow=False,
        font=dict(size=18, color=COLOURS["text"]),
    )
    return fig


# ── Drift Timeline ──────────────────────────────────────────


def build_drift_timeline(data_points: list[dict]) -> go.Figure:
    """Build a time-series line chart of drift scores with alert markers."""
    if not data_points:
        fig = go.Figure()
        fig.update_layout(**_LAYOUT_DEFAULTS, title="No data available")
        return fig

    dates = [dp["date"] for dp in data_points]
    scores = [dp.get("drift_score") for dp in data_points]

    fig = go.Figure()

    # Main drift score line
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=scores,
            mode="lines+markers",
            name="Drift Score",
            line=dict(color=COLOURS["primary"], width=2.5),
            marker=dict(size=6),
            hovertemplate="Date: %{x}<br>Drift Score: %{y:.4f}<extra></extra>",
        )
    )

    # Alert tier markers
    alert_dates = [dp["date"] for dp in data_points if dp.get("alert_tier")]
    alert_scores = [
        dp.get("drift_score") for dp in data_points if dp.get("alert_tier")
    ]
    alert_tiers = [dp["alert_tier"] for dp in data_points if dp.get("alert_tier")]
    alert_colours = [TIER_COLOURS.get(t, COLOURS["alert_t3"]) for t in alert_tiers]
    alert_text = [TIER_LABELS.get(t, t) for t in alert_tiers]

    if alert_dates:
        fig.add_trace(
            go.Scatter(
                x=alert_dates,
                y=alert_scores,
                mode="markers",
                name="Alerts",
                marker=dict(
                    size=14,
                    color=alert_colours,
                    symbol="diamond",
                    line=dict(width=1.5, color="#fff"),
                ),
                text=alert_text,
                hovertemplate="Date: %{x}<br>Tier: %{text}<br>Score: %{y:.4f}<extra></extra>",
            )
        )

    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title=dict(text="Drift Score Over Time", font=dict(size=16)),
        xaxis=dict(
            title="Date",
            gridcolor="rgba(148,163,184,0.15)",
            showgrid=True,
        ),
        yaxis=dict(
            title="Drift Score",
            gridcolor="rgba(148,163,184,0.15)",
            showgrid=True,
            rangemode="tozero",
        ),
        height=420,
        hovermode="x unified",
    )
    return fig


# ── Tier Badge HTML ──────────────────────────────────────────


def tier_badge(tier: str) -> str:
    """Return an HTML badge string for an alert tier."""
    colour = TIER_COLOURS.get(tier, COLOURS["muted"])
    label = TIER_LABELS.get(tier, tier)
    return (
        f'<span style="background:{colour};color:#fff;padding:3px 10px;'
        f'border-radius:12px;font-size:0.85em;font-weight:600;">'
        f"{tier} — {label}</span>"
    )


def status_dot(connected: bool) -> str:
    """Return an HTML status dot indicator."""
    colour = "#22c55e" if connected else "#ef4444"
    label = "Connected" if connected else "Disconnected"
    return (
        f'<span style="display:inline-flex;align-items:center;gap:6px;">'
        f'<span style="width:10px;height:10px;border-radius:50%;'
        f'background:{colour};display:inline-block;"></span>'
        f"{label}</span>"
    )

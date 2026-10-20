import calendar
from datetime import datetime, timezone
from ipaddress import ip_address as parse_ip_address
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models.website_visit import WebsiteVisit
from app.schemas.website_visit import WebsiteVisitCreate, WebsiteVisitStatsResponse


router = APIRouter(
    prefix="/website-visits",
    tags=["Website Visits"],
)

TAIPEI_TZ = ZoneInfo("Asia/Taipei")


def get_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        ips = [ip.strip() for ip in forwarded_for.split(",")]

        if len(ips) == 1:
            try:
                return str(parse_ip_address(ips[0]))
            except ValueError:
                pass

    return request.client.host if request.client else None


@router.post("/visits", status_code=status.HTTP_201_CREATED)
def create_website_visit(
    payload: WebsiteVisitCreate,
    request: Request,
):
    ip_address = get_client_ip(request)

    visit = WebsiteVisit(
        site_key=payload.site_key,
        visitor_id=payload.visitor_id,
        page_path=payload.page_path,
        ip_address=ip_address,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer"),
    )

    try:
        with SessionLocal() as session:
            session.add(visit)
            session.commit()
            session.refresh(visit)

            return {
                "id": visit.id,
                "status": "recorded",
            }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to record website visit",
        )


def empty_stats(days_in_month: int) -> dict:
    return {
        "yearly": 0,
        "monthly": [0] * 12,
        "daily": [0] * days_in_month,
    }


@router.get(
    "/stats",
    response_model=WebsiteVisitStatsResponse,
    status_code=status.HTTP_200_OK,
)
def get_website_visit_stats(
    site_key: str = Query(..., min_length=1, max_length=100),
):
    now = datetime.now(TAIPEI_TZ)
    year = now.year
    month = now.month
    days_in_month = calendar.monthrange(year, month)[1]

    year_start = datetime(year, 1, 1, tzinfo=TAIPEI_TZ)
    year_end = datetime(year + 1, 1, 1, tzinfo=TAIPEI_TZ)
    month_start = datetime(year, month, 1, tzinfo=TAIPEI_TZ)

    # 統一以 UTC 時間範圍查詢
    year_start_utc = year_start.astimezone(timezone.utc)
    year_end_utc = year_end.astimezone(timezone.utc)

    pages = {
        "total": empty_stats(days_in_month),
    }

    try:
        with SessionLocal() as session:
            # 先取得該網站所有曾經出現過的 page_path
            paths = session.execute(
                select(WebsiteVisit.page_path)
                .where(WebsiteVisit.site_key == site_key)
                .distinct()
            ).scalars().all()

            for path in paths:
                pages[path] = empty_stats(days_in_month)

            # 查詢今年的每日瀏覽次數
            taipei_date = func.date(
                func.timezone("Asia/Taipei", WebsiteVisit.visited_at)
            )

            rows = session.execute(
                select(
                    WebsiteVisit.page_path,
                    taipei_date.label("visit_date"),
                    func.count().label("views"),
                )
                .where(
                    WebsiteVisit.site_key == site_key,
                    WebsiteVisit.visited_at >= year_start_utc,
                    WebsiteVisit.visited_at < year_end_utc,
                )
                .group_by(WebsiteVisit.page_path, taipei_date)
            ).all()

            for path, visit_date, views in rows:
                for stats in (pages["total"], pages[path]):
                    stats["yearly"] += views
                    stats["monthly"][visit_date.month - 1] += views

                    if visit_date.month == month:
                        stats["daily"][visit_date.day - 1] += views

        return {
            "site_key": site_key,
            "year": year,
            "month": month,
            "pages": pages,
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve website visit statistics",
        )
        
        

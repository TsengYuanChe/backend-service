from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError
from ipaddress import ip_address as parse_ip_address

from app.database import SessionLocal
from app.models.website_visit import WebsiteVisit
from app.schemas.website_visit import WebsiteVisitCreate


router = APIRouter(
    prefix="/website-visits",
    tags=["Website Visits"],
)


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


